/**
 * GameMasterConfig Component
 * Configure the game master
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { getPrefabs, getContribComponents } from '../../utils/api';
import type { VariableConfig, ContribComponentConfig } from '../../types/simulation';
import SceneEditor from './SceneEditor';
import QuestionnaireBuilder from './QuestionnaireBuilder';

interface PrefabInfo {
  name: string;
  description: string;
  type: string;
}

interface VariableConfigWithId extends VariableConfig {
  id: string;
}

export default function GameMasterConfig() {
  const { config, setGameMaster } = useSimulation();
  const [variables, setVariables] = useState<VariableConfigWithId[]>(
    (config.game_master.grounded_variables || []).map((v, i) => ({ ...v, id: `var-${i}` }))
  );
  const [showVariables, setShowVariables] = useState(false);
  const [showCriticalDecisions, setShowCriticalDecisions] = useState(false);
  const [showContribComponents, setShowContribComponents] = useState(false);
  const [contribRegistry, setContribRegistry] = useState<Array<{
    id: string; name: string; description: string; category: string;
    params: Record<string, { type: string; default?: any; min?: number; max?: number; description?: string }>;
  }>>([]);
  const [gmPrefabs, setGmPrefabs] = useState<PrefabInfo[]>([]);

  useEffect(() => {
    getPrefabs().then(data => {
      setGmPrefabs(data.game_masters);
    }).catch(err => {
      console.error('Failed to load GM prefabs:', err);
    });
    getContribComponents().then(data => {
      setContribRegistry(data.components);
    }).catch(err => {
      console.error('Failed to load contrib components:', err);
    });
  }, []);

  // Sync variables with config when config changes externally
  useEffect(() => {
    if (config.game_master.grounded_variables) {
      setVariables(config.game_master.grounded_variables.map((v, i) => ({ ...v, id: `var-${i}` })));
    } else {
      setVariables([]);
    }
  }, [config.game_master.grounded_variables]);

  // Sync contrib components visibility when config changes externally
  useEffect(() => {
    if (config.game_master.contrib_components && config.game_master.contrib_components.length > 0) {
      setShowContribComponents(true);
    }
  }, [config.game_master.contrib_components]);

  // Get critical decision points from game_master (can be at root level or in parameters)
  const getCriticalDecisionPoints = (): Array<{step: number; description: string; options: string[]}> => {
    // Check at game master root level first (Urban Gentrification format)
    if ((config.game_master as any).critical_decision_points) {
      return (config.game_master as any).critical_decision_points;
    }
    // Fall back to parameters format (newer format)
    const params = config.game_master.parameters || {};
    return params.critical_decision_points || [];
  };

  const setCriticalDecisionPoints = (points: Array<{step: number; description: string; options: string[]}>) => {
    // Store at game master root level to match schema and existing templates
    setGameMaster({
      ...config.game_master,
      critical_decision_points: points as any
    });
  };

  const addCriticalDecisionPoint = () => {
    const current = getCriticalDecisionPoints();
    const maxStep = current.length > 0 ? Math.max(...current.map(p => p.step)) : 0;
    setCriticalDecisionPoints([
      ...current,
      { step: maxStep + 5, description: '', options: ['Option A', 'Option B'] }
    ]);
  };

  const updateCriticalDecisionPoint = (index: number, updates: Partial<{step: number; description: string; options: string[]}>) => {
    const current = getCriticalDecisionPoints();
    const updated = [...current];
    updated[index] = { ...updated[index], ...updates };
    setCriticalDecisionPoints(updated);
  };

  const removeCriticalDecisionPoint = (index: number) => {
    const current = getCriticalDecisionPoints();
    setCriticalDecisionPoints(current.filter((_, i) => i !== index));
  };

  const addOptionToDecision = (index: number) => {
    const current = getCriticalDecisionPoints();
    const updated = [...current];
    updated[index] = {
      ...updated[index],
      options: [...updated[index].options, `Option ${String.fromCharCode(65 + updated[index].options.length)}`]
    };
    setCriticalDecisionPoints(updated);
  };

  const updateDecisionOption = (decisionIndex: number, optionIndex: number, value: string) => {
    const current = getCriticalDecisionPoints();
    const updated = [...current];
    const options = [...updated[decisionIndex].options];
    options[optionIndex] = value;
    updated[decisionIndex] = { ...updated[decisionIndex], options };
    setCriticalDecisionPoints(updated);
  };

  const removeDecisionOption = (decisionIndex: number, optionIndex: number) => {
    const current = getCriticalDecisionPoints();
    const updated = [...current];
    updated[decisionIndex] = {
      ...updated[decisionIndex],
      options: updated[decisionIndex].options.filter((_, i) => i !== optionIndex)
    };
    setCriticalDecisionPoints(updated);
  };

  // Get prefab-specific example
  const addVariable = () => {
    const newVar: VariableConfigWithId = {
      id: `var-${Date.now()}`,
      name: '',
      variable_type: 'numerical',
      description: '',
      default_value: 0,
    };
    setVariables([...variables, newVar]);
  };

  const removeVariable = (id: string) => {
    const updated = variables.filter(v => v.id !== id);
    setVariables(updated);
    updateGroundedVariables(updated);
  };

  const updateVariable = (id: string, updates: Partial<VariableConfigWithId>) => {
    const updated = variables.map(v => v.id === id ? { ...v, ...updates } : v);
    setVariables(updated);
    updateGroundedVariables(updated);
  };

  const updateGroundedVariables = (vars: VariableConfigWithId[]) => {
    const cleanVars = vars.map(({ id, ...v }) => v);
    setGameMaster({
      ...config.game_master,
      grounded_variables: cleanVars.length > 0 ? cleanVars : undefined
    });
  };

  const contribComponents: ContribComponentConfig[] = config.game_master.contrib_components || [];

  const addContribComponent = (componentId: string) => {
    const entry = contribRegistry.find(c => c.id === componentId);
    if (!entry) return;
    const defaults: Record<string, any> = {};
    for (const [key, schema] of Object.entries(entry.params)) {
      if (schema.default !== undefined) defaults[key] = schema.default;
    }
    const updated = [...contribComponents, { component_id: componentId, params: defaults }];
    setGameMaster({ ...config.game_master, contrib_components: updated });
  };

  const updateContribComponent = (index: number, params: Record<string, any>) => {
    const updated = [...contribComponents];
    updated[index] = { ...updated[index], params };
    setGameMaster({ ...config.game_master, contrib_components: updated });
  };

  const removeContribComponent = (index: number) => {
    const updated = contribComponents.filter((_, i) => i !== index);
    setGameMaster({ ...config.game_master, contrib_components: updated.length > 0 ? updated : undefined });
  };

  const availableContribIds = contribRegistry
    .filter(c => !contribComponents.some(cc => cc.component_id === c.id))
    .map(c => c.id);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Game Master</h3>

      <div className="space-y-4">
        {/* Name */}
        <div>
          <label htmlFor="gm-name" className="block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            type="text"
            id="gm-name"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={config.game_master.name}
            onChange={(e) => setGameMaster({ ...config.game_master, name: e.target.value })}
          />
        </div>

        {/* Prefab */}
        <div>
          <label htmlFor="gm-prefab" className="block text-sm font-medium text-gray-700">
            Prefab Type
          </label>
          <select
            id="gm-prefab"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={config.game_master.prefab}
            onChange={(e) => setGameMaster({ ...config.game_master, prefab: e.target.value })}
          >
            {gmPrefabs.length > 0 ? (
              <>
                <optgroup label="Narrative">
                  {gmPrefabs.filter(p => ['generic__GameMaster', 'dialogic__GameMaster', 'dialogic_and_dramaturgic__GameMaster', 'scripted__GameMaster'].includes(p.name)).map(p => (
                    <option key={p.name} value={p.name}>{p.name.replace('__GameMaster', '')}</option>
                  ))}
                </optgroup>
                <optgroup label="Structured">
                  {gmPrefabs.filter(p => ['game_theoretic_and_dramaturgic__GameMaster', 'interviewer__GameMaster', 'open_ended_interviewer__GameMaster', 'marketplace__GameMaster', 'psychology_experiment__GameMaster'].includes(p.name)).map(p => (
                    <option key={p.name} value={p.name}>{p.name.replace('__GameMaster', '')}</option>
                  ))}
                </optgroup>
                <optgroup label="Situated">
                  {gmPrefabs.filter(p => ['situated__GameMaster', 'situated_in_time_and_place__GameMaster', 'physically_situated_and_dramaturgic__GameMaster'].includes(p.name)).map(p => (
                    <option key={p.name} value={p.name}>{p.name.replace('__GameMaster', '')}</option>
                  ))}
                </optgroup>
                <optgroup label="Simulation">
                  {gmPrefabs.filter(p => ['async_social_media__GameMaster', 'space_ship__GameMaster'].includes(p.name)).map(p => (
                    <option key={p.name} value={p.name}>{p.name.replace('__GameMaster', '')}</option>
                  ))}
                </optgroup>
              </>
            ) : (
              <>
                <option value="generic__GameMaster">generic</option>
                <option value="dialogic__GameMaster">dialogic</option>
                <option value="game_theoretic_and_dramaturgic__GameMaster">game_theoretic_and_dramaturgic</option>
                <option value="interviewer__GameMaster">interviewer</option>
              </>
            )}
          </select>
          {(() => {
            const selected = gmPrefabs.find(p => p.name === config.game_master.prefab);
            return selected ? (
              <p className="mt-1 text-xs text-gray-500">{selected.description}</p>
            ) : null;
          })()}
        </div>

        {/* Acting Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Acting Order
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'game_master_choice'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'game_master_choice' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Game Master Choice</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'fixed'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'fixed' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Fixed Order</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="acting_order"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={config.game_master.acting_order === 'random'}
                onChange={() => setGameMaster({ ...config.game_master, acting_order: 'random' as any })}
              />
              <span className="ml-2 text-sm text-gray-700">Random</span>
            </label>
          </div>
        </div>

        {/* Scene Editor - for game-theoretic and situated GMs */}
        {['game_theoretic_and_dramaturgic__GameMaster', 'physically_situated_and_dramaturgic__GameMaster', 'scripted__GameMaster'].includes(config.game_master.prefab) && (
          <SceneEditor />
        )}

        {/* Questionnaire Builder - for interviewer GMs */}
        {['interviewer__GameMaster', 'open_ended_interviewer__GameMaster'].includes(config.game_master.prefab) && (
          <QuestionnaireBuilder />
        )}

        {/* Grounded Variables - optional advanced feature */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-2">
            <div className="flex items-start gap-2 min-w-0">
              <svg className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium text-gray-700">Grounded Variables</span>
                <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full flex-shrink-0">Advanced</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowVariables(!showVariables)}
              className="text-sm text-blue-600 hover:text-blue-800 self-start sm:self-auto flex-shrink-0"
            >
              {showVariables ? '− Hide' : '+ Show'}
            </button>
          </div>

          {showVariables && (
            <div className="mt-3 bg-orange-50 p-4 rounded-md border border-orange-200">
              <p className="text-xs text-gray-600 mb-3">
                Track and update simulation state variables (morale, budget, health, etc.) during the simulation.
              </p>

              <div className="flex justify-between items-center mb-3">
                <span className="text-xs text-gray-600">
                  {variables.length} variable{variables.length !== 1 ? 's' : ''} configured
                </span>
                <button
                  type="button"
                  onClick={addVariable}
                  className="text-sm bg-orange-100 text-orange-700 px-3 py-1 rounded-md hover:bg-orange-200"
                >
                  + Add Variable
                </button>
              </div>

              {variables.length === 0 ? (
                <p className="text-sm text-gray-500 italic text-center py-2">
                  No variables configured. Add variables to track state during simulation.
                </p>
              ) : (
                <div className="space-y-3">
                  {variables.map((variable) => (
                    <div key={variable.id} className="bg-white p-3 rounded-md border border-gray-200">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1 grid grid-cols-2 gap-2">
                          {/* Name */}
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Variable Name
                            </label>
                            <input
                              type="text"
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                              value={variable.name}
                              onChange={(e) => updateVariable(variable.id, { name: e.target.value })}
                              placeholder="e.g., team_morale"
                            />
                          </div>

                          {/* Type */}
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Type
                            </label>
                            <select
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                              value={variable.variable_type}
                              onChange={(e) => updateVariable(variable.id, { variable_type: e.target.value as any })}
                            >
                              <option value="numerical">Numerical</option>
                              <option value="categorical">Categorical</option>
                              <option value="boolean">Boolean</option>
                              <option value="percentage">Percentage (0-100)</option>
                            </select>
                          </div>

                          {/* Description */}
                          <div className="col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Description
                            </label>
                            <input
                              type="text"
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                              value={variable.description}
                              onChange={(e) => updateVariable(variable.id, { description: e.target.value })}
                              placeholder="What this variable represents"
                            />
                          </div>

                          {/* Type-specific fields */}
                          {variable.variable_type === 'numerical' || variable.variable_type === 'percentage' ? (
                            <>
                              <div>
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                  Min Value
                                </label>
                                <input
                                  type="number"
                                  className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                  value={variable.min_value ?? ''}
                                  onChange={(e) => updateVariable(variable.id, { min_value: parseFloat(e.target.value) || undefined })}
                                  placeholder="0"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                  Max Value
                                </label>
                                <input
                                  type="number"
                                  className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                  value={variable.max_value ?? ''}
                                  onChange={(e) => updateVariable(variable.id, { max_value: parseFloat(e.target.value) || undefined })}
                                  placeholder="100"
                                />
                              </div>
                            </>
                          ) : variable.variable_type === 'categorical' ? (
                            <div className="col-span-2">
                              <label className="block text-xs font-medium text-gray-700 mb-1">
                                Allowed Values (comma-separated)
                              </label>
                              <input
                                type="text"
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                value={variable.allowed_values?.join(', ') || ''}
                                onChange={(e) => updateVariable(variable.id, { allowed_values: e.target.value.split(',').map(v => v.trim()).filter(v => v) })}
                                placeholder="option1, option2, option3"
                              />
                            </div>
                          ) : null}

                          {/* Default Value */}
                          <div className="col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Default Value
                            </label>
                            {variable.variable_type === 'boolean' ? (
                              <select
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                value={variable.default_value?.toString() || 'false'}
                                onChange={(e) => updateVariable(variable.id, { default_value: e.target.value === 'true' })}
                              >
                                <option value="true">True</option>
                                <option value="false">False</option>
                              </select>
                            ) : (
                              <input
                                type={variable.variable_type === 'numerical' || variable.variable_type === 'percentage' ? 'number' : 'text'}
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                value={variable.default_value ?? ''}
                                onChange={(e) => {
                                  const value = variable.variable_type === 'numerical' || variable.variable_type === 'percentage'
                                    ? parseFloat(e.target.value)
                                    : e.target.value;
                                  updateVariable(variable.id, { default_value: value });
                                }}
                                placeholder="Initial value"
                              />
                            )}
                          </div>

                          {/* Update Rule */}
                          <div className="col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Update Rule (Optional)
                            </label>
                            <input
                              type="text"
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                              value={variable.update_rule || ''}
                              onChange={(e) => updateVariable(variable.id, { update_rule: e.target.value })}
                              placeholder="How this variable changes during simulation"
                            />
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => removeVariable(variable.id)}
                          className="ml-2 text-red-400 hover:text-red-600 p-1"
                          title="Remove variable"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <p className="mt-3 text-xs text-gray-500 italic">
                💡 Tip: Variables are automatically tracked and updated by the Game Master during the simulation.
              </p>
            </div>
          )}
        </div>

        {/* Contrib GM Components */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-2">
            <div className="flex items-start gap-2 min-w-0">
              <svg className="h-4 w-4 text-indigo-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium text-gray-700">GM Components</span>
                <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full flex-shrink-0">Advanced</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowContribComponents(!showContribComponents)}
              className="text-sm text-blue-600 hover:text-blue-800 self-start sm:self-auto flex-shrink-0"
            >
              {showContribComponents ? '− Hide' : '+ Show'}
            </button>
          </div>

          {showContribComponents && (
            <div className="mt-3 bg-indigo-50 p-4 rounded-md border border-indigo-200">
              <p className="text-xs text-gray-600 mb-3">
                Add optional Concordia contrib components to enhance the Game Master with additional behaviors.
              </p>

              {availableContribIds.length > 0 && (
                <div className="flex gap-2 mb-3">
                  <select
                    id="contrib-component-select"
                    className="flex-1 border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm"
                    defaultValue=""
                  >
                    <option value="" disabled>Select a component...</option>
                    {availableContribIds.map(id => {
                      const entry = contribRegistry.find(c => c.id === id)!;
                      return (
                        <option key={id} value={id}>
                          {entry.name} — {entry.description}
                        </option>
                      );
                    })}
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      const select = document.getElementById('contrib-component-select') as HTMLSelectElement;
                      if (select.value) {
                        addContribComponent(select.value);
                        select.value = '';
                      }
                    }}
                    className="text-sm bg-indigo-100 text-indigo-700 px-3 py-1 rounded-md hover:bg-indigo-200 flex-shrink-0"
                  >
                    + Add
                  </button>
                </div>
              )}

              {contribComponents.length === 0 ? (
                <p className="text-sm text-gray-500 italic text-center py-2">
                  No GM components added. Select one above to enhance your Game Master.
                </p>
              ) : (
                <div className="space-y-3">
                  {contribComponents.map((cc, idx) => {
                    const entry = contribRegistry.find(c => c.id === cc.component_id);
                    if (!entry) return null;
                    return (
                      <div key={`${cc.component_id}-${idx}`} className="bg-white p-3 rounded-md border border-gray-200">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="text-sm font-medium text-gray-900">{entry.name}</span>
                            <span className="ml-2 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{entry.category}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeContribComponent(idx)}
                            className="text-red-400 hover:text-red-600 p-1"
                            title="Remove component"
                          >
                            ✕
                          </button>
                        </div>
                        <p className="text-xs text-gray-500 mb-2">{entry.description}</p>

                        {Object.keys(entry.params).length > 0 && (
                          <div className="grid grid-cols-2 gap-2">
                            {Object.entries(entry.params).map(([paramKey, paramSchema]) => (
                              <div key={paramKey} className={paramSchema.type === 'string' ? 'col-span-2' : ''}>
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                  {paramKey.replace(/_/g, ' ')}
                                </label>
                                {paramSchema.type === 'string' ? (
                                  <input
                                    type="text"
                                    className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value={cc.params[paramKey] ?? paramSchema.default ?? ''}
                                    onChange={(e) => updateContribComponent(idx, { ...cc.params, [paramKey]: e.target.value })}
                                    placeholder={paramSchema.description}
                                  />
                                ) : paramSchema.type === 'float' ? (
                                  <input
                                    type="number"
                                    step="0.01"
                                    min={paramSchema.min}
                                    max={paramSchema.max}
                                    className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value={cc.params[paramKey] ?? paramSchema.default ?? 0}
                                    onChange={(e) => updateContribComponent(idx, { ...cc.params, [paramKey]: parseFloat(e.target.value) || 0 })}
                                  />
                                ) : (
                                  <input
                                    type="number"
                                    min={paramSchema.min}
                                    max={paramSchema.max}
                                    className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value={cc.params[paramKey] ?? paramSchema.default ?? 0}
                                    onChange={(e) => updateContribComponent(idx, { ...cc.params, [paramKey]: parseInt(e.target.value) || 0 })}
                                  />
                                )}
                                {paramSchema.description && (
                                  <p className="mt-0.5 text-xs text-gray-400">{paramSchema.description}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Critical Decision Points - available for all Game Master types */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-2">
            <div className="flex items-start gap-2 min-w-0">
              <svg className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <div className="min-w-0">
                <div className="text-sm font-medium text-gray-700">
                  Critical Decision Points
                </div>
                {config.game_master.prefab !== 'generic__GameMaster' && (
                  <div className="text-xs font-normal text-gray-500">
                    (optional for {config.game_master.prefab})
                  </div>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowCriticalDecisions(!showCriticalDecisions)}
              className="text-sm text-blue-600 hover:text-blue-800 self-start sm:self-auto flex-shrink-0"
            >
              {showCriticalDecisions ? '− Hide' : '+ Show'}
            </button>
          </div>

            {showCriticalDecisions && (
              <div className="mt-3 bg-purple-50 p-4 rounded-md border border-purple-200">
                <p className="text-xs text-gray-600 mb-3">
                  Define key decision points in the simulation where agents must make important choices.
                  At each step, the Game Master will present agents with the specified options.
                </p>

                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs text-gray-600">
                    {getCriticalDecisionPoints().length} decision point{getCriticalDecisionPoints().length !== 1 ? 's' : ''} configured
                  </span>
                  <button
                    type="button"
                    onClick={addCriticalDecisionPoint}
                    className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-md hover:bg-purple-200"
                  >
                    + Add Decision Point
                  </button>
                </div>

                {getCriticalDecisionPoints().length === 0 ? (
                  <p className="text-sm text-gray-500 italic text-center py-4">
                    No critical decision points defined. Add decision points to create key choice moments in your simulation.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {getCriticalDecisionPoints().map((decision, decisionIndex) => (
                      <div key={decisionIndex} className="bg-white p-4 rounded-md border border-gray-200">
                        <div className="flex justify-between items-start mb-3">
                          <h4 className="text-sm font-medium text-gray-900">
                            Decision Point {decisionIndex + 1}
                          </h4>
                          <button
                            type="button"
                            onClick={() => removeCriticalDecisionPoint(decisionIndex)}
                            className="text-red-400 hover:text-red-600 text-sm"
                          >
                            ✕ Remove
                          </button>
                        </div>

                        {/* Step Number */}
                        <div className="mb-3">
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Step Number
                          </label>
                          <input
                            type="number"
                            min="1"
                            className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm"
                            value={decision.step}
                            onChange={(e) => updateCriticalDecisionPoint(decisionIndex, { step: parseInt(e.target.value) || 1 })}
                            placeholder="e.g., 10"
                          />
                          <p className="mt-1 text-xs text-gray-500">
                            The simulation step when this decision point occurs
                          </p>
                        </div>

                        {/* Description or Event (legacy format support) */}
                        {(decision as any).event ? (
                          <div className="mb-3">
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Event (Legacy Format)
                            </label>
                            <div className="bg-yellow-50 p-2 rounded border border-yellow-200 mb-2">
                              <p className="text-xs text-yellow-800">
                                ⚠️ This decision point uses the legacy event format. Consider converting to the new format with description and options.
                              </p>
                            </div>
                            <textarea
                              rows={3}
                              className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm"
                              value={(decision as any).event}
                              onChange={(e) => updateCriticalDecisionPoint(decisionIndex, { event: e.target.value } as any)}
                              placeholder="Full event description with outcome"
                            />
                            <p className="mt-1 text-xs text-gray-500">
                              The complete event text including the decision and its outcome
                            </p>
                          </div>
                        ) : (
                          <>
                            <div className="mb-3">
                              <label className="block text-xs font-medium text-gray-700 mb-1">
                                Decision Description
                              </label>
                              <textarea
                                rows={2}
                                className="w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm"
                                value={decision.description}
                                onChange={(e) => updateCriticalDecisionPoint(decisionIndex, { description: e.target.value })}
                                placeholder="e.g., Budget allocation vote - Council must decide between competing priorities"
                              />
                            </div>

                            {/* Options */}
                            <div>
                              <div className="flex justify-between items-center mb-2">
                                <label className="block text-xs font-medium text-gray-700">
                                  Available Options
                                </label>
                                <button
                                  type="button"
                                  onClick={() => addOptionToDecision(decisionIndex)}
                                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
                                >
                                  + Add Option
                                </button>
                              </div>

                              {decision.options.map((option, optionIndex) => (
                                <div key={optionIndex} className="flex items-center gap-2 mb-2">
                                  <input
                                    type="text"
                                    className="flex-1 border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                    value={option}
                                    onChange={(e) => updateDecisionOption(decisionIndex, optionIndex, e.target.value)}
                                    placeholder={`Option ${optionIndex + 1}`}
                                  />
                                  {decision.options.length > 1 && (
                                    <button
                                      type="button"
                                      onClick={() => removeDecisionOption(decisionIndex, optionIndex)}
                                      className="text-red-400 hover:text-red-600 text-sm"
                                      title="Remove option"
                                    >
                                      ✕
                                    </button>
                                  )}
                                </div>
                              ))}

                              <p className="mt-1 text-xs text-gray-500">
                                Agents will choose from these options at the decision point
                              </p>
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <p className="mt-3 text-xs text-gray-500 italic">
                  💡 Tip: Critical decision points create dramatic moments where agent choices significantly impact the simulation outcome.
                </p>
              </div>
            )}
        </div>

        {/* Extra Components - grounded_variables_intro for all Game Master types */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-start gap-2 mb-2">
            <div className="flex items-start gap-2 min-w-0">
              <svg className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div className="min-w-0">
                <div className="text-sm font-medium text-gray-700">
                  Grounded Variables Introduction
                </div>
                {config.game_master.prefab !== 'generic__GameMaster' && (
                  <div className="text-xs font-normal text-gray-500">
                    (optional for {config.game_master.prefab})
                  </div>
                )}
              </div>
            </div>
          </div>

          <p className="mt-1 text-xs text-gray-500">
            Provide instructions to the Game Master about what variables to track and how to interpret them during the simulation.
          </p>

          <textarea
            rows={4}
            className="mt-2 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={
              ((config.game_master as any).params?.extra_components?.grounded_variables_intro as string) ||
              ((config.game_master.parameters?.extra_components as any)?.grounded_variables_intro as string) ||
              ''
            }
            onChange={(e) => {
              const params = config.game_master.parameters || {};
              const extra = (params.extra_components as any) || {};
              setGameMaster({
                ...config.game_master,
                parameters: {
                  ...params,
                  extra_components: { ...extra, grounded_variables_intro: e.target.value }
                }
              });
            }}
            placeholder={`Track key outcomes throughout this simulation:
- Outcome 1: Brief description
- Outcome 2: Brief description
- Outcome 3: Brief description`}
          />
          <p className="mt-1 text-xs text-gray-500">
            💡 This text will be shown to the Game Master at the start of the simulation to guide variable tracking.
          </p>
        </div>

      </div>
    </div>
  );
}
