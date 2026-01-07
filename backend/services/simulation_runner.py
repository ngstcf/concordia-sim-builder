"""
Service for running simulations with streaming output.
"""
import asyncio
import json
import datetime
import os
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator, Optional
from concordia.language_model import language_model

from backend.models.schemas import (
    SimulationConfig,
    LLMSettings,
    SimulationEvent,
    EventType
)
from backend.services.simulation_builder import build_simulation
from backend.services.simulation_state import simulation_state


# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


async def run_simulation_stream(
    config: SimulationConfig,
    llm_settings: LLMSettings
) -> AsyncGenerator[str, None]:
    """
    Run a simulation and yield SSE events.

    Args:
        config: Simulation configuration
        llm_settings: LLM provider settings

    Yields:
        SSE-formatted event strings
    """
    try:
        # Import here to avoid issues with thread-unsafe imports
        import os
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'

        from backend.services.llm_factory import get_model_and_embedder

        # Log start
        print(f"\n{'='*60}")
        print(f"Starting Simulation Execution")
        print(f"{'='*60}")
        print(f"Provider: {llm_settings.provider}")
        print(f"Model: {llm_settings.model_name}")
        print(f"Max Steps: {config.max_steps}")
        print(f"Agents: {', '.join([a.name for a in config.agents])}")
        print(f"{'='*60}\n")

        # Get model and embedder
        print("🔄 Initializing LLM and embedder...")
        model, embedder = get_model_and_embedder(llm_settings)
        print("✓ Model and embedder ready\n")

        # Send start event
        yield _format_sse(EventType.SIMULATION_START, {
            'message': 'Building simulation...',
            'config': config.model_dump(mode='json')
        })

        # Build simulation
        print("🔨 Building simulation from configuration...")
        sim = build_simulation(config, model, embedder)
        print("✓ Simulation built successfully\n")

        yield _format_sse(EventType.SIMULATION_START, {
            'message': 'Simulation built successfully. Starting execution...'
        })

        # Run simulation with streaming and progress tracking
        # Use asyncio.Queue for thread-safe progress updates from sync callback
        import asyncio
        progress_queue: asyncio.Queue = asyncio.Queue()

        step_count_tracker = [0]  # Use list for mutable access in callback
        max_steps = config.max_steps
        start_time_progress = [time.time()]

        print("🎮 Running simulation...")
        print(f"   (This may take a while depending on {max_steps} steps and {len(config.agents)} agents)")
        print(f"   Each step requires multiple LLM API calls...")
        print(f"   Progress will be shown below:\n")

        start_time = time.time()

        # Get the event loop BEFORE starting the thread
        # This is critical - we need to capture the loop from the async context
        event_loop = asyncio.get_running_loop()
        print(f"[DEBUG] Captured event loop for thread-safe access: {event_loop}")

        def sync_progress_callback(checkpoint_data: dict):
            """Sync progress callback for Concordia - prints terminal progress and queues SSE events.

            Args:
                checkpoint_data: Dictionary containing checkpoint data with 'checkpoint_counter' key
            """
            try:
                # Extract step number from checkpoint data
                step = checkpoint_data.get('checkpoint_counter', 0)
                step_count_tracker[0] = step
                elapsed = time.time() - start_time_progress[0]

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
                    print(f"[DEBUG] Attempting to queue SSE progress event: {progress_data}")

                    # Use the captured event_loop reference instead of get_running_loop()
                    # This works from any thread
                    event_loop.call_soon_threadsafe(
                        progress_queue.put_nowait,
                        progress_data
                    )
                    print(f"[DEBUG] Successfully queued SSE progress event")
                else:
                    print(f"   ✓ Initializing simulation...")
            except Exception as e:
                print(f"[ERROR] Exception in sync_progress_callback: {e}")
                import traceback
                traceback.print_exc()

        # Run simulation in a thread to not block async loop
        import concurrent.futures

        def run_simulation_blocking():
            return sim.play(
                max_steps=max_steps,
                get_state_callback=sync_progress_callback
            )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_simulation_blocking)

            # Stream progress updates while simulation runs
            while not future.done():
                try:
                    # Get progress with timeout to check if simulation is done
                    progress_data = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                    print(f"[DEBUG] Yielding SSE progress event: {progress_data}")
                    yield _format_sse(EventType.STEP_PROGRESS, progress_data)
                except asyncio.TimeoutError:
                    # No progress update, check if simulation is done
                    continue

            # Simulation done, get results
            # Track if simulation completed successfully or had errors
            simulation_error = None
            simulation_error_type = None

            # Use a try-except to handle Concordia errors while still saving partial results
            try:
                results = future.result()
                print(f"[DEBUG] Simulation completed successfully, got results")
            except Exception as sim_error:
                # Simulation failed, but try to save partial results
                simulation_error = str(sim_error)
                simulation_error_type = type(sim_error).__name__

                print(f"[ERROR] Simulation failed with error: {sim_error}")
                import traceback
                traceback.print_exc()

                # Try to get partial results from the simulation object
                # The simulation object may have partial state that can be salvaged
                try:
                    results = str(sim)  # Get whatever state we can
                    print(f"[WARNING] Saving partial results due to simulation error")
                except Exception as partial_error:
                    # If we can't even get partial results, create a minimal error log
                    print(f"[ERROR] Could not extract partial results: {partial_error}")
                    results = f"<html><body><h1>Simulation Failed</h1><p>Error: {simulation_error}</p><pre>{traceback.format_exc()}</pre></body></html>"


            # Drain any remaining progress events from the queue
            while not progress_queue.empty():
                try:
                    progress_data = progress_queue.get_nowait()
                    print(f"[DEBUG] Draining remaining SSE progress event: {progress_data}")
                    yield _format_sse(EventType.STEP_PROGRESS, progress_data)
                except asyncio.QueueEmpty:
                    break

        elapsed = time.time() - start_time
        print(f"\n✓ Simulation completed in {elapsed:.1f} seconds")
        print(f"{'='*60}\n")

        # Send completion event with full results
        # Convert to HTML string
        print("[DEBUG] Starting to convert results to HTML...")

        # Declare variable at function scope for game-theoretic data
        game_theoretic_data = None

        # Special handling for interviewer prefab to extract questionnaire results
        if config.game_master.prefab == 'interviewer__GameMaster' and sim.game_masters:
            print(f"[DEBUG] Interviewer prefab detected, extracting questionnaire results")
            try:
                gm = sim.game_masters[0]
                print(f"[DEBUG] Game master name: {gm.name}")

                questionnaire_component = gm.get_component('questionnaire')
                print(f"[DEBUG] Questionnaire component: {questionnaire_component}")

                if questionnaire_component:
                    import pandas as pd

                    # Debug: Check questionnaire state
                    print(f"[DEBUG] Questionnaire component type: {type(questionnaire_component).__name__}")
                    print(f"[DEBUG] Questionnaire state: {questionnaire_component.get_state() if hasattr(questionnaire_component, 'get_state') else 'N/A'}")

                    results_df = questionnaire_component.get_questionnaires_results()
                    answers = questionnaire_component.get_answers()

                    print(f"[DEBUG] Results DataFrame: {results_df}")
                    print(f"[DEBUG] Answers dict: {answers}")
                    print(f"[DEBUG] Number of players with answers: {len(answers)}")

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
                    print(f"[DEBUG] Generated custom questionnaire HTML ({len(questionnaire_html)} chars)")
                else:
                    print("[WARNING] No questionnaire component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract questionnaire results: {e}")
                import traceback
                traceback.print_exc()

        # Special handling for game-theoretic prefab to extract payoff matrix results
        elif config.game_master.prefab == 'game_theoretic_and_dramaturgic__GameMaster' and sim.game_masters:
            print(f"[DEBUG] Game-theoretic prefab detected, extracting payoff matrix results")
            # game_theoretic_data already declared at function scope
            try:
                gm = sim.game_masters[0]
                print(f"[DEBUG] Game master name: {gm.name}")

                # Try to get payoff_matrix component by iterating through all components
                from concordia.components.game_master import payoff_matrix as payoff_matrix_lib
                payoff_component = None

                # Search for payoff matrix component using get_component_names
                component_names = gm.get_component_names() if hasattr(gm, 'get_component_names') else []
                print(f"[DEBUG] Game master has {len(component_names)} components")

                for component_name in component_names:
                    component = gm.get_component(component_name)
                    if isinstance(component, payoff_matrix_lib.PayoffMatrix):
                        payoff_component = component
                        print(f"[DEBUG] Found payoff matrix component: {component_name}")
                        break

                if payoff_component:
                    # Get scores and state
                    scores = payoff_component.get_scores()
                    state = payoff_component.get_state()
                    history = state.get('history', [])

                    print(f"[DEBUG] Player scores: {scores}")
                    print(f"[DEBUG] History entries: {len(history)}")
                    print(f"[DEBUG] Partial joint action: {state.get('partial_joint_action')}")

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
                    print(f"[DEBUG] Generated custom game-theoretic HTML ({len(game_theoretic_html)} chars)")
                else:
                    print("[WARNING] No payoff matrix component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract game-theoretic results: {e}")
                import traceback
                traceback.print_exc()

        try:
            results_html = str(results)
            print(f"[DEBUG] Results converted to HTML (length: {len(results_html)})")
        except Exception as e:
            print(f"[ERROR] Failed to convert results to HTML: {e}")
            import traceback
            traceback.print_exc()
            results_html = str(results)  # Try again

        # Inject CSS styles for better readability
        styled_html = _inject_html_styles(results_html)

        # Save HTML log to file with proper naming convention
        print("💾 Saving simulation log...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create safe filename from premise (first 50 chars, alphanumeric and basic symbols only)
        import re
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

        agent_metadata = {
            "timestamp": timestamp,
            "premise": config.premise,
            "game_master": {
                "prefab": config.game_master.prefab,
                "name": config.game_master.name
            },
            "agents": []
        }

        for agent in config.agents:
            agent_info = {
                "id": agent.id,
                "name": agent.name,
                "prefab": agent.prefab,
                "goal": agent.goal or "",
                "memories_count": len(agent.memories) if agent.memories else 0
            }
            agent_metadata["agents"].append(agent_info)

        # Add game-theoretic action data if available
        if game_theoretic_data is not None:
            agent_metadata["game_theoretic"] = {
                "scores": game_theoretic_data.get('scores', {}),
                "actions_by_player": game_theoretic_data.get('actions_by_player', {})
            }
            print(f"[DEBUG] Added game-theoretic data to metadata for {len(game_theoretic_data.get('actions_by_player', {}))} players")

        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(agent_metadata, f, indent=2)

        print(f"✓ Log saved to: {log_filename}")
        print(f"   Size: {len(styled_html):,} characters")
        print(f"✓ Metadata saved to: {metadata_filename}\n")

        # Send completion event WITHOUT full results HTML
        # The frontend will fetch the results from the log file instead
        # This avoids sending 1MB+ data in a single SSE event which can cause network issues
        print("[DEBUG] About to yield SIMULATION_COMPLETE event")

        # Determine completion status and message
        if simulation_error:
            completion_message = f'Simulation failed: {simulation_error}'
            completed = False
        else:
            completion_message = 'Simulation completed successfully'
            completed = True

        completion_event = _format_sse(EventType.SIMULATION_COMPLETE, {
            'message': completion_message,
            'steps_completed': step_count_tracker[0],
            'timestamp': datetime.datetime.now().isoformat(),
            'log_path': str(log_path),
            'log_filename': log_filename,
            'completed': completed,
            'error': simulation_error,
            'error_type': simulation_error_type
            # NOTE: 'results' field removed - frontend will load from log file
        })
        print(f"[DEBUG] SIMULATION_COMPLETE event formatted (length: {len(completion_event)} chars)")
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
    print(f"[DEBUG] _format_sse: event_type={event_type.value}, data_length={len(json.dumps(data))}, total_length={len(formatted)}")
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
    import re
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
            """
            # Extract step number from checkpoint data
            step = checkpoint_data.get('checkpoint_counter', 0)
            step_count[0] = step
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
        print(f"[DEBUG] Starting simulation play with max_steps={config.max_steps}")
        print(f"[DEBUG] Game master prefab: {config.game_master.prefab}")
        print(f"[DEBUG] Number of entities: {len(sim.entities)}")
        print(f"[DEBUG] Number of game masters: {len(sim.game_masters)}")
        for entity in sim.entities:
            print(f"[DEBUG] Entity: {entity.name}, type: {type(entity).__name__}")
        for gm in sim.game_masters:
            print(f"[DEBUG] Game Master: {gm.name}, type: {type(gm).__name__}")

        results = sim.play(
            max_steps=config.max_steps,
            get_state_callback=progress_callback,
            verbose=True
        )
        print(f"[DEBUG] Simulation play completed, results type: {type(results).__name__}")

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
        results_html = str(results)

        # Declare variable at function scope for game-theoretic data
        game_theoretic_data = None

        # Special handling for interviewer prefab to extract questionnaire results
        if config.game_master.prefab == 'interviewer__GameMaster' and sim.game_masters:
            try:
                gm = sim.game_masters[0]
                print(f"[DEBUG] Game master name: {gm.name}")
                print(f"[DEBUG] Game master components: {list(gm.get_component_names()) if hasattr(gm, 'get_component_names') else 'N/A'}")

                questionnaire_component = gm.get_component('questionnaire')
                print(f"[DEBUG] Questionnaire component: {questionnaire_component}")

                if questionnaire_component:
                    import pandas as pd

                    # Debug: Check questionnaire state
                    print(f"[DEBUG] Questionnaire component type: {type(questionnaire_component).__name__}")
                    print(f"[DEBUG] Questionnaire state: {questionnaire_component.get_state() if hasattr(questionnaire_component, 'get_state') else 'N/A'}")

                    results_df = questionnaire_component.get_questionnaires_results()
                    answers = questionnaire_component.get_answers()

                    print(f"[DEBUG] Results DataFrame: {results_df}")
                    print(f"[DEBUG] Answers dict: {answers}")
                    print(f"[DEBUG] Number of players with answers: {len(answers)}")

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
                    print(f"[DEBUG] Generated custom questionnaire HTML ({len(results_html)} chars)")
                else:
                    print("[WARNING] No questionnaire component found in game master")
            except Exception as e:
                print(f"[ERROR] Failed to extract questionnaire results: {e}")
                import traceback
                traceback.print_exc()

        # Special handling for game-theoretic prefab to extract payoff matrix results
        elif config.game_master.prefab == 'game_theoretic_and_dramaturgic__GameMaster' and sim.game_masters:
            print(f"[DEBUG] Game-theoretic prefab detected, extracting payoff matrix results")
            # game_theoretic_data already declared at function scope
            try:
                gm = sim.game_masters[0]
                print(f"[DEBUG] Game master name: {gm.name}")

                # Try to get payoff_matrix component by iterating through all components
                from concordia.components.game_master import payoff_matrix as payoff_matrix_lib
                payoff_component = None

                # Search for payoff matrix component using get_component_names
                component_names = gm.get_component_names() if hasattr(gm, 'get_component_names') else []
                print(f"[DEBUG] Game master has {len(component_names)} components")

                for component_name in component_names:
                    component = gm.get_component(component_name)
                    if isinstance(component, payoff_matrix_lib.PayoffMatrix):
                        payoff_component = component
                        print(f"[DEBUG] Found payoff matrix component: {component_name}")
                        break

                if payoff_component:
                    # Get scores and state
                    scores = payoff_component.get_scores()
                    state = payoff_component.get_state()
                    history = state.get('history', [])

                    print(f"[DEBUG] Player scores: {scores}")
                    print(f"[DEBUG] History entries: {len(history)}")
                    print(f"[DEBUG] Partial joint action: {state.get('partial_joint_action')}")

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
                    print(f"[DEBUG] Generated custom game-theoretic HTML ({len(game_theoretic_html)} chars)")
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

        agent_metadata = {
            "timestamp": timestamp,
            "premise": config.premise,
            "game_master": {
                "prefab": config.game_master.prefab,
                "name": config.game_master.name
            },
            "agents": []
        }

        for agent in config.agents:
            agent_info = {
                "id": agent.id,
                "name": agent.name,
                "prefab": agent.prefab,
                "goal": agent.goal or "",
                "memories_count": len(agent.memories) if agent.memories else 0
            }
            agent_metadata["agents"].append(agent_info)

        # Add game-theoretic action data if available
        if game_theoretic_data is not None:
            agent_metadata["game_theoretic"] = {
                "scores": game_theoretic_data.get('scores', {}),
                "actions_by_player": game_theoretic_data.get('actions_by_player', {})
            }
            print(f"[DEBUG] Added game-theoretic data to metadata for {len(game_theoretic_data.get('actions_by_player', {}))} players")

        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(agent_metadata, f, indent=2)

        print(f"✓ Log saved to: {log_filename}")
        print(f"   Size: {len(styled_html):,} characters")
        print(f"✓ Metadata saved to: {metadata_filename}\n")

        # Cleanup state
        simulation_state.cleanup_simulation(task_id)

        # Return results with log path
        return {
            'config': config.model_dump(mode='json'),
            'completed': True,
            'timestamp': datetime.datetime.now().isoformat(),
            'results': results_html,  # Return original for in-app viewing (styles injected separately in frontend)
            'log_path': str(log_path),
            'log_filename': log_filename,
            'task_id': task_id
        }

    except asyncio.CancelledError:
        # Handle cancellation
        simulation_state.update_simulation_status(task_id, status="cancelled")
        simulation_state.cleanup_simulation(task_id)
        raise

    except Exception as e:
        # Handle errors
        simulation_state.update_simulation_status(
            task_id,
            status="error",
            error=str(e)
        )
        simulation_state.cleanup_simulation(task_id)
        raise


def _inject_html_styles(html: str) -> str:
    """Inject CSS styles into Concordia HTML logs for better readability."""
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
        # Has html tag but no head - add head
        import re
        return re.sub(r'(<html[^>]*>)', r'\1<head>' + styles + '</head>', html)
    elif '<body>' in html:
        # Has body but no html - inject at start of body
        return html.replace('<body>', '<body>' + styles)
    else:
        # Fragment - wrap properly
        return '<!DOCTYPE html><html><head>' + styles + '</head><body>' + html + '</body></html>'
