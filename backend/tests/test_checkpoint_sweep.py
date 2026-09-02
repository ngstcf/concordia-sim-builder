"""Tests for deciding which checkpoints are safe to sweep.

Two things are being pinned. One is that a completed run's checkpoints are
recognised as redundant, which is where the disk space is: the emergency copy
alone is a second full state file per run. The other is that an unfinished
run's most advanced checkpoint is *not* swept, because it is the only resume
point that run has, and the sweep used to take it.
"""

import pytest

from backend.services.simulation_runner import _retire_superseded_checkpoint
from backend.utils.checkpoint_sweep import parse, partition

SLUG = "Agent_A_Agent_B_A_town_meeting_about_the_new_bridge"


def artifacts(stamp, marker=""):
    """The three files one checkpoint or final save writes."""
    base = f"{stamp}_{SLUG}{marker}"
    return [f"{base}.html", f"{base}.metadata.json", f"{base}.state.json"]


def emergency(stamp):
    return artifacts(stamp, "_EMERGENCY_CHECKPOINT")


def watchdog(stamp, step):
    return artifacts(stamp, f"_WATCHDOG_EMERGENCY_step{step}")


def checkpoint(stamp, step):
    return artifacts(stamp, f"_checkpoint_step{step}")


# --- Parsing --------------------------------------------------------------

@pytest.mark.parametrize("name, kind, ext, step", [
    (f"20260901_120003_{SLUG}.html", "final", "html", -1),
    (f"20260901_120003_{SLUG}.state.json", "final", "state", -1),
    (f"20260901_120000_{SLUG}_EMERGENCY_CHECKPOINT.state.json",
     "emergency", "state", -1),
    (f"20260901_120000_{SLUG}_WATCHDOG_EMERGENCY_step7.html",
     "watchdog", "html", 7),
    (f"20260901_120000_{SLUG}_checkpoint_step15.metadata.json",
     "checkpoint", "meta", 15),
])
def test_parses_every_naming_form(name, kind, ext, step):
    parsed = parse(name)
    assert parsed is not None
    assert (parsed.kind, parsed.ext, parsed.step) == (kind, ext, step)
    # Every form of one scenario has to reduce to the same slug, or the
    # artifacts of a run cannot be grouped together at all.
    assert parsed.slug == SLUG


@pytest.mark.parametrize("name", [
    "notes.txt",                      # not a log artifact
    "batch_summary.json",             # no timestamp
    "20260901_9999_short_stamp.html",  # malformed stamp
])
def test_rejects_what_is_not_a_log_artifact(name):
    assert parse(name) is None


def test_unrecognised_names_are_spared_not_swept():
    sweep = partition(["notes.txt"])
    assert sweep.redundant == []
    assert sweep.spared == ["notes.txt"]


# --- A run that finished --------------------------------------------------

def test_completed_run_makes_its_emergency_copy_redundant():
    names = emergency("20260901_120000") + artifacts("20260901_120003")
    sweep = partition(names)

    assert set(sweep.redundant) == set(emergency("20260901_120000"))
    assert sweep.unfinished_runs == 0


def test_final_artifacts_are_never_swept():
    names = emergency("20260901_120000") + artifacts("20260901_120003")
    sweep = partition(names)

    for name in artifacts("20260901_120003"):
        assert name in sweep.spared
        assert name not in sweep.redundant


def test_completed_run_makes_its_step_checkpoints_redundant():
    names = (checkpoint("20260901_120500", 5)
             + checkpoint("20260901_121000", 10)
             + emergency("20260901_121500")
             + artifacts("20260901_121502"))
    sweep = partition(names)

    assert len(sweep.redundant) == 9
    assert set(sweep.spared) == set(artifacts("20260901_121502"))


def test_emergency_copies_are_not_stranded_into_the_next_run():
    """`.` sorts before `_`, which once split a run across the boundary.

    Sorting these names by string puts the final `<slug>.html` ahead of the
    emergency `<slug>_EMERGENCY_CHECKPOINT.html` even though the emergency
    copy was written first, which used to leave the emergency files grouped
    with whatever ran next -- and so judged against the wrong run.
    """
    names = (emergency("20260901_120000") + artifacts("20260901_120003")
             + checkpoint("20260901_130000", 5))
    sweep = partition(names)

    # The first run finished, so its emergency copy goes; the second run has
    # not finished, so its step checkpoint stays.
    assert set(sweep.redundant) == set(emergency("20260901_120000"))
    assert set(checkpoint("20260901_130000", 5)) <= set(sweep.spared)
    assert sweep.unfinished_runs == 1


# --- A run that did not finish -------------------------------------------

def test_unfinished_run_keeps_its_emergency_copy():
    names = checkpoint("20260901_120500", 5) + emergency("20260901_121500")
    sweep = partition(names)

    assert set(sweep.spared) == set(emergency("20260901_121500"))
    assert set(sweep.redundant) == set(checkpoint("20260901_120500", 5))
    assert sweep.unfinished_runs == 1


def test_unfinished_run_without_a_recovery_copy_keeps_its_top_step():
    """A hard kill leaves no emergency copy, so the top checkpoint is it."""
    names = (checkpoint("20260901_120500", 5)
             + checkpoint("20260901_121000", 10))
    sweep = partition(names)

    assert set(sweep.spared) == set(checkpoint("20260901_121000", 10))
    assert set(sweep.redundant) == set(checkpoint("20260901_120500", 5))


def test_top_step_is_chosen_by_step_number_not_by_name():
    """step9 must not outrank step10 -- these numbers are not zero padded."""
    names = (checkpoint("20260901_120900", 9)
             + checkpoint("20260901_121000", 10))
    sweep = partition(names)

    assert set(sweep.spared) == set(checkpoint("20260901_121000", 10))


def test_unfinished_run_keeps_its_watchdog_copy_over_a_step_checkpoint():
    names = checkpoint("20260901_120500", 5) + watchdog("20260901_121500", 8)
    sweep = partition(names)

    assert set(sweep.spared) == set(watchdog("20260901_121500", 8))


def test_a_finished_run_does_not_condemn_a_later_unfinished_one():
    names = (emergency("20260901_120000") + artifacts("20260901_120003")
             + emergency("20260901_140000"))
    sweep = partition(names)

    assert set(sweep.spared) == (set(emergency("20260901_140000"))
                                 | set(artifacts("20260901_120003")))
    assert set(sweep.redundant) == set(emergency("20260901_120000"))
    assert sweep.unfinished_runs == 1


def test_checkpoint_before_a_later_completed_run_is_swept():
    """The one ambiguous case, pinned as documented.

    From the filenames alone a checkpoint sitting shortly before a final save
    cannot be told apart from a checkpoint that run wrote on its way through,
    so the sweep reads it as belonging to the completed run. Distinguishing
    them needs a run id in the filename.
    """
    names = (checkpoint("20260901_120500", 5)
             + emergency("20260901_121500") + artifacts("20260901_121502"))
    sweep = partition(names)

    assert set(checkpoint("20260901_120500", 5)) <= set(sweep.redundant)
    assert sweep.unfinished_runs == 0


# --- Retiring the emergency copy at the end of a run ----------------------

def _write(path, size):
    path.write_text("x" * size, encoding="utf-8")


def _make_pair(tmp_path, state_size=4096, final_state_size=4096):
    emergency_html = tmp_path / f"20260901_120000_{SLUG}_EMERGENCY_CHECKPOINT.html"
    _write(emergency_html, 100)
    _write(emergency_html.with_suffix(".metadata.json"), 50)
    _write(emergency_html.with_suffix(".state.json"), state_size)

    final_html = tmp_path / f"20260901_120003_{SLUG}.html"
    _write(final_html, 100)
    if final_state_size:
        _write(final_html.with_suffix(".state.json"), final_state_size)
    return emergency_html, final_html


def test_retires_the_whole_emergency_trio(tmp_path):
    emergency_html, final_html = _make_pair(tmp_path)

    reclaimed = _retire_superseded_checkpoint(emergency_html, final_html)

    assert not emergency_html.exists()
    assert not emergency_html.with_suffix(".metadata.json").exists()
    assert not emergency_html.with_suffix(".state.json").exists()
    assert reclaimed == 100 + 50 + 4096
    # The final artifacts are what the emergency copy insured; they stay.
    assert final_html.exists()
    assert final_html.with_suffix(".state.json").exists()


def test_keeps_the_state_when_it_is_not_the_expected_duplicate(tmp_path):
    """A size mismatch means the assumption broke; cost disk, not data."""
    emergency_html, final_html = _make_pair(
        tmp_path, state_size=8192, final_state_size=4096)

    reclaimed = _retire_superseded_checkpoint(emergency_html, final_html)

    assert emergency_html.with_suffix(".state.json").exists()
    assert reclaimed == 100 + 50


def test_retires_nothing_when_the_final_state_is_missing(tmp_path):
    """Then the emergency state is the only resumable copy on disk."""
    emergency_html, final_html = _make_pair(tmp_path, final_state_size=0)

    reclaimed = _retire_superseded_checkpoint(emergency_html, final_html)

    assert reclaimed == 0
    assert emergency_html.exists()
    assert emergency_html.with_suffix(".state.json").exists()


def test_retires_nothing_when_the_final_log_is_absent(tmp_path):
    emergency_html, _ = _make_pair(tmp_path)
    missing_final = tmp_path / f"20260901_120003_{SLUG}_absent.html"

    assert _retire_superseded_checkpoint(emergency_html, missing_final) == 0
    assert emergency_html.exists()
