"""Tests for cross-variable invariants on grounded variables.

The scenario throughout is two support percentages that describe one
population between them. Each is individually a legal 0-100 value, so
per-variable validation accepts any pair; only a declared joint constraint
rejects a pair whose total is impossible.
"""

import logging

import pytest

from backend.prefabs.grounded_variables import (
    create_grounded_variables_component,
)


class _NoModel:
    """Stands in for a language model that must never be called.

    Every event below carries an explicit [VARIABLES: ...] tag, so reaching
    the LLM fallback would mean the tag parser silently failed.
    """

    def sample_text(self, prompt, **kwargs):  # pragma: no cover
        raise AssertionError("LLM fallback should not be reached")


POLL_VARS = [
    {"name": "candidate_a_support", "variable_type": "percentage",
     "description": "", "default_value": 40,
     "min_value": 0, "max_value": 100, "group": "poll"},
    {"name": "candidate_b_support", "variable_type": "percentage",
     "description": "", "default_value": 35,
     "min_value": 0, "max_value": 100, "group": "poll"},
    {"name": "undecided_share", "variable_type": "percentage",
     "description": "", "default_value": 25,
     "min_value": 0, "max_value": 100, "group": "poll"},
]

MEMBERS = ("candidate_a_support", "candidate_b_support", "undecided_share")

# Individually legal, jointly impossible: 88 + 74 + 11 describes 173% of one
# population.
IMPOSSIBLE = ("[VARIABLES: candidate_a_support=88, candidate_b_support=74,"
              " undecided_share=11]")
IMPOSSIBLE_SUM = 173.0


def _component(variables=None, groups=None):
    return create_grounded_variables_component(
        model=_NoModel(),
        variable_configs=variables if variables is not None else POLL_VARS,
        variable_groups=groups,
    )


def test_impossible_total_is_repaired_and_recorded():
    c = _component()
    c.post_act(IMPOSSIBLE)

    assert sum(c.get_value(n) for n in MEMBERS) == pytest.approx(100.0, abs=0.01)

    # Renormalization preserves the reported ratio between the two candidates.
    assert c.get_value("candidate_a_support") == pytest.approx(88 / IMPOSSIBLE_SUM * 100, abs=0.01)
    assert c.get_value("candidate_b_support") == pytest.approx(74 / IMPOSSIBLE_SUM * 100, abs=0.01)

    violations = c.get_violations()
    assert len(violations) == 1
    assert violations[0]["kind"] == "group_sum"
    assert violations[0]["observed_sum"] == pytest.approx(IMPOSSIBLE_SUM)
    assert violations[0]["action"] == "renormalize"


def test_plausible_total_passes_untouched():
    c = _component()
    c.post_act("[VARIABLES: candidate_a_support=50, candidate_b_support=44,"
               " undecided_share=6]")

    assert c.get_value("candidate_a_support") == 50
    assert c.get_value("candidate_b_support") == 44
    assert c.get_violations() == []


def test_tolerance_boundary_is_inclusive():
    c = _component()
    # Sums to 101: exactly at the default tolerance, so no repair.
    c.post_act("[VARIABLES: candidate_a_support=51, candidate_b_support=44,"
               " undecided_share=6]")
    assert c.get_value("candidate_a_support") == 51
    assert c.get_violations() == []


def test_reject_restores_previous_values():
    groups = [{"name": "poll", "members": list(MEMBERS),
               "sums_to": 100, "on_violation": "reject"}]
    c = _component(groups=groups)
    c.post_act(IMPOSSIBLE)

    # Back to the declared defaults, which is the last state known to be valid.
    assert c.get_value("candidate_a_support") == 40
    assert c.get_value("candidate_b_support") == 35
    assert c.get_value("undecided_share") == 25
    assert c.get_violations()[0]["action"] == "reject"


def test_flag_records_without_changing_values():
    groups = [{"name": "poll", "members": list(MEMBERS),
               "sums_to": 100, "on_violation": "flag"}]
    c = _component(groups=groups)
    c.post_act(IMPOSSIBLE)

    assert c.get_value("candidate_a_support") == 88
    assert c.get_value("candidate_b_support") == 74
    assert c.get_violations()[0]["action"] == "flag"


def test_history_records_the_repaired_values():
    """The exported series must carry what was enforced, not what was claimed."""
    c = _component()
    c.post_act(IMPOSSIBLE)

    _, value = c.get_history("candidate_a_support")[-1]
    assert value == pytest.approx(88 / IMPOSSIBLE_SUM * 100, abs=0.01)


def test_error_cannot_accumulate_across_updates():
    """History is appended at every phase, so drift gets many chances."""
    c = _component()
    for _ in range(50):
        c.post_act(IMPOSSIBLE)
        assert sum(c.get_value(n) for n in MEMBERS) == pytest.approx(100.0, abs=0.01)


def test_ungrouped_variables_are_unaffected():
    """Scenarios that declare no group must behave exactly as before."""
    plain = [dict(v) for v in POLL_VARS]
    for v in plain:
        v.pop("group")
    c = _component(variables=plain)
    c.post_act(IMPOSSIBLE)

    assert c.get_value("candidate_a_support") == 88
    assert c.get_value("candidate_b_support") == 74
    assert c.get_violations() == []


# --- Cumulative counters -------------------------------------------------

EXPOSURE = {
    "name": "exposure_count", "variable_type": "numerical",
    "description": "", "default_value": 0, "min_value": 0,
    "cumulative": True,
}


def test_cumulative_counter_growth_is_capped():
    """A per-participant count cannot outrun the population that produces it."""
    c = _component(variables=[dict(EXPOSURE, max_delta=20)])
    c.post_act("[VARIABLES: exposure_count=6]")
    assert c.get_value("exposure_count") == 6

    # Without a cap a single update can move a running total arbitrarily far,
    # and a monotonic counter never recovers.
    c.post_act("[VARIABLES: exposure_count=12000000]")
    assert c.get_value("exposure_count") == 26  # 6 + 20

    assert [v["kind"] for v in c.get_violations()] == ["max_delta"]


def test_cumulative_counter_still_never_decreases():
    c = _component(variables=[dict(EXPOSURE, max_delta=20)])
    c.post_act("[VARIABLES: exposure_count=15]")
    c.post_act("[VARIABLES: exposure_count=3]")
    assert c.get_value("exposure_count") == 15


def test_unbounded_cumulative_counter_warns_at_construction(caplog):
    with caplog.at_level(logging.WARNING):
        _component(variables=[dict(EXPOSURE)])
    assert any("unbounded above" in r.getMessage() for r in caplog.records)


def test_bounded_cumulative_counter_does_not_warn(caplog):
    with caplog.at_level(logging.WARNING):
        _component(variables=[dict(EXPOSURE, max_delta=20)])
    assert not caplog.records


# --- Reporting -----------------------------------------------------------

def test_integrity_summary_reports_a_clean_run():
    c = _component()
    c.post_act("[VARIABLES: candidate_a_support=50, candidate_b_support=44,"
               " undecided_share=6]")

    summary = c.get_integrity_summary()
    assert summary["violations"] == 0
    assert summary["updates_seen"] == 1
    assert summary["groups_declared"] == ["poll"]


def test_integrity_summary_counts_by_kind():
    c = _component()
    for _ in range(3):
        c.post_act(IMPOSSIBLE)

    summary = c.get_integrity_summary()
    assert summary["violations"] == 3
    assert summary["violations_by_kind"] == {"group_sum": 3}


def test_group_naming_an_unknown_variable_warns(caplog):
    groups = [{"name": "poll",
               "members": ["candidate_a_support", "candidate_b_support", "turnout"],
               "sums_to": 100}]
    with caplog.at_level(logging.WARNING):
        c = _component(groups=groups)
    assert any("undeclared" in r.getMessage() for r in caplog.records)

    # The declared members still get enforced.
    c.post_act("[VARIABLES: candidate_a_support=88, candidate_b_support=74]")
    assert c.get_value("candidate_a_support") + c.get_value("candidate_b_support") == \
        pytest.approx(100.0, abs=0.01)
