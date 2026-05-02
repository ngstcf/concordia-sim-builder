import { useState, useRef } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import AgentEditor from './AgentEditor';

const PREFAB_BADGES: Record<string, { label: string; color: string }> = {
  basic: { label: 'Basic', color: 'bg-blue-100 text-blue-700' },
  basic_with_plan: { label: 'Planner', color: 'bg-blue-100 text-blue-700' },
  minimal: { label: 'Minimal', color: 'bg-gray-100 text-gray-700' },
  basic_scripted: { label: 'Scripted', color: 'bg-amber-100 text-amber-700' },
  context_aware_scripted: { label: 'Scripted+', color: 'bg-amber-100 text-amber-700' },
  conversational: { label: 'Dialogue', color: 'bg-green-100 text-green-700' },
  rational: { label: 'Rational', color: 'bg-purple-100 text-purple-700' },
  puppet: { label: 'Puppet', color: 'bg-red-100 text-red-700' },
  basic_with_image: { label: 'Multimodal', color: 'bg-pink-100 text-pink-700' },
};

function getPrefabBadge(prefab: string) {
  const key = prefab.replace('__Entity', '');
  return PREFAB_BADGES[key] || { label: key, color: 'bg-gray-100 text-gray-600' };
}

export default function AgentList() {
  const { config, addAgent, removeAgent, reorderAgents } = useSimulation();
  const [editingAgent, setEditingAgent] = useState<string | null>(null);
  const dragItem = useRef<number | null>(null);
  const dragOverItem = useRef<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const handleAddAgent = () => {
    const newAgent = {
      id: `agent-${Date.now()}`,
      name: `Agent ${config.agents.length + 1}`,
      prefab: 'basic__Entity',
      memories: [],
      randomize_choices: true,
    };
    addAgent(newAgent);
    setEditingAgent(newAgent.id);
  };

  const handleDuplicate = (agentId: string) => {
    const source = config.agents.find(a => a.id === agentId);
    if (!source) return;
    const dup = {
      ...source,
      id: `agent-${Date.now()}`,
      name: `${source.name} (copy)`,
      memories: [...source.memories],
      components: source.components ? { ...source.components } : undefined,
    };
    addAgent(dup);
  };

  const handleDragStart = (index: number) => {
    dragItem.current = index;
  };

  const handleDragEnter = (index: number) => {
    dragOverItem.current = index;
    setDragOverIndex(index);
  };

  const handleDragEnd = () => {
    if (dragItem.current !== null && dragOverItem.current !== null && dragItem.current !== dragOverItem.current) {
      reorderAgents(dragItem.current, dragOverItem.current);
    }
    dragItem.current = null;
    dragOverItem.current = null;
    setDragOverIndex(null);
  };

  const memoryCount = (agent: typeof config.agents[0]) => agent.memories?.length || 0;
  const componentCount = (agent: typeof config.agents[0]) =>
    agent.components ? Object.keys(agent.components).length : 0;

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
        <div className="space-y-2">
          {config.agents.map((agent, index) => {
            const badge = getPrefabBadge(agent.prefab);
            const mCount = memoryCount(agent);
            const cCount = componentCount(agent);

            return (
              <div
                key={agent.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragEnter={() => handleDragEnter(index)}
                onDragEnd={handleDragEnd}
                onDragOver={(e) => e.preventDefault()}
                className={`flex items-center justify-between p-3 rounded-md transition-colors cursor-grab active:cursor-grabbing ${
                  dragOverIndex === index
                    ? 'bg-blue-50 border-2 border-blue-300 border-dashed'
                    : 'bg-gray-50 hover:bg-gray-100 border border-transparent'
                }`}
              >
                {/* Drag handle */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/>
                    <circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/>
                    <circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/>
                  </svg>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 truncate">{agent.name}</p>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${badge.color}`}>
                        {badge.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      {agent.goal && (
                        <p className="text-xs text-gray-500 truncate max-w-[200px]">
                          {agent.goal}
                        </p>
                      )}
                      {mCount > 0 && (
                        <span className="text-xs text-gray-400" title={`${mCount} memories`}>
                          {mCount} mem
                        </span>
                      )}
                      {cCount > 0 && (
                        <span className="text-xs text-gray-400" title={`${cCount} components`}>
                          {cCount} comp
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-1 flex-shrink-0">
                  <button
                    onClick={() => handleDuplicate(agent.id)}
                    className="text-gray-400 hover:text-gray-600 p-1.5 rounded"
                    title="Duplicate agent"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setEditingAgent(agent.id)}
                    className="text-blue-600 hover:text-blue-800 p-1.5 rounded text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => removeAgent(agent.id)}
                    className="text-red-500 hover:text-red-700 p-1.5 rounded"
                    title="Remove agent"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {editingAgent && (
        <AgentEditor
          agentId={editingAgent}
          onClose={() => setEditingAgent(null)}
        />
      )}
    </div>
  );
}
