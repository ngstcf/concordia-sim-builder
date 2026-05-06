"""
Service for building Concordia simulations from configuration.
"""
import datetime
import sys
import os
from pathlib import Path

# Import debug print utility
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.debug_print import debug_print

# Add backend directory to path for custom prefab imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from concordia.utils import helper_functions
from concordia.prefabs import entity as entity_prefabs
from concordia.prefabs import game_master as game_master_prefabs
from concordia.prefabs.simulation import generic as simulation
from concordia.typing import prefab as prefab_lib
from concordia.associative_memory import basic_associative_memory
from concordia.language_model import language_model

from backend.models.schemas import (
    SimulationConfig,
    AgentConfig,
    GameMasterConfig,
    EngineType,
    ActingOrder
)

# Import custom context-aware scripted prefab
from backend.prefabs import context_aware_scripted


def _safe_get_package_classes(module) -> dict:
    """Like helper_functions.get_package_classes but skips classes that fail to instantiate."""
    import inspect, types
    package_name = module.__package__
    prefabs = {}
    submodule_names = [v for v in dir(module) if not v.startswith('__')]
    for submodule_name in submodule_names:
        submodule = getattr(module, submodule_name)
        for var_name in dir(submodule):
            var = getattr(submodule, var_name)
            if inspect.isclass(var) and var.__module__.startswith(package_name):
                key = f'{submodule_name}__{var_name}'
                try:
                    prefabs[key] = var()
                except TypeError:
                    pass
    return prefabs


def load_available_prefabs() -> dict:
    """Load all available prefabs from Concordia (core + contrib) and custom prefabs."""
    from concordia.contrib.prefabs import entity as contrib_entity_prefabs
    from concordia.contrib.prefabs import game_master as contrib_gm_prefabs

    prefabs = {
        **helper_functions.get_package_classes(entity_prefabs),
        **helper_functions.get_package_classes(game_master_prefabs),
        **_safe_get_package_classes(contrib_entity_prefabs),
        **_safe_get_package_classes(contrib_gm_prefabs),
    }

    # Add custom context-aware scripted prefab
    prefabs['context_aware_scripted__Entity'] = context_aware_scripted.Entity()

    # Ensure GameMasterSimultaneous is available even if upstream __init__.py
    # doesn't export simultaneous_resolution_gm (it's not exported by default).
    if 'simultaneous_resolution_gm__GameMasterSimultaneous' not in prefabs:
        try:
            from concordia.contrib.prefabs.game_master import simultaneous_resolution_gm
            prefabs['simultaneous_resolution_gm__GameMasterSimultaneous'] = (
                simultaneous_resolution_gm.GameMasterSimultaneous()
            )
        except (ImportError, TypeError):
            pass

    return prefabs


def create_memory_bank(embedder, memories: list[str]) -> basic_associative_memory.AssociativeMemoryBank:
    """Create and populate a memory bank."""
    memory = basic_associative_memory.AssociativeMemoryBank(
        sentence_embedder=embedder
    )
    for mem in memories:
        memory.add(mem)
    return memory


def build_simulation(
    config: SimulationConfig,
    model: language_model.LanguageModel,
    embedder,
    gm_model: language_model.LanguageModel | None = None,
) -> simulation.Simulation:
    """
    Build a Concordia simulation from configuration.

    Args:
        config: SimulationConfig object
        model: Language model instance
        embedder: Sentence embedder instance
        gm_model: Optional separate model for game master decisions

    Returns:
        Built simulation object ready to run
    """
    # Load available prefabs
    prefabs = load_available_prefabs()

    # Create instance configs for each agent
    instances = []

    # Optional: Add formative memories initializer if player_specific_context is provided
    if config.player_specific_context:
        init_params = {
            'name': 'initial setup rules',
            'next_game_master_name': config.game_master.name,
            'shared_memories': config.shared_memories,
            'player_specific_context': {
                agent.name: config.player_specific_context.get(agent.name, "")
                for agent in config.agents
            },
        }
        if config.player_specific_memories:
            init_params['player_specific_memories'] = {
                agent.name: config.player_specific_memories.get(agent.name, [])
                for agent in config.agents
            }
        initializer_config = prefab_lib.InstanceConfig(
            prefab='formative_memories_initializer__GameMaster',
            role=prefab_lib.Role.INITIALIZER,
            params=init_params,
        )
        instances.append(initializer_config)

    # Create entity instances
    for agent_config in config.agents:
        entity_params = {
            'name': agent_config.name,
            'randomize_choices': agent_config.randomize_choices,
        }

        # Add optional goal
        if agent_config.goal:
            entity_params['goal'] = agent_config.goal

        # Add custom memory if provided
        agent_memories = list(agent_config.memories) if agent_config.memories else []

        # Inject per-agent available actions into memories
        if hasattr(agent_config, 'available_actions') and agent_config.available_actions:
            actions_str = ', '.join(agent_config.available_actions)
            agent_memories.append(
                f"When deciding what to do, {agent_config.name} can choose from: {actions_str}."
            )
            debug_print(f"[DEBUG] Injected {len(agent_config.available_actions)} per-agent actions for {agent_config.name}")

        if agent_memories:
            entity_params['memory'] = create_memory_bank(embedder, agent_memories)

        # Add additional components if specified
        if agent_config.components:
            components_copy = dict(agent_config.components)

            # Handle reasoning_steps: instantiate for minimal__Entity
            reasoning_steps = components_copy.pop('reasoning_steps', None)
            if reasoning_steps and agent_config.prefab == 'minimal__Entity':
                from backend.prefabs.reasoning_steps import create_reasoning_step_component
                extra = components_copy.get('extra_components', {})
                for i, step_config in enumerate(reasoning_steps):
                    comp = create_reasoning_step_component(
                        model=model,
                        agent_name=agent_config.name,
                        config=step_config,
                        index=i,
                    )
                    extra[f'reasoning_step_{i}'] = comp
                components_copy['extra_components'] = extra

            # Handle emotional_stance: instantiate for minimal__Entity
            emotional_stance = components_copy.pop('emotional_stance', None)
            if emotional_stance and agent_config.prefab == 'minimal__Entity':
                from concordia.contrib.components.agent import emotional_stance as es_module
                extra = components_copy.get('extra_components', {})
                extra['emotional_stance'] = es_module.EmotionalStance(
                    model=model,
                    name=agent_config.name,
                    emotion_options=emotional_stance.get('emotion_options', ['happy', 'sad', 'neutral']),
                    num_observations_to_select=emotional_stance.get('num_observations_to_select', 5),
                )
                components_copy['extra_components'] = extra

            entity_params.update(components_copy)

        # Wire nested simulation component if configured
        if agent_config.nested_simulation:
            from backend.prefabs.nested_simulation import NestedSimulationComponent
            from backend.models.schemas import SimulationConfig as SC, AgentConfig as AC, GameMasterConfig as GMC

            nested_agents = [
                AC(id=f'nested-{i}', name=a.name if hasattr(a, 'name') else a.get('name', f'Agent{i}'),
                   prefab=a.prefab if hasattr(a, 'prefab') else a.get('prefab', 'basic__Entity'),
                   goal=a.goal if hasattr(a, 'goal') else a.get('goal'),
                   memories=a.memories if hasattr(a, 'memories') else a.get('memories', []))
                for i, a in enumerate(agent_config.nested_simulation.agents)
            ] if agent_config.nested_simulation.agents else []

            nested_sc = SC(
                premise=agent_config.nested_simulation.premise,
                max_steps=min(agent_config.nested_simulation.max_steps or 5, 10),
                agents=nested_agents if nested_agents else [AC(id='n-1', name='Observer', prefab='basic__Entity')],
                game_master=GMC(prefab='generic__GameMaster', name='nested rules'),
                shared_memories=agent_config.nested_simulation.shared_memories or [],
            )

            nested_component = NestedSimulationComponent(
                model=model,
                parent_context=config.premise,
                nested_config=nested_sc,
                max_steps=min(agent_config.nested_simulation.max_steps or 5, 10),
                extraction_prompt=agent_config.nested_simulation.extraction_prompt or 'What were the key observations from this simulation?',
                embedder=embedder,
            )
            extra = entity_params.get('extra_components', {})
            extra['nested_simulation'] = nested_component
            entity_params['extra_components'] = extra
            debug_print(f"[DEBUG] Added nested simulation component to agent: {agent_config.name}")

        instance_config = prefab_lib.InstanceConfig(
            prefab=agent_config.prefab,
            role=prefab_lib.Role.ENTITY,
            params=entity_params
        )
        instances.append(instance_config)

    # Create game master instance
    gm_params = {
        'name': config.game_master.name,
        'acting_order': config.game_master.acting_order.value,
        'can_terminate_simulation': config.game_master.allow_early_termination,
    }

    # Note: Don't use gm_params.update() here because we need to convert
    # special parameter types (scenes, questionnaires) first

    # Add player_names if provided (for interviewer GM) - simple list, no conversion needed
    if 'player_names' in config.game_master.parameters:
        gm_params['player_names'] = config.game_master.parameters['player_names']
        debug_print(f"[DEBUG] player_names: {config.game_master.parameters['player_names']}")

    # Add GameMasterSimultaneous params if provided
    for sim_gm_key in ('start_time', 'time_period_minutes', 'locations',
                        'game_rules', 'use_gm_working_memory',
                        'extra_event_resolution_steps'):
        if sim_gm_key in config.game_master.parameters:
            gm_params[sim_gm_key] = config.game_master.parameters[sim_gm_key]
            debug_print(f"[DEBUG] GM param {sim_gm_key}: {config.game_master.parameters[sim_gm_key]}")

    # Add scenes if provided (for game-theoretic GM)
    # Convert dict scenes to SceneSpec objects for Concordia
    if 'scenes' in config.game_master.parameters:
        from concordia.typing import scene as scene_lib
        from concordia.typing import entity as entity_lib

        scenes_data = config.game_master.parameters['scenes']
        debug_print(f"[DEBUG] Scenes found: {type(scenes_data)}, length={len(scenes_data) if hasattr(scenes_data, '__len__') else 'N/A'}")

        # Convert dict scenes to SceneSpec objects
        scene_objects = []
        for scene_dict in scenes_data:
            if isinstance(scene_dict, dict):
                # Convert dict to SceneSpec object
                debug_print(f"[DEBUG] Converting scene dict to SceneSpec: {scene_dict.get('scene_type')}")
                scene_type = scene_dict['scene_type']
                if isinstance(scene_type, dict):
                    # Convert scene_type dict to SceneTypeSpec
                    # Handle action_spec if provided in JSON
                    action_spec = None
                    if 'action_spec' in scene_type and scene_type['action_spec']:
                        action_spec_dict = scene_type['action_spec']
                        # Convert action_spec dict to ActionSpec object
                        if 'options' in action_spec_dict:
                            # Choice action spec
                            action_spec = entity_lib.ActionSpec(
                                call_to_action=action_spec_dict.get('call_to_action', 'What would {name} do?'),
                                output_type=entity_lib.OutputType.CHOICE,
                                options=tuple(action_spec_dict['options'])
                            )
                        else:
                            # Free action spec
                            action_spec = entity_lib.ActionSpec(
                                call_to_action=action_spec_dict.get('call_to_action', 'What would {name} do?'),
                                output_type=entity_lib.OutputType.FREE
                            )

                    scene_type_obj = scene_lib.SceneTypeSpec(
                        name=scene_type['name'],
                        game_master_name=scene_type.get('game_master_name'),
                        action_spec=action_spec
                    )
                    debug_print(f"[DEBUG] SceneTypeSpec created with action_spec: {action_spec}")
                else:
                    scene_type_obj = scene_type

                scene_obj = scene_lib.SceneSpec(
                    scene_type=scene_type_obj,
                    participants=scene_dict['participants'],
                    num_rounds=scene_dict['num_rounds'],
                    start_time=scene_dict.get('start_time'),
                    premise=scene_dict.get('premise')
                )
                scene_objects.append(scene_obj)
                debug_print(f"[DEBUG] Converted scene: {scene_obj}")
            else:
                # Already a SceneSpec object
                scene_objects.append(scene_dict)

        gm_params['scenes'] = scene_objects
        debug_print(f"[DEBUG] Final scenes list: {len(scene_objects)} SceneSpec objects")

    # Add questionnaires if provided (for interviewer GM)
    if 'questionnaires' in config.game_master.parameters:
        from concordia.contrib.data.questionnaires import base_questionnaire
        from typing import Dict, Any
        import pandas as pd

        questionnaires_data = config.game_master.parameters['questionnaires']
        debug_print(f"[DEBUG] Questionnaires found: {len(questionnaires_data)}")

        # Create a concrete Likert questionnaire class
        class LikertQuestionnaire(base_questionnaire.QuestionnaireBase):
            """Concrete implementation of a Likert scale questionnaire."""

            def aggregate_results(
                self, player_answers: Dict[str, Dict[str, Any]]
            ) -> Dict[str, Any]:
                """Aggregates answers by computing mean per dimension."""
                return self._default_aggregate_results(player_answers)

            def plot_results(
                self,
                results_df: pd.DataFrame,
                label_column: str | None = None,
                kwargs: dict[str, Any] | None = None,
            ) -> None:
                """Plotting not implemented for this use case."""
                pass

        # Convert dict questionnaires to QuestionnaireBase objects
        questionnaire_objects = []
        for qn_dict in questionnaires_data:
            if isinstance(qn_dict, dict):
                debug_print(f"[DEBUG] Converting questionnaire dict: {qn_dict.get('name')}")
                # Convert questions dict to Question objects
                questions = []
                for question_dict in qn_dict.get('questions', []):
                    from concordia.contrib.data.questionnaires.base_questionnaire import Question
                    question = base_questionnaire.Question(
                        statement=question_dict['statement'],
                        dimension=question_dict['dimension'],
                        preprompt=question_dict.get('preprompt', ''),
                        choices=question_dict.get('choices'),
                        ascending_scale=question_dict.get('ascending_scale', True)
                    )
                    questions.append(question)

                questionnaire = LikertQuestionnaire(
                    name=qn_dict['name'],
                    description=qn_dict['description'],
                    questionnaire_type=qn_dict['questionnaire_type'],
                    observation_preprompt=qn_dict['observation_preprompt'],
                    questions=questions,
                    preprompt=qn_dict.get('preprompt', ''),
                    dimensions=qn_dict.get('dimensions')
                )
                questionnaire_objects.append(questionnaire)
                debug_print(f"[DEBUG] Converted questionnaire: {questionnaire.name}")
            else:
                # Already a QuestionnaireBase object
                questionnaire_objects.append(qn_dict)

        gm_params['questionnaires'] = questionnaire_objects
        debug_print(f"[DEBUG] Final questionnaires list: {len(questionnaire_objects)} objects")

    # Add grounded_variables component if provided
    if config.game_master.grounded_variables:
        from backend.prefabs.grounded_variables import create_grounded_variables_component

        debug_print(f"[DEBUG] Grounded variables found: {len(config.game_master.grounded_variables)}")

        # Convert VariableConfig objects to dicts for the component factory
        variable_configs = [
            var.model_dump() if hasattr(var, 'model_dump') else var
            for var in config.game_master.grounded_variables
        ]

        # Create the grounded variables component
        grounded_vars_component = create_grounded_variables_component(
            model=model,
            variable_configs=variable_configs
        )

        # Add component to game master extra_components
        if 'extra_components' not in gm_params:
            gm_params['extra_components'] = {}

        gm_params['extra_components']['grounded_variables_component'] = grounded_vars_component
        debug_print(f"[DEBUG] Grounded variables component added to game master extra_components")
        debug_print(f"[DEBUG] Component type: {type(grounded_vars_component).__name__}")
        debug_print(f"[DEBUG] Component name: {grounded_vars_component.name if hasattr(grounded_vars_component, 'name') else 'N/A'}")
        debug_print(f"[DEBUG] extra_components keys: {list(gm_params['extra_components'].keys())}")

    # Add contrib GM components if provided
    if config.game_master.contrib_components:
        from backend.prefabs.contrib_gm_components import create_contrib_gm_component

        agent_names = [a.name for a in config.agents]
        if 'extra_components' not in gm_params:
            gm_params['extra_components'] = {}

        for cc in config.game_master.contrib_components:
            component = create_contrib_gm_component(
                component_id=cc.component_id,
                model=model,
                config=cc.params,
                agent_names=agent_names,
            )
            gm_params['extra_components'][f'contrib_{cc.component_id}'] = component
            debug_print(f"[DEBUG] Added contrib GM component: {cc.component_id}")

    gm_instance = prefab_lib.InstanceConfig(
        prefab=config.game_master.prefab,
        role=prefab_lib.Role.GAME_MASTER,
        params=gm_params
    )
    instances.append(gm_instance)

    # Append grounded variable tracking instructions to the premise so the
    # GM's event resolution chain (which reads instructions) is aware of them.
    premise_text = config.premise
    if config.game_master.grounded_variables:
        var_lines = []
        for var in config.game_master.grounded_variables:
            v = var.model_dump() if hasattr(var, 'model_dump') else var
            name = v['name']
            vtype = v.get('variable_type', 'numerical')
            desc = v.get('description', '')
            line = f"  - {name} ({vtype}): {desc}"
            if v.get('default_value') is not None:
                line += f" [starts at {v['default_value']}]"
            if v.get('update_rule'):
                line += f" — {v['update_rule']}"
            var_lines.append(line)

        premise_text += (
            "\n\nGROUNDED VARIABLES — you MUST track these quantitative"
            " variables as the simulation unfolds. After every event you"
            " narrate, append exactly one line in this format:\n"
            "  [VARIABLES: name1=value1, name2=value2]\n"
            "Include only variables that changed. If none changed, write"
            " [VARIABLES: NONE].\n\n"
            "Variables:\n" + "\n".join(var_lines)
        )
        debug_print(f"[DEBUG] Injected grounded variable tracking instructions into premise")
    debug_print(f"[DEBUG] Checking for critical decision points...")
    debug_print(f"[DEBUG] hasattr(config.game_master, 'critical_decision_points'): {hasattr(config.game_master, 'critical_decision_points')}")
    if hasattr(config.game_master, 'critical_decision_points'):
        debug_print(f"[DEBUG] config.game_master.critical_decision_points: {config.game_master.critical_decision_points}")
    if (hasattr(config.game_master, 'critical_decision_points') and
        config.game_master.critical_decision_points):
        decision_points = config.game_master.critical_decision_points
        debug_print(f"[DEBUG] Found {len(decision_points)} critical decision points")
        # Sort by step and append to premise
        decision_points_sorted = sorted(decision_points, key=lambda x: x['step'])
        decision_text = "\n\nCRITICAL DECISION POINTS:\n"
        for dp in decision_points_sorted:
            decision_text += f"- Step {dp['step']}: {dp['event']}\n"
        premise_text = premise_text + decision_text
        debug_print(f"[DEBUG] Appended critical decision points to premise")
        debug_print(f"[DEBUG] New premise length: {len(premise_text)}")
    else:
        debug_print(f"[DEBUG] No critical decision points found")

    # Inject available actions into premise if defined
    if hasattr(config, 'available_actions') and config.available_actions:
        action_lines = []
        for action in config.available_actions:
            a = action.model_dump() if hasattr(action, 'model_dump') else action
            line = f"  - {a['name']}"
            if a.get('description'):
                line += f": {a['description']}"
            if a.get('condition'):
                line += f" (available when: {a['condition']})"
            action_lines.append(line)
        premise_text += (
            "\n\nAVAILABLE ACTIONS — agents should ONLY choose from"
            " these actions when deciding what to do:\n"
            + "\n".join(action_lines)
            + "\nWhen asking agents what they do, present these as"
            " their available choices."
        )
        debug_print(f"[DEBUG] Injected {len(action_lines)} available actions into premise")

    # Inject Measurements into all instances for data capture
    if config.engine_type == EngineType.ASYNCHRONOUS:
        from concordia.utils import async_measurements
        measurements = async_measurements.ReactiveMeasurements()
        debug_print(f"[DEBUG] Injected ReactiveMeasurements into instances for async engine")
    else:
        from concordia.utils.measurements import Measurements
        measurements = Measurements()
        debug_print(f"[DEBUG] Injected Measurements into instances for {config.engine_type.value} engine")

    for inst in instances:
        if 'measurements' not in inst.params:
            inst.params['measurements'] = measurements

    # Create simulation configuration
    sim_config = prefab_lib.Config(
        default_premise=premise_text,
        default_max_steps=config.max_steps,
        prefabs=prefabs,
        instances=instances
    )

    # Select engine based on config or GM prefab
    if config.game_master.prefab == 'interviewer__GameMaster':
        from concordia.environment.engines import parallel
        engine = parallel.ParallelQuestionnaireEngine()
        debug_print(f"[DEBUG] Using ParallelQuestionnaireEngine for interviewer prefab")
    elif config.engine_type == EngineType.SIMULTANEOUS:
        from concordia.environment.engines import simultaneous
        engine = simultaneous.Simultaneous()
        debug_print(f"[DEBUG] Using Simultaneous engine")
    elif config.engine_type == EngineType.ASYNCHRONOUS:
        from concordia.environment.engines import asynchronous
        engine = asynchronous.Asynchronous()
        debug_print(f"[DEBUG] Using Asynchronous engine")
    else:
        from concordia.environment.engines import sequential
        engine = sequential.Sequential()
        debug_print(f"[DEBUG] Using Sequential engine")

    # Build and return simulation using the Simulation class
    sim = simulation.Simulation(
        config=sim_config,
        model=model,
        embedder=embedder,
        engine=engine,
        override_game_master_model=gm_model,
    )

    sim._measurements = measurements

    return sim


def get_available_prefabs_info() -> list[dict]:
    """Get information about available prefabs."""
    prefabs = load_available_prefabs()

    entity_prefabs_info = []
    gm_prefabs_info = []
    initializer_prefabs_info = []

    prefab_descriptions = {
        # Entity prefabs — core
        'basic__Entity': 'Standard agent with "three key questions" decision framework (situation, self-perception, action)',
        'basic_with_plan__Entity': 'Agent with strategic planning and time horizons for complex coordination',
        'basic_scripted__Entity': 'Follows predefined scripts exactly; goes silent when script is exhausted',
        'context_aware_scripted__Entity': 'Adapts script to conversation context; auto-closes when script ends',
        'minimal__Entity': 'Bare-minimum agent for lightweight simulations',
        'fake_assistant_with_configurable_system_prompt__Entity': 'AI assistant persona with custom system prompt',
        'conversational__Entity': 'Dialogue-focused agent optimized for conversation simulations',
        'rational__Entity': 'Expected utility maximizer for game-theoretic scenarios',
        'puppet__Entity': 'Externally controlled agent for wizard-of-oz or human-in-the-loop experiments',

        # Entity prefabs — contrib
        'basic_with_image__Entity': 'Multimodal agent that generates images alongside text responses',
        'conversations_with_ai_companions__AICompanionEntity': 'AI companion for tutoring and conversational scenarios',
        'conversations_with_ai_companions__HumanUserEntity': 'Human user entity for AI companion conversations',

        # Game master prefabs — core
        'generic__GameMaster': 'General-purpose narrative GM for most simulation types',
        'dialogic__GameMaster': 'Conversation-focused GM with auto-termination for dialogue-heavy scenarios',
        'dialogic_and_dramaturgic__GameMaster': 'Enhanced dialogue GM with dramatic scene structure',
        'game_theoretic_and_dramaturgic__GameMaster': 'Matrix games with payoffs, scores, and strategic decisions',
        'interviewer__GameMaster': 'Structured questionnaire administration for surveys and interviews',
        'open_ended_interviewer__GameMaster': 'Unstructured interview format with free-form questioning',
        'marketplace__GameMaster': 'Economic trading simulation with buy/sell/hold dynamics',
        'psychology_experiment__GameMaster': 'Experimental protocol management for research scenarios',
        'scripted__GameMaster': 'Follows predetermined narrative sequences',
        'situated__GameMaster': 'Location-aware GM for spatially grounded scenarios',
        'situated_in_time_and_place__GameMaster': 'Temporal and spatial context with time progression',
        'physically_situated_and_dramaturgic__GameMaster': 'Physical environment with dramatic scene structure',
        'async_social_media__GameMaster': 'Social media simulation with forums, posts, and asynchronous interaction',

        # Game master prefabs — contrib
        'simultaneous_resolution_gm__GameMasterSimultaneous': 'Simultaneous event resolution GM with location tracking, NPC events, working memory, and time-based pacing',
        'space_ship__GameMaster': 'Spaceship simulation with location tracking and system health/failure states',

        # Initializer
        'formative_memories_initializer__GameMaster': 'Creates character backgrounds from player-specific context before main simulation',
    }

    for prefab_name, prefab_class in prefabs.items():
        info = {
            'name': prefab_name,
            'description': prefab_descriptions.get(prefab_name, 'No description available'),
            'required_params': ['name'],
            'optional_params': [],
        }

        if '__Entity' in prefab_name:
            info['type'] = 'entity'
            info['required_params'] = ['name']
            info['optional_params'] = ['goal', 'memory', 'randomize_choices']
            entity_prefabs_info.append(info)
        elif '__GameMaster' in prefab_name:
            if 'initializer' in prefab_name.lower():
                info['type'] = 'initializer'
                info['required_params'] = ['name', 'next_game_master_name']
                info['optional_params'] = ['shared_memories', 'player_specific_context']
                initializer_prefabs_info.append(info)
            else:
                info['type'] = 'game_master'
                info['required_params'] = ['name']
                info['optional_params'] = ['acting_order']
                gm_prefabs_info.append(info)

    return {
        'entities': entity_prefabs_info,
        'game_masters': gm_prefabs_info,
        'initializers': initializer_prefabs_info
    }
