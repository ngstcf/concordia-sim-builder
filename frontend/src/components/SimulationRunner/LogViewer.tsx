import { useEffect, useRef, useState } from 'react';

export interface LogEntry {
  ts: number;
  cat: 'system' | 'debug' | 'llm';
  msg: string;
}

interface LogViewerProps {
  title: string;
  categories: ('system' | 'debug' | 'llm')[];
  entries: LogEntry[];
}

const MAX_LINES = 500;

function formatTime(ts: number): string {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString('en-GB', { hour12: false }) +
    '.' + String(d.getMilliseconds()).padStart(3, '0');
}

const LEGEND_ITEMS: { color: string; bg: string; label: string }[] = [
  { color: 'bg-cyan-300',    bg: '', label: 'Entity observations' },
  { color: 'bg-emerald-400', bg: '', label: 'Entity actions' },
  { color: 'bg-rose-300',    bg: '', label: 'GM narration' },
  { color: 'bg-yellow-400',  bg: '', label: 'Warnings' },
  { color: 'bg-orange-400',  bg: '', label: 'Watchdog alerts' },
  { color: 'bg-purple-400',  bg: '', label: 'Analyzer output' },
  { color: 'bg-indigo-400',  bg: '', label: 'LLM API calls' },
  { color: 'bg-amber-300',   bg: '', label: 'Progress / startup' },
  { color: 'bg-green-400',   bg: '', label: 'Completion' },
  { color: 'bg-sky-300',     bg: '', label: 'Checkpoint' },
  { color: 'bg-red-400',     bg: '', label: 'Errors / cancel' },
  { color: 'bg-gray-500',    bg: '', label: 'Debug messages' },
  { color: 'bg-gray-200',    bg: '', label: 'Other system messages' },
];

function lineColor(entry: LogEntry): string {
  if (entry.cat === 'llm') return 'text-indigo-400';
  if (entry.cat === 'debug') return 'text-gray-500';

  const m = entry.msg;

  // Entity observation & action (from Concordia engine verbose output)
  if (m.startsWith('Entity ') && m.includes(' observed: ')) return 'text-cyan-300';
  if (m.startsWith('Entity ') && m.includes(' chose action: ')) return 'text-emerald-400';
  if (m.startsWith('Entity ') && m.includes(' is next to act')) return 'text-emerald-400';

  // GM narration (resolved events, suggested actions, termination checks)
  if (m.startsWith('The resolved event was:')) return 'text-rose-300';
  if (m.startsWith('The suggested action or event to resolve was:')) return 'text-rose-300';
  if (m.startsWith('Terminate?')) return 'text-rose-300';
  if (m.startsWith('Game master:')) return 'text-rose-300';
  if (m.startsWith('Contributions:') || m.startsWith('Conversation:')) return 'text-rose-300';
  if (m.startsWith('Would they do it?')) return 'text-rose-300';
  if (m.includes('Skipping the action phase')) return 'text-rose-300';

  // Errors and cancellation
  if (m.includes('[ERROR]')) return 'text-red-400';
  if (m.includes('[CANCEL]')) return 'text-red-400';

  // Warnings
  if (m.includes('[WARNING]') || m.includes('⚠️')) return 'text-yellow-400';

  // Analyzer
  if (m.includes('[Analyzer]')) return 'text-purple-400';

  // Watchdog
  if (m.includes('[WATCHDOG]')) return 'text-orange-400';

  // Checkpoints
  if (m.includes('[CHECKPOINT]')) return 'text-sky-300';
  if (m.includes('[HEARTBEAT]')) return 'text-sky-300';

  // Completion
  if (m.startsWith('✓') || m.includes('Completed') || m.includes('complete'))
    return 'text-green-400';

  // Progress & startup
  if (m.startsWith('🔄') || m.startsWith('▶') || m.includes('Starting') || m.includes('Initializing'))
    return 'text-amber-300';
  if (m.startsWith('🔨') || m.startsWith('🎮') || m.startsWith('💾'))
    return 'text-amber-300';
  if (m.startsWith('Provider:') || m.startsWith('Model:') || m.startsWith('GM Provider:') || m.startsWith('GM Model:'))
    return 'text-amber-300';
  if (m.startsWith('Max Steps:') || m.startsWith('Agents:') || m.startsWith('Premise:') || m.startsWith('Early Termination:'))
    return 'text-amber-300';
  if (m.includes('==='))
    return 'text-amber-300';

  return 'text-gray-200';
}

export default function LogViewer({ title, categories, entries }: LogViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showLegend, setShowLegend] = useState(false);

  const filtered = entries
    .filter((e) => categories.includes(e.cat))
    .slice(-MAX_LINES);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [filtered.length, autoScroll]);

  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
    setAutoScroll(atBottom);
  };

  return (
    <div className="border border-gray-700 rounded-lg bg-gray-900 overflow-hidden">
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-800 border-b border-gray-700">
        <span className="text-xs font-medium text-gray-300">{title}</span>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-500">{filtered.length} lines</span>
          <button
            onClick={() => setShowLegend(!showLegend)}
            className="text-[10px] px-1.5 py-0.5 rounded text-gray-500 bg-gray-800 hover:text-gray-300"
            title="Toggle color legend"
          >
            Legend
          </button>
          <button
            onClick={() => {
              setAutoScroll(true);
              if (containerRef.current) {
                containerRef.current.scrollTop = containerRef.current.scrollHeight;
              }
            }}
            className={`text-[10px] px-1.5 py-0.5 rounded ${
              autoScroll
                ? 'text-green-400 bg-green-900/30'
                : 'text-gray-500 bg-gray-800 hover:text-gray-300'
            }`}
          >
            {autoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF'}
          </button>
        </div>
      </div>
      {showLegend && (
        <div className="px-3 py-2 bg-gray-800/60 border-b border-gray-700 flex flex-wrap gap-x-4 gap-y-1">
          {LEGEND_ITEMS.map((item) => (
            <span key={item.label} className="flex items-center gap-1.5 text-[10px] text-gray-400">
              <span className={`w-2 h-2 rounded-full ${item.color} inline-block flex-shrink-0`} />
              {item.label}
            </span>
          ))}
        </div>
      )}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-[32rem] overflow-y-auto p-2 font-mono text-[11px] leading-4"
      >
        {filtered.length === 0 ? (
          <div className="text-gray-600 text-center py-8">Waiting for log output...</div>
        ) : (
          filtered.map((entry, i) => (
            <div key={i} className={lineColor(entry)}>
              <span className="text-gray-600 select-none">{formatTime(entry.ts)} </span>
              {entry.msg}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
