"""Tests for the per-agent survey probe.

The property under test throughout is that the probe measures by counting.
A tally over a known roster cannot produce shares that fail to sum to 100, a
residual category that never moves, or a total with no ceiling, because none
of those arithmetic outcomes is reachable from counting answers.
"""

import json

import pandas as pd
import pytest

from backend.prefabs.agent_probe import (
    AgentProbeComponent,
    ProbeItem,
    create_agent_probe_component,
)

ITEM = ProbeItem(
    name="vote_intention",
    question="Which candidate do you currently intend to vote for?",
    options=["Candidate A", "Candidate B", "Undecided"],
)


class _Bank:
    """Stands in for an AssociativeMemoryBank."""

    def __init__(self, texts):
        self.texts = list(texts)
        self.reads = 0

    def get_data_frame(self):
        self.reads += 1
        return pd.DataFrame({"text": list(self.texts),
                             "embedding": [None] * len(self.texts)})


class _MemoryComponent:
    def __init__(self, texts):
        self._memory_bank = _Bank(texts)


class _Entity:
    """Minimal entity exposing only what the probe is allowed to touch."""

    def __init__(self, name, memories=()):
        self.name = name
        self._memory = _MemoryComponent(memories)
        self.act_calls = 0
        self.observe_calls = 0

    def get_all_context_components(self):
        return {"memory": self._memory}

    def act(self, *a, **k):  # pragma: no cover - must never be called
        self.act_calls += 1
        raise AssertionError("the probe must not make an entity act")

    def observe(self, *a, **k):  # pragma: no cover - must never be called
        self.observe_calls += 1
        raise AssertionError("the probe must not write to an entity")


class _ScriptedModel:
    """Answers each agent according to a fixed script."""

    def __init__(self, answers):
        self.answers = dict(answers)
        self.prompts = []

    def sample_choice(self, prompt, responses, **kwargs):
        self.prompts.append(prompt)
        for name, answer in self.answers.items():
            if f"You are {name}." in prompt:
                return responses.index(answer), answer, {}
        return 0, responses[0], {}


def _probe(model, entities, items=(ITEM,), interval=1, **kwargs):
    component = AgentProbeComponent(
        model=model, items=list(items), interval=interval, **kwargs
    )
    component.bind_entities(entities)
    return component


def _fire(component, times=1):
    for _ in range(times):
        component.post_act("some narrated event")


# --- The invariant the probe exists to guarantee -------------------------

def test_shares_sum_to_100_by_construction():
    entities = [_Entity(f"Agent{i}") for i in range(6)]
    model = _ScriptedModel({
        "Agent0": "Candidate A", "Agent1": "Candidate A",
        "Agent2": "Candidate B", "Agent3": "Candidate B",
        "Agent4": "Undecided", "Agent5": "Undecided",
    })
    component = _probe(model, entities)
    _fire(component)

    _, entry = component.get_history("vote_intention")[0]
    assert sum(entry["shares"].values()) == pytest.approx(100.0)
    assert entry["counts"] == {"Candidate A": 2, "Candidate B": 2,
                               "Undecided": 2}
    assert entry["n_responding"] == 6
    assert entry["n_population"] == 6


def test_a_lopsided_population_cannot_exceed_its_own_size():
    """Saturation is only reachable if the agents actually say so."""
    entities = [_Entity(f"Agent{i}") for i in range(6)]
    # Five of six for A is the most one dissenter allows.
    model = _ScriptedModel({f"Agent{i}": "Candidate A" for i in range(5)}
                           | {"Agent5": "Candidate B"})
    component = _probe(model, entities)
    _fire(component)

    _, entry = component.get_history("vote_intention")[0]
    assert entry["shares"]["Candidate A"] == pytest.approx(500 / 6, abs=0.01)
    assert entry["shares"]["Candidate A"] < 100.0
    assert sum(entry["shares"].values()) == pytest.approx(100.0)


def test_undecided_moves_only_when_an_agent_selects_it():
    entities = [_Entity(f"Agent{i}") for i in range(4)]
    decided = _ScriptedModel({f"Agent{i}": "Candidate A" for i in range(4)})
    component = _probe(decided, entities)
    _fire(component)
    _, first = component.get_history("vote_intention")[0]
    assert first["shares"]["Undecided"] == 0.0

    component._model = _ScriptedModel(
        {"Agent0": "Undecided", "Agent1": "Undecided",
         "Agent2": "Candidate A", "Agent3": "Candidate A"}
    )
    _fire(component)
    _, second = component.get_history("vote_intention")[1]
    assert second["shares"]["Undecided"] == pytest.approx(50.0)


def test_every_answer_is_attributable_to_an_agent():
    entities = [_Entity("Ana"), _Entity("Ben")]
    model = _ScriptedModel({"Ana": "Candidate A", "Ben": "Undecided"})
    component = _probe(model, entities)
    _fire(component)

    by_agent = {r["agent"]: r["answer"] for r in component.get_responses()}
    assert by_agent == {"Ana": "Candidate A", "Ben": "Undecided"}


# --- Non-invasiveness ----------------------------------------------------

def test_the_probe_never_acts_or_observes_on_an_entity():
    entities = [_Entity("Ana"), _Entity("Ben")]
    component = _probe(_ScriptedModel({}), entities)
    _fire(component, times=3)

    for entity in entities:
        assert entity.act_calls == 0
        assert entity.observe_calls == 0


def test_the_probe_contributes_nothing_to_game_master_context():
    """A measurement fed back into narration would perturb what it measures."""
    component = _probe(_ScriptedModel({}), [_Entity("Ana")])
    assert component.pre_act("agent_probe") == ''
    assert component.post_act("an event") == ''


def test_the_agents_own_memory_reaches_its_prompt():
    entity = _Entity("Ana", memories=["You read a claim about the election.",
                                      "You replied to a neighbor."])
    model = _ScriptedModel({"Ana": "Undecided"})
    component = _probe(model, [entity])
    _fire(component)

    prompt = model.prompts[0]
    assert "You are Ana." in prompt
    assert "You replied to a neighbor." in prompt
    assert ITEM.question in prompt


def test_memory_is_truncated_to_the_configured_limit():
    entity = _Entity("Ana", memories=[f"memory {i}" for i in range(100)])
    model = _ScriptedModel({"Ana": "Undecided"})
    component = _probe(model, [entity], memory_limit=5)
    _fire(component)

    prompt = model.prompts[0]
    assert "memory 99" in prompt      # most recent kept
    assert "memory 94" not in prompt  # beyond the limit dropped


# --- Cadence -------------------------------------------------------------

def test_the_probe_fires_only_on_its_interval():
    component = _probe(_ScriptedModel({}), [_Entity("Ana")], interval=5)
    _fire(component, times=4)
    assert component.get_history("vote_intention") == []

    _fire(component)
    assert len(component.get_history("vote_intention")) == 1

    _fire(component, times=5)
    assert len(component.get_history("vote_intention")) == 2


def test_events_are_stamped_on_the_series():
    """The asynchronous engine has no shared step boundary, so the game master
    event index is the only clock every agent is measured against."""
    component = _probe(_ScriptedModel({}), [_Entity("Ana")], interval=3)
    _fire(component, times=9)

    assert [index for index, _ in component.get_history("vote_intention")] \
        == [3, 6, 9]


def test_a_probe_with_no_entities_records_nothing():
    component = AgentProbeComponent(_ScriptedModel({}), [ITEM], interval=1)
    _fire(component, times=3)
    assert component.get_history("vote_intention") == []


# --- Failure is reported, not absorbed -----------------------------------

class _FlakyModel:
    def __init__(self, failing_names):
        self.failing = set(failing_names)

    def sample_choice(self, prompt, responses, **kwargs):
        for name in self.failing:
            if f"You are {name}." in prompt:
                raise RuntimeError("provider timeout")
        return 0, responses[0], {}


def test_a_dropped_response_shrinks_the_denominator_visibly():
    entities = [_Entity(f"Agent{i}") for i in range(4)]
    component = _probe(_FlakyModel({"Agent2", "Agent3"}), entities)
    _fire(component)

    _, entry = component.get_history("vote_intention")[0]
    assert entry["n_responding"] == 2
    assert entry["n_population"] == 4
    # Still a valid partition, but of a population the reader can see is short.
    assert sum(entry["shares"].values()) == pytest.approx(100.0)
    assert len(component.get_failures()) == 2


def test_a_total_failure_records_no_measurement_at_all():
    """An all-zero tally would read as a population that answered nothing."""
    entities = [_Entity("Ana"), _Entity("Ben")]
    component = _probe(_FlakyModel({"Ana", "Ben"}), entities)
    _fire(component)

    assert component.get_history("vote_intention") == []
    assert len(component.get_failures()) == 3  # two agents, then the item

def test_one_failing_agent_does_not_stop_the_run():
    entities = [_Entity("Ana"), _Entity("Ben")]
    component = _probe(_FlakyModel({"Ana"}), entities)
    _fire(component)  # must not raise
    assert component.get_history("vote_intention")[0][1]["n_responding"] == 1


def test_an_entity_without_reachable_memory_still_answers():
    class _Bare:
        name = "Bare"

    component = _probe(_ScriptedModel({}), [_Bare()])
    _fire(component)
    assert component.get_history("vote_intention")[0][1]["n_responding"] == 1


# --- Reporting and resume ------------------------------------------------

def test_integrity_summary_describes_what_was_measured():
    entities = [_Entity(f"Agent{i}") for i in range(4)]
    component = _probe(_FlakyModel({"Agent3"}), entities, interval=2)
    _fire(component, times=4)

    summary = component.get_integrity_summary()
    assert summary["population"] == 4
    assert summary["administrations"] == 2
    assert summary["events_seen"] == 4
    assert summary["failures"] == 2
    assert summary["per_item"]["vote_intention"]["min_responding"] == 3


def test_state_round_trips_through_a_checkpoint():
    entities = [_Entity("Ana"), _Entity("Ben")]
    model = _ScriptedModel({"Ana": "Candidate A", "Ben": "Undecided"})
    original = _probe(model, entities)
    _fire(original, times=2)

    restored = _probe(model, entities)
    restored.set_state(original.get_state())

    assert restored.get_history("vote_intention") == \
        original.get_history("vote_intention")
    assert restored.get_responses() == original.get_responses()
    assert json.loads(restored.get_state())["event_counter"] == 2


def test_unreadable_state_does_not_break_a_resume():
    component = _probe(_ScriptedModel({}), [_Entity("Ana")])
    component.set_state("not json")
    component.set_state("")
    _fire(component)
    assert len(component.get_history("vote_intention")) == 1


# --- Configuration -------------------------------------------------------

def test_an_item_needs_at_least_two_options():
    with pytest.raises(ValueError, match="at least two options"):
        ProbeItem(name="x", question="q?", options=["only"])


def test_duplicate_options_are_rejected():
    with pytest.raises(ValueError, match="duplicate options"):
        ProbeItem(name="x", question="q?", options=["a", "b", "a"])


def test_factory_builds_from_plain_dicts():
    component = create_agent_probe_component(
        model=_ScriptedModel({}),
        items=[{"name": "vote_intention", "question": "Who?",
                "options": ["A", "B"]}],
    )
    assert isinstance(component, AgentProbeComponent)


def test_factory_returns_none_when_unconfigured():
    """So callers can wire the probe unconditionally at no cost."""
    assert create_agent_probe_component(_ScriptedModel({}), []) is None
    assert create_agent_probe_component(_ScriptedModel({}), None) is None


# --- Reported precision must not break the partition ---------------------

@pytest.mark.parametrize("n_agents", [3, 6, 7, 9, 11, 13, 20, 50, 100])
def test_shares_close_exactly_for_awkward_population_sizes(n_agents):
    """Rounding each share on its own reintroduces the defect being fixed.

    Three equal shares of six agents are 33.3333 apiece under independent
    rounding, and sum to 99.9999.
    """
    entities = [_Entity(f"Agent{i}") for i in range(n_agents)]
    answers = {}
    for i in range(n_agents):
        answers[f"Agent{i}"] = ITEM.options[i % 3]
    component = _probe(_ScriptedModel(answers), entities)
    _fire(component)

    _, entry = component.get_history("vote_intention")[0]
    assert sum(entry["shares"].values()) == 100.0
    assert sum(entry["counts"].values()) == n_agents


def test_apportionment_stays_faithful_to_the_counts():
    """Closing the total must not move a share off its true value."""
    entities = [_Entity(f"Agent{i}") for i in range(3)]
    component = _probe(_ScriptedModel(
        {"Agent0": "Candidate A", "Agent1": "Candidate A",
         "Agent2": "Candidate B"}), entities)
    _fire(component)

    _, entry = component.get_history("vote_intention")[0]
    assert entry["shares"]["Candidate A"] == pytest.approx(200 / 3, abs=1e-4)
    assert entry["shares"]["Candidate B"] == pytest.approx(100 / 3, abs=1e-4)
    assert entry["shares"]["Undecided"] == 0.0
