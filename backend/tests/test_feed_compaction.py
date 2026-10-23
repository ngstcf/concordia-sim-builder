"""Unit tests for feed compaction (backend/prefabs/feed_compaction.py).

Pure unit tests: a stub language model and a real ForumState, no network.
They pin the behaviors the compacted feed mode promises:

- posts fold into the digest only once they age past the verbatim tail and
  only in batches of at least min_fold_batch;
- each agent receives a given digest version exactly once;
- the vote summary is capped with an explicit omission count;
- state round-trips through get_state/set_state (checkpoint contract);
- a failing digest model degrades to plain windowing instead of crashing.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.prefabs.feed_compaction import CompactingForumObservation
from concordia.contrib.components.game_master import forum as forum_module
from concordia.typing import entity as entity_lib

PLAYERS = ['Alice', 'Bob']


class StubModel:
    """Deterministic stand-in for a language model."""

    def __init__(self, reply='Digest: recurring themes and vote leaders.',
                 fail=False):
        self.reply = reply
        self.fail = fail
        self.calls = []

    def sample_text(self, prompt, **kwargs):
        self.calls.append(prompt)
        if self.fail:
            raise RuntimeError('provider down')
        return self.reply


def make_observation_spec(name):
    return entity_lib.ActionSpec(
        call_to_action=forum_module.DEFAULT_CALL_TO_MAKE_OBSERVATION.format(
            name=name),
        output_type=entity_lib.OutputType.MAKE_OBSERVATION,
    )


def make_component(model, forum_state, **kwargs):
    comp = CompactingForumObservation(model=model, **kwargs)
    comp._get_forum_state = lambda: forum_state
    comp._logging_channel = lambda *_args, **_kw: None
    return comp


def fill_forum(forum_state, n, start=0):
    for i in range(start, start + n):
        forum_state.create_post(
            author=PLAYERS[i % len(PLAYERS)],
            title=f'Post {i}',
            content=f'Content of post {i}',
        )


class FeedCompactionTest(unittest.TestCase):

    def setUp(self):
        self.forum = forum_module.ForumState(
            player_names=PLAYERS, forum_name='TestTown')

    def observe(self, comp, name='Alice'):
        return comp.pre_act(make_observation_spec(name))

    def test_no_fold_below_batch_threshold(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10)
        fill_forum(self.forum, 12)  # 7 aged, below the batch of 10
        out = self.observe(comp)
        self.assertEqual(model.calls, [])
        self.assertNotIn('recap of older activity', out)

    def test_fold_and_deliver_once_per_version(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10)
        fill_forum(self.forum, 20)  # 15 aged >= batch of 10 -> fold
        first = self.observe(comp, 'Alice')
        self.assertEqual(len(model.calls), 1)
        self.assertIn('recap of older activity', first)
        self.assertIn('Digest:', first)
        # Same version is not re-delivered to the same agent...
        second = self.observe(comp, 'Alice')
        self.assertNotIn('recap of older activity', second)
        # ...but a different agent still gets it once.
        bob = self.observe(comp, 'Bob')
        self.assertIn('recap of older activity', bob)
        # Watermark: everything up to (max_post_id - recent_posts) folded.
        self.assertEqual(comp._folded_watermark, 19 - 5)

    def test_new_version_redelivers(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10)
        fill_forum(self.forum, 20)
        self.observe(comp, 'Alice')          # v1 delivered
        fill_forum(self.forum, 15, start=20)  # age 15 more past the tail
        out = self.observe(comp, 'Alice')     # fold -> v2 -> redeliver
        self.assertEqual(len(model.calls), 2)
        self.assertIn('recap of older activity', out)
        self.assertEqual(comp._digest_version, 2)

    def test_vote_summary_capped_with_omission_count(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=100, min_fold_batch=100,
                              vote_summary_top=3)
        fill_forum(self.forum, 10)
        for pid in (2, 5, 7):
            self.forum.upvote(pid)
        out = self.observe(comp)
        self.assertIn('vote counts (top 3)', out)
        self.assertIn('(+7 more posts)', out)
        # The three upvoted posts are the ones listed.
        for pid in (2, 5, 7):
            self.assertIn(f'Post #{pid}: 1 votes', out)

    def test_digest_truncated_to_max_words(self):
        model = StubModel(reply=' '.join(f'w{i}' for i in range(500)))
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10,
                              digest_max_words=40)
        fill_forum(self.forum, 20)
        self.observe(comp)
        self.assertEqual(len(comp._digest.split()), 40)

    def test_model_failure_degrades_without_advancing(self):
        model = StubModel(fail=True)
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10)
        fill_forum(self.forum, 20)
        out = self.observe(comp)  # fold attempted, fails, run continues
        self.assertEqual(len(model.calls), 1)
        self.assertNotIn('recap of older activity', out)
        self.assertEqual(comp._digest, '')
        self.assertEqual(comp._folded_watermark, -1)
        # Recovery: the same aged posts fold on a later delivery.
        model.fail = False
        out2 = self.observe(comp)
        self.assertIn('recap of older activity', out2)
        self.assertEqual(comp._folded_watermark, 19 - 5)

    def test_state_roundtrip_preserves_delivery_and_watermark(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=5, min_fold_batch=10)
        fill_forum(self.forum, 20)
        self.observe(comp, 'Alice')
        state = comp.get_state()

        restored = make_component(StubModel(), self.forum,
                                  recent_posts=5, min_fold_batch=10)
        restored.set_state(state)
        # Alice already received v1: no re-delivery after resume.
        out = self.observe(restored, 'Alice')
        self.assertNotIn('recap of older activity', out)
        # Bob did not: delivered exactly once after resume.
        self.assertIn('recap of older activity', self.observe(restored, 'Bob'))
        self.assertEqual(restored._folded_watermark, comp._folded_watermark)

    def test_delta_delivery_inherited(self):
        model = StubModel()
        comp = make_component(model, self.forum,
                              recent_posts=100, min_fold_batch=100)
        fill_forum(self.forum, 3)
        first = self.observe(comp, 'Alice')
        self.assertIn('Post 2', first)
        second = self.observe(comp, 'Alice')
        self.assertIn('No new activity', second)


if __name__ == '__main__':
    unittest.main()
