"""
Simulation template registry.

Each template lives in its own module as a TEMPLATE dict.
TEMPLATES maps URL slug → template data.
"""
from .peace_negotiation import TEMPLATE as _peace_negotiation
from .coffee_shop import TEMPLATE as _coffee_shop
from .planning_agent import TEMPLATE as _planning_agent
from .scripted_entity import TEMPLATE as _scripted_entity
from .dialogic_conversation import TEMPLATE as _dialogic_conversation
from .strategic_game import TEMPLATE as _strategic_game
from .interviewer import TEMPLATE as _interviewer
from .formative_memories import TEMPLATE as _formative_memories
from .marketplace import TEMPLATE as _marketplace
from .state_formation import TEMPLATE as _state_formation
from .labor_action import TEMPLATE as _labor_action
from .fishery_management import TEMPLATE as _fishery_management
from .disaster_response import TEMPLATE as _disaster_response
from .inequality_mobility import TEMPLATE as _inequality_mobility
from .context_aware_moderator import TEMPLATE as _context_aware_moderator
from .vaccine_hesitancy import TEMPLATE as _vaccine_hesitancy
from .nested_simulation_demo import TEMPLATE as _nested_simulation_demo
from .phishing_attack_simulation import TEMPLATE as _phishing_attack_simulation
from .grounded_variables_demo import TEMPLATE as _grounded_variables_demo
from .urban_gentrification import TEMPLATE as _urban_gentrification
from .rational_negotiators import TEMPLATE as _rational_negotiators
from .social_media_discourse import TEMPLATE as _social_media_discourse
from .puppet_wizard_of_oz import TEMPLATE as _puppet_wizard_of_oz
from .conversational_debate import TEMPLATE as _conversational_debate
from .spaceship_crisis import TEMPLATE as _spaceship_crisis
from .simultaneous_auction import TEMPLATE as _simultaneous_auction
from .step_controller_demo import TEMPLATE as _step_controller_demo
from .contrib_gm_components_demo import TEMPLATE as _contrib_gm_components_demo
from .formative_memories_demo import TEMPLATE as _formative_memories_demo
from .measurements_demo import TEMPLATE as _measurements_demo
from .nested_sim_strategy import TEMPLATE as _nested_sim_strategy
from .devils_advocate_policy import TEMPLATE as _devils_advocate_policy
from .music_career_crossroads import TEMPLATE as _music_career_crossroads
from .upstream_social_media import TEMPLATE as _upstream_social_media
from .upstream_ai_companion_philosophy import TEMPLATE as _upstream_ai_companion_philosophy
from .upstream_ai_companion_trig_upsell import TEMPLATE as _upstream_ai_companion_trig_upsell
from .upstream_general_store import TEMPLATE as _upstream_general_store
from .upstream_pub_coordination import TEMPLATE as _upstream_pub_coordination
from .mastodon_influence_experiment import TEMPLATE as _mastodon_influence_experiment

TEMPLATES: dict[str, dict] = {
    "peace-negotiation": _peace_negotiation,
    "coffee-shop": _coffee_shop,
    "planning-agent": _planning_agent,
    "scripted-entity": _scripted_entity,
    "dialogic-conversation": _dialogic_conversation,
    "strategic-game": _strategic_game,
    "interviewer": _interviewer,
    "formative-memories": _formative_memories,
    "marketplace": _marketplace,
    "state-formation": _state_formation,
    "labor-action": _labor_action,
    "fishery-management": _fishery_management,
    "disaster-response": _disaster_response,
    "inequality-mobility": _inequality_mobility,
    "context-aware-moderator": _context_aware_moderator,
    "vaccine-hesitancy": _vaccine_hesitancy,
    "nested-simulation-demo": _nested_simulation_demo,
    "phishing-attack-simulation": _phishing_attack_simulation,
    "grounded-variables-demo": _grounded_variables_demo,
    "urban-gentrification": _urban_gentrification,
    "rational-negotiators": _rational_negotiators,
    "social-media-discourse": _social_media_discourse,
    "puppet-wizard-of-oz": _puppet_wizard_of_oz,
    "conversational-debate": _conversational_debate,
    "spaceship-crisis": _spaceship_crisis,
    "simultaneous-auction": _simultaneous_auction,
    "step-controller-demo": _step_controller_demo,
    "contrib-gm-components-demo": _contrib_gm_components_demo,
    "formative-memories-demo": _formative_memories_demo,
    "measurements-demo": _measurements_demo,
    "nested-sim-strategy": _nested_sim_strategy,
    "devils-advocate-policy": _devils_advocate_policy,
    "music-career-crossroads": _music_career_crossroads,
    "upstream-social-media": _upstream_social_media,
    "upstream-ai-companion-philosophy": _upstream_ai_companion_philosophy,
    "upstream-ai-companion-trig-upsell": _upstream_ai_companion_trig_upsell,
    "upstream-general-store": _upstream_general_store,
    "upstream-pub-coordination": _upstream_pub_coordination,
    "mastodon-influence-experiment": _mastodon_influence_experiment,
}
