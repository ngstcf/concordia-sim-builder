# Logging Configuration

Controls for console output and live log streaming in the Concordia Simulation Builder.

## How Logging Works

All `print()` output passes through a **stdout tee interceptor** (`stdout_tee.py`) that:

1. Writes to the original terminal (unchanged behavior)
2. Strips ANSI escape codes (from Concordia's `termcolor.colored()` output)
3. Categorizes each line by content pattern
4. Broadcasts to connected frontend clients via SSE

This means the same env vars control **both** terminal output and the frontend log panels.

### Message Categories

| Category | Detection | Examples |
|----------|-----------|---------|
| **LLM** | Contains `[LLM]` | API calls, response times, timeouts, retries |
| **DEBUG** | Contains `[DEBUG]` | Configuration details, component initialization |
| **SYSTEM** | Everything else | Runner ops, Concordia engine narrative, completions |

### Gating

- `debug_print()` checks `DEBUG_ENABLED` before calling `print()` → if disabled, nothing reaches stdout → nothing is broadcast
- `llm_print()` checks `LLM_LOGGING_ENABLED` before calling `print()` → same behavior
- SYSTEM messages (raw `print()` calls in runner and Concordia engine) always pass through

## Environment Variables

Add to your `.env` file:

```bash
# Control [DEBUG] messages in terminal and frontend (default: true)
DEBUG_ENABLED=true

# Control [LLM] API call details in terminal and frontend (default: true)
LLM_LOGGING_ENABLED=true
```

### Profiles

| Profile | Settings | Terminal Output | Frontend |
|---------|----------|----------------|----------|
| **Verbose** (default) | Both `true` | Everything | Main Log (system+debug) + LLM Log panel |
| **Quiet** | Both `false` | Runner progress only | Main Log (system only), no LLM panel |
| **Debug only** | `DEBUG=true`, `LLM=false` | Config + progress | Main Log (system+debug), no LLM panel |
| **LLM only** | `DEBUG=false`, `LLM=true` | Progress + API calls | Main Log (system only) + LLM Log panel |

## Frontend Log Panels

The frontend fetches `/api/simulations/logs/config` on mount to learn which flags are enabled, then connects to `/api/simulations/logs/stream` (SSE) for real-time entries.

- **Main Log** — Always shown. Displays SYSTEM messages (runner ops + Concordia narrative). Also includes DEBUG messages when `DEBUG_ENABLED=true`.
- **LLM Log** — Separate panel, only rendered when `LLM_LOGGING_ENABLED=true`. Shows API call traces.

### Color Coding

The frontend `LogViewer` applies colors by message content:

| Color | Message Pattern |
|-------|----------------|
| Cyan | Entity observations (`Entity X observed: ...`) |
| Emerald | Entity actions (`Entity X chose action: ...`) |
| Yellow | Warnings (`[WARNING]`, `⚠️`) |
| Orange | Watchdog messages (`[WATCHDOG]`) |
| Purple | Analyzer messages (`[Analyzer]`) |
| Amber | Progress messages (`🔄`, `▶`, `Starting`, `Initializing`) |
| Green | Completions (`✓`, `Completed`, `complete`) |
| Blue | LLM messages (entire LLM panel) |
| Gray (dim) | Debug messages |
| Gray (light) | Default system messages |

## Architecture

```
debug_print() ──┐
llm_print()  ──┐│    checks env var
               ││        │
               ▼▼        ▼
            print()  (suppressed if disabled)
               │
               ▼
         TeeStdout.write()
          ├── original stdout (terminal)
          └── LogBroadcaster.emit()
                 ├── buffer (500 entries, deque)
                 └── SSE subscribers (asyncio.Queue per client)
                        │
                        ▼
                  EventSource (frontend)
                        │
                   ┌────┴────┐
                   ▼         ▼
              Main Log    LLM Log
```

**Files:**
- `backend/utils/debug_print.py` — `debug_print()` and `llm_print()` with env var gating
- `backend/utils/stdout_tee.py` — `TeeStdout` wrapper, ANSI stripping, line categorization, `install_tee()`
- `backend/utils/log_broadcaster.py` — Thread-safe `LogBroadcaster` singleton with buffer and SSE fan-out
- `backend/api/simulations.py` — `GET /logs/config` and `GET /logs/stream` endpoints

## Programmatic Control

```python
from backend.utils.debug_print import debug_print, llm_print

debug_print("Configuration loaded")        # Shows if DEBUG_ENABLED=true
llm_print("Calling gpt-4o with timeout=120s")  # Shows if LLM_LOGGING_ENABLED=true
```

Runtime toggle (affects terminal and frontend):

```python
from backend.utils.logger import set_debug_enabled, set_llm_logging_enabled

set_debug_enabled(False)
set_llm_logging_enabled(False)
```

## Notes

- The tee is installed once at server startup in `backend/main.py` (after `load_dotenv()`)
- Terminal output is identical to pre-streaming behavior — the tee writes to original stdout first
- The frontend buffer holds 500 lines; older entries are dropped from the DOM
- SSE keepalive sent every 30s to prevent connection timeout
- Simulation HTML logs are always saved to `logs/` regardless of logging settings
