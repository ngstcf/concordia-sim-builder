/**
 * NaturalLanguageSummary Component
 * Displays AI-generated natural language summary of simulation results
 */
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
  gm_prefab?: string;
  agent_details?: Record<string, {
    actions: Array<{ step: number; text: string }>;
    observations?: Array<{ step: number; text: string }>;
    goal: string;
    memories: string[];
  }>;
  has_grounded_variables?: boolean;
  grounded_variables?: Array<{
    name: string;
    type: string;
    description: string;
    current_value: any;
    history: Array<{ step: number; value: any }>;
  }>;
}

interface NaturalLanguageSummaryProps {
  filename: string | null;
  htmlContent: string | null;
}

const markdownComponents = {
  h1: ({ children, ...props }: any) => <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-3 pb-2 border-b border-gray-200" {...props}>{children}</h1>,
  h2: ({ children, ...props }: any) => <h2 className="text-xl font-bold text-gray-900 mt-5 mb-2" {...props}>{children}</h2>,
  h3: ({ children, ...props }: any) => <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props}>{children}</h3>,
  h4: ({ children, ...props }: any) => <h4 className="text-base font-semibold text-gray-800 mt-3 mb-1" {...props}>{children}</h4>,
  p: ({ children, ...props }: any) => <p className="text-sm text-gray-700 leading-relaxed my-2" {...props}>{children}</p>,
  ul: ({ children, ...props }: any) => <ul className="list-disc list-outside ml-5 space-y-1 my-2" {...props}>{children}</ul>,
  ol: ({ children, ...props }: any) => <ol className="list-decimal list-outside ml-5 space-y-1 my-2" {...props}>{children}</ol>,
  li: ({ children, ...props }: any) => <li className="text-sm text-gray-700 leading-relaxed" {...props}>{children}</li>,
  strong: ({ children, ...props }: any) => <strong className="font-semibold text-gray-900" {...props}>{children}</strong>,
  em: ({ children, ...props }: any) => <em className="italic text-gray-600" {...props}>{children}</em>,
  hr: (props: any) => <hr className="my-4 border-gray-200" {...props} />,
  table: ({ children, ...props }: any) => (
    <div className="overflow-x-auto my-4">
      <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg text-sm" {...props}>{children}</table>
    </div>
  ),
  thead: ({ children, ...props }: any) => <thead className="bg-gray-50" {...props}>{children}</thead>,
  th: ({ children, ...props }: any) => <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200" {...props}>{children}</th>,
  td: ({ children, ...props }: any) => <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100" {...props}>{children}</td>,
  tr: ({ children, ...props }: any) => <tr className="hover:bg-gray-50" {...props}>{children}</tr>,
};

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

    const totalActions = Object.values(analytics.agent_actions).reduce((sum, count) => sum + count, 0);
    const mostActiveAgent = Object.entries(analytics.agent_actions).sort((a, b) => b[1] - a[1])[0];
    const leastActiveAgent = Object.entries(analytics.agent_actions).sort((a, b) => a[1] - b[1])[0];
    const avgActionsPerAgent = analytics.agents.length > 0 ? totalActions / analytics.agents.length : 0;
    const avgObservationsPerStep = analytics.total_steps > 0 ? analytics.total_observations / analytics.total_steps : 0;

    let md = `# Simulation Summary\n\n`;

    if (analytics.premise) {
      md += `## Premise\n\n${analytics.premise}\n\n`;
    }

    // Overview
    md += `## Overview\n\n`;
    md += `This simulation involved **${analytics.agents.length} agent${analytics.agents.length !== 1 ? 's' : ''}** `;
    md += `progressing through **${analytics.total_steps} step${analytics.total_steps !== 1 ? 's' : ''}** `;
    md += `of interaction, generating **${analytics.word_count.toLocaleString()} words** of narrative content.\n\n`;

    // Agent summary table
    if (analytics.agents.length > 0) {
      md += `## Agent Overview\n\n`;
      md += `| Agent | Actions | Share | Engagement |\n`;
      md += `|-------|---------|-------|------------|\n`;
      analytics.agents.forEach((agent) => {
        const actionCount = analytics.agent_actions[agent] || 0;
        const percentage = totalActions > 0 ? ((actionCount / totalActions) * 100).toFixed(0) : '0';
        const engagement = actionCount > 5 ? 'High' : actionCount > 2 ? 'Moderate' : actionCount > 0 ? 'Low' : 'None';
        md += `| ${agent} | ${actionCount} | ${percentage}% | ${engagement} |\n`;
      });
      md += `\n`;

      if (analytics.agents.length > 1 && mostActiveAgent && leastActiveAgent && mostActiveAgent[0] !== leastActiveAgent[0]) {
        const gap = mostActiveAgent[1] - leastActiveAgent[1];
        if (gap > 2) {
          md += `> **Participation imbalance detected:** ${mostActiveAgent[0]} took ${mostActiveAgent[1]} actions while ${leastActiveAgent[0]} took only ${leastActiveAgent[1]}. `;
          md += `This ${gap > 5 ? 'significant' : 'moderate'} gap may indicate turn-taking issues or one agent dominating the interaction.\n\n`;
        }
      }
    }

    // Agent Goals & Outcomes
    if (analytics.agent_details && Object.keys(analytics.agent_details).length > 0) {
      md += `## Agent Goals & Outcomes\n\n`;

      analytics.agents.forEach((agent) => {
        const details = analytics.agent_details?.[agent];
        if (!details) return;

        const actionCount = analytics.agent_actions[agent] || 0;

        md += `### ${agent}\n\n`;

        if (details.goal) {
          md += `**Goal:** ${details.goal}\n\n`;
        } else {
          md += `**Goal:** Not explicitly stated\n\n`;
        }

        const goalProgress = analyzeGoalProgress(details, actionCount, analytics.total_steps);
        md += `**Goal Progress:** ${goalProgress}\n\n`;

        if (details.actions.length > 0) {
          md += `**Key Actions:**\n`;
          details.actions.slice(0, 3).forEach((action) => {
            const stepPrefix = action.step !== null ? `[Step ${action.step}] ` : '';
            const text = action.text.length > 120 ? action.text.substring(0, 120) + '...' : action.text;
            md += `- ${stepPrefix}${text}\n`;
          });
          if (details.actions.length > 3) {
            md += `- *...and ${details.actions.length - 3} more action${details.actions.length - 3 > 1 ? 's' : ''}*\n`;
          }
          md += `\n`;
        }

        const obs = details.observations || [];
        if (obs.length > 0) {
          md += `**Key Observations:**\n`;
          obs.slice(0, 2).forEach((o) => {
            const text = o.text.length > 150 ? o.text.substring(0, 150) + '...' : o.text;
            md += `- [Step ${o.step}] ${text}\n`;
          });
          if (obs.length > 2) {
            md += `- *...and ${obs.length - 2} more observation${obs.length - 2 > 1 ? 's' : ''}*\n`;
          }
          md += `\n`;
        }
      });
    }

    // Grounded Variables Summary
    const gvars = analytics.grounded_variables || [];
    if (gvars.length > 0) {
      md += `## Grounded Variables\n\n`;
      md += `| Variable | Type | Initial | Final | Changes |\n`;
      md += `|----------|------|---------|-------|--------|\n`;
      gvars.forEach((v) => {
        const history = v.history || [];
        const initial = history.length > 0 ? history[0].value : v.current_value ?? '—';
        const final_ = history.length > 0 ? history[history.length - 1].value : v.current_value ?? '—';
        let changeCount = 0;
        for (let i = 1; i < history.length; i++) {
          if (history[i].value !== history[i - 1].value) changeCount++;
        }
        md += `| ${v.name} | ${v.type} | ${initial} | ${final_} | ${changeCount} |\n`;
      });
      md += `\n`;

      const unchangedVars = gvars.filter((v) => {
        const h = v.history || [];
        return h.length <= 1 || h.every((e) => e.value === h[0].value);
      });
      if (unchangedVars.length > 0 && unchangedVars.length < gvars.length) {
        md += `> **Note:** ${unchangedVars.map((v) => v.name).join(', ')} did not change during the simulation. This may indicate the GM did not narrate events affecting ${unchangedVars.length === 1 ? 'this variable' : 'these variables'}.\n\n`;
      } else if (unchangedVars.length === gvars.length) {
        md += `> **Warning:** No grounded variables changed during the simulation. The GM may not be outputting variable update tags. Check the Grounded Variables tab for details.\n\n`;
      }
    }

    // Cooperation Profile (game-theoretic simulations)
    if (analytics.gm_prefab === 'game_theoretic_and_dramaturgic__GameMaster' && analytics.agent_details) {
      const coopData: Array<{ agent: string; cooperate: number; defect: number; other: number; total: number }> = [];
      analytics.agents.forEach((agent) => {
        const details = analytics.agent_details?.[agent];
        if (!details) return;
        let cooperate = 0, defect = 0, other = 0;
        details.actions.forEach((a) => {
          const upper = a.text.toUpperCase().trim();
          if (upper === 'COOPERATE') cooperate++;
          else if (upper === 'DEFECT') defect++;
          else other++;
        });
        if (cooperate + defect > 0) {
          coopData.push({ agent, cooperate, defect, other, total: cooperate + defect + other });
        }
      });

      if (coopData.length > 0) {
        md += `## Cooperation Profile\n\n`;
        md += `| Agent | Cooperate | Defect | Cooperation Rate |\n`;
        md += `|-------|-----------|--------|------------------|\n`;
        coopData.forEach((d) => {
          const rate = d.cooperate + d.defect > 0
            ? ((d.cooperate / (d.cooperate + d.defect)) * 100).toFixed(0)
            : '—';
          md += `| ${d.agent} | ${d.cooperate} | ${d.defect} | ${rate}% |\n`;
        });
        md += `\n`;

        const totalCoop = coopData.reduce((s, d) => s + d.cooperate, 0);
        const totalDef = coopData.reduce((s, d) => s + d.defect, 0);
        const overallRate = totalCoop + totalDef > 0 ? (totalCoop / (totalCoop + totalDef)) * 100 : 0;

        if (overallRate > 75) {
          md += `> Agents showed **high cooperation** (${overallRate.toFixed(0)}% overall). This suggests mutual trust or strong incentives for cooperation.\n\n`;
        } else if (overallRate > 40) {
          md += `> **Mixed strategies** observed (${overallRate.toFixed(0)}% cooperation). Agents varied between cooperation and defection, typical of iterated games with uncertain trust.\n\n`;
        } else {
          md += `> Agents showed **low cooperation** (${overallRate.toFixed(0)}% overall). Defection dominated, which may indicate insufficient incentives for mutual cooperation or breakdown of trust.\n\n`;
        }
      }
    }

    // Activity Metrics
    md += `## Activity Metrics\n\n`;
    md += `| Metric | Value |\n`;
    md += `|--------|-------|\n`;
    md += `| Total Actions | ${totalActions} |\n`;
    md += `| Avg Actions per Agent | ${avgActionsPerAgent.toFixed(1)} |\n`;
    md += `| Total Observations | ${analytics.total_observations} |\n`;
    md += `| Avg Observations per Step | ${avgObservationsPerStep.toFixed(1)} |\n`;
    md += `| Words Generated | ${analytics.word_count.toLocaleString()} |\n`;
    md += `| Words per Step | ${analytics.total_steps > 0 ? (analytics.word_count / analytics.total_steps).toFixed(0) : 0} |\n`;
    md += `\n`;

    // Timeline Highlights
    if (analytics.timeline.length > 0) {
      md += `## Timeline Highlights\n\n`;

      const phaseSize = Math.max(1, Math.ceil(analytics.total_steps / 3));
      const phases = [
        { name: 'Opening', events: analytics.timeline.filter(e => e.step <= phaseSize) },
        { name: 'Development', events: analytics.timeline.filter(e => e.step > phaseSize && e.step <= phaseSize * 2) },
        { name: 'Resolution', events: analytics.timeline.filter(e => e.step > phaseSize * 2) }
      ];

      phases.forEach(phase => {
        if (phase.events.length > 0) {
          md += `### ${phase.name} (Steps ${phase.events[0].step}-${phase.events[phase.events.length - 1].step})\n\n`;
          phase.events.slice(0, 3).forEach(event => {
            const desc = event.description.length > 150 ? event.description.substring(0, 150) + '...' : event.description;
            md += `- **Step ${event.step}:** ${desc}\n`;
          });
          if (phase.events.length > 3) {
            md += `- *...${phase.events.length - 3} more events*\n`;
          }
          md += `\n`;
        }
      });
    }

    // Simulation Profile
    md += `## Simulation Profile\n\n`;

    if (analytics.agents.length === 1) {
      md += `**Type:** Single-agent simulation focusing on individual decision-making.\n\n`;
    } else if (analytics.agents.length === 2) {
      md += `**Type:** Dyadic interaction, typically used to study dialogue, negotiation, or social exchange.\n\n`;
    } else {
      md += `**Type:** Multi-agent simulation (${analytics.agents.length} agents) involving group dynamics and collective behavior.\n\n`;
    }

    const complexity = analytics.total_steps > 15 ? 'High' : analytics.total_steps > 8 ? 'Medium' : 'Low';
    md += `**Complexity:** ${complexity} (${analytics.total_steps} steps)\n\n`;

    // Improvement suggestions
    md += `## Suggestions for Improvement\n\n`;

    const suggestions: string[] = [];

    if (analytics.total_steps <= 6) {
      suggestions.push(`**Extend simulation length.** At ${analytics.total_steps} steps, agents may not have enough time to fully pursue their goals. Consider 12-15 steps for richer interactions.`);
    }

    if (mostActiveAgent && leastActiveAgent && mostActiveAgent[1] > leastActiveAgent[1] * 3) {
      suggestions.push(`**Address participation imbalance.** ${leastActiveAgent[0]} was significantly less active than ${mostActiveAgent[0]}. Consider adjusting the Game Master's acting order or adding turn-taking prompts.`);
    }

    if (analytics.agent_details) {
      const agentsWithoutGoals = analytics.agents.filter(a => !analytics.agent_details?.[a]?.goal);
      if (agentsWithoutGoals.length > 0) {
        suggestions.push(`**Add explicit goals** for ${agentsWithoutGoals.join(', ')}. Agents without goals tend to drift into generic conversation rather than purposeful action.`);
      }
    }

    if (totalActions < analytics.agents.length * 2) {
      suggestions.push(`**Low action rate detected.** Consider adding goal-anchoring memories to agents to increase goal-directed behavior.`);
    }

    suggestions.push(`**Use the Analysis tab** for LLM-powered deep analysis including goal attainment assessment, emergent dynamics, and research recommendations.`);

    suggestions.forEach((s, i) => {
      md += `${i + 1}. ${s}\n`;
    });

    setSummary(md);
  };

  const analyzeGoalProgress = (details: any, actionCount: number, totalSteps: number): string => {
    const hasGoal = details.goal && details.goal.length > 0;
    const hasActions = details.actions.length > 0;
    const completionRatio = totalSteps > 0 ? actionCount / totalSteps : 0;

    if (!hasGoal) return 'Unable to assess (no explicit goal stated)';
    if (!hasActions) return 'No progress (no actions taken)';

    if (completionRatio > 0.7 && actionCount >= 5) {
      return 'Strong engagement -- agent was highly active throughout';
    } else if (completionRatio > 0.4 && actionCount >= 3) {
      return 'Moderate engagement -- participated regularly';
    } else if (actionCount >= 1) {
      return 'Limited engagement -- sporadic participation';
    }
    return 'Minimal activity';
  };

  const handleSaveToFile = () => {
    if (!summary) return;
    const blob = new Blob([summary], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    a.download = `simulation_summary_${timestamp}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (analytics && htmlContent) {
      generateSummary();
    }
  }, [analytics]);

  if (!filename || !htmlContent) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Natural Language Summary</h3>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">
            Load a simulation to see a summary
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
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <button
              onClick={handleSaveToFile}
              className="inline-flex items-center text-sm text-gray-600 hover:text-gray-800 font-medium"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Save
            </button>
            <button
              onClick={() => {
                setSummary(null);
                generateSummary();
              }}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium whitespace-nowrap"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="p-5 max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
          {summary}
        </ReactMarkdown>
      </div>
    </div>
  );
}
