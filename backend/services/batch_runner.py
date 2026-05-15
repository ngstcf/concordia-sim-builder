"""
Batch runner for executing multiple simulation runs with parameter sweeps.

Runs simulations sequentially, yielding SSE-compatible progress events.
"""

import copy
import json
import time
import uuid
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from backend.models.schemas import ExecutionRequest, LLMSettings, SimulationConfig
from backend.services.simulation_state import simulation_state


BATCH_DIR = Path("logs")


def _set_nested_field(obj: Any, field_path: str, value: Any):
    """Set a nested field on a Pydantic model or dict, e.g. 'llm_settings.temperature'."""
    parts = field_path.split('.')
    current = obj
    for part in parts[:-1]:
        if hasattr(current, part):
            current = getattr(current, part)
        elif isinstance(current, dict):
            current = current[part]
        else:
            return
    final = parts[-1]
    if hasattr(current, final):
        setattr(current, final, value)
    elif isinstance(current, dict):
        current[final] = value


def _generate_param_combinations(
    sweep_parameters: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generate all combinations from sweep parameters."""
    if not sweep_parameters:
        return [{}]

    fields = [p['field'] for p in sweep_parameters]
    value_lists = [p['values'] for p in sweep_parameters]

    combinations = []
    for combo in product(*value_lists):
        combinations.append(dict(zip(fields, combo)))
    return combinations


def _parse_sse_event(event_str: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Parse an SSE event block into event type + JSON data payload."""
    event_type: Optional[str] = None
    data_lines: List[str] = []

    for raw_line in event_str.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(':'):
            continue
        if line.startswith('event:'):
            event_type = line[6:].strip()
        elif line.startswith('data:'):
            data_lines.append(line[5:].strip())

    if not data_lines:
        return event_type, None

    data_text = '\n'.join(data_lines)
    try:
        return event_type, json.loads(data_text)
    except (json.JSONDecodeError, ValueError):
        return event_type, None


class BatchRunner:
    def __init__(self):
        self._batches: Dict[str, Dict[str, Any]] = {}

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        return self._batches.get(batch_id)

    def cancel_batch(self, batch_id: str) -> bool:
        batch = self._batches.get(batch_id)
        if batch and batch['status'] == 'running':
            batch['status'] = 'cancelled'
            current_task = batch.get('current_task_id')
            if current_task:
                simulation_state.cancel_simulation(current_task)
            return True
        return False

    async def run_batch(
        self,
        config: SimulationConfig,
        llm_settings: LLMSettings,
        gm_llm_settings: Optional[LLMSettings],
        num_runs: int,
        sweep_parameters: List[Dict[str, Any]],
        batch_name: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Run a batch of simulations, yielding SSE events."""
        from backend.services.simulation_runner import run_simulation_stream

        batch_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
        param_combinations = _generate_param_combinations(sweep_parameters)
        total_runs = len(param_combinations) * num_runs

        batch_state = {
            'batch_id': batch_id,
            'batch_name': batch_name or f'Batch {batch_id}',
            'status': 'running',
            'total_runs': total_runs,
            'completed_runs': 0,
            'failed_runs': 0,
            'current_run': 0,
            'current_task_id': None,
            'run_results': [],
            'started_at': datetime.now().isoformat(),
            'param_combinations': [
                {k: str(v) for k, v in combo.items()} for combo in param_combinations
            ],
        }
        self._batches[batch_id] = batch_state

        yield f"data: {json.dumps({'type': 'batch_start', 'batch_id': batch_id, 'total_runs': total_runs, 'param_combinations': batch_state['param_combinations']})}\n\n"

        run_index = 0
        for combo in param_combinations:
            for repeat in range(num_runs):
                if batch_state['status'] == 'cancelled':
                    yield f"data: {json.dumps({'type': 'batch_cancelled', 'batch_id': batch_id, 'completed_runs': batch_state['completed_runs']})}\n\n"
                    self._save_batch_metadata(batch_state)
                    return

                run_index += 1
                batch_state['current_run'] = run_index

                run_config = config.model_copy(deep=True)
                run_llm = llm_settings.model_copy(deep=True)
                run_gm_llm = gm_llm_settings.model_copy(deep=True) if gm_llm_settings else None

                for field, value in combo.items():
                    if field.startswith('llm_settings.'):
                        _set_nested_field(run_llm, field.replace('llm_settings.', ''), value)
                    elif field.startswith('config.'):
                        _set_nested_field(run_config, field.replace('config.', ''), value)
                    elif field == 'temperature':
                        run_llm.temperature = float(value)
                    elif field == 'max_steps':
                        run_config.max_steps = int(value)

                combo_str = ', '.join(f'{k}={v}' for k, v in combo.items()) if combo else 'default'
                yield f"data: {json.dumps({'type': 'run_start', 'batch_id': batch_id, 'run_index': run_index, 'total_runs': total_runs, 'parameters': {k: str(v) for k, v in combo.items()}, 'repeat': repeat + 1})}\n\n"

                run_result = {
                    'run_index': run_index,
                    'parameters': {k: str(v) for k, v in combo.items()},
                    'repeat': repeat + 1,
                    'status': 'running',
                    'started_at': datetime.now().isoformat(),
                }

                start_time = time.time()
                log_filename = None
                error_msg = None

                try:
                    async for event_str in run_simulation_stream(
                        run_config, run_llm, gm_llm_settings=run_gm_llm
                    ):
                        if batch_state['status'] == 'cancelled':
                            break

                        inner_event_type, inner_event_data = _parse_sse_event(event_str)
                        if not inner_event_type or inner_event_data is None:
                            continue

                        if inner_event_type == 'simulation_start':
                            msg = inner_event_data.get('message')
                            if msg:
                                run_status_event = {
                                    'type': 'run_status',
                                    'batch_id': batch_id,
                                    'run_index': run_index,
                                    'total_runs': total_runs,
                                    'message': msg,
                                }
                                yield f"data: {json.dumps(run_status_event)}\n\n"
                        elif inner_event_type == 'step_progress':
                            run_progress_event = {
                                'type': 'run_progress',
                                'batch_id': batch_id,
                                'run_index': run_index,
                                'total_runs': total_runs,
                                **inner_event_data,
                            }
                            yield f"data: {json.dumps(run_progress_event)}\n\n"
                        elif inner_event_type == 'simulation_complete':
                            log_filename = inner_event_data.get('log_filename', '')
                        elif inner_event_type == 'error':
                            error_msg = inner_event_data.get('error', 'Unknown error')
                            run_error_event = {
                                'type': 'run_error',
                                'batch_id': batch_id,
                                'run_index': run_index,
                                'total_runs': total_runs,
                                'error': error_msg,
                            }
                            yield f"data: {json.dumps(run_error_event)}\n\n"

                except Exception as e:
                    error_msg = str(e)

                elapsed = time.time() - start_time
                run_result['elapsed_seconds'] = round(elapsed, 1)
                run_result['log_filename'] = log_filename
                run_result['completed_at'] = datetime.now().isoformat()

                if error_msg:
                    run_result['status'] = 'failed'
                    run_result['error'] = error_msg
                    batch_state['failed_runs'] += 1
                else:
                    run_result['status'] = 'completed'
                    batch_state['completed_runs'] += 1

                batch_state['run_results'].append(run_result)

                yield f"data: {json.dumps({'type': 'run_complete', 'batch_id': batch_id, 'run_index': run_index, 'total_runs': total_runs, 'run_result': run_result, 'completed_runs': batch_state['completed_runs'], 'failed_runs': batch_state['failed_runs']})}\n\n"

        batch_state['status'] = 'completed'
        batch_state['completed_at'] = datetime.now().isoformat()
        self._save_batch_metadata(batch_state)

        yield f"data: {json.dumps({'type': 'batch_complete', 'batch_id': batch_id, 'total_runs': total_runs, 'completed_runs': batch_state['completed_runs'], 'failed_runs': batch_state['failed_runs'], 'run_results': batch_state['run_results']})}\n\n"

    def _save_batch_metadata(self, batch_state: Dict[str, Any]):
        """Save batch metadata to disk."""
        batch_file = BATCH_DIR / f"batch_{batch_state['batch_id']}.json"
        try:
            with open(batch_file, 'w') as f:
                json.dump(batch_state, f, indent=2, default=str)
        except Exception as e:
            print(f"[BatchRunner] Failed to save batch metadata: {e}")

    def list_batches(self) -> List[Dict[str, Any]]:
        """List all batch metadata files."""
        batches = []
        for f in sorted(BATCH_DIR.glob("batch_*.json"), reverse=True):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                    batches.append({
                        'batch_id': data.get('batch_id', ''),
                        'batch_name': data.get('batch_name', ''),
                        'status': data.get('status', ''),
                        'total_runs': data.get('total_runs', 0),
                        'completed_runs': data.get('completed_runs', 0),
                        'failed_runs': data.get('failed_runs', 0),
                        'started_at': data.get('started_at', ''),
                    })
            except Exception:
                pass
        return batches


batch_runner = BatchRunner()
