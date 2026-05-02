/**
 * AgentEditor Component
 * Modal for editing agent configuration
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { getComponentTemplates, getPrefabs, generateFormativeMemories } from '../../utils/api';
import type { ScriptLine } from '../../types/simulation';

interface PrefabInfo {
  name: string;
  description: string;
  type: string;
}

interface AgentEditorProps {
  agentId: string;
  onClose: () => void;
}

interface ScriptPrompt {
  id: string;
  name: string;
  line: string;
}

interface ComponentConfig {
  templateId: string;
  name: string;
  parameters: Record<string, any>;
}

export default function AgentEditor({ agentId, onClose }: AgentEditorProps) {
  const { config, updateAgent, llmSettings } = useSimulation();
  const agent = config.agents.find(a => a.id === agentId);

  const [name, setName] = useState(agent?.name || '');
  const [prefab, setPrefab] = useState(agent?.prefab || 'basic__Entity');
  const [goal, setGoal] = useState(agent?.goal || '');
  const [memories, setMemories] = useState(agent?.memories?.join('\n') || '');
  const [randomize, setRandomize] = useState(agent?.randomize_choices ?? true);
  const [scriptPrompts, setScriptPrompts] = useState<ScriptPrompt[]>([]);
  const [componentConfigs, setComponentConfigs] = useState<ComponentConfig[]>([]);
  const [availableComponents, setAvailableComponents] = useState<Array<{
    id: string;
    name: string;
    description: string;
    parameters: Record<string, any>;
    category: string;
  }>>([]);
  const [entityPrefabs, setEntityPrefabs] = useState<PrefabInfo[]>([]);

  // Prefab-specific parameters
  const [observationHistoryLength, setObservationHistoryLength] = useState<number | undefined>(undefined);
  const [situationPerceptionHistoryLength, setSituationPerceptionHistoryLength] = useState<number | undefined>(undefined);
  const [personBySituationHistoryLength, setPersonBySituationHistoryLength] = useState<number | undefined>(undefined);
  const [forceTimeHorizon, setForceTimeHorizon] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [fixedResponses, setFixedResponses] = useState<Array<{ key: string; value: string }>>([]);
  const [reasoningSteps, setReasoningSteps] = useState<Array<{ question: string; answer_prefix: string; num_memories: number; add_to_memory: boolean }>>([]);
  const [generatingBackstory, setGeneratingBackstory] = useState(false);
  const [backstoryContext, setBackstoryContext] = useState('');
  const [showBackstoryDialog, setShowBackstoryDialog] = useState(false);

  useEffect(() => {
    getComponentTemplates().then(data => {
      setAvailableComponents(data.templates);
    }).catch(err => {
      console.error('Failed to load component templates:', err);
    });

    getPrefabs().then(data => {
      setEntityPrefabs(data.entities);
    }).catch(err => {
      console.error('Failed to load prefabs:', err);
    });
  }, []);

  useEffect(() => {
    if (agent) {
      setName(agent.name);
      setPrefab(agent.prefab);
      setGoal(agent.goal || '');
      setMemories(agent.memories?.join('\n') || '');
      setRandomize(agent.randomize_choices ?? true);

      // Load existing script prompts if available
      const existingScript = agent.components?.script as ScriptLine[] | undefined;
      if (existingScript) {
        setScriptPrompts(existingScript.map((line, idx) => ({
          id: String(idx),
          name: line.name,
          line: line.line
        })));
      } else {
        setScriptPrompts([]);
      }

      // Load prefab-specific params from components
      const comps = agent.components || {};
      setObservationHistoryLength(comps.observation_history_length as number | undefined);
      setSituationPerceptionHistoryLength(comps.situation_perception_history_length as number | undefined);
      setPersonBySituationHistoryLength(comps.person_by_situation_history_length as number | undefined);
      setForceTimeHorizon(comps.force_time_horizon ? String(comps.force_time_horizon) : '');
      setCustomInstructions((comps.custom_instructions as string) || '');
      const fr = comps.fixed_responses as Record<string, string> | undefined;
      setFixedResponses(fr ? Object.entries(fr).map(([key, value]) => ({ key, value })) : []);
      const rs = comps.reasoning_steps as Array<any> | undefined;
      setReasoningSteps(rs || []);

      // Load existing component configurations (excluding script and prefab params)
      const prefabParamKeys = ['script', 'observation_history_length', 'situation_perception_history_length', 'person_by_situation_history_length', 'force_time_horizon', 'custom_instructions', 'fixed_responses', 'reasoning_steps'];
      const existingComponents = agent.components || {};
      const componentEntries = Object.entries(existingComponents)
        .filter(([key]) => !prefabParamKeys.includes(key))
        .map(([key, value]) => ({
          templateId: key,
          name: key,
          parameters: value as Record<string, any>
        }));
      setComponentConfigs(componentEntries);
    }
  }, [agent]);

  if (!agent) return null;

  const handleSave = () => {
    const isScriptedPrefab = prefab === 'basic_scripted__Entity' || prefab === 'context_aware_scripted__Entity';

    // Build components object
    const components: Record<string, any> = {};

    // Add script component if scripted prefab
    if (isScriptedPrefab && scriptPrompts.length > 0) {
      components.script = scriptPrompts.map(p => ({ name: p.name, line: p.line }));
    }

    // Add psychological component configurations
    componentConfigs.forEach(comp => {
      components[comp.templateId] = comp.parameters;
    });

    // Add prefab-specific parameters
    if (prefab === 'basic__Entity') {
      if (observationHistoryLength !== undefined) components.observation_history_length = observationHistoryLength;
      if (situationPerceptionHistoryLength !== undefined) components.situation_perception_history_length = situationPerceptionHistoryLength;
      if (personBySituationHistoryLength !== undefined) components.person_by_situation_history_length = personBySituationHistoryLength;
    }
    if (prefab === 'basic_with_plan__Entity' && forceTimeHorizon) {
      components.force_time_horizon = forceTimeHorizon;
    }
    if (prefab === 'minimal__Entity' && customInstructions) {
      components.custom_instructions = customInstructions;
    }
    if (prefab === 'puppet__Entity' && fixedResponses.length > 0) {
      const fr: Record<string, string> = {};
      fixedResponses.forEach(({ key, value }) => { if (key.trim()) fr[key] = value; });
      if (Object.keys(fr).length > 0) components.fixed_responses = fr;
    }
    if (prefab === 'minimal__Entity' && reasoningSteps.length > 0) {
      const validSteps = reasoningSteps.filter(s => s.question.trim());
      if (validSteps.length > 0) components.reasoning_steps = validSteps;
    }

    updateAgent(agentId, {
      name,
      prefab,
      goal: goal || undefined,
      memories: memories.split('\n').filter(m => m.trim()),
      randomize_choices: randomize,
      components: Object.keys(components).length > 0 ? components : undefined
    });
    onClose();
  };

  const addScriptPrompt = () => {
    setScriptPrompts([...scriptPrompts, {
      id: Date.now().toString(),
      name: name,
      line: ''
    }]);
  };

  const updateScriptPrompt = (id: string, field: 'name' | 'line', value: string) => {
    setScriptPrompts(scriptPrompts.map(p =>
      p.id === id ? { ...p, [field]: value } : p
    ));
  };

  const removeScriptPrompt = (id: string) => {
    setScriptPrompts(scriptPrompts.filter(p => p.id !== id));
  };

  const movePrompt = (index: number, direction: 'up' | 'down') => {
    const newPrompts = [...scriptPrompts];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex >= 0 && targetIndex < newPrompts.length) {
      [newPrompts[index], newPrompts[targetIndex]] = [newPrompts[targetIndex], newPrompts[index]];
      setScriptPrompts(newPrompts);
    }
  };

  const addComponent = (templateId: string) => {
    const template = availableComponents.find(c => c.id === templateId);
    if (!template) return;

    // Get default values for parameters
    const defaultParams: Record<string, any> = {};
    Object.entries(template.parameters).forEach(([key, config]: [string, any]) => {
      if (config.default !== undefined) {
        defaultParams[key] = config.default;
      }
    });

    setComponentConfigs([...componentConfigs, {
      templateId,
      name: template.name,
      parameters: defaultParams
    }]);
  };

  const updateComponentParameter = (index: number, paramKey: string, value: any) => {
    const newConfigs = [...componentConfigs];
    newConfigs[index].parameters[paramKey] = value;
    setComponentConfigs(newConfigs);
  };

  const removeComponent = (index: number) => {
    setComponentConfigs(componentConfigs.filter((_, i) => i !== index));
  };

  const handleGenerateBackstory = async () => {
    setGeneratingBackstory(true);
    try {
      const result = await generateFormativeMemories({
        agent_name: name,
        agent_context: backstoryContext,
        shared_memories: config.shared_memories,
        sentences_per_episode: 5,
        llm_settings: llmSettings,
      });
      const existing = memories.trim();
      const newMemories = result.memories.filter(m => m.trim());
      setMemories(existing ? existing + '\n' + newMemories.join('\n') : newMemories.join('\n'));
      setShowBackstoryDialog(false);
      setBackstoryContext('');
    } catch (err: any) {
      alert('Backstory generation failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGeneratingBackstory(false);
    }
  };

  const isScripted = prefab === 'basic_scripted__Entity' || prefab === 'context_aware_scripted__Entity';

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Edit Agent</h3>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Prefab */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Prefab Type</label>
            <select
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              value={prefab}
              onChange={(e) => setPrefab(e.target.value)}
            >
              {entityPrefabs.length > 0 ? (
                <>
                  <optgroup label="Standard">
                    {entityPrefabs.filter(p => ['basic__Entity', 'basic_with_plan__Entity', 'minimal__Entity'].includes(p.name)).map(p => (
                      <option key={p.name} value={p.name}>{p.name.replace('__Entity', '')}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Scripted">
                    {entityPrefabs.filter(p => p.name.includes('scripted')).map(p => (
                      <option key={p.name} value={p.name}>{p.name.replace('__Entity', '')}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Specialized">
                    {entityPrefabs.filter(p => ['conversational__Entity', 'rational__Entity', 'puppet__Entity', 'fake_assistant_with_configurable_system_prompt__Entity'].includes(p.name)).map(p => (
                      <option key={p.name} value={p.name}>{p.name.replace('__Entity', '')}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Experimental">
                    {entityPrefabs.filter(p => p.name.includes('image') || p.name.includes('companion')).map(p => (
                      <option key={p.name} value={p.name}>{p.name.replace('__Entity', '').replace('__AICompanionEntity', ' (AI)').replace('__HumanUserEntity', ' (Human)')}</option>
                    ))}
                  </optgroup>
                </>
              ) : (
                <>
                  <option value="basic__Entity">basic</option>
                  <option value="basic_with_plan__Entity">basic_with_plan</option>
                  <option value="basic_scripted__Entity">basic_scripted</option>
                  <option value="context_aware_scripted__Entity">context_aware_scripted</option>
                  <option value="minimal__Entity">minimal</option>
                </>
              )}
            </select>
            {(() => {
              const selected = entityPrefabs.find(p => p.name === prefab);
              return selected ? (
                <p className="mt-1 text-xs text-gray-500">{selected.description}</p>
              ) : null;
            })()}
          </div>

          {/* Goal */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Goal (Optional)</label>
            <textarea
              rows={2}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              placeholder="What is this agent trying to achieve?"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
            />
          </div>

          {/* Memories */}
          <div>
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">Pre-loaded Memories</label>
              <button
                type="button"
                onClick={() => setShowBackstoryDialog(!showBackstoryDialog)}
                disabled={generatingBackstory || !name.trim()}
                className="text-sm text-emerald-600 hover:text-emerald-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generatingBackstory ? 'Generating...' : 'Generate Backstory'}
              </button>
            </div>

            {showBackstoryDialog && (
              <div className="mt-2 p-3 bg-emerald-50 border border-emerald-200 rounded-md">
                <p className="text-xs text-gray-600 mb-2">
                  Generate formative memories using LLM. Shared memories from the scenario will be included automatically.
                </p>
                <textarea
                  rows={3}
                  className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm mb-2"
                  value={backstoryContext}
                  onChange={(e) => setBackstoryContext(e.target.value)}
                  placeholder="Optional: Describe this character's background, role, or personality..."
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => { setShowBackstoryDialog(false); setBackstoryContext(''); }}
                    className="text-xs px-3 py-1 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleGenerateBackstory}
                    disabled={generatingBackstory}
                    className="text-xs px-3 py-1.5 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {generatingBackstory ? 'Generating...' : 'Generate'}
                  </button>
                </div>
              </div>
            )}

            <textarea
              rows={6}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-sm"
              placeholder="One memory per line..."
              value={memories}
              onChange={(e) => setMemories(e.target.value)}
            />
            <p className="mt-1 text-xs text-gray-500">Enter one memory per line</p>
          </div>

          {/* Randomize Choices */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="randomize"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              checked={randomize}
              onChange={(e) => setRandomize(e.target.checked)}
            />
            <label htmlFor="randomize" className="ml-2 block text-sm text-gray-900">
              Randomize action choices
            </label>
          </div>

          {/* Prefab-Specific Settings */}
          {(prefab === 'basic__Entity' || prefab === 'basic_with_plan__Entity' || prefab === 'minimal__Entity' || prefab === 'puppet__Entity') && (
            <div className="border-t border-gray-200 pt-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <span className="flex items-center">
                  <svg className="h-4 w-4 text-indigo-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Prefab Settings
                  <span className="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
                    {prefab.replace('__Entity', '')}
                  </span>
                </span>
              </label>

              <div className="space-y-3 bg-indigo-50 p-3 rounded-md border border-indigo-200">
                {/* basic__Entity: memory/perception history lengths */}
                {prefab === 'basic__Entity' && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Observation History Length</label>
                      <input
                        type="number" min={10} max={10000}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                        value={observationHistoryLength ?? ''}
                        onChange={e => setObservationHistoryLength(e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Default: 1000000"
                      />
                      <p className="text-[11px] text-gray-500 mt-0.5">How many observations the agent retains in working memory.</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Situation Perception Depth</label>
                      <input
                        type="number" min={1} max={100}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                        value={situationPerceptionHistoryLength ?? ''}
                        onChange={e => setSituationPerceptionHistoryLength(e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Default: 25"
                      />
                      <p className="text-[11px] text-gray-500 mt-0.5">Memories retrieved when agent asks "What situation am I in?"</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Person-by-Situation Depth</label>
                      <input
                        type="number" min={1} max={50}
                        className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                        value={personBySituationHistoryLength ?? ''}
                        onChange={e => setPersonBySituationHistoryLength(e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Default: 5"
                      />
                      <p className="text-[11px] text-gray-500 mt-0.5">Memories retrieved when agent asks "What would someone like me do?"</p>
                    </div>
                  </>
                )}

                {/* basic_with_plan__Entity: force_time_horizon */}
                {prefab === 'basic_with_plan__Entity' && (
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Force Time Horizon</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={forceTimeHorizon}
                      onChange={e => setForceTimeHorizon(e.target.value)}
                      placeholder='e.g., "the next 24 hours" (empty = LLM decides)'
                    />
                    <p className="text-[11px] text-gray-500 mt-0.5">Fixed time horizon for planning. Leave empty to let the agent decide dynamically.</p>
                  </div>
                )}

                {/* minimal__Entity: custom_instructions */}
                {prefab === 'minimal__Entity' && (
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Custom Instructions</label>
                    <textarea
                      rows={3}
                      className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={customInstructions}
                      onChange={e => setCustomInstructions(e.target.value)}
                      placeholder="Custom behavioral instructions for this agent (replaces default instructions)..."
                    />
                    <p className="text-[11px] text-gray-500 mt-0.5">Overrides the default instruction text. Use for highly customized agent behavior.</p>
                  </div>
                )}

                {/* puppet__Entity: fixed_responses */}
                {prefab === 'puppet__Entity' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-xs font-medium text-gray-700">Fixed Responses</label>
                      <button
                        type="button"
                        onClick={() => setFixedResponses([...fixedResponses, { key: '', value: '' }])}
                        className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        + Add Response
                      </button>
                    </div>
                    {fixedResponses.length === 0 ? (
                      <p className="text-xs text-gray-500 italic">No fixed responses. Agent will use LLM for all actions.</p>
                    ) : (
                      <div className="space-y-2">
                        {fixedResponses.map((fr, idx) => (
                          <div key={idx} className="flex gap-2 items-start">
                            <div className="flex-1">
                              <input
                                type="text"
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                value={fr.key}
                                onChange={e => {
                                  const updated = [...fixedResponses];
                                  updated[idx] = { ...fr, key: e.target.value };
                                  setFixedResponses(updated);
                                }}
                                placeholder="Call-to-action trigger..."
                              />
                            </div>
                            <div className="flex-1">
                              <input
                                type="text"
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                value={fr.value}
                                onChange={e => {
                                  const updated = [...fixedResponses];
                                  updated[idx] = { ...fr, value: e.target.value };
                                  setFixedResponses(updated);
                                }}
                                placeholder="Fixed response..."
                              />
                            </div>
                            <button
                              type="button"
                              onClick={() => setFixedResponses(fixedResponses.filter((_, i) => i !== idx))}
                              className="text-red-400 hover:text-red-600 text-xs p-1"
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <p className="text-[11px] text-gray-500 mt-1">Map call-to-action prompts to predetermined responses. Unmatched actions fall back to LLM.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Reasoning Steps - only for minimal__Entity */}
          {prefab === 'minimal__Entity' && (
            <div className="border-t border-gray-200 pt-4">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  <span className="flex items-center">
                    <svg className="h-4 w-4 text-amber-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    Custom Reasoning Steps
                    <span className="ml-2 text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">Cognition</span>
                  </span>
                </label>
                <button
                  type="button"
                  onClick={() => setReasoningSteps([...reasoningSteps, { question: '', answer_prefix: '{agent_name} thinks: ', num_memories: 10, add_to_memory: false }])}
                  className="text-sm text-amber-600 hover:text-amber-700 font-medium"
                >
                  + Add Step
                </button>
              </div>

              {reasoningSteps.length === 0 ? (
                <p className="text-sm text-gray-500 italic">
                  No custom reasoning steps. The agent uses default three-question reasoning.
                </p>
              ) : (
                <div className="space-y-3">
                  {reasoningSteps.map((step, index) => (
                    <div key={index} className="border border-amber-200 rounded-md p-3 bg-amber-50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-amber-700">Step {index + 1}</span>
                        <button
                          type="button"
                          onClick={() => setReasoningSteps(reasoningSteps.filter((_, i) => i !== index))}
                          className="text-red-400 hover:text-red-600 text-xs"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Question</label>
                          <textarea
                            rows={2}
                            className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                            value={step.question}
                            onChange={e => {
                              const updated = [...reasoningSteps];
                              updated[index] = { ...step, question: e.target.value };
                              setReasoningSteps(updated);
                            }}
                            placeholder='e.g., "Who might betray {agent_name} in this situation?"'
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Answer Prefix</label>
                            <input
                              type="text"
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-xs"
                              value={step.answer_prefix}
                              onChange={e => {
                                const updated = [...reasoningSteps];
                                updated[index] = { ...step, answer_prefix: e.target.value };
                                setReasoningSteps(updated);
                              }}
                              placeholder="{agent_name} thinks: "
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Memories to Retrieve</label>
                            <input
                              type="number" min={1} max={50}
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-xs"
                              value={step.num_memories}
                              onChange={e => {
                                const updated = [...reasoningSteps];
                                updated[index] = { ...step, num_memories: parseInt(e.target.value) || 10 };
                                setReasoningSteps(updated);
                              }}
                            />
                          </div>
                        </div>
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            className="h-3.5 w-3.5 text-amber-600 rounded"
                            checked={step.add_to_memory}
                            onChange={e => {
                              const updated = [...reasoningSteps];
                              updated[index] = { ...step, add_to_memory: e.target.checked };
                              setReasoningSteps(updated);
                            }}
                          />
                          <label className="ml-2 text-xs text-gray-600">Save reasoning result to memory</label>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <p className="mt-2 text-xs text-gray-500">
                Custom questions the agent asks itself each step. Use {'{agent_name}'} as a placeholder.
              </p>
            </div>
          )}

          {/* Scripted Prompts - only shown for scripted entities */}
          {isScripted && (
            <div className="border-t border-gray-200 pt-4">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Scripted Prompts
                </label>
                <button
                  type="button"
                  onClick={addScriptPrompt}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  + Add Prompt
                </button>
              </div>

              {scriptPrompts.length === 0 ? (
                <p className="text-sm text-gray-500 italic">
                  No scripted prompts yet. Click "+ Add Prompt" to create one.
                </p>
              ) : (
                <div className="space-y-3">
                  {scriptPrompts.map((prompt, index) => (
                    <div
                      key={prompt.id}
                      className="border border-gray-300 rounded-md p-3 bg-gray-50"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-gray-500">
                          Prompt {index + 1}
                        </span>
                        <div className="flex items-center space-x-1">
                          <button
                            type="button"
                            onClick={() => movePrompt(index, 'up')}
                            disabled={index === 0}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                            title="Move up"
                          >
                            ▲
                          </button>
                          <button
                            type="button"
                            onClick={() => movePrompt(index, 'down')}
                            disabled={index === scriptPrompts.length - 1}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                            title="Move down"
                          >
                            ▼
                          </button>
                          <button
                            type="button"
                            onClick={() => removeScriptPrompt(prompt.id)}
                            className="p-1 text-red-400 hover:text-red-600"
                            title="Remove prompt"
                          >
                            ✕
                          </button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Speaker Name
                          </label>
                          <input
                            type="text"
                            className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                            value={prompt.name}
                            onChange={(e) => updateScriptPrompt(prompt.id, 'name', e.target.value)}
                            placeholder="e.g., Dr. Chen"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Prompt Line
                          </label>
                          <textarea
                            rows={2}
                            className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm font-mono"
                            value={prompt.line}
                            onChange={(e) => updateScriptPrompt(prompt.id, 'line', e.target.value)}
                            placeholder="Enter the scripted dialogue or prompt..."
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <p className="mt-2 text-xs text-gray-500">
                Prompts will be executed in order. Drag to reorder.
              </p>
            </div>
          )}

          {/* Psychological Components - available for all agent types */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Psychological Components
              </label>
              <select
                className="text-sm border border-gray-300 rounded-md shadow-sm py-1.5 px-2"
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    addComponent(e.target.value);
                    e.target.value = '';
                  }
                }}
              >
                <option value="">+ Add Component...</option>
                {(() => {
                  const unused = availableComponents.filter(
                    t => !componentConfigs.some(c => c.templateId === t.id)
                  );
                  const groups: Record<string, typeof unused> = {};
                  unused.forEach(t => {
                    const cat = t.category || 'General';
                    (groups[cat] = groups[cat] || []).push(t);
                  });
                  return Object.entries(groups).map(([cat, templates]) => (
                    <optgroup key={cat} label={cat}>
                      {templates.map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </optgroup>
                  ));
                })()}
              </select>
            </div>

            {componentConfigs.length === 0 ? (
              <p className="text-sm text-gray-500 italic">
                No components added. Components modify agent behavior based on psychological theories.
              </p>
            ) : (
              <div className="space-y-3">
                {componentConfigs.map((config, index) => {
                  const template = availableComponents.find(c => c.id === config.templateId);
                  if (!template) return null;

                  return (
                    <div
                      key={config.templateId}
                      className="border border-gray-300 rounded-md p-3 bg-blue-50"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <span className="text-sm font-medium text-gray-900">
                            {template.name}
                          </span>
                          <p className="text-xs text-gray-600">{template.description}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeComponent(index)}
                          className="p-1 text-red-400 hover:text-red-600"
                          title="Remove component"
                        >
                          ✕
                        </button>
                      </div>

                      {/* Parameter inputs */}
                      <div className="space-y-2 mt-3">
                        {Object.entries(template.parameters).map(([paramKey, paramConfig]: [string, any]) => (
                          <div key={paramKey}>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                              {paramConfig.description || paramKey}
                            </label>
                            {paramConfig.enum ? (
                              <select
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                                value={config.parameters[paramKey] ?? paramConfig.default ?? ''}
                                onChange={(e) => {
                                  const value = paramConfig.type === 'integer'
                                    ? parseInt(e.target.value)
                                    : e.target.value;
                                  updateComponentParameter(index, paramKey, value);
                                }}
                              >
                                {paramConfig.enum.map((val: string) => (
                                  <option key={val} value={val}>{val}</option>
                                ))}
                              </select>
                            ) : paramConfig.type === 'boolean' ? (
                              <select
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                                value={config.parameters[paramKey] ?? paramConfig.default ?? false}
                                onChange={(e) => updateComponentParameter(index, paramKey, e.target.value === 'true')}
                              >
                                <option value="true">Yes</option>
                                <option value="false">No</option>
                              </select>
                            ) : paramConfig.type === 'integer' || paramConfig.type === 'float' ? (
                              <input
                                type="number"
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                                value={config.parameters[paramKey] ?? paramConfig.default ?? ''}
                                min={paramConfig.min}
                                max={paramConfig.max}
                                step={paramConfig.type === 'float' ? 0.1 : 1}
                                onChange={(e) => {
                                  const value = paramConfig.type === 'float'
                                    ? parseFloat(e.target.value)
                                    : parseInt(e.target.value);
                                  updateComponentParameter(index, paramKey, value);
                                }}
                              />
                            ) : paramConfig.type === 'dict' ? (
                              <textarea
                                rows={3}
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm font-mono"
                                value={JSON.stringify(config.parameters[paramKey] ?? paramConfig.default ?? {}, null, 2)}
                                onChange={(e) => {
                                  try {
                                    const value = JSON.parse(e.target.value);
                                    updateComponentParameter(index, paramKey, value);
                                  } catch {
                                    // Ignore invalid JSON
                                  }
                                }}
                                placeholder="Enter JSON object..."
                              />
                            ) : (
                              <input
                                type="text"
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                                value={config.parameters[paramKey] ?? paramConfig.default ?? ''}
                                onChange={(e) => updateComponentParameter(index, paramKey, e.target.value)}
                                placeholder={paramConfig.default?.toString() || ''}
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <p className="mt-2 text-xs text-gray-500">
              Components add psychological traits, biases, and behavioral patterns based on research.
            </p>
          </div>

          {/* Nested Simulation - optional advanced feature */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                <span className="flex items-center">
                  <svg className="h-4 w-4 text-purple-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                  </svg>
                  Nested Simulation
                  <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Advanced</span>
                </span>
              </label>
              <button
                type="button"
                onClick={() => {
                  const hasNestedSim = agent?.nested_simulation;
                  if (hasNestedSim) {
                    updateAgent(agentId, { nested_simulation: undefined });
                  } else {
                    updateAgent(agentId, {
                      nested_simulation: {
                        premise: '',
                        max_steps: 5,
                        agents: [],
                        shared_memories: [],
                        extraction_prompt: 'What were the key observations from this simulation?'
                      }
                    });
                  }
                }}
                className={`text-sm font-medium px-3 py-1.5 rounded-md transition ${
                  agent?.nested_simulation
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                }`}
              >
                {agent?.nested_simulation ? '− Remove Nested Sim' : '+ Add Nested Sim'}
              </button>
            </div>

            {agent?.nested_simulation ? (
              <div className="space-y-3 bg-purple-50 p-4 rounded-md border border-purple-200">
                <p className="text-xs text-gray-600 mb-3">
                  This agent can run a mini-simulation as part of their decision-making process (e.g., simulating a conversation to plan ahead).
                </p>

                {/* Premise */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Mini-Simulation Premise
                  </label>
                  <textarea
                    rows={2}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                    value={agent.nested_simulation.premise}
                    onChange={(e) => updateAgent(agentId, {
                      ...agent,
                      nested_simulation: { ...agent.nested_simulation!, premise: e.target.value }
                    })}
                    placeholder="e.g., 'Alice calls Bob to ask what to bring to the party'"
                  />
                </div>

                {/* Max Steps */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Max Steps (1-50)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                    value={agent.nested_simulation.max_steps}
                    onChange={(e) => updateAgent(agentId, {
                      ...agent,
                      nested_simulation: { ...agent.nested_simulation!, max_steps: parseInt(e.target.value) || 5 }
                    })}
                  />
                </div>

                {/* Shared Memories */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Shared Memories (one per line)
                  </label>
                  <textarea
                    rows={3}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm font-mono text-xs"
                    value={agent.nested_simulation.shared_memories.join('\n')}
                    onChange={(e) => updateAgent(agentId, {
                      ...agent,
                      nested_simulation: {
                        ...agent.nested_simulation!,
                        shared_memories: e.target.value.split('\n').filter(m => m.trim())
                      }
                    })}
                    placeholder="Context known to all agents in the mini-simulation..."
                  />
                </div>

                {/* Extraction Prompt */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Extraction Prompt (Optional)
                  </label>
                  <textarea
                    rows={2}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                    value={agent.nested_simulation.extraction_prompt || ''}
                    onChange={(e) => updateAgent(agentId, {
                      ...agent,
                      nested_simulation: { ...agent.nested_simulation!, extraction_prompt: e.target.value }
                    })}
                    placeholder="What should the agent learn from this simulation?"
                  />
                </div>

                <p className="text-xs text-gray-500 italic">
                  💡 Tip: Configure the mini-simulation agents by copying this agent and modifying it, then reference in JSON import/export.
                </p>
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">
                No nested simulation configured. Agents can run mini-simulations to inform their decisions.
              </p>
            )}
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
