/**
 * AgentProbeChart Component
 * Displays the per-agent probe: the share of the roster choosing each option,
 * administration by administration, with the integrity record that says how
 * much of the roster actually answered.
 *
 * Deliberately lines rather than a stacked area. When responses are dropped the
 * shares no longer sum to 100, and a stacked area would close that gap
 * silently; separate lines leave the shortfall visible, which is the whole
 * reason the probe records a denominator.
 */
import { useState, useEffect } from 'react';
import { getSimulationAnalytics } from '../../utils/api';
import type { SimulationAnalytics } from '../../utils/api';
import type { ProbeAdministration } from '../../types/simulation';

interface AgentProbeChartProps {
  filename: string | null;
}

// Same order as GroundedVariablesChart, so an option and a variable of the same
// rank read as the same color across the two tabs.
const COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#84CC16', // lime
];

const Panel = ({ children }: { children: React.ReactNode }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Probe</h3>
    {children}
  </div>
);

export default function AgentProbeChart({ filename }: AgentProbeChartProps) {
  const [analytics, setAnalytics] = useState<SimulationAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  useEffect(() => {
    if (!filename) {
      setAnalytics(null);
      setSelectedItem(null);
      return;
    }
    loadAnalytics();
  }, [filename]);

  const loadAnalytics = async () => {
    if (!filename) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSimulationAnalytics(filename);
      setAnalytics(data);
      const items = Object.keys(data.agent_probe?.series || {});
      setSelectedItem(items[0] ?? null);
    } catch (err: any) {
      console.error('Error loading agent probe:', err);
      setError(err.message || 'Failed to load agent probe results');
    } finally {
      setLoading(false);
    }
  };

  if (!filename) {
    return (
      <Panel>
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">Load a simulation to see probe results</p>
        </div>
      </Panel>
    );
  }

  if (loading) {
    return (
      <Panel>
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-teal-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-3 text-sm text-gray-600">Loading probe results...</span>
        </div>
      </Panel>
    );
  }

  if (error) {
    return (
      <Panel>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <p className="text-sm text-red-800">{error}</p>
          <button onClick={loadAnalytics} className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            Retry
          </button>
        </div>
      </Panel>
    );
  }

  const probe = analytics?.agent_probe;
  const series = probe?.series || {};
  const items = Object.keys(series);

  if (!probe || items.length === 0) {
    return (
      <Panel>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-4 text-sm text-gray-500">This simulation carries no probe results</p>
          <p className="text-xs text-gray-400 mt-2">
            Add an Agent Probe in the Game Master configuration to survey every agent
            directly on a set cadence, instead of relying on the narrator's estimate.
          </p>
        </div>
      </Panel>
    );
  }

  const integrity = probe.integrity;
  const active = selectedItem && series[selectedItem] ? selectedItem : items[0];
  const administrations: ProbeAdministration[] = series[active] || [];

  // Union across administrations rather than the first one: an option nobody
  // picks at the start still needs its own line once somebody does.
  const options = Array.from(
    administrations.reduce((set, a) => {
      Object.keys(a.shares || {}).forEach(o => set.add(o));
      return set;
    }, new Set<string>())
  );

  const itemIntegrity = integrity?.per_item?.[active];
  const population = integrity?.population ?? 0;
  // A shortfall anywhere means the denominator moved during the run, which
  // changes what the series is a measurement of.
  const incomplete = itemIntegrity ? itemIntegrity.min_responding < population : false;
  const last = administrations[administrations.length - 1];

  const xFor = (i: number) =>
    administrations.length > 1 ? (i / (administrations.length - 1)) * 100 : 50;

  // Plain numbers, not percentages: the points attribute takes user-space
  // coordinates only, so the polylines below live in a 0-100 viewBox.
  const pointsFor = (option: string) =>
    administrations
      .map((a, i) => `${xFor(i)},${100 - (a.shares?.[option] ?? 0)}`)
      .join(' ');

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">Agent Probe</h3>
          </div>
          <span className="text-sm text-gray-500">
            {integrity?.administrations ?? administrations.length} administrations
            {' · '}{population} agents
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Every agent answered these items directly, so each point is a tally over the
          roster rather than an estimate about it.
        </p>
      </div>

      <div className="p-5">
        {/* Integrity strip. Reported before the chart because a series measured
            on a shrinking denominator should be read differently, and by the
            time the reader is looking at the lines it is too late to say so. */}
        <div className="mb-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Population', value: population },
            { label: 'Administrations', value: integrity?.administrations ?? administrations.length },
            {
              label: 'Responding',
              value: itemIntegrity
                ? itemIntegrity.min_responding === itemIntegrity.max_responding
                  ? `${itemIntegrity.max_responding} of ${population}`
                  : `${itemIntegrity.min_responding}-${itemIntegrity.max_responding} of ${population}`
                : '-',
              warn: incomplete,
            },
            { label: 'Dropped responses', value: integrity?.failures ?? 0, warn: (integrity?.failures ?? 0) > 0 },
          ].map(stat => (
            <div
              key={stat.label}
              className={`rounded-lg p-3 border ${
                stat.warn ? 'bg-amber-50 border-amber-200' : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="text-xs text-gray-500">{stat.label}</div>
              <div className={`text-lg font-semibold ${stat.warn ? 'text-amber-800' : 'text-gray-900'}`}>
                {stat.value}
              </div>
            </div>
          ))}
        </div>

        {incomplete && (
          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-3">
            <p className="text-xs text-amber-800">
              At least one administration reached fewer than {population} agents. The shares
              below are over the agents who answered, so they will not sum to 100 where
              responses were dropped. Treat this as a partial measurement rather than a
              population shift.
            </p>
          </div>
        )}

        {/* Item selector */}
        {items.length > 1 && (
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Item:</label>
            <div className="flex flex-wrap gap-2">
              {items.map(item => (
                <button
                  key={item}
                  onClick={() => setSelectedItem(item)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    item === active
                      ? 'bg-teal-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chart */}
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="relative h-64 mb-4">
            {/* Spans the full plot height, not h-64 minus the x-axis strip: the
                labels have to sit on the gridlines they name. */}
            <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-500 -my-2">
              <span>100%</span>
              <span>50%</span>
              <span>0%</span>
            </div>

            <div className="ml-14 h-full relative border-l border-b border-gray-300">
              <div className="absolute inset-0 flex flex-col justify-between">
                <div className="border-t border-gray-200 border-dashed"></div>
                <div className="border-t border-gray-200 border-dashed"></div>
                <div className="border-t border-gray-200"></div>
              </div>

              {/* Drawn in two passes. The lines need a stretched viewBox so their
                  coordinates can be plain numbers; the markers stay in
                  percentage space, where a circle is still a circle. */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                {options.map((option, index) => (
                  <polyline
                    key={option}
                    fill="none"
                    stroke={COLORS[index % COLORS.length]}
                    strokeWidth="2"
                    vectorEffect="non-scaling-stroke"
                    points={pointsFor(option)}
                  />
                ))}
              </svg>

              <svg className="absolute inset-0 w-full h-full" style={{ overflow: 'visible' }}>
                {options.map((option, index) =>
                  administrations.map((a, i) => {
                    const share = a.shares?.[option] ?? 0;
                    return (
                      <circle
                        key={`${option}-${i}`}
                        cx={`${xFor(i)}%`}
                        cy={`${100 - share}%`}
                        r="3"
                        fill={COLORS[index % COLORS.length]}
                      >
                        <title>
                          {option}: {share.toFixed(1)}% ({a.counts?.[option] ?? 0} of {a.n_responding})
                          {'\n'}Administration {i + 1}, GM event {a.event_index}
                        </title>
                      </circle>
                    );
                  })
                )}
              </svg>

              <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-gray-500">
                <span>Administration 1</span>
                <span>{administrations.length}</span>
              </div>
            </div>
          </div>

          {/* Legend. Always present, so identity is never carried by color alone. */}
          <div className="flex flex-wrap gap-4 mt-8 pt-4 border-t border-gray-200">
            {options.map((option, index) => (
              <div key={option} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                <span className="text-sm text-gray-700">{option}</span>
                {last && (
                  <span className="text-xs text-gray-500">
                    ({(last.shares?.[option] ?? 0).toFixed(1)}% at the end)
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* The same numbers as text, so the chart is not the only way to read them. */}
        {last && (
          <div className="mt-6">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Final administration (GM event {last.event_index})
            </h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Option</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Agents</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Share</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {options.map(option => (
                    <tr key={option}>
                      <td className="px-4 py-2 text-sm font-medium text-gray-900">{option}</td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {last.counts?.[option] ?? 0} of {last.n_responding}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {(last.shares?.[option] ?? 0).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {probe.failures.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Dropped responses ({probe.failures.length})
            </h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {probe.failures.map((f, i) => (
                <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                  <span className="text-sm text-amber-900 font-medium">{f.item}</span>
                  <span className="ml-2 text-xs text-amber-700">GM event {f.event_index}</span>
                  <div className="text-xs text-amber-800 mt-0.5">{f.reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
