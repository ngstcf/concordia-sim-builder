/**
 * SimulationRunner Component
 * Run simulations and view results
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulation } from '../../contexts/SimulationContext';
import { executeSimulationStream, validateConfig, cancelSimulation, getProviderModels } from '../../utils/api';
import RecentSimulations from './RecentSimulations';
import StatisticalDashboard from './StatisticalDashboard';
import TimelineVisualization from './TimelineVisualization';
import ActionsView from './ActionsView';
import NaturalLanguageSummary from './NaturalLanguageSummary';
import GroundedVariablesChart from './GroundedVariablesChart';
import CooperationRateChart from './CooperationRateChart';
import SimulationAnalysis from './SimulationAnalysis';

// Inject CSS styles into Concordia HTML logs to improve readability
function injectStyles(html: string): string {
  // First, let's peek at what kind of HTML structure we have
  const hasHead = html.includes('<head>');
  const hasHtml = html.includes('<html');
  const hasBody = html.includes('<body');

  console.log('HTML structure:', { hasHead, hasHtml, hasBody });

  const styles = `
    <style type="text/css">
      /* Reset and base improvements */
      * {
        box-sizing: border-box !important;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        line-height: 1.7 !important;
        color: #1f2937 !important;
        padding: 1.5rem !important;
        max-width: 100% !important;
        margin: 0 !important;
      }

      /* Improve paragraph spacing - key fix for readability */
      p {
        margin: 0 0 1rem 0 !important;
        line-height: 1.7 !important;
      }

      /* Add space between all direct children in main content areas */
      > div {
        margin-bottom: 1.5rem !important;
      }

      /* Make headings more prominent */
      h1, h2, h3, h4, h5, h6 {
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
      }
      h1 { font-size: 2rem !important; }
      h2 { font-size: 1.5rem !important; }
      h3 { font-size: 1.25rem !important; }

      /* Add space between list items */
      ul, ol {
        margin-bottom: 1rem !important;
        padding-left: 1.5rem !important;
      }
      li {
        margin-bottom: 0.5rem !important;
        line-height: 1.6 !important;
      }

      /* Improve table readability */
      table {
        margin: 1rem 0 !important;
        border-collapse: collapse !important;
        width: 100% !important;
      }
      td, th {
        padding: 0.75rem !important;
        border: 1px solid #e5e7eb !important;
        text-align: left !important;
      }
      th {
        background: #f9fafb !important;
        font-weight: 600 !important;
      }

      /* Add visual separation for dialogue/interactions */
      div[class*="message"],
      div[class*="dialogue"],
      div[class*="utterance"],
      div[class*="interaction"],
      div[class*="action"] {
        margin: 1rem 0 !important;
        padding: 1rem !important;
        background: #f9fafb !important;
        border-radius: 0.5rem !important;
        border-left: 3px solid #d1d5db !important;
      }

      /* Highlight step/section indicators */
      div[id*="step"],
      div[id*="Step"],
      div[class*="step"],
      div[class*="Step"],
      section {
        margin: 2rem 0 !important;
        padding: 1.5rem !important;
        background: #eff6ff !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 0.5rem !important;
      }

      /* Make tabs more visible */
      .tabs,
      [role="tablist"],
      div[class*="tab"] {
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #e5e7eb !important;
      }
      [role="tab"],
      button[class*="tab"] {
        padding: 0.5rem 1rem !important;
        margin-right: 0.25rem !important;
        border-radius: 0.375rem 0.375rem 0 0 !important;
        background: #f3f4f6 !important;
        border: none !important;
        cursor: pointer !important;
      }
      [role="tab"][aria-selected="true"],
      button[class*="tab"].active {
        background: #3b82f6 !important;
        color: white !important;
      }

      /* Tab content panels */
      [role="tabpanel"],
      div[class*="tabpanel"],
      div[class*="tab-content"] {
        padding: 1rem 0 !important;
      }

      /* Add spacing between generic div elements */
      div {
        margin-bottom: 0.5rem !important;
      }

      /* Better spacing for pre/code blocks */
      pre, code {
        background: #f3f4f6 !important;
        padding: 0.75rem !important;
        border-radius: 0.375rem !important;
        font-size: 0.875rem !important;
        line-height: 1.5 !important;
      }

      /* Separator styling */
      hr {
        margin: 2rem 0 !important;
        border: none !important;
        border-top: 2px solid #e5e7eb !important;
      }
    </style>
  `;

  // Inject styles strategically
  if (hasHead) {
    // Best case: inject into existing head
    return html.replace('</head>', styles + '</head>');
  } else if (hasHtml) {
    // Has html tag but no head - add head after html tag
    return html.replace(/(<html[^>]*>)/, '$1<head>' + styles + '</head>');
  } else if (hasBody) {
    // Has body but no html - inject at start of body
    return html.replace('<body>', '<body>' + styles);
  }

  // Fragment or unknown structure - prepend styles
  return '<!DOCTYPE html><html><head>' + styles + '</head><body>' + html + '</body></html>';
}

// TimeoutWarning Component - shows warning when approaching simulation timeout
function TimeoutWarning({ startTime, timeout, warningThreshold }: { startTime: number; timeout: number; warningThreshold: number }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const updateElapsed = () => {
      setElapsed(Date.now() - startTime);
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const remaining = timeout - elapsed;
  const isWarning = elapsed >= warningThreshold;
  const isCritical = remaining < 5 * 60 * 1000; // Less than 5 minutes remaining

  const formatTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (!isWarning) return null;

  return (
    <div className={`mx-5 mt-4 rounded-lg p-3 border flex items-center gap-3 ${
      isCritical
        ? 'bg-red-50 border-red-200'
        : 'bg-yellow-50 border-yellow-200'
    }`}>
      <svg className={`h-5 w-5 flex-shrink-0 ${isCritical ? 'text-red-600' : 'text-yellow-600'}`} fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
      <div className="flex-1">
        <p className={`text-sm font-medium ${isCritical ? 'text-red-800' : 'text-yellow-800'}`}>
          {isCritical ? 'Critical: Simulation timeout imminent!' : 'Warning: Approaching timeout'}
        </p>
        <p className={`text-xs mt-0.5 ${isCritical ? 'text-red-700' : 'text-yellow-700'}`}>
          Elapsed: {formatTime(elapsed)} • {isCritical ? `${formatTime(remaining)} remaining` : `Timeout in ${formatTime(remaining)}`}
        </p>
      </div>
    </div>
  );
}

export default function SimulationRunner() {
  const navigate = useNavigate();
  const { config, validation, setValidation, llmSettings, setLLMSettings } = useSimulation();
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'log' | 'statistics' | 'timeline' | 'actions' | 'summary' | 'grounded-variables' | 'cooperation' | 'analysis'>('log');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [progress, setProgress] = useState<{
    step: number;
    max_steps: number;
    elapsed: number;
    est_remaining: number;
    est_time_str: string;
  } | null>(null);

  // Timeout warning state - track elapsed time for running simulations
  const SIMULATION_TIMEOUT = parseInt(import.meta.env.VITE_SIMULATION_TIMEOUT || '18000000', 10);
  const WARNING_THRESHOLD = SIMULATION_TIMEOUT * 0.8; // Show warning at 80% of timeout

  // Model selection state
  const [availableModels, setAvailableModels] = useState<Array<{ id: string; name: string; [key: string]: any }>>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [modelsError, setModelsError] = useState<string | null>(null);

  // Fetch available models when provider changes
  useEffect(() => {
    const fetchModels = async () => {
      if (!llmSettings.provider) return;

      setLoadingModels(true);
      setModelsError(null);

      try {
        const result = await getProviderModels(
          llmSettings.provider,
          llmSettings.api_key,
          llmSettings.base_url
        );

        if (result.error) {
          setModelsError(result.error);
          setAvailableModels([]);
        } else {
          setAvailableModels(result.models);
          // Auto-select the first model if the current one is not in the list
          if (result.models.length > 0 && !result.models.find(m => m.id === llmSettings.model_name)) {
            setLLMSettings({ ...llmSettings, model_name: result.models[0].id });
          }
        }
      } catch (err: any) {
        setModelsError(err.message || 'Failed to fetch models');
        setAvailableModels([]);
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, [llmSettings.provider]);

  const handleLoadSimulation = (htmlContent: string, filename: string, modified: number) => {
    setResults({
      results: htmlContent,
      log_filename: filename,
      log_path: `logs/${filename}`,
      completed: true,
      timestamp: modified
    });
    setError(null);
  };

  const handleRun = async () => {
    console.log('[handleRun] Starting...');
    setError(null);
    setResults(null);
    setTaskId(null);
    setProgress(null);

    // Check if there are agents before validating
    if (config.agents.length === 0 || !config.premise) {
      setError('Please add at least one agent and a premise before running.');
      return;
    }

    // Validate first
    try {
      const validationResult = await validateConfig(config);
      setValidation(validationResult);

      if (!validationResult.valid) {
        setError('Configuration is invalid. Please fix errors before running.');
        return;
      }
    } catch (err: any) {
      console.error('Validation error:', err);
      setError(err.message || 'Validation failed');
      return;
    }

    setRunning(true);
    setCancelling(false);
    console.log('[handleRun] About to call executeSimulationStream');

    // Use streaming execution for progress updates
    await executeSimulationStream(
      config,
      llmSettings,
      // onProgress
      (progressData: any) => {
        console.log('[handleRun] onProgress callback called with:', progressData);
        if (progressData.task_id) {
          setTaskId(progressData.task_id);
        }
        setProgress(progressData);
      },
      // onComplete
      (result) => {
        console.log('[handleRun] onComplete callback called');
        setResults(result);
        setProgress(null);
        setRunning(false);
      },
      // onError
      (errMsg) => {
        console.log('[handleRun] onError callback called:', errMsg);
        setError(errMsg);
        setProgress(null);
        setRunning(false);
      }
    );
    console.log('[handleRun] executeSimulationStream completed');
  };

  const handleCancel = async () => {
    if (!taskId) {
      setError('No simulation to cancel.');
      return;
    }

    setCancelling(true);
    try {
      await cancelSimulation(taskId);
      setError('Simulation cancellation requested. Please wait...');
      // Don't set running to false yet - wait for the actual cancellation
    } catch (err: any) {
      console.error('Cancel error:', err);
      setError(err.message || 'Failed to cancel simulation');
      setCancelling(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Simulation Runner</h2>
          <p className="text-sm text-gray-500">
            Configure and run your simulation
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          ← Back to Builder
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Settings & Config */}
        <div className="lg:col-span-1 space-y-6">
          {/* LLM Settings */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900">LLM Settings</h3>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Provider</label>
                <select
                  className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={llmSettings.provider}
                  onChange={(e) => {
                    const provider = e.target.value as any;
                    const timeout = (provider === 'ollama' || provider === 'ollama_remote') ? 300 : 120;
                    setLLMSettings({ ...llmSettings, provider, request_timeout: timeout });
                  }}
                >
                  <option value="deepseek">DeepSeek</option>
                  <option value="openai">OpenAI</option>
                  <option value="azure">Azure OpenAI</option>
                  <option value="gemini">Gemini</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="glm">GLM (Zhipu AI)</option>
                  <option value="ollama">Ollama (Local)</option>
                  <option value="ollama_remote">Ollama (Remote)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Model</label>
                {loadingModels ? (
                  <div className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 bg-gray-50 flex items-center">
                    <svg className="animate-spin h-4 w-4 text-gray-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-gray-500">Loading models...</span>
                  </div>
                ) : modelsError ? (
                  <div className="w-full">
                    <select
                      className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={llmSettings.model_name}
                      onChange={(e) => setLLMSettings({ ...llmSettings, model_name: e.target.value })}
                    >
                      <option value="">Custom model</option>
                      {availableModels.map(model => (
                        <option key={model.id} value={model.id}>
                          {model.name || model.id}
                        </option>
                      ))}
                    </select>
                    <p className="mt-1 text-xs text-amber-600">{modelsError}</p>
                  </div>
                ) : availableModels.length > 0 ? (
                  <select
                    className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={llmSettings.model_name}
                    onChange={(e) => setLLMSettings({ ...llmSettings, model_name: e.target.value })}
                  >
                    {availableModels.map(model => (
                      <option key={model.id} value={model.id}>
                        {model.name || model.id}
                      </option>
                    ))}
                  </select>
                ) : (
                  <>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={llmSettings.model_name}
                      onChange={(e) => setLLMSettings({ ...llmSettings, model_name: e.target.value })}
                      placeholder={llmSettings.provider === 'azure' ? "Enter deployment name (e.g., my-gpt4-deployment)" : "Enter model name manually"}
                    />
                    {llmSettings.provider === 'azure' && (
                      <p className="text-xs text-blue-600 mt-1 bg-blue-50 p-2 rounded">
                        <strong>Azure OpenAI:</strong> Enter your <strong>deployment name</strong> from Azure Portal.<br/>
                        Other parameters (endpoint, API key, API version) are loaded from <code className="text-xs bg-blue-100 px-1 rounded">.env</code> file.<br/>
                        Required env vars: <code className="text-xs bg-blue-100 px-1 rounded">AZURE_OAI_KEY</code>, <code className="text-xs bg-blue-100 px-1 rounded">AZURE_OAI_ENDPOINT</code>
                      </p>
                    )}
                  </>
                )}
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Temperature
                  <span className="text-gray-400 ml-1" title="Controls randomness. Higher = more creative">ⓘ</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={llmSettings.temperature}
                  onChange={(e) => setLLMSettings({ ...llmSettings, temperature: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Max Tokens
                  <span className="text-gray-400 ml-1" title="Maximum tokens to generate per response">ⓘ</span>
                </label>
                <input
                  type="number"
                  step="100"
                  min="1"
                  max="32000"
                  className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={llmSettings.max_tokens}
                  onChange={(e) => setLLMSettings({ ...llmSettings, max_tokens: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Request Timeout (s)
                  <span className="text-gray-400 ml-1" title="Max seconds to wait for each LLM response. Increase for slow models (e.g. Ollama Remote).">ⓘ</span>
                </label>
                <input
                  type="number"
                  step="10"
                  min="10"
                  max="600"
                  className="w-full border border-gray-300 rounded-lg text-sm py-2 px-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={llmSettings.request_timeout}
                  onChange={(e) => setLLMSettings({ ...llmSettings, request_timeout: parseInt(e.target.value) || 120 })}
                />
              </div>
            </div>
          </div>

          {/* Run/Cancel Buttons */}
          <div className="flex gap-3">
            {!running ? (
              <button
                onClick={handleRun}
                disabled={validation ? !validation.valid : undefined}
                className={`flex-1 py-3 px-6 rounded-xl text-base font-semibold transition-all ${
                  validation && !validation.valid
                    ? 'bg-gray-300 cursor-not-allowed text-gray-500'
                    : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg'
                }`}
              >
                Run Simulation
              </button>
            ) : (
              <>
                <button
                  onClick={handleCancel}
                  disabled={cancelling}
                  className={`flex-1 py-3 px-6 rounded-xl text-base font-semibold transition-all ${
                    cancelling
                      ? 'bg-gray-300 cursor-not-allowed text-gray-500'
                      : 'bg-red-600 hover:bg-red-700 text-white shadow-md hover:shadow-lg'
                  }`}
                >
                  {cancelling ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Cancelling...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <svg className="mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Cancel Simulation
                    </span>
                  )}
                </button>
                <div className="flex-1 bg-blue-50 border border-blue-200 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <svg className="animate-spin h-6 w-6 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="mt-2 text-sm font-medium text-blue-900">Running...</p>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Config Summary Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900">Configuration</h3>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <span className="text-xs font-medium text-gray-500">Premise</span>
                <p className="mt-1 text-sm text-gray-800 line-clamp-3">{config.premise}</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 rounded-lg p-2">
                  <span className="text-xs text-gray-500">Steps</span>
                  <p className="text-sm font-semibold text-gray-900">{config.max_steps}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-2">
                  <span className="text-xs text-gray-500">Agents</span>
                  <p className="text-sm font-semibold text-gray-900">{config.agents.length}</p>
                </div>
              </div>
              <details className="text-xs">
                <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-medium">
                  View details
                </summary>
                <div className="mt-3 space-y-2">
                  {config.agents.map((agent) => (
                    <div key={agent.id} className="bg-gray-50 rounded p-2">
                      <p className="font-medium text-gray-900">{agent.name}</p>
                      {agent.goal && <p className="text-gray-600 mt-1">{agent.goal}</p>}
                    </div>
                  ))}
                </div>
              </details>
            </div>
          </div>

          {/* Recent Simulations */}
          <RecentSimulations onLoadSimulation={handleLoadSimulation} />
        </div>

        {/* Right Column - Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Validation Status */}
          {validation && (
            <div className={`rounded-xl p-4 ${validation.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  {validation.valid ? (
                    <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <h3 className={`text-sm font-medium ${validation.valid ? 'text-green-800' : 'text-red-800'}`}>
                    {validation.valid ? 'Configuration valid' : 'Configuration has errors'}
                  </h3>
                  {!validation.valid && validation.errors.length > 0 && (
                    <ul className="mt-2 text-sm text-red-700 space-y-1">
                      {validation.errors.map((err, i) => (
                        <li key={i}>• {err}</li>
                      ))}
                    </ul>
                  )}
                  {validation.valid && validation.warnings.length > 0 && (
                    <ul className="mt-2 text-sm text-yellow-700 space-y-1">
                      {validation.warnings.map((warn, i) => (
                        <li key={i}>⚠️ {warn}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Running Progress */}
          {running && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-center">
                <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-semibold text-blue-900">Simulation Running</h3>
                  {progress ? (
                    <>
                      <p className="mt-1 text-sm text-blue-700">
                        {progress.step}/{progress.max_steps} steps completed
                      </p>
                      <p className="mt-1 text-xs text-blue-600 font-mono">
                        (elapsed: {progress.elapsed.toFixed(0)}s, est. remaining: {progress.est_time_str})
                      </p>
                      <div className="mt-2 bg-blue-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(progress.step / progress.max_steps) * 100}%` }}
                        ></div>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="mt-1 text-sm text-blue-700">
                        Running {config.max_steps} steps with {config.agents.length} agent{config.agents.length > 1 ? 's' : ''}...
                      </p>
                      <p className="mt-1 text-xs text-blue-600">
                        If this takes too long, check the Recent Simulations section for the result.
                      </p>
                      <div className="mt-2 bg-blue-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              {/* Timeout Warning Banner */}
              {!results.completed && (
                <TimeoutWarning startTime={results.timestamp * 1000} timeout={SIMULATION_TIMEOUT} warningThreshold={WARNING_THRESHOLD} />
              )}

              {/* Results Header */}
              <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Results</h3>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {results.completed ? (
                      <span className="text-green-600">✓ Completed</span>
                    ) : (
                      <span className="text-yellow-600">In Progress</span>
                    )} • {new Date(results.timestamp * 1000).toLocaleString()}
                  </p>
                </div>
                {results.log_filename && (
                  <button
                    onClick={() => {
                      const blob = new Blob([results.results], { type: 'text/html' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = results.log_filename;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </button>
                )}
              </div>

              {/* Log file info */}
              {results.log_filename && (
                <div className="mx-5 mt-4 bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-xs text-green-700 flex-1 min-w-0">
                      Log saved to <code className="bg-green-100 px-1.5 py-0.5 rounded text-xs break-all" style={{ wordBreak: 'break-all', overflowWrap: 'anywhere' }}>{results.log_path}</code>
                    </span>
                  </div>
                </div>
              )}

              {/* Analytics Tabs */}
              <div className="px-5 pt-5">
                <div className="border-b border-gray-200">
                  <nav className="flex space-x-6 overflow-x-auto" aria-label="Tabs">
                    <button
                      onClick={() => setActiveTab('log')}
                      className={`${
                        activeTab === 'log'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Simulation Log
                    </button>
                    <button
                      onClick={() => setActiveTab('statistics')}
                      className={`${
                        activeTab === 'statistics'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Statistical Dashboard
                    </button>
                    <button
                      onClick={() => setActiveTab('timeline')}
                      className={`${
                        activeTab === 'timeline'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Timeline
                    </button>
                    <button
                      onClick={() => setActiveTab('grounded-variables')}
                      className={`${
                        activeTab === 'grounded-variables'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Grounded Variables
                    </button>
                    <button
                      onClick={() => setActiveTab('cooperation')}
                      className={`${
                        activeTab === 'cooperation'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Cooperation
                    </button>
                    <button
                      onClick={() => setActiveTab('actions')}
                      className={`${
                        activeTab === 'actions'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Actions
                    </button>
                    <button
                      onClick={() => setActiveTab('summary')}
                      className={`${
                        activeTab === 'summary'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      AI Summary
                    </button>
                    <button
                      onClick={() => setActiveTab('analysis')}
                      className={`${
                        activeTab === 'analysis'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-colors min-w-fit`}
                    >
                      Analysis
                    </button>
                  </nav>
                </div>
              </div>

              {/* Tab Content */}
              <div className="p-5">
                {activeTab === 'log' && results.results && (
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-700">Simulation Log</span>
                      <span className="text-xs text-gray-500">Use tabs to switch views</span>
                    </div>
                    <div className="bg-white" style={{ height: '500px' }}>
                      <iframe
                        srcDoc={injectStyles(results.results)}
                        className="w-full h-full border-0"
                        sandbox="allow-same-origin allow-scripts"
                        title="Simulation Log"
                      />
                    </div>
                  </div>
                )}

                {activeTab === 'statistics' && (
                  <StatisticalDashboard filename={results.log_filename || null} />
                )}

                {activeTab === 'timeline' && (
                  <TimelineVisualization filename={results.log_filename || null} />
                )}

                {activeTab === 'actions' && (
                  <ActionsView filename={results.log_filename || null} />
                )}

                {activeTab === 'summary' && (
                  <NaturalLanguageSummary
                    filename={results.log_filename || null}
                    htmlContent={results.results || null}
                  />
                )}

                {activeTab === 'grounded-variables' && (
                  <GroundedVariablesChart
                    filename={results.log_filename || null}
                    simulationId={results.task_id || null}
                    llmSettings={llmSettings}
                  />
                )}

                {activeTab === 'cooperation' && (
                  <CooperationRateChart filename={results.log_filename || null} />
                )}

                {activeTab === 'analysis' && (
                  <SimulationAnalysis
                    simulationId={results.task_id || null}
                    logFilename={results.log_filename || null}
                    llmSettings={llmSettings}
                  />
                )}
              </div>

              {/* Raw JSON (collapsible) */}
              <details className="px-5 pb-5">
                <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700">
                  Raw JSON Response
                </summary>
                <pre className="mt-3 bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </details>
            </div>
          )}

          {/* Empty state when no results */}
          {!results && !running && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Ready to Run</h3>
              <p className="mt-2 text-sm text-gray-500">
                Configure your LLM settings and click "Run Simulation" to begin
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
