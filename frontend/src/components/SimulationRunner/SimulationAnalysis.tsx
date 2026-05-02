/**
 * SimulationAnalysis Component
 * LLM-powered deep content analysis of simulation logs
 */
import { useState, useEffect } from 'react';
import { analyzeSimulation } from '../../utils/api';
import type { LLMSettings } from '../../types/simulation';

interface SimulationAnalysisProps {
  simulationId: string | null;
  logFilename: string | null;
  llmSettings?: LLMSettings;
}

export default function SimulationAnalysis({ simulationId: propSimulationId, logFilename, llmSettings }: SimulationAnalysisProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Derive simulation ID from filename if not provided
  const extractSimulationId = (filename: string): string | null => {
    // Extract timestamp from filename like "20260109_224705_Simulation_Name.html"
    const match = filename.match(/^(\d{8}_\d{6})_/);
    return match ? match[1] : null;
  };

  const simulationId = propSimulationId || (logFilename ? extractSimulationId(logFilename) : null);

  // Reset analysis state when simulation changes
  useEffect(() => {
    setAnalysis(null);
    setError(null);
    setAnalyzing(false);
  }, [propSimulationId, logFilename]);

  const handleAnalyze = async () => {
    if (!simulationId) {
      setError('No simulation ID available');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await analyzeSimulation(simulationId, llmSettings);
      setAnalysis(result.analysis);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze simulation');
    } finally {
      setAnalyzing(false);
    }
  };

  if (!simulationId) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900">No Simulation Loaded</h3>
        <p className="mt-2 text-sm text-gray-500">
          Load a simulation log to view LLM-powered analysis
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analyze Button */}
      {!analysis && !analyzing && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">LLM-Powered Simulation Analysis</h3>
            <p className="mt-2 text-sm text-gray-500 mb-6">
              Generate comprehensive analysis including executive summary, per-agent goal attainment, psychological component effects, emergent dynamics, and research recommendations
            </p>
            <button
              onClick={handleAnalyze}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Analyze Simulation
            </button>
            <p className="mt-3 text-xs text-gray-400">
              This may take several minutes depending on simulation complexity
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {analyzing && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="flex flex-col items-center justify-center">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500"></div>
              <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-t-2 border-b-2 border-purple-300 animate-pulse"></div>
            </div>
            <h3 className="mt-6 text-lg font-medium text-gray-900">Analyzing Simulation...</h3>
            <p className="mt-2 text-sm text-gray-500 text-center max-w-md">
              Using LLM to generate comprehensive analysis. This includes parsing the simulation log, extracting events, analyzing team effectiveness, and generating recommendations.
            </p>
            <div className="mt-6 flex items-center space-x-4 text-xs text-gray-400">
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                3-5 minutes typical
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                AI-powered
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
              <button
                onClick={handleAnalyze}
                className="mt-3 text-sm font-medium text-red-800 hover:text-red-700 underline"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Action Bar */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Analysis Report</h2>
            <button
              onClick={() => {
                setAnalysis(null);
                setError(null);
              }}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Re-analyze
            </button>
          </div>

          {/* Executive Summary */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <svg className="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Executive Summary
              </h3>
            </div>
            <div className="px-6 py-4">
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                {analysis.executive_summary}
              </p>
            </div>
          </div>

          {/* Timeline */}
          {analysis.timeline && analysis.timeline.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Timeline of Events
                </h3>
              </div>
              <div className="px-6 py-4 space-y-4 max-h-96 overflow-y-auto">
                {analysis.timeline.slice(0, 15).map((event: any) => (
                  <div key={event.step} className="flex items-start">
                    <div className="flex-shrink-0 w-16 text-sm font-medium text-blue-600">
                      Step {event.step}
                    </div>
                    <div className="flex-1 text-sm text-gray-700">{event.summary}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Team Effectiveness */}
          {analysis.team_effectiveness && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Agent Analysis
                </h3>
              </div>
              <div className="px-6 py-4">
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                  {analysis.team_effectiveness.analysis}
                </div>
              </div>
            </div>
          )}

          {/* Insights */}
          {analysis.insights && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  Key Insights
                </h3>
              </div>
              <div className="px-6 py-4">
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                  {analysis.insights.analysis}
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analysis.recommendations && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806l3.826 1.416a.75.75 0 00.998-.199l2.936-2.936c.24-.24.24-.24-.63 0-.874l.707-.707a.75.75 0 011.06 0l.707.707c.24.24.24.24.63 0 .874l-.707.707a.75.75 0 01-1.06 0l-.707-.707a.75.75 0 00-.874 0l-1.8 1.8a.75.75 0 01-.874 0l-1.17-1.17a.75.75 0 00-.874 0l-.707.707a.75.75 0 01-1.06 0l-.707-.707a.75.75 0 010 1.06l.707.707a.75.75 0 001.06 0l.707.707a.75.75 0 00.874 0l1.17-1.17a.75.75 0 01.874 0l1.8-1.8a.75.75 0 01.874 0l.707-.707c.24-.24.24-.63 0-.874l-.707-.707a.75.75 0 00-1.06 0l-.707.707a.75.75 0 01-1.06 0l-.707.707a.75.75 0 010 1.06l.707.707c.24.24.24.63 0 .874 0l.707-.707a.75.75 0 01.874 0l1.8 1.8a.75.75 0 01.874 0l1.17 1.17a.75.75 0 01-.874.874l-.707.707a.75.75 0 00-1.06 0l-.707-.707a.75.75 0 00-.874 0l-1.8-1.8a.75.75 0 01-.874 0l-.707-.707c-.24-.24-.63-.24-.874 0l-.707.707a.75.75 0 01-1.06 0l-.707.707c-.24-.24-.24-.63 0-.874.707-.707a.75.75 0 010 1.06l.707.707a.75.75 0 01.874 0l1.8 1.8a.75.75 0 01.874 0l1.17-1.17a.75.75 0 01-.874.874l-.707.707a.75.75 0 00-1.06 0l-.707-.707a.75.75 0 00-.874 0l-1.8-1.8a.75.75 0 01-.874 0l-.707-.707z" />
                  </svg>
                  Recommendations
                </h3>
              </div>
              <div className="px-6 py-4">
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                  {analysis.recommendations.recommendations}
                </div>
              </div>
            </div>
          )}

          {/* Metadata */}
          {analysis.metadata && (
            <div className="bg-gray-50 rounded-lg p-4 text-xs text-gray-500">
              <div className="flex items-center justify-between">
                <span>Analyzed: {analysis.analysis_date}</span>
                <span>Simulation ID: {simulationId}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
