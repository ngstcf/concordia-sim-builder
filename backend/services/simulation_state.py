"""
Simulation state manager for tracking and controlling running simulations.
"""
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import threading


@dataclass
class RunningSimulation:
    """Represents a running simulation."""
    task_id: str
    config: Any
    started_at: datetime = field(default_factory=datetime.now)
    status: str = "running"
    should_cancel: bool = False
    steps_completed: int = 0
    error: Optional[str] = None


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
        self._lock = threading.Lock()

    def register_simulation(self, task_id: str, config: Any) -> RunningSimulation:
        """Register a new simulation."""
        with self._lock:
            sim = RunningSimulation(task_id=task_id, config=config)
            self._simulations[task_id] = sim
            return sim

    def get_simulation(self, task_id: str) -> Optional[RunningSimulation]:
        """Get a simulation by task ID."""
        with self._lock:
            return self._simulations.get(task_id)

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
            if error:
                sim.error = error

            return True

    def cleanup_simulation(self, task_id: str) -> bool:
        """Remove a completed/cancelled simulation from tracking."""
        with self._lock:
            if task_id in self._simulations:
                del self._simulations[task_id]
                return True
            return False

    def get_all_simulations(self) -> Dict[str, Dict]:
        """Get status of all tracked simulations."""
        with self._lock:
            return {
                task_id: {
                    "task_id": sim.task_id,
                    "started_at": sim.started_at.isoformat(),
                    "status": sim.status,
                    "steps_completed": sim.steps_completed,
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
