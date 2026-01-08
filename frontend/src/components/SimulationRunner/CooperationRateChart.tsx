/**
 * CooperationRateChart Component
 * Displays cooperation metrics for game-theoretic simulations
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics } from '../../utils/api';
import type { SimulationAnalytics } from '../../utils/api';

interface AgentCooperation {
  agent: string;
  cooperation_count: number;
  defection_count: number;
  total_actions: number;
  cooperation_rate: number;
}

interface CooperationRateChartProps {
  filename: string | null;
}

export default function CooperationRateChart({ filename }: CooperationRateChartProps) {
  const [analytics, setAnalytics] = useState<SimulationAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (filename) {
      loadAnalytics();
    } else {
      setAnalytics(null);
    }
  }, [filename]);

  const loadAnalytics = async () => {
    if (!filename) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);
    } catch (err: any) {
      console.error('Error loading analytics for cooperation rates:', err);
      setError(err.message || 'Failed to load cooperation data');
    } finally {
      setLoading(false);
    }
  };

  // Check if this is a game-theoretic simulation
  const isGameTheoretic = analytics?.gm_prefab?.includes('game_theoretic');

  // Extract cooperation data from agent actions
  const generateCooperationData = (): AgentCooperation[] => {
    if (!analytics || !analytics.agent_details) return [];

    return analytics.agents.map(agent => {
      const actions = analytics.agent_details?.[agent]?.actions || [];
      const totalActions = actions.length;

      // Analyze actions for cooperation indicators
      let cooperationCount = 0;
      let defectionCount = 0;

      actions.forEach(action => {
        const text = action.text.toLowerCase();

        // Cooperation indicators
        if (text.includes('cooperate') || text.includes('cooperates') ||
            text.includes('share') || text.includes('help') ||
            text.includes('trust') || text.includes('honest')) {
          cooperationCount++;
        }
        // Defection indicators
        else if (text.includes('defect') || text.includes('defects') ||
                 text.includes('betray') || text.includes('cheat') ||
                 text.includes('selfish') || text.includes('exploit')) {
          defectionCount++;
        }
        // If no clear indicator, count as unknown (neither)
      });

      const cooperationRate = totalActions > 0
        ? Math.round((cooperationCount / (cooperationCount + defectionCount)) * 100)
        : 0;

      return {
        agent,
        cooperation_count: cooperationCount,
        defection_count: defectionCount,
        total_actions: totalActions,
        cooperation_rate: cooperationRate
      };
    }).filter(d => d.total_actions > 0); // Only include agents with actions
  };

  const cooperationData = generateCooperationData();

  // Calculate overall statistics
  const totalCooperations = cooperationData.reduce((sum, d) => sum + d.cooperation_count, 0);
  const totalDefections = cooperationData.reduce((sum, d) => sum + d.defection_count, 0);
  const totalActions = totalCooperations + totalDefections;
  const overallCooperationRate = totalActions > 0 ? Math.round((totalCooperations / totalActions) * 100) : 0;

  if (!filename) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cooperation Analysis</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a game-theoretic simulation to see cooperation analysis
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cooperation Analysis</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading cooperation data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Cooperation Analysis</h3>
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

  if (!analytics || !isGameTheoretic) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cooperation Analysis</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            This visualization is for game-theoretic simulations (Prisoner's Dilemma, Marketplace, etc.)
          </p>
          {analytics && analytics.gm_prefab && (
            <p className="text-xs text-gray-400 mt-2">
              Current simulation uses: <code className="bg-gray-100 px-1 py-0.5 rounded">{analytics.gm_prefab}</code>
            </p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            Try loading a simulation with the <code className="bg-gray-100 px-1 py-0.5 rounded">game_theoretic__GameMaster</code> prefab.
          </p>
        </div>
      </div>
    );
  }

  // Check if there's any cooperation/defection data
  const hasCooperationData = cooperationData.length > 0 &&
    (totalCooperations > 0 || totalDefections > 0);

  if (!hasCooperationData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cooperation Analysis</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">No cooperation data available</p>
          <p className="text-xs text-gray-400 mt-2">The simulation may not have run long enough or doesn't contain clear cooperation/defection actions. Try running the simulation for more steps.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Cooperation Analysis</h3>
        </div>
      </div>

      <div className="p-5">
        {/* Overall Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-900">Total Cooperations</p>
                <p className="text-2xl font-bold text-green-700">{totalCooperations}</p>
              </div>
              <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-900">Total Defections</p>
                <p className="text-2xl font-bold text-red-700">{totalDefections}</p>
              </div>
              <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Cooperation Rate</p>
                <p className="text-2xl font-bold text-blue-700">{overallCooperationRate}%</p>
              </div>
              <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>

        {/* Per-Agent Cooperation Rates */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Per-Agent Cooperation Rates</h4>
          <div className="space-y-3">
            {cooperationData.map((data) => (
              <div key={data.agent} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{data.agent}</span>
                  <span className="text-sm text-gray-500">{data.total_actions} actions</span>
                </div>

                {/* Progress Bar */}
                <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full transition-all duration-500 rounded-full"
                    style={{
                      width: `${data.cooperation_rate}%`,
                      backgroundColor: data.cooperation_rate >= 50 ? '#10B981' : '#EF4444'
                    }}
                  ></div>
                </div>

                <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                  <span className="text-green-600 font-medium">{data.cooperation_count} cooperations</span>
                  <span className="font-bold">{data.cooperation_rate}%</span>
                  <span className="text-red-600 font-medium">{data.defection_count} defections</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stacked Bar Chart */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Overall Distribution</h4>
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="relative h-12 bg-gray-200 rounded-full overflow-hidden flex">
              {/* Cooperation portion */}
              <div
                className="h-full bg-green-500 transition-all duration-500"
                style={{ width: `${overallCooperationRate}%` }}
              ></div>
              {/* Defection portion */}
              <div
                className="h-full bg-red-500 transition-all duration-500"
                style={{ width: `${100 - overallCooperationRate}%` }}
              ></div>
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-8 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-green-500"></div>
                <span className="text-sm text-gray-700">
                  Cooperations ({totalCooperations}; {overallCooperationRate}%)
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-red-500"></div>
                <span className="text-sm text-gray-700">
                  Defections ({totalDefections}; {100 - overallCooperationRate}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Game Info */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <svg className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 className="text-sm font-semibold text-blue-900 mb-1">About This Visualization</h4>
                <p className="text-sm text-blue-800">
                  This chart shows cooperation and defection rates for game-theoretic simulations like Prisoner's Dilemma.
                  Higher cooperation rates indicate more collaborative behavior among agents.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
