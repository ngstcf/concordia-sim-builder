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

---

**v2.4.1 — Checkpoint Resume** is available on the `feat/resume-from-checkpoint` branch (tag: `v2.4.1`). This version adds mid-run simulation resumption using Concordia's native save/restore API. When a run is interrupted — server restart, network loss, or manual stop — it can be resumed from the nearest saved checkpoint without reloading the template or re-entering LLM settings. The agent state, memories, simulation log, and all configuration are persisted in a `.state.json` sidecar written alongside each checkpoint HTML file.

**Limitations:** resumption is not supported for simulations using `player_specific_context` (formative memory initializer may re-run); step-controller, interview, and survey engines are untested; and `.state.json` sidecars store the API key in plaintext (avoid placing the `logs/` directory in shared or publicly accessible storage).

---

## Sample Simulation Results

Nine completed simulation runs are included in the [`logs/`](logs/) directory, spanning 8 distinct scenarios across 3 Game Master types. Each run was configured and executed entirely through the web interface using different LLM provider combinations.

Each simulation produces three output files:

- **`.html`** — Concordia simulation log (structured entries with full narrative)
- **`.metadata.json`** — Run metadata (agents, LLM config, GM config, timestamps, duration)
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
- **Grounded Variables** — Track simulation state variables with AI-powered post-processing
- **Live Log Streaming** — Real-time terminal output mirrored to frontend via SSE with color-coded messages
- **9-Tab Analytics Dashboard** — Simulation Log, Statistical Dashboard, Timeline, Grounded Variables, Cooperation, Actions, AI Summary, Analysis, Component Logs
- **8 LLM Providers** — OpenAI, Azure OpenAI, DeepSeek, Anthropic, Gemini, GLM, Ollama Local, Ollama Remote
- **Separate GM LLM** — Independent model selection for Game Master
- **Checkpoint System** — Automatic checkpoints with metadata, watchdog emergency saves, scenario-named files
- **Simulation Management** — Mid-run cancellation with LLM-level interrupt (cancels before the next API call, not just between steps), partial results saved, per-simulation delete, server shutdown
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
WATCHDOG_TIMEOUT_SECONDS=600     # Hang detection timeout (default: 600)
WATCHDOG_ENABLED=true            # Set false to disable hang detection

# Console & live log streaming controls
DEBUG_ENABLED=true               # Control [DEBUG] messages
LLM_LOGGING_ENABLED=true         # Control [LLM] API call details

# Frontend
VITE_SIMULATION_TIMEOUT=10800000  # Simulation timeout in ms (default: 3 hours)
```

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
| `/api/simulations/configs` | GET | List saved configurations |
| `/api/simulations/configs` | POST | Save a named configuration |
| `/api/simulations/configs/{slug}` | GET | Load a saved configuration |
| `/api/simulations/configs/{slug}` | DELETE | Delete a saved configuration |

### Simulation Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/status` | GET | Status of all running simulations |
| `/api/simulations/status/{task_id}` | GET | Status of specific simulation |
| `/api/simulations/cancel/{task_id}` | POST | Cancel a running simulation (saves partial results) |
| `/api/simulations/control/{task_id}/pause` | POST | Pause (step controller engine) |
| `/api/simulations/control/{task_id}/resume` | POST | Resume |
| `/api/simulations/control/{task_id}/step` | POST | Advance one step |
| `/api/simulations/control/{task_id}/stop` | POST | Stop |
| `/api/simulations/shutdown` | POST | Shutdown server |

### Logs & Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/recent` | GET | List recent simulation logs |
| `/api/simulations/logs/{filename}` | GET | Get simulation log HTML |
| `/api/simulations/logs/{filename}` | DELETE | Delete simulation log + metadata |
| `/api/simulations/logs/{filename}/analytics` | GET | Analytics data for all 9 result tabs |
| `/api/simulations/logs/checkpoints` | GET | List checkpoint files |
| `/api/simulations/logs/checkpoints` | DELETE | Delete checkpoint files |
| `/api/simulations/logs/config` | GET | Log streaming config (debug/LLM flags) |
| `/api/simulations/logs/stream` | GET | SSE endpoint for live log streaming |

### Analysis & Variables

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/analyze-simulation` | POST | LLM-powered analysis report |
| `/api/simulations/grounded-variables/extract` | POST | Extract variable history from log using AI |
| `/api/simulations/grounded-variables/{simulation_id}` | GET | Get grounded variables data |
| `/api/simulations/formative-memories/generate` | POST | Generate agent backstory |

### Components & Templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/components/templates` | GET | Psychological component templates |
| `/api/simulations/components/validate` | POST | Validate component parameters |
| `/api/simulations/templates/{template-name}` | GET | Get template configuration (38 templates; more are added based on user feedback as the project grows) |

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

> **⚠️ Reproducibility:** the stock PyPI `gdm-concordia==2.4.0` does **not** contain these changes — with the unpatched library, per-agent activity rates are silently ignored (every agent posts on every step) and the Mastodon experiment will not reproduce. `requirements.txt` therefore pins the patched fork above, so `pip install -r requirements.txt` is sufficient.

### What changed and why

**1. `async_social_media__GameMaster` — per-agent stochastic activation** *(material)*

Stock v2.4.0 activates **every** eligible player on **every** step — its next-acting component simply returns all player names, with no notion of posting frequency. The Mastodon influence experiment depends on *differential* posting volume: a malicious actor posting at ~10× the baseline to dominate the feed, with the effect diluting as the honest population grows. That mechanism did not survive Concordia's upstream port of the prefab, so we re-introduced it at the GM level:

- Added `default_activity_rate`, `per_agent_activity_rates`, and `activity_seed` parameters.
- Added probabilistic per-agent sampling in the next-acting component (rate ≤ 1.0 → probability; rate > 1.0 → relative intensity, normalized to the most active agent).
- Seeded the RNG for reproducibility, and guaranteed the engine still advances when no agent is sampled in a step.

This is the GM-level mechanism behind the Builder's **Social Media Activity Model** sliders. Without it, the experiment's central manipulation — influence by posting volume — cannot be expressed.

**2. `simultaneous_resolution_gm__GameMasterSimultaneous` — variable-clock wiring** *(minor)*

The contrib clock already supported variable time increments, but the prefab never forwarded the configuration. The patch threads `use_variable_increments` and `variable_increment_rules` from GM params into the clock, enabling multi-interval / variable-step schedules from the Builder.

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
│   │   └── templates/               # 38 template modules (growing over time based on user feedback)
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
│   │   └── debug_print.py           # Gated debug/LLM print functions
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
├── logs/                            # Simulation logs (see inventory below)
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

If you use this software in your research, please cite the SIMULTECH 2026 paper (accepted manuscript archived on Zenodo: [10.5281/zenodo.18417283](https://doi.org/10.5281/zenodo.18417283)):

```bibtex
@inproceedings{concordia_sim_builder,
  title={Democratizing AI Social Simulation: A No-Code Web Interface for the Concordia Framework},
  author={Chong, Ng S. T.},
  booktitle={Proceedings of the 16th International Conference on Simulation and Modeling Methodologies, Technologies and Applications (SIMULTECH 2026)},
  year={2026},
  organization={INSTICC},
  url={https://github.com/ngstcf/concordia-sim-builder},
  institution={United Nations University}
}
```

### Artifact Availability

- **Paper (accepted manuscript):** Zenodo [10.5281/zenodo.18417283](https://doi.org/10.5281/zenodo.18417283) (concept DOI — always resolves to the latest version).
- **Builder source:** <https://github.com/ngstcf/concordia-sim-builder>
- **Patched Concordia 2.4.0:** [`ngstcf/concordia@5ed8813`](https://github.com/ngstcf/concordia/commit/5ed88134f7a08f2a13209b2e01bbb70a76d6771f) (branch `v2.4.0-simbuilder`), pinned in `requirements.txt` — see [Local Modifications to Concordia](#local-modifications-to-concordia-v240).

## Acknowledgments

- **Google DeepMind** for the [Concordia](https://github.com/google-deepmind/concordia) framework
- **FastAPI** and **React** communities

---

**Built using [Concordia](https://github.com/google-deepmind/concordia) by [Ng Chong](https://github.com/ngstcf) at United Nations University**
