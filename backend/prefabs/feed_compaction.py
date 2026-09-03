"""Feed compaction for the async social media game master.

Replaces the `ForumObservation` component that `async_social_media__GameMaster`
installs under `__make_observation__`, selected with
`game_master.parameters.feed_mode = "compacted"` (default `"full"` keeps the
upstream behavior byte-identical). Overriding the component key keeps the
pinned fork untouched, the same pattern as `activity_scheduler.py`.

Why this exists. Upstream delivery already sends each agent only the posts
that are new to them, but two terms still grow without bound and land in every
agent's accumulated observation history:

1.  The vote summary enumerates every post ever created on every delivery,
    so a single observation chunk is O(total posts) and the chunks accumulate.
2.  The per-delivery deltas themselves pile up in agent history, so prompt
    size grows with population x steps unless history is truncated, and plain
    truncation makes agents forget older forum activity outright.

Compacted mode bounds both while compensating for the forgetting:

-   The vote summary is capped to the top-K posts by votes, with an explicit
    omission count for the rest.
-   Posts that age past a verbatim tail are folded, in batches, into a single
    rolling digest maintained with one language-model call per fold, shared by
    the whole roster (the feed is a broadcast, so one digest serves everyone).
    Each agent receives the digest as its own observation chunk exactly once
    per version, so bounded observation history always contains at most a few
    digest copies rather than one per delivery.

The digest is generated text and therefore part of the instrument: what it
keeps or drops mediates every agent's memory of the older forum. It is
delivered as a visible observation ("recap of older activity"), logged on
every fold, and carried in checkpoints, so runs that use it are auditable and
resumable. Degradation is safe: if the digest model call fails, the previous
digest is kept, the watermark does not advance, and the fold is retried on a
later delivery.
"""

import threading

from concordia.contrib.components.game_master import forum as forum_module
from concordia.language_model import language_model
from concordia.typing import entity as entity_lib

DEFAULT_RECENT_POSTS = 60
DEFAULT_DIGEST_MAX_WORDS = 250
DEFAULT_VOTE_SUMMARY_TOP = 20
DEFAULT_MIN_FOLD_BATCH = 25

_FOLD_PROMPT = """\
You maintain the rolling digest of older activity on the forum '{forum_name}'.

Current digest (empty if none yet):
{digest}

Older posts to fold into the digest:
{aged}

Rewrite the digest to incorporate this material in at most {max_words} words.
Preserve recurring themes and how support for them is trending, the named
positions of frequent or influential posters, which posts lead on votes, and
questions that remain open. Drop greetings and one-off chatter. Neutral,
factual prose. Output only the digest text."""


class CompactingForumObservation(forum_module.ForumObservation):
  """ForumObservation that bounds delivery size and folds old posts.

  Drop-in replacement registered under `__make_observation__`. Per-player
  delta delivery and notifications are inherited unchanged; this class caps
  the vote summary and adds the rolling digest described in the module
  docstring.
  """

  def __init__(
      self,
      model: language_model.LanguageModel,
      recent_posts: int = DEFAULT_RECENT_POSTS,
      digest_max_words: int = DEFAULT_DIGEST_MAX_WORDS,
      vote_summary_top: int = DEFAULT_VOTE_SUMMARY_TOP,
      min_fold_batch: int = DEFAULT_MIN_FOLD_BATCH,
      **kwargs,
  ):
    super().__init__(**kwargs)
    self._model = model
    self._recent_posts = max(1, int(recent_posts))
    self._digest_max_words = max(20, int(digest_max_words))
    self._vote_summary_top = max(1, int(vote_summary_top))
    self._min_fold_batch = max(1, int(min_fold_batch))

    self._digest_lock = threading.Lock()
    self._digest = ''
    self._digest_version = 0
    # Highest post_id already folded into the digest. Posts above it are
    # either in the verbatim tail or awaiting the next fold.
    self._folded_watermark = -1
    self._delivered_version: dict[str, int] = {}

  # -- digest maintenance ----------------------------------------------------

  def _format_aged_post(self, post) -> str:
    content = ' '.join((post.content or '').split())
    words = content.split(' ')
    if len(words) > 60:
      content = ' '.join(words[:60]) + '...'
    line = (f'#{post.post_id} "{post.title}" by {post.author} '
            f'(votes {post.votes}, replies {len(post.replies)})')
    if content and content != post.title:
      line += f': {content}'
    return line

  def _maybe_fold(self, forum_state: forum_module.ForumState) -> None:
    """Fold posts that aged past the verbatim tail into the digest."""
    with self._digest_lock:
      posts = forum_state.get_recent_posts(None)  # all posts, newest first
      if not posts:
        return
      cutoff = posts[0].post_id - self._recent_posts
      aged = [p for p in posts
              if self._folded_watermark < p.post_id <= cutoff]
      if len(aged) < self._min_fold_batch:
        return
      aged.sort(key=lambda p: p.post_id)
      prompt = _FOLD_PROMPT.format(
          forum_name=getattr(forum_state, '_forum_name', 'the forum'),
          digest=self._digest or '(empty)',
          aged='\n'.join(self._format_aged_post(p) for p in aged),
          max_words=self._digest_max_words,
      )
      try:
        text = self._model.sample_text(
            prompt,
            max_tokens=int(self._digest_max_words * 2.5),
            temperature=0.0,
        ).strip()
      except Exception as e:  # degrade to plain windowing, retry next call
        self._logging_channel({
            'Key': 'FeedCompaction',
            'Summary': f'digest fold failed, keeping previous digest: {e}',
            'Value': '',
        })
        return
      if not text:
        return
      words = text.split()
      if len(words) > self._digest_max_words:
        text = ' '.join(words[:self._digest_max_words])
      self._digest = text
      self._digest_version += 1
      self._folded_watermark = aged[-1].post_id
      self._logging_channel({
          'Key': 'FeedCompaction',
          'Summary': (f'digest v{self._digest_version}: folded '
                      f'{len(aged)} posts through #{self._folded_watermark}'),
          'Value': self._digest,
      })
      print(f'[INFO] feed compaction: digest v{self._digest_version} folded '
            f'{len(aged)} posts (through #{self._folded_watermark}, '
            f'{len(self._digest.split())} words)')

  def _digest_chunk_for(self, player_name: str, forum_name: str) -> str:
    """The digest as a one-time-per-version observation chunk, or ''."""
    with self._digest_lock:
      if not self._digest:
        return ''
      if self._delivered_version.get(player_name, 0) >= self._digest_version:
        return ''
      self._delivered_version[player_name] = self._digest_version
      return (f'{forum_name} recap of older activity: {self._digest}')

  def _capped_vote_summary(self, forum_state: forum_module.ForumState) -> str:
    posts = forum_state.get_recent_posts(None)
    if not posts:
      return ''
    ranked = sorted(posts, key=lambda p: (-p.votes, p.post_id))
    top = ranked[:self._vote_summary_top]
    forum_name = getattr(forum_state, '_forum_name', 'Forum')
    entries = [f'Post #{p.post_id}: {p.votes} votes' for p in top]
    summary = f'{forum_name} vote counts (top {len(top)}): ' + ', '.join(entries)
    omitted = len(posts) - len(top)
    if omitted > 0:
      summary += f' (+{omitted} more posts)'
    return summary

  # -- delivery ----------------------------------------------------------------

  def pre_act(
      self,
      action_spec: entity_lib.ActionSpec,
  ) -> str:
    result = ''
    if action_spec.output_type == entity_lib.OutputType.MAKE_OBSERVATION:
      active_entity_name = self._get_active_entity_name_from_call_to_action(
          action_spec.call_to_action
      )
      forum_state = self._get_forum_state()
      self._maybe_fold(forum_state)

      forum_name = getattr(forum_state, '_forum_name', 'Forum')
      parts = []
      notifications = forum_state.drain_notifications(active_entity_name)
      if notifications:
        parts.extend(notifications)
      digest_chunk = self._digest_chunk_for(active_entity_name, forum_name)
      if digest_chunk:
        parts.append(digest_chunk)
      parts.append(
          forum_state.get_forum_summary_for_player(active_entity_name))
      vote_summary = self._capped_vote_summary(forum_state)
      if vote_summary:
        parts.append(vote_summary)
      # Same chunking contract as upstream: ObservationToMemory splits at
      # '\n\n\n' to create one observation memory per chunk.
      result = '\n\n\n'.join(parts)

    self._logging_channel({
        'Key': self._pre_act_label,
        'Summary': result,
        'Value': result,
    })
    return result

  # -- checkpointing -----------------------------------------------------------

  def get_state(self):
    with self._digest_lock:
      return {
          'digest': self._digest,
          'digest_version': self._digest_version,
          'folded_watermark': self._folded_watermark,
          'delivered_version': dict(self._delivered_version),
      }

  def set_state(self, state) -> None:
    with self._digest_lock:
      self._digest = state.get('digest', '')
      self._digest_version = int(state.get('digest_version', 0))
      self._folded_watermark = int(state.get('folded_watermark', -1))
      self._delivered_version = dict(state.get('delivered_version', {}))
