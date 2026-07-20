"""
Grounded Variables Component for Concordia simulations.

This module implements a component for tracking and updating simulation variables
over time, following the Concordia paper's recommendation for "grounded variables"
that can be tracked and updated by the Game Master.

Based on the existing WorldState and Inventory components in Concordia.
"""

import dataclasses
import re
from typing import Any, Optional, Dict, List, Union
from enum import Enum

from concordia.language_model import language_model
from concordia.typing import entity_component
from concordia.typing import entity as entity_lib


class VariableType(str, Enum):
    """Types of grounded variables."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"


@dataclasses.dataclass
class VariableConfig:
    """Configuration for a single grounded variable."""
    name: str
    variable_type: VariableType
    description: str
    default_value: Any = None
    min_value: Optional[float] = None  # For numerical/percentage
    max_value: Optional[float] = None  # For numerical/percentage
    allowed_values: Optional[List[str]] = None  # For categorical
    update_rule: Optional[str] = None  # Description of how it updates


class GroundedVariablesComponent(
    entity_component.ContextComponent,
    entity_component.ComponentWithLogging
):
    """Component for tracking and updating grounded variables in a simulation.

    This component allows the Game Master to track variables that change over
    the course of a simulation, such as:
    - Resource levels (health, money, energy)
    - Social metrics (trust, approval, influence)
    - Environmental state (temperature, danger level)
    - Counters (steps completed, items collected)

    The component maintains the current state of all variables and their
    historical values for analysis.
    """

    def __init__(
        self,
        model: language_model.LanguageModel,
        variable_configs: List[VariableConfig],
        initial_values: Optional[Dict[str, Any]] = None,
        pre_act_label: str = '\nGrounded Variables',
    ):
        """Initialize the grounded variables component.

        Args:
            model: Language model for interpreting updates
            variable_configs: List of variable configurations
            initial_values: Optional initial values (defaults to config defaults)
            pre_act_label: Label for pre-act output
        """
        self._model = model
        self._variable_configs = {cfg.name: cfg for cfg in variable_configs}
        self._pre_act_label = pre_act_label

        # Initialize current values
        self._current_values: Dict[str, Any] = {}
        for cfg in variable_configs:
            if initial_values and cfg.name in initial_values:
                self._current_values[cfg.name] = initial_values[cfg.name]
            elif cfg.default_value is not None:
                self._current_values[cfg.name] = cfg.default_value
            else:
                # Set reasonable defaults based on type
                if cfg.variable_type == VariableType.BOOLEAN:
                    self._current_values[cfg.name] = False
                elif cfg.variable_type in [VariableType.NUMERICAL, VariableType.PERCENTAGE]:
                    self._current_values[cfg.name] = cfg.min_value if cfg.min_value is not None else 0
                elif cfg.variable_type == VariableType.CATEGORICAL:
                    self._current_values[cfg.name] = cfg.allowed_values[0] if cfg.allowed_values else "unknown"

        # Track history for each variable
        self._history: Dict[str, List[tuple[int, Any]]] = {
            cfg.name: [] for cfg in variable_configs
        }
        self._step_counter = 0

        self._name = "grounded_variables"

    def get_name(self) -> str:
        """Return the component name."""
        return self._name

    def get_state(self) -> str:
        """Return the current state as a formatted string."""
        if not self._current_values:
            return "No grounded variables defined."

        lines = ["Current grounded variable values:"]
        for name, value in self._current_values.items():
            cfg = self._variable_configs[name]
            lines.append(f"  - {name}: {value} ({cfg.variable_type.value})")
            if cfg.description:
                lines.append(f"    Description: {cfg.description}")

        return "\n".join(lines)

    def set_state(self, state: str) -> None:
        """Set state from string (for deserialization)."""
        # Parse state string to extract values
        # Format: "name: value (type)"
        for line in state.split('\n'):
            if ':' in line and not line.startswith('Current'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip().replace('- ', '').replace('  ', '')
                    value_part = parts[1].strip()
                    # Remove type info
                    value = value_part.split('(')[0].strip()
                    # Try to set the value
                    try:
                        self._current_values[name] = self._parse_value(name, value)
                    except (KeyError, ValueError):
                        pass

    def pre_act(
        self,
        component_name: str,
        action_spec: Optional[entity_lib.ActionSpec] = None,
    ) -> str:
        """Provide current variable values and update instructions before the GM acts."""
        lines = ["Current grounded variable values (reassess ALL of these after each event):"]
        for name, value in self._current_values.items():
            cfg = self._variable_configs[name]
            line = f"  - {name}: {value}"
            if cfg.allowed_values:
                line += f"  [allowed: {', '.join(cfg.allowed_values)}]"
            if cfg.update_rule:
                line += f"  — {cfg.update_rule}"
            lines.append(line)
        lines.append("")
        lines.append(
            "IMPORTANT: After narrating what happens, you MUST append a"
            " variable update line in exactly this format:"
        )
        lines.append("  [VARIABLES: name1=value1, name2=value2]")
        lines.append(
            "Include EVERY variable whose value changed this step."
            " Categorical variables must use one of their listed allowed values exactly."
            " If nothing changed, write [VARIABLES: NONE]."
        )
        return "\n".join(lines)

    def post_act(self, event: str) -> str:
        """Process event and update variables if needed."""
        self._step_counter += 1

        # Try structured tag first, fall back to LLM extraction
        updates = self._parse_variable_tag(event)
        if not updates:
            updates = self._extract_variable_updates(event)

        # Apply updates with validation
        for name, new_value in updates.items():
            if name in self._variable_configs:
                validated_value = self._validate_value(name, new_value)
                if validated_value is not None:
                    self._current_values[name] = validated_value

        # Record values AFTER updates so history reflects end-of-step state
        for name, value in self._current_values.items():
            self._history[name].append((self._step_counter, value))

        return f"Variables updated: {list(updates.keys()) if updates else 'None'}"

    def get_value(self, name: str) -> Any:
        """Get the current value of a variable."""
        return self._current_values.get(name)

    def set_value(self, name: str, value: Any) -> bool:
        """Manually set a variable value with validation."""
        if name not in self._variable_configs:
            return False

        validated = self._validate_value(name, value)
        if validated is not None:
            self._current_values[name] = validated
            return True
        return False

    def get_history(self, name: str) -> List[tuple[int, Any]]:
        """Get the history of a variable."""
        return self._history.get(name, [])

    def get_all_values(self) -> Dict[str, Any]:
        """Get all current variable values."""
        return self._current_values.copy()

    _VARIABLE_TAG_RE = re.compile(
        r'\[VARIABLES:\s*(.+?)\]', re.IGNORECASE
    )

    def _parse_variable_tag(self, event: str) -> Dict[str, Any]:
        """Parse a [VARIABLES: k=v, ...] tag directly from the event text."""
        match = self._VARIABLE_TAG_RE.search(event)
        if not match:
            return {}
        payload = match.group(1).strip()
        if payload.upper() == "NONE":
            return {}
        updates: Dict[str, Any] = {}
        for pair in payload.split(','):
            if '=' in pair:
                name, value = pair.split('=', 1)
                name = name.strip()
                value = value.strip()
                parsed = self._parse_value(name, value)
                if parsed is not None:
                    updates[name] = parsed
        return updates

    def _extract_variable_updates(self, event: str) -> Dict[str, Any]:
        """Use LLM to extract variable updates from the event."""
        variable_descriptions = []
        for name, cfg in self._variable_configs.items():
            desc = f"  {name} = {self._current_values[name]} ({cfg.variable_type.value})"
            if cfg.description:
                desc += f" — {cfg.description}"
            if cfg.update_rule:
                desc += f" [rule: {cfg.update_rule}]"
            variable_descriptions.append(desc)

        prompt = f"""Analyze this simulation event and determine realistic variable changes.

Event: {event}

Current variables:
{chr(10).join(variable_descriptions)}

Think about what concretely happened: Was money spent? Did morale shift? Were tasks finished or blocked? Did conditions improve or worsen?

Respond with ONLY a comma-separated list: variable_name=new_value
If nothing changed, respond with ONLY: None

Examples:
budget_remaining=8500,tasks_completed=3
team_morale=55
None"""

        try:
            response = self._model.sample_text(prompt)
            clean = response.strip().split('\n')[0].strip()

            updates: Dict[str, Any] = {}
            if clean.upper() == "NONE":
                return updates
            for pair in clean.split(','):
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    parsed = self._parse_value(name, value)
                    if parsed is not None:
                        updates[name] = parsed
            return updates
        except Exception:
            return {}

    def _parse_value(self, name: str, value_str: str) -> Any:
        """Parse a string value to the appropriate type."""
        cfg = self._variable_configs.get(name)
        if not cfg:
            return None

        value_str = value_str.strip()

        try:
            if cfg.variable_type == VariableType.BOOLEAN:
                if value_str.lower() in ['true', 'yes', '1']:
                    return True
                elif value_str.lower() in ['false', 'no', '0']:
                    return False
                else:
                    return bool(value_str)

            elif cfg.variable_type in [VariableType.NUMERICAL, VariableType.PERCENTAGE]:
                return float(value_str)

            elif cfg.variable_type == VariableType.CATEGORICAL:
                return value_str

            else:
                return value_str
        except (ValueError, TypeError):
            return None

    def _validate_value(self, name: str, value: Any) -> Optional[Any]:
        """Validate a value against the variable configuration."""
        cfg = self._variable_configs.get(name)
        if not cfg:
            return None

        try:
            if cfg.variable_type == VariableType.BOOLEAN:
                # Convert to boolean
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1']
                return bool(value)

            elif cfg.variable_type == VariableType.NUMERICAL:
                num_value = float(value)
                if cfg.min_value is not None and num_value < cfg.min_value:
                    num_value = cfg.min_value
                if cfg.max_value is not None and num_value > cfg.max_value:
                    num_value = cfg.max_value
                return num_value

            elif cfg.variable_type == VariableType.PERCENTAGE:
                num_value = float(value)
                # Clamp to 0-100
                num_value = max(0, min(100, num_value))
                return num_value

            elif cfg.variable_type == VariableType.CATEGORICAL:
                str_value = str(value)
                if cfg.allowed_values and str_value not in cfg.allowed_values:
                    # Return current value if invalid
                    return self._current_values.get(name)
                return str_value

            return value

        except (ValueError, TypeError):
            # Return current value if validation fails
            return self._current_values.get(name)


def create_grounded_variables_component(
    model: language_model.LanguageModel,
    variable_configs: List[Dict[str, Any]],
    initial_values: Optional[Dict[str, Any]] = None,
) -> GroundedVariablesComponent:
    """Create a grounded variables component from configuration dictionaries.

    Args:
        model: Language model to use
        variable_configs: List of variable configuration dictionaries
        initial_values: Optional initial values

    Returns:
        A GroundedVariablesComponent instance

    Example:
        configs = [
            {
                "name": "health",
                "variable_type": "numerical",
                "description": "Player's health points",
                "default_value": 100,
                "min_value": 0,
                "max_value": 100
            },
            {
                "name": "status",
                "variable_type": "categorical",
                "description": "Current status",
                "allowed_values": ["healthy", "injured", "critical"]
            }
        ]
        component = create_grounded_variables_component(model, configs)
    """
    parsed_configs = []
    for config in variable_configs:
        var_type = VariableType(config.get("variable_type", "numerical"))
        parsed_configs.append(VariableConfig(
            name=config["name"],
            variable_type=var_type,
            description=config.get("description", ""),
            default_value=config.get("default_value"),
            min_value=config.get("min_value"),
            max_value=config.get("max_value"),
            allowed_values=config.get("allowed_values"),
            update_rule=config.get("update_rule"),
        ))

    return GroundedVariablesComponent(
        model=model,
        variable_configs=parsed_configs,
        initial_values=initial_values
    )
