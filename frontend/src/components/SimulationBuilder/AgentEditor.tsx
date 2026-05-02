/**
 * AgentEditor Component
 * Modal for editing agent configuration
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { getComponentTemplates, getPrefabs } from '../../utils/api';
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
  const { config, updateAgent } = useSimulation();
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

      // Load existing component configurations (excluding script)
      const existingComponents = agent.components || {};
      const componentEntries = Object.entries(existingComponents)
        .filter(([key]) => key !== 'script')
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
            <label className="block text-sm font-medium text-gray-700">Pre-loaded Memories</label>
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
