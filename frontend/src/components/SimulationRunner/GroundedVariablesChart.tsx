/**
 * GroundedVariablesChart Component
 * Displays time-series charts for grounded variables
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics, extractGroundedVariables } from '../../utils/api';
import type { SimulationAnalytics } from '../../utils/api';
import type { LLMSettings } from '../../types/simulation';

interface VariableValue {
  step: number;
  value: number | string | boolean;
}

interface ChartableVariable {
  name: string;
  type: string;
  description: string;
  history: VariableValue[];
  minValue: number;
  maxValue: number;
}

interface GroundedVariablesChartProps {
  filename: string | null;
  simulationId?: string | null;
  llmSettings?: LLMSettings | null;
}

export default function GroundedVariablesChart({
  filename,
  simulationId,
  llmSettings
}: GroundedVariablesChartProps) {
  const [analytics, setAnalytics] = useState<SimulationAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVariables, setSelectedVariables] = useState<Set<string>>(new Set());
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState<string | null>(null);
  const [extractSuccess, setExtractSuccess] = useState(false);

  // Extract simulation ID from filename (timestamp format: YYYYMMDD_HHMMSS)
  const getSimulationIdFromFilename = (filename: string | null): string | null => {
    if (!filename) return null;
    // Extract timestamp from filename like "20260107_220128_simulation.html"
    const match = filename.match(/(\d{8}_\d{6})/);
    return match ? match[1] : null;
  };

  const actualSimulationId = simulationId || getSimulationIdFromFilename(filename);

  useEffect(() => {
    if (filename) {
      loadAnalytics();
    } else {
      setAnalytics(null);
      setSelectedVariables(new Set());
    }
  }, [filename]);

  const loadAnalytics = async () => {
    if (!filename) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);

      // Auto-select numerical and percentage variables by default
      const numericalVars = new Set<string>();
      data.grounded_variables.forEach(v => {
        if (v.type === 'numerical' || v.type === 'percentage') {
          numericalVars.add(v.name);
        }
      });
      setSelectedVariables(numericalVars);
    } catch (err: any) {
      console.error('Error loading grounded variables:', err);
      setError(err.message || 'Failed to load grounded variables');
    } finally {
      setLoading(false);
    }
  };

  const toggleVariable = (varName: string) => {
    const newSelected = new Set(selectedVariables);
    if (newSelected.has(varName)) {
      newSelected.delete(varName);
    } else {
      newSelected.add(varName);
    }
    setSelectedVariables(newSelected);
  };

  const handleExtractVariables = async () => {
    if (!filename || !actualSimulationId || !llmSettings) {
      setExtractError('Missing required information for extraction');
      return;
    }

    setExtracting(true);
    setExtractError(null);
    setExtractSuccess(false);

    try {
      await extractGroundedVariables(actualSimulationId, filename, llmSettings);

      // Reload analytics after extraction
      await loadAnalytics();
      setExtractSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => setExtractSuccess(false), 3000);
    } catch (err: any) {
      console.error('Error extracting grounded variables:', err);
      setExtractError(err.message || 'Failed to extract grounded variables');
    } finally {
      setExtracting(false);
    }
  };

  // Get chartable variables (numerical, percentage) with their history
  const getChartableVariables = (): ChartableVariable[] => {
    if (!analytics) return [];

    return analytics.grounded_variables
      .filter(v => v.type === 'numerical' || v.type === 'percentage')
      .map(v => {
        const history = v.history.map(h => ({
          step: h.step,
          value: typeof h.value === 'number' ? h.value : 0
        }));

        // Calculate min/max from history
        const values = history.map(h => h.value as number);
        const minValue = Math.min(...values, 0);
        const maxValue = Math.max(...values, 100);

        return {
          name: v.name,
          type: v.type,
          description: v.description,
          history,
          minValue,
          maxValue
        };
      });
  };

  // Get non-chartable variables (boolean, categorical)
  const getNonChartableVariables = () => {
    if (!analytics) return [];
    return analytics.grounded_variables.filter(
      v => v.type === 'boolean' || v.type === 'categorical'
    );
  };

  // Calculate chart Y-axis range from selected variables
  const getChartRange = () => {
    const chartableVars = getChartableVariables();
    const selectedVars = chartableVars.filter(v =>
      selectedVariables.has(v.name)
    );

    if (selectedVars.length === 0) return { min: 0, max: 100 };

    let min = Infinity;
    let max = -Infinity;

    selectedVars.forEach(v => {
      min = Math.min(min, v.minValue);
      max = Math.max(max, v.maxValue);
    });

    return {
      min: min === Infinity ? 0 : min,
      max: max === -Infinity ? 100 : max
    };
  };

  // Color palette for different variables
  const colors = [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // amber
    '#EF4444', // red
    '#8B5CF6', // purple
    '#EC4899', // pink
    '#06B6D4', // cyan
    '#84CC16', // lime
  ];

  if (!filename) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Grounded Variables</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 3M4 12h8m-8 0h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see grounded variables
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Grounded Variables</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading grounded variables...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Grounded Variables</h3>
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

  if (!analytics || analytics.grounded_variables.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Grounded Variables</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">No grounded variables found in this simulation</p>
          <p className="text-xs text-gray-400 mt-2">Grounded variables track state changes over time. Try a simulation with grounded variables enabled.</p>
        </div>
      </div>
    );
  }

  const chartableVars = getChartableVariables();

  // Check if there's any actual history data
  const hasChartData = chartableVars.some(v => v.history.length > 0);

  if (!hasChartData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Grounded Variables</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">No data available for grounded variables</p>
          <p className="text-xs text-gray-400 mt-2">Variable history needs to be extracted from the simulation log.</p>

          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800 mb-3">
              <strong>Extract Variable History:</strong> Use AI to analyze the simulation log and extract how variables changed over time.
            </p>

            {extractSuccess && (
              <div className="mb-3 p-2 bg-green-50 border border-green-200 rounded">
                <p className="text-xs text-green-800">✓ Variables extracted successfully!</p>
              </div>
            )}

            {extractError && (
              <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded">
                <p className="text-xs text-red-800">{extractError}</p>
              </div>
            )}

            {llmSettings && actualSimulationId ? (
              <button
                onClick={handleExtractVariables}
                disabled={extracting}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {extracting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Extracting...
                  </>
                ) : (
                  <>
                    <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Extract Variables
                  </>
                )}
              </button>
            ) : (
              <p className="text-xs text-gray-500">
                {!llmSettings && 'LLM settings not configured. '}
                {!actualSimulationId && 'Simulation ID not found.'}
              </p>
            )}

            <p className="text-xs text-blue-700 mt-2">
              Variables found: {chartableVars.length} chartable, {getNonChartableVariables().length} other
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { min: yMin, max: yMax } = getChartRange();
  const yRange = yMax - yMin;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">Grounded Variables</h3>
          </div>

          {/* Variable Count */}
          <span className="text-sm text-gray-500">
            {chartableVars.length} chartable variables
          </span>
        </div>
      </div>

      <div className="p-5">
        {/* Variable Selector */}
        {chartableVars.length > 0 && (
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Select variables to display:
            </label>
            <div className="flex flex-wrap gap-2">
              {chartableVars.map((variable, index) => (
                <button
                  key={variable.name}
                  onClick={() => toggleVariable(variable.name)}
                  className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    selectedVariables.has(variable.name)
                      ? 'text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  style={{
                    backgroundColor: selectedVariables.has(variable.name) ? colors[index % colors.length] : undefined
                  }}
                >
                  <span
                    className={`w-2 h-2 rounded-full mr-2 ${
                      selectedVariables.has(variable.name) ? 'bg-white' : 'bg-gray-400'
                    }`}
                  ></span>
                  {variable.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chart */}
        {selectedVariables.size > 0 ? (
          <div className="border border-gray-200 rounded-lg p-4">
            {/* Y-Axis Labels */}
            <div className="relative h-64 mb-4">
              {/* Y-axis */}
              <div className="absolute left-0 top-0 bottom-8 w-12 flex flex-col justify-between text-xs text-gray-500">
                <span>{yMax}</span>
                <span>{Math.round((yMax + yMin) / 2)}</span>
                <span>{yMin}</span>
              </div>

              {/* Chart Area */}
              <div className="ml-14 h-full relative border-l border-b border-gray-300">
                {/* Grid lines */}
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-gray-200 border-dashed"></div>
                  <div className="border-t border-gray-200 border-dashed"></div>
                  <div className="border-t border-gray-200"></div>
                </div>

                {/* Data Lines */}
                {Array.from(selectedVariables).map((varName, varIndex) => {
                  const variable = chartableVars.find(v => v.name === varName);
                  if (!variable) return null;

                  const data = variable.history;
                  const color = colors[varIndex % colors.length];

                  return (
                    <svg key={varName} className="absolute inset-0 w-full h-full" style={{ overflow: 'visible' }}>
                      <polyline
                        fill="none"
                        stroke={color}
                        strokeWidth="2"
                        points={data.map((point, i) => {
                          const x = (i / (data.length - 1)) * 100;
                          const y = 100 - ((point.value as number - yMin) / yRange) * 100;
                          return `${x}%,${y}%`;
                        }).join(' ')}
                      />

                      {/* Data points */}
                      {data.map((point, i) => {
                        const x = (i / (data.length - 1)) * 100;
                        const y = 100 - ((point.value as number - yMin) / yRange) * 100;
                        return (
                          <circle
                            key={i}
                            cx={`${x}%`}
                            cy={`${y}%`}
                            r="3"
                            fill={color}
                            className="hover:r-4 transition-all cursor-pointer"
                          >
                            <title>
                              {variable.name} (Step {point.step}): {point.value}
                            </title>
                          </circle>
                        );
                      })}
                    </svg>
                  );
                })}

                {/* X-axis labels */}
                <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-gray-500">
                  <span>Step 1</span>
                  <span>Step {Math.round((analytics.total_steps || 10) / 2)}</span>
                  <span>Step {analytics.total_steps || 10}</span>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 mt-8 pt-4 border-t border-gray-200">
              {Array.from(selectedVariables).map((varName, index) => {
                const variable = chartableVars.find(v => v.name === varName);
                if (!variable) return null;

                const color = colors[index % colors.length];

                return (
                  <div key={varName} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    ></div>
                    <span className="text-sm text-gray-700">{variable.name}</span>
                    <span className="text-xs text-gray-500">
                      ({variable.minValue.toFixed(1)} - {variable.maxValue.toFixed(1)})
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">Select variables above to display chart</p>
          </div>
        )}

        {/* Variable Details Table */}
        {chartableVars.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Variable Details</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Variable</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Range</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {chartableVars.map((variable) => (
                    <tr key={variable.name}>
                      <td className="px-4 py-2 text-sm font-medium text-gray-900">{variable.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-500 capitalize">{variable.type}</td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {variable.minValue.toFixed(1)} - {variable.maxValue.toFixed(1)}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500 max-w-xs truncate">
                        {variable.description || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Non-chartable variables (boolean, categorical) */}
        {getNonChartableVariables().length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Other Variables</h4>
            <div className="space-y-2">
              {getNonChartableVariables().map((variable) => (
                <div key={variable.name} className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-900">{variable.name}</span>
                      <span className="ml-2 text-xs text-gray-500 capitalize">({variable.type})</span>
                    </div>
                    {variable.description && (
                      <span className="text-sm text-gray-500">{variable.description}</span>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Current: {String(variable.current_value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
