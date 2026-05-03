# Concordia Simulation Builder — Architecture

A web-based tool for creating, running, and analyzing multi-agent social simulations using Google DeepMind's Concordia framework (v2.4).

---

## System Overview

```
Frontend (React + TypeScript + Tailwind)
  │
  │  HTTP API
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
├── main.py                          # FastAPI entry point
├── api/
│   ├── simulations.py               # API router & endpoints
│   └── templates/                   # 31 simulation templates (one file each)
│       ├── __init__.py
│       ├── urban_gentrification.py
│       ├── peace_negotiation.py
│       ├── puppet_wizard_of_oz.py
│       └── ...
├── services/
│   ├── llm_factory.py               # LLM client factory (multi-provider)
│   ├── simulation_builder.py        # Converts config → runnable simulation
│   ├── simulation_runner.py         # Executes simulation, saves results
│   └── simulation_state.py          # State management & checkpointing
├── prefabs/
│   ├── grounded_variables.py        # Tracks state variables over time
│   ├── nested_simulation.py         # Nested simulations within agents
│   ├── contrib_gm_components.py     # Contrib GM component registry
│   ├── context_aware_scripted.py    # Context-aware scripted agents
│   └── reasoning_steps.py           # Reasoning step components
├── models/
│   ├── schemas.py                   # Pydantic models
│   └── llm_wrappers.py             # LLM wrapper utilities
└── utils/
    ├── simulation_analyzer.py       # HTML log → structured analytics
    ├── grounded_variables_post_processor.py
    ├── logger.py / logging_config.py
    └── debug_print.py
```

### Key Schemas (`models/schemas.py`)

| Model | Purpose |
|-------|---------|
| `SimulationConfig` | Full simulation definition (premise, agents, GM, engine) |
| `AgentConfig` | Agent definition (goal, memories, prefab, nested_simulation) |
| `GameMasterConfig` | GM prefab, acting order, grounded variables, contrib components, critical decision points, early termination |
| `VariableConfig` | Grounded variable (type, bounds, update rule) |
| `LLMSettings` | Provider, model, API key, temperature, max tokens |
| `ExecutionRequest` | Config + LLM settings + optional separate GM LLM settings |
| `NestedSimulationConfig` | Nested simulation parameters for agents |
| `ContribComponentConfig` | Contrib GM component configuration |

### LLM Providers (`LLMProvider` enum)

OpenAI, Azure, DeepSeek, Gemini, Anthropic, Ollama, Ollama Remote, GLM (Zhipu AI)

### Engine Types (`EngineType` enum)

| Type | Use Case |
|------|----------|
| `sequential` | Default turn-based execution |
| `simultaneous` | All agents act at once per step |
| `asynchronous` | Agents act independently |
| `step_controller` | Pause/resume/step-through control |
| `interview` | Interviewer-interviewee format |
| `survey` | Questionnaire-based |

### API Endpoints

**Templates & Config:**
- `GET /prefabs` — Available agent/GM prefabs
- `GET /providers` — LLM providers
- `GET /models/{provider}` — Available models (with OpenAI filtering)
- `GET /components/templates` — Component templates
- `GET /contrib-components` — Contrib GM components
- `GET /export-template` — Export simulation config
- `POST /import` — Import simulation config
- `POST /validate` — Validate config
- `POST /components/validate` — Validate component config

**Execution:**
- `POST /execute` — Run simulation (streaming)
- `POST /execute-simple` — Run simulation (simple)
- `POST /cancel/{task_id}` — Cancel running simulation
- `POST /control/{task_id}/play|pause|step|stop` — Step controller

**Results & Analysis:**
- `GET /recent` — Recent simulation list
- `GET /logs/{filename}` — Get simulation log
- `GET /logs/{filename}/analytics` — Extract analytics from HTML
- `DELETE /logs/{filename}` — Delete simulation
- `GET /logs/checkpoints` — List checkpoints
- `DELETE /logs/checkpoints` — Clean up checkpoints
- `GET /status` / `GET /status/{task_id}` — Simulation status

**Advanced:**
- `POST /grounded-variables/extract` — Extract variables from HTML
- `GET /grounded-variables/{simulation_id}` — Get variable history
- `POST /analyze-simulation` — LLM-powered simulation analysis
- `POST /generate-formative-memories` — Generate agent backstories
- `POST /generate-personas` — Generate agent personas

### Templates

Each template is a Python file in `backend/api/templates/` exporting a `TEMPLATE` dict. Templates are explicitly imported and registered in `__init__.py`, then `simulations.py` loops over the registry to create `GET /templates/{slug}` endpoints via `router.add_api_route()`.

31 templates covering: game theory, social dynamics, policy simulation, cybersecurity, strategy games, demos (step controller, nested sims, measurements, formative memories, contrib components).

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
│   │   ├── AgentEditor.tsx            # Agent CRUD
│   │   ├── AgentList.tsx              # Agent list display
│   │   ├── GameMasterConfig.tsx       # GM configuration
│   │   ├── ScenarioConfig.tsx         # Scenario/premise editor
│   │   ├── SceneEditor.tsx            # Scene editing
│   │   ├── PlayerContextEditor.tsx    # Player context config
│   │   └── QuestionnaireBuilder.tsx   # Survey/questionnaire builder
│   ├── SimulationRunner/
│   │   ├── SimulationRunner.tsx       # Main runner with 9 tabs
│   │   ├── RecentSimulations.tsx      # Browse past simulations
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
├── utils/
│   ├── api.ts                         # API client
│   └── types.ts                       # TypeScript types
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
- Results metadata display (provider, model, duration)
- Early termination toggle
- Markdown rendering (ReactMarkdown + remark-gfm) in summaries
- JSON import/export for simulation configs

---

## Key Subsystems

### Grounded Variables

Tracks simulation state variables (numerical, percentage, boolean, categorical) over time. Uses LLM to detect when events should trigger variable changes.

Flow: simulation step completes → `GroundedVariablesComponent.post_act(event)` → LLM analyzes event → validates against constraints → updates history.

Variables only change on explicit action verbs (VOTE, ENACT, APPROVE), not discussion verbs (advocate, propose, discuss).

### Critical Decision Points

Explicit policy events injected at specific simulation steps to force variable changes. Defined in template config under `game_master.critical_decision_points`, appended to the simulation premise at build time.

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

Last Updated: 2026-05-03
