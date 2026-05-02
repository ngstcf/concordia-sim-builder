"""
API endpoints for simulation management and execution.

Template data lives in backend.api.templates (one file per template).
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from backend.api.templates import TEMPLATES

from backend.models.schemas import (
    SimulationConfig,
    LLMSettings,
    ValidationResult,
    PrefabInfo,
    ExecutionRequest,
    ComponentValidationRequest,
    GroundedVariablesExtractionRequest,
    PersonaGenerationRequest,
    GeneratedPersona,
    PersonaGenerationResponse,
    FormativeMemoryRequest,
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
from backend.utils.debug_print import debug_print

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


@router.get("/contrib-components")
async def get_contrib_components():
    """Get registry of available contrib GM components."""
    from backend.prefabs.contrib_gm_components import CONTRIB_GM_REGISTRY
    return {
        "components": [
            {
                "id": comp_id,
                "name": entry["name"],
                "description": entry["description"],
                "category": entry["category"],
                "params": entry["params"],
            }
            for comp_id, entry in CONTRIB_GM_REGISTRY.items()
        ]
    }


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
    if provider in (LLMProvider.OLLAMA.value, LLMProvider.OLLAMA_REMOTE.value):
        # Local Ollama: always localhost, no auth
        # Remote Ollama: uses .env endpoint and key
        if provider == LLMProvider.OLLAMA_REMOTE.value:
            ollama_base = base_url or os.getenv('OLLAMA_BASE_URL', '')
            if not ollama_base:
                return {'provider': provider, 'models': [], 'error': 'OLLAMA_BASE_URL not set in .env'}
            models_url = f"{ollama_base.rstrip('/')}/models"
            headers = {}
            env_key = api_key or os.getenv('OLLAMA_API_KEY')
            if env_key:
                headers['Authorization'] = f"Bearer {env_key}"
        else:
            models_url = "http://localhost:11434/v1/models"
            headers = {}

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

    elif provider == LLMProvider.AZURE.value:
        # For Azure OpenAI, deployment names are user-specific and must be entered manually
        # Return empty list so users always see the manual input field
        return {'provider': provider, 'models': []}

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

    # Debug: Check if critical_decision_points are in the request
    debug_print(f"[DEBUG] execute_simulation: Checking for critical_decision_points in request...")
    debug_print(f"[DEBUG] hasattr(config, 'game_master'): {hasattr(config, 'game_master')}")
    if hasattr(config, 'game_master'):
        debug_print(f"[DEBUG] hasattr(config.game_master, 'critical_decision_points'): {hasattr(config.game_master, 'critical_decision_points')}")
        if hasattr(config.game_master, 'critical_decision_points'):
            debug_print(f"[DEBUG] config.game_master.critical_decision_points: {config.game_master.critical_decision_points}")

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



# --- Template endpoints (data in backend/api/templates/) ---

def _make_template_endpoint(template_data: dict):
    async def _get_template():
        return template_data
    return _get_template

for _slug, _data in TEMPLATES.items():
    router.add_api_route(
        f"/templates/{_slug}",
        _make_template_endpoint(_data),
        methods=["GET"],
        name=f"get_{_slug.replace('-', '_')}_template",
    )


@router.get("/recent")
async def get_recent_simulations(limit: int = 20):
    """Get list of recent simulation logs, excluding checkpoint files."""
    import os
    from pathlib import Path

    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []

    # Get all HTML files in logs directory, excluding checkpoints
    log_files = []
    for file_path in logs_dir.glob("*.html"):
        try:
            # Skip all checkpoint files (regular, emergency, watchdog)
            if ("_checkpoint_step" in file_path.name or
                "EMERGENCY_CHECKPOINT" in file_path.name or
                "WATCHDOG_EMERGENCY" in file_path.name):
                continue

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


@router.get("/logs/checkpoints")
async def get_checkpoint_files():
    """
    Get list of all checkpoint files in the logs directory.

    Includes regular checkpoints, emergency checkpoints, and watchdog emergency files.

    Returns:
        List of checkpoint files with metadata
    """
    import os
    from pathlib import Path

    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {
                "success": True,
                "checkpoints": [],
                "total_size": 0
            }

        # Find all checkpoint files (regular, emergency, and watchdog)
        checkpoint_files = list(logs_dir.glob("*_checkpoint_step*.html"))
        emergency_files = list(logs_dir.glob("*_EMERGENCY_CHECKPOINT.html"))
        watchdog_files = list(logs_dir.glob("*_WATCHDOG_EMERGENCY*.html"))

        # Combine all checkpoint types
        all_checkpoint_files = checkpoint_files + emergency_files + watchdog_files

        checkpoints = []
        total_size = 0

        for file_path in all_checkpoint_files:
            stat = file_path.stat()
            checkpoints.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": str(file_path)
            })
            total_size += stat.st_size

        # Sort by modified time (newest first)
        checkpoints.sort(key=lambda x: x["modified"], reverse=True)

        return {
            "success": True,
            "checkpoints": checkpoints,
            "total_count": len(checkpoints),
            "total_size": total_size
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get checkpoint files: {str(e)}"
        )


@router.delete("/logs/checkpoints")
async def delete_checkpoint_files():
    """
    Delete all checkpoint files from the logs directory.

    Checkpoint files include:
    - Regular checkpoints: '*_checkpoint_stepN.html'
    - Emergency checkpoints: '*_EMERGENCY_CHECKPOINT.html'
    - Watchdog emergency: '*_WATCHDOG_EMERGENCY*.html'

    Returns:
        Summary of deleted files
    """
    import os
    from pathlib import Path

    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {
                "success": False,
                "message": "Logs directory not found",
                "deleted_count": 0
            }

        # Find all checkpoint files (regular, emergency, and watchdog)
        checkpoint_files = list(logs_dir.glob("*_checkpoint_step*.html"))
        emergency_files = list(logs_dir.glob("*_EMERGENCY_CHECKPOINT.html"))
        watchdog_files = list(logs_dir.glob("*_WATCHDOG_EMERGENCY*.html"))

        # Combine all checkpoint types
        all_checkpoint_files = checkpoint_files + emergency_files + watchdog_files

        deleted_count = 0
        deleted_files = []

        for file_path in all_checkpoint_files:
            try:
                file_path.unlink()
                deleted_count += 1
                deleted_files.append(str(file_path.name))
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

        return {
            "success": True,
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "message": f"Deleted {deleted_count} checkpoint file(s)"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete checkpoint files: {str(e)}"
        )


@router.delete("/logs/{filename}")
async def delete_simulation_log(filename: str):
    """Delete a simulation log and its associated metadata file."""
    from pathlib import Path
    import re

    safe_filename = re.sub(r'[^\w\s\-.]', '', filename)
    if safe_filename != filename or '..' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    logs_dir = Path("logs")
    log_path = logs_dir / safe_filename
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")

    deleted = [safe_filename]
    log_path.unlink()

    meta_path = logs_dir / safe_filename.replace('.html', '.metadata.json')
    if meta_path.exists():
        meta_path.unlink()
        deleted.append(meta_path.name)

    return {"success": True, "deleted": deleted}


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
    has_measurements = False
    nested_sim_data = {}
    grounded_variables_data = {}
    component_data = {}
    measurements_data = {}

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
                        debug_print(f"[DEBUG] Found nested simulation for agent {agent['name']}")

                # NEW: Detect grounded variables
                if metadata.get("game_master", {}).get("grounded_variables"):
                    has_grounded_variables = True
                    grounded_variables_data["variables"] = metadata["game_master"]["grounded_variables"]
                    debug_print(f"[DEBUG] Found {len(grounded_variables_data['variables'])} grounded variables")

                # NEW: Detect components
                for agent in metadata.get("agents", []):
                    if agent.get("components"):
                        has_components = True
                        component_data[agent["name"]] = agent["components"]
                        debug_print(f"[DEBUG] Found components for agent {agent['name']}: {list(agent['components'].keys())}")

                # NEW: Detect measurements
                if metadata.get("measurements"):
                    has_measurements = True
                    measurements_data = metadata["measurements"]
                    debug_print(f"[DEBUG] Found measurements: {len(measurements_data)} channels")

                # Build a map of agent name -> metadata
                for agent in metadata.get("agents", []):
                    agent_metadata[agent["name"]] = {
                        "goal": agent.get("goal", ""),
                        "prefab": agent.get("prefab", ""),
                        "memories_count": agent.get("memories_count", 0)
                    }
                debug_print(f"[DEBUG] Loaded metadata for {len(agent_metadata)} agents")

                # Check for game-theoretic action data in metadata
                if "game_theoretic" in metadata:
                    gt_data = metadata["game_theoretic"]
                    actions_by_player = gt_data.get("actions_by_player", {})
                    # Convert to action counts for easy lookup, but only if not empty
                    if actions_by_player:  # Only use if actually has data
                        for player_name, actions in actions_by_player.items():
                            game_theoretic_actions[player_name] = len(actions)
                        debug_print(f"[DEBUG] Loaded game-theoretic action data: {game_theoretic_actions}")
                    else:
                        debug_print(f"[DEBUG] Game-theoretic metadata exists but empty, will use HTML extraction")
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
            "has_measurements": has_measurements,
            # NEW: Feature-specific data (populated from metadata)
            "nested_simulations": nested_sim_data,
            "grounded_variables": grounded_variables_data.get("variables", []),
            "components": component_data,
            "measurements": measurements_data
        }

        # Detect v2.4+ structured log format (content is in embedded JSON, not static HTML)
        # In this format, ENTRIES and CONTENT_STORE are JavaScript variables in a <script> tag
        entries_match = re.search(r'const ENTRIES = (\[.*?\]);\s*$', html_content, re.DOTALL | re.MULTILINE)
        content_store_match = re.search(r'const CONTENT_STORE = (\{.*?\});\s*$', html_content, re.DOTALL | re.MULTILINE)

        if entries_match:
            # === V2.4+ STRUCTURED LOG FORMAT ===
            debug_print("[DEBUG] Detected v2.4+ structured log format — parsing embedded JSON")
            try:
                structured_entries = json.loads(entries_match.group(1))
                content_store = json.loads(content_store_match.group(1)) if content_store_match else {}

                def _resolve_ref(value):
                    """Resolve content store references in deduplicated data."""
                    if isinstance(value, dict):
                        if '_ref' in value:
                            return content_store.get(value['_ref'], str(value))
                        return {k: _resolve_ref(v) for k, v in value.items()}
                    if isinstance(value, list):
                        return [_resolve_ref(v) for v in value]
                    return value

                excluded_entities = {'Game Master', 'game_master'}
                gm_name_from_meta = metadata.get("game_master", {}).get("name", "") if metadata else ""
                if gm_name_from_meta:
                    excluded_entities.add(gm_name_from_meta)

                agent_names_set = set()
                agent_action_counts = {}
                agent_action_texts = {}
                agent_goals = {}
                max_step = 0
                observation_count = 0
                timeline_entries = {}
                all_text_parts = []

                for entry in structured_entries:
                    step = entry.get('step', 0)
                    entity = entry.get('entity_name', '')
                    entry_type = entry.get('entry_type', '')
                    component = entry.get('component_name', '')
                    summary = entry.get('summary', '')
                    dedup_data = entry.get('deduplicated_data', {})

                    max_step = max(max_step, step)

                    # Collect all text for word count
                    all_text_parts.append(summary)

                    # Collect agent names only from entity-type entries (excludes GM step entries)
                    if entity and entity not in excluded_entities and entry_type == 'entity':
                        agent_names_set.add(entity)

                    # Count actions and extract action text from entity entries
                    if entry_type == 'entity' and entity not in excluded_entities:
                        resolved = _resolve_ref(dedup_data)
                        value_data = resolved.get('value', {})
                        if isinstance(value_data, dict):
                            has_action = '__act__' in value_data or value_data.get('Key') == '__act__'

                            if has_action:
                                agent_action_counts[entity] = agent_action_counts.get(entity, 0) + 1
                                act_data = value_data.get('__act__', {})
                                act_text = act_data.get('Value', '') if isinstance(act_data, dict) else str(act_data)
                                if act_text:
                                    if entity not in agent_action_texts:
                                        agent_action_texts[entity] = []
                                    agent_action_texts[entity].append({
                                        "step": step,
                                        "text": act_text
                                    })

                            if entity not in agent_goals and 'Goal' in value_data:
                                goal_data = value_data['Goal']
                                goal_text = goal_data.get('Value', '') if isinstance(goal_data, dict) else str(goal_data)
                                if goal_text:
                                    agent_goals[entity] = goal_text
                        else:
                            has_action = '__act__' in str(value_data) if value_data else False
                            if has_action:
                                agent_action_counts[entity] = agent_action_counts.get(entity, 0) + 1

                    # Count observations
                    if 'observation' in entry_type.lower() or '[observation]' in summary.lower():
                        observation_count += 1

                    # Build timeline (one entry per step)
                    if step > 0 and step not in timeline_entries:
                        description = summary
                        prefix_pattern = re.compile(r'Step\s+\d+\s+.*?---\s*Event:\s*', re.IGNORECASE)
                        description = prefix_pattern.sub('', description).strip()
                        if description:
                            timeline_entries[step] = {
                                "step": step,
                                "description": description,
                                "type": "step"
                            }

                analytics["total_steps"] = max_step
                analytics["agents"] = sorted(agent_names_set)
                analytics["agent_actions"] = {a: agent_action_counts.get(a, 0) for a in analytics["agents"]}
                analytics["total_observations"] = observation_count
                analytics["timeline"] = sorted(timeline_entries.values(), key=lambda x: x["step"])

                # Build agent_details from structured data
                analytics["agent_details"] = {}
                for agent in analytics["agents"]:
                    goal = agent_goals.get(agent, "")
                    if not goal and agent in agent_metadata and agent_metadata[agent].get("goal"):
                        goal = agent_metadata[agent]["goal"]
                    analytics["agent_details"][agent] = {
                        "actions": agent_action_texts.get(agent, []),
                        "goal": goal,
                        "memories": []
                    }
                    debug_print(f"[DEBUG] Agent '{agent}': goal='{goal[:80]}...', actions={len(agent_action_texts.get(agent, []))}")

                # Update word/character counts from structured data
                full_text = ' '.join(all_text_parts)
                if len(full_text) > len(soup_text):
                    analytics["word_count"] = len(full_text.split())
                    analytics["character_count"] = len(full_text)

                debug_print(f"[DEBUG] Structured log: {max_step} steps, {len(analytics['agents'])} agents, "
                           f"{sum(agent_action_counts.values())} actions")

            except (json.JSONDecodeError, Exception) as e:
                print(f"[WARNING] Failed to parse structured log JSON, falling back to HTML parsing: {e}")
                entries_match = None  # Fall through to legacy parsing

        if not entries_match:
            # === LEGACY HTML FORMAT (pre-v2.4) ===

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
                        debug_print(f"[DEBUG] Set {player_name} actions to {action_count} from game-theoretic metadata")
                debug_print(f"[DEBUG] Applied game-theoretic action data for {len(game_theoretic_actions)} players")

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
        # (skip if already populated by v2.4 structured log parser above)
        if "agent_details" not in analytics or not analytics["agent_details"]:
            analytics["agent_details"] = {}

        for agent in analytics["agents"]:
            if agent in analytics.get("agent_details", {}) and analytics["agent_details"][agent].get("actions"):
                continue
            agent_details = {
                "actions": [],
                "goal": "",
                "memories": []
            }

            # USE METADATA FOR GOAL - Much more reliable than HTML parsing!
            if agent in agent_metadata and agent_metadata[agent].get("goal"):
                agent_details["goal"] = agent_metadata[agent]["goal"]
                debug_print(f"[DEBUG] Agent '{agent}': using goal from metadata: {agent_details['goal'][:100]}...")
            else:
                # Fallback: Try to extract goal from HTML (old method)
                debug_print(f"[DEBUG] Agent '{agent}': no goal in metadata, trying HTML extraction")

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
                                    debug_print(f"[DEBUG] Agent '{agent}': found goal via regex: {goal[:100]}...")
                                    break

            analytics["agent_details"][agent] = agent_details

        # Extract actions for each agent from Game Master log
        game_master_log = soup.find('div', id=re.compile(r'Game Master log', re.IGNORECASE))
        if game_master_log:
            for agent in analytics["agents"]:
                agent_details = analytics["agent_details"][agent]

                debug_print(f"[DEBUG] Agent '{agent}': extracting actions from Game Master log")

                # PRIMARY METHOD: Extract actions from event descriptions
                # This is more reliable than parsing complex HTML structures
                debug_print(f"[DEBUG] Agent '{agent}': extracting actions from event descriptions")

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
                    debug_print(f"[DEBUG] Agent '{agent}': no actions in events, trying entity tag extraction")
                    entity_pattern_bs = re.compile(rf'Entity\s+\[{re.escape(agent)}\]', re.IGNORECASE)
                    entity_tags = game_master_log.find_all('b', string=entity_pattern_bs)
                    debug_print(f"[DEBUG] Agent '{agent}': found {len(entity_tags)} entity tags for action extraction")

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
                            debug_print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in parent li (filtered)")

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

                                debug_print(f"[DEBUG] Agent '{agent}': found {len(act_b_tags)} __act__ tags in details container (filtered)")

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
                                        debug_print(f"[DEBUG] Agent '{agent}': skipping game master __act__ tag (Action Spec: {action_spec_text})")
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
                                    debug_print(f"[DEBUG] Agent '{agent}': extracted action from summary, length={len(action_text)}")
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
                                                    debug_print(f"[DEBUG] Agent '{agent}': extracted action from value li, length={len(action_text)}")
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
                                        debug_print(f"[DEBUG] Agent '{agent}': added action (step={step_num}), total actions={len(agent_details['actions'])}")
                                    else:
                                        debug_print(f"[DEBUG] Agent '{agent}': skipping short response: '{action_text}'")
                                    action_text = None  # Reset for next iteration

                # TERTIARY METHOD: Regex fallback for game-theoretic actions
                # Looks for "Action: COOPERATE" pattern anywhere in game master log
                # Works for ANY action type (COOPERATE/DEFECT, BUY/SELL/HOLD, etc.)
                debug_print(f"[DEBUG] Agent '{agent}': regex fallback check - actions count={len(agent_details['actions'])}, gm_prefab={gm_prefab}")

                # FUTURE: Detection for other game master types (interviewer, dialogic)
                # These formats may use Q&A or dialogue turns instead of __act__ tags
                # Current implementation will gracefully fall back to event extraction
                # if gm_prefab in ['interviewer__GameMaster', 'dialogic__GameMaster']:
                #     debug_print(f"[DEBUG] Agent '{agent}': {gm_prefab} detected - using dialogue/Q&A extraction")
                #     # TODO: Add interviewer/dialogic-specific extraction logic here

                if len(agent_details["actions"]) == 0 and gm_prefab == 'game_theoretic_and_dramaturgic__GameMaster':
                    debug_print(f"[DEBUG] Agent '{agent}': trying regex fallback for game-theoretic actions")
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
                    debug_print(f"[DEBUG] Agent '{agent}': regex fallback found {len(entity_matches)} actions: {entity_matches}")

                # FALLBACK: If no entity tags found, try extracting from event descriptions
                # This handles cases like GLM-generated HTML where some agents don't have entity sections
                if len(entity_tags) == 0 and len(agent_details["actions"]) == 0:
                    debug_print(f"[DEBUG] Agent '{agent}': no entity tags found, trying fallback extraction from events")

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
                                        debug_print(f"[DEBUG] Agent '{agent}': added fallback action (step={step_num}), total actions={len(agent_details['actions'])}")
                                        break  # Only take one action per event

                # FALLBACK: If no entity tags found, also try to extract goal from events
                if len(entity_tags) == 0 and not agent_details["goal"]:
                    debug_print(f"[DEBUG] Agent '{agent}': no entity tags found, trying fallback goal extraction from events")

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
                                        debug_print(f"[DEBUG] Agent '{agent}': found fallback goal from event: {agent_details['goal'][:100]}...")
                                        break

                            if agent_details["goal"]:
                                break

                    # If still no goal, set a placeholder based on agent name
                    if not agent_details["goal"]:
                        agent_details["goal"] = f"Goal not explicitly stated in simulation logs"
                        debug_print(f"[DEBUG] Agent '{agent}': using placeholder goal")

                # Only extract from agent tab if we didn't find goal in Game Master log
                if not agent_details["goal"] or agent_details["goal"] == "Goal not explicitly stated in simulation logs":
                    agent_tab = soup.find('div', id=re.compile(re.escape(agent), re.IGNORECASE))
                    if agent_tab:
                        tab_text = agent_tab.get_text(strip=True)
                        debug_print(f"[DEBUG] Agent '{agent}': trying to extract goal from agent tab (tab_text_length={len(tab_text)})")

                        # Print first 500 chars of tab text for debugging
                        debug_print(f"[DEBUG] Agent '{agent}': tab text preview: {tab_text[:500]}...")

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
                                debug_print(f"[DEBUG] Agent '{agent}': found goal using pattern {i+1}: {agent_details['goal'][:100]}...")
                                break
                        if not agent_details["goal"] or agent_details["goal"] == "Goal not explicitly stated in simulation logs":
                            debug_print(f"[DEBUG] Agent '{agent}': no goal found in agent tab using patterns")
                    else:
                        debug_print(f"[DEBUG] Agent '{agent}': no agent tab found")

                        # Try to find ANY tab that might contain this agent's information
                        all_tabs = soup.find_all('div', id=True)
                        debug_print(f"[DEBUG] Agent '{agent}': searching through {len(all_tabs)} total tabs")
                        for tab in all_tabs[:5]:  # Check first 5 tabs
                            tab_id = tab.get('id', '')
                            debug_print(f"[DEBUG] Agent '{agent}': checking tab '{tab_id}'")
                            if agent.lower() in tab_id.lower() or 'entity' in tab_id.lower() or 'agent' in tab_id.lower():
                                tab_preview = tab.get_text(strip=True)[:200]
                                debug_print(f"[DEBUG] Agent '{agent}': tab '{tab_id}' preview: {tab_preview}...")

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

                debug_print(f"[DEBUG] Agent '{agent}': goal_found={bool(agent_details['goal'])}, goal_length={len(agent_details['goal'])}, actions_count={len(agent_details['actions'])}")
                analytics["agent_details"][agent] = agent_details

        # DISABLED: This was overwriting correct action counts with duplicates from agent_details
        # The correct counting is now done above at lines 3212-3257
        # # Update agent_actions count to match actual extracted actions
        # # This ensures fallback-extracted actions are counted
        # for agent in analytics["agents"]:
        #     if agent in analytics["agent_details"]:
        #         actual_count = len(analytics["agent_details"][agent].get("actions", []))
        #         analytics["agent_actions"][agent] = actual_count
        #         debug_print(f"[DEBUG] Updated agent_actions['{agent}'] = {actual_count}")

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
                                debug_print(f"[DEBUG] Found nested sim result for {agent_name}")
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
                                    debug_print(f"[DEBUG] Found nested sim mention for {agent_name} in GM log")
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

                debug_print(f"[DEBUG] Loaded {len(analytics['grounded_variables'])} grounded variables from metadata with history")

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
                    debug_print(f"[DEBUG] Parsed {len(analytics['grounded_variables'])} grounded variables from HTML")

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


@router.post("/control/{task_id}/play")
async def step_controller_play(task_id: str):
    """Resume continuous execution of a step-controlled simulation."""
    sim = simulation_state.get_simulation(task_id)
    if not sim or not sim.step_controller:
        raise HTTPException(status_code=404, detail="No step controller for this simulation")
    sim.step_controller.play()
    return {"status": "playing", "task_id": task_id}


@router.post("/control/{task_id}/pause")
async def step_controller_pause(task_id: str):
    """Pause a step-controlled simulation after the current step completes."""
    sim = simulation_state.get_simulation(task_id)
    if not sim or not sim.step_controller:
        raise HTTPException(status_code=404, detail="No step controller for this simulation")
    sim.step_controller.pause()
    return {"status": "paused", "task_id": task_id}


@router.post("/control/{task_id}/step")
async def step_controller_step(task_id: str):
    """Execute a single step then pause."""
    sim = simulation_state.get_simulation(task_id)
    if not sim or not sim.step_controller:
        raise HTTPException(status_code=404, detail="No step controller for this simulation")
    sim.step_controller.step()
    return {"status": "stepping", "task_id": task_id}


@router.post("/control/{task_id}/stop")
async def step_controller_stop(task_id: str):
    """Stop a step-controlled simulation completely."""
    sim = simulation_state.get_simulation(task_id)
    if not sim or not sim.step_controller:
        raise HTTPException(status_code=404, detail="No step controller for this simulation")
    sim.step_controller.stop()
    return {"status": "stopped", "task_id": task_id}


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


@router.post("/grounded-variables/extract")
async def extract_grounded_variables(request: GroundedVariablesExtractionRequest):
    """
    Extract grounded variables from a completed simulation using post-processing.

    This endpoint analyzes the HTML log of a completed simulation and uses LLM to
    identify and extract how grounded variables changed throughout the simulation.

    Args:
        request: Extraction request with simulation_id, html_file_path, and llm_settings

    Returns:
        Extracted variable history with changes at each step
    """
    import os
    from pathlib import Path
    from backend.utils.grounded_variables_post_processor import GroundedVariablesPostProcessor
    from backend.services.llm_factory import get_model_and_embedder

    try:
        simulation_id = request.simulation_id
        html_file_path = request.html_file_path
        llm_settings = request.llm_settings

        # Validate HTML file exists
        html_path = Path(html_file_path)
        if not html_path.is_absolute():
            # Assume relative to logs directory
            html_path = Path("logs") / html_file_path

        if not html_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"HTML file not found: {html_file_path}"
            )

        # Find corresponding metadata file
        metadata_path = html_path.with_suffix(".metadata.json")
        if not metadata_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Metadata file not found: {metadata_path.name}"
            )

        # Load metadata to get variable configurations
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Check if simulation has grounded variables
        if "game_master" not in metadata or "grounded_variables" not in metadata["game_master"]:
            return {
                "success": False,
                "message": "Simulation does not have grounded variables configured",
                "variables": []
            }

        # Build variable configs from metadata
        variable_configs = []
        for var in metadata["game_master"]["grounded_variables"]:
            variable_configs.append({
                "name": var["name"],
                "variable_type": var["variable_type"],
                "description": var.get("description", ""),
                "default_value": var.get("default_value"),
                "min_value": var.get("min_value"),
                "max_value": var.get("max_value"),
                "allowed_values": var.get("allowed_values"),
                "update_rule": var.get("update_rule"),
            })

        # Create LLM instance using the existing factory function
        # Note: We only need the model, not the embedder
        model, _ = get_model_and_embedder(llm_settings)

        # Create post-processor and extract variables
        processor = GroundedVariablesPostProcessor(model, variable_configs)
        history = processor.process_simulation(
            str(html_path),
            str(metadata_path)
        )

        # Format results for response
        results = {
            "success": True,
            "simulation_id": simulation_id,
            "html_file": str(html_path),
            "metadata_file": str(metadata_path),
            "variables": []
        }

        for var_name, var_history in history.items():
            # Find the variable config
            var_config = next((v for v in metadata["game_master"]["grounded_variables"] if v["name"] == var_name), None)

            if var_history:
                initial_value = var_history[0]["value"]
                final_value = var_history[-1]["value"]

                # Count changes
                changes = []
                prev_value = initial_value
                for entry in var_history:
                    if entry["value"] != prev_value:
                        changes.append({
                            "step": entry["step"],
                            "from": prev_value,
                            "to": entry["value"]
                        })
                        prev_value = entry["value"]

                results["variables"].append({
                    "name": var_name,
                    "type": var_config["variable_type"] if var_config else "unknown",
                    "description": var_config.get("description", "") if var_config else "",
                    "initial_value": initial_value,
                    "final_value": final_value,
                    "total_changes": len(changes),
                    "changes": changes,
                    "history": var_history
                })

        return results

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract grounded variables: {str(e)}"
        )


@router.get("/grounded-variables/{simulation_id}")
async def get_grounded_variables(simulation_id: str):
    """
    Get extracted grounded variables for a simulation.

    Returns the variable history from the metadata file if it exists.

    Args:
        simulation_id: ID of the simulation (timestamp format)

    Returns:
        Extracted variable history
    """
    import glob
    from pathlib import Path

    try:
        # Find metadata files matching the simulation ID
        logs_dir = Path("logs")
        pattern = f"*{simulation_id}*.metadata.json"
        matches = list(logs_dir.glob(pattern))

        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"No metadata found for simulation: {simulation_id}"
            )

        # Use the first match
        metadata_path = matches[0]

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Check if grounded variables exist
        if "game_master" not in metadata or "grounded_variables" not in metadata["game_master"]:
            return {
                "success": False,
                "message": "Simulation does not have grounded variables",
                "variables": []
            }

        variables = []
        for var in metadata["game_master"]["grounded_variables"]:
            var_data = {
                "name": var["name"],
                "type": var["variable_type"],
                "description": var.get("description", ""),
                "default_value": var.get("default_value"),
                "has_history": "history" in var and len(var.get("history", [])) > 0
            }

            # Include history if available
            if "history" in var and var["history"]:
                var_data["history"] = var["history"]
                var_data["initial_value"] = var["history"][0]["value"]
                var_data["final_value"] = var["history"][-1]["value"]

                # Count changes
                changes = []
                prev_value = var_data["initial_value"]
                for entry in var["history"]:
                    if entry["value"] != prev_value:
                        changes.append({
                            "step": entry["step"],
                            "from": prev_value,
                            "to": entry["value"]
                        })
                        prev_value = entry["value"]
                var_data["total_changes"] = len(changes)
                var_data["changes"] = changes

            variables.append(var_data)

        return {
            "success": True,
            "simulation_id": simulation_id,
            "metadata_file": str(metadata_path),
            "variables": variables
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get grounded variables: {str(e)}"
        )


@router.post("/analyze-simulation")
async def analyze_simulation_endpoint(request: dict):
    """
    Generate comprehensive analysis report for a simulation using LLM.
    
    This endpoint uses the SimulationAnalyzer to perform deep content analysis
    of simulation logs, generating insights, recommendations, and assessments.
    
    Args:
        request: Dictionary containing:
            - simulation_id: ID of the simulation (timestamp format)
            - llm_settings: Optional LLM settings (uses defaults if not provided)
    
    Returns:
        Analysis report containing:
            - metadata: Simulation metadata
            - executive_summary: High-level overview
            - timeline: Step-by-step events
            - team_effectiveness: Agent/team analysis
            - insights: Key findings
            - recommendations: Actionable suggestions
    """
    from pathlib import Path
    from backend.utils.simulation_analyzer import SimulationAnalyzer
    from backend.services.llm_factory import get_model_and_embedder
    from backend.models.schemas import LLMSettings, LLMProvider
    
    try:
        simulation_id = request.get("simulation_id")
        if not simulation_id:
            raise HTTPException(
                status_code=400,
                detail="simulation_id is required"
            )

        # Find the HTML log file
        logs_dir = Path("logs")
        html_files = list(logs_dir.glob(f"{simulation_id}*.html"))

        # Note: We include ALL HTML files including checkpoints for analysis
        # Checkpoints can be analyzed to understand partial simulation progress

        if not html_files:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation log not found for ID: {simulation_id}"
            )

        # Sort by preference: final file > emergency > watchdog > regular checkpoint
        # This ensures we analyze the most complete data available
        def file_priority(f):
            name = f.name
            if "_checkpoint_step" in name:
                return 3  # Regular checkpoint - lowest priority
            elif "WATCHDOG_EMERGENCY" in name:
                return 2  # Watchdog emergency
            elif "EMERGENCY_CHECKPOINT" in name:
                return 1  # Emergency checkpoint
            else:
                return 0  # Final file - highest priority

        html_files.sort(key=file_priority)
        log_path = str(html_files[0])
        
        # Get LLM settings from request or use defaults
        llm_settings_dict = request.get("llm_settings", {})
        llm_settings = LLMSettings(
            provider=LLMProvider(llm_settings_dict.get("provider", "glm")),
            model_name=llm_settings_dict.get("model_name", "glm-4.7"),
            api_key=llm_settings_dict.get("api_key"),
            temperature=llm_settings_dict.get("temperature", 0.7),
            embedder_model=llm_settings_dict.get("embedder_model", "all-MiniLM-L6-v2")
        )
        
        # Get LLM client
        model, embedder = get_model_and_embedder(llm_settings)
        
        # Run analysis
        analyzer = SimulationAnalyzer(model)
        analysis = analyzer.analyze_simulation(log_path)
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "log_file": html_files[0].name,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze simulation: {str(e)}"
        )


@router.post("/generate-formative-memories")
async def generate_formative_memories(request: FormativeMemoryRequest):
    """Generate formative backstory memories for an agent."""
    from backend.models.schemas import FormativeMemoryResponse
    from backend.services.llm_factory import get_model_and_embedder
    from concordia.components.game_master.formative_memories_initializer import FormativeMemoriesInitializer

    try:
        model, _ = get_model_and_embedder(request.llm_settings)
        initializer = FormativeMemoriesInitializer(
            model=model,
            next_game_master_name='backstory_generator',
            player_names=[request.agent_name],
            shared_memories=request.shared_memories,
            player_specific_context=(
                {request.agent_name: request.agent_context} if request.agent_context else {}
            ),
            sentences_per_episode=request.sentences_per_episode,
        )
        episodes = initializer.generate_backstory_episodes(request.agent_name)
        return FormativeMemoryResponse(memories=list(episodes))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Formative memory generation failed: {str(e)}"
        )


@router.post("/generate-personas")
async def generate_personas(request: PersonaGenerationRequest):
    """Generate diverse agent personas using Concordia's persona generators."""
    from backend.services.llm_factory import get_model_and_embedder
    from concordia.contrib.persona_generators.two_stage_persona_generator import TwoStagePersonaGenerator

    try:
        model, _ = get_model_and_embedder(request.llm_settings)
        generator = TwoStagePersonaGenerator(model)

        characteristics_list = generator.generate_diverse_persona_characteristics(
            initial_context=request.context,
            diversity_axes=request.diversity_axes,
            num_personas=request.num_personas,
        )

        personas = []
        for char_dict in characteristics_list:
            name = char_dict.get("name", "Unknown")
            description = char_dict.get("description", "")
            goal = char_dict.get("goal", "")

            memories = generator.generate_single_persona_memories(
                persona_details={**char_dict, "initial_context": request.context},
                num_memories=request.num_memories,
            )

            personas.append(GeneratedPersona(
                name=name,
                goal=goal,
                memories=memories,
                description=description,
            ))

        return PersonaGenerationResponse(personas=personas)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Persona generation failed: {str(e)}"
        )
