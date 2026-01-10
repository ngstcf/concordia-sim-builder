/**
 * RecentSimulations Component
 * Displays list of recent simulation logs and allows loading them
 */
import { useState, useEffect } from 'react';
import { getRecentSimulations, getSimulationLog, getCheckpointFiles, deleteCheckpointFiles } from '../../utils/api';

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
  const [checkpointInfo, setCheckpointInfo] = useState<{ count: number; size: number }>({ count: 0, size: 0 });
  const [showCleanup, setShowCleanup] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [showCheckpoints, setShowCheckpoints] = useState(false);
  const [checkpoints, setCheckpoints] = useState<SimulationLog[]>([]);

  useEffect(() => {
    loadRecentSimulations();
    loadCheckpointInfo();
  }, []);

  const loadCheckpointInfo = async () => {
    try {
      const data = await getCheckpointFiles();
      console.log('Checkpoint data received:', data);
      setCheckpointInfo({
        count: data.total_count || 0,
        size: data.total_size || 0
      });
      // Convert checkpoint data to SimulationLog format
      if (data.checkpoints && data.checkpoints.length > 0) {
        setCheckpoints(data.checkpoints.map(cp => ({
          filename: cp.filename,
          path: cp.path,
          size: cp.size,
          modified: cp.modified,
          created: cp.modified
        })));
      }
    } catch (err) {
      console.error('Failed to load checkpoint info:', err);
      // Set empty state on error
      setCheckpointInfo({ count: 0, size: 0 });
    }
  };

  const toggleShowCheckpoints = () => {
    setShowCheckpoints(!showCheckpoints);
  };

  const handleDeleteCheckpoints = async () => {
    if (!confirm('Are you sure you want to delete all checkpoint files? This cannot be undone.')) {
      return;
    }

    setCleaning(true);
    try {
      const result = await deleteCheckpointFiles();
      alert(result.message);
      setCheckpointInfo({ count: 0, size: 0 });
      setCheckpoints([]);
      setShowCleanup(false);
      setShowCheckpoints(false);
      // Reload simulations list
      loadRecentSimulations();
    } catch (err: any) {
      alert(`Failed to delete checkpoints: ${err.message}`);
    } finally {
      setCleaning(false);
    }
  };

  const loadRecentSimulations = async () => {
    setLoading(true);
    setError(null);
    try {
      const recentLogs = await getRecentSimulations(100);
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

  const extractCheckpointStep = (filename: string): string | null => {
    // Extract step number from checkpoint files like "*_checkpoint_step25.html"
    const match = filename.match(/checkpoint_step(\d+)\.html$/);
    return match ? `Step ${match[1]}` : null;
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
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <h3 className="text-lg font-semibold text-gray-900">Recent Simulations</h3>
          <div className="flex items-center gap-3 flex-wrap">
            {/* Show checkpoints toggle */}
            {checkpointInfo.count > 0 && (
              <button
                onClick={toggleShowCheckpoints}
                className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md border transition-colors whitespace-nowrap"
                style={{
                  backgroundColor: showCheckpoints ? 'rgb(234 179 8)' : 'white',
                  borderColor: showCheckpoints ? 'rgb(234 179 8)' : 'rgb(229 231 235)',
                  color: showCheckpoints ? 'white' : 'rgb(55 65 81)'
                }}
              >
                <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {showCheckpoints ? 'Hide' : 'Show'} Checkpoints ({checkpointInfo.count})
              </button>
            )}
            {/* Checkpoint cleanup button */}
            {checkpointInfo.count > 0 && (
              <button
                onClick={() => setShowCleanup(true)}
                className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-orange-50 text-orange-700 hover:bg-orange-100 transition-colors whitespace-nowrap"
              >
                <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clean Up
              </button>
            )}
            <button
              onClick={loadRecentSimulations}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium whitespace-nowrap"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Checkpoint cleanup dialog */}
      {showCleanup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Clean Up Checkpoint Files</h3>
            <p className="text-sm text-gray-600 mb-4">
              Checkpoint files are incremental saves created during simulation. They can be safely deleted to free up space.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Checkpoint files:</span>
                <span className="font-medium text-gray-900">{checkpointInfo.count} files</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-gray-600">Total size:</span>
                <span className="font-medium text-gray-900">
                  {formatFileSize(checkpointInfo.size)}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowCleanup(false)}
                disabled={cleaning}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteCheckpoints}
                disabled={cleaning}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {cleaning ? 'Deleting...' : 'Delete All Checkpoints'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {/* Regular simulations */}
        {logs.map((log) => (
          <div
            key={log.filename}
            className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => handleLoadSimulation(log.filename)}
          >
            <div className="flex items-start justify-between gap-3 max-w-full">
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 break-all" style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}>
                  {extractTitle(log.filename)}
                </h4>
                <div className="mt-1 flex items-center gap-4 text-xs text-gray-500">
                  <span>{formatDate(log.modified)}</span>
                  <span>{formatFileSize(log.size)}</span>
                </div>
              </div>
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        ))}

        {/* Checkpoint files (when shown) */}
        {showCheckpoints && checkpoints.length > 0 && (
          <>
            <div className="bg-amber-50 px-4 py-2 text-xs font-medium text-amber-800 border-y border-amber-200">
              Checkpoint Files (incomplete simulations)
            </div>
            {checkpoints.map((checkpoint) => (
              <div
                key={checkpoint.filename}
                className="p-4 hover:bg-amber-50 transition-colors cursor-pointer bg-amber-50/30"
                onClick={() => handleLoadSimulation(checkpoint.filename)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 min-w-0">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 flex-shrink-0">
                        CHECKPOINT
                      </span>
                      <span className="min-w-0 flex-1" style={{ overflowWrap: 'anywhere' }}>
                        <h4 className="text-sm font-medium text-gray-900 break-all">
                          {extractTitle(checkpoint.filename)}
                        </h4>
                      </span>
                      {extractCheckpointStep(checkpoint.filename) && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-200 text-amber-900 flex-shrink-0">
                          {extractCheckpointStep(checkpoint.filename)}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex items-center gap-4 text-xs text-gray-500">
                      <span>{formatDate(checkpoint.modified)}</span>
                      <span>{formatFileSize(checkpoint.size)}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
