"""
Pydantic schemas for simulation configuration and API requests/responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Literal, Union
from enum import Enum


class EngineType(str, Enum):
    """Available simulation engine types."""
    SEQUENTIAL = "sequential"
    SIMULTANEOUS = "simultaneous"
    ASYNCHRONOUS = "asynchronous"
    STEP_CONTROLLER = "step_controller"
    INTERVIEW = "interview"
    SURVEY = "survey"


class ClockType(str, Enum):
    """Available clock behavior types."""
    MULTI_INTERVAL = "multi_interval"
    FIXED_INCREMENT = "fixed_increment"
    GENERATIVE = "generative"


class ActingOrder(str, Enum):
    """Game master acting order options."""
    FIXED = "fixed"
    RANDOM = "random"
    GAME_MASTER_CHOICE = "game_master_choice"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    AZURE = "azure"  # Azure OpenAI
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OLLAMA_REMOTE = "ollama_remote"
    GLM = "glm"  # Zhipu AI (GLM models)


class NestedSimulationConfig(BaseModel):
    """Configuration for a nested simulation within the main simulation."""
    premise: str = Field(..., description="Premise of the nested simulation")
    max_steps: int = Field(5, ge=1, le=50, description="Max steps for nested simulation")
    agents: List['AgentConfig'] = Field(
        ...,
        min_items=1,
        description="Agents in the nested simulation"
    )
    shared_memories: List[str] = Field(
        default_factory=list,
        description="Shared memories for nested simulation"
    )
    extraction_prompt: Optional[str] = Field(
        None,
        description="Custom prompt for extracting observations from nested sim"
    )


class AgentConfig(BaseModel):
    """Configuration for a simulation agent."""
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Display name of the agent")
    prefab: str = Field(..., description="Prefab type (e.g., 'basic__Entity')")
    goal: Optional[str] = Field(None, description="Agent's objective/goal")
    memories: List[str] = Field(default_factory=list, description="Pre-loaded memories")
    components: Optional[Dict[str, Any]] = Field(None, description="Additional components")
    randomize_choices: bool = Field(True, description="Whether to randomize action choices")
    available_actions: Optional[List[str]] = Field(
        None,
        description="Per-agent available action names; overrides global list if set"
    )
    nested_simulation: Optional[NestedSimulationConfig] = Field(
        None,
        description="Optional nested simulation this agent can run"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "agent-1",
                "name": "Alice",
                "prefab": "basic__Entity",
                "goal": "Make new friends",
                "memories": ["Alice is a software engineer.", "Alice loves hiking."],
                "randomize_choices": True
            }
        }


class VariableConfig(BaseModel):
    """Configuration for a grounded variable."""
    name: str = Field(..., description="Variable name")
    variable_type: Literal["numerical", "categorical", "boolean", "percentage"] = Field(
        "numerical",
        description="Type of variable"
    )
    description: str = Field("", description="Variable description")
    default_value: Optional[Any] = Field(None, description="Default value")
    min_value: Optional[float] = Field(None, description="Minimum value (for numerical/percentage)")
    max_value: Optional[float] = Field(None, description="Maximum value (for numerical/percentage)")
    allowed_values: Optional[List[str]] = Field(None, description="Allowed values (for categorical)")
    update_rule: Optional[str] = Field(None, description="Description of how variable updates")


class AvailableAction(BaseModel):
    """An available action that agents can choose from."""
    name: str = Field(..., description="Action name (e.g., 'go_to_work')")
    description: str = Field("", description="What this action means")
    available_to: Optional[List[str]] = Field(None, description="Agent IDs that can use this; None means all")
    condition: Optional[str] = Field(None, description="When this action is available (free text)")


class ContribComponentConfig(BaseModel):
    """Configuration for a contrib GM component."""
    component_id: str = Field(..., description="Registry ID (e.g. 'death', 'npc_event_generator')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Component-specific parameters")


class GameMasterConfig(BaseModel):
    """Configuration for the game master."""
    prefab: str = Field(..., description="Game master prefab type")
    name: str = Field(..., description="Game master name")
    acting_order: ActingOrder = Field(
        default=ActingOrder.GAME_MASTER_CHOICE,
        description="How to choose the next actor"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional prefab-specific parameters"
    )
    grounded_variables: Optional[List[VariableConfig]] = Field(
        None,
        description="Optional grounded variables to track during simulation"
    )
    critical_decision_points: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional critical decision points that trigger variable changes at specific steps"
    )
    contrib_components: Optional[List[ContribComponentConfig]] = Field(
        None,
        description="Optional contrib GM components to add (Death, GMWorkingMemory, etc.)"
    )
    allow_early_termination: bool = Field(
        True,
        description="If False, simulation always runs to max_steps (disables LLM-driven early termination)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prefab": "generic__GameMaster",
                "name": "default rules",
                "acting_order": "game_master_choice",
                "parameters": {}
            }
        }


class ClockConfig(BaseModel):
    """Configuration for simulation clock behavior."""
    clock_type: ClockType = Field(
        default=ClockType.FIXED_INCREMENT,
        description="Clock behavior strategy"
    )
    start_time: Optional[str] = Field(
        None,
        description="Clock initial time string"
    )
    increment_minutes: int = Field(
        15,
        ge=1,
        le=1440,
        description="Base step size in minutes"
    )
    variable_increment_rules: Optional[Dict[int, int]] = Field(
        None,
        description="Hour -> minutes increment map for multi-interval clocks"
    )
    clock_description: Optional[str] = Field(
        None,
        description="Instructions/prompt used by generative clocks"
    )


class SimulationConfig(BaseModel):
    """Main simulation configuration."""
    premise: str = Field(..., description="Initial scenario description")
    max_steps: int = Field(100, ge=1, le=1000, description="Maximum simulation steps")
    engine_type: EngineType = Field(
        default=EngineType.SEQUENTIAL,
        description="Simulation engine type"
    )
    agents: List[AgentConfig] = Field(
        ...,
        min_items=1,
        description="List of agents in the simulation"
    )
    game_master: GameMasterConfig = Field(..., description="Game master configuration")
    shared_memories: List[str] = Field(
        default_factory=list,
        description="Shared world knowledge"
    )
    player_specific_context: Optional[Dict[str, str]] = Field(
        None,
        description="Character-specific context (for formative memories initializer)"
    )
    player_specific_memories: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Per-character memory lists (for formative memories initializer)"
    )
    checkpoint_interval: int = Field(
        5,
        ge=1,
        le=100,
        description="Save partial checkpoint every N steps (0 to disable)"
    )
    available_actions: Optional[List[AvailableAction]] = Field(
        None,
        description="Global set of available actions. When set, agents choose from these."
    )
    clock: Optional[ClockConfig] = Field(
        None,
        description="Optional clock configuration independent from game_master.parameters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "premise": "Alice and Bob meet at a coffee shop.",
                "max_steps": 10,
                "engine_type": "sequential",
                "agents": [
                    {
                        "id": "agent-1",
                        "name": "Alice",
                        "prefab": "basic__Entity",
                        "goal": "Make new friends"
                    },
                    {
                        "id": "agent-2",
                        "name": "Bob",
                        "prefab": "basic__Entity",
                        "goal": "Find a business partner"
                    }
                ],
                "game_master": {
                    "prefab": "generic__GameMaster",
                    "name": "default rules",
                    "acting_order": "fixed"
                },
                "shared_memories": ["The year is 2024."]
            }
        }


class LLMSettings(BaseModel):
    """LLM provider settings for simulation execution."""
    provider: LLMProvider = Field(..., description="LLM provider")
    model_name: str = Field(..., description="Model name or deployment name (for Azure OpenAI: use deployment name)")
    api_key: Optional[str] = Field(None, description="API key (optional, can use env). For Azure OpenAI, use AZURE_OAI_KEY")
    base_url: Optional[str] = Field(None, description="Custom base URL for OpenAI-compatible APIs. For Azure OpenAI, use AZURE_OAI_ENDPOINT")
    embedder_model: str = Field("all-MiniLM-L6-v2", description="Sentence transformer model")
    temperature: float = Field(0.5, ge=0, le=2, description="Sampling temperature")  # Match Concordia's DEFAULT_TEMPERATURE
    max_tokens: int = Field(16384, ge=1, le=65536, description="Maximum tokens to generate")
    api_version: Optional[str] = Field(None, description="API version for Azure OpenAI (e.g., '2024-02-15-preview'). Env: AZURE_OAI_API_VERSION")
    request_timeout: int = Field(300, ge=10, le=600, description="Per-request timeout in seconds for LLM calls")

    # Validators to strip whitespace from string fields
    @field_validator('model_name', 'base_url', 'api_key', mode='before')
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from string fields."""
        if v is None:
            return None
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model_name": "gpt-4o",
                "embedder_model": "all-MiniLM-L6-v2",
                "temperature": 0.5,
                "max_tokens": 16384
            }
        }


class ExecutionRequest(BaseModel):
    """Request to execute a simulation."""
    config: SimulationConfig
    llm_settings: LLMSettings
    gm_llm_settings: Optional[LLMSettings] = Field(
        None,
        description="Optional separate LLM settings for the Game Master. If not set, uses llm_settings."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "premise": "Alice and Bob meet at a coffee shop.",
                    "max_steps": 10,
                    "engine_type": "sequential",
                    "agents": [
                        {
                            "id": "agent-1",
                            "name": "Alice",
                            "prefab": "basic__Entity",
                            "goal": "Make new friends"
                        }
                    ]
                },
                "llm_settings": {
                    "provider": "gemini",
                    "model": "gemini-2.0-flash-exp"
                }
            }
        }


class ComponentValidationRequest(BaseModel):
    """Request to validate component parameters."""
    template_id: str = Field(..., description="Component template ID")
    parameters: Dict[str, Any] = Field(..., description="Parameters to validate")


# Simulation event types for streaming
class EventType(str, Enum):
    """Types of simulation events."""
    SIMULATION_START = "simulation_start"
    STEP_PROGRESS = "step_progress"
    STEP_START = "step_start"
    AGENT_ACT = "agent_act"
    OBSERVATION = "observation"
    STEP_END = "step_end"
    SIMULATION_COMPLETE = "simulation_complete"
    STEP_DATA = "step_data"
    CONTROLLER_STATE = "controller_state"
    ERROR = "error"


class SimulationEvent(BaseModel):
    """A simulation event for streaming."""
    type: EventType
    step: Optional[int] = None
    agent: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


class PrefabInfo(BaseModel):
    """Information about available prefabs."""
    name: str
    type: Literal["entity", "game_master", "initializer"]
    description: str
    required_params: List[str]
    optional_params: List[str]


class ValidationResult(BaseModel):
    """Result of configuration validation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SimulationResult(BaseModel):
    """Final result of a completed simulation."""
    config: SimulationConfig
    steps_completed: int
    events: List[SimulationEvent]
    final_summary: Optional[str] = None
    html_log: Optional[str] = None


class GroundedVariablesExtractionRequest(BaseModel):
    """Request to extract grounded variables from a completed simulation."""
    simulation_id: str = Field(..., description="ID of the simulation")
    html_file_path: str = Field(..., description="Path to the HTML log file")
    llm_settings: LLMSettings = Field(..., description="LLM configuration for extraction")

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "20260109_185806",
                "html_file_path": "20260109_185806_simulation.html",
                "llm_settings": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.0
                }
            }
        }


class FormativeMemoryRequest(BaseModel):
    """Request to generate formative memories for an agent."""
    agent_name: str = Field(..., description="Name of the agent")
    agent_context: str = Field("", description="Character-specific context")
    shared_memories: List[str] = Field(default_factory=list, description="Shared world knowledge")
    sentences_per_episode: int = Field(5, ge=1, le=20, description="Sentences per memory episode")
    llm_settings: LLMSettings


class FormativeMemoryResponse(BaseModel):
    """Response containing generated formative memories."""
    memories: List[str]


class PersonaGenerationRequest(BaseModel):
    """Request to generate diverse agent personas."""
    context: str = Field(..., description="Shared scenario context for all personas")
    diversity_axes: List[str] = Field(..., min_length=1, description="Axes along which to vary personas")
    num_personas: int = Field(5, ge=1, le=20, description="Number of personas to generate")
    num_memories: int = Field(5, ge=1, le=15, description="Memories per persona")
    llm_settings: LLMSettings = Field(..., description="LLM settings for generation")


class GeneratedPersona(BaseModel):
    """A generated persona."""
    name: str
    goal: str = ""
    memories: List[str] = Field(default_factory=list)
    description: str = ""


class PersonaGenerationResponse(BaseModel):
    """Response containing generated personas."""
    personas: List[GeneratedPersona]


class CensusDistributionSpec(BaseModel):
    """Demographic distribution specification for census-based agent generation."""
    dimensions: Optional[Dict[str, Dict[str, float]]] = Field(
        None,
        description="Independent marginals: {dim_name: {category: probability}}"
    )
    joint_profiles: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Joint profiles: [{weight: float, dim1: val1, ...}]"
    )


class CensusGenerationRequest(BaseModel):
    """Request to generate agents from a demographic distribution."""
    distribution: CensusDistributionSpec = Field(..., description="Demographic distribution spec")
    num_agents: int = Field(10, ge=1, le=100, description="Number of agents to generate")
    context: str = Field("", description="Scenario context for memory enrichment")
    enrich_with_llm: bool = Field(False, description="Use LLM to generate richer memories")
    num_memories: int = Field(5, ge=1, le=15, description="Memories per agent (if LLM enrichment)")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    llm_settings: Optional[LLMSettings] = Field(None, description="Required if enrich_with_llm is True")


class CensusGenerationResponse(BaseModel):
    """Response containing census-generated personas."""
    personas: List[GeneratedPersona]
    distribution_summary: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Actual counts per dimension after sampling"
    )


class SweepParameter(BaseModel):
    """A parameter to sweep across batch runs."""
    field: str = Field(..., description="Parameter field path (e.g., 'temperature', 'max_steps')")
    values: List[Any] = Field(..., min_length=1, description="Values to sweep over")


class BatchRunRequest(BaseModel):
    """Request to execute a batch of simulation runs."""
    config: SimulationConfig
    llm_settings: LLMSettings
    gm_llm_settings: Optional[LLMSettings] = None
    num_runs: int = Field(3, ge=1, le=50, description="Number of runs per parameter combination")
    sweep_parameters: List[SweepParameter] = Field(default_factory=list)
    batch_name: Optional[str] = Field(None, description="Human-readable batch name")


# Resolve forward references
NestedSimulationConfig.model_rebuild()
AgentConfig.model_rebuild()
