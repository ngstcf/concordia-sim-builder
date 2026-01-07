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
            "engine_type": "interview",
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
                "prefab": "interviewer__GameMaster",
                "name": "Group Session Manager",
                "acting_order": "game_master_choice",
                "parameters": {
                    "drive_role": "interviewer",
                    "drive_role_name": "Sarah"
                }
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

    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                premise_from_metadata = metadata.get("premise", "")
                gm_prefab = metadata.get("game_master", {}).get("prefab")

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
            "gm_prefab": gm_prefab  # Include game master prefab type
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

                # For each entity tag, find the associated __act__ section with "Action:" label
                act_count = 0
                for entity_tag in entity_tags:
                    # Look for __act__ in the same section (within the parent details/ul structure)
                    parent = entity_tag.find_parent(['details', 'ul', 'li'])
                    if parent:
                        # Find all __act__ tags in this section
                        act_b_tags = parent.find_all('b', string=re.compile(r'__act__', re.IGNORECASE))
                        for act_tag in act_b_tags:
                            # Check if there's a corresponding "Action:" label in the same section
                            # The Action: label should be in a summary within the same details/ul structure
                            act_section = act_tag.find_parent(['li', 'ul', 'details'])
                            if act_section:
                                # Look for "Action:" text in this section
                                action_label = act_section.find(string=re.compile(r'Action:', re.IGNORECASE))
                                if action_label:
                                    act_count += 1

                analytics["agent_actions"][agent] = act_count
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
        details_elements = soup.find_all('details')
        for detail in details_elements:
            summary = detail.find('summary')
            if summary:
                summary_text = summary.get_text(strip=True)
                # Check if this is a step event
                step_match = re.search(r'Step\s+(\d+)', summary_text, re.IGNORECASE)
                if step_match:
                    step_num = int(step_match.group(1))
                    analytics["timeline"].append({
                        "step": step_num,
                        "description": summary_text[:200],  # First 200 chars
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
                            act_b_tags = parent_li.find_all('b', string=re.compile(r'__act__', re.IGNORECASE))
                            print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in parent li")

                        # Fallback to original logic if no tags found in <li>
                        if not act_b_tags:
                            # For State Formation template, entity tag and __act__ tags are siblings in <details>
                            parent_container = entity_tag.find_parent('details')

                            if parent_container:
                                # Find all __act__ tags in the same <details> section
                                # Note: can't use string= with regex because __act__ tags have <ul> children
                                all_b_tags = parent_container.find_all('b')
                                act_pattern = re.compile(r'__act__', re.IGNORECASE)
                                act_b_tags = [b for b in all_b_tags if act_pattern.search(b.get_text())]
                                print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in details container")

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
                                            "text": action_text[:300]  # Limit to 300 chars
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

                    # Find all event summaries in Game Master log
                    event_summaries = game_master_log.find_all('summary')
                    for summary in event_summaries:
                        summary_text = summary.get_text()

                        # Check if this event mentions the agent
                        if agent.lower() in summary_text.lower():
                            # Extract step number if available
                            step_match = re.search(r'Step\s+(\d+)', str(summary.find_parent('details')), re.IGNORECASE)
                            step_num = int(step_match.group(1)) if step_match else None

                            # Extract the action description more intelligently
                            # Look for the narrative description that mentions the agent
                            # The format is typically: "Event: ... **Agent Name** did something..."

                            # First, try to find the specific sentence about the agent
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

                                    if len(action_text) > 50:  # Minimum length check
                                        agent_details["actions"].append({
                                            "step": step_num,
                                            "text": action_text[:300]
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

        # Update agent_actions count to match actual extracted actions
        # This ensures fallback-extracted actions are counted
        for agent in analytics["agents"]:
            if agent in analytics["agent_details"]:
                actual_count = len(analytics["agent_details"][agent].get("actions", []))
                analytics["agent_actions"][agent] = actual_count
                print(f"[DEBUG] Updated agent_actions['{agent}'] = {actual_count}")

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
