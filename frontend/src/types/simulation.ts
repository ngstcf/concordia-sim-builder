/**
 * TypeScript type definitions for simulation configuration and API responses.
 * These match the Pydantic schemas in backend/models/schemas.py
 */

// Type aliases for string literals (better API compatibility than enums)
export type EngineType = 'sequential' | 'simultaneous' | 'asynchronous' | 'step_controller' | 'interview' | 'survey';
export type ClockType = 'multi_interval' | 'fixed_increment' | 'generative';
export type ActingOrder = 'fixed' | 'random' | 'game_master_choice';
export type LLMProvider = 'openai' | 'azure' | 'deepseek' | 'gemini' | 'anthropic' | 'glm' | 'ollama' | 'ollama_remote';
export type EventType = 'simulation_start' | 'step_start' | 'agent_act' | 'observation' | 'step_end' | 'simulation_complete' | 'error';

// Constants for enum-like usage
export const EngineType = {
  SEQUENTIAL: 'sequential' as EngineType,
  SIMULTANEOUS: 'simultaneous' as EngineType,
  ASYNCHRONOUS: 'asynchronous' as EngineType,
  STEP_CONTROLLER: 'step_controller' as EngineType,
  INTERVIEW: 'interview' as EngineType,
  SURVEY: 'survey' as EngineType
};

export const ClockType = {
  MULTI_INTERVAL: 'multi_interval' as ClockType,
  FIXED_INCREMENT: 'fixed_increment' as ClockType,
  GENERATIVE: 'generative' as ClockType
};

export const ActingOrder = {
  FIXED: 'fixed' as ActingOrder,
  RANDOM: 'random' as ActingOrder,
  GAME_MASTER_CHOICE: 'game_master_choice' as ActingOrder
};

export const LLMProvider = {
  OPENAI: 'openai' as LLMProvider,
  AZURE: 'azure' as LLMProvider,
  DEEPSEEK: 'deepseek' as LLMProvider,
  GEMINI: 'gemini' as LLMProvider,
  ANTHROPIC: 'anthropic' as LLMProvider,
  GLM: 'glm' as LLMProvider,
  OLLAMA: 'ollama' as LLMProvider,
  OLLAMA_REMOTE: 'ollama_remote' as LLMProvider
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

// Script line for scripted entities
export interface ScriptLine {
  name: string;
  line: string;
}

// Nested Simulation Configuration
export interface NestedSimulationConfig {
  premise: string;
  max_steps: number;
  agents: AgentConfig[];
  shared_memories: string[];
  extraction_prompt?: string;
}

// Variable Configuration for Grounded Variables
export interface VariableConfig {
  name: string;
  variable_type: 'numerical' | 'categorical' | 'boolean' | 'percentage';
  description: string;
  default_value?: any;
  min_value?: number;
  max_value?: number;
  allowed_values?: string[];
  update_rule?: string;
}

// Available Action
export interface AvailableAction {
  name: string;
  description: string;
  available_to?: string[];
  condition?: string;
}

// Agent Configuration
export interface AgentConfig {
  id: string;
  name: string;
  prefab: string;
  goal?: string;
  memories: string[];
  components?: Record<string, any>;
  randomize_choices: boolean;
  available_actions?: string[];
  nested_simulation?: NestedSimulationConfig;
}

// Contrib GM Component Configuration
export interface ContribComponentConfig {
  component_id: string;
  params: Record<string, any>;
}

// Game Master Configuration
export interface GameMasterConfig {
  prefab: string;
  name: string;
  acting_order: ActingOrder;
  parameters: Record<string, any>;
  grounded_variables?: VariableConfig[];
  critical_decision_points?: CriticalDecisionPoint[];
  contrib_components?: ContribComponentConfig[];
  allow_early_termination?: boolean;
}

export interface ClockConfig {
  clock_type: ClockType;
  start_time?: string;
  increment_minutes?: number;
  variable_increment_rules?: Record<number, number>;
  clock_description?: string;
}

// Critical Decision Point
export interface CriticalDecisionPoint {
  step: number;
  description: string;
  options: string[];
  // Legacy format support (Urban Gentrification uses 'event' instead of description/options)
  event?: string;
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
  checkpoint_interval?: number;
  available_actions?: AvailableAction[];
  clock?: ClockConfig;
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
  api_version?: string;  // For Azure OpenAI
  request_timeout: number;
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

// Persona Generation
export interface PersonaGenerationRequest {
  context: string;
  diversity_axes: string[];
  num_personas: number;
  num_memories: number;
  llm_settings: LLMSettings;
}

export interface GeneratedPersona {
  name: string;
  goal: string;
  memories: string[];
  description: string;
}

export interface PersonaGenerationResponse {
  personas: GeneratedPersona[];
}

// Census/Distribution-based Generation
export interface CensusDistributionSpec {
  dimensions?: Record<string, Record<string, number>>;
  joint_profiles?: Array<Record<string, any>>;
}

export interface CensusGenerationRequest {
  distribution: CensusDistributionSpec;
  num_agents: number;
  context?: string;
  enrich_with_llm?: boolean;
  num_memories?: number;
  seed?: number | null;
  llm_settings?: LLMSettings;
}

export interface CensusGenerationResponse {
  personas: GeneratedPersona[];
  distribution_summary: Record<string, Record<string, number>>;
}

// Batch Run
export interface SweepParameter {
  field: string;
  values: any[];
}

export interface BatchRunRequest {
  config: SimulationConfig;
  llm_settings: LLMSettings;
  gm_llm_settings?: LLMSettings;
  num_runs: number;
  sweep_parameters: SweepParameter[];
  batch_name?: string;
}

export interface BatchRunResult {
  run_index: number;
  parameters: Record<string, string>;
  repeat: number;
  status: string;
  elapsed_seconds?: number;
  log_filename?: string;
  error?: string;
}

export interface BatchReliabilityDimension {
  icc3_1: number | null;
  n_agents: number;
  n_runs: number;
  reason?: string;
}

export interface BatchReliabilityReport {
  available: boolean;
  reason?: string;
  n_runs_used?: number;
  dimensions?: Record<string, BatchReliabilityDimension>;
  overall_mean_icc3_1?: number | null;
}

// API Response wrappers
export interface PrefabsResponseData extends PrefabsResponse {}

export interface ValidateResponse extends ValidationResult {}

export interface TemplateResponse extends SimulationTemplate {}
