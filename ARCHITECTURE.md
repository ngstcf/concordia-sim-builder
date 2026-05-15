# Concordia Simulation Builder — Architecture

A web-based tool for creating, running, and analyzing multi-agent social simulations using Google DeepMind's Concordia framework.

---

## System Overview

```
Frontend (React + TypeScript + Tailwind)
  │
  │  HTTP API + SSE streams
  ▼
Backend (FastAPI)
  │
  ▼
Concordia Framework (upstream at concordia-upstream/)
```

---

## Backend

### Directory Layout

```
backend/
├── main.py                          # FastAPI entry point, installs stdout tee
├── api/
│   ├── simulations.py               # API router (46 endpoints)
│   └── templates/                   # 39 simulation templates (one file each)
│       ├── __init__.py              # Template registry
│       ├── mastodon_influence_experiment.py
│       ├── peace_negotiation.py
│       ├── puppet_wizard_of_oz.py
│       └── ...
├── services/
│   ├── llm_factory.py               # LLM client factory (8 providers)
│   ├── simulation_builder.py        # Converts config → runnable simulation
│   ├── simulation_runner.py         # Executes simulation, saves results
│   ├── simulation_state.py          # State management & checkpointing
│   ├── batch_runner.py              # Batch execution with parameter sweeps
│   └── census_generator.py          # Distribution-based agent generation
├── prefabs/
│   ├── grounded_variables.py        # Tracks state variables over time
│   ├── nested_simulation.py         # Nested simulations within agents
│   ├── contrib_gm_components.py     # Contrib GM component registry
│   ├── context_aware_scripted.py    # Context-aware scripted entity prefab
│   ├── context_aware_scripted_act.py # Context-aware act component
│   └── reasoning_steps.py           # Reasoning step components
├── models/
│   ├── schemas.py                   # Pydantic models (30+ types)
│   └── llm_wrappers.py             # LLM wrapper utilities
└── utils/
    ├── simulation_analyzer.py       # HTML log → structured analytics
    ├── grounded_variables_post_processor.py  # LLM-powered variable extraction
    ├── data_exporter.py             # CSV/JSON export utilities
    ├── stdout_tee.py                # Transparent stdout interceptor for SSE
    ├── log_broadcaster.py           # Thread-safe SSE log broadcaster
    ├── thought_chain_fix.py         # Chain-of-thought formatting
    ├── logger.py                    # Logger configuration
    ├── logging_config.py            # Log level settings
    └── debug_print.py              # Conditional debug output
```

### Key Schemas (`models/schemas.py`)

**Core simulation:**

| Model | Purpose |
|-------|---------|
| `SimulationConfig` | Full simulation definition (premise, agents, GM, engine, clock) |
| `AgentConfig` | Agent definition (goal, memories, prefab, components, nested_simulation) |
| `GameMasterConfig` | GM prefab, acting order, grounded variables, contrib components, critical decision points, early termination |
| `ClockConfig` | Clock type, start time, increment, variable rules, generative description |
| `VariableConfig` | Grounded variable (type, bounds, update rule) |
| `NestedSimulationConfig` | Nested simulation parameters for agents |
| `ContribComponentConfig` | Contrib GM component configuration |
| `AvailableAction` | Constrained action choices for agents |

**Execution:**

| Model | Purpose |
|-------|---------|
| `LLMSettings` | Provider, model, API key, temperature, max tokens, timeout |
| `ExecutionRequest` | Config + LLM settings + optional separate GM LLM settings |
| `BatchRunRequest` | Config + LLM settings + num_runs + sweep parameters |
| `SweepParameter` | Field path + values for parameter sweep |

**Generation:**

| Model | Purpose |
|-------|---------|
| `PersonaGenerationRequest` | Context, diversity axes, count, LLM settings |
| `FormativeMemoryRequest` | Agent names + context for backstory generation |
| `CensusGenerationRequest` | Demographic distribution spec + enrichment options |
| `CensusDistributionSpec` | Marginal dimensions or joint profiles for census sampling |

**Enums:**

| Enum | Values |
|------|--------|
| `EngineType` | sequential, simultaneous, asynchronous, step_controller, interview, survey |
| `ClockType` | fixed_increment, multi_interval, generative |
| `ActingOrder` | fixed, random, game_master_choice |
| `LLMProvider` | openai, azure, deepseek, gemini, anthropic, glm, ollama, ollama_remote |

### API Endpoints (46 total)

**Templates & Config:**
- `GET /prefabs` — Available agent/GM prefabs (12 entity + 14 GM + 1 initializer)
- `GET /providers` — LLM providers
- `GET /models/{provider}` — Available models
- `GET /components/templates` — Component templates
- `GET /contrib-components` — Contrib GM components
- `POST /components/validate` — Validate component config
- `GET /export-template` — Export simulation config
- `POST /import` — Import simulation config
- `POST /validate` — Validate config (with clock/GM compatibility checks)
- `GET /templates/{slug}` — Per-template endpoints (39, dynamically registered)

**Execution:**
- `POST /execute` — Run simulation (SSE streaming)
- `POST /execute-simple` — Run simulation (simple response)
- `POST /cancel/{task_id}` — Cancel running simulation
- `POST /control/{task_id}/play|pause|step|stop` — Step controller

**Batch Execution:**
- `POST /batch/execute` — Run batch with parameter sweeps (SSE streaming)
- `GET /batch/list` — List batch runs
- `GET /batch/{batch_id}/status` — Batch status
- `POST /batch/{batch_id}/cancel` — Cancel batch
- `GET /batch/{batch_id}/export-csv` — Export batch results as CSV
- `GET /batch/{batch_id}/reliability` — ICC(3,1) reliability analysis

**Results & Analysis:**
- `GET /recent` — Recent simulation list
- `GET /logs/{filename}` — Get simulation log
- `GET /logs/{filename}/analytics` — Extract analytics from HTML
- `GET /logs/{filename}/export-csv` — Export actions/timeline as CSV
- `GET /logs/{filename}/export-json` — Export structured JSON
- `DELETE /logs/{filename}` — Delete simulation
- `GET /logs/checkpoints` — List checkpoints
- `DELETE /logs/checkpoints` — Clean up checkpoints
- `GET /status` / `GET /status/{task_id}` — Simulation status

**Live Logs:**
- `GET /logs/config` — Log panel configuration (debug/LLM enabled flags)
- `GET /logs/stream` — SSE stream of backend terminal output

**Advanced:**
- `POST /grounded-variables/extract` — Extract variables from HTML via LLM
- `GET /grounded-variables/{simulation_id}` — Get variable history
- `POST /analyze-simulation` — LLM-powered simulation analysis
- `POST /generate-formative-memories` — Generate agent backstories
- `POST /generate-personas` — Generate agent personas (diversity axes)
- `POST /generate-personas-census` — Generate agents from demographic distributions
- `POST /upload-distribution` — Upload demographic distribution file
- `POST /parse-distribution` — Parse distribution data

**Saved Configs:**
- `GET /configs` — List saved configurations
- `POST /configs` — Save configuration
- `GET /configs/{slug}` — Get saved config
- `DELETE /configs/{slug}` — Delete saved config

### Templates

Each template is a Python file in `backend/api/templates/` exporting a `TEMPLATE` dict. Templates are explicitly imported and registered in `__init__.py`, then `simulations.py` loops over the registry to create `GET /templates/{slug}` endpoints via `router.add_api_route()`.

39 templates across 7 categories: Quick Start, Prefab Demos, Research, SDG Scenarios, Advanced, General Scenarios, Upstream Examples. See the [Simulation Templates Guide](docs/SIMULATION_TEMPLATES_GUIDE.md) for the full list.

### Live Log Streaming

`stdout_tee.py` wraps `sys.stdout` to intercept all `print()` output (including Concordia engine internals). Each line is categorized (SYSTEM, DEBUG, LLM), stripped of ANSI codes, and broadcast via `log_broadcaster.py` to SSE subscribers. The frontend receives entries at `GET /logs/stream` and color-codes them by 13 message categories in `LogViewer.tsx`.

---

## Frontend

### Directory Layout

```
frontend/src/
├── components/
│   ├── SimulationBuilder/
│   │   ├── SimulationBuilder.tsx      # Main builder form
│   │   ├── TemplatePicker.tsx         # Template search, filter, sort
│   │   ├── templateMetadata.ts        # Template tags, categories, feature flags
│   │   ├── AgentEditor.tsx            # Agent CRUD with component config
│   │   ├── AgentList.tsx              # Agent list display
│   │   ├── AvailableActionsEditor.tsx # Constrained action choices editor
│   │   ├── GameMasterConfig.tsx       # GM config, activity rates, contrib components
│   │   ├── ScenarioConfig.tsx         # Premise, clock config, engine type
│   │   ├── SceneEditor.tsx            # Scene editing for dramaturgic GMs
│   │   ├── PlayerContextEditor.tsx    # Per-agent private context
│   │   └── QuestionnaireBuilder.tsx   # Survey/questionnaire builder
│   ├── SimulationRunner/
│   │   ├── SimulationRunner.tsx       # Main runner with 9 result tabs
│   │   ├── RecentSimulations.tsx      # Browse past simulations
│   │   ├── BatchRunner.tsx            # Batch execution with parameter sweeps
│   │   ├── LogViewer.tsx              # Color-coded live log panel with legend
│   │   ├── ActionsView.tsx            # Per-agent action timeline
│   │   ├── TimelineVisualization.tsx  # Event timeline
│   │   ├── GroundedVariablesChart.tsx # Variable time-series charts
│   │   ├── CooperationRateChart.tsx   # Game-theoretic metrics
│   │   ├── StatisticalDashboard.tsx   # Component statistics
│   │   ├── NaturalLanguageSummary.tsx # AI-generated markdown summary
│   │   └── SimulationAnalysis.tsx     # LLM-powered deep analysis
│   └── shared/
│       ├── JsonImportExport.tsx       # Import/export configs
│       └── MemoryEditor.tsx           # Shared memory editor
├── types/
│   └── simulation.ts                  # TypeScript types (mirrors schemas.py)
├── utils/
│   └── api.ts                         # API client (fetch wrappers, SSE handlers)
├── App.tsx
└── main.tsx
```

### SimulationRunner Tabs

| Tab | Component | Description |
|-----|-----------|-------------|
| log | (iframe) | Raw HTML simulation output |
| statistics | StatisticalDashboard | Component metrics and state |
| timeline | TimelineVisualization | Step-by-step event timeline |
| actions | ActionsView | Per-agent action history |
| summary | NaturalLanguageSummary | AI-generated markdown summary |
| grounded-variables | GroundedVariablesChart | Variable time-series charts |
| cooperation | CooperationRateChart | Cooperation/defection rates |
| analysis | SimulationAnalysis | LLM-powered deep analysis |
| measurements | (inline) | Component measurement logs |

### UI Features

- Collapsible left sidebar for simulation browsing
- Template picker with search, tag filtering, and category sorting
- Separate LLM provider/model selection for agents and GM
- Clock configuration (3 types: fixed increment, multi-interval, generative)
- Async social media activity rate controls (per-agent rates, seed)
- Batch runner with parameter sweeps and CSV export
- Results metadata display (provider, model, duration)
- Early termination toggle
- Live log streaming with 13 color-coded message categories and toggleable legend
- Markdown rendering (ReactMarkdown + remark-gfm) in summaries
- JSON import/export for simulation configs
- Census-based agent generation from demographic distributions

---

## Key Subsystems

### Grounded Variables

Tracks simulation state variables (numerical, percentage, boolean, categorical) over time. Uses LLM to detect when events should trigger variable changes.

Flow: simulation step completes → `GroundedVariablesComponent.post_act(event)` → LLM analyzes event → validates against constraints → updates history.

Variables only change on explicit action verbs (VOTE, ENACT, APPROVE), not discussion verbs (advocate, propose, discuss).

### Critical Decision Points

Explicit policy events injected at specific simulation steps to force variable changes. Defined in template config under `game_master.critical_decision_points`, appended to the simulation premise at build time.

### Clock Configuration

Three clock types routed through `SimulationConfig.clock`:
- **FixedIncrementClock** — Fixed step size (1–1440 minutes), passed as `time_period_minutes` to GM params
- **MultiIntervalClock** — Hour-based variable increments, passed as `variable_increment_rules` + `use_variable_increments=True`
- **GenerativeClock** — LLM-managed time, passed as `clock_description`

Builder validates clock/GM compatibility and warns on mismatches.

### Stochastic Agent Activation

The `async_social_media__GameMaster` supports per-agent activity rates via GM parameters (`default_activity_rate`, `per_agent_activity_rates`, `activity_seed`). Rates <=1.0 are probabilities; rates >1.0 are relative intensity weights. The GM handles stochastic sampling internally.

### Batch Execution

`batch_runner.py` manages N simulation runs with optional parameter sweeps over temperature, max_steps, or other fields. Results stream as SSE events. When runs include questionnaire metadata (interviewer GM), ICC(3,1) inter-rater reliability is computed per dimension via `GET /batch/{id}/reliability`.

### Nested Simulations

Agents can run inner simulations to reason about strategy. Configured via `AgentConfig.nested_simulation`.

### Puppet Agents

Wizard-of-Oz agents whose responses are pre-configured via `fixed_responses` mapping (call-to-action → response). No runtime input mechanism — responses are set before simulation starts. Unmatched actions fall back to LLM.

---

## Running

```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

Results saved to `logs/` as HTML + `.metadata.json` sidecar files.

---

Last Updated: 2026-05-16
