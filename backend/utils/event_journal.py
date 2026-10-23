"""Durable failure-event journal (JSONL under logs/events/).

The live SSE stream and the broadcaster's ring buffer are ephemeral: a
browser that was not connected when something failed has no way to find
out afterward. This module persists the failure-relevant subset of what
the server already reports so the UI can answer "did anything fail?"
after the fact:

- ``ingest`` is called by the stdout tee (via LogBroadcaster.emit) and
  pattern-matches already-printed lines (content-filter fallbacks,
  watchdog warnings, checkpoints, provider errors/retries).
- ``record`` is called at lifecycle choke points (simulation_state,
  batch_runner) with structured fields; events carrying a task_id are
  additionally appended to a per-task journal, which is what gives the
  run list its outcome badges.

Journaling must never break a run: every public function swallows its
own exceptions, and nothing here prints to stdout (the tee would feed
it back into ``ingest``).
"""

import datetime
import json
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGS_DIR = Path("logs")
EVENTS_DIR = LOGS_DIR / "events"

_lock = threading.Lock()

# First match wins; keep specific tags ahead of broad phrases.
_PATTERNS = [
    ("content_filter", re.compile(r"\[FILTER\]")),
    # Only actionable watchdog lines. The runner also prints a routine
    # per-minute status line under the same tag ("LLM call in progress
    # (2s) | 890 calls total"); journaling those filled the incident feed
    # at roughly one entry per minute of a healthy run, and since
    # "watchdog" is an alerting kind in the UI it meant a browser
    # notification every minute.
    ("watchdog", re.compile(r"\[WATCHDOG\].*(WARNING|hung|[Ee]mergency)")),
    ("emergency_save", re.compile(r"EMERGENCY_CHECKPOINT|WATCHDOG_EMERGENCY")),
    ("checkpoint", re.compile(r"\[CHECKPOINT\]")),
    ("error", re.compile(r"\[ERROR\]|Traceback \(most recent call last\)")),
    ("provider_error", re.compile(
        r"APIError|AuthenticationError|APITimeoutError|APIConnectionError"
        r"|timed out|connection error", re.I)),
    ("provider_retry", re.compile(r"rate.?limit|retry|backoff", re.I)),
]

_TERMINAL_KINDS = ("run_completed", "run_failed", "run_cancelled")


def _append(path: Path, entry: Dict[str, Any]) -> None:
    with _lock:
        EVENTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")


def _global_file(day: Optional[datetime.date] = None) -> Path:
    day = day or datetime.date.today()
    return EVENTS_DIR / f"events-{day.strftime('%Y%m%d')}.jsonl"


def record(kind: str, message: str = "",
           task_id: Optional[str] = None, **fields: Any) -> None:
    """Append a structured event to the global journal (and the task's)."""
    try:
        entry = {
            "ts": time.time(),
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "message": message,
        }
        entry.update({k: v for k, v in fields.items() if v is not None})
        if task_id:
            entry["task_id"] = task_id
        _append(_global_file(), entry)
        if task_id:
            _append(EVENTS_DIR / f"task-{task_id}.jsonl", entry)
    except Exception:
        pass


def ingest(category: str, line: str) -> None:
    """Classify an already-printed line; journal it if failure-relevant."""
    try:
        if category == "debug":
            return
        for kind, pattern in _PATTERNS:
            if pattern.search(line):
                record(kind, line[:500])
                return
    except Exception:
        pass


def tail(n: int = 50) -> List[Dict[str, Any]]:
    """Most recent n global events, oldest first (today, then yesterday)."""
    try:
        entries: List[Dict[str, Any]] = []
        today = datetime.date.today()
        for day in (today - datetime.timedelta(days=1), today):
            path = _global_file(day)
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as f:
                for raw in f:
                    try:
                        entries.append(json.loads(raw))
                    except Exception:
                        continue
        return entries[-n:]
    except Exception:
        return []


def run_outcomes(max_files: int = 300) -> Dict[str, Dict[str, Any]]:
    """Map log_filename -> terminal outcome, from per-task journals.

    Deliberately NOT read from .metadata.json: those files reach
    gigabytes on large runs, while a task journal is a few lines.
    """
    outcomes: Dict[str, Dict[str, Any]] = {}
    try:
        files = sorted(EVENTS_DIR.glob("task-*.jsonl"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files[:max_files]:
            try:
                with open(path, encoding="utf-8") as f:
                    for raw in f:
                        try:
                            e = json.loads(raw)
                        except Exception:
                            continue
                        name = e.get("log_filename")
                        if e.get("kind") in _TERMINAL_KINDS and name:
                            outcomes.setdefault(name, {
                                "outcome": e["kind"].replace("run_", ""),
                                "error": e.get("error"),
                                "error_type": e.get("error_type"),
                            })
            except Exception:
                continue
    except Exception:
        pass
    return outcomes


