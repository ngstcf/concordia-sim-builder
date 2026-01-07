"""
Grounded Variables Component for Concordia simulations.

This module implements a component for tracking and updating simulation variables
over time, following the Concordia paper's recommendation for "grounded variables"
that can be tracked and updated by the Game Master.

Based on the existing WorldState and Inventory components in Concordia.
"""

import dataclasses
from typing import Any, Optional, Dict, List, Union
from enum import Enum

from concordia.language_model import language_model
from concordia.typing import entity_component


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
        action_spec: Optional[entity_component.ActionSpec] = None,
    ) -> str:
        """Provide current variable values before the GM acts."""
        return self.get_state()

    def post_act(self, event: str) -> str:
        """Process event and update variables if needed."""
        self._step_counter += 1

        # Record current values in history
        for name, value in self._current_values.items():
            self._history[name].append((self._step_counter, value))

        # Try to extract variable updates from the event
        # This uses the LLM to identify if any variables should change
        updates = self._extract_variable_updates(event)

        # Apply updates with validation
        for name, new_value in updates.items():
            if name in self._variable_configs:
                validated_value = self._validate_value(name, new_value)
                if validated_value is not None:
                    old_value = self._current_values[name]
                    self._current_values[name] = validated_value

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

    def _extract_variable_updates(self, event: str) -> Dict[str, Any]:
        """Use LLM to extract variable updates from the event."""
        # Build prompt for LLM
        variable_descriptions = []
        for name, cfg in self._variable_configs.items():
            desc = f"{name} ({cfg.variable_type.value}, current: {self._current_values[name]})"
            if cfg.description:
                desc += f": {cfg.description}"
            if cfg.update_rule:
                desc += f" [Update rule: {cfg.update_rule}]"
            variable_descriptions.append(desc)

        prompt = f"""Given the following event and the current state of grounded variables,
identify which variables should be updated and what their new values should be.

Event: {event}

Variables:
{chr(10).join(variable_descriptions)}

Respond with a comma-separated list of updates in the format: "variable_name=new_value".
Only include variables that actually changed based on the event.
If no variables changed, respond with "None".

Examples of valid responses:
- "trust_level=7,anger_level=3"
- "health=85,fatigue=true"
- "None"
"""

        try:
            from concordia.language_model import google_cloud_model
            response = self._model.sample_text(prompt)

            # Parse response
            updates = {}
            if response.strip() != "None":
                for update in response.split(','):
                    if '=' in update:
                        name, value = update.split('=', 1)
                        name = name.strip()
                        value = value.strip()
                        # Try to parse value
                        parsed = self._parse_value(name, value)
                        if parsed is not None:
                            updates[name] = parsed

            return updates
        except Exception as e:
            # If LLM parsing fails, return empty dict
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
