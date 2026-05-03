/**
 * API client for communicating with the Concordia Simulation Builder backend.
 */
import axios from 'axios';
import type {
  SimulationConfig,
  LLMSettings,
  ValidationResult,
  PrefabsResponseData,
  ProviderInfo,
  SimulationTemplate
} from '../types/simulation';

// API base URL - default to localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Simulation timeout in milliseconds (default: 5 hours)
// Can be overridden via VITE_SIMULATION_TIMEOUT environment variable
const SIMULATION_TIMEOUT = parseInt(import.meta.env.VITE_SIMULATION_TIMEOUT || '18000000', 10);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get all available prefabs
 */
export async function getPrefabs(): Promise<PrefabsResponseData> {
  const response = await api.get('/api/simulations/prefabs');
  return response.data;
}

/**
 * Get all available LLM providers
 */
export async function getProviders(): Promise<ProviderInfo[]> {
  const response = await api.get('/api/simulations/providers');
  return response.data;
}

/**
 * Get all available component templates
 */
export async function getComponentTemplates(): Promise<{
  templates: Array<{
    id: string;
    name: string;
    description: string;
    parameters: Record<string, any>;
    category: string;
  }>;
}> {
  const response = await api.get('/api/simulations/components/templates');
  return response.data;
}

/**
 * Validate component parameters
 */
export async function validateComponentParameters(
  templateId: string,
  parameters: Record<string, any>
): Promise<{ valid: boolean; errors: string[] }> {
  const response = await api.post('/api/simulations/components/validate', {
    template_id: templateId,
    parameters
  });
  return response.data;
}

/**
 * Get available contrib GM components
 */
export async function getContribComponents(): Promise<{
  components: Array<{
    id: string;
    name: string;
    description: string;
    category: string;
    params: Record<string, { type: string; default?: any; min?: number; max?: number; description?: string }>;
  }>;
}> {
  const response = await api.get('/api/simulations/contrib-components');
  return response.data;
}

/**
 * Validate a simulation configuration
 */
export async function validateConfig(config: SimulationConfig): Promise<ValidationResult> {
  // Remove player_specific_context for validation as it's not used by basic simulations
  const { player_specific_context, ...configToValidate } = config as any;
  const response = await api.post('/api/simulations/validate', configToValidate);
  return response.data;
}

/**
 * Execute a simulation with SSE streaming
 * Returns an EventSource for listening to events
 *
 * Note: EventSource doesn't support POST requests with body, so we use fetch
 * to get a streaming response and parse SSE events manually.
 */
export async function executeSimulationStream(
  config: SimulationConfig,
  llmSettings: LLMSettings,
  onProgress?: (progress: { step: number; max_steps: number; elapsed: number; est_remaining: number; est_time_str: string }) => void,
  onComplete?: (result: any) => void,
  onError?: (error: string) => void,
  onStepData?: (data: { step: number; acting_entity: string; action: string; entity_actions: Record<string, string> }) => void,
  onControllerState?: (data: { state: string; message?: string; task_id?: string }) => void,
  gmLlmSettings?: LLMSettings | null,
): Promise<void> {
  // Remove player_specific_context for execution
  const { player_specific_context, ...configToUse } = config as any;

  console.log('[executeSimulationStream] Starting...', { API_BASE_URL, config: configToUse, llmSettings });

  try {
    const body: any = {
      config: configToUse,
      llm_settings: llmSettings,
    };
    if (gmLlmSettings) {
      body.gm_llm_settings = gmLlmSettings;
    }

    const response = await fetch(`${API_BASE_URL}/api/simulations/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('[executeSimulationStream] Response received:', { ok: response.ok, status: response.status, statusText: response.statusText, contentType: response.headers.get('content-type') });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is null');
    }

    let buffer = '';
    let eventCount = 0;

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        console.log('[executeSimulationStream] Stream done. Total events:', eventCount);
        console.log('[executeSimulationStream] Final buffer state:', { bufferLength: buffer.length, buffer: buffer.length > 0 ? buffer : '(empty)' });
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      console.log('[executeSimulationStream] Chunk received, buffer length:', buffer.length);

      // Process SSE events
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        if (line.startsWith('event:')) {
          const eventType = line.substring(6).trim();
          console.log('[executeSimulationStream] Event type:', eventType);

          // Next line should be "data: ..."
          if (i + 1 < lines.length) {
            const dataLine = lines[i + 1];
            if (dataLine.startsWith('data:')) {
              try {
                const data = JSON.parse(dataLine.substring(5).trim());
                console.log('[executeSimulationStream] Event data:', data);

                switch (eventType) {
                  case 'simulation_start':
                    console.log('[executeSimulationStream] Simulation started:', data.message, 'task_id:', data.task_id);
                    if (data.task_id) {
                      onProgress?.({ step: 0, max_steps: 0, elapsed: 0, est_remaining: 0, est_time_str: '', task_id: data.task_id } as any);
                    }
                    eventCount++;
                    break;
                  case 'step_progress':
                    console.log('[executeSimulationStream] Calling onProgress with:', data);
                    onProgress?.(data);
                    eventCount++;
                    break;
                  case 'simulation_complete':
                    console.log('[executeSimulationStream] Calling onComplete');
                    // Fetch the full log content from the server
                    if (data.log_filename) {
                      console.log('[executeSimulationStream] Fetching log content from:', data.log_filename);
                      fetch(`${API_BASE_URL}/api/simulations/logs/${data.log_filename}`)
                        .then(response => response.json())
                        .then(logData => {
                          console.log('[executeSimulationStream] Log content fetched, length:', logData.html_content?.length);
                          // Add the HTML content to the completion data
                          onComplete?.({
                            ...data,
                            results: logData.html_content,
                            timestamp: logData.modified
                          });
                        })
                        .catch(err => {
                          console.error('[executeSimulationStream] Failed to fetch log content:', err);
                          // Still call onComplete even if fetch fails
                          onComplete?.(data);
                        });
                    } else {
                      onComplete?.(data);
                    }
                    eventCount++;
                    break;
                  case 'step_data':
                    console.log('[executeSimulationStream] Step data:', data);
                    onStepData?.(data);
                    eventCount++;
                    break;
                  case 'controller_state':
                    console.log('[executeSimulationStream] Controller state:', data);
                    onControllerState?.(data);
                    eventCount++;
                    break;
                  case 'error':
                    console.log('[executeSimulationStream] Calling onError');
                    onError?.(data.error || 'Unknown error');
                    eventCount++;
                    break;
                  default:
                    console.log('[executeSimulationStream] Unhandled event type:', eventType);
                }
              } catch (e) {
                console.error('[executeSimulationStream] Failed to parse SSE data:', e, 'Line:', dataLine);
              }

              i++; // Skip data line as we've processed it
            }
          }
        }
      }
    }
    console.log('[executeSimulationStream] Exiting normally (stream ended)');
  } catch (error: any) {
    console.error('[executeSimulationStream] Error:', error);
    onError?.(error.message || 'Failed to execute simulation');
  }
}

/**
 * Execute a simulation (simple non-streaming version for testing)
 */
export async function executeSimulationSimple(
  config: SimulationConfig,
  llmSettings: LLMSettings
): Promise<any> {
  // Remove player_specific_context for execution
  const { player_specific_context, ...configToUse } = config as any;
  const response = await api.post('/api/simulations/execute-simple', {
    config: configToUse,
    llm_settings: llmSettings
  }, {
    timeout: SIMULATION_TIMEOUT, // Configurable timeout (default: 30 minutes)
  });
  return response.data;
}

/**
 * Get a blank configuration template
 */
export async function exportTemplate(): Promise<SimulationConfig> {
  const response = await api.get('/api/simulations/export-template');
  return response.data;
}

/**
 * Import a configuration from JSON
 */
export async function importConfig(configData: Record<string, any>): Promise<{
  config: SimulationConfig;
  validation: ValidationResult;
}> {
  const response = await api.post('/api/simulations/import', configData);
  return response.data;
}

/**
 * Get the peace negotiation template
 */
export async function getPeaceNegotiationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/peace-negotiation');
  return response.data;
}

/**
 * Get the coffee shop demo template
 */
export async function getCoffeeShopTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/coffee-shop');
  return response.data;
}

/**
 * Get the planning agent template (basic_with_plan__Entity)
 */
export async function getPlanningAgentTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/planning-agent');
  return response.data;
}

/**
 * Get the scripted entity template (basic_scripted__Entity)
 */
export async function getScriptedEntityTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/scripted-entity');
  return response.data;
}

/**
 * Get the dialogic conversation template (dialogic__GameMaster)
 */
export async function getDialogicConversationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/dialogic-conversation');
  return response.data;
}

/**
 * Get the strategic game template (game_theoretic_and_dramaturgic__GameMaster)
 */
export async function getStrategicGameTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/strategic-game');
  return response.data;
}

/**
 * Get the interviewer template (interviewer__GameMaster)
 */
export async function getInterviewerTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/interviewer');
  return response.data;
}

/**
 * Get the formative memories template (rich character backstories)
 */
export async function getFormativeMemoriesTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/formative-memories');
  return response.data;
}

/**
 * Get the marketplace template (marketplace__GameMaster)
 */
export async function getMarketplaceTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/marketplace');
  return response.data;
}

/**
 * Get the state formation template (SDG 16: Peace and Justice)
 */
export async function getStateFormationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/state-formation');
  return response.data;
}

/**
 * Get the labor action template (SDG 8: Decent Work)
 */
export async function getLaborActionTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/labor-action');
  return response.data;
}

/**
 * Get the fishery management template (SDG 14: Life Below Water)
 */
export async function getFisheryManagementTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/fishery-management');
  return response.data;
}

/**
 * Get the disaster response template (SDG 11/13: Sustainable Cities/Climate Action)
 */
export async function getDisasterResponseTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/disaster-response');
  return response.data;
}

/**
 * Get the inequality mobility template (SDG 10: Reduced Inequalities)
 */
export async function getInequalityMobilityTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/inequality-mobility');
  return response.data;
}

/**
 * Get the context-aware moderator template (NEW context_aware_scripted prefab demo)
 */
export async function getContextAwareModeratorTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/context-aware-moderator');
  return response.data;
}

/**
 * Get the vaccine hesitancy study template (Psychological Component System demo)
 */
export async function getVaccineHesitancyTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/vaccine-hesitancy');
  return response.data;
}

/**
 * Get the nested simulation demo template (PhoneGameMaster pattern demo)
 */
export async function getNestedSimulationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/nested-simulation-demo');
  return response.data;
}

/**
 * Get the grounded variables demo template (Grounded Variables tracking demo)
 */
export async function getGroundedVariablesTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/grounded-variables-demo');
  return response.data;
}

/**
 * Get the phishing attack simulation template (Cybersecurity tabletop exercise)
 */
export async function getPhishingAttackSimulationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/phishing-attack-simulation');
  return response.data;
}

/**
 * Get the urban gentrification simulation template (Urban economics & housing policy)
 */
export async function getUrbanGentrificationTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/urban-gentrification');
  return response.data;
}

/**
 * Get the rational negotiators template (rational__Entity demo)
 */
export async function getRationalNegotiatorsTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/rational-negotiators');
  return response.data;
}

/**
 * Get the social media discourse template (asynchronous engine demo)
 */
export async function getSocialMediaDiscourseTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/social-media-discourse');
  return response.data;
}

/**
 * Get the puppet wizard-of-oz template (puppet__Entity + simultaneous engine)
 */
export async function getPuppetWizardOfOzTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/puppet-wizard-of-oz');
  return response.data;
}

/**
 * Get the conversational debate template (conversational__Entity demo)
 */
export async function getConversationalDebateTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/conversational-debate');
  return response.data;
}

/**
 * Get the spaceship crisis template (space_ship GM from contrib)
 */
export async function getSpaceshipCrisisTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/spaceship-crisis');
  return response.data;
}

/**
 * Get the simultaneous auction template (simultaneous engine demo)
 */
export async function getSimultaneousAuctionTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/simultaneous-auction');
  return response.data;
}

/**
 * Get the step controller demo template
 */
export async function getStepControllerDemoTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/step-controller-demo');
  return response.data;
}

/**
 * Get the contrib GM components demo template
 */
export async function getContribGmComponentsDemoTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/contrib-gm-components-demo');
  return response.data;
}

/**
 * Get the formative memories demo template
 */
export async function getFormativeMemoriesDemoTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/formative-memories-demo');
  return response.data;
}

/**
 * Get the measurements demo template
 */
export async function getMeasurementsDemoTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/measurements-demo');
  return response.data;
}

/**
 * Get the nested simulation strategy template
 */
export async function getNestedSimStrategyTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/nested-sim-strategy');
  return response.data;
}

/**
 * Get available models for a specific provider
 * @param provider - The LLM provider (e.g., 'gemini', 'anthropic', 'openai', 'ollama')
 * @param api_key - Optional API key for authentication
 * @param base_url - Optional custom base URL (for Ollama)
 */
export async function getProviderModels(
  provider: string,
  api_key?: string,
  base_url?: string
): Promise<{ provider: string; models: Array<{ id: string; name: string; [key: string]: any }>; error?: string }> {
  const params: any = {};
  if (api_key) params.api_key = api_key;
  if (base_url) params.base_url = base_url;

  const response = await api.get(`/api/simulations/models/${provider}`, { params });
  return response.data;
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get('/health');
  return response.data;
}

/**
 * Get recent simulation logs
 */
export async function getRecentSimulations(limit: number = 20): Promise<any[]> {
  const response = await api.get('/api/simulations/recent', { params: { limit } });
  return response.data;
}

/**
 * Get a specific simulation log by filename
 */
export async function getSimulationLog(filename: string): Promise<{
  filename: string;
  path: string;
  size: number;
  modified: number;
  html_content: string;
}> {
  const response = await api.get(`/api/simulations/logs/${filename}`);
  return response.data;
}

/**
 * Get analytics for a simulation log
 */

// Nested simulation data structure
export interface NestedSimulationData {
  config: any;
  result_summary: string;
  found: boolean;
}

// Grounded variable data structure
export interface GroundedVariableData {
  name: string;
  type: string;
  description: string;
  current_value: any;
  history: Array<{
    step: number;
    value: any;
  }>;
}

// Component analysis data structure
export interface ComponentAnalysisData {
  [agentName: string]: Record<string, any>;
}

// Extended analytics interface
export interface SimulationAnalytics {
  filename: string;
  file_size: number;
  modified: number;
  total_steps: number;
  agents: string[];
  agent_actions: Record<string, number>;
  total_observations: number;
  interactions: any[];
  timeline: Array<{
    step: number;
    description: string;
    type: string;
  }>;
  word_count: number;
  character_count: number;
  premise?: string;
  gm_prefab?: string;
  llm?: { provider: string; model: string } | null;
  gm_llm?: { provider: string; model: string } | null;
  elapsed_seconds?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
  agent_details?: Record<string, {
    actions: Array<{
      step: number;
      text: string;
    }>;
    goal: string;
    memories: string[];
  }>;
  // NEW: Feature detection flags
  has_nested_sims: boolean;
  has_grounded_variables: boolean;
  has_components: boolean;
  has_measurements: boolean;
  // NEW: Feature-specific data
  nested_simulations: Record<string, NestedSimulationData>;
  grounded_variables: GroundedVariableData[];
  components: ComponentAnalysisData;
  measurements: Record<string, any[]>;
}

export async function getSimulationAnalytics(filename: string): Promise<SimulationAnalytics> {
  const response = await api.get(`/api/simulations/logs/${filename}/analytics`);
  return response.data;
}

/**
 * Extract grounded variables from a completed simulation
 */
export async function extractGroundedVariables(
  simulationId: string,
  htmlFilePath: string,
  llmSettings: LLMSettings
): Promise<{
  success: boolean;
  simulation_id: string;
  html_file: string;
  metadata_file: string;
  variables: Array<{
    name: string;
    type: string;
    description: string;
    initial_value: any;
    final_value: any;
    total_changes: number;
    changes: Array<{
      step: number;
      from: any;
      to: any;
    }>;
    history: Array<{
      step: number;
      value: any;
    }>;
  }>;
}> {
  const response = await api.post('/api/simulations/grounded-variables/extract', {
    simulation_id: simulationId,
    html_file_path: htmlFilePath,
    llm_settings: llmSettings
  });
  return response.data;
}

/**
 * Get extracted grounded variables for a simulation
 */
export async function getGroundedVariables(
  simulationId: string
): Promise<{
  success: boolean;
  simulation_id: string;
  metadata_file: string;
  variables: Array<{
    name: string;
    type: string;
    description: string;
    default_value: any;
    has_history: boolean;
    initial_value?: any;
    final_value?: any;
    total_changes?: number;
    changes?: Array<{
      step: number;
      from: any;
      to: any;
    }>;
    history?: Array<{
      step: number;
      value: any;
    }>;
  }>;
}> {
  const response = await api.get(`/api/simulations/grounded-variables/${simulationId}`);
  return response.data;
}

/**
 * Cancel a running simulation
 */
export async function cancelSimulation(taskId: string): Promise<{
  status: string;
  task_id: string;
  message: string;
}> {
  const response = await api.post(`/api/simulations/cancel/${taskId}`);
  return response.data;
}

export async function simulationPlay(taskId: string): Promise<{ status: string; task_id: string }> {
  const response = await api.post(`/api/simulations/control/${taskId}/play`);
  return response.data;
}

export async function simulationPause(taskId: string): Promise<{ status: string; task_id: string }> {
  const response = await api.post(`/api/simulations/control/${taskId}/pause`);
  return response.data;
}

export async function simulationStep(taskId: string): Promise<{ status: string; task_id: string }> {
  const response = await api.post(`/api/simulations/control/${taskId}/step`);
  return response.data;
}

export async function simulationStop(taskId: string): Promise<{ status: string; task_id: string }> {
  const response = await api.post(`/api/simulations/control/${taskId}/stop`);
  return response.data;
}

/**
 * Get status of all simulations
 */
export async function getSimulationsStatus(): Promise<Record<string, any>> {
  const response = await api.get('/api/simulations/status');
  return response.data;
}

/**
 * Get status of a specific simulation
 */
export async function getSimulationStatus(taskId: string): Promise<{
  task_id: string;
  status: string;
  started_at: string;
  steps_completed: number;
  error: string | null;
  config: {
    premise: string;
    max_steps: number;
    num_agents: number;
  };
}> {
  const response = await api.get(`/api/simulations/status/${taskId}`);
  return response.data;
}

/**
 * Get checkpoint files
 */
export async function getCheckpointFiles(): Promise<{
  success: boolean;
  checkpoints: Array<{
    filename: string;
    size: number;
    modified: number;
    path: string;
  }>;
  total_count: number;
  total_size: number;
}> {
  const response = await api.get('/api/simulations/logs/checkpoints');
  return response.data;
}

/**
 * Delete all checkpoint files
 */
export async function deleteCheckpointFiles(): Promise<{
  success: boolean;
  deleted_count: number;
  deleted_files: string[];
  message: string;
}> {
  const response = await api.delete('/api/simulations/logs/checkpoints');
  return response.data;
}

/**
 * Delete a simulation log and its metadata
 */
export async function deleteSimulationLog(filename: string): Promise<{
  success: boolean;
  deleted: string[];
}> {
  const response = await api.delete(`/api/simulations/logs/${encodeURIComponent(filename)}`);
  return response.data;
}

/**
 * Analyze a simulation log using LLM
 */
export async function analyzeSimulation(simulationId: string, llmSettings?: {
  provider?: string;
  model_name?: string;
  api_key?: string;
  temperature?: number;
  embedder_model?: string;
}): Promise<{
  success: boolean;
  simulation_id: string;
  log_file: string;
  analysis: {
    metadata: any;
    executive_summary: string;
    timeline: Array<{
      step: number;
      summary: string;
      details: string;
    }>;
    team_effectiveness: {
      analysis: string;
      agents_analyzed: number;
    };
    insights: {
      analysis: string;
      categories: string[];
    };
    recommendations: {
      recommendations: string;
      timeframes: string[];
    };
    analysis_date: string;
  };
}> {
  const response = await api.post('/api/simulations/analyze-simulation', {
    simulation_id: simulationId,
    llm_settings: llmSettings
  });
  return response.data;
}

export async function generateFormativeMemories(request: {
  agent_name: string;
  agent_context?: string;
  shared_memories?: string[];
  sentences_per_episode?: number;
  llm_settings: any;
}): Promise<{ memories: string[] }> {
  const response = await api.post('/api/simulations/generate-formative-memories', request);
  return response.data;
}

export async function generatePersonas(request: {
  context: string;
  diversity_axes: string[];
  num_personas: number;
  num_memories: number;
  llm_settings: any;
}): Promise<{ personas: Array<{ name: string; goal: string; memories: string[]; description: string }> }> {
  const response = await api.post('/api/simulations/generate-personas', request);
  return response.data;
}

export async function shutdownServer(): Promise<void> {
  await api.post('/api/server/shutdown');
}

export default api;
