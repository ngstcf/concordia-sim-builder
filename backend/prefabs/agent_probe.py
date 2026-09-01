"""Per-agent survey probe for longitudinal outcome measurement.

Two different instruments can produce a number called "support for candidate
A". A game master can be asked to estimate it from the events it narrated, or
every agent in the population can be asked directly and the answers counted.
These are not interchangeable.

An estimate has no denominator. The game master sees a stream of events, not a
roster, so nothing in its situation fixes what the percentages are shares *of*.
Each figure is re-derived independently at every update, so a set of shares
that should partition one population has no reason to sum to anything in
particular, a residual category like "undecided" has no reason to be the
remainder, and a running total handed to a narrator has no population ceiling
to stop it. Per-variable range checks accept every one of these outcomes,
because each individual number is inside its declared bounds.

A tally has a denominator by construction. This component puts one forced
choice question to each entity, in its own voice and against its own
accumulated memory, and counts the answers over the known roster. Shares sum
to 100 because they are counts divided by N. "Undecided" moves only when an
agent selects it. No arithmetic is delegated to a language model.

The probe is deliberately read-only. It never calls entity.act(), never adds
to an entity's memory, and contributes nothing to the game master's context,
so measuring does not perturb the thing being measured. It reads each memory
bank through the bank's own lock, which is what makes it safe to run while the
asynchronous engine has every entity on its own thread.
"""

import dataclasses
import datetime
import logging
import threading
from typing import Any, Dict, List, Optional, Sequence

from concordia.language_model import language_model
from concordia.typing import entity_component
from concordia.typing import entity as entity_lib

logger = logging.getLogger(__name__)

DEFAULT_MEMORY_LIMIT = 40

# Shares are reported to four decimal places, in whole units of 1e-4 percent.
_SHARE_UNITS = 1_000_000


def _apportion(counts: Dict[str, int], total: int) -> Dict[str, float]:
    """Convert counts to percentages that sum to exactly 100.

    Rounding each share independently reintroduces the very defect the tally
    removes: three equal shares of six agents round to 33.3333 apiece and sum
    to 99.9999, so the exported partition does not add up. Apportion by
    largest remainder instead, which distributes the leftover units to the
    categories with the largest fractional parts and therefore closes exactly.
    """
    if total <= 0:
        return {option: 0.0 for option in counts}

    exact = {option: count * _SHARE_UNITS / total
             for option, count in counts.items()}
    floors = {option: int(value) for option, value in exact.items()}
    remaining = _SHARE_UNITS - sum(floors.values())

    # Ties broken by option order so the result is deterministic, which
    # matters when runs are compared across seeds.
    ranked = sorted(
        counts,
        key=lambda option: (-(exact[option] - floors[option]),
                            list(counts).index(option)),
    )
    for option in ranked[:remaining]:
        floors[option] += 1

    return {option: units / (_SHARE_UNITS // 100)
            for option, units in floors.items()}


@dataclasses.dataclass
class ProbeItem:
    """One forced choice survey question put to every agent.

    Attributes:
        name: Identifier for the resulting series in the exported dataset.
        question: The question as put to the agent, in the second person.
        options: The permitted answers. An agent's response is always one of
            these, so the tally is exhaustive and the shares sum to 100.
        description: Optional human-readable note carried into the export.
    """
    name: str
    question: str
    options: List[str]
    description: str = ""

    def __post_init__(self):
        if len(self.options) < 2:
            raise ValueError(
                f"Probe item '{self.name}' needs at least two options; a "
                "single-option item measures nothing."
            )
        if len(set(self.options)) != len(self.options):
            raise ValueError(
                f"Probe item '{self.name}' has duplicate options, which would "
                "make the tally ambiguous."
            )


class AgentProbeComponent(
    entity_component.ContextComponent,
    entity_component.ComponentWithLogging
):
    """Administers survey items to every entity and tallies the answers.

    Attach to a game master so the probe fires on the same cadence as the
    simulation, then hand it the population with bind_entities(). It produces
    a per-item time series of population shares plus the underlying per-agent
    responses, so a shift in the aggregate can always be traced to the
    individual agents who changed their answer.
    """

    def __init__(
        self,
        model: language_model.LanguageModel,
        items: Sequence[ProbeItem],
        interval: int = 25,
        memory_limit: int = DEFAULT_MEMORY_LIMIT,
        pre_act_label: str = '',
    ):
        """Initialize the probe.

        Args:
            model: Language model used to put each item to each agent. The
                builder passes the agent model rather than the game master's,
                because the probe simulates an agent answering for itself.
            items: The survey items to administer.
            interval: Administer once every this many game master events. The
                asynchronous engine gives every entity its own thread with no
                shared step boundary, so there is no population-wide "episode"
                to key on; game master events are the only clock all agents
                are measured against. See _administer for how each response is
                stamped.
            memory_limit: How many of an agent's most recent memories to put in
                front of it when it answers. Bounds probe cost per agent.
            pre_act_label: Unused, and empty by design. The probe contributes
                nothing to the game master's context; a measurement that fed
                back into the narration would change the thing it measures.
        """
        self._model = model
        self._items = list(items)
        self._interval = max(1, int(interval))
        self._memory_limit = max(1, int(memory_limit))
        self._pre_act_label = pre_act_label

        self._entities: List[Any] = []
        self._event_counter = 0
        self._administrations = 0

        # Shares per item over time: name -> [(event_index, {option: share})]
        self._history: Dict[str, List[tuple]] = {
            item.name: [] for item in self._items
        }
        # Every individual answer, so aggregate movement stays attributable.
        self._responses: List[Dict[str, Any]] = []
        self._failures: List[Dict[str, Any]] = []

        # The probe runs inside whichever entity thread the game master is
        # resolving on, so its own bookkeeping needs a lock of its own.
        self._lock = threading.Lock()
        self._name = "agent_probe"

    # --- Wiring ----------------------------------------------------------

    def bind_entities(self, entities: Sequence[Any]) -> None:
        """Supply the population to be surveyed.

        Separate from __init__ because the component is built before the
        simulation that owns the entities exists.
        """
        self._entities = [e for e in entities if e is not None]
        per_administration = len(self._entities) * len(self._items)
        # Stated up front because probe cost is the product of three separate
        # settings and scales with population: an interval tuned for a small
        # run surveys a large one many times more often than intended.
        logger.info(
            "Agent probe bound to %d entities for %d item(s): %s. Each "
            "administration costs %d model calls, one every %d game master "
            "events.",
            len(self._entities), len(self._items),
            ", ".join(item.name for item in self._items),
            per_administration, self._interval,
        )
        print(f"[PROBE] {len(self._entities)} agents x {len(self._items)} item(s) "
              f"= {per_administration} model calls per administration, "
              f"every {self._interval} game master events")

    def get_name(self) -> str:
        return self._name

    # --- Component protocol ----------------------------------------------

    def pre_act(
        self,
        component_name: str,
        action_spec: Optional[entity_lib.ActionSpec] = None,
    ) -> str:
        """Contribute nothing. The probe observes; it does not narrate."""
        return ''

    def post_act(self, event: str) -> str:
        """Count game master events and administer the probe when due.

        The first event always administers, giving the series a baseline read
        on the same instrument as every later point. Without it the only
        available starting value is the game master's declared default, and
        comparing a probe reading against a declared default is the instrument
        mixing this component exists to avoid. It is a baseline in the sense
        that the population has not yet been exposed to the run, not that
        nothing at all has happened: one entity has acted by this point.
        """
        with self._lock:
            self._event_counter += 1
            event_index = self._event_counter
            due = (event_index == 1
                   or event_index % self._interval == 0)

        if due and self._entities and self._items:
            self._administer(event_index)
        return ''

    def get_state(self) -> str:
        """Serialize for checkpoint and resume."""
        import json
        return json.dumps({
            'event_counter': self._event_counter,
            'administrations': self._administrations,
            'history': {k: [list(pair) for pair in v]
                        for k, v in self._history.items()},
            'responses': self._responses,
            'failures': self._failures,
        })

    def set_state(self, state: str) -> None:
        """Restore from a checkpoint, tolerating an absent or stale payload."""
        import json
        try:
            data = json.loads(state) if state else {}
        except (TypeError, ValueError):
            logger.warning("Agent probe state unreadable; starting fresh.")
            return
        if not isinstance(data, dict):
            return
        self._event_counter = data.get('event_counter', 0)
        self._administrations = data.get('administrations', 0)
        restored = data.get('history') or {}
        for name in self._history:
            self._history[name] = [
                tuple(pair) for pair in restored.get(name, [])
            ]
        self._responses = data.get('responses') or []
        self._failures = data.get('failures') or []

    # --- Administration ---------------------------------------------------

    def _administer(self, event_index: int) -> None:
        """Put every item to every agent and tally the answers."""
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')

        for item in self._items:
            counts = {option: 0 for option in item.options}
            answered = 0

            for entity in self._entities:
                answer = self._ask(entity, item)
                if answer is None:
                    continue
                counts[answer] += 1
                answered += 1
                with self._lock:
                    self._responses.append({
                        'event_index': event_index,
                        'timestamp': timestamp,
                        'item': item.name,
                        'agent': getattr(entity, 'name', '<unnamed>'),
                        'answer': answer,
                    })

            if not answered:
                # Recording an all-zero tally would look like a real
                # measurement of a population that said nothing.
                self._record_failure(event_index, item.name,
                                     "no agent produced a usable answer")
                continue

            # The denominator is the number of agents who actually answered,
            # so the shares partition a population that is known rather than
            # assumed. answered < len(entities) is reported as a failure above
            # for each agent that dropped out.
            shares = _apportion(counts, answered)

            with self._lock:
                self._history[item.name].append((event_index, {
                    'shares': shares,
                    'counts': dict(counts),
                    'n_responding': answered,
                    'n_population': len(self._entities),
                    'timestamp': timestamp,
                }))

        with self._lock:
            self._administrations += 1

    def _ask(self, entity: Any, item: ProbeItem) -> Optional[str]:
        """Put one item to one agent and return its chosen option."""
        agent_name = getattr(entity, 'name', '<unnamed>')
        try:
            prompt = self._build_prompt(entity, agent_name, item)
            index, answer, _ = self._model.sample_choice(
                prompt=prompt,
                responses=item.options,
            )
            # sample_choice constrains the answer to the option list, so no
            # parsing or fuzzy matching is needed and none is attempted.
            if 0 <= index < len(item.options):
                return item.options[index]
            logger.warning(
                "Probe answer index %s out of range for item '%s'; dropping.",
                index, item.name,
            )
            self._record_failure(self._event_counter, item.name,
                                 f"{agent_name}: answer index out of range")
            return None
        except Exception as exc:  # noqa: BLE001 - a probe must not kill a run
            logger.warning(
                "Probe failed for %s on item '%s': %s", agent_name,
                item.name, exc,
            )
            self._record_failure(self._event_counter, item.name,
                                 f"{agent_name}: {exc}")
            return None

    def _build_prompt(self, entity: Any, agent_name: str,
                      item: ProbeItem) -> str:
        """Compose the survey prompt from the agent's own accumulated memory."""
        memories = self._recent_memories(entity)
        recalled = "\n".join(f"- {m}" for m in memories) if memories else \
            "- (nothing recalled yet)"

        return (
            f"You are {agent_name}.\n\n"
            f"This is what you have experienced and read so far, most recent "
            f"last:\n{recalled}\n\n"
            f"Answer the following question as {agent_name} would answer it "
            f"right now, based only on the above. This is a private survey; "
            f"no one else will see your answer, so answer honestly rather "
            f"than persuasively.\n\n"
            f"Question: {item.question}"
        )

    def _recent_memories(self, entity: Any) -> List[str]:
        """Return an entity's most recent memories without disturbing it.

        Reads the memory bank directly rather than through the memory
        component's retrieve_recent(). That method raises if the entity
        happens to be in the UPDATE phase, and under the asynchronous engine
        every entity is on its own thread, so it frequently is. The bank's own
        accessor takes the bank lock and returns a copy, which is both safe to
        call from another thread and free of side effects on the entity.
        """
        bank = self._find_memory_bank(entity)
        if bank is None:
            return []
        try:
            frame = bank.get_data_frame()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not read memory for %s: %s",
                getattr(entity, 'name', '<unnamed>'), exc,
            )
            return []
        if 'text' not in getattr(frame, 'columns', []):
            return []
        texts = [str(t) for t in frame['text'].tolist()]
        return texts[-self._memory_limit:]

    @staticmethod
    def _find_memory_bank(entity: Any) -> Optional[Any]:
        """Locate an entity's memory bank, or None if it has no reachable one."""
        components = {}
        for accessor in ('get_all_context_components', 'context_components'):
            try:
                value = getattr(entity, accessor, None)
                if callable(value):
                    value = value()
                if isinstance(value, dict) and value:
                    components = value
                    break
            except Exception:  # noqa: BLE001
                continue

        for component in components.values():
            bank = getattr(component, '_memory_bank', None)
            if bank is not None and hasattr(bank, 'get_data_frame'):
                return bank
        return None

    def _record_failure(self, event_index: int, item_name: str,
                        reason: str) -> None:
        """Record a probe that did not return a usable answer.

        A dropped response silently shrinks the denominator, so it is recorded
        rather than absorbed: an item answered by half the population is a
        different measurement from one answered by all of it.
        """
        with self._lock:
            self._failures.append({
                'event_index': event_index,
                'item': item_name,
                'reason': reason,
            })

    # --- Reporting --------------------------------------------------------

    def get_history(self, item_name: str) -> List[tuple]:
        """Return the tallied series for one item."""
        with self._lock:
            return list(self._history.get(item_name, []))

    def get_all_history(self) -> Dict[str, List[tuple]]:
        with self._lock:
            return {k: list(v) for k, v in self._history.items()}

    def get_responses(self) -> List[Dict[str, Any]]:
        """Return every individual answer recorded."""
        with self._lock:
            return list(self._responses)

    def get_failures(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._failures)

    def get_integrity_summary(self) -> Dict[str, Any]:
        """Report what the probe actually managed to measure.

        Reported alongside the series so a reader can tell a real population
        shift from an instrument that stopped working partway through.
        """
        with self._lock:
            per_item = {}
            for name, series in self._history.items():
                responding = [entry[1]['n_responding'] for entry in series]
                per_item[name] = {
                    'administrations': len(series),
                    'min_responding': min(responding) if responding else 0,
                    'max_responding': max(responding) if responding else 0,
                }
            return {
                'population': len(self._entities),
                'items': [item.name for item in self._items],
                'interval': self._interval,
                'administrations': self._administrations,
                'events_seen': self._event_counter,
                'failures': len(self._failures),
                'per_item': per_item,
            }


def create_agent_probe_component(
    model: language_model.LanguageModel,
    items: Sequence[Any],
    interval: int = 25,
    memory_limit: int = DEFAULT_MEMORY_LIMIT,
) -> Optional[AgentProbeComponent]:
    """Build a probe from plain dicts or ProbeItem instances.

    Returns None when no items are configured, so callers can wire the probe
    unconditionally and have it cost nothing when unused.
    """
    parsed: List[ProbeItem] = []
    for raw in items or []:
        if isinstance(raw, ProbeItem):
            parsed.append(raw)
            continue
        parsed.append(ProbeItem(
            name=raw['name'],
            question=raw['question'],
            options=list(raw['options']),
            description=raw.get('description', ''),
        ))

    if not parsed:
        return None

    return AgentProbeComponent(
        model=model,
        items=parsed,
        interval=interval,
        memory_limit=memory_limit,
    )
