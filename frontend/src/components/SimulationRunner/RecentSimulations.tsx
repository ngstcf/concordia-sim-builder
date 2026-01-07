/**
 * RecentSimulations Component
 * Displays list of recent simulation logs and allows loading them
 */
import { useState, useEffect } from 'react';
import { getRecentSimulations, getSimulationLog } from '../../utils/api';

interface SimulationLog {
  filename: string;
  path: string;
  size: number;
  modified: number;
  created: number;
}

interface RecentSimulationsProps {
  onLoadSimulation: (htmlContent: string, filename: string) => void;
}

export default function RecentSimulations({ onLoadSimulation }: RecentSimulationsProps) {
  const [logs, setLogs] = useState<SimulationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecentSimulations();
  }, []);

  const loadRecentSimulations = async () => {
    setLoading(true);
    setError(null);
    try {
      const recentLogs = await getRecentSimulations(20);
      setLogs(recentLogs);
    } catch (err: any) {
      console.error('Error loading recent simulations:', err);
      setError(err.message || 'Failed to load recent simulations');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSimulation = async (filename: string) => {
    try {
      const logData = await getSimulationLog(filename);
      onLoadSimulation(logData.html_content, logData.filename);
    } catch (err: any) {
      console.error('Error loading simulation:', err);
      alert(`Failed to load simulation: ${err.message}`);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  const extractTitle = (filename: string): string => {
    // Remove timestamp and .html extension
    return filename
      .replace(/^\d{8}_\d{6}_/, '')
      .replace(/_/g, ' ')
      .replace(/\.html$/, '')
      .substring(0, 80);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Simulations</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading recent simulations...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Simulations</h3>
          <button
            onClick={loadRecentSimulations}
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

  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Simulations</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            No simulation logs found. Run a simulation to see it here!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Recent Simulations</h3>
        <button
          onClick={loadRecentSimulations}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Refresh
        </button>
      </div>
      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {logs.map((log) => (
          <div
            key={log.filename}
            className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => handleLoadSimulation(log.filename)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {extractTitle(log.filename)}
                </h4>
                <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                  <span>{formatDate(log.modified)}</span>
                  <span>{formatFileSize(log.size)}</span>
                </div>
              </div>
              <div className="ml-4 flex-shrink-0">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
