/**
 * GameMasterConfig Component
 * Configure the game master
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import type { VariableConfig } from '../../types/simulation';

interface VariableConfigWithId extends VariableConfig {
  id: string;
}

export default function GameMasterConfig() {
  const { config, setGameMaster } = useSimulation();
  const [variables, setVariables] = useState<VariableConfigWithId[]>(
    (config.game_master.grounded_variables || []).map((v, i) => ({ ...v, id: `var-${i}` }))
  );
  const [showVariables, setShowVariables] = useState(false);
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [showExample, setShowExample] = useState(false);

  // Sync variables with config when config changes externally
  useEffect(() => {
    if (config.game_master.grounded_variables) {
      setVariables(config.game_master.grounded_variables.map((v, i) => ({ ...v, id: `var-${i}` })));
    }
  }, [config.game_master.grounded_variables]);

  // Get prefab-specific example
  const getPrefabExample = (): string => {
    switch (config.game_master.prefab) {
      case 'generic__GameMaster':
        return JSON.stringify({
          critical_decision_points: [
            {
              step: 10,
              description: "Budget allocation vote - Council must decide between competing priorities",
              options: ["Approve affordable housing", "Approve commercial development", "Table decision"]
            },
            {
              step: 15,
              description: "Rent control proposal - Tenant advocates vs property owners",
              options: ["Pass rent control", "Reject rent control", "Compromise with phased implementation"]
            }
          ],
          extra_components: {
            grounded_variables_intro: "Track key outcomes:\n- Median rent changes\n- Displacement rates\n- Business survival\n- Policy decisions"
          }
        }, null, 2);

      case 'interviewer__GameMaster':
        return JSON.stringify({
          questionnaires: [
            {
              name: "Job Satisfaction",
              description: "Annual employee satisfaction survey",
              questionnaire_type: "multiple_choice",
              observation_preprompt: "Please answer the following questions about your job satisfaction.",
              questions: [
                {
                  statement: "I am satisfied with my current role and responsibilities.",
                  dimension: "job_satisfaction",
                  preprompt: "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                  choices: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                  ascending_scale: true
                }
              ]
            }
          ]
        }, null, 2);

      case 'game_theoretic_and_dramaturgic__GameMaster':
        return JSON.stringify({
          scenes: [{
            scene_type: {
              name: "decision",
              game_master_name: "Game Master",
              action_spec: {
                call_to_action: "What does {name} do?",
                options: ["COOPERATE", "DEFECT"]
              }
            },
            participants: ["Agent1", "Agent2"],
            num_rounds: 4
          }]
        }, null, 2);

      default:
        return JSON.stringify({}, null, 2);
    }
  };

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
            <option value="generic__GameMaster">Generic (Narrative)</option>
            <option value="dialogic__GameMaster">Dialogic (Conversation)</option>
            <option value="game_theoretic_and_dramaturgic__GameMaster">Game-Theoretic</option>
            <option value="interviewer__GameMaster">Interviewer</option>
          </select>
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

        {/* Grounded Variables - optional advanced feature */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              <span className="flex items-center">
                <svg className="h-4 w-4 text-orange-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Grounded Variables
                <span className="ml-2 text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">Advanced</span>
              </span>
            </label>
            <button
              type="button"
              onClick={() => setShowVariables(!showVariables)}
              className="text-sm text-blue-600 hover:text-blue-800"
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

        {/* Parameters (JSON) */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="gm-parameters" className="block text-sm font-medium text-gray-700">
              Parameters (JSON) - Optional
            </label>
            <button
              type="button"
              onClick={() => setShowExample(!showExample)}
              className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
            >
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {showExample ? 'Hide' : 'Show'} Example
            </button>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Advanced configuration for {config.game_master.prefab}.{' '}
            {config.game_master.prefab === 'game_theoretic_and_dramaturgic__GameMaster' && (
              <span className="text-amber-600 font-medium">
                Note: num_rounds must equal max_steps (not multiplied).
              </span>
            )}
          </p>

          {showExample && (
            <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-blue-800">
                  Example for {config.game_master.prefab}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setGameMaster({ ...config.game_master, parameters: JSON.parse(getPrefabExample()) });
                    setShowExample(false);
                  }}
                  className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                >
                  Use This Example
                </button>
              </div>
              <pre className="text-xs font-mono text-gray-700 overflow-x-auto bg-white p-2 rounded border border-blue-100">
                {getPrefabExample()}
              </pre>
            </div>
          )}

          <textarea
            id="gm-parameters"
            rows={8}
            className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 sm:text-sm font-mono text-xs ${
              jsonError ? 'border-red-300 focus:border-red-500' : 'border-gray-300 focus:border-blue-500'
            }`}
            value={config.game_master.parameters ? JSON.stringify(config.game_master.parameters, null, 2) : ''}
            onChange={(e) => {
              try {
                const params = e.target.value ? JSON.parse(e.target.value) : {};
                setGameMaster({ ...config.game_master, parameters: params });
                setJsonError(null);
              } catch (err) {
                setJsonError('Invalid JSON: ' + (err as Error).message);
              }
            }}
          />

          {jsonError && (
            <p className="mt-1 text-xs text-red-600">
              ⚠️ {jsonError}
            </p>
          )}

          {!jsonError && config.game_master.parameters && Object.keys(config.game_master.parameters).length > 0 && (
            <p className="mt-1 text-xs text-green-600">
              ✓ Valid JSON ({Object.keys(config.game_master.parameters).length} top-level key{Object.keys(config.game_master.parameters).length !== 1 ? 's' : ''})
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
