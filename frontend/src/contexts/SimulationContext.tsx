/**
 * React Context for simulation state management.
 */
import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import type {
  SimulationConfig,
  AgentConfig,
  GameMasterConfig,
  LLMSettings,
  ValidationResult,
  SimulationEvent
} from '../types/simulation';

interface SimulationContextType {
  // Configuration
  config: SimulationConfig;
  setConfig: (config: SimulationConfig) => void;

  // Agent management
  addAgent: (agent: AgentConfig) => void;
  updateAgent: (id: string, agent: Partial<AgentConfig>) => void;
  removeAgent: (id: string) => void;
  reorderAgents: (fromIndex: number, toIndex: number) => void;

  // Game master
  setGameMaster: (gm: GameMasterConfig) => void;

  // Shared memories
  addSharedMemory: (memory: string) => void;
  removeSharedMemory: (index: number) => void;
  updateSharedMemory: (index: number, memory: string) => void;

  // LLM settings
  llmSettings: LLMSettings;
  setLLMSettings: (settings: LLMSettings) => void;

  // Optional separate GM LLM settings
  gmLlmSettings: LLMSettings | null;
  setGmLlmSettings: (settings: LLMSettings | null) => void;

  // Validation
  validation: ValidationResult | null;
  setValidation: (validation: ValidationResult | null) => void;

  // Simulation state
  isRunning: boolean;
  setIsRunning: (running: boolean) => void;
  events: SimulationEvent[];
  addEvent: (event: SimulationEvent) => void;
  clearEvents: () => void;
}

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

const defaultConfig: SimulationConfig = {
  premise: '',
  max_steps: 10,
  engine_type: 'sequential',
  agents: [],
  game_master: {
    prefab: 'generic__GameMaster',
    name: 'Game Master',
    acting_order: 'game_master_choice',
    parameters: {}
  },
  shared_memories: []
};

const defaultLLMSettings: LLMSettings = {
  provider: 'deepseek',
  model_name: 'deepseek-chat',
  embedder_model: 'all-MiniLM-L6-v2',
  temperature: 0.5,  // Match Concordia's DEFAULT_TEMPERATURE
  max_tokens: 3500,  // Increased for better response quality
  request_timeout: 120
};

interface SimulationProviderProps {
  children: ReactNode;
}

export function SimulationProvider({ children }: SimulationProviderProps) {
  const [config, setConfig] = useState<SimulationConfig>(defaultConfig);
  const [llmSettings, setLLMSettings] = useState<LLMSettings>(defaultLLMSettings);
  const [gmLlmSettings, setGmLlmSettings] = useState<LLMSettings | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<SimulationEvent[]>([]);

  // Agent management
  const addAgent = useCallback((agent: AgentConfig) => {
    setConfig(prev => ({
      ...prev,
      agents: [...prev.agents, agent]
    }));
  }, []);

  const updateAgent = useCallback((id: string, updates: Partial<AgentConfig>) => {
    setConfig(prev => ({
      ...prev,
      agents: prev.agents.map(a => a.id === id ? { ...a, ...updates } : a)
    }));
  }, []);

  const removeAgent = useCallback((id: string) => {
    setConfig(prev => ({
      ...prev,
      agents: prev.agents.filter(a => a.id !== id)
    }));
  }, []);

  const reorderAgents = useCallback((fromIndex: number, toIndex: number) => {
    setConfig(prev => {
      const agents = [...prev.agents];
      const [removed] = agents.splice(fromIndex, 1);
      agents.splice(toIndex, 0, removed);
      return { ...prev, agents };
    });
  }, []);

  // Game master
  const setGameMaster = useCallback((gm: GameMasterConfig) => {
    setConfig(prev => ({
      ...prev,
      game_master: gm
    }));
  }, []);

  // Shared memories
  const addSharedMemory = useCallback((memory: string) => {
    setConfig(prev => ({
      ...prev,
      shared_memories: [...prev.shared_memories, memory]
    }));
  }, []);

  const removeSharedMemory = useCallback((index: number) => {
    setConfig(prev => ({
      ...prev,
      shared_memories: prev.shared_memories.filter((_, i) => i !== index)
    }));
  }, []);

  const updateSharedMemory = useCallback((index: number, memory: string) => {
    setConfig(prev => ({
      ...prev,
      shared_memories: prev.shared_memories.map((m, i) => i === index ? memory : m)
    }));
  }, []);

  // Simulation events
  const addEvent = useCallback((event: SimulationEvent) => {
    setEvents(prev => [...prev, event]);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  const value: SimulationContextType = {
    config,
    setConfig,
    addAgent,
    updateAgent,
    removeAgent,
    reorderAgents,
    setGameMaster,
    addSharedMemory,
    removeSharedMemory,
    updateSharedMemory,
    llmSettings,
    setLLMSettings,
    gmLlmSettings,
    setGmLlmSettings,
    validation,
    setValidation,
    isRunning,
    setIsRunning,
    events,
    addEvent,
    clearEvents
  };

  return (
    <SimulationContext.Provider value={value}>
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation(): SimulationContextType {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
}
