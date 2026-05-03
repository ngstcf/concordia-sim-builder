"""
Registry and factory for Concordia contrib GM components.

Exposes Death, GMWorkingMemory, LocationBasedFilter, NpcEventGenerator, and
SpaceshipSystem through a JSON-configurable interface so the builder UI can
add them as extra_components on any Game Master.
"""
import datetime
from typing import Any, Sequence

from concordia.language_model import language_model


CONTRIB_GM_REGISTRY: dict[str, dict[str, Any]] = {
    "death": {
        "name": "Death Mechanics",
        "description": "Removes deceased actors. Uses LLM to detect death events from narrative.",
        "category": "Narrative",
        "params": {
            "death_message": {
                "type": "string",
                "default": "{actor_name} has died.",
                "description": "Message template when an actor dies",
            },
        },
    },
    "gm_working_memory": {
        "name": "GM Working Memory",
        "description": "GM maintains a 500-700 word narrative summary of simulation state.",
        "category": "Narrative",
        "params": {
            "num_memories_to_retrieve": {
                "type": "integer",
                "default": 100,
                "min": 10,
                "max": 500,
                "description": "Number of memories to retrieve for summary",
            },
        },
    },
    "npc_event_generator": {
        "name": "NPC Event Generator",
        "description": "Random ambient NPC events at configurable probability per step.",
        "category": "World",
        "params": {
            "scenario_context": {
                "type": "string",
                "default": "",
                "description": "Context for generating realistic events",
            },
            "event_probability": {
                "type": "float",
                "default": 0.15,
                "min": 0.0,
                "max": 1.0,
                "description": "Probability of an event each step (0-1)",
            },
        },
    },
    "location_based_filter": {
        "name": "Location-Based Filter",
        "description": "Agents can only observe events at their location. Enforces partial observability.",
        "category": "World",
        "params": {},
    },
    "spaceship_system": {
        "name": "Spaceship System",
        "description": "Tracks system health with probabilistic failures.",
        "category": "World",
        "params": {
            "system_name": {
                "type": "string",
                "default": "Life Support",
                "description": "Name of the spaceship system",
            },
            "system_max_health": {
                "type": "integer",
                "default": 100,
                "min": 1,
                "max": 1000,
                "description": "Maximum health of the system",
            },
            "system_failure_probability": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "max": 1.0,
                "description": "Probability of failure per step",
            },
            "warning_message": {
                "type": "string",
                "default": "Warning: {system_name} failing!",
                "description": "Warning message template",
            },
        },
    },
}


class _SimpleClock:
    """Minimal clock wrapper for NpcEventGenerator compatibility."""

    def __init__(self):
        self._game_clock = self

    def now(self):
        return datetime.datetime.now()


def create_contrib_gm_component(
    component_id: str,
    model: language_model.LanguageModel,
    config: dict[str, Any],
    agent_names: Sequence[str],
) -> Any:
    """Instantiate a contrib GM component from JSON config."""
    if component_id not in CONTRIB_GM_REGISTRY:
        raise ValueError(f"Unknown contrib GM component: {component_id}")

    registry_entry = CONTRIB_GM_REGISTRY[component_id]
    defaults = {k: v["default"] for k, v in registry_entry["params"].items() if "default" in v}
    params = {**defaults, **config}

    if component_id == "death":
        from concordia.contrib.components.game_master import death
        return death.Death(
            model=model,
            pre_act_label="Death Check",
            actor_names=list(agent_names),
            death_message=params.get("death_message", "{actor_name} has died."),
        )

    if component_id == "gm_working_memory":
        from concordia.contrib.components.game_master import gm_working_memory
        return gm_working_memory.GMWorkingMemory(
            model=model,
            num_memories_to_retrieve=params.get("num_memories_to_retrieve", 100),
        )

    if component_id == "npc_event_generator":
        from concordia.contrib.components.game_master import npc_event_generator
        return npc_event_generator.NpcEventGenerator(
            model=model,
            clock=_SimpleClock(),
            scenario_context=params.get("scenario_context", ""),
            event_probability=params.get("event_probability", 0.15),
        )

    if component_id == "location_based_filter":
        from concordia.contrib.components.game_master import location_based_filter
        return location_based_filter.LocationBasedFilter(
            model=model,
            entity_names=list(agent_names),
        )

    if component_id == "spaceship_system":
        from concordia.contrib.components.game_master import spaceship_system
        return spaceship_system.SpaceshipSystem(
            model=model,
            system_name=params.get("system_name", "Life Support"),
            system_max_health=params.get("system_max_health", 100),
            system_failure_probability=params.get("system_failure_probability", 0.1),
            warning_message=params.get("warning_message", "Warning: {system_name} failing!"),
            pre_act_label=f"{params.get('system_name', 'Life Support')} Status",
        )

    raise ValueError(f"No factory for component: {component_id}")
