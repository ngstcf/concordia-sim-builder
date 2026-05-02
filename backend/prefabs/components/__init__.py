"""
Custom component prefabs for the Concordia Simulation Builder.

This module provides pre-built components for common psychological and social
constructs that can be easily added to agents in the simulation.

Based on the Concordia paper's recommendations for implementing classic
psychological models as component architectures.
"""
from concordia.language_model import language_model
from concordia.typing import entity_component
from typing import Any


def personality_traits_component(
    model: language_model.LanguageModel,
    traits: dict[str, str | int],
) -> entity_component.ComponentT:
    from concordia.components.agent import trait

    trait_descriptions = []
    for trait_name, value in traits.items():
        trait_descriptions.append(f"{trait_name.capitalize()}: {value}/5")

    state = f"Personality traits: {', '.join(trait_descriptions)}"

    class PersonalityComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "personality_traits"

    return PersonalityComponent(state)


def cognitive_bias_component(
    model: language_model.LanguageModel,
    bias_type: str,
    bias_strength: str = "moderate",
) -> entity_component.ComponentT:
    """
    Create a component representing a cognitive bias that affects decision-making.

    Common biases (based on Tversky & Kahneman's work):
    - confirmation_bias: Tendency to search for information that confirms beliefs
    - availability_heuristic: Overweighting easily recalled information
    - anchoring_bias: Relying too heavily on initial information
    - sunk_cost_fallacy: Continuing due to past investment
    - overconfidence_bias: Overestimating one's abilities

    Args:
        model: The language model to use
        bias_type: The type of cognitive bias
        bias_strength: How strongly this bias affects reasoning (weak/moderate/strong)

    Returns:
        A component that influences reasoning based on the specified bias
    """
    bias_descriptions = {
        "confirmation_bias": "tends to seek information confirming existing beliefs",
        "availability_heuristic": "gives disproportionate weight to easily recalled examples",
        "anchoring_bias": "relies heavily on initial information when making decisions",
        "sunk_cost_fallacy": "continues activities due to past investment despite poor prospects",
        "overconfidence_bias": "overestimates the accuracy of their judgments and abilities",
    }

    description = bias_descriptions.get(bias_type, f"exhibits {bias_type}")

    state = f"This person {description} (strength: {biasness_strength})."

    class CognitiveBiasComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "cognitive_bias"

    return CognitiveBiasComponent(state)


def social_identity_component(
    model: language_model.LanguageModel,
    group_membership: list[str],
    identification_strength: str = "moderate",
) -> entity_component.ComponentT:
    """
    Create a component representing social identity and group memberships.

    Based on Social Identity Theory (Tajfel & Turner, 1979), people derive
    self-esteem from group memberships and tend to favor in-group members.

    Args:
        model: The language model to use
        group_membership: List of groups this agent identifies with
            Example: ["Democrat", "Parent", "Engineer"]
        identification_strength: How strongly they identify with these groups

    Returns:
        A component representing social identity and group affiliations
    """
    groups_str = ", ".join(group_membership)

    state = (
        f"This person identifies as: {groups_str}. "
        f"They feel {identification_strength} attachment to these groups, "
        f"which affects how they perceive others and interpret events."
    )

    class SocialIdentityComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "social_identity"

    return SocialIdentityComponent(state)


def emotion_component(
    model: language_model.LanguageModel,
    current_emotion: str,
    emotion_intensity: str = "moderate",
) -> entity_component.ComponentT:
    """
    Create a component representing the agent's current emotional state.

    Based on Constructivist theories of emotion (Barrett, 2006), emotions
    are constructed from basic physiological states categorized using
    conceptual knowledge.

    Args:
        model: The language model to use
        current_emotion: The primary emotion (e.g., "joy", "fear", "anger", "sadness")
        emotion_intensity: How intensely the emotion is felt

    Returns:
        A component representing the agent's emotional state
    """
    state = (
        f"Currently feeling {current_emotion} ({emotion_intensity} intensity). "
        f"This affects their perception of events and decision-making."
    )

    class EmotionComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "emotion"

    return EmotionComponent(state)


def theory_of_planned_behavior_component(
    model: language_model.LanguageModel,
    behavior: str,
    attitude: str,
    subjective_norm: str,
    perceived_control: str,
) -> entity_component.ComponentT:
    """
    Create a component implementing Ajzen's Theory of Planned Behavior (1991).

    This model posits that behavioral intention is determined by:
    1. Attitude toward the behavior
    2. Subjective norms (social pressure)
    3. Perceived behavioral control

    Args:
        model: The language model to use
        behavior: The behavior being considered
        attitude: Personal evaluation of the behavior (positive/negative)
        subjective_norm: Perception of social expectations
        perceived_control: Perception of how easy/difficult the behavior is

    Returns:
        A component that evaluates behaviors using TPB framework
    """
    state = (
        f"When considering '{behavior}':\n"
        f"- Attitude: {attitude}\n"
        f"- Social norms suggest: {subjective_norm}\n"
        f"- Perceived control: {perceived_control}\n"
        f"Intention is determined by balancing these three factors."
    )

    class TPBComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "theory_of_planned_behavior"

    return TPBComponent(state)


def values_component(
    model: language_model.LanguageModel,
    core_values: list[str],
    value_conflict: str | None = None,
) -> entity_component.ComponentT:
    """
    Create a component representing the agent's core values and moral framework.

    Based on Schwartz Theory of Basic Human Values (1992), values guide
    the selection and evaluation of actions and policies.

    Args:
        model: The language model to use
        core_values: List of values the agent prioritizes
            Example: ["honesty", "achievement", "benevolence"]
        value_conflict: Optional conflict between values that creates tension

    Returns:
        A component representing the agent's value system
    """
    values_str = ", ".join(core_values)

    if value_conflict:
        state = (
            f"Core values: {values_str}. "
            f"Currently experiencing tension: {value_conflict}. "
            f"This conflict may cause hesitation or internal struggle in decisions."
        )
    else:
        state = (
            f"Core values: {values_str}. "
            f"Decisions are evaluated based on alignment with these values."
        )

    class ValuesComponent(entity_component.ConstantComponent):
        def __init__(self, state: str = state):
            super().__init__(state)
            self._name = "values"

    return ValuesComponent(state)


# Component template registry
COMPONENT_TEMPLATES = {
    "personality_traits": {
        "name": "Personality Traits (Big Five)",
        "description": "Agent's personality based on Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism",
        "category": "Psychological",
        "parameters": {
            "traits": {
                "type": "dict",
                "description": "Personality traits with values 1-5",
                "default": {"openness": 3, "conscientiousness": 3, "extraversion": 3, "agreeableness": 3, "neuroticism": 3},
                "schema": {
                    "type": "object",
                    "properties": {
                        "openness": {"type": "number", "minimum": 1, "maximum": 5},
                        "conscientiousness": {"type": "number", "minimum": 1, "maximum": 5},
                        "extraversion": {"type": "number", "minimum": 1, "maximum": 5},
                        "agreeableness": {"type": "number", "minimum": 1, "maximum": 5},
                        "neuroticism": {"type": "number", "minimum": 1, "maximum": 5},
                    }
                }
            }
        },
        "function": personality_traits_component
    },
    "cognitive_bias": {
        "name": "Cognitive Bias",
        "description": "A cognitive bias that affects decision-making (e.g., confirmation bias, availability heuristic)",
        "category": "Psychological",
        "parameters": {
            "bias_type": {
                "type": "string",
                "description": "Type of cognitive bias",
                "enum": ["confirmation_bias", "availability_heuristic", "anchoring_bias", "sunk_cost_fallacy", "overconfidence_bias"],
                "default": "confirmation_bias"
            },
            "bias_strength": {
                "type": "string",
                "description": "How strongly the bias affects reasoning",
                "enum": ["weak", "moderate", "strong"],
                "default": "moderate"
            }
        },
        "function": cognitive_bias_component
    },
    "social_identity": {
        "name": "Social Identity",
        "description": "Group memberships and social affiliations that affect perception and behavior",
        "category": "Social",
        "parameters": {
            "group_membership": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of groups the agent identifies with",
                "default": []
            },
            "identification_strength": {
                "type": "string",
                "description": "How strongly they identify with these groups",
                "enum": ["weak", "moderate", "strong"],
                "default": "moderate"
            }
        },
        "function": social_identity_component
    },
    "emotion": {
        "name": "Current Emotion",
        "description": "The agent's current emotional state which affects decision-making",
        "category": "Psychological",
        "parameters": {
            "current_emotion": {
                "type": "string",
                "description": "Primary emotion",
                "enum": ["joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation", "neutral"],
                "default": "neutral"
            },
            "emotion_intensity": {
                "type": "string",
                "description": "Emotional intensity",
                "enum": ["weak", "moderate", "strong"],
                "default": "moderate"
            }
        },
        "function": emotion_component
    },
    "theory_of_planned_behavior": {
        "name": "Theory of Planned Behavior",
        "description": "Evaluates behaviors using attitude, norms, and perceived control",
        "category": "Social",
        "parameters": {
            "behavior": {
                "type": "string",
                "description": "The behavior being considered",
                "default": "taking action"
            },
            "attitude": {
                "type": "string",
                "description": "Personal evaluation of the behavior",
                "default": "neutral"
            },
            "subjective_norm": {
                "type": "string",
                "description": "Perception of social expectations",
                "default": "neutral"
            },
            "perceived_control": {
                "type": "string",
                "description": "Perception of how easy/difficult the behavior is",
                "default": "moderate control"
            }
        },
        "function": theory_of_planned_behavior_component
    },
    "values": {
        "name": "Core Values",
        "description": "Agent's moral framework and prioritized values",
        "category": "Psychological",
        "parameters": {
            "core_values": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Values the agent prioritizes",
                "default": ["honesty", "fairness"]
            },
            "value_conflict": {
                "type": "string",
                "description": "Optional conflict between values",
                "default": None
            }
        },
        "function": values_component
    },
}


def get_available_templates() -> dict:
    """Get all available component templates."""
    return COMPONENT_TEMPLATES


def create_component_from_template(
    template_id: str,
    model: language_model.LanguageModel,
    parameters: dict,
) -> entity_component.ComponentT:
    """
    Create a component instance from a template.

    Args:
        template_id: ID of the component template
        model: The language model to use
        parameters: Parameters for the component

    Returns:
        A component instance

    Raises:
        ValueError: If template_id is not found
    """
    if template_id not in COMPONENT_TEMPLATES:
        raise ValueError(f"Unknown component template: {template_id}")

    template = COMPONENT_TEMPLATES[template_id]
    component_func = template["function"]

    return component_func(model, **parameters)
