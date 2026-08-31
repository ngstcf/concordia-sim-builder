"""
Simulation state manager for tracking and controlling running simulations.
"""
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import threading

from backend.utils import event_journal


@dataclass
class RunningSimulation:
    """Represents a running simulation."""
    task_id: str
    config: Any
    started_at: datetime = field(default_factory=datetime.now)
    status: str = "running"
    should_cancel: bool = False
    steps_completed: int = 0
    last_progress_at: float = field(default_factory=time.time)
    error: Optional[str] = None
    step_controller: Optional[Any] = None
    log_filename: Optional[str] = None
    completion_data: Optional[Dict[str, Any]] = None


class SimulationStateManager:
    """
    Manages the state of running simulations and provides cancellation support.
    Thread-safe singleton pattern.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._simulations: Dict[str, RunningSimulation] = {}
        self._completed: Dict[str, RunningSimulation] = {}
        self._lock = threading.Lock()

    def register_simulation(self, task_id: str, config: Any) -> RunningSimulation:
        """Register a new simulation."""
        with self._lock:
            sim = RunningSimulation(task_id=task_id, config=config)
            self._simulations[task_id] = sim
        event_journal.record(
            "run_registered", task_id=task_id,
            max_steps=getattr(config, "max_steps", None),
            num_agents=len(config.agents) if hasattr(config, "agents") else None,
        )
        return sim

    def get_simulation(self, task_id: str) -> Optional[RunningSimulation]:
        """Get a simulation by task ID (checks running first, then completed)."""
        with self._lock:
            return self._simulations.get(task_id) or self._completed.get(task_id)

    def cancel_simulation(self, task_id: str) -> bool:
        """
        Request cancellation of a simulation.

        Returns:
            True if cancellation was requested, False if simulation not found
        """
        with self._lock:
            sim = self._simulations.get(task_id)
            if sim and sim.status == "running":
                sim.should_cancel = True
                sim.status = "cancelling"
                return True
            return False

    def update_simulation_status(
        self,
        task_id: str,
        status: Optional[str] = None,
        steps_completed: Optional[int] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update simulation status."""
        with self._lock:
            sim = self._simulations.get(task_id)
            if not sim:
                return False

            if status:
                sim.status = status
            if steps_completed is not None:
                sim.steps_completed = steps_completed
                sim.last_progress_at = time.time()
            if error:
                sim.error = error

            return True

    def complete_simulation(self, task_id: str, log_filename: str = None, completion_data: dict = None) -> bool:
        """Move a simulation to completed state (retains data for polling recovery)."""
        with self._lock:
            sim = self._simulations.pop(task_id, None)
            if sim:
                prior_status = sim.status
                sim.status = "completed"
                sim.log_filename = log_filename
                sim.completion_data = completion_data
                self._completed[task_id] = sim
                if len(self._completed) > 20:
                    oldest = next(iter(self._completed))
                    del self._completed[oldest]
        if sim:
            # Terminal journal event: this is the choke point every
            # execution path (stream, simple, resume, cancel) funnels
            # through, and it feeds the run list's outcome badges.
            data = completion_data or {}
            if prior_status == "cancelled":
                kind = "run_cancelled"
            elif data.get("completed", sim.error is None):
                kind = "run_completed"
            else:
                kind = "run_failed"
            event_journal.record(
                kind, task_id=task_id, log_filename=log_filename,
                steps_completed=sim.steps_completed,
                error=data.get("error") or sim.error,
                error_type=data.get("error_type"),
            )
            return True
        return False

    def cleanup_simulation(self, task_id: str) -> bool:
        """Remove a simulation from tracking entirely."""
        with self._lock:
            removed = self._simulations.pop(task_id, None) is not None
            removed = self._completed.pop(task_id, None) is not None or removed
            return removed

    def get_all_simulations(self) -> Dict[str, Dict]:
        """Get status of all tracked simulations."""
        with self._lock:
            return {
                task_id: {
                    "task_id": sim.task_id,
                    "started_at": sim.started_at.isoformat(),
                    "status": sim.status,
                    "steps_completed": sim.steps_completed,
                    "seconds_since_progress": round(
                        time.time() - sim.last_progress_at),
                    "error": sim.error,
                    "config": {
                        "premise": sim.config.premise[:100] if hasattr(sim.config, 'premise') else "N/A",
                        "max_steps": sim.config.max_steps if hasattr(sim.config, 'max_steps') else 0,
                        "num_agents": len(sim.config.agents) if hasattr(sim.config, 'agents') else 0
                    }
                }
                for task_id, sim in self._simulations.items()
            }

    def should_cancel(self, task_id: str) -> bool:
        """Check if a simulation should be cancelled."""
        with self._lock:
            sim = self._simulations.get(task_id)
            return sim.should_cancel if sim else False


# Global instance
simulation_state = SimulationStateManager()
