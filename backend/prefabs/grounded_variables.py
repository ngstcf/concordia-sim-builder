"""
Grounded Variables Component for Concordia simulations.

This module implements a component for tracking and updating simulation variables
over time, following the Concordia paper's recommendation for "grounded variables"
that can be tracked and updated by the Game Master.

Based on the existing WorldState and Inventory components in Concordia.
"""

import dataclasses
import logging
import re
from typing import Any, Optional, Dict, List, Union
from enum import Enum

from concordia.language_model import language_model
from concordia.typing import entity_component
from concordia.typing import entity as entity_lib

logger = logging.getLogger(__name__)


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
    cumulative: bool = False  # Running total: carried forward, never decreases
    max_delta: Optional[float] = None  # Largest permitted increase per update
    group: Optional[str] = None  # Name of the VariableGroup this belongs to


@dataclasses.dataclass
class VariableGroup:
    """A set of variables that jointly partition a whole.

    Per-variable bounds cannot express "these shares describe one
    population". Two support percentages may each be a legal 0-100 value
    while summing to an impossible total, because the game master
    re-estimates each share independently at every event and nothing checks
    them against each other. The bad total then enters the exported dataset
    silently.

    Declaring the members as a group makes the joint constraint explicit and
    checkable at the moment of update.
    """
    name: str
    members: List[str]
    sums_to: float
    tolerance: float = 1.0
    # renormalize: rescale members to satisfy the sum, preserving proportions.
    # reject:      discard this step's updates to the group, keep prior values.
    # flag:        leave values untouched; only record the violation.
    on_violation: str = "renormalize"


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
        variable_groups: Optional[List[VariableGroup]] = None,
    ):
        """Initialize the grounded variables component.

        Args:
            model: Language model for interpreting updates
            variable_configs: List of variable configurations
            initial_values: Optional initial values (defaults to config defaults)
            pre_act_label: Label for pre-act output
            variable_groups: Optional joint constraints across variables
        """
        self._model = model
        self._variable_configs = {cfg.name: cfg for cfg in variable_configs}
        self._pre_act_label = pre_act_label
        self._variable_groups = list(variable_groups or [])
        # Every invariant breach, in order, so a run's measurement integrity is
        # inspectable after the fact instead of being inferred from impossible
        # numbers in the exported dataset.
        self._violations: List[Dict[str, Any]] = []

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
            cfg = self._variable_configs.get(name)
            if cfg is None:
                continue
            lines.append(f"  - {name}: {value} ({cfg.variable_type.value})")
            if cfg.description:
                lines.append(f"    Description: {cfg.description}")

        return "\n".join(lines)

    def set_state(self, state: str) -> None:
        """Set state from string (for deserialization)."""
        for line in state.split('\n'):
            stripped = line.strip()
            # Skip header, empty lines, and description sub-lines
            if not stripped or stripped.startswith('Current') or stripped.startswith('Description:'):
                continue
            if ':' not in stripped:
                continue
            parts = stripped.split(':', 1)
            name = parts[0].strip().replace('- ', '')
            # Only restore variables that exist in this component's config
            if not name or name not in self._variable_configs:
                continue
            value = parts[1].strip().split('(')[0].strip()
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
        lines = ["Current grounded variable values:"]
        for name, value in self._current_values.items():
            cfg = self._variable_configs[name]
            line = f"  - {name}: {value}"
            if cfg.allowed_values:
                line += f"  [allowed: {', '.join(cfg.allowed_values)}]"
            if cfg.cumulative:
                line += ("  [RUNNING TOTAL: report the previous value plus"
                         " whatever this event adds; it can never decrease]")
            if cfg.update_rule:
                line += f"  — {cfg.update_rule}"
            lines.append(line)
        lines.append("")
        # "Reassess ALL of these" is right for state variables and wrong for
        # counters. A game master seeing only recent history re-derives a
        # count from the current event, so a total meant to accumulate spikes
        # while something is happening and decays back toward zero once it
        # stops, which leaves a cumulative counter useless as a measure. Keep
        # the blanket wording verbatim when nothing accumulates, so existing
        # scenarios are unaffected.
        if any(c.cumulative for c in self._variable_configs.values()):
            lines.append(
                "Reassess each value above from the current state of the world,"
                " EXCEPT those marked RUNNING TOTAL: carry those forward and add"
                " this event's contribution."
            )
        else:
            lines.append("Reassess ALL of these after each event.")
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

        # Snapshot before applying, so a rejected group update can be undone.
        previous = dict(self._current_values)

        # Apply updates with validation
        for name, new_value in updates.items():
            if name in self._variable_configs:
                validated_value = self._validate_value(name, new_value)
                if validated_value is not None:
                    self._current_values[name] = validated_value

        # Per-variable validation cannot see across variables; enforce the
        # declared joint constraints only after the whole update set is in.
        self._enforce_groups(previous)

        # Record values AFTER updates so history reflects end-of-step state
        for name in self._variable_configs:
            if name in self._current_values:
                self._history[name].append((self._step_counter, self._current_values[name]))

        return f"Variables updated: {list(updates.keys()) if updates else 'None'}"

    def _enforce_groups(self, previous: Dict[str, Any]) -> None:
        """Check and repair declared cross-variable constraints."""
        for group in self._variable_groups:
            present = [
                name for name in group.members
                if isinstance(self._current_values.get(name), (int, float))
                and not isinstance(self._current_values.get(name), bool)
            ]
            if len(present) < 2:
                continue

            total = sum(float(self._current_values[name]) for name in present)
            if abs(total - group.sums_to) <= group.tolerance:
                continue

            observed = {name: self._current_values[name] for name in present}
            action = group.on_violation

            if action == "renormalize" and total > 0:
                scale = group.sums_to / total
                for name in present:
                    self._current_values[name] = round(
                        float(self._current_values[name]) * scale, 4
                    )
            elif action == "reject":
                for name in present:
                    if name in previous:
                        self._current_values[name] = previous[name]
            else:
                action = "flag"

            self._record_violation(
                kind="group_sum",
                detail={
                    "group": group.name,
                    "members": present,
                    "observed": observed,
                    "observed_sum": round(total, 4),
                    "expected_sum": group.sums_to,
                    "action": action,
                    "repaired": {
                        name: self._current_values[name] for name in present
                    },
                },
            )

    def _record_violation(self, kind: str, detail: Dict[str, Any]) -> None:
        """Record an invariant breach and make it visible in the run log."""
        entry = {"step": self._step_counter, "kind": kind, **detail}
        self._violations.append(entry)
        logger.warning("grounded-variable invariant breach: %s", entry)

    def get_violations(self) -> List[Dict[str, Any]]:
        """Return every invariant breach recorded so far."""
        return list(self._violations)

    def get_integrity_summary(self) -> Dict[str, Any]:
        """Summarize measurement integrity for this run.

        A count of zero is itself a result: it says the declared invariants
        held for every update, which is what makes the exported series worth
        analyzing.
        """
        by_kind: Dict[str, int] = {}
        for v in self._violations:
            by_kind[v["kind"]] = by_kind.get(v["kind"], 0) + 1
        return {
            "updates_seen": self._step_counter,
            "violations": len(self._violations),
            "violations_by_kind": by_kind,
            "groups_declared": [g.name for g in self._variable_groups],
        }

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
            if cfg.cumulative:
                desc += (" [RUNNING TOTAL: previous value plus what this event"
                         " adds; never decreases]")
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

    def _apply_delta_cap(
        self, name: str, cfg: VariableConfig, num_value: float
    ) -> float:
        """Bound how far one update may move a variable.

        A running total with no ceiling is the other way a declared bound can
        be missing: `min_value: 0` with `cumulative: True` and no `max_value`
        permits unbounded growth. Because history is appended at every
        game-master phase, and there can be many phases per step, a counter
        meant to top out near the population size can drift orders of
        magnitude above it. A per-update cap bounds growth to something the
        design can justify (for a per-participant count, the population size)
        without requiring a total to be known in advance.
        """
        if cfg.max_delta is None:
            return num_value
        current = self._current_values.get(name)
        if not isinstance(current, (int, float)) or isinstance(current, bool):
            return num_value
        ceiling = float(current) + cfg.max_delta
        if num_value > ceiling:
            self._record_violation(
                kind="max_delta",
                detail={
                    "variable": name,
                    "previous": current,
                    "proposed": num_value,
                    "max_delta": cfg.max_delta,
                    "action": "clamped",
                    "repaired": ceiling,
                },
            )
            return ceiling
        return num_value

    def _apply_monotonic_floor(
        self, name: str, cfg: VariableConfig, num_value: float
    ) -> float:
        """Stop a cumulative total from going backwards.

        The prompt asks the game master to carry running totals forward, but
        one lapse would otherwise discard the accumulated count for the rest
        of the run. Enforcing it here makes the guarantee structural rather
        than a request the model may ignore.
        """
        if not cfg.cumulative:
            return num_value
        current = self._current_values.get(name)
        if isinstance(current, (int, float)) and not isinstance(current, bool):
            return max(num_value, float(current))
        return num_value

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
                num_value = self._apply_delta_cap(name, cfg, num_value)
                return self._apply_monotonic_floor(name, cfg, num_value)

            elif cfg.variable_type == VariableType.PERCENTAGE:
                num_value = float(value)
                # Clamp to 0-100
                num_value = max(0, min(100, num_value))
                num_value = self._apply_delta_cap(name, cfg, num_value)
                return self._apply_monotonic_floor(name, cfg, num_value)

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
    variable_groups: Optional[List[Dict[str, Any]]] = None,
) -> GroundedVariablesComponent:
    """Create a grounded variables component from configuration dictionaries.

    Args:
        model: Language model to use
        variable_configs: List of variable configuration dictionaries
        initial_values: Optional initial values
        variable_groups: Optional joint constraints, each a dictionary with
            `name`, `members`, `sums_to`, and optionally `tolerance` and
            `on_violation`

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
        cfg = VariableConfig(
            name=config["name"],
            variable_type=var_type,
            description=config.get("description", ""),
            default_value=config.get("default_value"),
            min_value=config.get("min_value"),
            max_value=config.get("max_value"),
            allowed_values=config.get("allowed_values"),
            update_rule=config.get("update_rule"),
            cumulative=bool(config.get("cumulative", False)),
            max_delta=config.get("max_delta"),
            group=config.get("group"),
        )
        # A running total with neither a ceiling nor a per-update cap can grow
        # without limit, and the growth is invisible until the exported series
        # is inspected. Warn at construction, where the scenario author can
        # still fix the declaration, rather than after the compute is spent.
        if cfg.cumulative and cfg.max_value is None and cfg.max_delta is None:
            logger.warning(
                "grounded variable '%s' is cumulative with no max_value and no"
                " max_delta: its running total is unbounded above",
                cfg.name,
            )
        parsed_configs.append(cfg)

    declared = {c.name for c in parsed_configs}
    parsed_groups = []
    for group in variable_groups or []:
        members = [m for m in group.get("members", []) if m in declared]
        missing = [m for m in group.get("members", []) if m not in declared]
        if missing:
            logger.warning(
                "variable group '%s' names undeclared variables: %s",
                group.get("name"), missing,
            )
        if len(members) < 2 or group.get("sums_to") is None:
            continue
        parsed_groups.append(VariableGroup(
            name=group.get("name") or "+".join(members),
            members=members,
            sums_to=float(group["sums_to"]),
            tolerance=float(group.get("tolerance", 1.0)),
            on_violation=group.get("on_violation", "renormalize"),
        ))

    # Also accept the constraint declared inline on the variables themselves,
    # so a scenario can name a group without a separate top-level block.
    for name in sorted({c.group for c in parsed_configs if c.group}):
        if any(g.name == name for g in parsed_groups):
            continue
        members = [c.name for c in parsed_configs if c.group == name]
        if len(members) < 2:
            continue
        percentages = all(
            c.variable_type == VariableType.PERCENTAGE
            for c in parsed_configs if c.group == name
        )
        if not percentages:
            logger.warning(
                "variable group '%s' declared inline but its members are not"
                " all percentages, so no total can be inferred; declare it in"
                " variable_groups with an explicit sums_to",
                name,
            )
            continue
        parsed_groups.append(VariableGroup(
            name=name, members=members, sums_to=100.0
        ))

    return GroundedVariablesComponent(
        model=model,
        variable_configs=parsed_configs,
        initial_values=initial_values,
        variable_groups=parsed_groups,
    )
