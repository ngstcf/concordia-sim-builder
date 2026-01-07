"""
Pydantic schemas for simulation configuration and API requests/responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


class EngineType(str, Enum):
    """Available simulation engine types."""
    SEQUENTIAL = "sequential"
    SIMULTANEOUS = "simultaneous"
    INTERVIEW = "interview"
    SURVEY = "survey"


class ActingOrder(str, Enum):
    """Game master acting order options."""
    FIXED = "fixed"
    RANDOM = "random"
    GAME_MASTER_CHOICE = "game_master_choice"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GLM = "glm"  # Zhipu AI (GLM models)


class AgentConfig(BaseModel):
    """Configuration for a simulation agent."""
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Display name of the agent")
    prefab: str = Field(..., description="Prefab type (e.g., 'basic__Entity')")
    goal: Optional[str] = Field(None, description="Agent's objective/goal")
    memories: List[str] = Field(default_factory=list, description="Pre-loaded memories")
    components: Optional[Dict[str, Any]] = Field(None, description="Additional components")
    randomize_choices: bool = Field(True, description="Whether to randomize action choices")

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

    class Config:
        json_schema_extra = {
            "example": {
                "prefab": "generic__GameMaster",
                "name": "default rules",
                "acting_order": "game_master_choice",
                "parameters": {}
            }
        }


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
    model_name: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key (optional, can use env)")
    base_url: Optional[str] = Field(None, description="Custom base URL for OpenAI-compatible APIs")
    embedder_model: str = Field("all-MiniLM-L6-v2", description="Sentence transformer model")
    temperature: float = Field(0.5, ge=0, le=2, description="Sampling temperature")  # Match Concordia's DEFAULT_TEMPERATURE
    max_tokens: int = Field(3500, ge=1, le=32000, description="Maximum tokens to generate")  # Increased for better response quality

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
                "model_name": "gpt-4",
                "embedder_model": "all-MiniLM-L6-v2",
                "temperature": 0.5,  # Match Concordia's DEFAULT_TEMPERATURE
                "max_tokens": 3500  # Increased for better response quality
            }
        }


class ExecutionRequest(BaseModel):
    """Request to execute a simulation."""
    config: SimulationConfig
    llm_settings: LLMSettings

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
                    ],
                    "game_master": {
                        "prefab": "generic__GameMaster",
                        "name": "Narrator",
                        "acting_order": "fixed"
                    }
                },
                "llm_settings": {
                    "provider": "deepseek",
                    "model_name": "deepseek-chat",
                    "embedder_model": "all-MiniLM-L6-v2",
                    "temperature": 1.0
                }
            }
        }


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
