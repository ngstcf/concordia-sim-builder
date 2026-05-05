# Concordia Simulation Builder

A web interface for Google DeepMind's [Concordia](https://github.com/google-deepmind/concordia) library that makes running agent-based social simulations accessible—no Python programming required.

Configure agents, psychological components, and scenarios through forms. Run simulations powered by LLMs. Analyze results with built-in analytics including timeline visualization, cooperation metrics, grounded variables tracking, and AI-powered deep content analysis.

![Simulation Builder](https://img.shields.io/badge/Concordia-Simulation%20Builder-blue)
![Version](https://img.shields.io/badge/Version-2.4.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

**Documentation:** [c3.unu.edu/projects/ai/simulator/v2.4.html](https://c3.unu.edu/projects/ai/simulator/v2.4.html)

**Guides:**
- [Simulation Building Guide](docs/SIMULATION_BUILDING_GUIDE.md) — Practitioner guide for creating simulations, configuring agents, components, and engines
- [Simulation Templates Guide](docs/SIMULATION_TEMPLATES_GUIDE.md) — Practitioner guide for all 32 templates with research setups and experiment suggestions
- [Template Creation Guide](docs/TEMPLATE_CREATION_GUIDE.md) — Developer guide for adding new simulation templates
- [Timeout Configuration](docs/TIMEOUT_CONFIGURATION.md) — Tuning LLM, watchdog, and frontend timeouts

**Research Use Cases:**
- [Vaccine Hesitancy Study](docs/research-use-cases/vaccine-hesitancy-study.md)
- [Phishing Attack Simulation](docs/research-use-cases/phishing-attack-simulation.md)
- [Urban Gentrification Simulation](docs/research-use-cases/urban-gentrification-simulation.md)

## Sample Simulation Results

Seven completed simulation runs are included in the [`logs/`](logs/) directory, spanning peace negotiation, game theory, disaster response, and SDG-aligned scenarios. Each run was configured and executed entirely through the web interface using different LLM provider combinations.

Each simulation produces three output files:

- **`.html`** — Concordia simulation log (structured entries with full narrative)
- **`.metadata.json`** — Run metadata (agents, LLM config, GM config, timestamps, duration)
- **`_analysis.md`** — LLM-powered analysis report (executive summary, effectiveness assessment, insights, recommendations)

| # | Scenario | Agents | Agent LLM | GM LLM | Duration |
|---|----------|--------|-----------|--------|----------|
| 1 | **Peace Negotiation** — Russia-Ukraine talks at Istanbul, Jan 2026 | 2 (Agent R, Agent U) | DeepSeek V4 Flash | Claude Sonnet 4.6 | 29 min |
| 2 | **Strategic Game** — Prisoner's Dilemma behavioral economics experiment | 2 (Alex, Sam) | OpenAI O3-Mini | Claude Sonnet 4.6 | 3 min |
| 3 | **Flood Evacuation** — Coastal town Category 3 hurricane response (SDG 11/13) | 5 (Sarah Williams, Robert Thompson, Javier Rodriguez, Eleanor O'Brien, Pastor Moses) | DeepSeek V4 Flash | GPT-5.5 | 57 min |
| 4 | **Software Team** — Fintech startup payment processing sprint | 3 (Project Manager, Senior Developer, Junior Developer) | GPT-5.4 Mini | Claude Opus 4.7 | 49 min |
| 5 | **Conversational Debate** — AI tutors vs human teachers roundtable | 3 (Dr. Chen, Mr. Patel, Ms. Jackson) | Claude Haiku 4.5 | GPT-5.5 | 7 min |
| 6 | **Labor Strike** — Collective action and wage negotiation (SDG 8) | 4 (Elena Vasquez, David Kim, Amina Johnson, Richard Sterling) | DeepSeek V4 Flash | GPT-5.5 | 73 min |
| 7 | **Fishery Management** — Tragedy of the commons in marine resources (SDG 14) | 4 (Hiroshi Tanaka, Maria Santos, Okonkwo Nnamdi, Dr. Lisa Chen) | OpenAI O3-Mini | GPT-5 | 133 min |

## Features

- **Form-Based Configuration** — Intuitive web UI for building agent-based simulations without coding
- **32 Simulation Templates** — Pre-built scenarios covering peace negotiation, game theory, SDG research, cybersecurity, and more (see [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md))
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
- **Simulation Management** — Mid-run cancellation with partial results, per-simulation delete, server shutdown
- **Import/Export** — Save and share simulation configurations as JSON

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

- Python 3.10 or higher
- Node.js 18 or higher
- API keys for at least one LLM provider (OpenAI, DeepSeek, Gemini, or Anthropic), OR Ollama for local models

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/ngstcf/concordia-sim-builder.git
cd concordia-sim-builder

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies (includes pinned gdm-concordia 2.4.0)
pip install -r requirements.txt
```

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

## Templates (32)

| Category | Templates |
|----------|-----------|
| **Quick Start** | Coffee Shop Demo (5 steps), Peace Negotiation (20 steps) |
| **Prefab Demos** | Planning Agent, Scripted Entity, Context-Aware Moderator, Dialogic Conversation |
| **Game Theory** | Strategic Game (Prisoner's Dilemma), Marketplace, Sealed-Bid Auction |
| **SDG Research** | State Formation (16), Labor Action (8), Fishery Management (14), Disaster Response (11/13), Inequality Mobility (10) |
| **Research** | Vaccine Hesitancy, Urban Gentrification, Phishing Attack |
| **v2.4 Features** | Hostage Negotiation (step controller), Colony Survival (contrib GM), Bookstore Reunion (formative memories), Clinical Trial Ethics (measurements), Diplomatic Crisis (nested sim) |
| **Advanced** | Rational Negotiators, Social Media, Puppet, Conversational Debate, Spaceship Crisis, AI Policy Red Team |

See [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md) for detailed parameter documentation and research guides for all templates.

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
| `/api/simulations/export-template` | GET | Get blank configuration template |
| `/api/simulations/import` | POST | Import configuration from JSON |

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
| `/api/simulations/templates/{template-name}` | GET | Get template configuration (32 templates) |

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

## Project Structure

```
concordia-sim-builder/
├── backend/
│   ├── api/
│   │   ├── simulations.py           # API endpoints + analytics
│   │   └── templates/               # 26 template modules
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

## License

This project uses the [Concordia library](https://github.com/google-deepmind/concordia) (Apache-2.0 license).

Licensed under the Apache 2.0 License — see the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

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

## Acknowledgments

- **Google DeepMind** for the [Concordia](https://github.com/google-deepmind/concordia) framework
- **FastAPI** and **React** communities

---

**Built using [Concordia](https://github.com/google-deepmind/concordia) by [Ng Chong](https://github.com/ngstcf) at United Nations University**
