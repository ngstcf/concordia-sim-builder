# Concordia Simulation Builder

A web interface for Google DeepMind's [Concordia](https://github.com/google-deepmind/concordia) library that makes running agent-based social simulations accessible—no Python programming required.

Configure agents, psychological components, and scenarios through forms. Run simulations powered by LLMs. Analyze results with built-in analytics including timeline visualization, cooperation metrics, grounded variables tracking, and AI-powered deep content analysis.

## Why a Builder?

Concordia is a powerful research framework, but coding a simulation from scratch requires significant Python expertise. Even standard upstream examples — 2-to-4-agent scenarios using built-in prefabs — require 1,100 to 1,300 lines of Python across multiple files; examples with custom game masters and payoff logic reach 1,600 lines; research scenarios with large persona datasets exceed 7,000 lines. Each involves LLM initialization, agent configuration, memory injection, Game Master wiring, engine selection, and result parsing — all before the first simulation step executes.

| Without the Builder | With the Builder |
|---------------------|------------------|
| 1,100–7,000+ lines of Python per scenario | Configure through form fields and dropdowns |
| Discover valid prefabs by reading library source | Browse prefabs with descriptions and defaults |
| Invalid configs fail at runtime, after spending API credits | Real-time validation catches errors before execution |
| Terminal-only output, no way to pause or inspect mid-run | Play/Pause/Step/Stop controls with live log streaming |
| Kill the process to stop; restart from scratch to retry | Cancel with partial results saved; adjust and re-run |
| Build your own output pipeline | Structured HTML report, 9-tab analytics dashboard, AI-powered analysis |
| Write custom scripts for data extraction and analysis | Structured CSV/JSON export, cooperation metrics, grounded variable tracking |
| Manual agent creation, one at a time | Census-based generation from demographic distributions, persona generator |
| Re-run manually with different parameters | Batch runs with parameter sweeps over temperature and step count |
| Every new scenario is a new coding effort | 38 ready-to-run templates covering research, policy, game theory, upstream DeepMind examples, and more |

![Simulation Builder](https://img.shields.io/badge/Concordia-Simulation%20Builder-blue)
![Version](https://img.shields.io/badge/Version-2.4.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

**Documentation:** [c3.unu.edu/projects/ai/simulator/v2.4.html](https://c3.unu.edu/projects/ai/simulator/v2.4.html)

**Blog article:** [AI-Powered Agent-Based Simulation Platform with Applications to the UN Sustainable Development Goals](https://c3.unu.edu/blog/concordia-simulation-builder-research-education)

**Guides:**
- [Simulation Building Guide](docs/SIMULATION_BUILDING_GUIDE.md) — Practitioner guide for creating simulations, configuring agents, components, and engines
- [Simulation Templates Guide](docs/SIMULATION_TEMPLATES_GUIDE.md) — Practitioner guide with research setups and experiment suggestions
- [Template Creation Guide](docs/TEMPLATE_CREATION_GUIDE.md) — Developer guide for adding new simulation templates
- [Timeout Configuration](docs/TIMEOUT_CONFIGURATION.md) — Tuning LLM, watchdog, and frontend timeouts

Template inventory is updated over time; the latest template count is always reflected in [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md).

**Research Use Cases:**
- [Vaccine Hesitancy Study](docs/research-use-cases/vaccine-hesitancy-study.md)
- [Phishing Attack Simulation](docs/research-use-cases/phishing-attack-simulation.md)
- [Urban Gentrification Simulation](docs/research-use-cases/urban-gentrification-simulation.md)

## Sample Simulation Results

Nine completed simulation runs are included in the [`logs/`](logs/) directory, spanning 8 distinct scenarios across 3 Game Master types. Each run was configured and executed entirely through the web interface using different LLM provider combinations.

Each simulation produces three output files:

- **`.html`** — Concordia simulation log (structured entries with full narrative)
- **`.metadata.json`** — Run metadata (agents, LLM config, GM config, timestamps, duration, plus outcome fields: completion status, steps completed vs. max steps, and error details when a run fails)
- **`_analysis.md`** — LLM-powered analysis report (executive summary, effectiveness assessment, insights, recommendations)

| # | Scenario | GM Type | Agents | Agent LLM | GM LLM | Duration |
|---|----------|---------|--------|-----------|--------|----------|
| 1 | **Peace Negotiation** — Russia-Ukraine talks at Istanbul, Jan 2026 | Generic | 2 (Agent R, Agent U) | DeepSeek V4 Flash | Claude Sonnet 4.6 | 29 min |
| 2 | **Strategic Game** — Prisoner's Dilemma behavioral economics experiment | Game-Theoretic | 2 (Alex, Sam) | OpenAI O3-Mini | Claude Sonnet 4.6 | 3 min |
| 3 | **Flood Evacuation** — Coastal town Category 3 hurricane response (SDG 11/13) | Generic | 5 (Sarah, Robert, Javier, Eleanor, Pastor Moses) | DeepSeek V4 Flash | GPT-5.5 | 57 min |
| 4 | **Software Team** — Fintech startup payment processing sprint | Generic | 3 (Project Manager, Senior Dev, Junior Dev) | GPT-5.4 Mini | Claude Opus 4.7 | 49 min |
| 5 | **Conversational Debate** — AI tutors vs human teachers roundtable | Dialogic | 3 (Dr. Chen, Mr. Patel, Ms. Jackson) | Claude Haiku 4.5 | GPT-5.5 | 7 min |
| 6 | **Labor Strike** — Collective action and wage negotiation (SDG 8) | Generic | 4 (Elena, David, Amina, Richard) | DeepSeek V4 Flash | GPT-5.5 | 73 min |
| 7 | **Fishery Management** — Tragedy of the commons in marine resources (SDG 14) | Generic | 4 (Hiroshi, Maria, Okonkwo, Dr. Lisa) | OpenAI O3-Mini | GPT-5 | 133 min |
| 8 | **Music Career** — Singer-songwriter deliberation with friends | Dialogic | 5 (Jordan, Sandra, Dev, Rae, Marcus) | Ollama Gemma4 | Azure GPT-5 | 207 min |
| 9 | **Flood Evacuation** *(rerun)* — Same scenario, different LLM combination | Generic | 5 (Sarah, Robert, Javier, Eleanor, Pastor Moses) | OpenAI GPT-4o-Mini | Claude Sonnet 4.6 | 62 min |

## Features

- **Form-Based Configuration** — Intuitive web UI for building agent-based simulations without coding
- **38 Simulation Templates** — Pre-built scenarios covering peace negotiation, game theory, SDG research, cybersecurity, and 5 adapted Google DeepMind upstream examples (see [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md))
- **Template Growth** — More templates are added based on user feedback as the project grows
- **Multi-Agent System** — Define agents with unique goals, memories, psychological components, and behavioral prefabs
- **Psychological Components** — Personality, cognitive bias, social identity, emotions, values, Theory of Planned Behavior
- **Multiple Simulation Engines** — Sequential, asynchronous, simultaneous, and step controller (play/pause/step/stop)
- **5 Contrib GM Components** — Death, GMWorkingMemory, NpcEventGenerator, LocationBasedFilter, SpaceshipSystem
- **Formative Memories** — Generate agent backstories with standalone endpoint and in-editor button
- **Nested Simulations** — PhoneGameMaster pattern for running mini-simulations within simulations
- **Measurements** — Inject measurements into any engine with Component Logs tab in results
- **Grounded Variables** — Track simulation state variables with AI-powered post-processing, with optional joint constraints (`variable_groups`) for shares of a common whole that must sum to a declared total
- **Agent Probe** — Administer a fixed multiple-choice question to every agent during the run and tally the answers, so a measured quantity has the roster as its denominator rather than a narrator's estimate (see [Measuring by Counting](#measuring-by-counting))
- **Live Log Streaming** — Real-time terminal output mirrored to frontend via SSE with color-coded messages
- **9-Tab Analytics Dashboard** — Simulation Log, Statistical Dashboard, Timeline, Grounded Variables, Cooperation, Actions, AI Summary, Analysis, Component Logs
- **8 LLM Providers** — OpenAI, Azure OpenAI (up to two endpoints), DeepSeek, Anthropic, Gemini, GLM, Ollama Local, Ollama Remote
- **Separate GM LLM** — Independent model selection for Game Master
- **Checkpoint, Resume & Extend** — Automatic mid-run HTML checkpoints + resumable `.state.json` sidecars every N steps; a green **Resume** button on any checkpoint restores full agent/GM memory state and continues from where the run stopped. A teal **Extend** button appears on every completed run in Recent Simulations — enter how many additional steps to run and continue from the final state, whether the simulation ended early (LLM decision) or reached `max_steps`. All state is persisted via Concordia's native `load_from_checkpoint` API; LLM settings, agent config, and all memories are restored from the sidecar — no template reload needed. **Limitations:** (1) Resumable state is written only for the *streaming* execution path (`/execute`), not the simple path (`/execute-simple`); (2) Sims using `player_specific_context` (formative memories initializer) may re-run initializer steps on resume — verify before relying on it for those templates; (3) Resuming batch runs is not supported; (4) Concordia's JSON serialisation silently drops non-serializable component attributes (e.g. live model references) — these are re-injected from the reconstructed config, so the simulation continues correctly but those attributes are not checkpointed verbatim. **Disk:** a state file is roughly the size of the run's memory banks and reaches tens of megabytes on a long run, so checkpoints dominate `logs/` over time. The emergency copy written between the engine loop and the final save is retired automatically once the final log and state are on disk, and the DELETE sweep below clears whatever completed runs have made redundant while sparing the resume point of any run that never finished.
- **Simulation Management** — Mid-run cancellation with LLM-level interrupt (cancels before the next API call, not just between steps), partial results saved, per-simulation delete, server shutdown
- **Failure Observability** — Durable event journal, run outcome badges, a Health strip with stall detection, and opt-in browser notifications, so the browser can answer "did anything fail?" even after disconnects or overnight runs (see [Monitoring Long-Running Simulations](#monitoring-long-running-simulations))
- **Save & Load Configurations** — Save named configs to the server, reload from "My Configs" panel, or export/import as JSON files

For the complete building guide, see [SIMULATION_BUILDING_GUIDE.md](docs/SIMULATION_BUILDING_GUIDE.md).

## Use Cases

- **Social Science Research** — Model complex social interactions with psychological realism
- **Policy Simulation** — Test SDG-aligned scenarios (peace, labor, fisheries, disaster response, inequality)
- **Game Theory** — Run iterated games with payoff tracking and cooperation analytics
- **Education** — Teach negotiation, conflict resolution, and social dynamics
- **Cybersecurity** — Tabletop exercises with nested adversarial simulations
- **Creative Writing** — Explore character interactions and story outcomes

## Tech Stack

**Backend:**
- Python 3.10+ with FastAPI
- Google DeepMind Concordia 2.4.0
- Pydantic for data validation
- Sentence Transformers for embeddings

**Frontend:**
- React 18 with TypeScript
- Vite for fast development
- Tailwind CSS v4 for styling
- React Router for navigation
- TanStack Query for data management
- react-markdown with remark-gfm for report rendering

## Installation

### Prerequisites

- Python 3.13 or higher
- Node.js 18 or higher
- API keys for at least one LLM provider (OpenAI, Azure OpenAI, DeepSeek, Gemini, Anthropic, or GLM), OR Ollama for local models

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/ngstcf/concordia-sim-builder.git
cd concordia-sim-builder

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies (pins a patched Concordia 2.4.0 fork — see note below)
pip install -r requirements.txt
```

> **Note:** `requirements.txt` pins a small **patched fork** of Concordia 2.4.0 ([`ngstcf/concordia`](https://github.com/ngstcf/concordia/tree/v2.4.0-simbuilder)), not the stock PyPI wheel. Two Game Master features — per-agent social-media activity rates and variable-increment clocks — depend on it; with the stock wheel, activity rates are silently ignored and the Mastodon influence experiment will not reproduce. `pip install -r requirements.txt` pulls the patched fork automatically. See [Local Modifications to Concordia](#local-modifications-to-concordia-v240) for what changed and why.

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# LLM Provider Configuration (set at least one)
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
ANTHROPIC_API_KEY=sk-xxx
AZURE_OAI_KEY=xxx
AZURE_OAI_ENDPOINT=https://your-resource.openai.azure.com

# Optional: second Azure OpenAI resource (provider id "azure2")
# AZURE_OAI_KEY2=xxx
# AZURE_OAI_ENDPOINT2=https://your-second-resource.openai.azure.com

# Optional: Separate GM LLM (defaults to agent LLM if not set)
# GM_LLM_PROVIDER=openai
# GM_LLM_MODEL=gpt-4o

# Optional: Ollama (local or remote)
# OLLAMA_BASE_URL=http://localhost:11434/v1
# OLLAMA_API_KEY=your-key-for-remote

# Timeouts
LLM_TIMEOUT=180                  # Per-request timeout in seconds (default: 180)
LLM_REASONING_TIMEOUT=300        # Timeout for reasoning models like O3 (default: 300)
LLM_MAX_RETRIES=2                # Retry attempts (default: 2)
LLM_MAX_CONCURRENCY=64           # Max concurrent LLM requests per model instance (default: 16)
WATCHDOG_TIMEOUT_SECONDS=600     # Hang detection timeout (default: 600)
WATCHDOG_ENABLED=true            # Set false to disable hang detection

# Console & live log streaming controls
DEBUG_ENABLED=true               # Control [DEBUG] messages
LLM_LOGGING_ENABLED=true         # Control [LLM] API call details

# Frontend
VITE_SIMULATION_TIMEOUT=10800000  # Simulation timeout in ms (default: 3 hours)
```

**Provider-specific request fields (`extra_body`).** LLM settings accept an optional `extra_body` object whose fields are sent verbatim in the API request body, for deployment-specific parameters that have no first-class setting. The main use is reasoning effort on reasoning-model deployments, e.g. `"extra_body": {"reasoning_effort": "none"}`. Verified menus: gpt-5.6 family `reasoning_effort: none | low | medium | high | xhigh` (`none` turns a reasoning model into a fast non-reasoning one); DeepSeek `reasoning_effort: none | low | high | max` plus a `"thinking": {"type": "enabled"|"disabled"}` toggle (V4 models default to `high`; `none` alone disables thinking, and when both fields are sent the `thinking` toggle takes precedence in both directions, verified via reasoning-token usage). Anthropic's native API has no `reasoning_effort` field: its thinking toggle is `"thinking": {"type": ...}` (verified) and effort control is `"output_config": {"effort": ...}` on models that support it (claude-haiku-4-5 does not). Values are provider-defined and can vary by deployment; an unsupported value fails fast with a clear 400 naming the allowed set. Supported on all OpenAI-compatible providers and Anthropic.

## Running the Application

### Start Backend (Terminal 1)

```bash
source env/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: `http://localhost:8000` | API Docs: `http://localhost:8000/docs`

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend: `http://localhost:5173`

## Monitoring Long-Running Simulations

Long runs outlive browser sessions: connections drop, laptops sleep, and a
failure at 3 a.m. used to be visible only in the server terminal. The
platform therefore keeps a **durable failure journal** on the server and
surfaces it in the UI, so you can close the browser, come back later, and
still answer *"did anything fail while I was away?"*

### What you see in the UI

- **Health strip** (top of the Runner page). For every running simulation
  it shows `step ≥X/Y · active Ns ago`, colored by time since the last
  LLM call: green (fresh), amber (>5 min), red (>15 min). A grey chip
  shows total LLM calls this backend session and how many are in flight.
  Click **show incidents** to expand the recent event feed (failures in
  red). Click **🔔 enable alerts** once to grant browser-notification
  permission; you will then get a desktop notification on run failures,
  content-filter events, watchdog warnings, and stalls (>15 min with no
  LLM activity) while the tab is open, even in a background window.
- **Outcome badges** in Recent Simulations: **✓** (completed), red
  **failed** (hover for the error message), amber **cancelled**. Runs
  executed before this feature have no journal and show no badge.

Interpreting stalls: "active Ns ago" measures time since the last LLM
call started or returned, and a call in flight counts as active however
long the provider takes — a slow response is work in progress, not a
stall. Liveness deliberately does *not* use the step counter: the
asynchronous social-media engine reports a step only when its first
entity happens to act, so a healthy large-population run can go two full
steps between step events (hence `step ≥X`, a lower bound on true engine
progress). Large populations legitimately take minutes per step, so amber
during a heavy run is normal; red is the signal worth investigating
(start with the incident feed, then the live log panel).

### Where the data lives

Events append to JSONL files under `logs/events/` — one global file per
day (`events-YYYYMMDD.jsonl`) and one small file per run
(`task-{task_id}.jsonl`). They survive backend restarts, are safe to
delete (you lose only badges and incident history, never simulation
data), and are grep-friendly:

```json
{"ts": 1788178119.6, "time": "2026-08-31T21:28:39", "kind": "run_failed",
 "task_id": "d5c1…", "log_filename": "20260831_212839_….html",
 "steps_completed": 0, "error": "Error code: 404 - …", "error_type": "NotFoundError"}
```

Journaled event kinds:

| Group | Kinds |
|-------|-------|
| Run lifecycle | `run_registered`, `run_completed`, `run_failed`, `run_cancelled` |
| Batch lifecycle | `batch_started`, `batch_run_failed`, `batch_complete`, `batch_cancelled` |
| Captured from server output | `content_filter`, `watchdog`, `checkpoint`, `emergency_save`, `provider_error`, `provider_retry`, `error` |

### API

- `GET /api/simulations/health?incidents=50` — running tasks (with
  `steps_completed` and `seconds_since_progress`), an `llm` block
  (`calls_in_flight`, `total_calls`, `seconds_since_call`) that is the
  liveness signal, plus the most recent journaled incidents. This is what
  the Health strip polls every 30 s.
- `GET /api/simulations/recent` — each entry now carries `outcome`
  (`completed` / `failed` / `cancelled` / `null`) and `outcome_error`.

Scope note: this is *observability through the browser* — detection still
requires polling from an open tab. Server-side alerting that needs no tab
at all (webhooks, scheduled sentinels) is planned as part of a dedicated
long-run operating mode.

## Measuring by Counting

Grounded variables are estimated by the Game Master: asked what share of a
population holds some view, it reads the current situation and narrates a
figure. That is useful as situational state carried in the narrative, but
nothing ties the number to the agents that exist, so it should not be read
as a measurement of them. Two features address this. Both are configured in
the Game Master form (Agent Probe, and Joint Constraints under Grounded
Variables) and both round-trip through the simulation config JSON, so they
can equally be set by hand or through `POST /api/simulations/execute`.

### Agent probe

Puts a fixed multiple-choice question to every agent at a set cadence and
tallies the answers. The denominator is the roster by construction, so the
shares cannot fail to sum to 100, and every point is attributable to named
respondents.

```json
"game_master": {
  "agent_probe": {
    "items": [{
      "name": "vote_intention",
      "question": "Which candidate do you currently intend to vote for?",
      "options": ["Candidate A", "Candidate B", "Undecided"]
    }],
    "interval": 54,
    "memory_limit": 40
  }
}
```

`interval` counts **Game Master events, not engine steps**. Under the
asynchronous engine each entity runs its own loop with no shared step
boundary, so events are the only clock every agent is measured against.
Cost scales with population, so an interval tuned for a small cast
oversamples a large one by the same factor the cast grew: size it from the
number of agents expected to act, not from a fixed number of steps. The
Game Master form does that conversion for you: pick a cadence in steps and
it derives the event interval from the cast and their activity rates, then
previews how many measurements the run will yield and what they will cost
in model calls.

The probe reads memory and never makes an agent act or observe, so it does
not perturb the run. Results land at the top level of the JSON export
under `agent_probe`, in four blocks: `series` (the tally per item over
time), `responses` (every individual answer, with the agent that gave it),
`failures` (each reading that did not come back, with a reason), and
`integrity` (administrations, events seen, and failure count).

Read `integrity` before the series. An agent that cannot be surveyed is
recorded as a failure and left out of that reading's denominator, rather
than being given a default answer, so a series that moved because fewer
agents answered is distinguishable from one that moved because the
population changed. If a component is configured but cannot be found at
harvest time, the run says so loudly rather than exporting nothing.

### Variable groups

Per-variable bounds cannot express that several variables describe one
whole: each share can be a legal 0-100 value while the total is
impossible. `variable_groups` declares the joint constraint.

```json
"game_master": {
  "variable_groups": [{
    "name": "poll_shares",
    "members": ["rivera_support", "hale_support", "undecided_rate"],
    "sums_to": 100.0,
    "tolerance": 1.0,
    "on_violation": "renormalize"
  }]
}
```

`on_violation` is `renormalize` (rescale to the declared total, preserving
proportions), `reject` (discard the offending update, keep the previous
values), or `flag` (record it and change nothing). Violations are recorded
under all three, so a rescaled series still shows where it had to be
rescaled. Individual variables also accept `cumulative` (a running total
that never decreases) and `max_delta` (the largest single-update
increase), which together keep a counter from being unbounded above.

## Templates (38)

| Category | Templates |
|----------|-----------|
| **Quick Start** | Coffee Shop Demo (5 steps), Peace Negotiation (20 steps) |
| **Prefab Demos** | Planning Agent, Scripted Entity, Context-Aware Moderator, Dialogic Conversation, Strategic Game, Interviewer, Formative Memories, Marketplace |
| **Research** | Vaccine Hesitancy, Urban Gentrification, Phishing Attack, AI Policy Red Team, Music Career Crossroads |
| **General Scenarios** | Rational Negotiators, Philosophy Roundtable, Social Media Debate, Sealed-Bid Auction, Wizard-of-Oz CS Training, Spaceship Crisis |
| **Advanced Scenarios** | Nested Simulation, Grounded Variables, Hostage Negotiation (step controller), Colony Survival (contrib GM), Bookstore Reunion (formative mem), Ethics Board (measurements), Diplomatic Crisis (nested sim) |
| **SDG Scenarios** | State Formation (16), Labor Strike (8), Fishery Management (14), Flood Evacuation (11/13), Educational Opportunity (10) |
| **Upstream Examples** | Robot Alchemy Forum (async), Philosophy Exam Prep, Romantic Trig Tutor, General Store: Crime & Punishment (simultaneous, 7 agents), Pub Coordination: London (game theory) |

See [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md) for detailed parameter documentation and research guides for all templates. The guide always reflects the latest template count.

## API Endpoints

### Core

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/simulations/prefabs` | GET | List available entity/GM prefabs |
| `/api/simulations/providers` | GET | List supported LLM providers |
| `/api/simulations/models/{provider}` | GET | List models for a provider |
| `/api/simulations/validate` | POST | Validate simulation configuration |
| `/api/simulations/execute` | POST | Run simulation with real-time SSE streaming |
| `/api/simulations/execute-simple` | POST | Run simulation and return complete results (non-streaming; no resumable state written) |
| `/api/simulations/import` | POST | Import and validate a configuration from JSON |
| `/api/simulations/export-template` | GET | Export a blank configuration template |
| `/api/simulations/configs` | GET | List saved configurations |
| `/api/simulations/configs` | POST | Save a named configuration |
| `/api/simulations/configs/{slug}` | GET | Load a saved configuration |
| `/api/simulations/configs/{slug}` | DELETE | Delete a saved configuration |

### Simulation Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/status` | GET | Status of all running simulations |
| `/api/simulations/status/{task_id}` | GET | Status of specific simulation |
| `/api/simulations/health` | GET | Running tasks, LLM-call liveness, and recent journaled incidents (`?incidents=N`) |
| `/api/simulations/cancel/{task_id}` | POST | Cancel a running simulation (saves partial results) |
| `/api/simulations/control/{task_id}/pause` | POST | Pause (step controller engine) |
| `/api/simulations/control/{task_id}/play` | POST | Resume continuous execution |
| `/api/simulations/control/{task_id}/step` | POST | Advance one step |
| `/api/simulations/control/{task_id}/stop` | POST | Stop |
| `/api/server/shutdown` | POST | Shutdown server |

### Logs & Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/recent` | GET | List recent simulation logs (includes `resumable` flag, `state_filename`, and journal-derived `outcome` / `outcome_error`) |
| `/api/simulations/logs/{filename}` | GET | Get simulation log HTML |
| `/api/simulations/logs/{filename}` | DELETE | Delete simulation log + metadata |
| `/api/simulations/logs/{filename}/analytics` | GET | Analytics data for all 9 result tabs |
| `/api/simulations/logs/{filename}/export-json` | GET | Full structured export (grounded-variable histories, action records) |
| `/api/simulations/logs/{filename}/export-csv` | GET | Structured export as CSV (`?data_type=variables\|actions\|...`) |
| `/api/simulations/logs/checkpoints` | GET | List checkpoint files (includes `resumable` flag + `state_filename`) |
| `/api/simulations/logs/checkpoints` | DELETE | Delete the checkpoint files + `.state.json` sidecars that completed runs have made redundant; the most advanced checkpoint of a run that never finished is spared, since it is that run's only resume point. `?include_unfinished=true` clears those too |
| `/api/simulations/resume` | POST | Resume or extend simulation from a `.state.json` sidecar (SSE stream); accepts optional `additional_steps` to run beyond the saved state |
| `/api/simulations/logs/config` | GET | Log streaming config (debug/LLM flags) |
| `/api/simulations/logs/stream` | GET | SSE endpoint for live log streaming |

### Batch Runs & Reliability

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/batch/execute` | POST | Run a batch of simulations with optional parameter sweeps |
| `/api/simulations/batch/list` | GET | List completed batch runs |
| `/api/simulations/batch/{batch_id}/status` | GET | Current status of a batch run |
| `/api/simulations/batch/{batch_id}/cancel` | POST | Cancel a running batch |
| `/api/simulations/batch/{batch_id}/export-csv` | GET | Aggregated CSV across all runs in a batch |
| `/api/simulations/batch/{batch_id}/reliability` | GET | ICC(3,1) reliability report for questionnaire outcomes |

### Analysis & Variables

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/analyze-simulation` | POST | LLM-powered analysis report |
| `/api/simulations/grounded-variables/extract` | POST | Extract variable history from log using AI |
| `/api/simulations/grounded-variables/{simulation_id}` | GET | Get grounded variables data |
| `/api/simulations/generate-formative-memories` | POST | Generate formative backstory memories for an agent |
| `/api/simulations/generate-personas` | POST | Generate diverse personas via Concordia's persona generators |
| `/api/simulations/generate-personas-census` | POST | Generate personas by sampling a demographic distribution |
| `/api/simulations/parse-distribution` | POST | Parse a distribution spec from JSON or CSV content |
| `/api/simulations/upload-distribution` | POST | Parse an uploaded CSV/JSON file into a distribution spec |

### Components & Templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/components/templates` | GET | Psychological component templates |
| `/api/simulations/components/validate` | POST | Validate component parameters |
| `/api/simulations/contrib-components` | GET | Registry of available contrib GM components |
| `/api/simulations/templates/{template-name}` | GET | Get template configuration (39 templates; more are added based on user feedback as the project grows) |

## Supported Prefabs

### Entity Prefabs (Agents)

| Prefab | Description | Best For |
|--------|-------------|----------|
| `basic__Entity` | Standard agent with "three key questions" decision framework | Most scenarios |
| `basic_with_plan__Entity` | Adds strategic planning with time horizons | Complex coordination |
| `basic_scripted__Entity` | Follows predefined scripts exactly | Testing, demonstrations |
| `context_aware_scripted__Entity` | Adapts script to context, auto-closes when exhausted | Natural moderators |
| `minimal__Entity` | Simplified decision-making | Lightweight simulations |

### Game Master Prefabs

| Prefab | Description | Best For |
|--------|-------------|----------|
| `generic__GameMaster` | Standard narrative control | Most simulations |
| `dialogic__GameMaster` | Conversation-focused with auto-termination | Dialogue scenarios |
| `game_theoretic_and_dramaturgic__GameMaster` | Matrix games with payoffs/scores | Strategic games |
| `interviewer__GameMaster` | Administers questionnaires | Surveys, interviews |
| `marketplace__GameMaster` | Economic trading systems | Market simulations |
| `async_social_media__GameMaster` † | Social media forum with posts and feeds, **per-agent activity rates** | Online discourse studies |
| `simultaneous_resolution_gm__GameMasterSimultaneous` † | Simultaneous event resolution with locations, NPCs, working memory | Multi-agent workplace, spatial scenarios |
| `space_ship__GameMaster` | Spaceship systems with health/failure tracking | Spaceship crisis scenarios |

† Carries a [local modification](#local-modifications-to-concordia-v240) beyond stock Concordia 2.4.0.

## Local Modifications to Concordia (v2.4.0)

The Builder runs against Concordia **v2.4.0** with two small local patches to Game Master prefabs — the tree that produced the published Mastodon influence experiment results. The patches are published as a public fork, [**`ngstcf/concordia@5ed8813`**](https://github.com/ngstcf/concordia/commit/5ed88134f7a08f2a13209b2e01bbb70a76d6771f) (branch `v2.4.0-simbuilder`), which `requirements.txt` pins directly. They are also captured as a standalone tracked patch for review and offline use: [`patches/concordia-2.4.0-local.patch`](patches/concordia-2.4.0-local.patch).

> **⚠️ Reproducibility:** the stock PyPI `gdm-concordia==2.4.0` does **not** contain these changes. The Builder's vendored activation scheduler (see item 1's update below) now provides per-agent activity sampling at runtime regardless of the library tree, but the pinned fork remains the supported, tested configuration and still carries the variable-clock patch (item 2). `requirements.txt` pins the fork, so `pip install -r requirements.txt` is sufficient.

### What changed and why

**1. `async_social_media__GameMaster` — per-agent stochastic activation** *(material; sampling rule now superseded at runtime, see the update below)*

Stock v2.4.0 activates **every** eligible player on **every** step — its next-acting component simply returns all player names, with no notion of posting frequency. Per-agent posting schedules did not survive Concordia's upstream port of the prefab, so the fork re-introduced them at the GM level:

- Added `default_activity_rate`, `per_agent_activity_rates`, and `activity_seed` parameters.
- Added probabilistic per-agent sampling in the next-acting component.
- Seeded the RNG for reproducibility, and guaranteed the engine still advances when no agent is sampled in a step.

This is the GM-level mechanism behind the Builder's **Social Media Activity Model** sliders.

**Update (Aug 2026): corrected activation semantics, vendored into the backend.** The fork patch's sampling rule normalized rates above 1.0 against the roster maximum, which gave a per-agent parameter global side effects (raising one agent's rate silently suppressed every other agent's activation) and made the rule discontinuous at 1.0 (an agent at rate 1.6 could act far less often than one at 0.8). The Builder now overrides the GM's next-acting component at build time with a vendored scheduler, [`backend/prefabs/activity_scheduler.py`](backend/prefabs/activity_scheduler.py): each agent's per-step probability is `min(1, rate / default_activity_rate)`, independent of every other agent's rate. Because the engine allows at most one act per agent per step, rates above `default_activity_rate` cannot be honored; they are clipped to 1.0 with a startup warning naming the affected agents. To express "agent X is N times as active," scale the *other* agents down instead. The fork's parameter plumbing is still used; only its sampling rule is superseded. The bundled Mastodon template follows the source study's implementation ([sandbox-social/mastodon-sim](https://github.com/sandbox-social/mastodon-sim)): voters act with per-step probability 0.8 and the malicious actor 0.9, the manipulation being carried by the agent's goal and content rather than posting volume.

**Context-window control (Aug 2026).** In a broadcast forum every post lands in every agent's history (~140 tokens per entry), so prompts grow with population × steps: 100 agents × 20 steps projects ~275k tokens per prompt, beyond typical 128k contexts. For the async social media GM, `game_master.parameters.context_window_steps` bounds each agent's observation and self-perception history to a window expressed in engine steps (converted to an entry budget via the scheduler's expected actions per step) and bounds the GM's own observation buffer with the same budget. `POST /validate` now projects peak prompt tokens for these configs and warns when the projection exceeds ~100k, so an infeasible population is caught before compute is spent, not hours into a run. The control is exposed in the builder UI as the **"Context Window (steps)"** field on the async GM's Social Media Activity Model panel (empty = full history), and the validation projection surfaces through the builder's normal warnings display, so both are usable without touching JSON. Per-agent `components.observation_history_length` / `components.self_perception_history_length` remain individually settable and take precedence. Note the semantics: a window is bounded attention (agents forget older posts permanently); it is not equivalent to feed-based architectures where agents can re-query history.

**2. `simultaneous_resolution_gm__GameMasterSimultaneous` — variable-clock wiring** *(minor)*

The contrib clock already supported variable time increments, but the prefab never forwarded the configuration. The patch threads `use_variable_increments` and `variable_increment_rules` from GM params into the clock, enabling multi-interval / variable-step schedules from the Builder.

**3. Vendored `ParallelQuestionnaireEngine` — backend, not a fork patch** *(material for questionnaires)*

Upstream Concordia removed this engine (and `EntityAgent.stateless_act`) in commit `030d2fa`, but it is the only engine that can drive the multiple-choice questionnaire component's JSON-list protocol used by the `interviewer__GameMaster` prefab — without it, interviewer runs record no answers and batch ICC reliability is empty. Rather than patching the fork further, the engine is vendored into the backend at `backend/services/parallel_questionnaire_engine.py` (recovered verbatim from the commit before its removal, with a module-level replica of `stateless_act`; provenance in the module docstring). The pinned fork stays limited to the two patches above.

**4. Asynchronous engine — progress reporting** *(reporting only; not in the pinned commit)*

The asynchronous engine gives each entity its own loop and documents `checkpoint_callback` as running "after each iteration," but the call sat past the two `continue` statements taken when the entity draws no turn, so an iteration in which it did not act passed through silently — and only entity 0 receives the callback at all. The backend counted invocations, so it measured `max_steps × activity_rate(first agent in the roster)`: a completed 20-step run with that agent acting at rate 0.8 reported **16 of 20** and looked truncated. Because the rate that governs the count belongs to whichever agent happens to be listed first, the size of the undercount also varies with configuration: two setups that differ only in that agent's activity rate report different completed-step totals for the same `max_steps`, which can be mistaken for a real difference in how long the runs went.

The iterations were always real: exported action records reach the final step with the full cast acting, and action volumes are unaffected. Only the reporting was short — but it also misaligned interval checkpointing, since a state saved every 5 callbacks landed at true iterations ~6, ~13, ~19, so a checkpoint labelled step 10 was not one.

Both skip paths now report, and `save_checkpoint` puts the engine's own loop index into `checkpoint_data` as `engine_step` so callers need not reconstruct it (`checkpoint_counter` cannot serve that purpose — `make_checkpoint_data()` increments it, and emergency and final saves happen outside the loop, so it counts snapshots rather than steps). The backend prefers `engine_step` and falls back to counting on an unpatched tree, so it works either way.

Tracked separately as [`patches/concordia-async-step-reporting.patch`](patches/concordia-async-step-reporting.patch), which applies onto `5ed8813`. It is deliberately **not** folded into the pinned commit or `patches/concordia-2.4.0-local.patch`: that tree is the one every published result was produced on, and this patch postdates all of them. Apply it for accurate progress on asynchronous runs; nothing about simulation behavior changes with or without it.

### Reproducing the patched environment

The published results used Concordia at commit `5482bca` (`git describe` → `v2.4.0-28-g5482bca`) plus the two patches above, published as the public fork [**`ngstcf/concordia@5ed8813`**](https://github.com/ngstcf/concordia/commit/5ed88134f7a08f2a13209b2e01bbb70a76d6771f) (branch `v2.4.0-simbuilder`).

**Default — pinned fork (one command).** `requirements.txt` already pins that commit, so a fresh clone reproduces it directly:

```bash
pip install -r requirements.txt   # installs gdm-concordia from ngstcf/concordia@5ed8813
```

**Alternative — local editable install** (e.g. to keep developing against Concordia):

```bash
# Clone, pin the exact commit, apply the patch, install editable:
git clone https://github.com/google-deepmind/concordia concordia-upstream
cd concordia-upstream
git checkout 5482bca            # v2.4.0 + 28 commits — the exact tree this work used
git apply ../patches/concordia-2.4.0-local.patch
pip install -e .               # shadows the pinned PyPI gdm-concordia==2.4.0
```

<details>
<summary>How the fork was produced (provenance)</summary>

```bash
gh repo fork google-deepmind/concordia --fork-name concordia --clone=false
git checkout 5482bca -b v2.4.0-simbuilder
git apply patches/concordia-2.4.0-local.patch
git commit -am "Per-agent activity rates + variable-clock wiring for Concordia Sim Builder"
git push -u fork v2.4.0-simbuilder
```
</details>

## Project Structure

```
concordia-sim-builder/
├── backend/
│   ├── api/
│   │   ├── simulations.py           # API endpoints + analytics
│   │   └── templates/               # 39 template modules (growing over time based on user feedback)
│   ├── models/
│   │   ├── schemas.py               # Pydantic models
│   │   └── llm_wrappers.py          # LLM provider wrappers
│   ├── services/
│   │   ├── simulation_builder.py    # Simulation construction
│   │   ├── simulation_runner.py     # Execution with streaming
│   │   ├── simulation_state.py      # Task state management
│   │   └── llm_factory.py           # LLM provider factory
│   ├── utils/
│   │   ├── log_broadcaster.py       # SSE log broadcaster
│   │   ├── stdout_tee.py            # stdout interceptor for log streaming
│   │   ├── debug_print.py           # Gated debug/LLM print functions
│   │   ├── logger.py                # Centralized backend logging config
│   │   ├── logging_config.py        # Console-output suppression
│   │   ├── event_journal.py         # Durable failure-event journal (logs/events/)
│   │   ├── data_exporter.py         # Structured JSON/CSV export
│   │   ├── grounded_variables_post_processor.py  # Variable-update extraction
│   │   ├── checkpoint_sweep.py      # Decides which checkpoints a sweep may delete
│   │   ├── simulation_analyzer.py   # LLM-powered content analysis
│   │   └── thought_chain_fix.py     # LLM response-parsing repairs
│   ├── tests/                       # Pure unit tests (no network/credentials)
│   └── main.py                      # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SimulationBuilder/   # Builder UI
│   │   │   ├── SimulationRunner/    # Runner UI + 9 analytics tabs
│   │   │   │   ├── LogViewer.tsx    # Live log panel (color-coded)
│   │   │   │   ├── StatisticalDashboard.tsx
│   │   │   │   ├── TimelineVisualization.tsx
│   │   │   │   ├── ActionsView.tsx
│   │   │   │   ├── CooperationChart.tsx
│   │   │   │   ├── GroundedVariablesChart.tsx
│   │   │   │   ├── NaturalLanguageSummary.tsx
│   │   │   │   ├── AnalysisTab.tsx
│   │   │   │   └── ComponentLogs.tsx
│   │   │   └── RecentSimulations/   # Logs browser
│   │   └── utils/
│   │       └── api.ts               # API client
│   └── package.json
├── docs/
│   ├── SIMULATION_BUILDING_GUIDE.md
│   ├── SIMULATION_TEMPLATES_GUIDE.md
│   ├── TIMEOUT_CONFIGURATION.md
│   └── research-use-cases/
│       ├── vaccine-hesitancy-study.md
│       ├── phishing-attack-simulation.md
│       └── urban-gentrification-simulation.md
├── logs/                            # Simulation logs, checkpoints, and events/ journals
├── CHANGELOG.md
└── requirements.txt                 # Python dependencies (gdm-concordia pinned)
```

## Troubleshooting

**ImportError: No module named 'concordia'**
```bash
pip install -r requirements.txt
```

**Ollama timeouts** — Common with local models on slower hardware. Use DeepSeek or OpenAI for reliability.

**Anthropic "temperature is deprecated for this model"** — Handled automatically for Opus 4.7+ models (extended thinking mode rejects temperature).

**CORS errors** — Ensure backend runs on port 8000 and frontend `.env` has correct `VITE_API_URL`.

**Empty analytics tabs on older logs** — Pre-v2.4 logs use a different HTML format. The analytics parser handles both, but some tabs may have limited data.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push and open a Pull Request

### Development Tips

- Templates live in `backend/api/templates/` — one file per template
- Frontend components use React Context for state management
- All simulations auto-save to `logs/` with descriptive filenames
- See [CHANGELOG.md](CHANGELOG.md) for version history and upgrade procedures

## Disclaimer

All agent names, personas, scenarios, and narrative content in the templates and examples are entirely fictional. They are designed for research and educational purposes and do not represent real individuals, organizations, events, or policies. Any resemblance to actual persons, living or dead, or actual events is purely coincidental.

## License

This project uses the [Concordia library](https://github.com/google-deepmind/concordia) (Apache-2.0 license).

Licensed under the Apache 2.0 License — see the LICENSE file for details.

## Citation

If you use this software in your research, please cite the SIMULTECH 2026 paper (published version DOI [10.5220/0014756100004094](https://doi.org/10.5220/0014756100004094); accepted manuscript archived on Zenodo: [10.5281/zenodo.18417283](https://doi.org/10.5281/zenodo.18417283)):

```bibtex
@inproceedings{concordia_sim_builder,
  title={Democratizing AI Social Simulation: A No-Code Web Interface for the Concordia Framework},
  author={Chong, Ng S. T.},
  booktitle={Proceedings of the 16th International Conference on Simulation and
             Modeling Methodologies, Technologies and Applications - SIMULTECH},
  year={2026},
  pages={537--548},
  publisher={SciTePress},
  isbn={978-989-758-857-0},
  doi={10.5220/0014756100004094},
  url={https://github.com/ngstcf/concordia-sim-builder}
}
```

### Artifact Availability

- **Paper:** published version DOI [10.5220/0014756100004094](https://doi.org/10.5220/0014756100004094) (SciTePress); accepted manuscript on Zenodo [10.5281/zenodo.18417283](https://doi.org/10.5281/zenodo.18417283) (concept DOI — always resolves to the latest version).
- **Builder source:** <https://github.com/ngstcf/concordia-sim-builder>
- **Patched Concordia 2.4.0:** [`ngstcf/concordia@5ed8813`](https://github.com/ngstcf/concordia/commit/5ed88134f7a08f2a13209b2e01bbb70a76d6771f) (branch `v2.4.0-simbuilder`), pinned in `requirements.txt` — see [Local Modifications to Concordia](#local-modifications-to-concordia-v240).

## Acknowledgments

- **Google DeepMind** for the [Concordia](https://github.com/google-deepmind/concordia) framework
- **FastAPI** and **React** communities

---

**Built using [Concordia](https://github.com/google-deepmind/concordia) by [Ng Chong](https://github.com/ngstcf) at United Nations University**
