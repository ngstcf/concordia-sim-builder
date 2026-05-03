import { useState } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';

export default function PlayerContextEditor() {
  const { config, setConfig } = useSimulation();
  const [isExpanded, setIsExpanded] = useState(
    !!config.player_specific_context && Object.keys(config.player_specific_context).length > 0
  );

  const playerContext = config.player_specific_context || {};

  const updateContext = (agentName: string, value: string) => {
    const updated = { ...playerContext, [agentName]: value };
    if (!value.trim()) {
      delete updated[agentName];
    }
    const hasContent = Object.values(updated).some(v => v.trim());
    setConfig({
      ...config,
      player_specific_context: hasContent ? updated : undefined,
    });
  };

  const agentNames = config.agents.map(a => a.name);
  const contextCount = Object.values(playerContext).filter(v => v.trim()).length;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
          <svg className="h-5 w-5 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Private Context
          {contextCount > 0 && (
            <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
              {contextCount} agent{contextCount !== 1 ? 's' : ''}
            </span>
          )}
        </h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      <p className="text-xs text-gray-500 mb-3">
        Private instructions only visible to each agent. Triggers formative memory generation for deeper character integration.
      </p>

      {isExpanded && (
        <div className="space-y-3">
          {agentNames.length === 0 ? (
            <p className="text-sm text-gray-400 italic">Add agents first to configure private context.</p>
          ) : (
            agentNames.map(name => (
              <div key={name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {name}
                </label>
                <textarea
                  rows={2}
                  className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  value={playerContext[name] || ''}
                  onChange={e => updateContext(name, e.target.value)}
                  placeholder={`Private information only ${name} knows...`}
                />
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
