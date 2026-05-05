import { useState } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import type { AvailableAction } from '../../types/simulation';

export default function AvailableActionsEditor() {
  const { config, setConfig } = useSimulation();
  const [expanded, setExpanded] = useState(false);

  const actions: AvailableAction[] = config.available_actions || [];

  const updateActions = (newActions: AvailableAction[]) => {
    setConfig({
      ...config,
      available_actions: newActions.length > 0 ? newActions : undefined,
    });
  };

  const addAction = () => {
    updateActions([...actions, { name: '', description: '' }]);
    if (!expanded) setExpanded(true);
  };

  const removeAction = (index: number) => {
    updateActions(actions.filter((_, i) => i !== index));
  };

  const updateAction = (index: number, field: keyof AvailableAction, value: string) => {
    const updated = actions.map((a, i) =>
      i === index ? { ...a, [field]: value } : a
    );
    updateActions(updated);
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-2">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Available Actions
            {actions.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({actions.length})
              </span>
            )}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Constrain what agents can do each step. When set, agents choose from this list.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {actions.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              {expanded ? 'Collapse' : 'Expand'}
            </button>
          )}
          <button
            onClick={addAction}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg className="mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Action
          </button>
        </div>
      </div>

      {actions.length === 0 ? (
        <p className="text-sm text-gray-400 italic">
          No action constraints. Agents will decide freely what to do.
        </p>
      ) : expanded ? (
        <div className="space-y-3 mt-3">
          {actions.map((action, index) => (
            <div key={index} className="flex gap-3 items-start bg-gray-50 rounded-md p-3">
              <div className="flex-1 grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-0.5">Action Name</label>
                  <input
                    type="text"
                    value={action.name}
                    onChange={e => updateAction(index, 'name', e.target.value)}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="go_to_work"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-0.5">Description</label>
                  <input
                    type="text"
                    value={action.description}
                    onChange={e => updateAction(index, 'description', e.target.value)}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Travel to workplace and begin shift"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-gray-600 mb-0.5">Condition (optional)</label>
                  <input
                    type="text"
                    value={action.condition || ''}
                    onChange={e => updateAction(index, 'condition', e.target.value)}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., only during business hours"
                  />
                </div>
              </div>
              <button
                onClick={() => removeAction(index)}
                className="text-red-400 hover:text-red-600 p-1 mt-4"
                title="Remove action"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {actions.map((action, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {action.name || `Action ${index + 1}`}
              <button
                onClick={() => removeAction(index)}
                className="ml-1 text-blue-600 hover:text-blue-900"
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
