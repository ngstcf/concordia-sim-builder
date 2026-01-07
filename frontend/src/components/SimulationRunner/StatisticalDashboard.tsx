/**
 * StatisticalDashboard Component
 * Displays statistical analysis of simulation results
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics } from '../../utils/api';

interface AnalyticsData {
  filename: string;
  file_size: number;
  modified: number;
  total_steps: number;
  agents: string[];
  agent_actions: Record<string, number>;
  total_observations: number;
  interactions: any[];
  timeline: Array<{
    step: number;
    description: string;
    type: string;
  }>;
  word_count: number;
  character_count: number;
}

interface StatisticalDashboardProps {
  filename: string | null;
}

export default function StatisticalDashboard({ filename }: StatisticalDashboardProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
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
      console.error('Error loading analytics:', err);
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!filename) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistical Dashboard</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see statistics and analytics
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistical Dashboard</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Statistical Dashboard</h3>
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

  if (!analytics) {
    return null;
  }

  const totalActions = Object.values(analytics.agent_actions).reduce((sum, count) => sum + count, 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Statistical Dashboard</h3>
        <button
          onClick={loadAnalytics}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="p-5 space-y-6">
        {/* Overview Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-blue-600 uppercase tracking-wide">Total Steps</p>
                <p className="mt-1 text-2xl font-bold text-blue-900">{analytics.total_steps}</p>
              </div>
              <svg className="h-8 w-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-green-600 uppercase tracking-wide">Agents</p>
                <p className="mt-1 text-2xl font-bold text-green-900">{analytics.agents.length}</p>
              </div>
              <svg className="h-8 w-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>

          <div className="bg-purple-50 rounded-lg p-4 relative group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-purple-600 uppercase tracking-wide">Observations</p>
                <p className="mt-1 text-2xl font-bold text-purple-900">{analytics.total_observations}</p>
              </div>
              <svg className="h-8 w-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            {/* Tooltip */}
            <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block z-10">
              <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 max-w-xs">
                <p className="font-medium mb-1">What are observations?</p>
                <p className="text-gray-300">Observations are what agents perceive about their environment and other agents during the simulation. They form the basis for agent decision-making.</p>
                <div className="absolute bottom-0 left-4 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-orange-600 uppercase tracking-wide">Total Actions</p>
                <p className="mt-1 text-2xl font-bold text-orange-900">{totalActions}</p>
              </div>
              <svg className="h-8 w-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Agent Breakdown */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Agent Activity</h4>
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            {analytics.agents.map((agent) => {
              const actionCount = analytics.agent_actions[agent] || 0;
              const percentage = totalActions > 0 ? (actionCount / totalActions) * 100 : 0;
              return (
                <div key={agent} className="border border-gray-200 rounded-lg p-3 bg-white">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-900">{agent}</span>
                    <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                      {actionCount} actions
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all"
                        style={{ width: `${Math.max(percentage, 2)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600 min-w-[60px] text-right">
                      {percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Text Statistics */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Text Statistics</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Word Count</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{formatNumber(analytics.word_count)}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Character Count</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{formatNumber(analytics.character_count)}</p>
            </div>
          </div>
        </div>

        {/* File Info */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">File Information</h4>
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Filename</span>
              <span className="text-sm font-medium text-gray-900 truncate ml-4 max-w-xs" title={analytics.filename}>
                {analytics.filename}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">File Size</span>
              <span className="text-sm font-medium text-gray-900">{formatFileSize(analytics.file_size)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Last Modified</span>
              <span className="text-sm font-medium text-gray-900">
                {new Date(analytics.modified * 1000).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
