/**
 * HealthStrip Component
 *
 * Failure observability for long-running work: polls /health for running
 * tasks (with time since last step progress) and the durable incident
 * journal, so the browser can answer "did anything fail?" even after
 * disconnects. Optional browser notifications on failures and stalls.
 */
import { useState, useEffect, useRef } from 'react';
import { getHealth } from '../../utils/api';
import type { HealthStatus, HealthIncident } from '../../utils/api';

const POLL_MS = 30_000;
const STALL_AMBER_S = 300;   // 5 min without step progress
const STALL_RED_S = 900;     // 15 min: notify
const ALERT_KINDS = ['run_failed', 'batch_run_failed', 'error', 'watchdog', 'content_filter'];

function notify(title: string, body: string) {
  if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
    try { new Notification(title, { body }); } catch { /* not fatal */ }
  }
}

function formatAge(seconds: number): string {
  if (seconds < 90) return `${seconds}s`;
  if (seconds < 5400) return `${Math.round(seconds / 60)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

export default function HealthStrip() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [showIncidents, setShowIncidents] = useState(false);
  const [alertsEnabled, setAlertsEnabled] = useState(
    typeof Notification !== 'undefined' && Notification.permission === 'granted'
  );
  // Dedup state: incidents already notified (by ts) and tasks already
  // flagged as stalled, so a 30s poll doesn't re-alert every cycle.
  const notifiedRef = useRef<{ lastIncidentTs: number; stalledTasks: Set<string> }>({
    lastIncidentTs: Date.now() / 1000,
    stalledTasks: new Set(),
  });

  useEffect(() => {
    let stopped = false;

    const poll = async () => {
      try {
        const h = await getHealth(50);
        if (stopped) return;
        setHealth(h);

        const seen = notifiedRef.current;
        for (const inc of h.incidents) {
          if (inc.ts > seen.lastIncidentTs && ALERT_KINDS.includes(inc.kind)) {
            notify(`Simulation ${inc.kind.replace(/_/g, ' ')}`, inc.message?.slice(0, 120) || inc.kind);
          }
        }
        if (h.incidents.length > 0) {
          seen.lastIncidentTs = Math.max(seen.lastIncidentTs, ...h.incidents.map(i => i.ts));
        }
        for (const t of h.tasks) {
          if (t.status === 'running' && t.seconds_since_progress > STALL_RED_S && !seen.stalledTasks.has(t.task_id)) {
            seen.stalledTasks.add(t.task_id);
            notify('Simulation may be stalled', `No step progress for ${formatAge(t.seconds_since_progress)} (step ${t.steps_completed}/${t.config?.max_steps ?? '?'})`);
          }
          if (t.seconds_since_progress < STALL_AMBER_S) {
            seen.stalledTasks.delete(t.task_id);
          }
        }
      } catch {
        // Backend unreachable: keep the last snapshot; the run banner
        // handles connection-loss messaging.
      }
    };

    poll();
    const id = setInterval(poll, POLL_MS);
    return () => { stopped = true; clearInterval(id); };
  }, []);

  const enableAlerts = async () => {
    if (typeof Notification === 'undefined') return;
    const perm = await Notification.requestPermission();
    setAlertsEnabled(perm === 'granted');
  };

  if (!health) return null;
  const running = health.tasks.filter(t => t.status === 'running' || t.status === 'cancelling');
  const recentIncidents = [...health.incidents].reverse();

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-3 text-xs">
      <div className="flex items-center flex-wrap gap-3">
        <span className="font-medium text-gray-700">Health</span>
        {running.length === 0 && (
          <span className="text-gray-400">no running simulations</span>
        )}
        {running.map(t => {
          const age = t.seconds_since_progress;
          const color = age >= STALL_RED_S ? 'bg-red-100 text-red-700'
            : age >= STALL_AMBER_S ? 'bg-amber-100 text-amber-700'
            : 'bg-green-100 text-green-700';
          return (
            <span key={t.task_id} className={`px-2 py-0.5 rounded ${color}`}
              title={t.config?.premise || t.task_id}>
              step {t.steps_completed}/{t.config?.max_steps ?? '?'} · progress {formatAge(age)} ago
            </span>
          );
        })}
        <button
          onClick={() => setShowIncidents(s => !s)}
          className="text-teal-600 hover:text-teal-800"
        >
          {showIncidents ? 'hide' : 'show'} incidents ({health.incidents.length})
        </button>
        {!alertsEnabled && typeof Notification !== 'undefined' && (
          <button onClick={enableAlerts} className="text-gray-500 hover:text-gray-700" title="Browser notifications on failures and stalls">
            🔔 enable alerts
          </button>
        )}
      </div>
      {showIncidents && (
        <div className="mt-2 max-h-48 overflow-y-auto divide-y divide-gray-100">
          {recentIncidents.length === 0 && (
            <p className="text-gray-400 py-1">no incidents journaled</p>
          )}
          {recentIncidents.map((inc: HealthIncident, i) => (
            <div key={`${inc.ts}-${i}`} className="py-1 flex items-start gap-2">
              <span className="text-gray-400 whitespace-nowrap">{inc.time?.slice(11, 19)}</span>
              <span className={`px-1 rounded whitespace-nowrap ${ALERT_KINDS.includes(inc.kind) ? 'bg-red-50 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
                {inc.kind}
              </span>
              <span className="text-gray-600 break-all">{inc.message || inc.log_filename || inc.batch_id || ''}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
