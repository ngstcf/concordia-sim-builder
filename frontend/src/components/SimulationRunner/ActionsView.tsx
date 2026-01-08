/**
 * ActionsView Component
 * Displays agent-specific actions extracted from simulation logs
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics } from '../../utils/api';

interface AgentAction {
  step: number | null;
  action: string;
  goal?: string;
}

interface AgentDetails {
  actions: AgentAction[];
  goal: string;
  memories: string[];
}

interface AnalyticsData {
  filename: string;
  agents: string[];
  agent_details?: Record<string, AgentDetails>;
  premise?: string;
}

interface ActionsViewProps {
  filename: string | null;
}

export default function ActionsView({ filename }: ActionsViewProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  useEffect(() => {
    if (filename) {
      loadAnalytics();
    } else {
      setAnalytics(null);
      setSelectedAgent(null);
    }
  }, [filename]);

  useEffect(() => {
    if (analytics && analytics.agents.length > 0 && !selectedAgent) {
      setSelectedAgent(analytics.agents[0]);
    }
  }, [analytics, selectedAgent]);

  const loadAnalytics = async () => {
    if (!filename) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);
    } catch (err: any) {
      console.error('Error loading analytics for actions:', err);
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (!filename) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Actions</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see agent actions
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Actions</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading actions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Agent Actions</h3>
          <button
            onClick={loadAnalytics}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Retry
          </button>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!analytics || analytics.agents.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Actions</h3>
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">No agent actions found in this simulation</p>
        </div>
      </div>
    );
  }

  const currentAgent = selectedAgent && analytics.agent_details ? analytics.agent_details[selectedAgent] : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header with Agent Selector */}
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">Agent Actions</h3>
          </div>

          {/* Agent Selector Dropdown */}
          <select
            value={selectedAgent || ''}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {analytics.agents.map((agent) => (
              <option key={agent} value={agent}>
                {agent} ({analytics.agent_details?.[agent]?.actions.length || 0} actions)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {currentAgent && (
          <div className="space-y-6">
            {/* Agent Goal */}
            {currentAgent.goal && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <svg className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-semibold text-blue-900 mb-1">Goal</h4>
                    <p className="text-sm text-blue-800">{currentAgent.goal}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Memories */}
            {currentAgent.memories.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Context & Memories</h4>
                <div className="space-y-2">
                  {currentAgent.memories.map((memory, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-3 border-l-4 border-gray-300">
                      <p className="text-sm text-gray-700">{memory}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions List */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">
                Actions ({currentAgent.actions.length})
              </h4>
              {currentAgent.actions.length === 0 ? (
                <div className="text-center py-8 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">No actions recorded for this agent</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {currentAgent.actions.map((action, idx) => (
                    <div
                      key={idx}
                      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                    >
                      <div className="flex items-start gap-3">
                        {/* Step Badge */}
                        {action.step !== null && (
                          <div className="flex-shrink-0">
                            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold">
                              {action.step}
                            </span>
                          </div>
                        )}

                        {/* Action Content */}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 leading-relaxed">
                            {action.action}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
