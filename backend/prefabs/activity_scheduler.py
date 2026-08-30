"""Per-agent activity scheduling for the async social media game master.

Replaces the `_NextActingEligiblePlayers` component that
`async_social_media__GameMaster` installs under `__next_acting__`. The
upstream component converts a per-agent activity rate into a per-step
probability like this:

    if rate <= 1.0:
        return rate                      # taken as a direct probability
    max_rate = max(default, *all_other_rates, 1.0)
    return min(1.0, rate / max_rate)     # taken as a relative intensity

Two problems follow from that, both of which corrupt controlled experiments:

1.  **A per-agent parameter has global side effects.** `max_rate` is drawn
    from every agent's rate, so raising one agent's rate rescales everyone
    else. Example: with rates {A: 1.6, B: 0.8}, agent A acts at p=1.0; add
    agent C at rate 10.0 and A silently drops to p=0.16 while C itself acts
    at p=1.0. Configuring one agent changed another's behavior, which
    breaks any condition contrast that adds or re-rates a single agent.

2.  **The rule is discontinuous at 1.0.** Rates at or below 1.0 skip
    normalization entirely, so with a 10.0 agent present, an agent at 1.6
    (p=0.16) acts far less than one at 0.8 (p=0.80) -- the ordering inverts.

Here a rate is always a relative intensity measured against
`default_activity_rate`, and depends on nothing else:

    p = min(1.0, rate / default_activity_rate)

Adding, removing, or re-rating one agent therefore leaves every other
agent's behaviour untouched, which is what a condition contrast requires.

Note the ceiling. The async engine gives each entity one opportunity to act
per iteration, so p is capped at 1.0 and no agent can act more than once per
step: an amplification factor above `default_activity_rate` cannot be
honoured, only clipped. To express "this agent is 10x as active as the
others", scale the *others* down (manipulator 1.0, honest agents 0.1) rather
than scaling the manipulator up. `clipped_players()` reports every rate that
had to be clipped so callers can surface it instead of silently
reinterpreting the experimental design.
"""

from collections.abc import Mapping, Sequence
import random
import threading

from concordia.components import game_master as gm_components
from concordia.typing import entity as entity_lib
from concordia.typing import entity_component


class IndependentActivityScheduler(entity_component.ContextComponent):
    """Samples the players who act next, independently per player."""

    def __init__(
        self,
        player_names: Sequence[str] = (),
        default_activity_rate: float = 1.0,
        per_agent_activity_rates: Mapping[str, float] | None = None,
        activity_seed: int | None = None,
        pre_act_label: str = (
            gm_components.next_acting.DEFAULT_NEXT_ACTING_PRE_ACT_LABEL
        ),
    ):
        super().__init__()
        self._player_names = list(player_names)
        self._default_activity_rate = default_activity_rate
        self._per_agent_activity_rates = dict(per_agent_activity_rates or {})
        self._rng = random.Random(activity_seed)
        self._pre_act_label = pre_act_label
        self._lock = threading.Lock()

    def _rate(self, player_name: str) -> float:
        return self._per_agent_activity_rates.get(
            player_name, self._default_activity_rate
        )

    def _effective_probability(self, player_name: str) -> float:
        """Activity rate -> per-step probability, independent of other agents."""
        rate = self._rate(player_name)
        if rate <= 0:
            return 0.0
        reference = (
            self._default_activity_rate
            if self._default_activity_rate > 0
            else 1.0
        )
        return min(1.0, float(rate) / float(reference))

    def clipped_players(self) -> dict[str, float]:
        """Players whose configured rate exceeds what one act per step allows.

        Maps player name -> the requested rate. A non-empty result means the
        configuration asks for an amplification the engine cannot deliver.
        """
        reference = (
            self._default_activity_rate
            if self._default_activity_rate > 0
            else 1.0
        )
        return {
            name: self._rate(name)
            for name in self._player_names
            if self._rate(name) > reference
        }

    def remove_player(self, player_name: str) -> None:
        """Remove a player from the active set (e.g. ban from platform)."""
        with self._lock:
            if player_name in self._player_names:
                self._player_names.remove(player_name)

    def add_player(self, player_name: str) -> None:
        """Add a player back to the active set (e.g. unban)."""
        with self._lock:
            if player_name not in self._player_names:
                self._player_names.append(player_name)

    def pre_act(self, action_spec: entity_lib.ActionSpec) -> str:
        if action_spec.output_type == entity_lib.OutputType.NEXT_ACTING:
            with self._lock:
                sampled = []
                for player_name in self._player_names:
                    p = self._effective_probability(player_name)
                    if p > 0 and self._rng.random() < p:
                        sampled.append(player_name)
                # Ensure the engine still progresses even at low rates.
                if not sampled and self._player_names:
                    sampled = [self._rng.choice(self._player_names)]
                return ', '.join(sampled)
        return ''

    def get_state(self) -> entity_component.ComponentState:
        with self._lock:
            return {'player_names': list(self._player_names)}

    def set_state(self, state: entity_component.ComponentState) -> None:
        with self._lock:
            self._player_names = list(state['player_names'])
