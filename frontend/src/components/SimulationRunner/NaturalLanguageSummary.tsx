/**
 * NaturalLanguageSummary Component
 * Displays AI-generated natural language summary of simulation results
 */
import { useState, useEffect } from 'react';
import type { JSX } from 'react';
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
  premise?: string;
  agent_details?: Record<string, {
    actions: Array<{ step: number; action: string; goal?: string }>;
    goal: string;
    memories: string[];
  }>;
}

interface NaturalLanguageSummaryProps {
  filename: string | null;
  htmlContent: string | null;
}

export default function NaturalLanguageSummary({ filename, htmlContent }: NaturalLanguageSummaryProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);

  useEffect(() => {
    if (filename && htmlContent) {
      loadAnalytics();
    } else {
      setAnalytics(null);
      setSummary(null);
    }
  }, [filename, htmlContent]);

  const loadAnalytics = async () => {
    if (!filename) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);
    } catch (err: any) {
      console.error('Error loading analytics for summary:', err);
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = () => {
    if (!analytics || !htmlContent) return;

    // Extract key information for summary
    const totalActions = Object.values(analytics.agent_actions).reduce((sum, count) => sum + count, 0);
    const mostActiveAgent = Object.entries(analytics.agent_actions).sort((a, b) => b[1] - a[1])[0];
    const avgActionsPerAgent = analytics.agents.length > 0 ? totalActions / analytics.agents.length : 0;
    const avgObservationsPerStep = analytics.total_steps > 0 ? analytics.total_observations / analytics.total_steps : 0;

    // Build natural language summary
    let summaryText = `# Simulation Summary\n\n`;

    // Premise
    if (analytics.premise) {
      summaryText += `## Premise\n\n`;
      summaryText += `${analytics.premise}\n\n`;
    }

    // Overview
    summaryText += `## Overview\n\n`;
    summaryText += `This simulation involved **${analytics.agents.length} agent${analytics.agents.length !== 1 ? 's' : ''}** `;
    summaryText += `progressing through **${analytics.total_steps} step${analytics.total_steps !== 1 ? 's' : ''}** `;
    summaryText += `of interaction. The simulation generated **${analytics.word_count.toLocaleString()} words** `;
    summaryText += `of detailed narrative content.\n\n`;

    // Agent Goal Analysis (NEW)
    if (analytics.agent_details && Object.keys(analytics.agent_details).length > 0) {
      summaryText += `## Agent Goals & Outcomes\n\n`;

      analytics.agents.forEach((agent) => {
        const details = analytics.agent_details?.[agent];
        if (!details) return;

        const actionCount = analytics.agent_actions[agent] || 0;

        summaryText += `### ${agent}\n\n`;

        // Goal
        if (details.goal) {
          summaryText += `**Goal**: ${details.goal}\n\n`;
        } else {
          summaryText += `**Goal**: Not explicitly stated\n\n`;
        }

        // Goal Achievement Analysis
        const engagementLevel = actionCount > 5 ? 'High' : actionCount > 2 ? 'Moderate' : 'Low';
        const goalProgress = analyzeGoalProgress(details, actionCount, analytics.total_steps);

        summaryText += `**Engagement**: ${engagementLevel} (${actionCount} actions taken)\n\n`;
        summaryText += `**Goal Progress**: ${goalProgress}\n\n`;

        // Key Actions
        if (details.actions.length > 0) {
          summaryText += `**Key Actions**:\n`;
          details.actions.slice(0, 3).forEach((action) => {
            const stepPrefix = action.step !== null ? `[Step ${action.step}] ` : '';
            summaryText += `- ${stepPrefix}${action.action.substring(0, 80)}...\n`;
          });
          if (details.actions.length > 3) {
            summaryText += `- *...and ${details.actions.length - 3} more action${details.actions.length - 3 > 1 ? 's' : ''}*\n`;
          }
          summaryText += `\n`;
        }
      });
    }

    // Agent Analysis (simplified - goals handled above)
    if (!analytics.agent_details || Object.keys(analytics.agent_details).length === 0) {
      summaryText += `## Agent Analysis\n\n`;
      summaryText += `The following agents participated in the simulation:\n\n`;
      analytics.agents.forEach((agent) => {
        const actionCount = analytics.agent_actions[agent] || 0;
        const percentage = totalActions > 0 ? ((actionCount / totalActions) * 100).toFixed(1) : '0.0';
        summaryText += `- **${agent}**: ${actionCount} actions (${percentage}% of total)\n`;
      });
      summaryText += `\n`;

      if (mostActiveAgent && mostActiveAgent[1] > 0) {
        summaryText += `**Most Active Agent**: ${mostActiveAgent[0]} with ${mostActiveAgent[1]} actions\n\n`;
      }
    }

    // Activity Metrics
    summaryText += `## Activity Metrics\n\n`;
    summaryText += `- **Total Actions**: ${totalActions} (deliberate choices made by agents)\n`;
    summaryText += `- **Average Actions per Agent**: ${avgActionsPerAgent.toFixed(1)}\n`;
    summaryText += `- **Total Observations**: ${analytics.total_observations} (what agents perceived)\n`;
    summaryText += `- **Average Observations per Step**: ${avgObservationsPerStep.toFixed(1)}\n`;
    summaryText += `- **Simulation Complexity**: ${analytics.total_steps > 10 ? 'High' : analytics.total_steps > 5 ? 'Medium' : 'Low'}\n\n`;
    summaryText += `*Note: Observations represent what each agent perceives about their environment, including the actions and statements of other agents. These observations inform each agent's subsequent decisions.*\n\n`;

    // Timeline Summary
    if (analytics.timeline.length > 0) {
      summaryText += `## Timeline Highlights\n\n`;
      summaryText += `The simulation progressed through several key phases:\n\n`;

      // Group timeline events by phase
      const phaseSize = Math.max(1, Math.ceil(analytics.total_steps / 3));
      const phases = [
        { name: 'Early Phase', events: analytics.timeline.filter(e => e.step <= phaseSize) },
        { name: 'Middle Phase', events: analytics.timeline.filter(e => e.step > phaseSize && e.step <= phaseSize * 2) },
        { name: 'Late Phase', events: analytics.timeline.filter(e => e.step > phaseSize * 2) }
      ];

      phases.forEach(phase => {
        if (phase.events.length > 0) {
          summaryText += `### ${phase.name}\n`;
          summaryText += `${phase.events.length} event${phase.events.length !== 1 ? 's' : ''} occurred during this phase.\n\n`;
          // Show first event as example
          if (phase.events[0]) {
            summaryText += `*Example: "${phase.events[0].description.substring(0, 100)}..."\n\n`;
          }
        }
      });
    }

    // Content Analysis
    summaryText += `## Content Analysis\n\n`;
    summaryText += `The simulation contains:\n`;
    summaryText += `- **${analytics.word_count.toLocaleString()} words** of narrative content\n`;
    summaryText += `- **${analytics.character_count.toLocaleString()} characters** total\n`;
    summaryText += `- Average word density: ${analytics.total_steps > 0 ? (analytics.word_count / analytics.total_steps).toFixed(0) : 0} words per step\n\n`;

    // Interpretation
    summaryText += `## Interpretation\n\n`;

    if (analytics.agents.length === 1) {
      summaryText += `This is a **single-agent simulation** focusing on individual decision-making and behavior patterns. `;
    } else if (analytics.agents.length === 2) {
      summaryText += `This is a **dyadic interaction** between two agents, typically used to study dialogue, negotiation, or social exchange. `;
    } else {
      summaryText += `This is a **multi-agent simulation** involving group dynamics, social interactions, and collective behavior. `;
    }

    if (analytics.total_steps > 15) {
      summaryText += `The simulation ran for a relatively long duration (${analytics.total_steps} steps), allowing for complex narrative development and character evolution.`;
    } else if (analytics.total_steps > 8) {
      summaryText += `The simulation had moderate length (${analytics.total_steps} steps), providing enough space for meaningful interaction while maintaining focus.`;
    } else {
      summaryText += `The simulation was concise (${analytics.total_steps} steps), focusing on a specific interaction or scenario.`;
    }

    summaryText += `\n\n`;

    // Suggestions
    summaryText += `## Analysis Suggestions\n\n`;
    summaryText += `For deeper analysis, consider:\n\n`;
    summaryText += `1. **Agent Behavior Patterns**: Review individual agent logs to identify behavioral consistencies and changes\n`;
    summaryText += `2. **Goal Achievement**: Use the Actions tab to see detailed agent actions and assess goal completion\n`;
    summaryText += `3. **Interaction Networks**: Map how agents influence each other's decisions over time\n`;
    summaryText += `4. **Temporal Dynamics**: Analyze how the simulation evolves across different phases\n`;
    summaryText += `5. **Comparative Analysis**: Compare this simulation with others using similar configurations\n`;

    setSummary(summaryText);
  };

  // Helper function to analyze goal progress
  const analyzeGoalProgress = (details: any, actionCount: number, totalSteps: number): string => {
    const hasGoal = details.goal && details.goal.length > 0;
    const hasActions = details.actions.length > 0;
    const completionRatio = totalSteps > 0 ? actionCount / totalSteps : 0;

    if (!hasGoal) {
      return 'Unable to assess (no explicit goal stated)';
    }

    if (!hasActions) {
      return 'No progress (no actions taken)';
    }

    // Analyze based on engagement and action patterns
    if (completionRatio > 0.7 && actionCount >= 5) {
      return 'Strong progress - Agent was highly active and engaged throughout the simulation';
    } else if (completionRatio > 0.4 && actionCount >= 3) {
      return 'Moderate progress - Agent participated regularly but may not have fully achieved goal';
    } else if (actionCount >= 1) {
      return 'Limited progress - Agent took some actions but engagement was sporadic';
    } else {
      return 'No visible progress - Agent was minimally active';
    }
  };

  // Regenerate summary when analytics changes
  useEffect(() => {
    if (analytics && htmlContent) {
      generateSummary();
    }
  }, [analytics]);

  const formatMarkdown = (text: string): JSX.Element => {
    // Simple markdown formatter
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    let currentList: string[] = [];

    const flushList = () => {
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="list-disc list-inside space-y-1 my-2">
            {currentList.map((item, i) => (
              <li key={i} className="text-gray-700">{item}</li>
            ))}
          </ul>
        );
        currentList = [];
      }
    };

    lines.forEach((line, index) => {
      // Headers
      if (line.startsWith('# ')) {
        flushList();
        elements.push(
          <h2 key={`h2-${index}`} className="text-xl font-bold text-gray-900 mt-6 mb-3">
            {line.substring(2)}
          </h2>
        );
      } else if (line.startsWith('## ')) {
        flushList();
        elements.push(
          <h3 key={`h3-${index}`} className="text-lg font-semibold text-gray-900 mt-5 mb-2">
            {line.substring(3)}
          </h3>
        );
      } else if (line.startsWith('### ')) {
        flushList();
        elements.push(
          <h4 key={`h4-${index}`} className="text-base font-semibold text-gray-900 mt-4 mb-2">
            {line.substring(4)}
          </h4>
        );
      }
      // List items
      else if (line.trim().startsWith('- ')) {
        const content = line.trim().substring(2);
        // Handle bold markdown
        const formattedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        currentList.push(formattedContent);
      }
      // Paragraphs
      else if (line.trim()) {
        flushList();
        const formattedLine = line
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>');
        elements.push(
          <p key={`p-${index}`} className="text-gray-700 my-2" dangerouslySetInnerHTML={{ __html: formattedLine }} />
        );
      } else {
        flushList();
      }
    });

    flushList();
    return <>{elements}</>;
  };

  if (!filename || !htmlContent) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Natural Language Summary</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see an AI-generated summary
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Natural Language Summary</h3>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Generating summary...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Natural Language Summary</h3>
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

  if (!summary) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Natural Language Summary</h3>
        </div>
        <button
          onClick={() => {
            setSummary(null);
            generateSummary();
          }}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="p-5 prose prose-sm max-w-none">
        {formatMarkdown(summary)}
      </div>
    </div>
  );
}
