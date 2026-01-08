/**
 * AgentList Component
 * List and manage agents in the simulation
 */
import { useState } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import AgentEditor from './AgentEditor';

export default function AgentList() {
  const { config, addAgent, removeAgent } = useSimulation();
  const [editingAgent, setEditingAgent] = useState<string | null>(null);

  const handleAddAgent = () => {
    const newAgent = {
      id: `agent-${Date.now()}`,
      name: `Agent ${config.agents.length + 1}`,
      prefab: 'basic__Entity',
      memories: [],
      randomize_choices: true
    };
    addAgent(newAgent);
    setEditingAgent(newAgent.id);
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          Agents ({config.agents.length})
        </h3>
        <button
          onClick={handleAddAgent}
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Agent
        </button>
      </div>

      {config.agents.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-md border-2 border-dashed border-gray-300">
          <p className="text-sm text-gray-500">No agents yet. Add your first agent to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {config.agents.map((agent) => (
            <div
              key={agent.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100"
            >
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{agent.name}</p>
                <p className="text-xs text-gray-500">
                  {agent.prefab} {agent.goal ? `• ${agent.goal.substring(0, 50)}...` : ''}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setEditingAgent(agent.id)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => removeAgent(agent.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Agent Editor Modal */}
      {editingAgent && (
        <AgentEditor
          agentId={editingAgent}
          onClose={() => setEditingAgent(null)}
        />
      )}
    </div>
  );
}
