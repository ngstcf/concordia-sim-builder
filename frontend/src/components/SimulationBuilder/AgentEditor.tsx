/**
 * AgentEditor Component
 * Modal for editing agent configuration
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import type { ScriptLine } from '../../types/simulation';

interface AgentEditorProps {
  agentId: string;
  onClose: () => void;
}

interface ScriptPrompt {
  id: string;
  name: string;
  line: string;
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
    }
  }, [agent]);

  if (!agent) return null;

  const handleSave = () => {
    const isScriptedPrefab = prefab === 'basic_scripted__Entity' || prefab === 'context_aware_scripted__Entity';
    const components = isScriptedPrefab && scriptPrompts.length > 0
      ? { script: scriptPrompts.map(p => ({ name: p.name, line: p.line })) }
      : agent?.components;

    updateAgent(agentId, {
      name,
      prefab,
      goal: goal || undefined,
      memories: memories.split('\n').filter(m => m.trim()),
      randomize_choices: randomize,
      components
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
              <option value="basic__Entity">Basic Entity</option>
              <option value="basic_with_plan__Entity">Entity with Plan</option>
              <option value="basic_scripted__Entity">Scripted Entity (Exact Responses)</option>
              <option value="context_aware_scripted__Entity">Scripted Entity (Context-Aware)</option>
              <option value="minimal__Entity">Minimal Entity</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {isScripted && (
                prefab === 'basic_scripted__Entity'
                  ? 'Forces exact scripted responses regardless of context'
                  : 'Adapts scripted prompts based on conversation context'
              )}
            </p>
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
