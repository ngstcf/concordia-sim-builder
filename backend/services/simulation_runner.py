"""
Service for running simulations with streaming output.
"""
import asyncio
import contextlib
import json
import datetime
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator, Optional
from concordia.language_model import language_model

from backend.models.schemas import (
    SimulationConfig,
    LLMSettings,
    SimulationEvent,
    EventType,
    EngineType,
)
from backend.services.simulation_builder import build_simulation

# Import debug print utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.debug_print import debug_print
from backend.services.simulation_state import simulation_state

# Apply global patches to handle verbose LLM responses in binary choice questions
# This patches ActionSpec.validate() to normalize verbose yes/no responses
from backend.utils.thought_chain_fix import apply_all_patches
apply_all_patches()

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class SimulationCancelled(Exception):
    """Raised from within a step callback to stop the simulation loop."""
    pass


def _raw_log_to_html(raw_log) -> str:
    """Convert a raw simulation log to HTML using v2.4's structured logging."""
    from concordia.utils.structured_logging import SimulationLog
    sim_log = SimulationLog.from_raw_log(raw_log)
    return sim_log.to_html()


def _simulation_log_to_html(sim_log_or_result) -> str:
    """Convert a SimulationLog (or legacy result) to HTML string.

    In Concordia v2.4.0, sim.play() returns a SimulationLog object.
    In older versions it returned HTML strings directly.
    """
    from concordia.utils.structured_logging import SimulationLog
    if isinstance(sim_log_or_result, SimulationLog):
        return sim_log_or_result.to_html()
    return str(sim_log_or_result)


def _save_checkpoint_metadata(
    checkpoint_path: Path,
    config: SimulationConfig,
    llm_settings: LLMSettings,
    gm_llm_settings: LLMSettings | None,
    start_time: float,
    current_step: int,
    max_steps: int,
):
    """Save partial metadata alongside a checkpoint so analytics tabs work."""
    import json

    metadata = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "started_at": datetime.datetime.fromtimestamp(start_time).isoformat(),
        "completed_at": None,
        "elapsed_seconds": round(time.time() - start_time, 1),
        "is_checkpoint": True,
        "checkpoint_step": current_step,
        "max_steps": max_steps,
        "llm": {
            "provider": llm_settings.provider.value if hasattr(llm_settings.provider, 'value') else str(llm_settings.provider),
            "model": llm_settings.model_name,
        },
        "gm_llm": {
            "provider": gm_llm_settings.provider.value if hasattr(gm_llm_settings.provider, 'value') else str(gm_llm_settings.provider),
            "model": gm_llm_settings.model_name,
        } if gm_llm_settings else None,
        "premise": config.premise,
        "game_master": {
            "prefab": config.game_master.prefab,
            "name": config.game_master.name,
        },
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "prefab": agent.prefab,
                "goal": agent.goal or "",
                "memories_count": len(agent.memories) if agent.memories else 0,
            }
            for agent in config.agents
        ],
    }

    if hasattr(config.game_master, 'grounded_variables') and config.game_master.grounded_variables:
        metadata["game_master"]["grounded_variables"] = [
            var.model_dump() if hasattr(var, 'model_dump') else var
            for var in config.game_master.grounded_variables
        ]

    metadata_path = checkpoint_path.with_suffix('.metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


@contextlib.contextmanager
def _mark_run_loop_completion(sim, finished_flag: list):
    """Record when the engine's run loop ends, before sim.play() returns.

    play() does not return once the loop is done: it then builds a
    SimulationLog from the raw log, which on a large run is minutes of pure
    CPU with no LLM calls and no step events. From outside that is
    indistinguishable from a hang. The step counter cannot stand in for "the
    loop is done" because under the asynchronous engine it undercounts, so
    mark the transition at its source.

    Restores the original method on exit, and is a no-op if the simulation
    exposes no engine, leaving watchdog behavior exactly as it was.
    """
    engine = getattr(sim, '_engine', None)
    original_run_loop = getattr(engine, 'run_loop', None)
    if original_run_loop is None:
        yield
        return

    def _run_loop_marking_completion(*args, **kwargs):
        try:
            return original_run_loop(*args, **kwargs)
        finally:
            # Also on failure: the error path does heavy work of its own and
            # must not be mistaken for a hang either.
            finished_flag[0] = True

    # run_loop is normally a class method, so assigning it back on exit would
    # leave an instance attribute shadowing it. Remember which it was and undo
    # the wrap exactly, leaving the engine as it was found.
    shadowed_own_attribute = 'run_loop' in getattr(engine, '__dict__', {})
    engine.run_loop = _run_loop_marking_completion
    try:
        yield
    finally:
        if shadowed_own_attribute:
            engine.run_loop = original_run_loop
        else:
            try:
                del engine.run_loop
            except AttributeError:
                engine.run_loop = original_run_loop


def _classify_watchdog_state(
    *,
    llm_stalled: bool,
    time_since_progress: float,
    timeout: float | None,
    run_loop_finished: bool,
    enabled: bool = True,
) -> str:
    """Name what a quiet simulation is actually doing.

    Returns 'ok' while there is LLM work or recent progress, 'finalizing' when
    the run loop has ended and the results log is still being built, and
    'hung' when neither explains the silence. Only 'hung' warrants an
    emergency save; treating 'finalizing' as 'hung' cost a spurious
    multi-hundred-megabyte write at the end of long runs.
    """
    if not (enabled and timeout and llm_stalled
            and time_since_progress > timeout):
        return 'ok'
    return 'finalizing' if run_loop_finished else 'hung'


def _save_resumable_state(
    base_path: Path,
    checkpoint_data: dict,
    config: SimulationConfig,
    llm_settings: LLMSettings,
    gm_llm_settings: LLMSettings | None,
    steps_completed: int,
    max_steps: int,
) -> bool:
    """Persist Concordia's full checkpoint_data alongside an HTML checkpoint.

    Writes a ``.state.json`` sidecar next to *base_path* containing everything
    needed to reconstruct and resume the simulation from *steps_completed*.

    Returns True on success, False on error (errors are logged but never raised
    so they cannot crash an ongoing simulation run).
    """
    import json

    state_path = base_path.with_suffix('.state.json')
    try:
        payload = {
            "format_version": 1,
            "steps_completed": steps_completed,
            "max_steps": max_steps,
            "engine_type": config.engine_type.value if hasattr(config.engine_type, 'value') else str(config.engine_type),
            "config": config.model_dump(mode='json'),
            "llm_settings": llm_settings.model_dump(mode='json'),
            "gm_llm_settings": gm_llm_settings.model_dump(mode='json') if gm_llm_settings else None,
            "checkpoint_data": checkpoint_data,
        }
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        print(f"[CHECKPOINT] ✓ Resumable state saved: {state_path.name} ({state_path.stat().st_size:,} bytes)")
        return True
    except (TypeError, ValueError) as e:
        # raw_log may contain non-JSON-serializable objects — log and continue
        print(f"[WARNING] Could not save resumable state (serialisation error): {e}")
        return False
    except Exception as e:
        print(f"[WARNING] Could not save resumable state: {e}")
        return False


async def run_simulation_stream(
    config: SimulationConfig,
    llm_settings: LLMSettings,
    gm_llm_settings: LLMSettings | None = None,
    resume_state: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    Run a simulation and yield SSE events.

    Args:
        config: Simulation configuration
        llm_settings: LLM provider settings
        gm_llm_settings: Optional separate LLM settings for the Game Master
        resume_state: When set, load Concordia checkpoint from this dict and run
            only the remaining steps instead of starting from scratch.  The dict
            must have the structure written by _save_resumable_state.

    Yields:
        SSE-formatted event strings
    """
    try:
        # Import here to avoid issues with thread-unsafe imports
        import os
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'

        from backend.services.llm_factory import get_model_and_embedder

        # Check for GM LLM settings from env if not provided via request
        if not gm_llm_settings:
            gm_provider = os.getenv('GM_LLM_PROVIDER')
            gm_model_name = os.getenv('GM_LLM_MODEL')
            if gm_provider and gm_model_name:
                gm_llm_settings = LLMSettings(
                    provider=gm_provider,
                    model_name=gm_model_name,
                    api_key=os.getenv('GM_LLM_API_KEY'),
                    base_url=os.getenv('GM_LLM_BASE_URL'),
                    temperature=float(os.getenv('GM_LLM_TEMPERATURE', '0.3')),
                    max_tokens=int(os.getenv('GM_LLM_MAX_TOKENS', '3500')),
                    request_timeout=int(os.getenv('GM_LLM_TIMEOUT', str(llm_settings.request_timeout))),
                    embedder_model=llm_settings.embedder_model,
                )
                print(f"[GM LLM] Using env-configured GM model: {gm_provider}/{gm_model_name}")

        # Log start
        print(f"\n{'='*60}")
        print(f"Starting Simulation Execution")
        print(f"{'='*60}")
        print(f"Provider: {llm_settings.provider}")
        print(f"Model: {llm_settings.model_name}")
        if gm_llm_settings:
            print(f"GM Provider: {gm_llm_settings.provider}")
            print(f"GM Model: {gm_llm_settings.model_name}")
        print(f"Max Steps: {config.max_steps}")
        print(f"Agents: {', '.join([a.name for a in config.agents])}")
        print(f"Early Termination: {'enabled' if config.game_master.allow_early_termination else 'disabled'}")
        print(f"{'='*60}\n")

        # Generate task_id for cancellation support
        task_id = str(uuid.uuid4())
        simulation_state.register_simulation(task_id, config)

        # Get model and embedder
        print("🔄 Initializing LLM and embedder...")
        model, embedder = get_model_and_embedder(llm_settings)
        print("✓ Model and embedder ready")

        # Create separate GM model if configured
        gm_model = None
        if gm_llm_settings:
            print(f"🔄 Initializing separate GM LLM ({gm_llm_settings.provider}/{gm_llm_settings.model_name})...")
            gm_model, _ = get_model_and_embedder(gm_llm_settings)
            print("✓ GM model ready")
        print()

        # Send start event with task_id so frontend can cancel
        yield _format_sse(EventType.SIMULATION_START, {
            'message': 'Building simulation...',
            'task_id': task_id,
            'config': config.model_dump(mode='json')
        })

        # For extend runs (resuming a *completed* simulation), disable early
        # termination so the GM doesn't immediately say "Yes" before the first
        # new step runs.  The user explicitly requested more steps, so the
        # YOLO terminate check should not fire at step 0.
        if resume_state:
            src_completed = int(resume_state.get('steps_completed', 0))
            src_max = int(resume_state.get('max_steps', 0))
            if src_completed >= src_max > 0:
                if getattr(config.game_master, 'allow_early_termination', False):
                    config.game_master.allow_early_termination = False
                    print("[RESUME] Extend mode: early termination disabled for this run")

        # Build simulation
        print("🔨 Building simulation from configuration...")
        sim = build_simulation(config, model, embedder, gm_model=gm_model)
        print("✓ Simulation built successfully\n")

        # ── Resume path: restore Concordia state from a saved checkpoint ──
        _already_completed = 0
        if resume_state:
            try:
                concordia_checkpoint = resume_state['checkpoint_data']
                _already_completed = int(resume_state.get('steps_completed', 0))
                sim.load_from_checkpoint(concordia_checkpoint)
                print(f"[RESUME] ✓ Loaded checkpoint: {_already_completed} steps already completed")
                print(f"[RESUME]   Remaining: {config.max_steps - _already_completed} steps to run")
            except Exception as _resume_err:
                raise RuntimeError(f"Failed to restore simulation state: {_resume_err}") from _resume_err

        yield _format_sse(EventType.SIMULATION_START, {
            'message': 'Resuming from checkpoint...' if resume_state else 'Simulation built successfully. Starting execution...',
            'resumed_from_step': _already_completed if resume_state else None,
        })

        # Run simulation with streaming and progress tracking
        # Use asyncio.Queue for thread-safe progress updates from sync callback
        import asyncio
        progress_queue: asyncio.Queue = asyncio.Queue()

        # When resuming, seed counters so progress display and checkpoint gating
        # continue correctly from where we left off.
        step_count_tracker = [_already_completed]
        max_steps = config.max_steps
        start_time_progress = [time.time()]

        # Variables for partial checkpointing
        last_checkpoint_step = [_already_completed]  # avoids re-triggering checkpoint at resume step
        checkpoint_interval = getattr(config, 'checkpoint_interval', 5) or 5

        print("🎮 Running simulation...")
        print(f"   (This may take a while depending on {max_steps} steps and {len(config.agents)} agents)")
        print(f"   Each step requires multiple LLM API calls...")
        print(f"   Progress will be shown below:")
        print(f"   Partial checkpoints will be saved every {checkpoint_interval} steps\n")

        start_time = time.time()

        # Get the event loop BEFORE starting the thread
        # This is critical - we need to capture the loop from the async context
        event_loop = asyncio.get_running_loop()
        debug_print(f"[DEBUG] Captured event loop for thread-safe access: {event_loop}")

        def sync_progress_callback(checkpoint_data: dict):
            """Sync progress callback for Concordia - prints terminal progress and queues SSE events.

            Args:
                checkpoint_data: Dictionary containing checkpoint data with 'checkpoint_counter' key

            Raises:
                SimulationCancelled: If cancellation was requested, stops the engine loop.
            """
            if simulation_state.should_cancel(task_id):
                print(f"[CANCEL] Cancellation requested — stopping after step {step_count_tracker[0]}")
                raise SimulationCancelled(f"Cancelled by user after step {step_count_tracker[0]}")

            try:
                # Increment local counter rather than using checkpoint_counter, which
                # can be inflated by extra make_checkpoint_data() calls (emergency
                # checkpoint, final state save) in the run that produced the state.json
                # we restored from — causing resume/extend step numbers to read high.
                step_count_tracker[0] += 1
                step = step_count_tracker[0]
                elapsed = time.time() - start_time_progress[0]

                # Keep the task registry in sync: reattaching clients poll
                # /status/{task_id}.steps_completed, which otherwise stays 0
                # for streamed runs (only the non-stream path updated it).
                simulation_state.update_simulation_status(
                    task_id, steps_completed=step
                )

                # Log timestamp for debugging hangs
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[HEARTBEAT] {current_time} - Step {step}/{max_steps} callback received")

                # Calculate estimated time remaining
                if step > 0:
                    avg_time_per_step = elapsed / step
                    remaining_steps = max_steps - step
                    est_remaining = avg_time_per_step * remaining_steps

                    if est_remaining > 60:
                        est_time_str = f"{est_remaining/60:.1f} minutes"
                    else:
                        est_time_str = f"{est_remaining:.0f} seconds"

                    progress_msg = (f"Step {step}/{max_steps} completed "
                                   f"(elapsed: {elapsed:.0f}s, est. remaining: {est_time_str})")
                    print(f"   ✓ {progress_msg}")

                    # Put progress data in queue for SSE streaming
                    progress_data = {
                        'step': step,
                        'max_steps': max_steps,
                        'elapsed': elapsed,
                        'est_remaining': est_remaining,
                        'est_time_str': est_time_str
                    }
                    debug_print(f"[DEBUG] Attempting to queue SSE progress event: {progress_data}")

                    # Use the captured event_loop reference instead of get_running_loop()
                    # This works from any thread
                    event_loop.call_soon_threadsafe(
                        progress_queue.put_nowait,
                        progress_data
                    )
                    debug_print(f"[DEBUG] Successfully queued SSE progress event")

                    # Save partial checkpoint every N steps
                    if step % checkpoint_interval == 0 and step > last_checkpoint_step[0]:
                        last_checkpoint_step[0] = step
                        print(f"[CHECKPOINT] Saving partial results at step {step}/{max_steps}...")
                        try:
                            raw_log = sim.get_raw_log()
                            partial_log_html = _raw_log_to_html(raw_log)

                            # Create partial checkpoint filename
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            safe_premise = re.sub(r'[^\w\s-]', '', config.premise[:50])
                            safe_premise = re.sub(r'[-\s]+', '_', safe_premise.strip())
                            safe_premise = safe_premise[:50]
                            agent_names = '_'.join([agent.name[:15] for agent in config.agents[:3]])
                            if len(config.agents) > 3:
                                agent_names += f"_and_{len(config.agents) - 3}_more"

                            checkpoint_filename = f"{timestamp}_{agent_names}_{safe_premise}_checkpoint_step{step}.html"
                            checkpoint_path = LOGS_DIR / checkpoint_filename

                            # Save partial results with styles injected
                            styled_partial = _inject_html_styles(partial_log_html)
                            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                                f.write(styled_partial)

                            # Save partial metadata so analytics tabs work on checkpoints
                            _save_checkpoint_metadata(
                                checkpoint_path, config, llm_settings, gm_llm_settings,
                                start_time, step, max_steps
                            )

                            # Save full Concordia state so this checkpoint is resumable
                            _save_resumable_state(
                                checkpoint_path, checkpoint_data, config,
                                llm_settings, gm_llm_settings, step, max_steps
                            )

                            print(f"[CHECKPOINT] ✓ Partial results saved to: {checkpoint_filename} ({len(styled_partial):,} chars)")
                        except Exception as checkpoint_error:
                            print(f"[WARNING] Failed to save checkpoint: {checkpoint_error}")
                            import traceback
                            traceback.print_exc()
                else:
                    print(f"   ✓ Initializing simulation...")
            except Exception as e:
                print(f"[ERROR] Exception in sync_progress_callback: {e}")
                import traceback
                traceback.print_exc()

        # Run simulation in a thread to not block async loop
        import concurrent.futures

        # Step controller for interactive step-by-step execution
        step_ctrl = None
        if config.engine_type == EngineType.STEP_CONTROLLER:
            from concordia.environment.step_controller import StepController, StepData

            step_ctrl = StepController(start_paused=True)
            sim_record = simulation_state.get_simulation(task_id)
            if sim_record:
                sim_record.step_controller = step_ctrl

            def step_data_callback(data: StepData):
                event_loop.call_soon_threadsafe(
                    progress_queue.put_nowait,
                    {
                        'type': 'step_data',
                        'step': data.step,
                        'acting_entity': data.acting_entity,
                        'action': data.action,
                        'entity_actions': dict(data.entity_actions) if data.entity_actions else {},
                    }
                )

            yield _format_sse(EventType.CONTROLLER_STATE, {
                'state': 'paused',
                'message': 'Simulation ready. Use Play/Step/Pause/Stop to control execution.',
                'task_id': task_id,
            })

        # Set once the engine's run loop ends, while sim.play() is still busy
        # building the results log. See _mark_run_loop_completion.
        run_loop_finished = [False]

        def run_simulation_blocking():
            from backend.services.llm_factory import set_active_task_id
            set_active_task_id(task_id)
            try:
                steps_to_run = (max_steps - _already_completed) if resume_state else max_steps
                # When resuming, pass premise="" to suppress re-observation of the opening
                # premise (sequential engine's run_loop only calls observe() when `if premise:`).
                resume_premise = "" if resume_state else None
                kwargs = dict(
                    max_steps=steps_to_run,
                    get_state_callback=sync_progress_callback,
                )
                if resume_premise is not None:
                    kwargs['premise'] = resume_premise
                if step_ctrl is not None:
                    kwargs['step_controller'] = step_ctrl
                    kwargs['step_callback'] = step_data_callback
                with _mark_run_loop_completion(sim, run_loop_finished):
                    return sim.play(**kwargs)
            finally:
                set_active_task_id(None)

        # Watchdog settings - detect when simulation hangs
        # Can be overridden via WATCHDOG_TIMEOUT_SECONDS environment variable
        # Can be disabled via WATCHDOG_ENABLED environment variable
        import os
        watchdog_enabled = os.getenv('WATCHDOG_ENABLED', 'true').lower() == 'true'
        watchdog_timeout = float(os.getenv('WATCHDOG_TIMEOUT_SECONDS', '600')) if watchdog_enabled else None  # Default: 10 minutes
        last_progress_time = [time.time()]  # Use list for mutable access
        # One emergency save + throttled warnings per hang episode; re-armed
        # when progress resumes (a hung run used to save a file every 5 s).
        watchdog_episode = {"saved": False, "last_warn": 0.0}

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(run_simulation_blocking)

            # Stream progress updates while simulation runs
            while not future.done():
                try:
                    # Get progress with timeout to check if simulation is done
                    progress_data = await asyncio.wait_for(progress_queue.get(), timeout=5.0)
                    if progress_data.get('type') == 'step_data':
                        debug_print(f"[DEBUG] Yielding SSE step_data event: step {progress_data.get('step')}")
                        yield _format_sse(EventType.STEP_DATA, progress_data)
                        yield _format_sse(EventType.CONTROLLER_STATE, {'state': 'paused', 'task_id': task_id})
                    else:
                        debug_print(f"[DEBUG] Yielding SSE progress event: {progress_data}")
                        yield _format_sse(EventType.STEP_PROGRESS, progress_data)
                    # Update last progress time
                    last_progress_time[0] = time.time()
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    # No progress update for 5 seconds, check for hang
                    time_since_progress = time.time() - last_progress_time[0]

                    # Log periodic watchdog status every minute
                    if int(time_since_progress) % 60 == 0 and time_since_progress > 0:
                        from backend.services.llm_factory import get_llm_activity
                        activity = get_llm_activity()
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if activity['calls_in_flight'] > 0:
                            waiting = time.time() - activity['last_call_start']
                            print(f"[WATCHDOG] {current_time} - Step {step_count_tracker[0]}/{max_steps} | LLM call in progress ({waiting:.0f}s) | {activity['total_calls']} calls total")
                        elif run_loop_finished[0]:
                            print(f"[WATCHDOG] {current_time} - Run loop complete, building results log ({time_since_progress:.0f}s since last step event)")
                        else:
                            print(f"[WATCHDOG] {current_time} - No progress for {time_since_progress:.0f}s, last step: {step_count_tracker[0]}/{max_steps}")

                    # A hang means "no LLM work happening", not "no step
                    # progress reported". Under the asynchronous engine a step
                    # is reported only when entity 0 acts, so at N=100
                    # (~10 min/step) two steps can pass without a progress
                    # event and the timeout fired on healthy runs — 7 spurious
                    # WATCHDOG_EMERGENCY saves on the N=100 legs, including at
                    # step 0, where a single step already exceeds the default
                    # 600 s. LLM-call recency advances many times per step.
                    _llm_stalled = True
                    if watchdog_enabled and watchdog_timeout:
                        from backend.services.llm_factory import get_llm_activity
                        _act = get_llm_activity()
                        _last_llm = max(_act.get('last_call_start') or 0.0,
                                        _act.get('last_call_end') or 0.0)
                        _llm_stalled = (
                            _act.get('calls_in_flight', 0) <= 0
                            and (not _last_llm
                                 or time.time() - _last_llm > watchdog_timeout)
                        )

                    _watchdog_state = _classify_watchdog_state(
                        llm_stalled=_llm_stalled,
                        time_since_progress=time_since_progress,
                        timeout=watchdog_timeout,
                        run_loop_finished=run_loop_finished[0],
                        enabled=watchdog_enabled,
                    )

                    if _watchdog_state == 'finalizing':
                        # Quiet by design, not stalled: keep it visible so a
                        # genuine stall while serializing is still reportable,
                        # but do not write an emergency copy of a run that is
                        # about to save itself a few lines below.
                        _now = time.time()
                        if _now - watchdog_episode["last_warn"] >= 300:
                            watchdog_episode["last_warn"] = _now
                            print(f"[WATCHDOG] Run loop complete; results log still building after {time_since_progress:.0f}s. Emergency save suppressed.")
                    elif _watchdog_state == 'hung':
                        _now = time.time()
                        if _now - watchdog_episode["last_warn"] >= 300:
                            watchdog_episode["last_warn"] = _now
                            print(f"[WATCHDOG] ⚠️  WARNING: No progress for {time_since_progress:.0f}s - simulation may be hung")
                            print(f"[WATCHDOG] Last completed step: {step_count_tracker[0]}/{max_steps}")
                            print(f"[WATCHDOG] Hint: Check if LLM API is responsive or try a faster model")

                        # Try to save one emergency checkpoint per hang episode
                        try:
                            if watchdog_episode["saved"]:
                                raise StopIteration  # already saved this episode
                            print(f"[WATCHDOG] Attempting emergency checkpoint save...")
                            hung_raw_log = sim.get_raw_log()
                            hung_html = _raw_log_to_html(hung_raw_log)
                            hung_styled = _inject_html_styles(hung_html)

                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            safe_premise_wd = re.sub(r'[^\w\s-]', '', config.premise[:50])
                            safe_premise_wd = re.sub(r'[-\s]+', '_', safe_premise_wd.strip())[:50]
                            agent_names_wd = '_'.join([agent.name[:15] for agent in config.agents[:3]])
                            if len(config.agents) > 3:
                                agent_names_wd += f"_and_{len(config.agents) - 3}_more"
                            hung_filename = f"{timestamp}_{agent_names_wd}_{safe_premise_wd}_WATCHDOG_EMERGENCY_step{step_count_tracker[0]}.html"
                            hung_path = LOGS_DIR / hung_filename

                            with open(hung_path, 'w', encoding='utf-8') as f:
                                f.write(hung_styled)

                            _save_checkpoint_metadata(
                                hung_path, config, llm_settings, gm_llm_settings,
                                start_time, step_count_tracker[0], max_steps
                            )

                            print(f"[WATCHDOG] ✓ Emergency checkpoint saved: {hung_filename} ({len(hung_styled):,} chars)")
                            watchdog_episode["saved"] = True
                        except StopIteration:
                            pass
                        except Exception as hung_error:
                            print(f"[WATCHDOG] Failed to save emergency checkpoint: {hung_error}")

                        # Don't kill the simulation - just warn and continue monitoring
                    elif watchdog_episode["saved"] or watchdog_episode["last_warn"]:
                        # Progress resumed: re-arm for a future hang episode.
                        watchdog_episode["saved"] = False
                        watchdog_episode["last_warn"] = 0.0
                    # Check if simulation is done
                    continue

            # Simulation done, get results
            # Track if simulation completed successfully or had errors
            simulation_error = None
            simulation_error_type = None

            # Use a try-except to handle Concordia errors while still saving partial results
            was_cancelled = False
            try:
                debug_print(f"[DEBUG] Waiting for future.result() to get simulation results...")
                results = future.result()
                debug_print(f"[DEBUG] Simulation completed successfully, got results (type: {type(results).__name__})")
                debug_print(f"[DEBUG] Results length: {len(str(results)) if results else 0} characters")
            except SimulationCancelled:
                was_cancelled = True
                print(f"[CANCEL] Simulation cancelled after step {step_count_tracker[0]}/{max_steps}")
                simulation_error = f"Cancelled by user after step {step_count_tracker[0]}"
                simulation_error_type = "SimulationCancelled"
                simulation_state.update_simulation_status(task_id, status="cancelled")
                try:
                    raw_log = sim.get_raw_log()
                    results = _raw_log_to_html(raw_log)
                    print(f"[CANCEL] Saved partial results ({len(results)} chars)")
                except Exception:
                    results = f"<html><body><h1>Simulation Cancelled</h1><p>Cancelled after step {step_count_tracker[0]}</p></body></html>"
            except Exception as sim_error:
                # Simulation failed, but try to save partial results
                simulation_error = str(sim_error)
                simulation_error_type = type(sim_error).__name__

                print(f"[ERROR] Simulation failed with error: {sim_error}")
                print(f"[ERROR] Error type: {simulation_error_type}")
                import traceback
                traceback.print_exc()

                # Try to get partial results from the simulation object
                # The simulation object may have partial state that can be salvaged
                try:
                    raw_log = sim.get_raw_log()
                    debug_print(f"[DEBUG] Retrieved raw_log with {len(raw_log)} entries")
                    results = _raw_log_to_html(raw_log)
                    print(f"[WARNING] Saved partial results due to simulation error ({len(results)} chars)")
                except Exception as partial_error:
                    # If we can't even get partial results, create a minimal error log
                    print(f"[ERROR] Could not extract partial results: {partial_error}")
                    import traceback
                    traceback.print_exc()
                    results = f"<html><body><h1>Simulation Failed</h1><p>Error: {simulation_error}</p><pre>{traceback.format_exc()}</pre></body></html>"


            # Drain any remaining progress events from the queue
            while not progress_queue.empty():
                try:
                    progress_data = progress_queue.get_nowait()
                    debug_print(f"[DEBUG] Draining remaining SSE progress event: {progress_data}")
                    yield _format_sse(EventType.STEP_PROGRESS, progress_data)
                except asyncio.QueueEmpty:
                    break

        finally:
            # Do NOT block waiting for the LLM thread — that's what freezes Ctrl-C.
            executor.shutdown(wait=False, cancel_futures=True)

        elapsed = time.time() - start_time
        print(f"\n✓ Simulation execution completed in {elapsed:.1f} seconds")
        print(f"{'='*60}\n")

        # EMERGENCY CHECKPOINT: Save results immediately after simulation completes
        # This ensures we have a saved copy even if HTML conversion fails
        try:
            print("[CHECKPOINT] Saving emergency checkpoint before HTML processing...")
            emergency_raw_log = sim.get_raw_log()
            emergency_html = _raw_log_to_html(emergency_raw_log)
            emergency_styled = _inject_html_styles(emergency_html)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_premise_ec = re.sub(r'[^\w\s-]', '', config.premise[:50])
            safe_premise_ec = re.sub(r'[-\s]+', '_', safe_premise_ec.strip())[:50]
            agent_names_ec = '_'.join([agent.name[:15] for agent in config.agents[:3]])
            if len(config.agents) > 3:
                agent_names_ec += f"_and_{len(config.agents) - 3}_more"
            emergency_filename = f"{timestamp}_{agent_names_ec}_{safe_premise_ec}_EMERGENCY_CHECKPOINT.html"
            emergency_path = LOGS_DIR / emergency_filename

            with open(emergency_path, 'w', encoding='utf-8') as f:
                f.write(emergency_styled)

            _save_checkpoint_metadata(
                emergency_path, config, llm_settings, gm_llm_settings,
                start_time, step_count_tracker[0], max_steps
            )

            # Save the latest Concordia state — this is the primary resume point when
            # a run dies mid-way (crashed / timed out / killed).
            emergency_concordia_state = sim.make_checkpoint_data()
            _save_resumable_state(
                emergency_path, emergency_concordia_state, config,
                llm_settings, gm_llm_settings, step_count_tracker[0], max_steps
            )

            print(f"[CHECKPOINT] ✓ Emergency checkpoint saved: {emergency_filename} ({len(emergency_styled):,} chars)")
        except Exception as emergency_error:
            print(f"[WARNING] Failed to save emergency checkpoint: {emergency_error}")
            import traceback
            traceback.print_exc()

        # Send completion event with full results
        # Convert to HTML string
        print("[DEBUG] Starting to convert results to HTML...")

        # Declare variable at function scope for game-theoretic/questionnaire data
        game_theoretic_data = None
        questionnaire_answers = None
        questionnaire_aggregates = None

        # Extract grounded variables history if present (for all game master types)
        grounded_variables_history = None
        if sim.game_masters and hasattr(config.game_master, 'grounded_variables') and config.game_master.grounded_variables:
            debug_print(f"[DEBUG] Grounded variables configured: {len(config.game_master.grounded_variables)} variables")
            try:
                gm = sim.game_masters[0]
                grounded_vars_component = None  # Initialize at the top level

                # Debug: print the type and attributes of the game master
                debug_print(f"[DEBUG] Game master type: {type(gm).__name__}")

                # Try get_all_context_components first (EntityAgentWithLogging method)
                if hasattr(gm, 'get_all_context_components'):
                    print("[DEBUG] Game master has get_all_context_components() method")
                    try:
                        all_components = gm.get_all_context_components()
                        debug_print(f"[DEBUG] All context components: {list(all_components.keys())}")

                        for comp_name, comp in all_components.items():
                            class_name = comp.__class__.__name__
                            debug_print(f"[DEBUG] Component '{comp_name}' is of type '{class_name}'")
                            if class_name == 'GroundedVariablesComponent':
                                grounded_vars_component = comp
                                debug_print(f"[DEBUG] Found grounded variables component: {comp_name}")
                                break
                    except Exception as e:
                        debug_print(f"[DEBUG] Error calling get_all_context_components: {e}")

                # Fallback 1: Try get_component_names() if it exists
                if not grounded_vars_component and hasattr(gm, 'get_component_names'):
                    component_names = gm.get_component_names()
                    debug_print(f"[DEBUG] Game master has get_component_names(), found: {component_names}")

                    for component_name in component_names:
                        try:
                            component = gm.get_component(component_name)
                            class_name = component.__class__.__name__
                            debug_print(f"[DEBUG] Component '{component_name}' is of type '{class_name}'")
                            if class_name == 'GroundedVariablesComponent':
                                grounded_vars_component = component
                                debug_print(f"[DEBUG] Found grounded variables component: {component_name}")
                                break
                        except Exception as e:
                            debug_print(f"[DEBUG] Error accessing component '{component_name}': {e}")

                # Fallback 2: Try context_components attribute directly
                if not grounded_vars_component and hasattr(gm, 'context_components'):
                    debug_print(f"[DEBUG] Game master has context_components: {list(gm.context_components.keys())}")
                    for comp_name, comp in gm.context_components.items():
                        class_name = comp.__class__.__name__
                        debug_print(f"[DEBUG] Context component '{comp_name}' is of type '{class_name}'")
                        if class_name == 'GroundedVariablesComponent':
                            grounded_vars_component = comp
                            debug_print(f"[DEBUG] Found grounded variables component in context_components: {comp_name}")
                            break

                # Fallback 3: Try to get the component directly by name
                if not grounded_vars_component:
                    print("[DEBUG] Trying to get component directly by name 'grounded_variables_component'")
                    try:
                        component = gm.get_component('grounded_variables_component')
                        if component:
                            class_name = component.__class__.__name__
                            debug_print(f"[DEBUG] Direct component is of type '{class_name}'")
                            if class_name == 'GroundedVariablesComponent':
                                grounded_vars_component = component
                                debug_print(f"[DEBUG] Found grounded variables component via direct get_component call")
                    except Exception as e:
                        debug_print(f"[DEBUG] Error getting component directly: {e}")

                # Fallback 4: Check act_component if it exists
                if not grounded_vars_component and hasattr(gm, 'act_component'):
                    print("[DEBUG] Checking act_component for grounded variables...")
                    act_comp = gm.act_component
                    debug_print(f"[DEBUG] Act component type: {type(act_comp).__name__}")
                    if hasattr(act_comp, '_components'):
                        debug_print(f"[DEBUG] Act component has _components: {list(act_comp._components.keys())}")
                        for comp_name, comp in act_comp._components.items():
                            class_name = comp.__class__.__name__
                            if class_name == 'GroundedVariablesComponent':
                                grounded_vars_component = comp
                                debug_print(f"[DEBUG] Found grounded variables component in act_component: {comp_name}")
                                break

                if grounded_vars_component:
                    debug_print(f"[DEBUG] Extracting history from grounded variables component")
                    grounded_variables_history = {}

                    # Get history for each variable
                    for var_config in config.game_master.grounded_variables:
                        var_name = var_config.name if hasattr(var_config, 'name') else var_config.get('name')
                        history = grounded_vars_component.get_history(var_name)

                        # Convert history tuples to dict format for JSON serialization
                        # History format: List of (step, value) tuples
                        formatted_history = [
                            {"step": step, "value": value}
                            for step, value in history
                        ]

                        grounded_variables_history[var_name] = formatted_history
                        debug_print(f"[DEBUG] Variable '{var_name}' has {len(history)} history entries")

                    debug_print(f"[DEBUG] Extracted history for {len(grounded_variables_history)} variables")
                else:
                    print("[WARNING] Grounded variables component not found in game master after checking all locations")
                    print("[INFO] This means the component was not properly attached to the game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract grounded variables history: {e}")
                import traceback
                traceback.print_exc()

        # Special handling for interviewer prefab to extract questionnaire results
        if config.game_master.prefab == 'interviewer__GameMaster' and sim.game_masters:
            debug_print(f"[DEBUG] Interviewer prefab detected, extracting questionnaire results")
            try:
                gm = sim.game_masters[0]
                debug_print(f"[DEBUG] Game master name: {gm.name}")

                questionnaire_component = gm.get_component('questionnaire')
                debug_print(f"[DEBUG] Questionnaire component: {questionnaire_component}")

                if questionnaire_component:
                    import pandas as pd

                    # Debug: Check questionnaire state
                    debug_print(f"[DEBUG] Questionnaire component type: {type(questionnaire_component).__name__}")
                    debug_print(f"[DEBUG] Questionnaire state: {questionnaire_component.get_state() if hasattr(questionnaire_component, 'get_state') else 'N/A'}")

                    # Capture raw per-question answers FIRST: this is what the
                    # ICC(3,1) reliability path consumes and it must survive even
                    # when aggregation fails. get_questionnaires_results() raises
                    # for questionnaires whose `dimensions` attribute is None
                    # (base_questionnaire._default_aggregate_results evaluates
                    # `dimension in self.dimensions`), so run it separately and
                    # never let an aggregation error discard the answers.
                    answers = questionnaire_component.get_answers()
                    questionnaire_answers = answers
                    results_df = None
                    try:
                        results_df = questionnaire_component.get_questionnaires_results()
                        if results_df is not None and not results_df.empty:
                            questionnaire_aggregates = results_df.to_dict()
                    except Exception as agg_err:
                        print(f"[WARNING] Questionnaire aggregation failed (answers still captured): {agg_err}")

                    debug_print(f"[DEBUG] Results DataFrame: {results_df}")
                    debug_print(f"[DEBUG] Answers dict: {answers}")
                    debug_print(f"[DEBUG] Number of players with answers: {len(answers)}")

                    # Generate custom HTML for questionnaire results
                    questionnaire_html = f"""
<html>
<head>
    <title>Questionnaire Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .score {{ font-weight: bold; color: #2196F3; }}
        .timestamp {{ color: #888; font-size: 0.9em; margin-top: 30px; }}
        .premise {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Questionnaire Results</h1>
        <div class="premise"><strong>Premise:</strong> {config.premise}</div>
"""

                    # Add aggregated results table if available
                    if results_df is not None and not results_df.empty:
                        questionnaire_html += "<h2>Aggregated Scores by Dimension</h2>\n"
                        questionnaire_html += results_df.to_html(classes='results-table', index=True)

                    # Add detailed answers
                    questionnaire_html += "<h2>Detailed Answers</h2>\n"
                    for player_name, player_answers in answers.items():
                        questionnaire_html += f"<h3>Player: {player_name}</h3>\n"
                        questionnaire_html += "<table>\n"
                        questionnaire_html += "<tr><th>Question</th><th>Answer</th><th>Dimension</th><th>Value</th></tr>\n"

                        for qn_name, qn_answers in player_answers.items():
                            for q_id, answer_data in qn_answers.items():
                                questionnaire_html += f"""
                                <tr>
                                    <td>{answer_data['statement']}</td>
                                    <td>{answer_data['text']}</td>
                                    <td>{answer_data['dimension']}</td>
                                    <td class="score">{answer_data['value']}</td>
                                </tr>
                                """

                        questionnaire_html += "</table>\n"

                    questionnaire_html += f"""
        <p class="timestamp">Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
                    results = questionnaire_html
                    debug_print(f"[DEBUG] Generated custom questionnaire HTML ({len(questionnaire_html)} chars)")
                else:
                    print("[WARNING] No questionnaire component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract questionnaire results: {e}")
                import traceback
                traceback.print_exc()

        # Special handling for game-theoretic prefab to extract payoff matrix results
        elif config.game_master.prefab == 'game_theoretic_and_dramaturgic__GameMaster' and sim.game_masters:
            debug_print(f"[DEBUG] Game-theoretic prefab detected, extracting payoff matrix results")
            # game_theoretic_data already declared at function scope
            try:
                gm = sim.game_masters[0]
                debug_print(f"[DEBUG] Game master name: {gm.name}")

                # Try to get payoff_matrix component by iterating through all components
                from concordia.components.game_master import payoff_matrix as payoff_matrix_lib
                payoff_component = None

                # Search for payoff matrix component using get_component_names
                component_names = gm.get_component_names() if hasattr(gm, 'get_component_names') else []
                debug_print(f"[DEBUG] Game master has {len(component_names)} components")

                for component_name in component_names:
                    component = gm.get_component(component_name)
                    if isinstance(component, payoff_matrix_lib.PayoffMatrix):
                        payoff_component = component
                        debug_print(f"[DEBUG] Found payoff matrix component: {component_name}")
                        break

                if payoff_component:
                    # Get scores and state
                    scores = payoff_component.get_scores()
                    state = payoff_component.get_state()
                    history = state.get('history', [])

                    debug_print(f"[DEBUG] Player scores: {scores}")
                    debug_print(f"[DEBUG] History entries: {len(history)}")
                    debug_print(f"[DEBUG] Partial joint action: {state.get('partial_joint_action')}")

                    # Initialize game_theoretic_data
                    game_theoretic_data = {}
                    # Generate custom HTML for game-theoretic results
                    actions_by_player = {name: [] for name in scores.keys()}
                    game_theoretic_data['scores'] = dict(scores)
                    game_theoretic_data['actions_by_player'] = {name: [] for name in scores.keys()}

                    # Process history to extract actions
                    for entry in history:
                        if 'Joint Action' in entry and entry['Joint Action']:
                            joint_action = entry['Joint Action']
                            for player_name, action in joint_action.items():
                                if action:  # Only record non-None actions
                                    action_data = {
                                        'action': action,
                                        'score_after': entry.get('Player Scores', {}).get(player_name, 0)
                                    }
                                    actions_by_player[player_name].append(action_data)
                                    game_theoretic_data['actions_by_player'][player_name].append(action)

                    # Calculate action statistics
                    action_stats = {}
                    for player_name, actions in actions_by_player.items():
                        stats = {}
                        for action_entry in actions:
                            action = action_entry['action']
                            stats[action] = stats.get(action, 0) + 1
                        action_stats[player_name] = stats

                    # Build HTML tables
                    scores_table_rows = ""
                    for player, score in sorted(scores.items(), key=lambda x: -x[1]):
                        scores_table_rows += f"""
                        <tr>
                            <td><strong>{player}</strong></td>
                            <td class="score">{score:.1f}</td>
                        </tr>"""

                    actions_table_rows = ""
                    for player_name in sorted(actions_by_player.keys()):
                        actions = actions_by_player[player_name]
                        stats = action_stats.get(player_name, {})
                        stats_str = ", ".join([f"{action}: {count}" for action, count in stats.items()])
                        actions_table_rows += f"""
                        <tr>
                            <td><strong>{player_name}</strong></td>
                            <td>{len(actions)}</td>
                            <td>{stats_str}</td>
                            <td>{scores.get(player_name, 0):.1f}</td>
                        </tr>"""

                    # Build action history table
                    history_rows = ""
                    for i, entry in enumerate(history[:50], 1):  # Limit to 50 entries
                        joint_action = entry.get('Joint Action', {})
                        player_scores = entry.get('Player Scores', {})
                        action_summary = ", ".join([f"{p}: {a}" for p, a in joint_action.items() if a])
                        scores_summary = ", ".join([f"{p}: {s:.1f}" for p, s in player_scores.items()])
                        history_rows += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{action_summary if action_summary else '-'}</td>
                            <td>{scores_summary if scores_summary else '-'}</td>
                        </tr>"""

                    game_theoretic_html = f"""
<html>
<head>
    <title>Game-Theoretic Simulation Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #2196F3; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .score {{ font-weight: bold; color: #2196F3; font-size: 1.1em; }}
        .timestamp {{ color: #888; font-size: 0.9em; margin-top: 30px; }}
        .premise {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ flex: 1; background: #f5f5f5; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .summary-card h3 {{ margin-top: 0; color: #2196F3; }}
        .stat {{ font-size: 2em; font-weight: bold; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Game-Theoretic Simulation Results</h1>

        <div class="premise">
            <strong>Scenario:</strong> {config.premise[:200]}...
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Rounds</h3>
                <div class="stat">{len(history)}</div>
            </div>
            <div class="summary-card">
                <h3>Players</h3>
                <div class="stat">{len(scores)}</div>
            </div>
            <div class="summary-card">
                <h3>Total Actions</h3>
                <div class="stat">{sum(len(actions) for actions in actions_by_player.values())}</div>
            </div>
        </div>

        <h2>📊 Final Scores</h2>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Final Score</th>
                </tr>
            </thead>
            <tbody>
                {scores_table_rows}
            </tbody>
        </table>

        <h2>📈 Action Summary by Player</h2>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Total Actions</th>
                    <th>Action Distribution</th>
                    <th>Final Score</th>
                </tr>
            </thead>
            <tbody>
                {actions_table_rows}
            </tbody>
        </table>

        <h2>📜 Action History (First 50 Rounds)</h2>
        <table>
            <thead>
                <tr>
                    <th>Round</th>
                    <th>Joint Actions</th>
                    <th>Cumulative Scores</th>
                </tr>
            </thead>
            <tbody>
                {history_rows}
            </tbody>
        </table>

        <div class="timestamp">
            Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""
                    results = game_theoretic_html
                    debug_print(f"[DEBUG] Generated custom game-theoretic HTML ({len(game_theoretic_html)} chars)")
                else:
                    print("[WARNING] No payoff matrix component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract game-theoretic results: {e}")
                import traceback
                traceback.print_exc()

        try:
            results_html = _simulation_log_to_html(results)
            debug_print(f"[DEBUG] Results converted to HTML (length: {len(results_html)})")
        except Exception as e:
            print(f"[ERROR] Failed to convert results to HTML: {e}")
            import traceback
            traceback.print_exc()
            results_html = str(results)

        # Inject CSS styles for better readability
        styled_html = _inject_html_styles(results_html)

        # Save HTML log to file with proper naming convention
        print("💾 Saving simulation log...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        safe_premise = re.sub(r'[^\w\s-]', '', config.premise[:50])
        safe_premise = re.sub(r'[-\s]+', '_', safe_premise.strip())
        safe_premise = safe_premise[:50]  # Truncate again after sanitization

        # Get agent names for the filename
        agent_names = '_'.join([agent.name[:15] for agent in config.agents[:3]])
        if len(config.agents) > 3:
            agent_names += f"_and_{len(config.agents) - 3}_more"

        log_filename = f"{timestamp}_{agent_names}_{safe_premise}.html"
        log_path = LOGS_DIR / log_filename

        # Save the styled HTML log
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        # Save agent metadata as JSON for analytics
        metadata_filename = log_path.stem + '.metadata.json'
        metadata_path = LOGS_DIR / metadata_filename

        start_time_iso = datetime.datetime.fromtimestamp(start_time).isoformat()
        end_time_iso = datetime.datetime.now().isoformat()

        gm_llm_info = None
        if gm_llm_settings:
            gm_llm_info = {
                "provider": gm_llm_settings.provider.value if hasattr(gm_llm_settings.provider, 'value') else str(gm_llm_settings.provider),
                "model": gm_llm_settings.model_name,
            }

        # Outcome fields. Without them the metadata records only that a run
        # happened, not whether it finished: recovering the step count meant
        # inferring it from grounded-variable tick counts after the fact.
        if was_cancelled:
            run_status = "cancelled"
        elif simulation_error:
            run_status = "failed"
        else:
            run_status = "completed"

        agent_metadata = {
            "timestamp": timestamp,
            "started_at": start_time_iso,
            "completed_at": end_time_iso,
            "elapsed_seconds": round(elapsed, 1),
            "status": run_status,
            "steps_completed": step_count_tracker[0],
            "max_steps": max_steps,
            "error": simulation_error,
            "error_type": simulation_error_type,
            "llm": {
                "provider": llm_settings.provider.value if hasattr(llm_settings.provider, 'value') else str(llm_settings.provider),
                "model": llm_settings.model_name,
            },
            "gm_llm": gm_llm_info,
            "premise": config.premise,
            "game_master": {
                "prefab": config.game_master.prefab,
                "name": config.game_master.name
            },
            "agents": []
        }

        # Add grounded_variables if present - convert to dict for JSON serialization
        if hasattr(config.game_master, 'grounded_variables') and config.game_master.grounded_variables:
            # Get the variable configs
            grounded_vars_data = [
                var.model_dump() if hasattr(var, 'model_dump') else var
                for var in config.game_master.grounded_variables
            ]

            # Add history data if available
            if grounded_variables_history:
                # Merge history into the variable configs
                for var_data in grounded_vars_data:
                    var_name = var_data.get('name') if isinstance(var_data, dict) else var_data
                    if var_name in grounded_variables_history:
                        var_data['history'] = grounded_variables_history[var_name]
                        debug_print(f"[DEBUG] Added history for variable '{var_name}': {len(grounded_variables_history[var_name])} entries")

            agent_metadata["game_master"]["grounded_variables"] = grounded_vars_data
            debug_print(f"[DEBUG] Added {len(grounded_vars_data)} grounded variables to metadata")

        for agent in config.agents:
            agent_info = {
                "id": agent.id,
                "name": agent.name,
                "prefab": agent.prefab,
                "goal": agent.goal or "",
                "memories_count": len(agent.memories) if agent.memories else 0
            }
            # Add nested_simulation if present
            if hasattr(agent, 'nested_simulation') and agent.nested_simulation:
                # Convert to dict for JSON serialization
                if hasattr(agent.nested_simulation, 'model_dump'):
                    agent_info["nested_simulation"] = agent.nested_simulation.model_dump()
                elif hasattr(agent.nested_simulation, 'dict'):
                    agent_info["nested_simulation"] = agent.nested_simulation.dict()
                else:
                    agent_info["nested_simulation"] = agent.nested_simulation
            # Add components if present - convert to dict for JSON serialization
            if hasattr(agent, 'components') and agent.components:
                # Handle both dict components and model components
                if hasattr(agent.components, 'model_dump'):
                    agent_info["components"] = agent.components.model_dump()
                elif isinstance(agent.components, dict):
                    agent_info["components"] = {
                        k: v.model_dump() if hasattr(v, 'model_dump') else v
                        for k, v in agent.components.items()
                    }
                else:
                    agent_info["components"] = agent.components
            agent_metadata["agents"].append(agent_info)

        # Add game-theoretic action data if available
        if game_theoretic_data is not None:
            agent_metadata["game_theoretic"] = {
                "scores": game_theoretic_data.get('scores', {}),
                "actions_by_player": game_theoretic_data.get('actions_by_player', {})
            }
            debug_print(f"[DEBUG] Added game-theoretic data to metadata for {len(game_theoretic_data.get('actions_by_player', {}))} players")

        # Add questionnaire outcomes if available
        if questionnaire_answers is not None:
            agent_metadata["questionnaire"] = {
                "answers": questionnaire_answers,
                "aggregated_scores": questionnaire_aggregates,
            }
            debug_print(
                f"[DEBUG] Added questionnaire data to metadata for {len(questionnaire_answers)} players"
            )

        # Extract measurements channel data if available
        if hasattr(sim, '_measurements') and sim._measurements:
            try:
                all_channels = sim._measurements.get_all_channels()
                if all_channels:
                    measurements_data = {}
                    for ch_name, ch_data in all_channels.items():
                        serialized = []
                        for datum in ch_data:
                            if hasattr(datum, '__dict__'):
                                serialized.append({k: str(v) for k, v in datum.__dict__.items()})
                            elif isinstance(datum, dict):
                                serialized.append({k: str(v) for k, v in datum.items()})
                            else:
                                serialized.append(str(datum))
                        measurements_data[ch_name] = serialized
                    agent_metadata["measurements"] = measurements_data
                    debug_print(f"[DEBUG] Added measurements: {len(all_channels)} channels")
            except Exception as meas_err:
                debug_print(f"[WARNING] Failed to extract measurements: {meas_err}")

        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(agent_metadata, f, indent=2)

        # Save resumable state sidecar alongside the final log so completed
        # runs can be extended from the UI via the additional_steps flow.
        try:
            final_concordia_state = sim.make_checkpoint_data()
            _save_resumable_state(
                log_path, final_concordia_state, config, llm_settings,
                gm_llm_settings,
                steps_completed=step_count_tracker[0],
                max_steps=step_count_tracker[0],
            )
            print(f"[CHECKPOINT] ✓ Final resumable state saved: {log_path.stem}.state.json")
        except Exception as _frs_err:
            print(f"[WARNING] Failed to save final resumable state: {_frs_err}")

        print(f"✓ Log saved to: {log_filename}")
        print(f"   Size: {len(styled_html):,} characters")
        print(f"✓ Metadata saved to: {metadata_filename}\n")

        # Send completion event WITHOUT full results HTML
        # The frontend will fetch the results from the log file instead
        # This avoids sending 1MB+ data in a single SSE event which can cause network issues
        print("[DEBUG] About to yield SIMULATION_COMPLETE event")

        # Determine completion status and message
        if was_cancelled:
            completion_message = f'Simulation cancelled after step {step_count_tracker[0]}/{max_steps} (partial results saved)'
            completed = False
        elif simulation_error:
            completion_message = f'Simulation failed: {simulation_error}'
            completed = False
        else:
            completion_message = 'Simulation completed successfully'
            completed = True

        completion_data = {
            'message': completion_message,
            'steps_completed': step_count_tracker[0],
            'timestamp': datetime.datetime.now().isoformat(),
            'log_path': str(log_path),
            'log_filename': log_filename,
            'completed': completed,
            'error': simulation_error,
            'error_type': simulation_error_type,
            'elapsed_seconds': round(elapsed, 1),
            'llm_provider': llm_settings.provider.value if hasattr(llm_settings.provider, 'value') else str(llm_settings.provider),
            'llm_model': llm_settings.model_name,
            'gm_llm_provider': (gm_llm_settings.provider.value if hasattr(gm_llm_settings.provider, 'value') else str(gm_llm_settings.provider)) if gm_llm_settings else None,
            'gm_llm_model': gm_llm_settings.model_name if gm_llm_settings else None,
        }
        simulation_state.complete_simulation(task_id, log_filename=log_filename, completion_data=completion_data)
        completion_event = _format_sse(EventType.SIMULATION_COMPLETE, completion_data)
        debug_print(f"[DEBUG] SIMULATION_COMPLETE event formatted (length: {len(completion_event)} chars)")
        yield completion_event
        print("[DEBUG] SIMULATION_COMPLETE event yielded")

    except Exception as e:
        # Send error event
        yield _format_sse(EventType.ERROR, {
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.datetime.now().isoformat()
        })


def _format_sse(event_type: EventType, data: dict) -> str:
    """Format data as Server-Sent Event."""
    formatted = f"event: {event_type.value}\ndata: {json.dumps(data)}\n\n"
    debug_print(f"[DEBUG] _format_sse: event_type={event_type.value}, data_length={len(json.dumps(data))}, total_length={len(formatted)}")
    return formatted


async def run_simulation_simple(
    config: SimulationConfig,
    llm_settings: LLMSettings,
    task_id: Optional[str] = None
) -> dict:
    """
    Run a simulation and return results (non-streaming).

    Args:
        config: Simulation configuration
        llm_settings: LLM provider settings
        task_id: Optional task ID for cancellation support

    Returns:
        Dictionary with simulation results
    """
    import os
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'

    from backend.services.llm_factory import get_model_and_embedder

    # Generate task ID if not provided
    if task_id is None:
        task_id = str(uuid.uuid4())

    # Register simulation for tracking
    sim_state = simulation_state.register_simulation(task_id, config)

    try:
        # Log start
        print(f"\n{'='*60}")
        print(f"Starting Simulation Execution")
        print(f"{'='*60}")
        print(f"Provider: {llm_settings.provider}")
        print(f"Model: {llm_settings.model_name}")
        print(f"Max Steps: {config.max_steps}")
        print(f"Agents: {', '.join([a.name for a in config.agents])}")
        print(f"Premise: {config.premise[:100]}...")
        print(f"{'='*60}\n")

        # Get model and embedder
        print("🔄 Initializing LLM and embedder...")
        model, embedder = get_model_and_embedder(llm_settings)
        print("✓ Model and embedder ready\n")

        # Check for cancellation before building
        if simulation_state.should_cancel(task_id):
            raise asyncio.CancelledError("Simulation cancelled by user")

        # Build and run simulation
        print("🔨 Building simulation from configuration...")
        sim = build_simulation(config, model, embedder)
        print("✓ Simulation built successfully\n")

        # Update state to indicate building is complete
        simulation_state.update_simulation_status(task_id, status="running")

        # Run the simulation (this is a blocking call, but we can't easily interrupt it)
        # Concordia doesn't natively support cancellation mid-execution
        print("🎮 Running simulation...")
        print(f"   Max steps: {config.max_steps}")
        print(f"   Agents: {', '.join([a.name for a in config.agents])}")
        print(f"   Each step requires multiple LLM API calls...")
        print(f"   Progress will be shown below:\n")

        import time
        start_time = time.time()

        # Create a progress callback that prints step completion like negotiatepeace.py
        step_count = [0]  # Use list to allow modification in nested function
        start_time_progress = [start_time]

        def progress_callback(checkpoint_data: dict):
            """Called after each step completes to show progress.

            Args:
                checkpoint_data: Dictionary containing checkpoint data with 'checkpoint_counter' key

            Raises:
                SimulationCancelled: If cancellation was requested, stops the engine loop.
            """
            if simulation_state.should_cancel(task_id):
                print(f"[CANCEL] Cancellation requested — stopping after step {step_count[0]}")
                raise SimulationCancelled(f"Cancelled by user after step {step_count[0]}")

            step_count[0] += 1
            step = step_count[0]
            elapsed = time.time() - start_time_progress[0]

            # Calculate estimated time remaining
            if step > 0:
                avg_time_per_step = elapsed / step
                remaining_steps = config.max_steps - step
                est_remaining = avg_time_per_step * remaining_steps

                # Format time nicely
                if est_remaining > 60:
                    est_time_str = f"{est_remaining/60:.1f} minutes"
                else:
                    est_time_str = f"{est_remaining:.0f} seconds"

                print(f"   ✓ Step {step}/{config.max_steps} completed "
                      f"(elapsed: {elapsed:.0f}s, est. remaining: {est_time_str})")
            else:
                print(f"   ✓ Initializing simulation...")

        # Run simulation with progress callback
        debug_print(f"[DEBUG] Starting simulation play with max_steps={config.max_steps}")
        debug_print(f"[DEBUG] Game master prefab: {config.game_master.prefab}")
        debug_print(f"[DEBUG] Number of entities: {len(sim.entities)}")
        debug_print(f"[DEBUG] Number of game masters: {len(sim.game_masters)}")
        for entity in sim.entities:
            debug_print(f"[DEBUG] Entity: {entity.name}, type: {type(entity).__name__}")
        for gm in sim.game_masters:
            debug_print(f"[DEBUG] Game Master: {gm.name}, type: {type(gm).__name__}")

        from backend.services.llm_factory import set_active_task_id
        set_active_task_id(task_id)
        was_cancelled = False
        try:
            results = sim.play(
                max_steps=config.max_steps,
                get_state_callback=progress_callback,
            )
        except SimulationCancelled:
            was_cancelled = True
            print(f"[CANCEL] Simulation cancelled after step {step_count[0]}/{config.max_steps}")
            simulation_state.update_simulation_status(task_id, status="cancelled")
            raw_log = sim.get_raw_log()
            results = _raw_log_to_html(raw_log)
            print(f"[CANCEL] Saved partial results ({len(str(results))} chars)")
        finally:
            set_active_task_id(None)
        debug_print(f"[DEBUG] Simulation play completed, results type: {type(results).__name__}")

        # Try to get step count from results
        # Use the step_count from our progress callback for accurate reporting
        actual_steps = step_count[0]

        if actual_steps > 0:
            steps_completed = f"{actual_steps} steps completed"
            print(f"\n   ✓ {steps_completed}")
        elif hasattr(results, 'history'):
            # Fallback: count from history if callback wasn't triggered
            step_count_final = 0
            for event in results.history:
                if hasattr(event, 'action'):
                    step_count_final += 1

            if step_count_final > 0 and len(config.agents) > 0:
                estimated_steps = step_count_final // len(config.agents)
                steps_completed = f"~{estimated_steps} actual steps ({step_count_final} agent actions)"
                print(f"\n   ✓ Completed {steps_completed}")
            else:
                steps_completed = f"{step_count_final} agent actions"
                print(f"\n   ✓ Completed {steps_completed}")
        else:
            steps_completed = "Simulation complete"
            print(f"\n   ✓ Simulation complete")

        elapsed = time.time() - start_time
        print(f"\n✓ Simulation completed in {elapsed:.1f} seconds")
        print(f"{'='*60}\n")

        # Update completion
        simulation_state.update_simulation_status(
            task_id,
            status="completed",
            steps_completed=actual_steps if actual_steps > 0 else config.max_steps
        )

        # Convert to HTML string
        results_html = _simulation_log_to_html(results)

        # Declare variable at function scope for game-theoretic/questionnaire data
        game_theoretic_data = None
        questionnaire_answers = None
        questionnaire_aggregates = None

        # Special handling for interviewer prefab to extract questionnaire results
        if config.game_master.prefab == 'interviewer__GameMaster' and sim.game_masters:
            try:
                gm = sim.game_masters[0]
                debug_print(f"[DEBUG] Game master name: {gm.name}")
                debug_print(f"[DEBUG] Game master components: {list(gm.get_component_names()) if hasattr(gm, 'get_component_names') else 'N/A'}")

                questionnaire_component = gm.get_component('questionnaire')
                debug_print(f"[DEBUG] Questionnaire component: {questionnaire_component}")

                if questionnaire_component:
                    import pandas as pd

                    # Debug: Check questionnaire state
                    debug_print(f"[DEBUG] Questionnaire component type: {type(questionnaire_component).__name__}")
                    debug_print(f"[DEBUG] Questionnaire state: {questionnaire_component.get_state() if hasattr(questionnaire_component, 'get_state') else 'N/A'}")

                    # Capture raw per-question answers FIRST: this is what the
                    # ICC(3,1) reliability path consumes and it must survive even
                    # when aggregation fails. get_questionnaires_results() raises
                    # for questionnaires whose `dimensions` attribute is None
                    # (base_questionnaire._default_aggregate_results evaluates
                    # `dimension in self.dimensions`), so run it separately and
                    # never let an aggregation error discard the answers.
                    answers = questionnaire_component.get_answers()
                    questionnaire_answers = answers
                    results_df = None
                    try:
                        results_df = questionnaire_component.get_questionnaires_results()
                        if results_df is not None and not results_df.empty:
                            questionnaire_aggregates = results_df.to_dict()
                    except Exception as agg_err:
                        print(f"[WARNING] Questionnaire aggregation failed (answers still captured): {agg_err}")

                    debug_print(f"[DEBUG] Results DataFrame: {results_df}")
                    debug_print(f"[DEBUG] Answers dict: {answers}")
                    debug_print(f"[DEBUG] Number of players with answers: {len(answers)}")

                    # Generate custom HTML for questionnaire results
                    questionnaire_html = f"""
<html>
<head>
    <title>Questionnaire Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .score {{ font-weight: bold; color: #2196F3; }}
        .timestamp {{ color: #888; font-size: 0.9em; margin-top: 30px; }}
        .premise {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Questionnaire Results</h1>
        <div class="premise"><strong>Premise:</strong> {config.premise}</div>
"""

                    # Add aggregated results table if available
                    if results_df is not None and not results_df.empty:
                        questionnaire_html += "<h2>Aggregated Scores by Dimension</h2>\n"
                        questionnaire_html += results_df.to_html(classes='results-table', index=True)

                    # Add detailed answers
                    questionnaire_html += "<h2>Detailed Answers</h2>\n"
                    for player_name, player_answers in answers.items():
                        questionnaire_html += f"<h3>Player: {player_name}</h3>\n"
                        questionnaire_html += "<table>\n"
                        questionnaire_html += "<tr><th>Question</th><th>Answer</th><th>Dimension</th><th>Value</th></tr>\n"

                        for qn_name, qn_answers in player_answers.items():
                            for q_id, answer_data in qn_answers.items():
                                questionnaire_html += f"""
                                <tr>
                                    <td>{answer_data['statement']}</td>
                                    <td>{answer_data['text']}</td>
                                    <td>{answer_data['dimension']}</td>
                                    <td class="score">{answer_data['value']}</td>
                                </tr>
                                """

                        questionnaire_html += "</table>\n"

                    questionnaire_html += f"""
        <p class="timestamp">Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
                    results_html = questionnaire_html
                    debug_print(f"[DEBUG] Generated custom questionnaire HTML ({len(results_html)} chars)")
                else:
                    print("[WARNING] No questionnaire component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract questionnaire results: {e}")
                import traceback
                traceback.print_exc()

        # Special handling for game-theoretic prefab to extract payoff matrix results
        elif config.game_master.prefab == 'game_theoretic_and_dramaturgic__GameMaster' and sim.game_masters:
            debug_print(f"[DEBUG] Game-theoretic prefab detected, extracting payoff matrix results")
            # game_theoretic_data already declared at function scope
            try:
                gm = sim.game_masters[0]
                debug_print(f"[DEBUG] Game master name: {gm.name}")

                # Try to get payoff_matrix component by iterating through all components
                from concordia.components.game_master import payoff_matrix as payoff_matrix_lib
                payoff_component = None

                # Search for payoff matrix component using get_component_names
                component_names = gm.get_component_names() if hasattr(gm, 'get_component_names') else []
                debug_print(f"[DEBUG] Game master has {len(component_names)} components")

                for component_name in component_names:
                    component = gm.get_component(component_name)
                    if isinstance(component, payoff_matrix_lib.PayoffMatrix):
                        payoff_component = component
                        debug_print(f"[DEBUG] Found payoff matrix component: {component_name}")
                        break

                if payoff_component:
                    # Get scores and state
                    scores = payoff_component.get_scores()
                    state = payoff_component.get_state()
                    history = state.get('history', [])

                    debug_print(f"[DEBUG] Player scores: {scores}")
                    debug_print(f"[DEBUG] History entries: {len(history)}")
                    debug_print(f"[DEBUG] Partial joint action: {state.get('partial_joint_action')}")

                    # Initialize game_theoretic_data
                    game_theoretic_data = {}
                    # Generate custom HTML for game-theoretic results
                    actions_by_player = {name: [] for name in scores.keys()}
                    game_theoretic_data['scores'] = dict(scores)
                    game_theoretic_data['actions_by_player'] = {name: [] for name in scores.keys()}

                    # Process history to extract actions
                    for entry in history:
                        if 'Joint Action' in entry and entry['Joint Action']:
                            joint_action = entry['Joint Action']
                            for player_name, action in joint_action.items():
                                if action:  # Only record non-None actions
                                    action_data = {
                                        'action': action,
                                        'score_after': entry.get('Player Scores', {}).get(player_name, 0)
                                    }
                                    actions_by_player[player_name].append(action_data)
                                    game_theoretic_data['actions_by_player'][player_name].append(action)

                    # Calculate action statistics
                    action_stats = {}
                    for player_name, actions in actions_by_player.items():
                        stats = {}
                        for action_entry in actions:
                            action = action_entry['action']
                            stats[action] = stats.get(action, 0) + 1
                        action_stats[player_name] = stats

                    # Build HTML tables
                    scores_table_rows = ""
                    for player, score in sorted(scores.items(), key=lambda x: -x[1]):
                        scores_table_rows += f"""
                        <tr>
                            <td><strong>{player}</strong></td>
                            <td class="score">{score:.1f}</td>
                        </tr>"""

                    actions_table_rows = ""
                    for player_name in sorted(actions_by_player.keys()):
                        actions = actions_by_player[player_name]
                        stats = action_stats.get(player_name, {})
                        stats_str = ", ".join([f"{action}: {count}" for action, count in stats.items()])
                        actions_table_rows += f"""
                        <tr>
                            <td><strong>{player_name}</strong></td>
                            <td>{len(actions)}</td>
                            <td>{stats_str}</td>
                            <td>{scores.get(player_name, 0):.1f}</td>
                        </tr>"""

                    # Build action history table
                    history_rows = ""
                    for i, entry in enumerate(history[:50], 1):  # Limit to 50 entries
                        joint_action = entry.get('Joint Action', {})
                        player_scores = entry.get('Player Scores', {})
                        action_summary = ", ".join([f"{p}: {a}" for p, a in joint_action.items() if a])
                        scores_summary = ", ".join([f"{p}: {s:.1f}" for p, s in player_scores.items()])
                        history_rows += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{action_summary if action_summary else '-'}</td>
                            <td>{scores_summary if scores_summary else '-'}</td>
                        </tr>"""

                    game_theoretic_html = f"""
<html>
<head>
    <title>Game-Theoretic Simulation Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #2196F3; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .score {{ font-weight: bold; color: #2196F3; font-size: 1.1em; }}
        .timestamp {{ color: #888; font-size: 0.9em; margin-top: 30px; }}
        .premise {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ flex: 1; background: #f5f5f5; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .summary-card h3 {{ margin-top: 0; color: #2196F3; }}
        .stat {{ font-size: 2em; font-weight: bold; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Game-Theoretic Simulation Results</h1>

        <div class="premise">
            <strong>Scenario:</strong> {config.premise[:200]}...
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Rounds</h3>
                <div class="stat">{len(history)}</div>
            </div>
            <div class="summary-card">
                <h3>Players</h3>
                <div class="stat">{len(scores)}</div>
            </div>
            <div class="summary-card">
                <h3>Total Actions</h3>
                <div class="stat">{sum(len(actions) for actions in actions_by_player.values())}</div>
            </div>
        </div>

        <h2>📊 Final Scores</h2>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Final Score</th>
                </tr>
            </thead>
            <tbody>
                {scores_table_rows}
            </tbody>
        </table>

        <h2>📈 Action Summary by Player</h2>
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Total Actions</th>
                    <th>Action Distribution</th>
                    <th>Final Score</th>
                </tr>
            </thead>
            <tbody>
                {actions_table_rows}
            </tbody>
        </table>

        <h2>📜 Action History (First 50 Rounds)</h2>
        <table>
            <thead>
                <tr>
                    <th>Round</th>
                    <th>Joint Actions</th>
                    <th>Cumulative Scores</th>
                </tr>
            </thead>
            <tbody>
                {history_rows}
            </tbody>
        </table>

        <div class="timestamp">
            Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""
                    results_html = game_theoretic_html
                    debug_print(f"[DEBUG] Generated custom game-theoretic HTML ({len(game_theoretic_html)} chars)")
                else:
                    print("[WARNING] No payoff matrix component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract game-theoretic results: {e}")
                import traceback
                traceback.print_exc()

        # Inject CSS styles for better readability
        styled_html = _inject_html_styles(results_html)

        # Save HTML log to file with proper naming convention
        print("💾 Saving simulation log...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create safe filename from premise (first 50 chars, alphanumeric and basic symbols only)
        safe_premise = re.sub(r'[^\w\s-]', '', config.premise[:50])
        safe_premise = re.sub(r'[-\s]+', '_', safe_premise.strip())
        safe_premise = safe_premise[:50]  # Truncate again after sanitization

        # Get agent names for the filename
        agent_names = '_'.join([agent.name[:15] for agent in config.agents[:3]])
        if len(config.agents) > 3:
            agent_names += f"_and_{len(config.agents) - 3}_more"

        log_filename = f"{timestamp}_{agent_names}_{safe_premise}.html"
        log_path = LOGS_DIR / log_filename

        # Save the styled HTML log
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        # Save agent metadata as JSON for analytics
        metadata_filename = log_path.stem + '.metadata.json'
        metadata_path = LOGS_DIR / metadata_filename

        start_time_iso = datetime.datetime.fromtimestamp(start_time).isoformat()
        end_time_iso = datetime.datetime.now().isoformat()

        gm_llm_info = None
        if gm_llm_settings:
            gm_llm_info = {
                "provider": gm_llm_settings.provider.value if hasattr(gm_llm_settings.provider, 'value') else str(gm_llm_settings.provider),
                "model": gm_llm_settings.model_name,
            }

        # Outcome fields, as in the streaming path. This entry point has no
        # error capture of its own, so only cancellation is distinguishable.
        run_status = "cancelled" if was_cancelled else "completed"

        agent_metadata = {
            "timestamp": timestamp,
            "started_at": start_time_iso,
            "completed_at": end_time_iso,
            "elapsed_seconds": round(elapsed, 1),
            "status": run_status,
            "steps_completed": step_count[0],
            "max_steps": config.max_steps,
            "llm": {
                "provider": llm_settings.provider.value if hasattr(llm_settings.provider, 'value') else str(llm_settings.provider),
                "model": llm_settings.model_name,
            },
            "gm_llm": gm_llm_info,
            "premise": config.premise,
            "game_master": {
                "prefab": config.game_master.prefab,
                "name": config.game_master.name
            },
            "agents": []
        }

        # Add grounded_variables if present - convert to dict for JSON serialization
        if hasattr(config.game_master, 'grounded_variables') and config.game_master.grounded_variables:
            agent_metadata["game_master"]["grounded_variables"] = [
                var.model_dump() if hasattr(var, 'model_dump') else var
                for var in config.game_master.grounded_variables
            ]

        for agent in config.agents:
            agent_info = {
                "id": agent.id,
                "name": agent.name,
                "prefab": agent.prefab,
                "goal": agent.goal or "",
                "memories_count": len(agent.memories) if agent.memories else 0
            }
            # Add nested_simulation if present
            if hasattr(agent, 'nested_simulation') and agent.nested_simulation:
                # Convert to dict for JSON serialization
                if hasattr(agent.nested_simulation, 'model_dump'):
                    agent_info["nested_simulation"] = agent.nested_simulation.model_dump()
                elif hasattr(agent.nested_simulation, 'dict'):
                    agent_info["nested_simulation"] = agent.nested_simulation.dict()
                else:
                    agent_info["nested_simulation"] = agent.nested_simulation
            # Add components if present - convert to dict for JSON serialization
            if hasattr(agent, 'components') and agent.components:
                # Handle both dict components and model components
                if hasattr(agent.components, 'model_dump'):
                    agent_info["components"] = agent.components.model_dump()
                elif isinstance(agent.components, dict):
                    agent_info["components"] = {
                        k: v.model_dump() if hasattr(v, 'model_dump') else v
                        for k, v in agent.components.items()
                    }
                else:
                    agent_info["components"] = agent.components
            agent_metadata["agents"].append(agent_info)

        # Add game-theoretic action data if available
        if game_theoretic_data is not None:
            agent_metadata["game_theoretic"] = {
                "scores": game_theoretic_data.get('scores', {}),
                "actions_by_player": game_theoretic_data.get('actions_by_player', {})
            }
            debug_print(f"[DEBUG] Added game-theoretic data to metadata for {len(game_theoretic_data.get('actions_by_player', {}))} players")

        # Add questionnaire outcomes if available
        if questionnaire_answers is not None:
            agent_metadata["questionnaire"] = {
                "answers": questionnaire_answers,
                "aggregated_scores": questionnaire_aggregates,
            }
            debug_print(
                f"[DEBUG] Added questionnaire data to metadata for {len(questionnaire_answers)} players"
            )

        # Extract measurements channel data if available
        if hasattr(sim, '_measurements') and sim._measurements:
            try:
                all_channels = sim._measurements.get_all_channels()
                if all_channels:
                    measurements_data = {}
                    for ch_name, ch_data in all_channels.items():
                        serialized = []
                        for datum in ch_data:
                            if hasattr(datum, '__dict__'):
                                serialized.append({k: str(v) for k, v in datum.__dict__.items()})
                            elif isinstance(datum, dict):
                                serialized.append({k: str(v) for k, v in datum.items()})
                            else:
                                serialized.append(str(datum))
                        measurements_data[ch_name] = serialized
                    agent_metadata["measurements"] = measurements_data
                    debug_print(f"[DEBUG] Added measurements: {len(all_channels)} channels")
            except Exception as meas_err:
                debug_print(f"[WARNING] Failed to extract measurements: {meas_err}")

        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(agent_metadata, f, indent=2)

        print(f"✓ Log saved to: {log_filename}")
        print(f"   Size: {len(styled_html):,} characters")
        print(f"✓ Metadata saved to: {metadata_filename}\n")

        result_data = {
            'config': config.model_dump(mode='json'),
            'completed': not was_cancelled,
            'cancelled': was_cancelled,
            'timestamp': datetime.datetime.now().isoformat(),
            'results': results_html,
            'log_path': str(log_path),
            'log_filename': log_filename,
            'task_id': task_id,
            'message': f'Cancelled after step {step_count[0]}' if was_cancelled else 'Simulation completed successfully'
        }
        simulation_state.complete_simulation(task_id, log_filename=log_filename, completion_data=result_data)
        return result_data

    except asyncio.CancelledError:
        simulation_state.update_simulation_status(task_id, status="cancelled")
        simulation_state.complete_simulation(task_id)
        raise

    except Exception as e:
        simulation_state.update_simulation_status(
            task_id,
            status="error",
            error=str(e)
        )
        simulation_state.complete_simulation(task_id)
        raise


def _inject_html_styles(html: str) -> str:
    """Inject CSS styles into Concordia HTML logs for better readability.
    Skips injection for v2.4+ structured logs which have their own styling."""
    if 'const ENTRIES =' in html and 'const CONTENT_STORE =' in html:
        return html
    styles = """
    <style type="text/css">
      /* Reset and base improvements */
      * { box-sizing: border-box !important; }

      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        line-height: 1.7 !important;
        color: #1f2937 !important;
        padding: 1.5rem !important;
        max-width: 100% !important;
        margin: 0 !important;
      }

      /* Improve paragraph spacing - key fix for readability */
      p {
        margin: 0 0 1rem 0 !important;
        line-height: 1.7 !important;
      }

      /* Make headings more prominent */
      h1, h2, h3, h4, h5, h6 {
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
      }
      h1 { font-size: 2rem !important; }
      h2 { font-size: 1.5rem !important; }
      h3 { font-size: 1.25rem !important; }

      /* Add space between list items */
      ul, ol {
        margin-bottom: 1rem !important;
        padding-left: 1.5rem !important;
      }
      li {
        margin-bottom: 0.5rem !important;
        line-height: 1.6 !important;
      }

      /* Improve table readability */
      table {
        margin: 1rem 0 !important;
        border-collapse: collapse !important;
        width: 100% !important;
      }
      td, th {
        padding: 0.75rem !important;
        border: 1px solid #e5e7eb !important;
        text-align: left !important;
      }
      th {
        background: #f9fafb !important;
        font-weight: 600 !important;
      }

      /* Add visual separation for dialogue/interactions */
      div[class*="message"],
      div[class*="dialogue"],
      div[class*="utterance"],
      div[class*="interaction"],
      div[class*="action"] {
        margin: 1rem 0 !important;
        padding: 1rem !important;
        background: #f9fafb !important;
        border-radius: 0.5rem !important;
        border-left: 3px solid #d1d5db !important;
      }

      /* Highlight step/section indicators */
      div[id*="step"],
      div[id*="Step"],
      div[class*="step"],
      div[class*="Step"],
      section {
        margin: 2rem 0 !important;
        padding: 1.5rem !important;
        background: #eff6ff !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 0.5rem !important;
      }

      /* Make tabs more visible */
      .tabs,
      [role="tablist"],
      div[class*="tab"] {
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #e5e7eb !important;
      }
      [role="tab"],
      button[class*="tab"] {
        padding: 0.5rem 1rem !important;
        margin-right: 0.25rem !important;
        border-radius: 0.375rem 0.375rem 0 0 !important;
        background: #f3f4f6 !important;
        border: none !important;
        cursor: pointer !important;
      }
      [role="tab"][aria-selected="true"],
      button[class*="tab"].active {
        background: #3b82f6 !important;
        color: white !important;
      }

      /* Tab content panels */
      [role="tabpanel"],
      div[class*="tabpanel"],
      div[class*="tab-content"] {
        padding: 1rem 0 !important;
      }

      /* Add spacing between generic div elements */
      div {
        margin-bottom: 0.5rem !important;
      }

      /* Better spacing for pre/code blocks */
      pre, code {
        background: #f3f4f6 !important;
        padding: 0.75rem !important;
        border-radius: 0.375rem !important;
        font-size: 0.875rem !important;
        line-height: 1.5 !important;
      }

      /* Separator styling */
      hr {
        margin: 2rem 0 !important;
        border: none !important;
        border-top: 2px solid #e5e7eb !important;
      }
    </style>
    """

    # Inject styles strategically
    if '</head>' in html:
        # Best case: inject before closing head tag
        return html.replace('</head>', styles + '</head>')
    elif '<html' in html:
        return re.sub(r'(<html[^>]*>)', r'\1<head>' + styles + '</head>', html)
    elif '<body>' in html:
        # Has body but no html - inject at start of body
        return html.replace('<body>', '<body>' + styles)
    else:
        # Fragment - wrap properly
        return '<!DOCTYPE html><html><head>' + styles + '</head><body>' + html + '</body></html>'
