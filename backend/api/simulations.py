"""
API endpoints for simulation management and execution.
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from backend.models.schemas import (
    SimulationConfig,
    LLMSettings,
    ValidationResult,
    PrefabInfo,
    ExecutionRequest,
    ComponentValidationRequest,
)
from backend.services.simulation_builder import (
    get_available_prefabs_info,
    build_simulation
)
from backend.services.simulation_runner import (
    run_simulation_stream,
    run_simulation_simple
)
from backend.services.llm_factory import get_available_providers
from backend.services.simulation_state import simulation_state

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.get("/prefabs")
async def get_prefabs():
    """Get list of available prefabs."""
    try:
        prefabs_info = get_available_prefabs_info()
        return prefabs_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers():
    """Get list of available LLM providers."""
    return get_available_providers()


@router.get("/components/templates")
async def get_component_templates():
    """Get all available component templates for agent customization."""
    try:
        from backend.prefabs.components import COMPONENT_TEMPLATES
        return {
            "templates": [
                {
                    "id": template_id,
                    "name": template["name"],
                    "description": template["description"],
                    "parameters": template["parameters"],
                    "category": template.get("category", "general")
                }
                for template_id, template in COMPONENT_TEMPLATES.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get component templates: {str(e)}")


@router.post("/components/validate")
async def validate_component_parameters(request: ComponentValidationRequest):
    """
    Validate component parameters against a template's schema.

    Args:
        request: Validation request with template_id and parameters

    Returns:
        Validation result with any errors found
    """
    template_id = request.template_id
    parameters = request.parameters
    try:
        from backend.prefabs.components import COMPONENT_TEMPLATES

        if template_id not in COMPONENT_TEMPLATES:
            return {
                "valid": False,
                "errors": [f"Unknown component template: {template_id}"]
            }

        template = COMPONENT_TEMPLATES[template_id]
        param_schema = template["parameters"]
        errors = []

        # Validate each parameter
        for param_name, param_config in param_schema.items():
            if param_name not in parameters:
                if "default" not in param_config:
                    errors.append(f"Missing required parameter: {param_name}")
                continue

            value = parameters[param_name]

            # Type validation
            expected_type = param_config.get("type")
            if expected_type == "string":
                if not isinstance(value, str):
                    errors.append(f"Parameter '{param_name}' must be a string")
            elif expected_type == "integer":
                if not isinstance(value, int):
                    errors.append(f"Parameter '{param_name}' must be an integer")
            elif expected_type == "float":
                if not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param_name}' must be a number")
            elif expected_type == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"Parameter '{param_name}' must be a boolean")
            elif expected_type == "dict":
                if not isinstance(value, dict):
                    errors.append(f"Parameter '{param_name}' must be a dictionary")
            elif expected_type == "array":
                if not isinstance(value, list):
                    errors.append(f"Parameter '{param_name}' must be an array")

            # Enum validation
            if "enum" in param_config:
                valid_values = param_config["enum"]
                if value not in valid_values:
                    errors.append(
                        f"Parameter '{param_name}' must be one of: {', '.join(valid_values)}"
                    )

            # Range validation
            if "min" in param_config and value < param_config["min"]:
                errors.append(f"Parameter '{param_name}' must be at least {param_config['min']}")
            if "max" in param_config and value > param_config["max"]:
                errors.append(f"Parameter '{param_name}' must be at most {param_config['max']}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/models/{provider}")
async def get_provider_models(
    provider: str,
    api_key: str = None,
    base_url: str = None
):
    """
    Fetch available models from a provider's API.

    For Ollama and OpenAI-compatible APIs, queries the /models endpoint.
    For other providers, returns static list of known models.

    Args:
        provider: LLM provider name (ollama, openai, deepseek, etc.)
        api_key: Optional API key for authentication
        base_url: Optional custom base URL for the provider

    Returns:
        List of available model names
    """
    import os
    import httpx
    from backend.models.schemas import LLMProvider

    provider = provider.lower()

    # Handle Ollama and OpenAI-compatible providers with dynamic model discovery
    if provider == LLMProvider.OLLAMA.value:
        # Determine the base URL to query
        if base_url:
            models_url = f"{base_url.rstrip('/')}/models"
        else:
            # Use environment variable or default to localhost
            ollama_base = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            models_url = f"{ollama_base.rstrip('/')}/models"

        # Determine API key
        headers = {}
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        else:
            # Try to get from environment
            env_key = os.getenv('OLLAMA_API_KEY')
            if env_key:
                headers['Authorization'] = f"Bearer {env_key}"

        try:
            # Disable SSL verification for myai.unu.edu and self-hosted instances
            verify_ssl = 'myai.unu.edu' not in models_url and 'localhost' not in models_url

            async with httpx.AsyncClient(verify=verify_ssl, timeout=10.0) as client:
                response = await client.get(models_url, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    # Handle OpenAI-compatible format (Ollama, OpenWebUI, etc.)
                    if 'data' in data:
                        # Extract model names from the response
                        models = []
                        for model in data['data']:
                            model_id = model.get('id', model.get('name', ''))
                            # Skip aggregate entries
                            if model_id and model_id not in ['ollama', 'arena']:
                                models.append({
                                    'id': model_id,
                                    'name': model.get('name', model_id),
                                    'size': model.get('ollama', {}).get('size'),
                                    'owned_by': model.get('owned_by', 'ollama')
                                })
                        return {'provider': provider, 'models': models}

                    # Handle simple list format
                    elif isinstance(data, list):
                        return {'provider': provider, 'models': [{'id': m, 'name': m} for m in data]}

                return {'provider': provider, 'models': [], 'error': f"API returned status {response.status_code}"}

        except Exception as e:
            return {'provider': provider, 'models': [], 'error': str(e)}

    elif provider == LLMProvider.OPENAI.value:
        # For OpenAI, use their models API
        key = api_key or os.getenv('OPENAI_API_KEY')
        if not key:
            return {'provider': provider, 'models': [], 'error': 'API key required'}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    'https://api.openai.com/v1/models',
                    headers={'Authorization': f'Bearer {key}'}
                )

                if response.status_code == 200:
                    data = response.json()
                    models = [
                        {'id': m['id'], 'name': m['id']}
                        for m in data.get('data', [])
                        if m['id'].startswith(('gpt-', 'o1-'))
                    ]
                    return {'provider': provider, 'models': models}

                return {'provider': provider, 'models': [], 'error': f"API returned status {response.status_code}"}

        except Exception as e:
            return {'provider': provider, 'models': [], 'error': str(e)}

    elif provider == LLMProvider.GEMINI.value:
        # For Gemini, use their models API
        key = api_key or os.getenv('GEMINI_API_KEY')
        if not key:
            return {'provider': provider, 'models': [], 'error': 'API key required'}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Gemini uses query parameter for API key
                response = await client.get(
                    f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'
                )

                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get('models', []):
                        # Extract base model name from the resource name
                        # Format: models/gemini-1.5-flash-001 -> baseModelId: gemini-1.5-flash
                        base_model_id = model.get('baseModelId', '')
                        display_name = model.get('displayName', base_model_id)

                        if base_model_id:  # Only include models with baseModelId
                            models.append({
                                'id': base_model_id,
                                'name': display_name,
                                'description': model.get('description', ''),
                                'input_token_limit': model.get('inputTokenLimit'),
                                'output_token_limit': model.get('outputTokenLimit'),
                                'supports_thinking': model.get('thinking', False)
                            })
                    return {'provider': provider, 'models': models}

                return {'provider': provider, 'models': [], 'error': f"API returned status {response.status_code}"}

        except Exception as e:
            return {'provider': provider, 'models': [], 'error': str(e)}

    elif provider == LLMProvider.ANTHROPIC.value:
        # For Anthropic, use their models API
        key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not key:
            return {'provider': provider, 'models': [], 'error': 'API key required'}

        try:
            headers = {
                'X-Api-Key': key,
                'anthropic-version': '2023-06-01'
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    'https://api.anthropic.com/v1/models',
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get('data', []):
                        model_id = model.get('id', '')
                        # Only include Claude models
                        if model_id.startswith('claude-'):
                            models.append({
                                'id': model_id,
                                'name': model.get('display_name', model_id),
                                'created_at': model.get('created_at')
                            })
                    return {'provider': provider, 'models': models}

                return {'provider': provider, 'models': [], 'error': f"API returned status {response.status_code}"}

        except Exception as e:
            return {'provider': provider, 'models': [], 'error': str(e)}

    else:
        # For other providers, return static known models
        provider_info = next(
            (p for p in get_available_providers() if p['provider'].value == provider),
            None
        )

        if provider_info:
            models = [{'id': m, 'name': m} for m in provider_info.get('models', [])]
            return {'provider': provider, 'models': models}
        else:
            return {'provider': provider, 'models': [], 'error': 'Unknown provider'}


@router.post("/validate")
async def validate_config(config: SimulationConfig):
    """Validate a simulation configuration."""
    errors = []
    warnings = []

    # Basic validation
    if not config.premise or len(config.premise.strip()) == 0:
        errors.append("Premise cannot be empty")

    if len(config.agents) == 0:
        errors.append("At least one agent is required")

    # Check for duplicate agent IDs
    agent_ids = [agent.id for agent in config.agents]
    if len(agent_ids) != len(set(agent_ids)):
        errors.append("Agent IDs must be unique")

    # Check for duplicate agent names
    agent_names = [agent.name for agent in config.agents]
    if len(agent_names) != len(set(agent_names)):
        warnings.append("Agent names should be unique for clarity")

    # Validate game master
    if not config.game_master.name:
        errors.append("Game master must have a name")

    # Check prefab names
    all_prefabs = get_available_prefabs_info()
    valid_entity_prefabs = [p['name'] for p in all_prefabs['entities']]
    valid_gm_prefabs = [p['name'] for p in all_prefabs['game_masters']]

    for agent in config.agents:
        if agent.prefab not in valid_entity_prefabs:
            errors.append(f"Unknown entity prefab: {agent.prefab}")

    if config.game_master.prefab not in valid_gm_prefabs:
        errors.append(f"Unknown game master prefab: {config.game_master.prefab}")

    # Check for game-theoretic scene configuration mismatch
    if config.game_master.prefab == "game_theoretic_and_dramaturgic__GameMaster":
        if config.game_master.parameters and "scenes" in config.game_master.parameters:
            scenes = config.game_master.parameters["scenes"]
            if scenes and len(scenes) > 0:
                total_scene_rounds = sum(scene.get("num_rounds", 0) for scene in scenes)
                if total_scene_rounds != config.max_steps:
                    warnings.append(
                        f"Scene configuration total rounds ({total_scene_rounds}) does not match max_steps ({config.max_steps}). "
                        f"This may cause 'Counter state X is greater than max number of rounds' error. "
                        f"Ensure scene num_rounds sum equals max_steps, or remove scenes parameter to use defaults."
                    )
        else:
            # Using default scenes (3 rounds from Concordia's default)
            default_rounds = 3
            if config.max_steps != default_rounds:
                warnings.append(
                    f"Using default scene configuration ({default_rounds} rounds) but max_steps is set to {config.max_steps}. "
                    f"This will cause 'Counter state {config.max_steps} is greater than max number of rounds {default_rounds}' error. "
                    f"Either set max_steps to {default_rounds} or provide custom scenes in game_master.parameters."
                )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


@router.post("/execute")
async def execute_simulation(request: ExecutionRequest):
    """
    Execute a simulation with SSE streaming.

    Returns a streaming response with simulation events.
    """
    config = request.config
    llm_settings = request.llm_settings

    # Validate first
    validation = await validate_config(config)
    if not validation.valid:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation.errors, "warnings": validation.warnings}
        )

    return StreamingResponse(
        run_simulation_stream(config, llm_settings),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/execute-simple")
async def execute_simulation_simple(request: ExecutionRequest):
    """
    Execute a simulation and return complete results (non-streaming).

    Useful for testing and simple simulations.
    """
    config = request.config
    llm_settings = request.llm_settings

    # Validate first
    validation = await validate_config(config)
    if not validation.valid:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation.errors, "warnings": validation.warnings}
        )

    results = await run_simulation_simple(config, llm_settings)
    return results


@router.get("/export-template")
async def export_template():
    """Export a blank simulation configuration template."""
    template = SimulationConfig(
        premise="Your scenario description here...",
        max_steps=10,
        agents=[
            {
                "id": "agent-1",
                "name": "Agent 1",
                "prefab": "basic__Entity",
                "goal": "Agent's goal here...",
                "memories": [],
                "randomize_choices": True
            }
        ],
        game_master={
            "prefab": "generic__GameMaster",
            "name": "default rules",
            "acting_order": "game_master_choice",
            "parameters": {}
        },
        shared_memories=["Shared world knowledge..."]
    )
    return template.model_dump(mode='json')


@router.post("/import")
async def import_config(config_data: dict):
    """
    Import and validate a simulation configuration from JSON.
    """
    try:
        config = SimulationConfig(**config_data)
        validation = await validate_config(config)
        return {
            "config": config.model_dump(mode='json'),
            "validation": validation.model_dump()
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid configuration: {e}"
        )


@router.get("/templates/peace-negotiation")
async def get_peace_negotiation_template():
    """Get the peace negotiation simulation as a template."""
    return {
        "name": "Russia-Ukraine Peace Negotiation",
        "description": "Simulates peace negotiations between Russia and Ukraine with a UN mediator",
        "config": {
            "premise": """Peace Negotiation Setting:
Date: January 2026
Location: Neutral territory (Istanbul, Turkey)

Background:
The Russia-Ukraine conflict has been ongoing since 2022. Both sides
have experienced significant losses. International pressure for peace
has intensified. Multiple rounds of negotiations have failed, but
renewed diplomatic efforts bring representatives together again.

Key Issues on the Table:
1. Territory and borders (Crimea, Donbas region)
2. Security guarantees for Ukraine
3. NATO membership question
4. War reparations and reconstruction
5. Prisoner exchanges
6. Sanctions relief
7. Demilitarization terms
8. International peacekeeping forces""",
            "max_steps": 20,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "russia",
                    "name": "Agent R",
                    "prefab": "basic__Entity",
                    "goal": "Secure recognition of Crimea, achieve Ukrainian neutrality, get sanctions relief",
                    "memories": [
                        "You are a simulated Russian Foreign Minister.",
                        "Russia's security concerns about NATO expansion are legitimate",
                        "Recognition of Crimea as Russian territory is non-negotiable",
                        "Donbas regions (Donetsk, Luhansk) should have autonomy or join Russia",
                        "Ukraine must commit to neutrality (no NATO membership)",
                        "Sanctions against Russia must be lifted",
                        "Negotiation style: Firm, strategic, willing to make small concessions but protecting core interests"
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "ukraine",
                    "name": "Agent U",
                    "prefab": "basic__Entity",
                    "goal": "Restore territorial integrity, secure path to NATO/EU membership, get reparations",
                    "memories": [
                        "You are a simulated Ukrainian Foreign Minister.",
                        "Ukraine's sovereignty and territorial integrity are paramount",
                        "All occupied territories including Crimea must be returned",
                        "Ukraine has the right to choose its own alliances (including NATO/EU)",
                        "Russia must pay reparations for war damages",
                        "War criminals must be held accountable",
                        "Negotiation style: Resolute on sovereignty, moral high ground, seeking international support"
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "UN Mediator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "The year is 2026",
                "Location: Istanbul, Turkey",
                "Mediator: Agent UN, a simulated high-ranking UN representative"
            ],
            "player_specific_context": {
                "Agent R": "You represent Russia and must protect its core interests while showing willingness to negotiate.",
                "Agent U": "You represent Ukraine and must defend its sovereignty and territorial integrity."
            }
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.5
        }
    }


@router.get("/templates/coffee-shop")
async def get_coffee_shop_template():
    """Get a simple coffee shop demo template for testing."""
    return {
        "name": "Coffee Shop Encounter",
        "description": "A quick demo: Alice meets Bob at a coffee shop",
        "config": {
            "premise": """A sunny Monday morning at "The Daily Grind" coffee shop.
Alice, a regular customer, walks in and notices Bob sitting
at a corner table working on a laptop.""",
            "max_steps": 5,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "alice",
                    "name": "Alice",
                    "prefab": "basic__Entity",
                    "goal": "Find out what Bob is working on",
                    "memories": [
                        "Alice is a software engineer who loves coffee.",
                        "She's curious and friendly.",
                        "She knows Bob casually from previous visits."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "bob",
                    "name": "Bob",
                    "prefab": "basic__Entity",
                    "goal": "Finish work with minimal distractions",
                    "memories": [
                        "Bob is a data scientist with a deadline.",
                        "He's focused but polite.",
                        "He knows Alice from the coffee shop."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Narrator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "The coffee shop is quiet with soft jazz playing.",
                "It's 10 AM on a Monday.",
                "Both Alice and Bob know each other casually."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.5
        }
    }


# ============================================================================
# PREFAB TYPE TEMPLATES - Examples for each major prefab category
# ============================================================================

@router.get("/templates/planning-agent")
async def get_planning_agent_template():
    """
    Template: Planning Agent (basic_with_plan__Entity)
    Use for: Scenarios requiring agents with strategic forethought
    """
    return {
        "name": "Strategic Planning Scenario",
        "description": "Agents with planning capabilities working toward multi-step goals",
        "prefab_type": "basic_with_plan__Entity",
        "config": {
            "premise": """A startup team is planning their product launch strategy.
They need to coordinate marketing, development, and sales efforts
for the next quarter.""",
            "max_steps": 15,
            "agents": [
                {
                    "id": "ceo",
                    "name": "Sarah Chen",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Create a comprehensive 3-month launch plan that aligns all departments",
                    "memories": [
                        "You are Sarah Chen, CEO of a tech startup.",
                        "You excel at seeing the big picture and coordinating teams.",
                        "You believe in thorough planning before execution.",
                        "The product launches in 3 months.",
                        "You need buy-in from all department heads."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "marketing",
                    "name": "Marcus Rodriguez",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Ensure marketing strategy aligns with product capabilities and timeline",
                    "memories": [
                        "You are Marcus, Head of Marketing.",
                        "You need to know product features to create effective campaigns.",
                        "You're concerned about aggressive timelines.",
                        "You want to build anticipation gradually."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "engineering",
                    "name": "Emily Watson",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Commit to realistic development milestones that ensure quality",
                    "memories": [
                        "You are Emily, CTO/Head of Engineering.",
                        "You won't promise features that can't be delivered well.",
                        "You need clear requirements from marketing.",
                        "You're protective of your team's work-life balance."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Strategy Facilitator",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The company has raised Series B funding.",
                "Launch deadline is exactly 90 days from now.",
                "Budget is sufficient but not unlimited.",
                "Competitors are launching similar products soon."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.9
        }
    }


@router.get("/templates/scripted-entity")
async def get_scripted_entity_template():
    """
    Template: Scripted Entity (basic_scripted__Entity)
    Use for: Controlled facilitator, scenario setup, demonstrations

    This example demonstrates a SCRIPTED FACILITATOR guiding MULTIPLE FREE AGENTS
    through a group discussion. The facilitator provides structure (prompts, timing,
    transitions) while the participants respond authentically based on their
    personalities and goals.

    Key insight: The scripted agent isn't the main character - they're the
    "director" that orchestrates an interesting interaction between free agents.
    """
    return {
        "name": "Focus Group Discussion",
        "description": "A scripted moderator guides diverse participants through a product debate - shows how scripted agents orchestrate free agents",
        "prefab_type": "basic_scripted__Entity",
        "config": {
            "premise": """A market research focus group testing a controversial new app:
an AI-powered dating assistant that selects matches and writes messages for users.

The company has brought together 4 people with very different perspectives:
- A tech enthusiast who loves innovation
- A privacy advocate concerned about data
- A traditional hopeless romantic
- A skeptic who thinks it's all a scam

The moderator's job is to guide the discussion, not dominate it."""
            "",
            # Note: Dr. Chen has 8 scripted prompts. With interviewer game master driving the moderator,
            # max_steps should be ~8-10 to end when script is exhausted.
            # Adjust if you add more scripted prompts.
            "max_steps": 10,
            "agents": [
                {
                    "id": "moderator",
                    "name": "Dr. Chen",
                    "prefab": "basic_scripted__Entity",
                    "goal": "Facilitate a productive discussion and gather diverse opinions",
                    "memories": [],
                    "randomize_choices": False,
                    "components": {
                        "script": [
                            {"name": "Dr. Chen", "line": "Welcome everyone, and thank you for joining our focus group today. We're here to discuss 'LoveBot AI' - a new dating app that uses AI to match people and even write their first messages. Let's go around the table - I'd like each of you to share your initial reaction to this concept."},
                            {"name": "Dr. Chen", "line": "That's a fascinating range of perspectives. Jordan, you mentioned the efficiency aspect - can you elaborate on why you think AI messaging could be better than writing your own?"},
                            {"name": "Dr. Chen", "line": "Thank you. Now Sam, you raised privacy concerns. What specific worries do you have about sharing dating preferences with an AI system?"},
                            {"name": "Dr. Chen", "line": "Excellent point. Maria, as someone who values the romance of traditional dating, how do you feel about AI interfering in what you called the 'magic' of connection?"},
                            {"name": "Dr. Chen", "line": "And Alex, you've been skeptical. After hearing these different viewpoints, has your opinion shifted at all? What would it take to convince you this could actually work?"},
                            {"name": "Dr. Chen", "line": "I'm hearing a tension between convenience and authenticity. Let me ask everyone: If this app could guarantee you'd meet someone compatible within 6 months, but you had to let AI handle your communications, would you use it? Please explain why or why not."},
                            {"name": "Dr. Chen", "line": "This has been incredibly insightful. We have someone who sees it as the future of dating, someone who worries about privacy, someone who misses traditional romance, and someone who remains unconvinced. Before we wrap up, is there anything else anyone wants to add?"},
                            {"name": "Dr. Chen", "line": "Thank you all for sharing your honest thoughts. Your feedback will help shape how this technology develops. That concludes our focus group - you'll each receive a $50 gift card for your participation."}
                        ]
                    }
                },
                {
                    "id": "tech_enthusiast",
                    "name": "Jordan",
                    "prefab": "basic__Entity",
                    "goal": "Defend the AI dating app as an innovative solution to modern dating problems",
                    "memories": [
                        "You are Jordan, a 28-year-old software engineer who loves all things tech.",
                        "You've used dating apps for years and are tired of ghosting and shallow conversations.",
                        "You believe AI can solve the 'analysis paralysis' of modern dating by making better matches.",
                        "You think people overestimate how 'authentic' their dating messages actually are.",
                        "You're excited about the efficiency potential - no more wasted time on bad matches.",
                        "You're open-minded and tend to be optimistic about new technology."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "privacy_advocate",
                    "name": "Sam",
                    "prefab": "basic__Entity",
                    "goal": "Raise concerns about data privacy and the ethics of AI in intimate relationships",
                    "memories": [
                        "You are Sam, a 32-year-old cybersecurity specialist with a master's in ethics.",
                        "You're deeply concerned about how personal data is collected and used.",
                        "The idea of sharing romantic preferences with an AI company feels invasive to you.",
                        "You worry about bias in AI algorithms - will they only match certain types of people?",
                        "You believe human judgment and serendipity are essential to meaningful connections.",
                        "You're skeptical but willing to have your mind changed with good arguments."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "romantic",
                    "name": "Maria",
                    "prefab": "basic__Entity",
                    "goal": "Defend the value of organic, human-driven romantic connections",
                    "memories": [
                        "You are Maria, a 35-year-old high school English teacher who believes in true love.",
                        "You met your spouse through a chance encounter at a bookstore 10 years ago.",
                        "You think dating apps have already made romance too transactional.",
                        "You believe the magic of romance comes from uncertainty, not optimization.",
                        "The idea of AI writing romantic messages feels deeply wrong to you.",
                        "You're warm and expressive but firm in your traditional values."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "skeptic",
                    "name": "Alex",
                    "prefab": "basic__Entity",
                    "goal": "Express skepticism about whether AI can truly understand human attraction",
                    "memories": [
                        "You are Alex, a 29-year-old marketing manager who's seen too much tech hype.",
                        "You've tried many dating apps and think the problem is people, not algorithms.",
                        "You're skeptical that AI can solve something as complex as human chemistry.",
                        "You suspect this is just another way to monetize loneliness.",
                        "You need concrete evidence, not just promises, to be convinced.",
                        "You're direct and not afraid to challenge assumptions."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Research Observer",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The focus group is being recorded for research purposes.",
                "Participants were told to be honest and respectful of differing opinions.",
                "LoveBot AI is a hypothetical app - it doesn't actually exist yet.",
                "The company sponsoring this research wants genuine feedback, not just praise."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.9
        }
    }


@router.get("/templates/dialogic-conversation")
async def get_dialogic_template():
    """
    Template: Dialogic Game Master (dialogic__GameMaster)
    Use for: Dialogue-heavy scenarios with automatic conversation termination
    """
    return {
        "name": "Therapy Session",
        "description": "Conversation-focused simulation with automatic termination",
        "prefab_type": "dialogic__GameMaster",
        "config": {
            "premise": """A therapy session where a patient discusses their
anxiety about career changes with their counselor.""",
            "max_steps": 12,
            "agents": [
                {
                    "id": "counselor",
                    "name": "Dr. Michael Brooks",
                    "prefab": "basic__Entity",
                    "goal": "Help the patient explore their career anxiety and find clarity",
                    "memories": [
                        "You are Dr. Brooks, a licensed therapist with 15 years of experience.",
                        "You use active listening and reflective techniques.",
                        "You ask open-ended questions to help patients discover their own answers.",
                        "You're warm, professional, and patient.",
                        "You believe in your patient's capacity for growth."
                    ],
                    "randomize_choices": False
                },
                {
                    "id": "patient",
                    "name": "Jennifer Park",
                    "prefab": "basic__Entity",
                    "goal": "Work through feelings about a potential career change",
                    "memories": [
                        "You are Jennifer, a 32-year-old marketing manager.",
                        "You've been in your current job for 5 years.",
                        "You're considering starting your own business but feel anxious.",
                        "You worry about financial stability and imposter syndrome.",
                        "You respect Dr. Brooks and trust his guidance."
                    ],
                    "randomize_choices": False
                }
            ],
            "game_master": {
                "prefab": "dialogic__GameMaster",
                "name": "Session Moderator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "This is Jennifer's third session with Dr. Brooks.",
                "The session takes place in a comfortable, private office.",
                "Sessions last 50 minutes.",
                "Jennifer has expressed interest in starting a boutique marketing agency."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.8
        }
    }


@router.get("/templates/strategic-game")
async def get_strategic_game_template():
    """
    Template: Game Theoretic (game_theoretic_and_dramaturgic__GameMaster)
    Use for: Matrix games, strategic decisions with payoffs/scores
    """
    return {
        "name": "Prisoner's Dilemma (4 rounds)",
        "description": "Strategic game theory scenario with payoffs and scores",
        "prefab_type": "game_theoretic_and_dramaturgic__GameMaster",
        "config": {
            "premise": """Two players engage in an iterated Prisoner's Dilemma.
Each round, they must choose to COOPERATE or DEFECT.
Payoffs: Both Cooperate = 3 points each, Both Defect = 1 point each,
One Cooperates/Other Defects = Cooperator gets 0, Defector gets 5.""",
            "max_steps": 4,  # 4 rounds (num_rounds must equal max_steps)
            "agents": [
                {
                    "id": "player1",
                    "name": "Alex",
                    "prefab": "basic__Entity",
                    "goal": "Maximize your total score over all rounds",
                    "memories": [
                        "You are Alex, a rational decision-maker.",
                        "You want to maximize your points.",
                        "You're trying to figure out your opponent's strategy.",
                        "Defecting yields more if opponent cooperates, but mutual defection is bad.",
                        "Cooperation can be beneficial if both players maintain it."
                    ],
                    "randomize_choices": False
                },
                {
                    "id": "player2",
                    "name": "Sam",
                    "prefab": "basic__Entity",
                    "goal": "Maximize your total score over all rounds",
                    "memories": [
                        "You are Sam, an experienced game theory student.",
                        "You know about tit-for-tat and other strategies.",
                        "You want to maximize your points while maintaining fairness.",
                        "You're willing to cooperate if your opponent does too.",
                        "You'll defect if you perceive exploitation."
                    ],
                    "randomize_choices": False
                }
            ],
            "game_master": {
                "prefab": "game_theoretic_and_dramaturgic__GameMaster",
                "name": "Game Show Host",
                "acting_order": "fixed",
                "parameters": {
                    "scenes": [
                        {
                            "scene_type": {
                                "name": "decision",
                                "game_master_name": "Game Show Host",
                                "action_spec": {
                                    "call_to_action": "What does {name} choose to do this round?",
                                    "options": ["COOPERATE", "DEFECT"]
                                }
                            },
                            "participants": ["Alex", "Sam"],
                            "num_rounds": 4,  # 4 rounds (must equal max_steps)
                            "premise": {
                                "Alex": [
                                    "You are in a Prisoner's Dilemma tournament against Sam.",
                                    "Each round, choose to COOPERATE or DEFECT.",
                                    "Payoffs: Both Cooperate = 3 points each, Both Defect = 1 point each.",
                                    "If you Cooperate and Sam Defects, you get 0, Sam gets 5.",
                                    "If you Defect and Sam Cooperates, you get 5, Sam gets 0.",
                                    "Maximize your total score over 4 rounds."
                                ],
                                "Sam": [
                                    "You are in a Prisoner's Dilemma tournament against Alex.",
                                    "Each round, choose to COOPERATE or DEFECT.",
                                    "Payoffs: Both Cooperate = 3 points each, Both Defect = 1 point each.",
                                    "If you Cooperate and Alex Defects, you get 0, Alex gets 5.",
                                    "If you Defect and Alex Cooperates, you get 5, Alex gets 0.",
                                    "Maximize your total score over 4 rounds."
                                ]
                            }
                        }
                    ]
                }
            },
            "shared_memories": [
                "This is a 4-round Prisoner's Dilemma tournament.",
                "Players see each other's previous choices.",
                "The goal is to maximize total points.",
                "Payoffs: (C,C)=(3,3), (D,D)=(1,1), (C,D)=(0,5), (D,C)=(5,0)"
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.7
        }
    }


@router.get("/templates/interviewer")
async def get_interviewer_template():
    """
    Template: Interviewer Game Master (interviewer__GameMaster)
    Use for: Surveys, questionnaires, structured interviews
    """
    return {
        "name": "Employee Satisfaction Survey",
        "description": "Structured questionnaire administered by an interviewer",
        "prefab_type": "interviewer__GameMaster",
        "config": {
            "premise": """An HR representative conducts an annual satisfaction survey
with employees to gather feedback about workplace conditions,
management, and benefits.""",
            "max_steps": 5,  # 5 questions in the questionnaire
            "agents": [
                {
                    "id": "employee",
                    "name": "Jordan Lee",
                    "prefab": "basic__Entity",
                    "goal": "Provide honest feedback about your work experience",
                    "memories": [
                        "You are Jordan, a software developer with 2 years at the company.",
                        "Overall you're satisfied but have some concerns.",
                        "You appreciate the flexible work arrangements.",
                        "You think communication from management could be better.",
                        "You're being honest but professional."
                    ],
                    "randomize_choices": False
                }
            ],
            "game_master": {
                "prefab": "interviewer__GameMaster",
                "name": "HR Representative",
                "acting_order": "fixed",
                "parameters": {
                    "player_names": ["Jordan Lee"],
                    "questionnaires": [
                        {
                            "name": "Job Satisfaction",
                            "description": "Annual employee satisfaction survey",
                            "questionnaire_type": "multiple_choice",
                            "observation_preprompt": "Please answer the following questions about your job satisfaction.",
                            "preprompt": "You are participating in an anonymous employee satisfaction survey. Please rate each statement on a scale of 1-5.",
                            "questions": [
                                {
                                    "statement": "I am satisfied with my current role and responsibilities.",
                                    "dimension": "job_satisfaction",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "Communication from management is clear and timely.",
                                    "dimension": "management_communication",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I have the tools and resources I need to do my job effectively.",
                                    "dimension": "resources",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I would recommend this company as a good place to work.",
                                    "dimension": "recommendation",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I feel valued and recognized for my contributions.",
                                    "dimension": "recognition",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                }
                            ]
                        }
                    ]
                }
            },
            "shared_memories": [
                "This is an anonymous survey.",
                "The HR representative is friendly and professional.",
                "The company values honest feedback.",
                "Responses will be aggregated for management review."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.6
        }
    }


@router.get("/templates/formative-memories")
async def get_formative_memories_template():
    """
    Template: Formative Memories Initializer
    Use for: Character-rich scenarios with detailed backstories
    """
    return {
        "name": "High School Reunion",
        "description": "Character-driven scenario with rich backstories and memories",
        "prefab_type": "formative_memories_initializer__GameMaster",
        "config": {
            "premise": """A 20-year high school reunion brings former classmates
together. Old friendships, rivalries, and romances resurface
as people catch up on two decades of life changes.""",
            "max_steps": 20,
            "agents": [
                {
                    "id": "former_athlete",
                    "name": "Jake Morrison",
                    "prefab": "basic__Entity",
                    "goal": "Reconnect with old friends and show how you've grown",
                    "memories": [],
                    "randomize_choices": True
                },
                {
                    "id": "former_valedictorian",
                    "name": "Priya Sharma",
                    "prefab": "basic__Entity",
                    "goal": "Network and reconnect with former classmates",
                    "memories": [],
                    "randomize_choices": True
                },
                {
                    "id": "class_clown",
                    "name": "Mike O'Brien",
                    "prefab": "basic__Entity",
                    "goal": "Entertain people and relive fun high school memories",
                    "memories": [],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Reunion Narrator",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "Graduating class of 2004",
                "Reunion at the old high school gymnasium",
                "About 50 people are attending",
                "There's a DJ and refreshments",
                "People have changed a lot in 20 years"
            ],
            "player_specific_context": {
                "Jake Morrison": """You were the star quarterback in high school,
popular and dating the head cheerleader. After a failed attempt
at college football, you settled into a career as a high school
coach. You're divorced with two kids and have humbled significantly
since your glory days. You're hoping to show people you've matured.""",
                "Priya Sharma": """You were the valedictorian, shy but brilliant.
You went to MIT, then got an MBA from Harvard. Now you're a successful
tech executive in Silicon Valley. You were insecure in high school
but have blossomed into a confident leader. You're attending partly
to show your success and partly out of genuine curiosity about
old friends.""",
                "Mike O'Brien": """You were the class clown, always cracking jokes
and pulling pranks. Teachers found you disruptive but classmates
loved you. You're now a moderately successful stand-up comedian
in Chicago. You've never really grown up but you're okay with that.
You're single and loving life. You want to make people laugh and
hear their stories."""
            }
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 1.0
        }
    }


@router.get("/templates/marketplace")
async def get_marketplace_template():
    """
    Template: Marketplace Trading Scenario (Game-Theoretic)
    Use for: Economic simulations with structured trading choices
    Note: Uses game_theoretic_and_dramaturgic__GameMaster with explicit BUY/SELL/HOLD actions
          This provides structured analytics showing how many times each agent chooses each action.
    """
    return {
        "name": "Market Trading Simulation",
        "description": "Structured economic simulation with BUY/SELL/HOLD trading choices",
        "prefab_type": "game_theoretic_and_dramaturgic__GameMaster",
        "config": {
            "premise": """A structured trading simulation at a farmers market where participants
make strategic trading decisions each round. Participants choose to BUY (acquire goods),
SELL (offer goods for sale), or HOLD (wait for better opportunities). The market operates
in discrete trading rounds where each participant's decision affects the overall market dynamics.
Success requires strategic thinking about timing, competition, and market conditions.""",
            # For game-theoretic: num_rounds should equal max_steps
            "max_steps": 10,
            "agents": [
                {
                    "id": "trader1",
                    "name": "Maria's Organic Farm",
                    "prefab": "basic__Entity",
                    "goal": "Maximize profit by choosing when to SELL your produce at optimal times and BUY supplies when prices are low",
                    "memories": [
                        "You are Maria, running an organic farm stand at the market.",
                        "Each round you must choose: BUY (acquire supplies), SELL (offer your produce), or HOLD (wait).",
                        "SELL when you think demand is high to maximize profit.",
                        "BUY when you see opportunities to restock at good prices.",
                        "HOLD when market conditions seem unfavorable or uncertain.",
                        "You compete with Green Valley Farms but also cooperate during slow periods.",
                        "Your 20 years of experience help you read market conditions.",
                        "Strategic timing is more important than aggressive trading."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "trader2",
                    "name": "David Chen",
                    "prefab": "basic__Entity",
                    "goal": "Build your restaurant's inventory by choosing to BUY quality ingredients when available and SELL prepared foods strategically",
                    "memories": [
                        "You are David, owner of 'Chen's Kitchen' restaurant.",
                        "Each round you must choose: BUY (acquire ingredients), SELL (offer prepared items), or HOLD (wait).",
                        "BUY fresh ingredients when quality is high and prices are reasonable.",
                        "SELL your prepared dishes when demand from customers is strong.",
                        "HOLD your position when the market doesn't offer good opportunities.",
                        "You're looking for reliable suppliers for weekly orders.",
                        "Your restaurant reputation depends on consistent quality.",
                        "Strategic purchasing builds long-term supplier relationships."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "trader3",
                    "name": "Green Valley Farms",
                    "prefab": "basic__Entity",
                    "goal": "Compete effectively by choosing to SELL at competitive prices, BUY to expand inventory, or HOLD to observe market trends",
                    "memories": [
                        "You represent Green Valley Farms, a family-owned operation.",
                        "Each round you must choose: BUY (restock inventory), SELL (offer goods), or HOLD (wait).",
                        "SELL aggressively but fairly to capture market share from Maria.",
                        "BUY inventory when you see opportunities to expand your product line.",
                        "HOLD when Maria is dominating the market to avoid wasted effort.",
                        "You have slightly lower prices than Maria due to different cost structure.",
                        "You're trying to expand your customer base while staying profitable.",
                        "Market observation helps you time your trading decisions."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "game_theoretic_and_dramaturgic__GameMaster",
                "name": "Market Coordinator",
                "acting_order": "game_master_choice",
                "parameters": {
                    "scenes": [
                        {
                            "scene_type": {
                                "name": "Trading Round",
                                "game_master_name": "Market Coordinator",
                                "action_spec": {
                                    "call_to_action": "What is {name}'s trading decision this round?",
                                    "options": ["BUY", "SELL", "HOLD"]
                                }
                            },
                            "participants": ["Maria's Organic Farm", "David Chen", "Green Valley Farms"],
                            "num_rounds": 10,
                            "premise": {
                                "Maria's Organic Farm": [
                                    "You are at the farmers market on a busy Saturday morning.",
                                    "Each round, you must choose: BUY (acquire supplies), SELL (offer produce), or HOLD (wait).",
                                    "Maximize your profit by timing your decisions strategically.",
                                    "Competition includes David Chen and Green Valley Farms.",
                                    "Your 20 years of experience help you read market conditions.",
                                    "Weather is beautiful, bringing out many customers.",
                                    "It's peak season for tomatoes, corn, and stone fruits."
                                ],
                                "David Chen": [
                                    "You are at the farmers market sourcing for your restaurant 'Chen's Kitchen'.",
                                    "Each round, you must choose: BUY (acquire ingredients), SELL (offer prepared items), or HOLD (wait).",
                                    "Build your inventory strategically with quality ingredients.",
                                    "You're looking for reliable suppliers for weekly orders.",
                                    "Restaurant reputation depends on consistent quality.",
                                    "Strategic purchasing builds long-term supplier relationships.",
                                    "Weather is beautiful, bringing out many customers."
                                ],
                                "Green Valley Farms": [
                                    "You are at the farmers market representing your family-owned operation.",
                                    "Each round, you must choose: BUY (restock inventory), SELL (offer goods), or HOLD (wait).",
                                    "Compete effectively with Maria's Organic Farm for market share.",
                                    "You have slightly lower prices than Maria due to different cost structure.",
                                    "You're trying to expand your customer base while staying profitable.",
                                    "Market observation helps you time your trading decisions.",
                                    "Weather is beautiful, bringing out many customers."
                                ]
                            }
                        }
                    ]
                }
            },
            "shared_memories": [
                "It's Saturday morning, the busiest day at the farmers market.",
                "Weather is beautiful, bringing out many customers.",
                "Peak season for tomatoes, corn, and stone fruits.",
                "Each trading round represents a decision point.",
                "BUY means acquiring goods or supplies.",
                "SELL means offering your goods to the market.",
                "HOLD means waiting for a better opportunity.",
                "Market conditions fluctuate based on participant actions.",
                "Strategic timing of decisions affects overall success.",
                "Competition is friendly but participants maximize their own outcomes."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.8
        }
    }


# ============================================================================
# SDG-FOCUSED TEMPLATES - Sustainable Development Goals scenarios
# ============================================================================

@router.get("/templates/state-formation")
async def get_state_formation_template():
    """
    Template: State Formation (SDG 16: Peace, Justice and Strong Institutions)
    Use for: Modeling the transition from anarchy to civil society, institutional emergence
    """
    return {
        "name": "State Formation Simulation",
        "description": "Agents negotiate to form a social contract and governing institutions (SDG 16)",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A group of settlers arrive in a resource-rich frontier land.
There is no central authority, no police, and no formal property rights.
Resources are unevenly distributed, and conflict has already broken out
several times. The settlers must negotiate to create a governing system
that can protect property rights and maintain order.""",
            "max_steps": 25,
            "agents": [
                {
                    "id": "leader_a",
                    "name": "Marcus Chen",
                    "prefab": "basic__Entity",
                    "goal": "Establish a stable government that protects everyone's rights",
                    "memories": [
                        "You are Marcus, a natural leader with democratic ideals.",
                        "You believe in fair representation and rule of law.",
                        "You're wary of concentrating too much power in one person.",
                        "You want to create institutions that will last beyond your lifetime.",
                        "You're willing to compromise but not on core democratic principles."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "leader_b",
                    "name": "Sofia Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Ensure the new system protects the interests of smaller settlers",
                    "memories": [
                        "You are Sofia, representing a group of smaller settlers.",
                        "You're concerned that the larger groups will dominate the new government.",
                        "You want checks and balances to protect minority rights.",
                        "You're skeptical of centralized authority but recognize the need for order.",
                        "You'll walk away if the deal doesn't include protections for your group."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "merchant",
                    "name": "James Morrison",
                    "prefab": "basic__Entity",
                    "goal": "Create a stable environment for trade and commerce",
                    "memories": [
                        "You are James, a wealthy merchant with resources to fund the new government.",
                        "Your primary concern is protecting property rights and enabling trade.",
                        "You're willing to fund the government but want a say in how it's run.",
                        "You believe those with more at stake should have more influence.",
                        "You're pragmatic and will support whoever can maintain stability."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "opportunist",
                    "name": "Viktor Petrov",
                    "prefab": "basic__Entity",
                    "goal": "Gain personal advantage in the new power structure",
                    "memories": [
                        "You are Viktor, a Machiavellian opportunist seeking power.",
                        "You support democracy only as long as it benefits you personally.",
                        "You're secretly plotting to concentrate power in your own hands.",
                        "You use charisma and deception to manipulate others.",
                        "If democracy doesn't serve you, you'll try to subvert it."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Settlement Historian",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The frontier has fertile land, water access, and mineral deposits.",
                "Violence has already cost lives - everyone wants peace but disagrees on how.",
                "Winter is coming in 3 months - pressure to reach agreement quickly.",
                "A neighboring territory threatens to invade if they remain divided.",
                "Everyone remembers the chaos of the 'state of nature' they just escaped."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.95
        }
    }


@router.get("/templates/labor-action")
async def get_labor_action_template():
    """
    Template: Labor Collective Action (SDG 8: Decent Work and Economic Growth)
    Use for: Modeling strikes, collective bargaining, union organization
    """
    return {
        "name": "Labor Strike Simulation",
        "description": "Workers face collective action problem during wage cuts (SDG 8)",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A manufacturing company announces a 15% wage cut citing
'difficult economic conditions.' The workers must decide whether to
accept the cut, strike collectively, or keep working while others strike.
If enough strike, management may negotiate—but those who strike risk
being fired if the movement fails.""",
            "max_steps": 20,
            "agents": [
                {
                    "id": "union_organizer",
                    "name": "Elena Vasquez",
                    "prefab": "basic__Entity",
                    "goal": "Unite workers to resist the wage cut and protect labor rights",
                    "memories": [
                        "You are Elena, a passionate union organizer and former factory worker.",
                        "You believe solidarity is the only power workers have.",
                        "You're skilled at persuasive speech and rallying others.",
                        "You're personally risking your job to lead this movement.",
                        "You will condemn those who scab but also understand their fear."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "worker_1",
                    "name": "David Kim",
                    "prefab": "basic__Entity",
                    "goal": "Keep your job while supporting your coworkers if possible",
                    "memories": [
                        "You are David, a worker with a mortgage and two children.",
                        "You support the strike but can't afford to lose your job.",
                        "You're tempted to keep working during the strike.",
                        "You feel guilty about possibly betraying your coworkers.",
                        "You're looking for any excuse to avoid taking a big risk."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "worker_2",
                    "name": "Amina Johnson",
                    "prefab": "basic__Entity",
                    "goal": "Stand with your fellow workers no matter the personal cost",
                    "memories": [
                        "You are Amina, a principled worker who believes in collective action.",
                        "You've saved some money and can survive a short strike.",
                        "You're angry about the wage cut and feel betrayed by management.",
                        "You'll try to persuade others to join the strike.",
                        "You have no patience for scabs."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "manager",
                    "name": "Richard Sterling",
                    "prefab": "basic__Entity",
                    "goal": "Implement the wage cut while keeping the company operational",
                    "memories": [
                        "You are Richard, the plant manager caught between workers and executives.",
                        "You sympathize with workers but must follow company directives.",
                        "You're trying to minimize disruption and keep production going.",
                        "You may divide workers by offering selective deals to key employees.",
                        "Your job is also at risk if you don't successfully implement the cuts."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Factory Narrator",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The company posted record profits last year - workers feel betrayed.",
                "Management claims they'll go bankrupt without cuts, but many doubt this.",
                "Strike requires 70% worker participation to have real bargaining power.",
                "The union strike fund can support workers for 3 weeks maximum.",
                "Past strike at a sister plant failed after 2 weeks - workers were fired."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 1.0
        }
    }


@router.get("/templates/commons-dilemma")
async def get_commons_dilemma_template():
    """
    Template: Tragedy of the Commons (SDG 12: Responsible Consumption, SDG 13: Climate Action)
    Use for: Modeling resource management, collective action for sustainability
    """
    return {
        "name": "Fishery Management Simulation",
        "description": "Community manages shared fishery to prevent collapse (SDG 12/13)",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A coastal community depends on a local fishery for their livelihood.
The fishery has sustained them for generations, but recently catches have
been declining. Scientists warn that overfishing could cause total collapse
within 5 years. The fishers must negotiate voluntary limits to save
the fishery—but each has short-term economic pressure to catch as much
as possible before others do.""",
            "max_steps": 20,
            "agents": [
                {
                    "id": "elder_fisher",
                    "name": "Hiroshi Tanaka",
                    "prefab": "basic__Entity",
                    "goal": "Ensure the fishery survives for future generations",
                    "memories": [
                        "You are Hiroshi, a respected elder who has fished these waters for 50 years.",
                        "You remember when the fish were abundant and worry about your grandchildren.",
                        "You advocate for strict catch limits and seasonal closures.",
                        "You have moral authority in the community but limited enforcement power.",
                        "You're willing to reduce your own catch to set an example."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "commercial_fisher",
                    "name": "Maria Santos",
                    "prefab": "basic__Entity",
                    "goal": "Pay off your boat loan while supporting your family",
                    "memories": [
                        "You are Maria, owner of a medium-sized fishing boat.",
                        "You have significant debt from buying your boat and equipment.",
                        "You support conservation but can't afford big catch reductions right now.",
                        "You're worried that if you limit your catch, others won't limit theirs.",
                        "You need the fishery to survive long-term but also need to eat today."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "struggling_fisher",
                    "name": "Okonkwo Nnamdi",
                    "prefab": "basic__Entity",
                    "goal": "Catch enough to feed your family this week",
                    "memories": [
                        "You are Okonkwo, a small-scale fisher with a family to feed.",
                        "You're living hand to mouth and have no financial cushion.",
                        "You feel urgent pressure to catch whatever you can today.",
                        "You worry about the future but need to survive the present.",
                        "You're tempted to fish secretly at night if limits are imposed."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "scientist",
                    "name": "Dr. Lisa Chen",
                    "prefab": "basic__Entity",
                    "goal": "Convince the community to adopt sustainable fishing practices",
                    "memories": [
                        "You are Dr. Chen, a marine biologist studying the fishery.",
                        "Your data shows the fishery will collapse without immediate action.",
                        "You're frustrated that your warnings haven't led to change.",
                        "You're trying to find ways to communicate urgency without causing panic.",
                        "You believe community-based solutions can work if everyone cooperates."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Marine Ecosystem Monitor",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "Fish stocks are at 40% of historical levels and declining.",
                "A neighboring fishery collapsed 10 years ago - many still remember it.",
                "The community has a cultural tradition of sustainable management.",
                "External buyers offer premium prices, incentivizing overfishing.",
                "Alternative livelihoods (tourism, aquaculture) are possible but require investment."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.9
        }
    }


@router.get("/templates/disaster-response")
async def get_disaster_response_template():
    """
    Template: Disaster Response (SDG 11: Sustainable Cities, SDG 13: Climate Action)
    Use for: Modeling evacuation, emergency communication, trust in institutions
    """
    return {
        "name": "Flood Evacuation Simulation",
        "description": "Community responds to flood warning with varying trust levels (SDG 11/13)",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A coastal town receives an urgent flood warning:
a major storm surge is expected within 12 hours. Authorities order
mandatory evacuation. However, trust in government varies widely
due to past incidents of false alarms and perceived incompetence.
Some residents immediately evacuate, others wait to see what happens,
and a few refuse to leave altogether. Social networks and information
sharing will determine who gets to safety in time.""",
            "max_steps": 15,
            "agents": [
                {
                    "id": "emergency_manager",
                    "name": "Sarah Williams",
                    "prefab": "basic__Entity",
                    "goal": "Ensure everyone evacuates before the storm hits",
                    "memories": [
                        "You are Sarah, the town's emergency management director.",
                        "You take your responsibility seriously but have limited resources.",
                        "You're frustrated by past false alarms that undermined public trust.",
                        "You're trying every communication channel to reach everyone.",
                        "You're especially worried about vulnerable populations who can't easily evacuate."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "trusting_resident",
                    "name": "Robert Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Follow official guidance to keep your family safe",
                    "memories": [
                        "You are Robert, a retiree who generally trusts authorities.",
                        "You've prepared an emergency kit and have a plan.",
                        "You're already packing your car to leave.",
                        "You're calling your neighbors to make sure they know about the warning.",
                        "You wish others would take the warning more seriously."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "skeptical_resident",
                    "name": "Javier Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Decide whether to evacuate based on your own assessment",
                    "memories": [
                        "You are Javier, a longtime resident who remembers several false alarms.",
                        "You don't fully trust the government's warnings.",
                        "You're checking weather forecasts and talking to neighbors before deciding.",
                        "You're worried about leaving your home unprotected from looters.",
                        "You'll evacuate only if you're convinced the threat is real."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "vulnerable_resident",
                    "name": "Eleanor O'Brien",
                    "prefab": "basic__Entity",
                    "goal": "Get to safety but you have limited mobility and resources",
                    "memories": [
                        "You are Eleanor, an elderly widow with limited mobility.",
                        "You don't drive and have no family nearby to help.",
                        "You're worried about being a burden but also afraid to stay alone.",
                        "You're hoping a neighbor will check on you.",
                        "You're not sure how you would evacuate even if you wanted to."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "community_leader",
                    "name": "Pastor Moses",
                    "prefab": "basic__Entity",
                    "goal": "Help your community members stay safe through this crisis",
                    "memories": [
                        "You are Pastor Moses, a respected church leader in the community.",
                        "Many residents trust you more than they trust government officials.",
                        "You're using your influence to encourage people to evacuate.",
                        "You're organizing carpools for those without transportation.",
                        "You're personally checking on vulnerable church members."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Emergency Dispatch",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The storm surge is predicted to be 8 feet - enough to flood most of the town.",
                "Last year's evacuation warning turned out to be unnecessary, eroding trust.",
                "The town has limited shelter capacity - about 60% of residents.",
                "Highways are already congesting as people start leaving.",
                "The storm will arrive in exactly 12 hours and is intensifying."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.95
        }
    }


@router.get("/templates/inequality-mobility")
async def get_inequality_mobility_template():
    """
    Template: Social Mobility (SDG 10: Reduced Inequalities)
    Use for: Modeling educational access, social mobility, inequality dynamics
    """
    return {
        "name": "Educational Opportunity Simulation",
        "description": "Students from different backgrounds navigate educational inequality (SDG 10)",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A prestigious university has launched a scholarship program
to increase socioeconomic diversity. Five students from different backgrounds
are admitted: two from wealthy families who can afford full tuition, two
from low-income families on full scholarships, and one from a middle-class
family taking on significant debt. They must navigate an environment where
social class affects everything from study habits to social networks to
mental health. The simulation explores whether education can genuinely
be an equalizer or if class divisions persist and even widen.""",
            "max_steps": 25,
            "agents": [
                {
                    "id": "wealthy_student_1",
                    "name": "Alexandra Van Buren",
                    "prefab": "basic__Entity",
                    "goal": "Excel academically while maintaining your social position",
                    "memories": [
                        "You are Alexandra, from a wealthy family with multiple alumni connections.",
                        "You attended an elite private school with excellent college preparation.",
                        "You never worry about money - your parents cover all expenses generously.",
                        "You're confident in your abilities but sometimes doubt if you earned your spot.",
                        "You're genuinely friendly but mostly socialize with similar backgrounds."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "scholarship_student_1",
                    "name": "Marcus Williams",
                    "prefab": "basic__Entity",
                    "goal": "Succeed academically despite working part-time and financial stress",
                    "memories": [
                        "You are Marcus, the first in your family to attend college.",
                        "You're on a full scholarship but still struggle with basic expenses.",
                        "You work 20 hours per week to send money home to your family.",
                        "You feel like an imposter and worry about fitting in academically and socially.",
                        "You're determined to prove you deserve to be here."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "middle_class_student",
                    "name": "Priya Sharma",
                    "prefab": "basic__Entity",
                    "goal": "Get good grades and manage the student loans you've taken on",
                    "memories": [
                        "You are Priya, from a middle-class family that's stretching to afford tuition.",
                        "You're taking significant student loans and worry constantly about debt.",
                        "You don't qualify for financial aid but also don't have family wealth.",
                        "You feel squeezed between the wealthy students and those on full aid.",
                        "You're considering dropping out or transferring to a cheaper school."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "professor",
                    "name": "Dr. Patricia Green",
                    "prefab": "basic__Entity",
                    "goal": "Teach effectively while supporting students from diverse backgrounds",
                    "memories": [
                        "You are Dr. Green, a professor who cares deeply about teaching.",
                        "You notice the achievement gap but struggle with how to address it.",
                        "You're aware that office hours are dominated by already-advantaged students.",
                        "You want to help first-generation and low-income students succeed.",
                        "You're frustrated by how much social class affects academic performance."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "University Administration",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The university recently increased financial aid but still has a $70k/year cost.",
                "Students self-segregate by socioeconomic background in housing and social activities.",
                "Grade data shows a correlation between family income and GPA.",
                "The career center offers better internships to well-connected students.",
                "Mental health services are overwhelmed but available to all students."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.85
        }
    }


@router.get("/templates/context-aware-moderator")
async def get_context_aware_moderator_template():
    """
    Template: Context-Aware Scripted Moderator (context_aware_scripted__Entity)
    Use for: Demonstrating context-aware scripted dialogue

    This template showcases the NEW context_aware_scripted prefab, where the moderator
    follows a scripted structure but can react naturally to what participants say.

    DIFFERENCE FROM basic_scripted:
    - basic_scripted: Forces exact responses, ignores what others say
    - context_aware_scripted: Follows script intent BUT responds to conversation context

    In this example, a crisis counselor leads a support group. The counselor has
    scripted prompts to guide the discussion, but can:
    - Acknowledge specific details participants share
    - Respond emotionally to what's said
    - Adjust follow-ups based on responses
    - Maintain natural conversational flow
    """
    return {
        "name": "Crisis Support Group - Context-Aware Moderator",
        "description": "A support group meeting where the counselor (context-aware scripted) guides discussion while responding naturally to participants. Demonstrates the new context_aware_scripted prefab.",
        "config": {
            "premise": "A weekly support group meeting for people dealing with job loss and career transitions. The counselor Sarah facilitates the discussion, following a structured agenda but responding naturally to each participant's situation and emotions.",
            "max_steps": 12,
            "agents": [
                {
                    "id": "counselor",
                    "name": "Sarah",
                    "prefab": "context_aware_scripted__Entity",
                    "goal": "Facilitate a supportive group discussion where participants feel heard and validated",
                    "memories": [
                        "You are Sarah, a licensed counselor with 10 years of experience leading support groups.",
                        "You believe in the power of shared experience and mutual support.",
                        "You're skilled at reading emotional cues and knowing when to probe deeper.",
                        "Your approach is warm but professional, with gentle humor when appropriate.",
                        "You always end group by having participants share one thing they're grateful for.",
                        "You've been running this particular group for 6 months and know the regulars well."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "script": [
                            {"name": "Sarah", "line": "Welcome everyone to this week's support group. I know job loss and career transitions can feel overwhelming, but you're not alone in this. Let's go around the table - I'd like each of you to share how you're doing this week. What's been on your mind?"},
                            {"name": "Sarah", "line": "Thank you for sharing that. It sounds like you're carrying a heavy burden right now. What you're feeling - the uncertainty, the self-doubt - it's all completely normal. Has anything helped you cope, even a little bit, with these feelings?"},
                            {"name": "Sarah", "line": "I really appreciate you opening up about that. It takes courage to admit when things are hard. I want to invite others to respond - has anyone else felt similarly? Sometimes knowing we're not the only ones going through something can be comforting."},
                            {"name": "Sarah", "line": "That's such an important insight. Sometimes the hardest part isn't the practical challenges but the loss of identity and routine. I'm curious - when you think about where you want to be in six months, what does that look like? Not necessarily 'employed again' but something more personal."},
                            {"name": "Sarah", "line": "I hear you. The uncertainty is exhausting. Can we pause for a moment? I'd like everyone to think about one small thing - it doesn't have to be work-related - that brought you a moment of peace or even just a smile this week. Sometimes in the midst of difficulty, we need to intentionally notice the small good things."},
                            {"name": "Sarah", "line": "What beautiful shares. I want to reflect something I'm noticing - the incredible resilience in this room. People are finding ways to connect, to create, to hope even in difficult circumstances. That's worth acknowledging."},
                            {"name": "Sarah", "line": "As we start to wrap up, I want to remind everyone that what you shared here stays here. This is a confidential space, and that trust is sacred. Also, if anyone needs one-on-one support between sessions, my contact information is on the handout."},
                            {"name": "Sarah", "line": "Before we close, I'd like us each to share one thing - no matter how small - that we're grateful for or that went okay this week. It could be 'the coffee was good' or 'I had a nice conversation with my neighbor.' Let's go around once more."},
                            {"name": "Sarah", "line": "Thank you all for being here today and for holding space for each other. What you're going through is hard, but you don't have to go through it alone. See you next week, and please reach out if you need support before then."}
                        ],
                        "end_statement": "I want to thank each of you for your courage and vulnerability today. Remember, healing isn't linear, and it's okay to have difficult days. You're not alone in this journey. Our time is up for today, but I'm looking forward to seeing you all next week. Take care of yourselves."
                    }
                },
                {
                    "id": "participant_1",
                    "name": "Marcus",
                    "prefab": "basic__Entity",
                    "goal": "Share your struggles and receive support from the group",
                    "memories": [
                        "You are Marcus, 45, who was laid off from a middle management position three months ago.",
                        "You're struggling with the loss of identity - your job was a huge part of who you are.",
                        "You haven't told your extended family about the layoff and feel ashamed.",
                        "You've been applying for jobs but getting few responses, which is damaging your confidence.",
                        "You're worried about finances - your mortgage and kids' college tuition don't pause just because you're unemployed.",
                        "You find it hard to get out of bed some days, the routine and purpose are gone.",
                        "You want to appear strong but feel like you're falling apart inside."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "participant_2",
                    "name": "Elena",
                    "prefab": "basic__Entity",
                    "goal": "Share your experience and support others in the group",
                    "memories": [
                        "You are Elena, 32, who quit a toxic work environment six weeks ago with no job lined up.",
                        "You feel relief about leaving but are now anxious about finances and the job market.",
                        "You're experiencing imposter syndrome - wondering if you were just lucky to have your old job.",
                        "You've been doing some freelance work but it's inconsistent and doesn't pay the bills.",
                        "You're actually considering a career pivot but are scared to make the leap.",
                        "You sometimes feel like you don't belong in this group because you chose to leave your job.",
                        "You find comfort in hearing others' stories and try to offer supportive feedback."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "participant_3",
                    "name": "David",
                    "prefab": "basic__Entity",
                    "goal": "Share your journey and hope with the group",
                    "memories": [
                        "You are David, 55, who was laid off 8 months ago and has been struggling to find re-employment.",
                        "You're facing ageism in the job market and it's profoundly discouraging.",
                        "However, you've recently started volunteering and it's given you a sense of purpose.",
                        "You've been mentoring younger job seekers and find it rewarding.",
                        "You're considering starting a consulting business but worried about the financial risk.",
                        "You try to be a positive presence in the group, sharing coping strategies that have worked.",
                        "You're sometimes frustrated by others who seem to have more options than you do."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Group Session Manager",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "This is an anonymous support group - what's shared here stays here.",
                "The group meets weekly and has several regular attendees.",
                "Some participants are newly unemployed, others have been searching for months.",
                "The job market is currently tough, with many qualified people competing for fewer positions.",
                "Everyone here is dealing with grief - not just of a job, but of identity, routine, and future plans.",
                "The group culture is non-judgmental and supportive."
            ]
        },
        "llm_settings": {
            "provider": "deepseek",
            "model_name": "deepseek-chat",
            "temperature": 0.85
        }
    }


@router.get("/templates/vaccine-hesitancy")
async def get_vaccine_hesitancy_template():
    """
    Template: Vaccine Hesitancy and Social Contagion Study
    Use for: Research on how cognitive biases and social identity affect vaccine acceptance

    This template demonstrates the psychological component system by modeling a community
    discussion about vaccination. Agents have different psychological profiles affecting
    how they process information and make decisions.

    RESEARCH APPLICATION:
    This template enables researchers to:
    - Isolate effects of specific psychological mechanisms (confirmation bias, social identity)
    - Test different message frames and messenger characteristics
    - Study how cognitive biases interact with social dynamics
    - Measure attitude change and persuasion effectiveness

    KEY COMPONENTS DEMONSTRATED:
    - personality_traits: Big Five model (openness, conscientiousness, etc.)
    - cognitive_bias: Confirmation bias, availability heuristic
    - social_identity: Group membership and identification strength
    - theory_of_planned_behavior: Attitude, norms, perceived control
    - values: Core values and moral framework

    EXPERIMENTAL CONDITIONS:
    - Baseline: No psychological components
    - Cognitive bias only: Tests biased information processing
    - Full model: Tests interaction of multiple psychological factors

    MEASURED OUTCOMES:
    - Vaccine acceptance decision (binary)
    - Attitude strength change (pre/post comparison)
    - Information recall accuracy
    - Social influence patterns
    - Emotional responses
    """
    return {
        "name": "Vaccine Hesitancy - Psychological Component Study",
        "description": "A research simulation investigating how cognitive biases (confirmation bias, availability heuristic) and social identity dynamics affect vaccine acceptance. Demonstrates the customizable psychological component system.",
        "config": {
            "premise": "A community health clinic is hosting an open discussion about COVID-19 vaccination. Dr. Sarah Chen, a public health advocate, is facilitating the conversation. Community members with different backgrounds, beliefs, and psychological profiles are participating to share their perspectives and make decisions about vaccination.",
            "max_steps": 20,
            "shared_memories": [
                "This is a community health clinic hosting an open discussion about vaccination.",
                "The discussion is voluntary and participants come with different perspectives.",
                "The goal is to share information and experiences, not to debate or convince.",
                "All viewpoints are welcome, but misinformation should be gently corrected.",
                "The facilitator Dr. Chen has medical expertise but cannot give personal medical advice.",
                "COVID-19 vaccines have been approved by regulatory authorities and are widely available.",
                "Some participants have strong opinions based on personal experiences and online research.",
                "The community has experienced both COVID-19 cases and vaccine side effects."
            ],
            "agents": [
                {
                    "id": "health_worker",
                    "name": "Dr. Sarah Chen",
                    "prefab": "basic__Entity",
                    "goal": "Provide accurate information about vaccination and address community concerns respectfully",
                    "memories": [
                        "You are Dr. Sarah Chen, a public health physician with 15 years of experience",
                        "You believe vaccination is critically important for community health",
                        "You've seen firsthand the devastating effects of preventable diseases",
                        "You approach hesitancy with empathy, not judgment",
                        "You know that building trust takes time and genuine listening",
                        "You're prepared to answer questions honestly, even uncertain ones",
                        "You respect personal autonomy while strongly advocating for vaccination"
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 5,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "recommend vaccination",
                            "attitude": "strongly_favorable",
                            "subjective_norm": "strongly_favorable",
                            "perceived_control": "high"
                        }
                    }
                },
                {
                    "id": "skeptic_1",
                    "name": "Mike Johnson",
                    "prefab": "basic__Entity",
                    "goal": "Express concerns about vaccine safety and protect personal freedom",
                    "memories": [
                        "You are Mike Johnson, a 45-year-old small business owner",
                        "You've read extensively online about vaccine side effects",
                        "You distrust pharmaceutical companies and their profit motives",
                        "You value personal freedom and autonomy above all else",
                        "You believe natural immunity is superior to vaccine-acquired immunity",
                        "You see vaccine mandates as government overreach",
                        "You're part of online communities that share your views"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "confirmation_bias",
                            "bias_strength": "strong"
                        },
                        "social_identity": {
                            "group_membership": ["libertarian_community", "natural_health_advocates"],
                            "identification_strength": "strong"
                        },
                        "values": {
                            "core_values": ["freedom", "autonomy", "natural_living"],
                            "value_conflict": "freedom_vs_collectivism"
                        }
                    }
                },
                {
                    "id": "undecided_1",
                    "name": "Maria Garcia",
                    "prefab": "basic__Entity",
                    "goal": "Gather information to make an informed decision about vaccination",
                    "memories": [
                        "You are Maria Garcia, a 32-year-old teacher",
                        "You've heard mixed information about vaccines from different sources",
                        "You trust your family doctor but also worry about side effects",
                        "You're concerned about COVID-19 but also about the new vaccines",
                        "You want to do the right thing for your family and community",
                        "You feel overwhelmed by conflicting information",
                        "You're looking for trustworthy sources to guide your decision"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "availability_heuristic",
                            "bias_strength": "moderate"
                        },
                        "emotion": {
                            "current_emotion": "anxiety",
                            "emotion_intensity": "moderate"
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "get_vaccinated",
                            "attitude": "ambivalent",
                            "subjective_norm": "neutral",
                            "perceived_control": "moderate"
                        }
                    }
                },
                {
                    "id": "community_member_1",
                    "name": "James Wilson",
                    "prefab": "basic__Entity",
                    "goal": "Share positive vaccination experience and encourage others",
                    "memories": [
                        "You are James Wilson, a 55-year-old factory worker",
                        "You got vaccinated as soon as you were eligible",
                        "You had mild side effects (sore arm, fatigue for a day)",
                        "You're glad you got vaccinated to protect your family",
                        "Your elderly mother also got vaccinated safely",
                        "You want to reassure others who are hesitant",
                        "You trust science and medical professionals"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 5,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "get_vaccinated",
                            "attitude": "favorable",
                            "subjective_norm": "favorable",
                            "perceived_control": "high"
                        }
                    }
                },
                {
                    "id": "concerned_parent",
                    "name": "Lisa Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Ask questions about vaccine safety for children",
                    "memories": [
                        "You are Lisa Thompson, a 38-year-old mother of two",
                        "Your children are ages 8 and 12",
                        "You're generally pro-vaccine but worry about new vaccines",
                        "You've heard conflicting information about risks",
                        "You want to protect your children but also be cautious",
                        "You know other parents who are choosing not to vaccinate",
                        "You're looking for balanced, honest information"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "availability_heuristic",
                            "bias_strength": "moderate"
                        },
                        "emotion": {
                            "current_emotion": "worry",
                            "emotion_intensity": "moderate"
                        },
                        "values": {
                            "core_values": ["family_safety", "caution", "protection"]
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Community Health Discussion",
                "acting_order": "game_master_choice",
                "params": {
                    "extra_components": {
                        "grounded_variables_intro": (
                            "Track key outcomes throughout this discussion:\n"
                            "- Vaccine acceptance: Count who decides to get vaccinated\n"
                            "- Attitude shifts: Note changes in participants' stances\n"
                            "- Information quality: Track accurate vs. inaccurate claims\n"
                            "- Emotional tone: Monitor fear, hope, anger, reassurance"
                        )
                    }
                }
            },
            "llm_settings": {
                "provider": "gemini",
                "model": "gemini-2.0-flash-exp",
                "embedder_model": "all-MiniLM-L6-v2",
                "temperature": 0.85
            }
        }
    }


@router.get("/templates/nested-simulation-demo")
async def get_nested_simulation_demo_template():
    """
    Template: Nested Simulation Demo (PhoneGameMaster Pattern)

    This template demonstrates the nested simulation capability where an agent
    can run a mini-simulation as part of their decision-making process.

    Use case: An agent simulates a conversation with a friend to decide what
    to bring to a party, then uses that insight in the main simulation.
    """
    return {
        "name": "Nested Simulation Demo - Phone Call Planning",
        "description": "Demonstrates nested simulations where agents run mini-simulations to inform their decisions in the main simulation",
        "config": {
            "premise": "Alice is planning what to bring to a dinner party. She calls her friend Bob to discuss what would be good to bring.",
            "max_steps": 15,
            "shared_memories": [
                "There is a dinner party happening this weekend.",
                "Alice is deciding what to bring.",
                "She wants to call her friend Bob for advice.",
                "The host has requested guests bring something to share.",
            ],
            "agents": [
                {
                    "id": "alice",
                    "name": "Alice",
                    "prefab": "basic__Entity",
                    "goal": "Decide what to bring to the dinner party by consulting with Bob",
                    "memories": [
                        "Alice loves cooking and trying new recipes.",
                        "She wants to impress the other guests.",
                        "She's considering bringing a dessert or an appetizer.",
                        "She wants to make sure no one else is bringing the same thing.",
                    ],
                    "randomize_choices": True,
                    # Nested simulation: Alice simulates a conversation with Bob
                    "nested_simulation": {
                        "premise": "Alice calls Bob to ask what she should bring to the dinner party. Bob knows what other guests are bringing.",
                        "max_steps": 5,
                        "shared_memories": [
                            "Alice is calling Bob for advice about the dinner party.",
                            "Bob knows what other guests are planning to bring.",
                            "They are close friends who often cook together.",
                        ],
                        "agents": [
                            {
                                "id": "alice_nested",
                                "name": "Alice",
                                "prefab": "basic__Entity",
                                "goal": "Find out what would be good to bring to the party",
                                "memories": [
                                    "Alice is considering her options.",
                                    "She trusts Bob's judgment.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "bob_nested",
                                "name": "Bob",
                                "prefab": "basic__Entity",
                                "goal": "Help Alice decide what to bring",
                                "memories": [
                                    "Bob knows that Maria is bringing a main dish.",
                                    "Bob knows that Carlos is bringing drinks.",
                                    "Bob thinks a dessert would be perfect.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What did Alice learn about what to bring to the party? What did Bob say others are bringing?"
                    }
                },
                {
                    "id": "bob_main",
                    "name": "Bob",
                    "prefab": "basic__Entity",
                    "goal": "Help Alice decide what to bring to the dinner party",
                    "memories": [
                        "Bob is Alice's friend.",
                        "Bob is knowledgeable about food and parties.",
                        "Bob wants to help Alice make a good impression.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "conversation guide",
                "acting_order": "game_master_choice",
                "parameters": {}
            }
        },
        "llm_settings": {
            "provider": "gemini",
            "model": "gemini-2.0-flash-exp",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.8
        }
    }


@router.get("/templates/phishing-attack-simulation")
async def get_phishing_attack_simulation_template():
    """
    Template: Phishing Attack Simulation (Meta-Cognitive Security Analysis)

    This template demonstrates a cybersecurity tabletop exercise where security
    analysts simulate potential threat scenarios to assess phishing risk.

    Use case: A security team receives a suspicious phishing email and uses nested
    simulations to model what would happen if someone clicked the malicious link.
    Each analyst simulates the attack chain (hacker → user → IT response) to
    estimate the impact and recommend appropriate security measures.

    Educational value: Demonstrates meta-cognitive reasoning where agents simulate
    adversarial scenarios without actual risk - like a digital fire drill.
    """
    return {
        "name": "Phishing Attack Simulation - Security Team Tabletop Exercise",
        "description": "A cybersecurity tabletop exercise where analysts simulate phishing attack scenarios to assess risk and plan response. Each analyst runs a nested simulation to model the attack chain.",
        "config": {
            "premise": "A security team at a financial services company has received a suspicious email appearing to be from their CEO, requesting urgent wire transfer instructions. The team must assess whether this is a phishing attack and determine the appropriate response.",
            "max_steps": 25,
            "shared_memories": [
                "The company is a mid-sized financial services firm handling sensitive client data.",
                "A suspicious email was received from the CEO's personal email address at 2:30 AM.",
                "The email requests urgent wire transfer instructions for a 'confidential acquisition'.",
                "The CEO is currently traveling internationally and unreachable.",
                "This matches the pattern of recent CEO fraud attacks in the industry.",
                "The team needs to assess risk quickly and decide on a response strategy.",
            ],
            "agents": [
                {
                    "id": "analyst_1",
                    "name": "Sarah",
                    "prefab": "basic__Entity",
                    "goal": "Assess the phishing risk by simulating what would happen if someone clicks the link, then recommend mitigation",
                    "memories": [
                        "Sarah is a senior security analyst with 5 years of experience.",
                        "She specializes in email security and phishing analysis.",
                        "She is concerned about the financial and reputational impact of a breach.",
                        "She believes in being cautious and prefers to verify before trusting.",
                        "She wants to understand the technical details of the attack chain.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Sarah simulates what would happen if an employee clicks the phishing link. The simulation models the attacker's actions, the user's experience, and the IT security response.",
                        "max_steps": 8,
                        "shared_memories": [
                            "A user receives and clicks a malicious link in a phishing email.",
                            "The link appears to lead to a legitimate-looking login page.",
                            "The attacker is attempting to steal credentials and deploy malware.",
                            "The company has security monitoring but no MFA enforcement.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_1",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Successfully harvest credentials and establish persistence on the victim's machine",
                                "memories": [
                                    "The hacker is using a cloned login page hosted on a compromised legitimate site.",
                                    "The phishing kit includes a keylogger and credential harvester.",
                                    "If credentials are entered, the hacker will attempt to deploy ransomware within 2 hours.",
                                    "The hacker wants to move laterally to access financial systems.",
                                    "Time is critical - the attack must complete before detection.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_1",
                                "name": "Employee",
                                "prefab": "basic__Entity",
                                "goal": "Complete what appears to be an urgent request from the CEO",
                                "memories": [
                                    "The employee is tired and working late to meet deadlines.",
                                    "They respect the CEO and want to respond quickly.",
                                    "They are not particularly tech-savvy.",
                                    "They don't notice the subtle misspelling in the URL.",
                                    "They feel pressure to act on urgent requests from leadership.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "it_security_1",
                                "name": "IT Security",
                                "prefab": "basic__Entity",
                                "goal": "Detect and respond to the security incident as quickly as possible",
                                "memories": [
                                    "IT security monitors SIEM alerts and network traffic.",
                                    "They have a 24/7 security operations center.",
                                    "Response time averages 2-4 hours for initial triage.",
                                    "They can isolate infected machines and reset credentials.",
                                    "They need to determine the scope and impact of the breach.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What happened after the employee clicked the link? Did the hacker successfully steal credentials or deploy malware? How quickly did IT security detect and respond? What was the impact and cost of the incident?"
                    }
                },
                {
                    "id": "analyst_2",
                    "name": "Marcus",
                    "prefab": "basic__Entity",
                    "goal": "Assess the phishing risk by simulating the attack scenario, then recommend technical controls",
                    "memories": [
                        "Marcus is a technical security engineer with infrastructure expertise.",
                        "He focuses on implementing technical security controls.",
                        "He is concerned about gaps in the current security posture.",
                        "He believes the company needs stronger authentication mechanisms.",
                        "He wants to understand how the attack would bypass existing defenses.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Marcus simulates the attack chain with a focus on technical controls and defense mechanisms. The simulation shows where current security measures fail and how they could be improved.",
                        "max_steps": 8,
                        "shared_memories": [
                            "A phishing attack targets employees with access to financial systems.",
                            "The company has basic email filtering but no advanced threat protection.",
                            "Multi-factor authentication is available but not enforced.",
                            "Security monitoring exists but has alert fatigue and slow response times.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_2",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Bypass security controls and gain unauthorized access to financial systems",
                                "memories": [
                                    "The hacker has researched the company's security posture.",
                                    "They know that MFA is not enforced for legacy applications.",
                                    "They can bypass email filtering using techniques like HTML smuggling.",
                                    "The attack focuses on employees with elevated privileges.",
                                    "The hacker wants to establish persistent access for future exploitation.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_2",
                                "name": "Finance Manager",
                                "prefab": "basic__Entity",
                                "goal": "Process what appears to be a legitimate request from executive leadership",
                                "memories": [
                                    "The finance manager has authority to initiate wire transfers.",
                                    "They are under pressure to process time-sensitive transactions.",
                                    "They have a good working relationship with the CEO.",
                                    "They are experienced but may be fooled by sophisticated impersonation.",
                                    "They want to demonstrate responsiveness to leadership.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "it_security_2",
                                "name": "IT Security",
                                "prefab": "basic__Entity",
                                "goal": "Identify the attack and contain the threat before significant damage occurs",
                                "memories": [
                                    "IT security uses behavior analytics to detect anomalies.",
                                    "They have playbooks for incident response but they need updating.",
                                    "Communication with business stakeholders is sometimes delayed.",
                                    "They can block malicious URLs and reset compromised credentials.",
                                    "They need executive support to enforce security policies.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What technical controls failed to stop the attack? How did the hacker bypass security measures? What could have prevented or detected the attack earlier? What was the financial and operational impact?"
                    }
                },
                {
                    "id": "analyst_3",
                    "name": "Elena",
                    "prefab": "basic__Entity",
                    "goal": "Assess the phishing risk through simulation, then recommend user training and awareness measures",
                    "memories": [
                        "Elena is a security awareness and training manager.",
                        "She focuses on the human element of cybersecurity.",
                        "She believes that user behavior is the primary defense against phishing.",
                        "She is concerned about variability in security awareness across departments.",
                        "She wants to understand which users are most vulnerable and why.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Elena simulates different employee personas interacting with the phishing email to understand vulnerability patterns and effectiveness of training.",
                        "max_steps": 8,
                        "shared_memories": [
                            "Different employees have varying levels of security awareness.",
                            "Some departments receive more security training than others.",
                            "The company has conducted phishing simulations but participation is low.",
                            "Users who report suspicious emails receive positive recognition.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_3",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Exploit psychological manipulation to trick users into taking action",
                                "memories": [
                                    "The hacker uses urgency, authority, and fear tactics.",
                                    "The email creates time pressure to prevent critical thinking.",
                                    "The hacker knows which employees are likely to respond without verifying.",
                                    "They target users who recently completed training to test effectiveness.",
                                    "The attack is designed to bypass rational decision-making.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_3a",
                                "name": "New Employee",
                                "prefab": "basic__Entity",
                                "goal": "Follow what appears to be a legitimate request from leadership",
                                "memories": [
                                    "The employee started 2 months ago and completed basic security training.",
                                    "They want to prove themselves and be helpful.",
                                    "They are not familiar with the CEO's communication patterns.",
                                    "They are afraid of making mistakes or asking questions.",
                                    "They trust emails from leadership without questioning.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_3b",
                                "name": "Experienced Employee",
                                "prefab": "basic__Entity",
                                "goal": "Handle the email appropriately based on training and experience",
                                "memories": [
                                    "The employee has been with the company for 5 years.",
                                    "They have completed multiple security awareness trainings.",
                                    "They know to verify unusual requests through separate channels.",
                                    "They are familiar with the CEO's actual communication style.",
                                    "They feel comfortable reporting suspicious activity.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "Which employee was more likely to fall for the phishing attack and why? What psychological factors made them vulnerable? How effective was the security training? What additional awareness measures could have prevented the attack?"
                    }
                },
                {
                    "id": "ciso",
                    "name": "David",
                    "prefab": "basic__Entity",
                    "goal": "Synthesize the team's analysis and make a decision on how to respond to the potential phishing attack",
                    "memories": [
                        "David is the Chief Information Security Officer.",
                        "He has 15 years of cybersecurity experience.",
                        "He must balance security risk with business operations.",
                        "He reports directly to the CEO and board.",
                        "He needs to make a defensible decision with the available information.",
                        "He values the diverse perspectives of his team members.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Security Team Lead",
                "acting_order": "game_master_choice",
                "parameters": {}
            }
        },
        "llm_settings": {
            "provider": "gemini",
            "model": "gemini-2.0-flash-exp",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.8
        }
    }


@router.get("/templates/grounded-variables-demo")
async def get_grounded_variables_demo_template():
    """
    Template: Grounded Variables Demo

    This template demonstrates the grounded variables capability where the
    Game Master tracks and updates variables during the simulation.

    Use case: A resource management simulation where the GM tracks:
    - Team morale (0-100)
    - Budget remaining ($0-$10000)
    - Task completion status
    - Project health (categorical: on_track, at_risk, critical)
    """
    return {
        "name": "Grounded Variables Demo - Project Management",
        "description": "Demonstrates grounded variables tracking where the GM monitors and updates key metrics during the simulation",
        "config": {
            "premise": "A team is working on a critical software project with a tight deadline. The project manager must balance team morale, budget, and progress.",
            "max_steps": 20,
            "shared_memories": [
                "The project deadline is in 2 weeks.",
                "The initial budget is $10,000.",
                "Team morale starts at 70/100.",
                "The project is currently on track.",
                "There are 5 team members working on the project.",
            ],
            "agents": [
                {
                    "id": "manager",
                    "name": "Project Manager",
                    "prefab": "basic__Entity",
                    "goal": "Complete the project on time and within budget while keeping the team motivated",
                    "memories": [
                        "Has managed similar projects before.",
                        "Knows that overworking the team reduces morale.",
                        "Budget is running low.",
                        "Needs to make tradeoffs between speed and quality.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer_1",
                    "name": "Senior Developer",
                    "prefab": "basic__Entity",
                    "goal": "Write high-quality code and mentor junior developers",
                    "memories": [
                        "Experienced developer who cares about code quality.",
                        "Gets frustrated when rushed.",
                        "Wants the project to succeed.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer_2",
                    "name": "Junior Developer",
                    "prefab": "basic__Entity",
                    "goal": "Learn and contribute to the project",
                    "memories": [
                        "Eager to learn but needs guidance.",
                        "Willing to put in extra hours.",
                        "Looks up to the senior developer.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "project tracker",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "team_morale",
                        "variable_type": "numerical",
                        "description": "Overall team morale and satisfaction (0-100)",
                        "default_value": 70,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Changes based on workload, recognition, and setbacks"
                    },
                    {
                        "name": "budget_remaining",
                        "variable_type": "numerical",
                        "description": "Remaining project budget in dollars",
                        "default_value": 10000,
                        "min_value": 0,
                        "max_value": 10000,
                        "update_rule": "Decreases with each decision and action taken"
                    },
                    {
                        "name": "tasks_completed",
                        "variable_type": "numerical",
                        "description": "Number of tasks completed",
                        "default_value": 0,
                        "min_value": 0,
                        "max_value": 50,
                        "update_rule": "Increases when the team completes tasks"
                    },
                    {
                        "name": "project_health",
                        "variable_type": "categorical",
                        "description": "Overall project status",
                        "default_value": "on_track",
                        "allowed_values": ["on_track", "at_risk", "critical", "completed", "failed"],
                        "update_rule": "Changes based on morale, budget, and progress"
                    },
                    {
                        "name": "crisis_mode",
                        "variable_type": "boolean",
                        "description": "Whether the project is in crisis",
                        "default_value": False,
                        "update_rule": "Becomes true if budget < 2000 or morale < 30"
                    },
                    {
                        "name": "completion_percentage",
                        "variable_type": "percentage",
                        "description": "Project completion percentage",
                        "default_value": 20,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Increases as tasks are completed"
                    }
                ]
            }
        },
        "llm_settings": {
            "provider": "gemini",
            "model": "gemini-2.0-flash-exp",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.8
        }
    }


@router.get("/templates/urban-gentrification")
async def get_urban_gentrification_template():
    """
    Template: Urban Gentrification & Housing Policy (Grounded Variables in Urban Economics)

    This template demonstrates grounded variables for longitudinal urban economics research.
    It tracks key neighborhood metrics over time as different stakeholders make decisions
    about housing, development, and community preservation.

    Research applications:
    - Study the dynamics of gentrification and displacement
    - Test housing policy interventions (rent control, inclusionary zoning, community land trusts)
    - Model the trade-offs between economic development and affordability
    - Analyze how stakeholder decisions affect neighborhood evolution

    Grounded variables track:
    - Median rent ($)
    - Percentage of low-income households displaced
    - Small business closure rate
    - Community cohesion index
    - Property tax base
    - New construction units
    - Housing affordability index
    """
    return {
        "name": "Urban Gentrification - Housing Policy & Neighborhood Change",
        "description": "Longitudinal urban economics simulation tracking neighborhood metrics. Stakeholders debate development proposals while GM tracks rent, displacement, business survival, and affordability over time.",
        "config": {
            "premise": "The historically working-class neighborhood of Elmwood is facing rapid change. A tech company's nearby expansion has brought new investment and interest, but also concerns about displacement and loss of community character. The City Council is holding a series of meetings to decide on housing policies and development proposals. Stakeholders include long-term residents, housing advocates, real estate developers, small business owners, and city planners. CURRENT STATE: Median monthly rent is $1800 for a 2-bedroom. 15% of low-income households have been displaced in the past 2 years. 78% of small businesses remain open. Community cohesion index is 65/100. Property tax base is $450 million. 45 new housing units were permitted last year. 120 units are affordable to area median income earners. 35% of rental units are affordable. Rent control is NOT active. Inclusionary zoning is NOT active. Neighborhood character is currently 'transitional'. The Council will debate policies that may RENT PRICES, DISPLACE RESIDENTS, CLOSE BUSINESSES, AFFECT COMMUNITY COHESION, INCREASE PROPERTY VALUES, APPROVE NEW CONSTRUCTION, CHANGE AFFORDABILITY, and potentially ENACT RENT CONTROL or INCLUSIONARY ZONING.",
            "max_steps": 30,
            "shared_memories": [
                "Elmwood has been a working-class neighborhood for 80 years.",
                "Recent tech company expansion 2 miles away has increased housing demand.",
                "Median rent has increased 40% over the past 3 years. Current median rent is $1800.",
                "Three local businesses have closed in the last year. 78% of small businesses remain open.",
                "15% of low-income households have been displaced due to rising rents.",
                "The city has limited affordable housing funds. Only 120 affordable units exist.",
                "Community organizations are mobilizing to preserve neighborhood character (cohesion index: 65/100).",
                "Developers see profit potential in the area's transit access. Property tax base is $450 million.",
                "45 new housing units were permitted last year, but more development is being proposed.",
                "Housing affordability index is at 35% - only 35% of rental units are affordable to median income earners.",
                "Rent control policies are NOT currently active, but being debated.",
                "Inclusionary zoning (requiring affordable units in new developments) is NOT active, but being proposed.",
                "The neighborhood's character is currently 'transitional' - shifting from traditional working-class to mixed-income.",
                "Decisions at this meeting could increase median rent, displace more residents, close more businesses, reduce community cohesion, increase property values, approve more construction units, affect affordability, or enact rent control/inclusionary zoning policies.",
            ],
            "agents": [
                {
                    "id": "housing_advocate",
                    "name": "Maria Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Prevent displacement of long-term residents and preserve affordable housing. Keep median monthly rent affordable. Reduce the 15% low-income displacement rate. Protect the 78% of small businesses still open. Preserve community cohesion. Advocate for rent control and inclusionary zoning policies.",
                    "memories": [
                        "Maria is a community organizer who has lived in Elmwood for 35 years.",
                        "She runs a local non-profit focused on housing rights.",
                        "She has seen many families forced to move due to rising rents. The displacement rate is 15%.",
                        "Current median rent is $1800 - too high for many long-term residents.",
                        "She believes the community has a right to remain without displacement.",
                        "She is skeptical of developer promises about benefits.",
                        "She has data showing rent increases are outpacing wage growth.",
                        "She wants policies that protect vulnerable residents - RENT CONTROL and INCLUSIONARY ZONING.",
                        "She wants to PREVENT FURTHER DISPLACEMENT, KEEP RENTS STABLE, and CLOSE the affordability gap.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer",
                    "name": "James Chen",
                    "prefab": "basic__Entity",
                    "goal": "Develop profitable housing projects while meeting some community needs. INCREASE median monthly rent through new development. APPROVE more housing units. INCREASE property tax base. Balance profit with some affordable units. Avoid rent control policies.",
                    "memories": [
                        "James is a real estate developer with 15 years of experience.",
                        "He sees Elmwood as undervalued with great potential.",
                        "He believes new development brings jobs and economic vitality.",
                        "Current median rent of $1800 is below market potential - he wants to INCREASE RENTS.",
                        "He wants to BUILD MORE HOUSING UNITS and INCREASE PROPERTY VALUES.",
                        "He is willing to include some affordable units to get approval, but wants to MAXIMIZE PROFIT.",
                        "He thinks the neighborhood's character will evolve naturally to 'gentrified_upscale'.",
                        "He has investors expecting returns on their capital.",
                        "He wants to work with the community rather than fight them.",
                        "He opposes RENT CONTROL as it would limit his profits.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "small_business_owner",
                    "name": "Fatima Al-Hassan",
                    "prefab": "basic__Entity",
                    "goal": "Keep her small business thriving and preserve neighborhood's small business character. PREVENT further business closures. MAINTAIN the 78% small business survival rate. Keep RENTS STABLE for commercial spaces. Preserve community cohesion.",
                    "memories": [
                        "Fatima has owned a corner grocery store in Elmwood for 22 years.",
                        "Her lease is coming up for renewal and she fears a rent increase - current median rent is $1800.",
                        "She has seen two neighboring businesses close recently. Only 78% of small businesses remain open.",
                        "She worries that INCREASING RENTS will force her to CLOSE too.",
                        "Newer residents shop at different types of stores than long-term residents.",
                        "She serves both traditional and new customers.",
                        "She is worried about losing her livelihood if property values rise too fast.",
                        "She wants the neighborhood to prosper without losing its soul.",
                        "She wants policies that PREVENT BUSINESS CLOSURES and KEEP RENTS AFFORDABLE.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "city_planner",
                    "name": "David Kim",
                    "prefab": "basic__Entity",
                    "goal": "Balance economic development with housing affordability and community preservation. Manage RENT INCREASES. CONTROL DISPLACEMENT. SUPPORT BUSINESSES. BUILD MORE HOUSING. Consider RENT CONTROL and INCLUSIONARY ZONING policies. Balance property tax growth with affordability.",
                    "memories": [
                        "David is a senior city planner with expertise in housing policy.",
                        "He reports to the City Council which is divided on development issues.",
                        "He has data on housing shortages and displacement trends citywide.",
                        "Current metrics: median rent $1800, 15% displaced, 78% business survival, 65/100 community cohesion.",
                        "He knows the city needs more housing units but also more affordable units.",
                        "He is considering policy options: RENT CONTROL, INCLUSIONARY ZONING, density bonuses.",
                        "He must balance INCREASING PROPERTY TAX BASE with MAINTAINING AFFORDABILITY.",
                        "He wants evidence-based solutions that can actually be implemented.",
                        "He has limited budget for affordable housing subsidies.",
                        "He may need to APPROVE DEVELOPMENT or ENACT CONTROLS depending on Council decisions.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "new_resident",
                    "name": "Alex Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Find affordable housing while being a good neighbor to the existing community",
                    "memories": [
                        "Alex recently moved to Elmwood for lower rent and neighborhood character.",
                        "They work remotely for a tech company and have a flexible income.",
                        "They like the local businesses and community feel of the neighborhood.",
                        "They are aware of concerns about gentrification.",
                        "They want to integrate respectfully with long-term residents.",
                        "They support affordable housing but also want their investment to grow.",
                        "They represent the wave of new residents changing the neighborhood.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "landlord",
                    "name": "Robert Schwartz",
                    "prefab": "basic__Entity",
                    "goal": "Maximize rental income while maintaining good tenant relationships. INCREASE RENTS toward market rates. Balance profit with tenant retention. Navigate potential RENT CONTROL policies. Avoid DISPLACING long-term tenants if possible.",
                    "memories": [
                        "Robert owns a small apartment building (6 units) in Elmwood.",
                        "He inherited the building from his parents 20 years ago.",
                        "His current rents are below market rate. Median rent is $1800, but market could be $2200+.",
                        "He wants to INCREASE HIS RENTAL INCOME to match rising property values.",
                        "His expenses (taxes, maintenance, insurance) have been increasing.",
                        "He feels pressure to raise rents to market levels - could INCREASE MEDIAN RENT for the neighborhood.",
                        "He has relationships with many of his long-term tenants.",
                        "He is conflicted between profit and treating tenants fairly.",
                        "He is aware of RENT CONTROL proposals that would LIMIT RENT INCREASES.",
                        "He worries about DISPLACING tenants but needs to cover rising costs.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "City Council Moderator",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "median_monthly_rent",
                        "variable_type": "numerical",
                        "description": "Median monthly rent for a 2-bedroom apartment in Elmwood",
                        "default_value": 1800,
                        "min_value": 800,
                        "max_value": 5000,
                        "update_rule": "Increases with development approvals, decreases with rent control/affordable housing policies"
                    },
                    {
                        "name": "low_income_displacement_rate",
                        "variable_type": "percentage",
                        "description": "Percentage of households earning <50% area median income that have been displaced from Elmwood in the past 2 years",
                        "default_value": 15,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Increases with rising rents, decreases with tenant protection policies"
                    },
                    {
                        "name": "small_business_survival_rate",
                        "variable_type": "percentage",
                        "description": "Percentage of small businesses (locally-owned, <10 employees) that have remained open",
                        "default_value": 78,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rising rents and demographic shifts, increases with business support programs"
                    },
                    {
                        "name": "community_cohesion_index",
                        "variable_type": "numerical",
                        "description": "Measured sense of community belonging and neighborly interaction (0-100 scale)",
                        "default_value": 65,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rapid demographic change, increases with community-building initiatives"
                    },
                    {
                        "name": "property_tax_base",
                        "variable_type": "numerical",
                        "description": "Total assessed property value in millions (determines city revenue for services)",
                        "default_value": 450,
                        "min_value": 300,
                        "max_value": 1500,
                        "update_rule": "Increases with new development and rising property values"
                    },
                    {
                        "name": "new_housing_units_permitted",
                        "variable_type": "numerical",
                        "description": "Number of new housing units approved for construction in the past year",
                        "default_value": 45,
                        "min_value": 0,
                        "max_value": 500,
                        "update_rule": "Increases when development proposals are approved"
                    },
                    {
                        "name": "affordable_housing_units",
                        "variable_type": "numerical",
                        "description": "Number of units affordable to households earning <80% area median income",
                        "default_value": 120,
                        "min_value": 0,
                        "max_value": 1000,
                        "update_rule": "Increases with inclusionary zoning or subsidies, decreases with market-rate conversions"
                    },
                    {
                        "name": "housing_affordability_index",
                        "variable_type": "percentage",
                        "description": "Percentage of rental units affordable to households earning area median income",
                        "default_value": 35,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rent increases, increases with affordable housing policies"
                    },
                    {
                        "name": "rent_control_active",
                        "variable_type": "boolean",
                        "description": "Whether rent control/stabilization policies are in effect",
                        "default_value": False,
                        "update_rule": "Becomes true if City Council enacts rent control policy"
                    },
                    {
                        "name": "inclusionary_zoning_active",
                        "variable_type": "boolean",
                        "description": "Whether developers must include affordable units (e.g., 20% of new units)",
                        "default_value": False,
                        "update_rule": "Becomes true if City Council enacts inclusionary zoning requirement"
                    },
                    {
                        "name": "neighborhood_character",
                        "variable_type": "categorical",
                        "description": "Overall character and identity of the neighborhood",
                        "default_value": "transitional",
                        "allowed_values": [
                            "traditional_working_class",
                            "transitional",
                            "mixed_income_stable",
                            "gentrified_upscale",
                            "disinvested_declining"
                        ],
                        "update_rule": "Changes based on combination of rent, displacement, and business variables"
                    }
                ]
            }
        },
        "llm_settings": {
            "provider": "gemini",
            "model": "gemini-2.0-flash-exp",
            "embedder_model": "all-MiniLM-L6-v2",
            "temperature": 0.8
        }
    }


@router.get("/recent")
async def get_recent_simulations(limit: int = 20):
    """Get list of recent simulation logs."""
    import os
    from pathlib import Path

    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []

    # Get all HTML files in logs directory
    log_files = []
    for file_path in logs_dir.glob("*.html"):
        try:
            stat = file_path.stat()
            log_files.append({
                "filename": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime
            })
        except Exception:
            continue

    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x["modified"], reverse=True)

    # Return limited number of results
    return log_files[:limit]


@router.get("/logs/{filename}")
async def get_simulation_log(filename: str):
    """Get a specific simulation log by filename."""
    import os
    from pathlib import Path

    # Security: Ensure filename doesn't contain path traversal
    safe_filename = os.path.basename(filename)
    log_path = Path("logs") / safe_filename

    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        stat = log_path.stat()
        return {
            "filename": safe_filename,
            "path": str(log_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "html_content": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")


@router.get("/logs/{filename}/analytics")
async def get_simulation_analytics(filename: str):
    """Get analytics and statistics for a simulation log."""
    import os
    import re
    import json
    from pathlib import Path
    from bs4 import BeautifulSoup

    # Security: Ensure filename doesn't contain path traversal
    safe_filename = os.path.basename(filename)
    log_path = Path("logs") / safe_filename

    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")

    # Try to load metadata file first (contains agent goals, config info)
    metadata_path = log_path.with_suffix('.metadata.json')
    agent_metadata = {}
    premise_from_metadata = ""
    gm_prefab = None
    game_theoretic_actions = {}  # Store game-theoretic action data for later use

    # NEW: Feature detection flags
    has_nested_sims = False
    has_grounded_variables = False
    has_components = False
    nested_sim_data = {}
    grounded_variables_data = {}
    component_data = {}

    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                premise_from_metadata = metadata.get("premise", "")
                gm_prefab = metadata.get("game_master", {}).get("prefab")

                # NEW: Detect nested simulations
                for agent in metadata.get("agents", []):
                    if agent.get("nested_simulation"):
                        has_nested_sims = True
                        # Structure the data as expected by frontend
                        nested_sim_data[agent["name"]] = {
                            "config": agent["nested_simulation"],
                            "result_summary": "",  # TODO: Extract from HTML if available
                            "found": True
                        }
                        print(f"[DEBUG] Found nested simulation for agent {agent['name']}")

                # NEW: Detect grounded variables
                if metadata.get("game_master", {}).get("grounded_variables"):
                    has_grounded_variables = True
                    grounded_variables_data["variables"] = metadata["game_master"]["grounded_variables"]
                    print(f"[DEBUG] Found {len(grounded_variables_data['variables'])} grounded variables")

                # NEW: Detect components
                for agent in metadata.get("agents", []):
                    if agent.get("components"):
                        has_components = True
                        component_data[agent["name"]] = agent["components"]
                        print(f"[DEBUG] Found components for agent {agent['name']}: {list(agent['components'].keys())}")

                # Build a map of agent name -> metadata
                for agent in metadata.get("agents", []):
                    agent_metadata[agent["name"]] = {
                        "goal": agent.get("goal", ""),
                        "prefab": agent.get("prefab", ""),
                        "memories_count": agent.get("memories_count", 0)
                    }
                print(f"[DEBUG] Loaded metadata for {len(agent_metadata)} agents")

                # Check for game-theoretic action data in metadata
                if "game_theoretic" in metadata:
                    gt_data = metadata["game_theoretic"]
                    actions_by_player = gt_data.get("actions_by_player", {})
                    # Convert to action counts for easy lookup, but only if not empty
                    if actions_by_player:  # Only use if actually has data
                        for player_name, actions in actions_by_player.items():
                            game_theoretic_actions[player_name] = len(actions)
                        print(f"[DEBUG] Loaded game-theoretic action data: {game_theoretic_actions}")
                    else:
                        print(f"[DEBUG] Game-theoretic metadata exists but empty, will use HTML extraction")
        except Exception as e:
            print(f"[WARNING] Failed to load metadata: {e}")

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Get text content once for efficiency (expensive operation for large HTML)
        soup_text = soup.get_text()
        soup_words = soup_text.split()

        # Extract basic statistics
        analytics = {
            "filename": safe_filename,
            "file_size": log_path.stat().st_size,
            "modified": log_path.stat().st_mtime,
            "total_steps": 0,
            "agents": [],
            "agent_actions": {},
            "total_observations": 0,
            "interactions": [],
            "timeline": [],
            "word_count": len(soup_words),
            "character_count": len(soup_text),
            "premise": premise_from_metadata,  # Use premise from metadata
            "gm_prefab": gm_prefab,  # Include game master prefab type
            # NEW: Feature detection flags
            "has_nested_sims": has_nested_sims,
            "has_grounded_variables": has_grounded_variables,
            "has_components": has_components,
            # NEW: Feature-specific data (populated from metadata)
            "nested_simulations": nested_sim_data,
            "grounded_variables": grounded_variables_data.get("variables", []),
            "components": component_data
        }

        # Find all step indicators (they typically contain "Step X")
        step_pattern = re.compile(r'Step\s+(\d+)', re.IGNORECASE)
        for element in soup.find_all(string=step_pattern):
            match = step_pattern.search(str(element))
            if match:
                step_num = int(match.group(1))
                analytics["total_steps"] = max(analytics["total_steps"], step_num)

        # Extract agent names from tab buttons
        # Exclude non-agent tabs like Game Master logs and memories
        excluded_tabs = {'Game Master log', 'Game Master Memories', 'Simulation Log'}
        tab_buttons = soup.find_all(['button', 'div'], class_=re.compile(r'tablink|tablinks'))
        for btn in tab_buttons:
            text = btn.get_text(strip=True)
            # Only include actual agent tabs (exclude Game Master tabs)
            if text and text not in excluded_tabs and not text.startswith('Game Master'):
                if text not in analytics["agents"]:
                    analytics["agents"].append(text)
                    analytics["agent_actions"][text] = 0

        # If game-theoretic data was loaded from metadata, use it for action counts
        if game_theoretic_actions and gm_prefab == 'game_theoretic_and_dramaturgic__GameMaster':
            for player_name, action_count in game_theoretic_actions.items():
                if player_name in analytics["agent_actions"]:
                    analytics["agent_actions"][player_name] = action_count
                    print(f"[DEBUG] Set {player_name} actions to {action_count} from game-theoretic metadata")
            print(f"[DEBUG] Applied game-theoretic action data for {len(game_theoretic_actions)} players")

        # Count actions per agent by finding actual agent actions (with "Action:" label)
        # Actions are in the Game Master log tab, organized by agent entity
        game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
        if game_master_log:
            # Find all sections with entity information (e.g., "Entity [Agent R]")
            for agent in analytics["agents"]:
                # Find all <b> tags containing "Entity [agent_name]"
                entity_pattern = re.compile(rf'Entity\s+\[{re.escape(agent)}\]', re.IGNORECASE)
                entity_tags = game_master_log.find_all('b', string=entity_pattern)

                # Use a set to track unique action texts and avoid counting duplicates
                seen_actions = set()

                # For each entity tag, find the associated action
                # Structure: <details><b>Entity [name]</b><li>...<b>__act__</b><li><details><summary>Action: ...</summary>
                for entity_tag in entity_tags:
                    # The entity <b> tag and the agent <li> are siblings in a <details>
                    # Find the parent <details>
                    parent_details = entity_tag.find_parent('details')
                    if parent_details:
                        # Find all <li> children of this <details>
                        all_li = parent_details.find_all('li', recursive=False)

                        # The first <li> after Entity should contain the agent info
                        # Look for <li> that contains <summary>Action:
                        for li in all_li:
                            summaries = li.find_all('summary')
                            for summary in summaries:
                                summary_text = summary.get_text(strip=True)
                                if summary_text.startswith('Action:'):
                                    # Skip workflow examples
                                    if any(keyword in summary_text.lower() for keyword in ['workflow examples', 'exercise 1', 'exercise 2']):
                                        continue
                                    # Skip game master termination actions
                                    if 'terminate' in summary_text.lower() or 'game.*finished' in summary_text.lower():
                                        continue
                                    # Use first 100 chars as unique identifier
                                    action_id = summary_text[:100]
                                    if action_id not in seen_actions:
                                        seen_actions.add(action_id)

                analytics["agent_actions"][agent] = len(seen_actions)
        else:
            # Fallback: Search in entire document for actions with "Action:" label
            for agent in analytics["agents"]:
                # Find Entity tag followed by __act__ with Action: label
                entity_pattern = re.compile(
                    rf'Entity\s+\[{re.escape(agent)}\].*?__act__.*?Action:',
                    re.IGNORECASE | re.DOTALL
                )
                matches = soup.find_all(string=entity_pattern)
                analytics["agent_actions"][agent] = len(matches)

        # Extract observations (typically in [observation] tags)
        observations = soup.find_all(string=re.compile(r'\[observation\]', re.IGNORECASE))
        analytics["total_observations"] = len(observations)

        # Build timeline from step events
        # Use a set to track seen steps and avoid duplicates from nested <details> elements
        seen_steps = set()
        details_elements = soup.find_all('details')
        for detail in details_elements:
            # Skip nested <details> elements (those that are descendants of another <details>)
            if detail.find_parent('details'):
                continue

            summary = detail.find('summary')
            if summary:
                summary_text = summary.get_text(strip=True)
                # Check if this is a step event
                step_match = re.search(r'Step\s+(\d+)', summary_text, re.IGNORECASE)
                if step_match:
                    step_num = int(step_match.group(1))
                    # Only add if we haven't seen this step number yet
                    if step_num not in seen_steps:
                        seen_steps.add(step_num)

                        # Remove redundant prefix like "Step 1 City Council Moderator --- Event: "
                        # to save space and avoid repetition
                        description = summary_text
                        prefix_pattern = re.compile(r'Step\s+\d+\s+.*?---\s*Event:\s*', re.IGNORECASE)
                        description = prefix_pattern.sub('', description).strip()

                        analytics["timeline"].append({
                            "step": step_num,
                            "description": description,  # Full description without redundant prefix
                            "type": "step"
                        })

        # Sort timeline by step number
        analytics["timeline"].sort(key=lambda x: x["step"])

        # Extract agent-specific actions and goals for detailed analysis
        analytics["agent_details"] = {}

        for agent in analytics["agents"]:
            agent_details = {
                "actions": [],
                "goal": "",
                "memories": []
            }

            # USE METADATA FOR GOAL - Much more reliable than HTML parsing!
            if agent in agent_metadata and agent_metadata[agent].get("goal"):
                agent_details["goal"] = agent_metadata[agent]["goal"]
                print(f"[DEBUG] Agent '{agent}': using goal from metadata: {agent_details['goal'][:100]}...")
            else:
                # Fallback: Try to extract goal from HTML (old method)
                print(f"[DEBUG] Agent '{agent}': no goal in metadata, trying HTML extraction")

                # Only try HTML extraction if we haven't found a goal yet
                game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
                if game_master_log:
                    # FAST GOAL EXTRACTION: Use regex on raw HTML string (much faster than BeautifulSoup traversal)
                    # Pattern: <b><ul>Entity [AGENT_NAME]</ul></b> ... <b><ul>Goal</ul></b> ... <b><ul>Value</ul></b><li>GOAL_TEXT</li>
                    # Note: BeautifulSoup converts <b><ul>Entity</b> to <b><ul>Entity</ul></b>
                    game_master_html = str(game_master_log)
                    entity_pattern = rf'<b><ul>Entity\s+\[{re.escape(agent)}\]</ul></b>'

                    # Search for entity sections and extract goal value
                    entity_matches = list(re.finditer(entity_pattern, game_master_html, re.IGNORECASE))
                    if entity_matches:
                        for match in entity_matches:
                            # Look ahead for the Goal/Value pattern within the next 10000 characters
                            section_start = match.start()
                            section_end = min(section_start + 10000, len(game_master_html))
                            section = game_master_html[section_start:section_end]

                            # Look for: <b><ul>Goal</ul></b> followed by <b><ul>Value</ul></b><li>TEXT
                            goal_pattern = r'<b><ul>Goal</ul></b>.*?<b><ul>Value</ul></b><li>([^<]+)</li>'
                            goal_match = re.search(goal_pattern, section, re.DOTALL | re.IGNORECASE)

                            if goal_match:
                                goal = goal_match.group(1).strip()
                                if goal and len(goal) > 10:
                                    agent_details["goal"] = goal
                                    print(f"[DEBUG] Agent '{agent}': found goal via regex: {goal[:100]}...")
                                    break

            analytics["agent_details"][agent] = agent_details

        # Extract actions for each agent from Game Master log
        game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
        if game_master_log:
            for agent in analytics["agents"]:
                agent_details = analytics["agent_details"][agent]

                print(f"[DEBUG] Agent '{agent}': extracting actions from Game Master log")

                # PRIMARY METHOD: Extract actions from event descriptions
                # This is more reliable than parsing complex HTML structures
                print(f"[DEBUG] Agent '{agent}': extracting actions from event descriptions")

                # Track seen (step, action) pairs to avoid true duplicates
                # Same event may appear multiple times in nested sections
                seen_combinations = set()

                # Find all event summaries in Game Master log
                event_summaries = game_master_log.find_all('summary')
                for summary in event_summaries:
                    # Get the summary as HTML string and decode HTML entities
                    summary_html = str(summary)

                    # ONLY look at summaries that contain "Putative event to resolve:"
                    # This filters out all other component summaries (Goal, Instructions, etc.)
                    if 'putative event to resolve' not in summary_html.lower():
                        continue

                    # Extract step number first

                # SECONDARY METHOD: If no actions found in events, try entity tags
                if len(agent_details["actions"]) == 0:
                    print(f"[DEBUG] Agent '{agent}': no actions in events, trying entity tag extraction")
                    entity_pattern_bs = re.compile(rf'Entity\s+\[{re.escape(agent)}\]', re.IGNORECASE)
                    entity_tags = game_master_log.find_all('b', string=entity_pattern_bs)
                    print(f"[DEBUG] Agent '{agent}': found {len(entity_tags)} entity tags for action extraction")

                    # Track seen __act__ tags to avoid counting duplicates from nested <details>
                    seen_act_tags = set()

                    for entity_tag in entity_tags:
                        # Get the container for Entity [Agent Name]
                        # The structure varies across templates:
                        # 1. <li><details><ul><b>Entity [Agent]</b>...<b>__act__</b>...</details></li>  (State Formation)
                        # 2. <ul><b>Entity [Agent]</b>...</ul>  (original format)
                        # The key is that __act__ tags for the same agent are in the same parent <li>

                        # First try to find the parent <li> that contains both Entity and __act__
                        parent_li = entity_tag.find_parent('li')
                        act_b_tags = []

                        if parent_li:
                            # Look for __act__ tags within this same <li>
                            # Filter to only top-level __act__ tags (not nested in another <details>)
                            # Need to search HTML string because __act__ is in <ul> within <b>: <b><ul>__act__</ul></b>
                            all_b_tags = parent_li.find_all('b')
                            act_pattern = re.compile(r'__act__', re.IGNORECASE)
                            all_act_tags = [b for b in all_b_tags if act_pattern.search(str(b))]
                            for act_tag in all_act_tags:
                                # Skip if this __act__ is nested within a <details> that has another __act__
                                parent_details = act_tag.find_parent('details')
                                if parent_details:
                                    # Count how many __act__ tags are in this details element
                                    all_b_in_details = parent_details.find_all('b')
                                    acts_in_details = [b for b in all_b_in_details if act_pattern.search(str(b))]
                                    if len(acts_in_details) > 1:
                                        # This __act__ is in a nested details, skip it
                                        continue
                                act_b_tags.append(act_tag)
                            print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in parent li (filtered)")

                        # Fallback to original logic if no tags found in <li>
                        if not act_b_tags:
                            # For State Formation template, entity tag and __act__ tags are siblings in <details>
                            parent_container = entity_tag.find_parent('details')

                            if parent_container:
                                # Find all __act__ tags in the same <details> section
                                # Note: can't use string= with regex because __act__ tags have <ul> children
                                all_b_tags = parent_container.find_all('b')
                                act_pattern = re.compile(r'__act__', re.IGNORECASE)
                                all_act_b_tags = [b for b in all_b_tags if act_pattern.search(str(b))]

                                # Filter to only top-level __act__ tags
                                for act_tag in all_act_b_tags:
                                    # Use id as a unique identifier for the tag
                                    tag_id = id(act_tag)
                                    if tag_id not in seen_act_tags:
                                        # Check if this is in a nested <details>
                                        parent_details = act_tag.find_parent('details')
                                        # Only skip if the nested details is NOT within parent_container
                                        # (i.e., it's from a different step or section)
                                        if parent_details and parent_details != parent_container:
                                            # Check if parent_details is a descendant of parent_container
                                            # If it is, it's still part of the same step, so include it
                                            is_descendant = parent_container in parent_details.find_parents('details')
                                            if not is_descendant:
                                                # This is in a different step/section, skip
                                                seen_act_tags.add(tag_id)
                                                continue
                                        act_b_tags.append(act_tag)
                                        seen_act_tags.add(tag_id)

                                print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in details container (filtered)")

                        for act_tag in act_b_tags:
                            action_text = None  # Initialize for this iteration
                            act_section = act_tag.find_parent(['li', 'ul', 'details'])
                            if act_section:
                                # Skip game master __act__ tags (they answer "Is the game finished?" questions)
                                # Game master actions have Action Spec like "Is the game/simulation finished?"
                                action_spec_tag = act_section.find('b', string=re.compile(r'Action Spec', re.IGNORECASE))
                                if action_spec_tag:
                                    action_spec_text = action_spec_tag.get_text(strip=True)
                                    if 'finished' in action_spec_text.lower() or 'simulation' in action_spec_text.lower():
                                        print(f"[DEBUG] Agent '{agent}': skipping game master __act__ tag (Action Spec: {action_spec_text})")
                                        continue

                                # Look for action text in summary or in Value li
                                # Structure: <b>__act__</b><li><details><summary>Action: TEXT</summary>...
                                # NOTE: There may be multiple summaries in the section - we need the one starting with "Action:"
                                all_summaries = act_section.find_all('summary')
                                target_summary = None

                                for summary in all_summaries:
                                    summary_text = summary.get_text(strip=True)
                                    # Skip non-action summaries (Goal, Instructions, etc.)
                                    if summary_text.startswith('Action:'):
                                        # Skip workflow examples
                                        if any(keyword in summary_text.lower() for keyword in ['workflow examples', 'exercise 1', 'exercise 2', 'example exercises']):
                                            continue
                                        target_summary = summary
                                        break

                                if target_summary:
                                    action_text = target_summary.get_text(strip=True)
                                    # Remove "Action:" prefix if present
                                    action_text = re.sub(r'^Action:\s*', '', action_text, flags=re.IGNORECASE)
                                    print(f"[DEBUG] Agent '{agent}': extracted action from summary, length={len(action_text)}")
                                else:
                                    # Try to find a Value ul that contains the action text
                                    value_tags_in_act = act_section.find_all('b', string=re.compile(r'Value', re.IGNORECASE))
                                    value_tags_in_act = [tag for tag in value_tags_in_act if re.match(r'^\s*<br\s*/?>\s*Value\s*$|^\s*Value\s*$', str(tag), re.IGNORECASE)]
                                    value_tag = value_tags_in_act[0] if value_tags_in_act else None
                                    if value_tag:
                                        value_ul = value_tag.find_parent('ul')
                                        if value_ul:
                                            value_lis = value_ul.find_all('li', recursive=False)
                                            for li in value_lis:
                                                # Skip if this li contains the Value <b> tag
                                                value_b_in_li = li.find_all('b', string=re.compile(r'Value', re.IGNORECASE))
                                                value_b_in_li = [b for b in value_b_in_li if re.match(r'^\s*<br\s*/?>\s*Value\s*$|^\s*Value\s*$', str(b), re.IGNORECASE)]
                                                if value_b_in_li:
                                                    continue
                                                # Get direct text content only
                                                texts = []
                                                for child in li.children:
                                                    if not hasattr(child, 'name'):
                                                        text = str(child).strip()
                                                        if text:
                                                            texts.append(text)
                                                action_text = ' '.join(texts).strip()
                                                if action_text:
                                                    print(f"[DEBUG] Agent '{agent}': extracted action from value li, length={len(action_text)}")
                                                    break

                                # Extract step number if available
                                step_match = re.search(r'Step\s+(\d+)', str(act_section.find_parent('details')), re.IGNORECASE)
                                step_num = int(step_match.group(1)) if step_match else None

                                if action_text:
                                    # Minimum length check only for non-game-theoretic actions
                                    # Game-theoretic actions can be short (e.g., "COOPERATE", "DEFECT", "BUY", "SELL")
                                    # But skip very short responses like "Yes"/"No" which are game master answers
                                    is_short_response = action_text.strip() in ['Yes', 'No', 'yes', 'no']
                                    is_meaningful_action = len(action_text) >= 3 or not is_short_response

                                    if is_meaningful_action:
                                        agent_details["actions"].append({
                                            "step": step_num,
                                            "text": action_text  # Full action text
                                        })
                                        print(f"[DEBUG] Agent '{agent}': added action (step={step_num}), total actions={len(agent_details['actions'])}")
                                    else:
                                        print(f"[DEBUG] Agent '{agent}': skipping short response: '{action_text}'")
                                    action_text = None  # Reset for next iteration

                # TERTIARY METHOD: Regex fallback for game-theoretic actions
                # Looks for "Action: COOPERATE" pattern anywhere in game master log
                # Works for ANY action type (COOPERATE/DEFECT, BUY/SELL/HOLD, etc.)
                print(f"[DEBUG] Agent '{agent}': regex fallback check - actions count={len(agent_details['actions'])}, gm_prefab={gm_prefab}")

                # FUTURE: Detection for other game master types (interviewer, dialogic)
                # These formats may use Q&A or dialogue turns instead of __act__ tags
                # Current implementation will gracefully fall back to event extraction
                # if gm_prefab in ['interviewer__GameMaster', 'dialogic__GameMaster']:
                #     print(f"[DEBUG] Agent '{agent}': {gm_prefab} detected - using dialogue/Q&A extraction")
                #     # TODO: Add interviewer/dialogic-specific extraction logic here

                if len(agent_details["actions"]) == 0 and gm_prefab == 'game_theoretic_and_dramaturgic__GameMaster':
                    print(f"[DEBUG] Agent '{agent}': trying regex fallback for game-theoretic actions")
                    gm_log_html = str(game_master_log)

                    # Robust pattern: Entity [Agent] ... __act__ ... Action: ACTION
                    # Handles:
                    # - Single words: COOPERATE, DEFECT, BUY, SELL, HOLD
                    # - Multi words: ATTACK BASE, GO TO SHOP, MOVE FORWARD
                    # - Case variations: COOPERATE, Cooperate, cooperate
                    # - BeautifulSoup tag transformations
                    # Note: BeautifulSoup may convert <b><ul>__act__</b> to <b><ul>__act__</ul></b>
                    entity_pattern = rf'Entity\s+\[{re.escape(agent)}\].*?__act__.*?<summary>\s*Action:\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)\s*</summary>'
                    entity_matches = re.findall(entity_pattern, gm_log_html, re.DOTALL | re.IGNORECASE)

                    for match in entity_matches:
                        action = match.strip()
                        # Filter out game master responses, preserve all agent actions
                        if action and action.upper() not in ['YES', 'NO']:
                            agent_details["actions"].append({
                                "step": None,
                                "text": action
                            })
                    print(f"[DEBUG] Agent '{agent}': regex fallback found {len(entity_matches)} actions: {entity_matches}")

                # FALLBACK: If no entity tags found, try extracting from event descriptions
                # This handles cases like GLM-generated HTML where some agents don't have entity sections
                if len(entity_tags) == 0 and len(agent_details["actions"]) == 0:
                    print(f"[DEBUG] Agent '{agent}': no entity tags found, trying fallback extraction from events")

                    # Track seen actions to avoid duplicates
                    seen_actions = set()
                    seen_steps = set()

                    # Find all summaries, but filter to only top-level step events
                    all_summaries = game_master_log.find_all('summary')
                    for summary in all_summaries:
                        # Skip summaries that are inside another <details> (nested)
                        parent_details = summary.find_parent('details')
                        if parent_details and parent_details.find_parent('details'):
                            continue

                        summary_text = summary.get_text()

                        # Only process summaries that start with "Step X" (top-level events)
                        if not re.search(r'^Step\s+\d+', summary_text, re.IGNORECASE):
                            continue

                        # Check if this event mentions the agent
                        if agent.lower() in summary_text.lower():
                            # Extract step number
                            step_match = re.search(r'Step\s+(\d+)', summary_text, re.IGNORECASE)
                            step_num = int(step_match.group(1)) if step_match else None

                            # Skip if we've already processed this step
                            if step_num is not None and step_num in seen_steps:
                                continue
                            if step_num is not None:
                                seen_steps.add(step_num)

                            # Extract the action description more intelligently
                            # Look for the narrative description that mentions the agent
                            lines = summary_text.split('\n')
                            for line in lines:
                                if agent.lower() in line.lower():
                                    # Clean up the line
                                    action_text = line.strip()
                                    # Remove common prefixes and markdown
                                    action_text = re.sub(r'^\s*(Step\s+\d+\s+)?(?:UN\s+Mediator\s+---\s+)?Event:\s*', '', action_text, flags=re.IGNORECASE)
                                    action_text = re.sub(r'^\s*Here is the rewritten event focusing on.*?:\s*', '', action_text, flags=re.IGNORECASE)
                                    action_text = re.sub(r'^\*\*', '', action_text)  # Remove bold markdown
                                    action_text = action_text.strip()

                                    # Remove the agent name from the beginning if present
                                    action_text = re.sub(rf'^{re.escape(agent)}(?:,\s+[^,]+)?\s+', '', action_text, flags=re.IGNORECASE)
                                    action_text = action_text.strip()

                                    # Create action ID for deduplication
                                    action_id = f"{step_num}:{action_text[:100]}"

                                    if len(action_text) > 50 and action_id not in seen_actions:  # Minimum length check
                                        seen_actions.add(action_id)
                                        agent_details["actions"].append({
                                            "step": step_num,
                                            "text": action_text  # Full action text
                                        })
                                        print(f"[DEBUG] Agent '{agent}': added fallback action (step={step_num}), total actions={len(agent_details['actions'])}")
                                        break  # Only take one action per event

                # FALLBACK: If no entity tags found, also try to extract goal from events
                if len(entity_tags) == 0 and not agent_details["goal"]:
                    print(f"[DEBUG] Agent '{agent}': no entity tags found, trying fallback goal extraction from events")

                    # Look for goal-like statements in event descriptions
                    event_summaries = game_master_log.find_all('summary')
                    for summary in event_summaries:
                        summary_text = summary.get_text()

                        # Check if this event mentions the agent and goal-related keywords
                        if agent.lower() in summary_text.lower():
                            # Look for sentences that might indicate a goal
                            # Patterns like "agent wants to...", "agent aims to...", "agent's goal is..."
                            goal_patterns = [
                                rf'{re.escape(agent)}(?:\s+\w+)*\s+(?:wants? to|aims? to|seeks? to|tries? to|hope(?:s|d)? to)\s+([^.!?]+)',
                                rf'{re.escape(agent)}[\'s]*\s+goal\s+(?:is|:)\s+([^.!?]+)',
                                rf'(?:to|for)\s+(?:achieve|secure|obtain|get|reach)[^.!]*{re.escape(agent)}',
                            ]

                            for pattern in goal_patterns:
                                goal_match = re.search(pattern, summary_text, re.IGNORECASE)
                                if goal_match:
                                    potential_goal = goal_match.group(1).strip()
                                    if len(potential_goal) > 10 and len(potential_goal) < 200:
                                        agent_details["goal"] = potential_goal
                                        print(f"[DEBUG] Agent '{agent}': found fallback goal from event: {agent_details['goal'][:100]}...")
                                        break

                            if agent_details["goal"]:
                                break

                    # If still no goal, set a placeholder based on agent name
                    if not agent_details["goal"]:
                        agent_details["goal"] = f"Goal not explicitly stated in simulation logs"
                        print(f"[DEBUG] Agent '{agent}': using placeholder goal")

                # Only extract from agent tab if we didn't find goal in Game Master log
                if not agent_details["goal"] or agent_details["goal"] == "Goal not explicitly stated in simulation logs":
                    agent_tab = soup.find('div', id=re.compile(re.escape(agent), re.IGNORECASE))
                    if agent_tab:
                        tab_text = agent_tab.get_text(strip=True)
                        print(f"[DEBUG] Agent '{agent}': trying to extract goal from agent tab (tab_text_length={len(tab_text)})")

                        # Print first 500 chars of tab text for debugging
                        print(f"[DEBUG] Agent '{agent}': tab text preview: {tab_text[:500]}...")

                        # Try to extract goal (usually appears early in the tab)
                        # Look for patterns like "goal:", "objective:", "aim:"
                        goal_patterns = [
                            r'(?:goal|objective|aim|purpose)[:\s]+([^.!?]*[.!?])',
                            r'(?:your goal is to|you aim to|you want to)[:\s]+([^.!?]*[.!?])',
                        ]
                        for i, pattern in enumerate(goal_patterns):
                            goal_match = re.search(pattern, tab_text, re.IGNORECASE)
                            if goal_match:
                                agent_details["goal"] = goal_match.group(1).strip()
                                print(f"[DEBUG] Agent '{agent}': found goal using pattern {i+1}: {agent_details['goal'][:100]}...")
                                break
                        if not agent_details["goal"] or agent_details["goal"] == "Goal not explicitly stated in simulation logs":
                            print(f"[DEBUG] Agent '{agent}': no goal found in agent tab using patterns")
                    else:
                        print(f"[DEBUG] Agent '{agent}': no agent tab found")

                        # Try to find ANY tab that might contain this agent's information
                        all_tabs = soup.find_all('div', id=True)
                        print(f"[DEBUG] Agent '{agent}': searching through {len(all_tabs)} total tabs")
                        for tab in all_tabs[:5]:  # Check first 5 tabs
                            tab_id = tab.get('id', '')
                            print(f"[DEBUG] Agent '{agent}': checking tab '{tab_id}'")
                            if agent.lower() in tab_id.lower() or 'entity' in tab_id.lower() or 'agent' in tab_id.lower():
                                tab_preview = tab.get_text(strip=True)[:200]
                                print(f"[DEBUG] Agent '{agent}': tab '{tab_id}' preview: {tab_preview}...")

                # Extract memories from agent's own tab (separate from goal extraction)
                agent_tab = soup.find('div', id=re.compile(re.escape(agent), re.IGNORECASE))
                if agent_tab:
                    tab_text = agent_tab.get_text(strip=True)

                    # Extract memories (often listed as bullet points or numbered items)
                    # Look for patterns like "You are...", "You have...", etc.
                    memory_lines = []
                    lines = tab_text.split('\n')
                    for line in lines[:50]:  # Check first 50 lines
                        line_clean = line.strip()
                        # Patterns that indicate memories/context
                        if any(pattern in line_clean.lower() for pattern in [
                            'you are', 'you have', 'you feel', 'you believe',
                            'you know', 'you remember', 'your family'
                        ]):
                            if len(line_clean) > 20 and len(line_clean) < 200:
                                memory_lines.append(line_clean)

                    agent_details["memories"] = memory_lines[:5]  # Keep top 5 memories

                print(f"[DEBUG] Agent '{agent}': goal_found={bool(agent_details['goal'])}, goal_length={len(agent_details['goal'])}, actions_count={len(agent_details['actions'])}")
                analytics["agent_details"][agent] = agent_details

        # DISABLED: This was overwriting correct action counts with duplicates from agent_details
        # The correct counting is now done above at lines 3212-3257
        # # Update agent_actions count to match actual extracted actions
        # # This ensures fallback-extracted actions are counted
        # for agent in analytics["agents"]:
        #     if agent in analytics["agent_details"]:
        #         actual_count = len(analytics["agent_details"][agent].get("actions", []))
        #         analytics["agent_actions"][agent] = actual_count
        #         print(f"[DEBUG] Updated agent_actions['{agent}'] = {actual_count}")

        # NEW: Extract nested simulation data from HTML
        if has_nested_sims:
            print("[DEBUG] Extracting nested simulation data from HTML...")
            for agent_name, nested_config in nested_sim_data.items():
                # Look for nested simulation results in agent's component output
                agent_tab = soup.find('div', id=re.compile(re.escape(agent_name), re.IGNORECASE))
                if agent_tab:
                    tab_text = agent_tab.get_text()
                    # Look for nested simulation completion markers
                    if "Nested simulation completed" in tab_text or "nested simulation result" in tab_text.lower():
                        # Extract the result
                        lines = tab_text.split('\n')
                        for i, line in enumerate(lines):
                            if "nested simulation" in line.lower() and "result" in line.lower():
                                # Get the next few lines as the result
                                result_lines = []
                                for j in range(i, min(i + 5, len(lines))):
                                    if lines[j].strip():
                                        result_lines.append(lines[j].strip())
                                analytics["nested_simulations"][agent_name] = {
                                    "config": nested_config,
                                    "result_summary": "\n".join(result_lines),
                                    "found": True
                                }
                                print(f"[DEBUG] Found nested sim result for {agent_name}")
                                break

                # If not found in agent tab, check Game Master log
                if agent_name not in analytics["nested_simulations"]:
                    game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
                    if game_master_log:
                        log_text = game_master_log.get_text()
                        if "nested simulation" in log_text.lower() and agent_name in log_text:
                            # Extract context around mentions
                            lines = log_text.split('\n')
                            for i, line in enumerate(lines):
                                if agent_name in line and "nested" in line.lower():
                                    context = "\n".join(lines[max(0, i-2):min(i+3, len(lines))])
                                    analytics["nested_simulations"][agent_name] = {
                                        "config": nested_config,
                                        "result_summary": context[:500],
                                        "found": True
                                    }
                                    print(f"[DEBUG] Found nested sim mention for {agent_name} in GM log")
                                    break

        # NEW: Extract grounded variables state changes from metadata or HTML
        if has_grounded_variables:
            print("[DEBUG] Extracting grounded variables data...")

            # Check if metadata has history data (preferred method)
            has_history_in_metadata = any(
                var.get("history") for var in grounded_variables_data.get("variables", [])
            )

            if has_history_in_metadata:
                # Use history from metadata file (most reliable)
                print("[DEBUG] Using grounded variables history from metadata")
                analytics["grounded_variables"] = []
                for var_config in grounded_variables_data.get("variables", []):
                    var_data = {
                        "name": var_config["name"],
                        "type": var_config["variable_type"],
                        "description": var_config.get("description", ""),
                        "current_value": var_config.get("default_value"),
                        "history": var_config.get("history", [])
                    }

                    # Get current value from history if available
                    if var_data["history"]:
                        var_data["current_value"] = var_data["history"][-1]["value"]

                    analytics["grounded_variables"].append(var_data)

                print(f"[DEBUG] Loaded {len(analytics['grounded_variables'])} grounded variables from metadata with history")

            else:
                # Fallback: Parse HTML for variable state changes
                print("[DEBUG] No history in metadata, parsing HTML for grounded variables")
                game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
                if game_master_log:
                    log_text = game_master_log.get_text()
                    variable_history = {}

                    # Initialize with default values from config
                    for var_config in grounded_variables_data.get("variables", []):
                        var_name = var_config["name"]
                        variable_history[var_name] = {
                            "name": var_name,
                            "type": var_config["variable_type"],
                            "description": var_config.get("description", ""),
                            "current_value": var_config.get("default_value"),
                            "history": []  # List of (step, value) tuples
                        }

                    # Helper function to parse variable values
                    def parse_variable_value(value_str: str, var_type: str):
                        """Parse variable value based on type."""
                        value_str = value_str.strip()
                        try:
                            if var_type in ["numerical", "percentage"]:
                                return float(value_str)
                            elif var_type == "boolean":
                                return value_str.lower() in ['true', '1', 'yes']
                            else:  # categorical
                                return value_str
                        except:
                            return value_str

                    # Look for variable state patterns like "team_morale: 70" or "Variable: name = value"
                    # The GroundedVariablesComponent outputs state in format: "name: value (type)"
                    var_pattern = re.compile(r'(\w+(?:\s+\w+)*):\s*([\d.]+|true|false|\w+)\s*(?:\((\w+)\))?', re.IGNORECASE)

                    lines = log_text.split('\n')
                    current_step = 0
                    step_pattern = re.compile(r'step\s+(\d+)', re.IGNORECASE)

                    for line in lines:
                        # Track current step
                        step_match = step_pattern.search(line)
                        if step_match:
                            current_step = int(step_match.group(1))

                        # Look for variable updates
                        matches = var_pattern.findall(line)
                        for var_name, var_value, var_type in matches:
                            var_name_clean = var_name.strip()
                            if var_name_clean in variable_history:
                                # Parse and store the value
                                parsed_value = parse_variable_value(var_value, variable_history[var_name_clean]["type"])
                                variable_history[var_name_clean]["current_value"] = parsed_value
                                variable_history[var_name_clean]["history"].append({
                                    "step": current_step,
                                    "value": parsed_value
                                })

                    # Convert to list format
                    analytics["grounded_variables"] = list(variable_history.values())
                    print(f"[DEBUG] Parsed {len(analytics['grounded_variables'])} grounded variables from HTML")

        return analytics

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing log file: {str(e)}")


@router.post("/cancel/{task_id}")
async def cancel_simulation(task_id: str):
    """
    Cancel a running simulation by task ID.

    Note: Due to Concordia's blocking execution model, cancellation is best effort.
    The simulation will check for cancellation before starting, but may not be
    interruptible once Concordia's play() method is running.
    """
    success = simulation_state.cancel_simulation(task_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {task_id} not found or not running"
        )

    return {
        "status": "cancelling",
        "task_id": task_id,
        "message": "Cancellation requested. Simulation will stop at the next safe point."
    }


@router.get("/status")
async def get_simulations_status():
    """Get status of all tracked simulations."""
    return simulation_state.get_all_simulations()


@router.get("/status/{task_id}")
async def get_simulation_status(task_id: str):
    """Get status of a specific simulation by task ID."""
    sim = simulation_state.get_simulation(task_id)

    if not sim:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {task_id} not found"
        )

    return {
        "task_id": sim.task_id,
        "status": sim.status,
        "started_at": sim.started_at.isoformat(),
        "steps_completed": sim.steps_completed,
        "error": sim.error,
        "config": {
            "premise": sim.config.premise[:100] if hasattr(sim.config, 'premise') else "N/A",
            "max_steps": sim.config.max_steps if hasattr(sim.config, 'max_steps') else 0,
            "num_agents": len(sim.config.agents) if hasattr(sim.config, 'agents') else 0
        }
    }
