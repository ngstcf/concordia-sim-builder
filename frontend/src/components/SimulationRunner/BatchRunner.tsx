import { useState, useRef } from 'react';
import { useSimulation } from '../../contexts/SimulationContext';
import { executeBatchStream, exportBatchCSV, cancelBatch } from '../../utils/api';
import type { BatchRunResult } from '../../types/simulation';

interface SweepParam {
  field: string;
  values: string;
}

export default function BatchRunner({ onClose }: { onClose: () => void }) {
  const { config, llmSettings, gmLlmSettings } = useSimulation();
  const [numRuns, setNumRuns] = useState(3);
  const [batchName, setBatchName] = useState('');
  const [sweepParams, setSweepParams] = useState<SweepParam[]>([]);
  const [running, setRunning] = useState(false);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [results, setResults] = useState<BatchRunResult[]>([]);
  const [completedRuns, setCompletedRuns] = useState(0);
  const [totalRuns, setTotalRuns] = useState(0);
  const [batchStatus, setBatchStatus] = useState<string>('');
  const [error, setError] = useState('');
  const cancelRef = useRef<{ cancel: () => void } | null>(null);

  const addSweepParam = () => {
    setSweepParams([...sweepParams, { field: 'temperature', values: '0.3, 0.5, 0.7' }]);
  };

  const removeSweepParam = (index: number) => {
    setSweepParams(sweepParams.filter((_, i) => i !== index));
  };

  const updateSweepParam = (index: number, key: keyof SweepParam, value: string) => {
    setSweepParams(sweepParams.map((p, i) => i === index ? { ...p, [key]: value } : p));
  };

  const parseValues = (valuesStr: string, field: string): any[] => {
    return valuesStr.split(',').map(v => {
      const trimmed = v.trim();
      if (field === 'temperature') return parseFloat(trimmed);
      if (field === 'max_steps') return parseInt(trimmed);
      return trimmed;
    }).filter(v => v !== undefined && !Number.isNaN(v));
  };

  const handleStart = () => {
    setRunning(true);
    setError('');
    setResults([]);
    setCompletedRuns(0);
    setBatchStatus('running');

    const request = {
      config,
      llm_settings: llmSettings,
      gm_llm_settings: gmLlmSettings || undefined,
      num_runs: numRuns,
      sweep_parameters: sweepParams.map(p => ({
        field: p.field,
        values: parseValues(p.values, p.field),
      })),
      batch_name: batchName || undefined,
    };

    cancelRef.current = executeBatchStream(
      request,
      (event) => {
        if (event.type === 'batch_start') {
          setBatchId(event.batch_id);
          setTotalRuns(event.total_runs);
        } else if (event.type === 'run_complete') {
          setResults(prev => [...prev, event.run_result]);
          setCompletedRuns(event.completed_runs);
        } else if (event.type === 'batch_complete') {
          setBatchStatus('completed');
          setRunning(false);
        } else if (event.type === 'batch_cancelled') {
          setBatchStatus('cancelled');
          setRunning(false);
        }
      },
      (err) => {
        setError(err?.message || 'Batch execution failed');
        setRunning(false);
        setBatchStatus('error');
      },
    );
  };

  const handleCancel = async () => {
    cancelRef.current?.cancel();
    if (batchId) {
      try {
        await cancelBatch(batchId);
      } catch { /* ignore */ }
    }
    setRunning(false);
    setBatchStatus('cancelled');
  };

  const handleExportCSV = async () => {
    if (!batchId) return;
    try {
      const blob = await exportBatchCSV(batchId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_${batchId}_summary.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError('CSV export failed: ' + (e?.message || ''));
    }
  };

  const sweepFieldOptions = [
    { value: 'temperature', label: 'Temperature' },
    { value: 'max_steps', label: 'Max Steps' },
  ];

  const paramCombinations = sweepParams.length > 0
    ? sweepParams.reduce((acc, p) => acc * parseValues(p.values, p.field).length, 1)
    : 1;
  const estimatedTotalRuns = paramCombinations * numRuns;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[85vh] flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
              <svg className="h-5 w-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Batch Run
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600" disabled={running}>
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Run the current simulation configuration multiple times with optional parameter sweeps.
          </p>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {!running && batchStatus !== 'completed' ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Runs per Combination</label>
                  <input
                    type="number" min={1} max={50}
                    className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                    value={numRuns}
                    onChange={e => setNumRuns(parseInt(e.target.value) || 3)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Batch Name (optional)</label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                    value={batchName}
                    onChange={e => setBatchName(e.target.value)}
                    placeholder={`Batch ${new Date().toLocaleDateString()}`}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">Parameter Sweeps</label>
                  <button
                    onClick={addSweepParam}
                    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    + Add Parameter
                  </button>
                </div>
                {sweepParams.length === 0 ? (
                  <p className="text-xs text-gray-400 italic">
                    No parameter sweeps. Each run will use identical settings.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {sweepParams.map((param, index) => (
                      <div key={index} className="flex gap-2 items-center bg-gray-50 rounded-md p-2">
                        <select
                          value={param.field}
                          onChange={e => updateSweepParam(index, 'field', e.target.value)}
                          className="border border-gray-300 rounded-md py-1.5 px-2 text-sm"
                        >
                          {sweepFieldOptions.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                        <input
                          type="text"
                          value={param.values}
                          onChange={e => updateSweepParam(index, 'values', e.target.value)}
                          className="flex-1 border border-gray-300 rounded-md py-1.5 px-2 text-sm"
                          placeholder="0.3, 0.5, 0.7"
                        />
                        <button
                          onClick={() => removeSweepParam(index)}
                          className="text-red-400 hover:text-red-600 p-1"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-indigo-50 rounded-md p-3 text-sm text-indigo-700">
                Total runs: <span className="font-semibold">{estimatedTotalRuns}</span>
                {sweepParams.length > 0 && (
                  <span className="text-indigo-500">
                    {' '}({paramCombinations} combination{paramCombinations !== 1 ? 's' : ''} x {numRuns} run{numRuns !== 1 ? 's' : ''})
                  </span>
                )}
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-700">
                  {batchStatus === 'completed' ? 'Batch Complete' :
                   batchStatus === 'cancelled' ? 'Batch Cancelled' :
                   `Running... (${completedRuns}/${totalRuns})`}
                </p>
                {batchId && (
                  <span className="text-xs text-gray-400 font-mono">{batchId}</span>
                )}
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full transition-all ${
                    batchStatus === 'completed' ? 'bg-green-500' :
                    batchStatus === 'cancelled' ? 'bg-yellow-500' :
                    'bg-indigo-500'
                  }`}
                  style={{ width: `${totalRuns > 0 ? (completedRuns / totalRuns) * 100 : 0}%` }}
                />
              </div>

              {results.length > 0 && (
                <div className="border border-gray-200 rounded-md overflow-hidden">
                  <table className="w-full text-xs">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">#</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Parameters</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Status</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Time</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {results.map((r, i) => (
                        <tr key={i} className="hover:bg-gray-50">
                          <td className="px-3 py-1.5 text-gray-700">{r.run_index}</td>
                          <td className="px-3 py-1.5 text-gray-500 font-mono">
                            {Object.entries(r.parameters || {}).map(([k, v]) => `${k}=${v}`).join(', ') || 'default'}
                          </td>
                          <td className="px-3 py-1.5">
                            <span className={`inline-flex px-1.5 py-0.5 rounded-full text-[10px] font-medium ${
                              r.status === 'completed' ? 'bg-green-100 text-green-700' :
                              r.status === 'failed' ? 'bg-red-100 text-red-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>
                              {r.status}
                            </span>
                          </td>
                          <td className="px-3 py-1.5 text-right text-gray-500">
                            {r.elapsed_seconds ? `${r.elapsed_seconds}s` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="px-6 py-3 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0">
          {running ? (
            <button
              onClick={handleCancel}
              className="px-4 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-white hover:bg-red-50"
            >
              Cancel Batch
            </button>
          ) : batchStatus === 'completed' || batchStatus === 'cancelled' ? (
            <>
              {batchId && (
                <button
                  onClick={handleExportCSV}
                  className="px-4 py-2 border border-green-300 rounded-md text-sm font-medium text-green-700 bg-white hover:bg-green-50"
                >
                  Export CSV
                </button>
              )}
              <button
                onClick={() => { setResults([]); setBatchStatus(''); setBatchId(null); setCompletedRuns(0); }}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                New Batch
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Done
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleStart}
                disabled={!config.premise || config.agents.length === 0}
                className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Start Batch ({estimatedTotalRuns} run{estimatedTotalRuns !== 1 ? 's' : ''})
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
