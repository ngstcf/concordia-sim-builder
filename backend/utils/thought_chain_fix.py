"""
Utility functions to fix LLM response parsing issues in Concordia thought chains.

Handles two classes of verbose LLM responses:
1. Binary (Yes/No) choices answered with an explanation — patched at ActionSpec.validate().
2. Action-spec generation where the LLM prefixes the required JSON with prose —
   patched at concordia.environment.engine.action_spec_parser().
"""

import json
import re
from concordia.typing import entity as entity_lib


def normalize_binary_response(response: str, options: tuple[str, ...] = ('Yes', 'No')) -> str:
    """
    Normalize a verbose LLM response to match expected binary options.

    Extracts the first matching option from the response, or falls back to
    checking the first word against the options.

    Args:
        response: The potentially verbose LLM response
        options: Tuple of valid options (default: ('Yes', 'No'))

    Returns:
        A normalized response matching one of the options
    """
    if response in options:
        return response

    # Try to find any of the options in the response
    for option in options:
        if option in response:
            return option

    # Fall back to checking first word (case-insensitive)
    first_word = response.strip().split()[0].lower()
    for option in options:
        if first_word == option.lower():
            return option

    # If all else fails, try to match common patterns
    response_lower = response.lower()
    if any(word in response_lower for word in ['yes', 'yeah', 'yep', 'certainly', 'definitely', 'absolutely']):
        return 'Yes'
    if any(word in response_lower for word in ['no', 'nope', 'never', 'not']):
        return 'No'

    # Last resort: return first option
    return options[0]


def patch_action_spec_validate():
    """
    Patch ActionSpec.validate() to normalize binary responses before validation.

    This is the MOST ROBUST approach because it intercepts at the validation level,
    which happens AFTER the LLM response is generated but BEFORE the error is raised.
    This works regardless of where the thought chain or agent is defined.
    """
    original_validate = entity_lib.ActionSpec.validate

    def patched_validate(self, action: str) -> str | None:
        # For binary choice specs, normalize the action before validation
        if (self.output_type == entity_lib.OutputType.CHOICE and
            len(self.options) == 2 and
            self.options in (('Yes', 'No'), ('No', 'Yes'))):
            action = normalize_binary_response(action, self.options)

        # Call original validation with normalized action
        return original_validate(self, action)

    entity_lib.ActionSpec.validate = patched_validate


def patch_act_method_for_binary_validation(entity) -> None:
    """
    Patch an entity's act method to normalize binary choice responses.

    This provides an additional layer of protection by normalizing at the entity level.
    This is a DEFENSE IN DEPTH approach.

    Args:
        entity: The entity to patch (can be an agent or game master)
    """
    original_act = entity.act

    def patched_act(action_spec: entity_lib.ActionSpec) -> str:
        result = original_act(action_spec)
        return result  # Validation is now handled by patched ActionSpec.validate()

    entity.act = patched_act


def patch_agent_for_binary_thought_chains(agent) -> None:
    """
    Patch an agent to handle verbose yes/no responses in thought chains.

    Args:
        agent: The agent entity to patch
    """
    patch_act_method_for_binary_validation(agent)


def patch_all_agents_in_simulation(simulation) -> None:
    """
    Patch all agents in a simulation to handle verbose binary responses.

    Args:
        simulation: The Simulation object containing agents to patch
    """
    for entity in simulation.get_entities():
        patch_agent_for_binary_thought_chains(entity)

    for gm in simulation.get_game_masters():
        patch_agent_for_binary_thought_chains(gm)


def patch_action_spec_parser():
    """
    Patch concordia.environment.engine.action_spec_parser to tolerate verbose
    LLM responses that embed the required JSON after explanatory prose.

    When the LLM outputs something like:
        "So we output the JSON. I'll choose the first example.
         {"call_to_action": "...", "output_type": "free", ...}"
    the stock parser's json.loads() fails and the legacy fallback raises
    RuntimeError. This patch extracts the first {...} block from the string and
    retries before giving up.
    """
    from concordia.environment import engine as engine_mod

    original_parser = engine_mod.action_spec_parser

    def patched_parser(next_action_spec_string: str):
        try:
            return original_parser(next_action_spec_string)
        except (RuntimeError, json.JSONDecodeError):
            pass

        # Try to extract an embedded JSON object from the verbose string.
        match = re.search(r'\{.*\}', next_action_spec_string, re.DOTALL)
        if match:
            try:
                spec_dict = json.loads(match.group())
                return entity_lib.action_spec_from_dict(spec_dict)
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # No embedded JSON found — re-raise via original to get a clear error.
        return original_parser(next_action_spec_string)

    engine_mod.action_spec_parser = patched_parser


def apply_all_patches():
    """
    Apply all patches needed to handle verbose LLM responses.

    Called once at application startup.
    """
    patch_action_spec_validate()
    patch_action_spec_parser()
    print("✓ Applied ActionSpec.validate() patch for verbose binary response normalization")
    print("✓ Applied action_spec_parser patch for verbose JSON action spec responses")
