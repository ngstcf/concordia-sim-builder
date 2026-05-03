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

function lineColor(entry: LogEntry): string {
  if (entry.cat === 'llm') return 'text-blue-400';
  if (entry.cat === 'debug') return 'text-gray-500';

  const m = entry.msg;

  if (m.startsWith('Entity ') && m.includes(' observed: ')) return 'text-cyan-300';
  if (m.startsWith('Entity ') && m.includes(' chose action: ')) return 'text-emerald-400';

  if (m.includes('[WARNING]') || m.includes('⚠️')) return 'text-yellow-400';
  if (m.includes('[Analyzer]')) return 'text-purple-400';
  if (m.includes('[WATCHDOG]')) return 'text-orange-400';

  if (m.startsWith('✓') || m.includes('Completed') || m.includes('complete'))
    return 'text-green-400';
  if (m.startsWith('🔄') || m.startsWith('▶') || m.includes('Starting') || m.includes('Initializing'))
    return 'text-amber-300';

  return 'text-gray-200';
}

export default function LogViewer({ title, categories, entries }: LogViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

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
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-96 overflow-y-auto p-2 font-mono text-[11px] leading-4"
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
