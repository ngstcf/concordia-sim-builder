/**
 * TypeScript type definitions for simulation configuration and API responses.
 * These match the Pydantic schemas in backend/models/schemas.py
 */

// Type aliases for string literals (better API compatibility than enums)
export type EngineType = 'sequential' | 'simultaneous' | 'interview' | 'survey';
export type ActingOrder = 'fixed' | 'random' | 'game_master_choice';
export type LLMProvider = 'openai' | 'deepseek' | 'gemini' | 'anthropic' | 'glm' | 'ollama';
export type EventType = 'simulation_start' | 'step_start' | 'agent_act' | 'observation' | 'step_end' | 'simulation_complete' | 'error';

// Constants for enum-like usage
export const EngineType = {
  SEQUENTIAL: 'sequential' as EngineType,
  SIMULTANEOUS: 'simultaneous' as EngineType,
  INTERVIEW: 'interview' as EngineType,
  SURVEY: 'survey' as EngineType
};

export const ActingOrder = {
  FIXED: 'fixed' as ActingOrder,
  RANDOM: 'random' as ActingOrder,
  GAME_MASTER_CHOICE: 'game_master_choice' as ActingOrder
};

export const LLMProvider = {
  OPENAI: 'openai' as LLMProvider,
  DEEPSEEK: 'deepseek' as LLMProvider,
  GEMINI: 'gemini' as LLMProvider,
  ANTHROPIC: 'anthropic' as LLMProvider,
  GLM: 'glm' as LLMProvider,
  OLLAMA: 'ollama' as LLMProvider
};

export const EventType = {
  SIMULATION_START: 'simulation_start' as EventType,
  STEP_START: 'step_start' as EventType,
  AGENT_ACT: 'agent_act' as EventType,
  OBSERVATION: 'observation' as EventType,
  STEP_END: 'step_end' as EventType,
  SIMULATION_COMPLETE: 'simulation_complete' as EventType,
  ERROR: 'error' as EventType
};

// Agent Configuration
export interface AgentConfig {
  id: string;
  name: string;
  prefab: string;
  goal?: string;
  memories: string[];
  components?: Record<string, any>;
  randomize_choices: boolean;
}

// Game Master Configuration
export interface GameMasterConfig {
  prefab: string;
  name: string;
  acting_order: ActingOrder;
  parameters: Record<string, any>;
}

// Main Simulation Configuration
export interface SimulationConfig {
  premise: string;
  max_steps: number;
  engine_type: EngineType;
  agents: AgentConfig[];
  game_master: GameMasterConfig;
  shared_memories: string[];
  player_specific_context?: Record<string, string>;
}

// LLM Settings
export interface LLMSettings {
  provider: LLMProvider;
  model_name: string;
  api_key?: string;
  base_url?: string;
  embedder_model: string;
  temperature: number;
  max_tokens: number;
}

// Execution Request
export interface ExecutionRequest {
  config: SimulationConfig;
  llm_settings: LLMSettings;
}

// Simulation Event
export interface SimulationEvent {
  type: EventType;
  step?: number;
  agent?: string;
  data: Record<string, any>;
  timestamp: string;
}

// Prefab Information
export interface PrefabInfo {
  name: string;
  type: 'entity' | 'game_master' | 'initializer';
  description: string;
  required_params: string[];
  optional_params: string[];
}

export interface PrefabsResponse {
  entities: PrefabInfo[];
  game_masters: PrefabInfo[];
  initializers: PrefabInfo[];
}

// LLM Provider Information
export interface ProviderInfo {
  provider: LLMProvider;
  name: string;
  models: string[];
  requires_api_key: boolean;
}

// Validation Result
export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// Simulation Result
export interface SimulationResult {
  config: SimulationConfig;
  steps_completed: number;
  events: SimulationEvent[];
  final_summary?: string;
  html_log?: string;
}

// Template
export interface SimulationTemplate {
  name: string;
  description: string;
  config: SimulationConfig;
  llm_settings: LLMSettings;
}

// API Response wrappers
export interface PrefabsResponseData extends PrefabsResponse {}

export interface ValidateResponse extends ValidationResult {}

export interface TemplateResponse extends SimulationTemplate {}
