/**
 * AgentEditor Component
 * Modal for editing agent configuration
 */
import { useState, useEffect } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';

interface AgentEditorProps {
  agentId: string;
  onClose: () => void;
}

export default function AgentEditor({ agentId, onClose }: AgentEditorProps) {
  const { config, updateAgent } = useSimulation();
  const agent = config.agents.find(a => a.id === agentId);

  const [name, setName] = useState(agent?.name || '');
  const [prefab, setPrefab] = useState(agent?.prefab || 'basic__Entity');
  const [goal, setGoal] = useState(agent?.goal || '');
  const [memories, setMemories] = useState(agent?.memories?.join('\n') || '');
  const [randomize, setRandomize] = useState(agent?.randomize_choices ?? true);

  useEffect(() => {
    if (agent) {
      setName(agent.name);
      setPrefab(agent.prefab);
      setGoal(agent.goal || '');
      setMemories(agent.memories?.join('\n') || '');
      setRandomize(agent.randomize_choices ?? true);
    }
  }, [agent]);

  if (!agent) return null;

  const handleSave = () => {
    updateAgent(agentId, {
      name,
      prefab,
      goal: goal || undefined,
      memories: memories.split('\n').filter(m => m.trim()),
      randomize_choices: randomize
    });
    onClose();
  };

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
              <option value="basic_scripted__Entity">Scripted Entity</option>
              <option value="minimal__Entity">Minimal Entity</option>
            </select>
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
