# Concordia Simulation Builder — Full Reference

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
- [Simulation Templates Guide](docs/SIMULATION_TEMPLATES_GUIDE.md) — Practitioner guide for all 31 templates with research setups and experiment suggestions

> This is the extended reference. For a concise overview, see [README.md](README.md).

## Features

### Simulation Building
- **Form-Based Configuration** — Build agent-based simulations without coding
- **31 Simulation Templates** — Pre-built scenarios across research, game theory, SDG policy, and more
- **Multi-Agent System** — Unique goals, memories, psychological components, and behavioral prefabs per agent
- **Psychological Components** — Personality, cognitive bias, social identity, emotions, values, Theory of Planned Behavior
- **Agent Editor** — Drag-to-reorder, duplicate, prefab badges, component count display, grouped component dropdown
- **Scene Editor** — Visual scene configuration with questionnaire builder
- **Persona Generator** — Generate agent backstories from formative memories
- **Searchable Template Picker** — Filter, sort, search by agent names and keywords
- **Import/Export** — Save and share simulation configurations as JSON

### Simulation Engines
- **Sequential** — Agents act one at a time in fixed order
- **Asynchronous** — Agents act concurrently
- **Simultaneous** — All agents act at once per step
- **Step Controller** — Interactive play/pause/step/stop control with per-step action log

### Game Master
- **8 GM Prefabs** — Generic, dialogic, game-theoretic, interviewer, marketplace, psychology experiment, scripted, formative memories initializer
- **5 Contrib GM Components** — Death, GMWorkingMemory, NpcEventGenerator, LocationBasedFilter, SpaceshipSystem
- **Separate GM LLM** — Independent model selection via UI toggle or `.env` fallback (`GM_LLM_PROVIDER`, `GM_LLM_MODEL`)
- **Early Termination** — Toggle `can_terminate_simulation` flag per simulation

### Agent Capabilities
- **Formative Memories** — Standalone endpoint with Generate Backstory button in agent editor
- **Measurements** — Inject into any engine with Component Logs tab in results
- **Nested Simulations** — PhoneGameMaster pattern for running mini-simulations within agent pre_act
- **Player-Specific Context** — Per-agent context editor
- **Custom Reasoning Steps** — Configurable reasoning pipeline
- **Emotional Stance** — Emotional state component

### Execution & Monitoring
- **Real-time SSE Streaming** — Step-by-step progress with elapsed time and ETA
- **Live Log Streaming** — Terminal output mirrored to frontend via stdout tee interceptor
- **Color-Coded Log Messages** — Observations (cyan), actions (emerald), warnings (yellow), watchdog (orange), analyzer (purple), progress (amber), completions (green), LLM calls (blue)
- **Two Log Panels** — Main Log (system + debug) and separate LLM Log panel
- **Mid-Run Cancellation** — Step callbacks check `should_cancel`, saves partial results
- **Configurable Checkpoint Interval** — 1-100 steps (default 5) with UI control
- **Checkpoint Metadata** — Agents, LLM info, premise saved alongside every checkpoint
- **Scenario-Named Checkpoints** — All checkpoint types include agent names and premise in filename
- **Watchdog Monitoring** — Detects hung simulations, saves emergency checkpoints

### Analytics (9 Tabs)
1. **Simulation Log** — Full HTML output with agent interactions
2. **Statistical Dashboard** — Metrics, agent activity, text statistics
3. **Timeline** — Step-by-step event visualization
4. **Grounded Variables** — AI-powered variable history extraction and charting
5. **Cooperation** — Cooperation rate tracking for game-theoretic simulations
6. **Actions** — Per-agent action breakdown with extracted goals
7. **AI Summary** — Agent overview table, participation imbalance, per-phase timeline
8. **Analysis** — LLM-powered deep content analysis with anti-fabrication guardrails
9. **Component Logs** — Measurement outputs per component

### LLM Providers (8)

| Provider | Notes |
|----------|-------|
| **OpenAI** | GPT-4o, GPT-5, O3; filtered model list (drops below GPT-4, preview, audio, etc.) |
| **Azure OpenAI** | Enterprise-grade with data residency |
| **DeepSeek** | v4 models |
| **Anthropic** | Claude Sonnet, Opus; auto-skips temperature for Opus 4.7+ (extended thinking) |
| **Gemini** | Google Gemini 1.5/2.0 |
| **GLM** | GLM-5.1, GLM-5, GLM-4.7 |
| **Ollama Local** | Local models, no API key required |
| **Ollama Remote** | Hosted Ollama with `OLLAMA_BASE_URL` and `OLLAMA_API_KEY` |

- Default max tokens: 9000
- LLM activity tracker and watchdog integration for call monitoring
- `llm_print()` across all providers (respects `LLM_LOGGING_ENABLED`)
- Automatic parameter handling for reasoning models (O3, GPT-5: `max_completion_tokens`, no `temperature`)

## Use Cases

- **Social Science Research** — Model complex social interactions with psychological realism
- **Policy Simulation** — Test SDG-aligned scenarios (peace, labor, fisheries, disaster response, inequality)
- **Game Theory** — Iterated games with payoff tracking and cooperation analytics
- **Cybersecurity** — Tabletop exercises with nested adversarial simulations
- **Education** — Teach negotiation, conflict resolution, and social dynamics
- **Urban Planning** — Gentrification dynamics with grounded variable tracking
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

# Azure OpenAI (optional)
AZURE_OAI_KEY=xxx
AZURE_OAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OAI_VERSION=2024-12-01-preview

# Separate GM LLM (optional — defaults to agent LLM if not set)
# GM_LLM_PROVIDER=openai
# GM_LLM_MODEL=gpt-4o

# Ollama (optional)
# OLLAMA_BASE_URL=http://localhost:11434/v1    # Local or remote endpoint
# OLLAMA_API_KEY=your-key-for-remote           # Only for remote/authenticated

# Timeouts
LLM_TIMEOUT=180                  # Per-request timeout in seconds (default: 180)
LLM_REASONING_TIMEOUT=300        # Timeout for reasoning models like O3 (default: 300)
LLM_MAX_RETRIES=2                # Retry attempts (default: 2)
WATCHDOG_TIMEOUT_SECONDS=600     # Hang detection timeout (default: 600)
WATCHDOG_ENABLED=true            # Set false to disable hang detection

# Console & live log streaming controls
DEBUG_ENABLED=true               # Control [DEBUG] messages in terminal and frontend
LLM_LOGGING_ENABLED=true         # Control [LLM] API call details in terminal and frontend

# Frontend
VITE_SIMULATION_TIMEOUT=10800000  # Simulation timeout in ms (default: 3 hours)
```

### Using Ollama (Local Models)

For local simulations without API costs using [Ollama](https://ollama.com):

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Start
ollama serve
```

In the web UI, select "Ollama (Local)" as the provider and enter the model name. No API key required for local Ollama.

**Performance notes:**
- 8GB+ RAM for 7B models, 16GB+ recommended for larger
- GPU optional but significantly improves speed
- Timeouts common on slower hardware — use DeepSeek or OpenAI for reliability

**Remote/hosted Ollama** (e.g., OpenWebUI): Set `OLLAMA_BASE_URL` and `OLLAMA_API_KEY` in `.env`, then select "Ollama (Remote)" in the UI.

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

## Usage Guide

### 1. Building a Simulation

1. **Set the Premise** — Describe the scenario and setting
2. **Configure Parameters**
   - **Max Steps**: Rounds of action (each agent acts once per step)
   - **Checkpoint Interval**: Save partial results every N steps (default: 5)
   - **Engine Type**: Sequential, asynchronous, simultaneous, or step controller
3. **Add Agents**
   - Set name, goal, and initial memories
   - Choose a prefab (e.g., `basic__Entity`, `basic_with_plan__Entity`)
   - Add psychological components (personality, cognitive bias, social identity, etc.)
   - Optionally generate backstory with formative memories
4. **Configure Game Master**
   - Choose GM prefab and acting order
   - Optionally enable separate GM LLM
   - Add contrib GM components if needed
   - Configure early termination toggle
5. **Add Shared Memories** — Context known to all agents
6. **Configure Grounded Variables** — State variables to track (optional)

### 2. Running a Simulation

1. Navigate to the **Runner** tab
2. Configure LLM settings (provider, model, temperature, request timeout)
3. Click **"Run Simulation"**
4. Monitor progress:
   - Progress bar with step count, elapsed time, and ETA
   - **Live Logs** panel: color-coded terminal output in real time
   - Step controller toolbar (if using step controller engine)
5. View results across 9 analytics tabs
6. Download HTML logs or analysis reports

### 3. Using Templates

See [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md) for detailed parameter documentation, research guides, and experiment suggestions for all 31 templates.

| Category | Templates |
|----------|-----------|
| **Quick Start** | Coffee Shop Demo (5 steps), Peace Negotiation (20 steps) |
| **Prefab Demos** | Planning Agent, Scripted Entity, Context-Aware Moderator, Dialogic Conversation |
| **Game Theory** | Strategic Game (Prisoner's Dilemma), Marketplace, Sealed-Bid Auction |
| **SDG Research** | State Formation (16), Labor Action (8), Fishery Management (14), Disaster Response (11/13), Inequality Mobility (10) |
| **Research** | Vaccine Hesitancy, Urban Gentrification, Phishing Attack |
| **v2.4 Feature Demos** | Hostage Negotiation (step controller), Colony Survival (contrib GM), Bookstore Reunion (formative memories), Clinical Trial Ethics (measurements), Diplomatic Crisis (nested sim) |
| **Advanced** | Rational Negotiators, Social Media, Puppet, Conversational Debate, Spaceship Crisis, Nested Simulation Demo, Grounded Variables Demo |

### 4. Simulation Analyzer

LLM-powered deep content analysis generating comprehensive reports.

**Available via:**
- **Web UI**: Analysis tab in results page
- **Web API**: `POST /api/simulations/analyze-simulation`
- **CLI**: `python backend/scripts/analyze_simulation.py <log_path>`

**Report sections:** Executive summary, timeline analysis, agent effectiveness, key insights, recommendations. Reports use full simulation metadata (agents, goals, components, grounded variables, game-theoretic scores) for context-aware analysis with anti-fabrication guardrails.

### Configuring Game-Theoretic Simulations

For `game_theoretic_and_dramaturgic__GameMaster` (Prisoner's Dilemma, Marketplace):

- `max_steps` = number of game rounds
- `num_rounds` in scene parameters must equal `max_steps`
- Total individual actions = `num_rounds` x participants

Scene `premise` must be a **dictionary** mapping each participant to their context:

```json
{
  "premise": {
    "Agent1": ["Context specific to Agent1"],
    "Agent2": ["Context specific to Agent2"]
  }
}
```

Using a string instead of a dictionary causes: `TypeError: string indices must be integers, not 'str'`

### Checkpointing and Hang Prevention

**Automatic Checkpointing:**
- Partial results saved every N steps (configurable, default 5)
- Checkpoint files: `{timestamp}_{agents}_{premise}_checkpoint_step{N}.html`
- Companion `.metadata.json` saved with agents, LLM info, premise
- Analyzable in Results page with all 9 tabs

**Emergency Checkpoints:**
- Post-completion: saved before HTML post-processing as a safety net
- Watchdog: saved when simulation is detected as hung
- Both include scenario context in filename and metadata

**Watchdog Monitoring:**
- Detects no progress for configurable timeout (default: 10 minutes)
- Saves emergency checkpoint and warns, but does not kill the simulation
- Configurable via `WATCHDOG_TIMEOUT_SECONDS`, disable with `WATCHDOG_ENABLED=false`

**Per-Request Timeout:**
- Standard models: 180s (configurable via `LLM_TIMEOUT`)
- Reasoning models (O3, GPT-5): 300s (configurable via `LLM_REASONING_TIMEOUT`)
- System waits full timeout before flagging error

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
| `/api/simulations/cancel/{task_id}` | POST | Cancel (saves partial results) |
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
| `/api/simulations/templates/{template-name}` | GET | Get template configuration (31 templates) |

## Supported Prefabs

### Entity Prefabs (Agents)

| Prefab | Description | Best For |
|--------|-------------|----------|
| `basic__Entity` | Standard agent with "three key questions" decision framework | Most scenarios |
| `basic_with_plan__Entity` | Adds strategic planning with time horizons | Complex coordination |
| `basic_scripted__Entity` | Follows predefined scripts exactly | Testing, demonstrations |
| `context_aware_scripted__Entity` | Adapts script to context, auto-closes when exhausted | Natural moderators |
| `minimal__Entity` | Simplified decision-making | Lightweight simulations |
| `fake_assistant_with_configurable_system_prompt__Entity` | AI assistant with custom system prompt | Simulating AI personas |

### Game Master Prefabs

| Prefab | Description | Best For |
|--------|-------------|----------|
| `generic__GameMaster` | Standard narrative control | Most simulations |
| `dialogic__GameMaster` | Conversation-focused with auto-termination | Dialogue scenarios |
| `dialogic_and_dramaturgic__GameMaster` | Enhanced dialogue with dramatic structure | Rich conversations |
| `game_theoretic_and_dramaturgic__GameMaster` | Matrix games with payoffs/scores | Strategic games |
| `interviewer__GameMaster` | Administers questionnaires | Surveys, interviews |
| `psychology_experiment__GameMaster` | Experimental protocols | Research scenarios |
| `scripted__GameMaster` | Follows predetermined narrative | Controlled storytelling |
| `marketplace__GameMaster` | Economic trading systems | Market simulations |

### Initializer Prefabs

| Prefab | Description |
|--------|-------------|
| `formative_memories_initializer__GameMaster` | Creates character backgrounds from `player_specific_context` before main simulation |

## Configuration Examples

### Simple Coffee Shop Encounter

```json
{
  "premise": "Alice meets Bob at a coffee shop on Monday morning.",
  "max_steps": 5,
  "agents": [
    {
      "name": "Alice",
      "goal": "Find out what Bob is working on",
      "prefab": "basic__Entity",
      "memories": ["Alice is friendly and curious"]
    },
    {
      "name": "Bob",
      "goal": "Finish work with minimal distractions",
      "prefab": "basic__Entity",
      "memories": ["Bob has a deadline"]
    }
  ]
}
```

### Complex Negotiation with Components

```json
{
  "premise": "Peace negotiation between two conflicting parties.",
  "max_steps": 20,
  "checkpoint_interval": 5,
  "agents": [
    {
      "name": "Party A Representative",
      "goal": "Secure territorial recognition",
      "prefab": "basic__Entity",
      "memories": ["Territory is non-negotiable core interest"],
      "components": [
        {"type": "personality", "params": {"traits": "assertive, analytical"}},
        {"type": "cognitive_bias", "params": {"bias_type": "anchoring"}}
      ]
    },
    {
      "name": "Party B Representative",
      "goal": "Restore territorial integrity",
      "prefab": "basic__Entity",
      "memories": ["Sovereignty must be fully restored"]
    }
  ],
  "shared_memories": ["International observers are present", "Media is watching"]
}
```

## LLM Integration Architecture

The Simulation Builder includes a custom multi-provider LLM integration layer instead of using Concordia's built-in `GptLanguageModel`.

**Why custom?** Concordia's `GptLanguageModel` only supports OpenAI's API. Our implementation adds:

1. **Cost Optimization** — DeepSeek (10-50x cheaper than GPT-4), Ollama (free local), Azure (enterprise pricing)
2. **Geographic & Compliance Flexibility** — Azure data residency, Ollama air-gapped operation
3. **Model-Specific Handling** — O3/GPT-5 parameter detection, Opus 4.7+ temperature skip, generous token limits
4. **Production Reliability** — Provider fallback, retry logic, actionable error messages, `llm_print()` logging

```
backend/models/llm_wrappers.py     # 8 provider-specific wrappers
backend/services/llm_factory.py    # Factory pattern for provider selection
backend/models/schemas.py          # LLMSettings with provider-specific fields
```

## Project Structure

```
concordia-sim-builder/
├── backend/
│   ├── api/
│   │   ├── simulations.py           # API endpoints + analytics
│   │   └── templates/               # 26 template modules (auto-registered)
│   ├── models/
│   │   ├── schemas.py               # Pydantic models
│   │   └── llm_wrappers.py          # LLM provider wrappers
│   ├── services/
│   │   ├── simulation_builder.py    # Simulation construction
│   │   ├── simulation_runner.py     # Execution with streaming + checkpoints
│   │   ├── simulation_state.py      # Task state management
│   │   └── llm_factory.py           # LLM provider factory
│   ├── utils/
│   │   ├── log_broadcaster.py       # SSE log broadcaster singleton
│   │   ├── stdout_tee.py            # stdout interceptor for log streaming
│   │   └── debug_print.py           # Gated debug/LLM print functions
│   └── main.py                      # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SimulationBuilder/   # Builder UI (agent editor, scene editor, etc.)
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
│   │   │   └── RecentSimulations/   # Logs browser with delete
│   │   └── utils/
│   │       └── api.ts               # API client + log stream
│   └── package.json
├── docs/
│   ├── SIMULATION_BUILDING_GUIDE.md # How to build simulations
│   └── SIMULATION_TEMPLATES_GUIDE.md # All 31 templates documented
├── logs/                            # Auto-generated simulation logs
├── CHANGELOG.md                     # Version history
└── requirements.txt                 # Python dependencies (gdm-concordia pinned)
```

## Troubleshooting

**ImportError: No module named 'concordia'**
```bash
pip install -r requirements.txt
```

**CUDA/GPU errors**
```bash
pip install sentence-transformers --no-deps
pip install transformers torch
```

**Ollama timeouts** — Common with local models on slower hardware. Use DeepSeek or OpenAI for reliability.

**Anthropic "temperature is deprecated for this model"** — Handled automatically for Opus 4.7+ models (extended thinking mode rejects temperature).

**CORS errors** — Ensure backend runs on port 8000 and frontend `.env` has correct `VITE_API_URL`.

**Empty analytics tabs on older logs** — Pre-v2.4 logs use a different HTML format. The parser handles both, but some tabs may show limited data.

**`TypeError: string indices must be integers, not 'str'`** — Scene premise for game-theoretic GM must be a dictionary, not a string. See game-theoretic configuration above.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push and open a Pull Request

### Development Tips

- Templates live in `backend/api/templates/` — one file per template, auto-registered via `router.add_api_route()`
- Frontend components use React Context for state management
- All simulations auto-save to `logs/` with descriptive filenames
- See [CHANGELOG.md](CHANGELOG.md) for version history and upgrade procedures

## License

This project uses the [Concordia library](https://github.com/google-deepmind/concordia) (Apache-2.0 license).

Licensed under the Apache 2.0 License — see the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{concordia_sim_builder,
  title={Democratizing AI Social Simulation: A No-Code Web Interface for the Concordia Framework},
  author={Chong, Ng S. T.},
  year={2026},
  url={https://github.com/ngstcf/concordia-sim-builder},
  institution={United Nations University}
}
```

## Acknowledgments

- **Google DeepMind** for the [Concordia](https://github.com/google-deepmind/concordia) framework
- **FastAPI** and **React** communities

## Resources

- **Documentation**: [c3.unu.edu/projects/ai/simulator/v2.4.html](https://c3.unu.edu/projects/ai/simulator/v2.4.html)
- **Building Guide**: [SIMULATION_BUILDING_GUIDE.md](docs/SIMULATION_BUILDING_GUIDE.md)
- **Templates Guide**: [SIMULATION_TEMPLATES_GUIDE.md](docs/SIMULATION_TEMPLATES_GUIDE.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Known Issues**: [CONCORDIA_ISSUES.md](CONCORDIA_ISSUES.md)
- **GitHub Issues**: Report bugs or request features

---

**Built using [Concordia](https://github.com/google-deepmind/concordia) by [Ng Chong](https://github.com/ngstcf) at United Nations University**
