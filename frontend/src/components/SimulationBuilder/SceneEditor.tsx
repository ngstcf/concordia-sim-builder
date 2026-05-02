import { useState } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';

interface ActionSpec {
  call_to_action: string;
  output_type?: string;
  options?: string[];
}

interface SceneType {
  name: string;
  game_master_name: string;
  action_spec: ActionSpec;
}

interface Scene {
  id: string;
  scene_type: SceneType;
  participants: string[];
  num_rounds: number;
}

const OUTPUT_TYPES = [
  { value: 'FREE', label: 'Free Text', description: 'Agent responds with any text' },
  { value: 'CHOICE', label: 'Multiple Choice', description: 'Agent picks from options list' },
  { value: 'FLOAT', label: 'Numeric', description: 'Agent responds with a number' },
];

export default function SceneEditor() {
  const { config, setConfig, setGameMaster } = useSimulation();

  const existingScenes: Scene[] = (config.game_master.parameters?.scenes || []).map(
    (s: any, i: number) => ({ ...s, id: s.id || `scene-${i}` })
  );

  const [scenes, setScenes] = useState<Scene[]>(existingScenes);
  const [expandedScene, setExpandedScene] = useState<string | null>(
    scenes.length > 0 ? scenes[0].id : null
  );

  const agentNames = config.agents.map(a => a.name);

  const syncToConfig = (updated: Scene[]) => {
    const clean = updated.map(({ id, ...rest }) => rest);
    const totalRounds = updated.reduce((sum, s) => sum + s.num_rounds, 0);
    setConfig({
      ...config,
      max_steps: totalRounds > 0 ? totalRounds : config.max_steps,
      game_master: {
        ...config.game_master,
        parameters: { ...config.game_master.parameters, scenes: clean },
      },
    });
  };

  const addScene = () => {
    const newScene: Scene = {
      id: `scene-${Date.now()}`,
      scene_type: {
        name: `Scene ${scenes.length + 1}`,
        game_master_name: config.game_master.name || 'Game Master',
        action_spec: {
          call_to_action: 'What does {name} do?',
          output_type: 'CHOICE',
          options: ['Option A', 'Option B'],
        },
      },
      participants: agentNames.length > 0 ? [agentNames[0]] : [],
      num_rounds: 3,
    };
    const updated = [...scenes, newScene];
    setScenes(updated);
    syncToConfig(updated);
    setExpandedScene(newScene.id);
  };

  const removeScene = (id: string) => {
    const updated = scenes.filter(s => s.id !== id);
    setScenes(updated);
    syncToConfig(updated);
    if (expandedScene === id) setExpandedScene(null);
  };

  const updateScene = (id: string, patch: Partial<Scene>) => {
    const updated = scenes.map(s => (s.id === id ? { ...s, ...patch } : s));
    setScenes(updated);
    syncToConfig(updated);
  };

  const updateSceneType = (id: string, patch: Partial<SceneType>) => {
    const scene = scenes.find(s => s.id === id);
    if (!scene) return;
    updateScene(id, { scene_type: { ...scene.scene_type, ...patch } });
  };

  const updateActionSpec = (id: string, patch: Partial<ActionSpec>) => {
    const scene = scenes.find(s => s.id === id);
    if (!scene) return;
    updateSceneType(id, { action_spec: { ...scene.scene_type.action_spec, ...patch } });
  };

  const moveScene = (index: number, direction: 'up' | 'down') => {
    const target = direction === 'up' ? index - 1 : index + 1;
    if (target < 0 || target >= scenes.length) return;
    const updated = [...scenes];
    [updated[index], updated[target]] = [updated[target], updated[index]];
    setScenes(updated);
    syncToConfig(updated);
  };

  const toggleParticipant = (sceneId: string, agentName: string) => {
    const scene = scenes.find(s => s.id === sceneId);
    if (!scene) return;
    const has = scene.participants.includes(agentName);
    updateScene(sceneId, {
      participants: has
        ? scene.participants.filter(p => p !== agentName)
        : [...scene.participants, agentName],
    });
  };

  return (
    <div className="mt-4 bg-indigo-50 p-4 rounded-md border border-indigo-200">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Scene Configuration</h4>
          <p className="text-xs text-gray-500">
            Define scenes with action specifications for structured gameplay
          </p>
        </div>
        <button
          type="button"
          onClick={addScene}
          className="text-sm bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-md hover:bg-indigo-200"
        >
          + Add Scene
        </button>
      </div>

      {scenes.length === 0 ? (
        <div className="text-center py-6 bg-white rounded-md border border-dashed border-indigo-300">
          <p className="text-sm text-gray-500">No scenes configured.</p>
          <p className="text-xs text-gray-400 mt-1">
            Add scenes to define structured interactions between agents.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className="bg-white rounded-md border border-gray-200 overflow-hidden"
            >
              {/* Scene header */}
              <div
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => setExpandedScene(expandedScene === scene.id ? null : scene.id)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-gray-400 w-5">{index + 1}</span>
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      {scene.scene_type.name}
                    </span>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-gray-500">
                        {scene.num_rounds} round{scene.num_rounds !== 1 ? 's' : ''}
                      </span>
                      <span className="text-xs text-gray-300">|</span>
                      <span className="text-xs text-gray-500">
                        {scene.participants.length} participant{scene.participants.length !== 1 ? 's' : ''}
                      </span>
                      {scene.scene_type.action_spec.output_type && (
                        <>
                          <span className="text-xs text-gray-300">|</span>
                          <span className="text-xs px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded">
                            {scene.scene_type.action_spec.output_type}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); moveScene(index, 'up'); }}
                    disabled={index === 0}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                    title="Move up"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" /></svg>
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); moveScene(index, 'down'); }}
                    disabled={index === scenes.length - 1}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                    title="Move down"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); removeScene(scene.id); }}
                    className="p-1 text-red-400 hover:text-red-600 ml-1"
                    title="Remove scene"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                  <svg
                    className={`w-4 h-4 text-gray-400 ml-1 transform transition-transform ${expandedScene === scene.id ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Scene body */}
              {expandedScene === scene.id && (
                <div className="px-4 pb-4 pt-1 border-t border-gray-100 space-y-4">
                  {/* Scene name */}
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Scene Name</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={scene.scene_type.name}
                      onChange={(e) => updateSceneType(scene.id, { name: e.target.value })}
                    />
                  </div>

                  {/* Participants */}
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Participants</label>
                    {agentNames.length === 0 ? (
                      <p className="text-xs text-gray-400 italic">Add agents first to assign participants.</p>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {agentNames.map(name => {
                          const active = scene.participants.includes(name);
                          return (
                            <button
                              key={name}
                              type="button"
                              onClick={() => toggleParticipant(scene.id, name)}
                              className={`text-xs px-2.5 py-1 rounded-full border transition ${
                                active
                                  ? 'bg-indigo-100 border-indigo-300 text-indigo-800'
                                  : 'bg-white border-gray-300 text-gray-500 hover:border-indigo-300'
                              }`}
                            >
                              {name}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Rounds */}
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Number of Rounds</label>
                    <input
                      type="number"
                      min={1}
                      max={100}
                      className="w-32 border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                      value={scene.num_rounds}
                      onChange={(e) => {
                        const newRounds = parseInt(e.target.value) || 1;
                        const cta = scene.scene_type.action_spec.call_to_action;
                        const updatedCta = cta.replace(/\b\d+\s+rounds?\b/gi, `${newRounds} rounds`);
                        if (updatedCta !== cta) {
                          updateScene(scene.id, {
                            num_rounds: newRounds,
                            scene_type: {
                              ...scene.scene_type,
                              action_spec: { ...scene.scene_type.action_spec, call_to_action: updatedCta },
                            },
                          });
                        } else {
                          updateScene(scene.id, { num_rounds: newRounds });
                        }
                      }}
                    />
                  </div>

                  {/* Action Spec */}
                  <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                    <h5 className="text-xs font-medium text-gray-700 mb-2">Action Specification</h5>

                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Call to Action</label>
                        <input
                          type="text"
                          className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                          value={scene.scene_type.action_spec.call_to_action}
                          onChange={(e) => updateActionSpec(scene.id, { call_to_action: e.target.value })}
                          placeholder="What does {name} do?"
                        />
                        <p className="mt-0.5 text-xs text-gray-400">Use {'{name}'} as a placeholder for the agent's name</p>
                      </div>

                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Output Type</label>
                        <select
                          className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm"
                          value={scene.scene_type.action_spec.output_type || 'FREE'}
                          onChange={(e) => updateActionSpec(scene.id, {
                            output_type: e.target.value,
                            options: e.target.value === 'CHOICE' ? (scene.scene_type.action_spec.options || ['Option A', 'Option B']) : undefined,
                          })}
                        >
                          {OUTPUT_TYPES.map(t => (
                            <option key={t.value} value={t.value}>{t.label}</option>
                          ))}
                        </select>
                        <p className="mt-0.5 text-xs text-gray-400">
                          {OUTPUT_TYPES.find(t => t.value === (scene.scene_type.action_spec.output_type || 'FREE'))?.description}
                        </p>
                      </div>

                      {/* Choice options */}
                      {scene.scene_type.action_spec.output_type === 'CHOICE' && (
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <label className="block text-xs text-gray-600">Options</label>
                            <button
                              type="button"
                              onClick={() => {
                                const opts = scene.scene_type.action_spec.options || [];
                                updateActionSpec(scene.id, {
                                  options: [...opts, `Option ${String.fromCharCode(65 + opts.length)}`],
                                });
                              }}
                              className="text-xs text-indigo-600 hover:text-indigo-800"
                            >
                              + Add
                            </button>
                          </div>
                          <div className="space-y-1.5">
                            {(scene.scene_type.action_spec.options || []).map((opt, oi) => (
                              <div key={oi} className="flex items-center gap-2">
                                <input
                                  type="text"
                                  className="flex-1 border border-gray-300 rounded-md shadow-sm py-1 px-2 text-xs"
                                  value={opt}
                                  onChange={(e) => {
                                    const opts = [...(scene.scene_type.action_spec.options || [])];
                                    opts[oi] = e.target.value;
                                    updateActionSpec(scene.id, { options: opts });
                                  }}
                                />
                                {(scene.scene_type.action_spec.options?.length || 0) > 1 && (
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const opts = (scene.scene_type.action_spec.options || []).filter((_, i) => i !== oi);
                                      updateActionSpec(scene.id, { options: opts });
                                    }}
                                    className="text-red-400 hover:text-red-600 text-xs"
                                  >
                                    ✕
                                  </button>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
