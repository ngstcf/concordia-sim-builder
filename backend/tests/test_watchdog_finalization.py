"""Tests for the watchdog's handling of a run's quiet tail.

A simulation goes silent for two different reasons and the watchdog has to
tell them apart. It hangs, in which case an emergency copy of the run is worth
writing; or its engine loop has ended and it is building the results log, in
which case the run is finishing normally and an emergency copy is a large
wasted write of data that is about to be saved properly anyway.
"""

import pytest

from backend.services.simulation_runner import (
    _classify_watchdog_state,
    _mark_run_loop_completion,
)


class _Engine:
    def __init__(self, body=None):
        self.calls = []
        self._body = body

    def run_loop(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self._body is not None:
            return self._body()
        return "loop result"


class _Sim:
    """Minimal stand-in exposing the one attribute the guard reaches for."""

    def __init__(self, engine):
        self._engine = engine


# --- Marking the transition ----------------------------------------------

def test_flag_is_unset_until_the_loop_returns():
    flag = [False]
    seen = []

    engine = _Engine(body=lambda: seen.append(flag[0]))
    with _mark_run_loop_completion(_Sim(engine), flag):
        assert flag[0] is False  # play() has not started the loop yet
        engine.run_loop(max_steps=3)

    # Inside the loop the run is still live, so the watchdog must stay armed.
    assert seen == [False]
    assert flag[0] is True


def test_flag_is_set_when_the_loop_raises():
    """The error path does heavy work of its own and is not a hang either."""
    flag = [False]

    def _boom():
        raise RuntimeError("engine failed")

    engine = _Engine(body=_boom)
    with _mark_run_loop_completion(_Sim(engine), flag):
        with pytest.raises(RuntimeError):
            engine.run_loop()

    assert flag[0] is True


def test_arguments_and_return_value_pass_through():
    flag = [False]
    engine = _Engine()
    sim = _Sim(engine)

    with _mark_run_loop_completion(sim, flag):
        result = sim._engine.run_loop("premise", max_steps=20)

    assert result == "loop result"
    assert engine.calls == [(("premise",), {"max_steps": 20})]


def test_the_engine_is_left_exactly_as_found():
    """No instance attribute may be left shadowing the class method."""
    flag = [False]
    engine = _Engine()

    with _mark_run_loop_completion(_Sim(engine), flag):
        assert 'run_loop' in engine.__dict__  # wrapped for the duration
    assert 'run_loop' not in engine.__dict__

    # And the unwrapped method no longer reports completion.
    flag[0] = False
    engine.run_loop()
    assert flag[0] is False


def test_the_engine_is_left_as_found_after_an_error():
    flag = [False]
    engine = _Engine()

    with pytest.raises(ValueError):
        with _mark_run_loop_completion(_Sim(engine), flag):
            raise ValueError("something else went wrong")

    assert 'run_loop' not in engine.__dict__


def test_an_engine_owning_run_loop_keeps_its_own_attribute():
    flag = [False]
    engine = _Engine()
    own = lambda *a, **k: "own result"
    engine.run_loop = own

    with _mark_run_loop_completion(_Sim(engine), flag):
        pass

    assert engine.run_loop is own


def test_simulation_without_an_engine_is_a_no_op():
    """Unknown simulation shapes keep the previous watchdog behaviour."""
    flag = [False]

    class _NoEngine:
        pass

    with _mark_run_loop_completion(_NoEngine(), flag):
        pass

    assert flag[0] is False


# --- Classifying the silence ---------------------------------------------

def _state(**overrides):
    kwargs = dict(
        llm_stalled=True,
        time_since_progress=900.0,
        timeout=600.0,
        run_loop_finished=False,
    )
    kwargs.update(overrides)
    return _classify_watchdog_state(**kwargs)


def test_silence_with_the_loop_still_running_is_a_hang():
    assert _state() == 'hung'


def test_silence_while_building_the_results_log_is_not_a_hang():
    """The regression this guard exists for.

    Serializing a large run takes minutes, does no LLM work, and emits no step
    events, so every input the watchdog reads looks exactly like a hang.
    """
    assert _state(run_loop_finished=True) == 'finalizing'


def test_live_llm_work_is_never_a_hang():
    assert _state(llm_stalled=False) == 'ok'
    assert _state(llm_stalled=False, run_loop_finished=True) == 'ok'


def test_recent_progress_is_never_a_hang():
    assert _state(time_since_progress=599.0) == 'ok'


def test_timeout_boundary_is_exclusive():
    assert _state(time_since_progress=600.0) == 'ok'
    assert _state(time_since_progress=600.1) == 'hung'


def test_disabled_watchdog_reports_ok_in_both_phases():
    assert _state(enabled=False) == 'ok'
    assert _state(enabled=False, run_loop_finished=True) == 'ok'


def test_absent_timeout_reports_ok():
    assert _state(timeout=None) == 'ok'
    assert _state(timeout=0) == 'ok'
