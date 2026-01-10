# Concordia Simulation Builder

A web interface for Google DeepMind's [Concordia](https://github.com/google-deepmind/concordia) library that makes running agent-based social simulations accessible—no Python programming required.

Configure agents, psychological components, and scenarios through forms. Run simulations powered by LLMs. Analyze results with built-in analytics including timeline visualization, cooperation metrics, grounded variables tracking, and AI-powered deep content analysis.

![Simulation Builder](https://img.shields.io/badge/Concordia-Simulation%20Builder-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

**📖 Documentation:** [c3.unu.edu/projects/ai/simulator/](https://c3.unu.edu/projects/ai/simulator/)

## ✨ Features

- **🎨 Form-Based Configuration** - Intuitive web UI for configuring agent-based simulations without coding
- **🤖 Multi-Agent Scenarios** - Define multiple agents with unique goals, memories, and behaviors
- **🧩 Customizable Components** - Add psychological components (personality, cognitive bias, social identity, emotions, values, TPB) to agents
- **🔄 Nested Simulations** - PhoneGameMaster pattern for running mini-simulations within simulations
- **📊 Grounded Variables** - Track and update simulation state variables (morale, budget, health, etc.) with AI-powered post-processing to extract variable history from simulation logs
- **⚡ Real-time Progress Streaming** - Watch simulations unfold with live step-by-step progress, elapsed time, and ETA
- **📊 Analytics Dashboard** - Statistical analysis, timeline visualization, action breakdown, and AI-generated summaries
- **🧠 LLM-Powered Simulation Analyzer** - Automated deep content analysis generating executive summaries, team effectiveness assessments, insights, and recommendations
- **📂 Recent Simulations Browser** - Easily view and analyze previous simulation results with checkpoint file management
- **🎮 Rich Output Format** - Interactive HTML logs with tabbed views and agent activity tracking
- **🔄 Template System** - Pre-built templates (Peace Negotiation, Coffee Shop Demo, and more)
- **🌐 Multiple LLM Support** - OpenAI, Azure OpenAI, DeepSeek (recommended), Gemini, Anthropic, and Ollama
- **💾 Import/Export** - Save and share simulation configurations as JSON
- **📝 Automatic Logging** - All simulations saved with timestamped, descriptive filenames

## 🎯 Use Cases

- **Social Science Research** - Model and study complex social interactions with psychological realism
- **Psychological Experiments** - Test how cognitive biases, social identity, and emotions affect decision-making
- **Game Design** - Test NPC behaviors and dialogue systems
- **Education** - Teach negotiation, conflict resolution, and social dynamics
- **Creative Writing** - Explore character interactions and story outcomes
- **Business Scenarios** - Simulate meetings, negotiations, and team dynamics
- **Resource Management** - Track budget, morale, and other metrics over time

## 🛠️ Tech Stack

**Backend:**
- Python 3.10+ with FastAPI
- Google DeepMind Concordia library
- Pydantic for data validation
- Sentence Transformers for embeddings

**Frontend:**
- React 18 with TypeScript
- Vite for fast development
- Tailwind CSS v4 for styling
- React Router for navigation
- TanStack Query for data management

## 📦 Installation

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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (includes pinned gdm-concordia version)
pip install -r requirements.txt
```

**Note:** The `gdm-concordia` version is pinned to `2.1.0` to ensure compatibility with all templates and features. See [CHANGELOG.md](CHANGELOG.md) for upgrade procedures.

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# LLM Provider Configuration
OPENAI_API_KEY=sk-xxx                    # For OpenAI models
AZURE_OAI_KEY=xxx                        # For Azure OpenAI (see docs/AZURE_OPENAI_SETUP.md)
AZURE_OAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OAI_VERSION=2024-12-01-preview     # Optional: API version for Azure OpenAI
DEEPSEEK_API_KEY=sk-xxx                  # For DeepSeek (recommended)
GEMINI_API_KEY=xxx                       # For Gemini models
ANTHROPIC_API_KEY=sk-xxx                # For Claude models
# OLLAMA_BASE_URL=http://localhost:11434/v1  # Optional: Custom Ollama endpoint
```

### Using Ollama (Local Models)

For completely local simulations without API costs, you can use [Ollama](https://ollama.com):

**Performance Requirements:**
Ollama works well when running on hardware with sufficient resources:
- **RAM**: 8GB+ for 7B models, 16GB+ recommended for larger models
- **CPU**: Multi-core processor recommended (local models are CPU-intensive)
- **GPU**: Optional but significantly improves inference speed
- For best performance, consider using a hosted Ollama service or cloud-based LLMs (DeepSeek, OpenAI)

**When to use Ollama:**
- ✅ Privacy-sensitive simulations (data stays local)
- ✅ Testing and development without API costs
- ✅ Machines with good CPU/GPU performance
- ✅ Hosted Ollama services with sufficient server resources

1. **Install Ollama:**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Or download from https://ollama.com for Windows
   ```

2. **Pull a model:**
   ```bash
   # Llama 3 (8B) - Recommended balance of quality and speed
   ollama pull llama3

   # For faster performance with smaller models
   ollama pull llama3:2

   # Other options: mistral, codellama, phi3, gemma2, qwen2
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Configure in the web UI:**
   - Select "Ollama (Local)" as the provider
   - Enter the model name (e.g., "llama3")
   - No API key required for local Ollama!

**Available Ollama models:** `llama3`, `llama3:2`, `mistral`, `codellama`, `phi3`, `gemma2`, `qwen2`

**⚠️ Important Note on Ollama Timeouts:**
- Local models like Ollama can experience timeout issues, especially with larger models or slower hardware
- Typical timeout symptoms: "Timeout on attempt X/3. Retrying in Y seconds..."
- If you experience frequent timeouts, consider using **DeepSeek** (recommended) instead
- Hosted Ollama services (e.g., on powerful servers) work well for production use

### Using Hosted Ollama Services (OpenWebUI, etc.)

If you're using a hosted Ollama service (like OpenWebUI) that requires authentication:

1. Set the `OLLAMA_BASE_URL` to your hosted service endpoint
2. Set `OLLAMA_API_KEY` to your API key (if required)
3. In the web UI, select "Ollama (Local)" and enter your API key

```bash
# Example .env configuration for hosted Ollama
OLLAMA_BASE_URL=https://your-openwebui-instance.com/v1
OLLAMA_API_KEY=your-api-key-here
```

### Configuring Game-Theoretic Simulations

For simulations using `game_theoretic_and_dramaturgic__GameMaster` (Prisoner's Dilemma, Marketplace):

**Important Configuration Rules:**
- `max_steps` = Number of game rounds (e.g., 4 rounds = max_steps: 4)
- `num_rounds` in scene parameters = Must equal `max_steps`
- **Formula**: `num_rounds = max_steps` (NOT multiplied by participants)

Example for 4-round Prisoner's Dilemma with 2 players:
```json
{
  "max_steps": 4,
  "game_master": {
    "parameters": {
      "scenes": [{
        "num_rounds": 4  // Must equal max_steps
      }]
    }
  }
}
```

Total individual actions = num_rounds × participants (e.g., 4 × 2 = 8 actions)

**Scene Premise Format:**
The scene's `premise` must be a **dictionary** mapping each participant to their individual context:

```json
{
  "premise": {
    "Agent1": ["Context specific to Agent1", "More context..."],
    "Agent2": ["Context specific to Agent2", "More context..."]
  }
}
```

Using a string instead of a dictionary will cause: `TypeError: string indices must be integers, not 'str'`

**Analytics:**
Game-theoretic simulations automatically track action choices (COOPERATE/DEFECT, BUY/SELL/HOLD) in the analytics dashboard with robust extraction supporting any action format.

**Frontend Configuration:**

```bash
# Simulation timeout in milliseconds (default: 10800000 = 3 hours)
# Increase this for very long simulations
VITE_SIMULATION_TIMEOUT=10800000
```

### Simulation Checkpointing and Hang Prevention

The Simulation Builder includes robust features to prevent data loss from long-running simulations:

**Automatic Checkpointing:**
- Partial results are saved every 5 steps to `logs/` directory
- Checkpoint files include `_checkpoint_step{N}.html` suffix
- Enables recovery if simulation encounters issues
- No manual intervention required

**Watchdog Monitoring:**
- Detects when simulation hangs (no progress for 10 minutes)
- Configurable via `WATCHDOG_TIMEOUT_SECONDS` environment variable
- Can be disabled via `WATCHDOG_ENABLED=false` if warnings interfere with simulations
- Prevents indefinite waiting on stuck simulations

**Per-Request Timeout Enforcement:**
- Default: 180 seconds per LLM request (standard models)
- Default: 300 seconds per LLM request (reasoning models like O1, O3)
- Configurable via `LLM_TIMEOUT` and `LLM_REASONING_TIMEOUT` environment variables
- System waits FULL timeout before flagging error (no premature interruption)

**Configuration:**

```bash
# Per-LLM-request timeout in seconds (default: 180 = 3 minutes)
LLM_TIMEOUT=180

# Per-LLM-request timeout for reasoning models (default: 300 = 5 minutes)
LLM_REASONING_TIMEOUT=300

# Maximum retry attempts for LLM requests (default: 2)
LLM_MAX_RETRIES=2

# Simulation watchdog timeout in seconds (default: 600 = 10 minutes)
WATCHDOG_TIMEOUT_SECONDS=600

# Enable/disable watchdog monitoring (default: true)
# Set to 'false' to disable hang prevention if it interferes with simulations
WATCHDOG_ENABLED=true

# Frontend simulation timeout in milliseconds (default: 10800000 = 3 hours)
VITE_SIMULATION_TIMEOUT=10800000
```

**Important Notes:**
- The system waits the FULL timeout duration before flagging an error
- If a request completes at 179s (of 180s timeout) → SUCCESS
- If a request completes at 181s (of 180s timeout) → RETRY
- Checkpoints are saved automatically - no configuration needed
- All timeout values are configurable via environment variables

For detailed configuration guidance, see [docs/TIMEOUT_CONFIGURATION.md](docs/TIMEOUT_CONFIGURATION.md).

## 🚀 Running the Application

### Start Backend (Terminal 1)

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 📖 Usage Guide

### 1. Building a Simulation

1. **Set the Premise** - Describe the scenario and setting
2. **Configure Parameters**
   - **Max Steps**: How many rounds of action (each agent acts once per step)
   - More steps = longer, more detailed simulations
3. **Add Agents**
   - Click "Add Agent" to create a new character
   - Set their name, goal, and initial memories
   - Choose an appropriate prefab (e.g., `basic__Entity`)
4. **Configure Game Master**
   - Choose the acting order (fixed or game_master_choice)
   - Set the narrator name
5. **Add Shared Memories** - Context known to all agents

### 2. Running a Simulation

1. Navigate to the **Runner** tab
2. Configure LLM settings:
   - Select your provider (**DeepSeek recommended** for cost/quality and full compatibility)
   - Choose model name
   - Set temperature (0.8-1.2 for creative, 0.1-0.4 for focused)
3. Click **"Run Simulation"**
4. **✨ Watch real-time progress in the web UI** showing:
   - Current step completion (e.g., "3/5 steps completed")
   - Elapsed time and estimated remaining time
   - Progress bar filling as simulation advances
5. View results in the embedded log viewer with tabs for:
   - **Simulation Log** - Full HTML output with agent interactions
   - **Statistical Dashboard** - Metrics, agent activity, text statistics
   - **Timeline Visualization** - Step-by-step event timeline
   - **Actions View** - Per-agent action breakdown with goals
   - **Natural Language Summary** - AI-generated analysis
6. Download HTML logs for sharing or archiving

**Console Logs**: Detailed progress also shown in terminal with timing information

### 3. Using Templates

**Basic Templates:**
- **Peace Negotiation** - Russia-Ukraine peace talks with UN mediator (20 steps)
- **Coffee Shop Demo** - Quick 5-step demo for testing basic interactions

**Prefab Type Templates:**
- **Planning Agent** (`/templates/planning-agent`) - Strategic scenario with `basic_with_plan__Entity`
  - Startup team coordinating product launch strategy
  - Agents with multi-step planning capabilities
  - Best for: Complex coordination scenarios

- **Scripted Entity** (`/templates/scripted-entity`) - Focus group discussion with `basic_scripted__Entity`
  - Scripted moderator guides 4 diverse participants through a debate
  - Demonstrates exact scripted responses (ignores context)
  - Best for: Facilitated discussions, controlled scenarios, demonstrations

- **Context-Aware Moderator** (`/templates/context-aware-moderator`) - Support group with `context_aware_scripted__Entity`
  - Crisis counselor guides job loss support group with adaptive responses
  - Demonstrates natural context-aware scripted dialogue
  - Responds to what participants say while following script structure
  - Automatically delivers closing statement when script is exhausted
  - Best for: Support groups, therapy sessions, responsive facilitation

**Research Templates:**
- **Vaccine Hesitancy Study** (`/templates/vaccine-hesitancy`) - Psychological component system research demo
  - 5 agents with different psychological profiles (personality, cognitive bias, social identity, TPB)
  - Demonstrates how customizable components enable theory-driven agent design
  - Based on cognitive bias theory and social identity theory
  - Best for: Research on persuasion, attitude change, social influence

- **Phishing Attack Simulation** (`/templates/phishing-attack-simulation`) - Cybersecurity tabletop exercise
  - 4 security analysts simulate phishing attack scenarios to assess risk and plan response
  - Each analyst runs a nested simulation (hacker → user → IT security) to model attack chains
  - Demonstrates meta-cognitive reasoning - agents simulate adversarial scenarios without actual risk
  - Based on red team/blue team exercises and tabletop simulation methodologies
  - Best for: Cybersecurity training, threat modeling, incident response planning

- **Urban Gentrification** (`/templates/urban-gentrification`) - Housing policy and neighborhood change simulation
  - 6 stakeholders debate housing policies while GM tracks 11 neighborhood indicators
  - Grounded variables track rent, displacement, business survival, community cohesion, affordability
  - **AI-Powered Post-Processing:** Extract variable history from completed simulations to analyze policy impacts
  - Longitudinal urban economics research with policy intervention testing
  - Based on gentrification dynamics, rent gap theory, displacement mechanisms
  - Best for: Urban planning research, housing policy evaluation, neighborhood change studies

**Advanced Features:**
- **Nested Simulation Demo** (`/templates/nested-simulation-demo`) - PhoneGameMaster pattern demo
  - Alice simulates a conversation with Bob to decide what to bring to a party
  - Demonstrates nested simulations where agents run mini-simulations as part of decision-making
  - Best for: Complex planning, social reasoning, "what-if" scenarios

- **Grounded Variables Demo** (`/templates/grounded-variables-demo`) - Grounded variables tracking demo
  - Project management scenario tracking team morale, budget, tasks, health, crisis mode, completion %
  - **AI-Powered Post-Processing:** Extract variable history from completed simulations using LLM analysis
  - Works around Concordia's limitation where variables aren't updated during simulation
  - Analyzes unstructured HTML logs to identify variable changes (explicit and inferred)
  - Supports numerical, categorical, boolean, and percentage variable types
  - Best for: Resource management, state tracking, dynamic scenarios, longitudinal analysis

- **Dialogic Conversation** (`/templates/dialogic-conversation`) - Therapy session with `dialogic__GameMaster`
  - Counselor-patient dialogue with auto-termination
  - Focus on conversation flow
  - Best for: Dialogue-heavy scenarios

- **Strategic Game** (`/templates/strategic-game`) - Prisoner's Dilemma with `game_theoretic_and_dramaturgic__GameMaster`
  - Iterated Prisoner's Dilemma tournament (4 rounds)
  - Payoffs, scores, and strategic decisions (COOPERATE/DEFECT)
  - Analytics dashboard shows action counts per agent
  - Best for: Game theory scenarios

- **Marketplace** (`/templates/marketplace`) - Farmers market with `game_theoretic_and_dramaturgic__GameMaster`
  - Economic trading simulation (10 rounds)
  - Three vendors making BUY/SELL/HOLD decisions
  - Game-theoretic structure with payoffs and analytics
  - Best for: Economic/trading scenarios with strategic choices

- **Interviewer** (`/templates/interviewer`) - Employee survey with `interviewer__GameMaster`
  - Structured questionnaire administration
  - HR conducting satisfaction survey
  - Best for: Survey/interview scenarios

- **Formative Memories** (`/templates/formative-memories`) - High school reunion with character backstories
  - Rich character development via `player_specific_context`
  - Agents with detailed formative memories
  - Best for: Character-driven narratives

### 4. Simulation Analyzer - LLM-Powered Deep Analysis

The Simulation Analyzer automatically analyzes simulation logs using LLM to generate comprehensive reports.

**Available via:**
- **Web API**: `POST /api/simulations/analyze-simulation`
- **CLI**: `python backend/scripts/analyze_simulation.py <log_path>`

**Features:**
- **Executive Summary** - High-level overview of what happened
- **Timeline Analysis** - Step-by-step event breakdown
- **Team Effectiveness** - Agent/team performance assessment
- **Key Insights** - Technical findings, human factors, decision quality
- **Recommendations** - Actionable suggestions organized by timeframe

**Usage Examples:**

```bash
# Analyze a simulation via CLI
python backend/scripts/analyze_simulation.py logs/20260109_224705_simulation.html

# Specify custom output path
python backend/scripts/analyze_simulation.py logs/simulation.html reports/analysis.md
```

```typescript
// Analyze via Web API (from frontend)
import { analyzeSimulation } from './utils/api';

const analysis = await analyzeSimulation('20260109_224705');
console.log(analysis.executive_summary);
console.log(analysis.recommendations);
```

## 📚 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/simulations/prefabs` | GET | List available entity/game master prefabs |
| `/api/simulations/providers` | GET | List supported LLM providers |
| `/api/simulations/models/{provider}` | GET | List available models for a provider |
| `/api/simulations/validate` | POST | Validate simulation configuration |
| `/api/simulations/execute` | POST | Run simulation with **real-time progress streaming** ✨ |
| `/api/simulations/execute-simple` | POST | Run simulation (non-streaming, for testing) |
| `/api/simulations/export-template` | GET | Get blank configuration template |
| `/api/simulations/import` | POST | Import configuration from JSON |

### Simulation Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/status` | GET | Get status of all running simulations |
| `/api/simulations/status/{task_id}` | GET | Get status of specific simulation |
| `/api/simulations/cancel/{task_id}` | POST | Cancel a running simulation |

### Logs & Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/recent` | GET | List recent simulation logs |
| `/api/simulations/logs/{filename}` | GET | Get specific simulation log HTML |
| `/api/simulations/logs/{filename}/analytics` | GET | Get analytics for simulation log |
| `/api/simulations/logs/checkpoints` | GET | List checkpoint files (with filter options) |
| `/api/simulations/logs/checkpoints` | DELETE | Delete checkpoint files (with filter options) |

### Grounded Variables

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/grounded-variables/extract` | POST | Extract variable history from simulation log using AI |
| `/api/simulations/grounded-variables/{simulation_id}` | GET | Get grounded variables data for simulation |

### Analysis & Insights

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/analyze-simulation` | POST | Generate comprehensive LLM-powered analysis report |

### Component System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/components/templates` | GET | List available psychological component templates |
| `/api/simulations/components/validate` | POST | Validate component parameters |

### Templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulations/templates/peace-negotiation` | GET | Peace negotiation template |
| `/api/simulations/templates/coffee-shop` | GET | Coffee shop demo template |
| `/api/simulations/templates/planning-agent` | GET | Planning agent template |
| `/api/simulations/templates/scripted-entity` | GET | Scripted entity (focus group moderator) template |
| `/api/simulations/templates/context-aware-moderator` | GET | Context-aware moderator (support group) template |
| `/api/simulations/templates/dialogic-conversation` | GET | Dialogic conversation template |
| `/api/simulations/templates/strategic-game` | GET | Strategic game theory template |
| `/api/simulations/templates/interviewer` | GET | Interview/survey template |
| `/api/simulations/templates/formative-memories` | GET | Character backstory template |
| `/api/simulations/templates/marketplace` | GET | Marketplace trading template |
| `/api/simulations/templates/state-formation` | GET | State formation simulation (SDG 16) |
| `/api/simulations/templates/labor-action` | GET | Labor strike simulation (SDG 8) |
| `/api/simulations/templates/commons-dilemma` | GET | Fishery management simulation (SDG 12/13) |
| `/api/simulations/templates/disaster-response` | GET | Flood evacuation simulation (SDG 11/13) |
| `/api/simulations/templates/inequality-mobility` | GET | Educational opportunity simulation (SDG 10) |
| `/api/simulations/templates/vaccine-hesitancy` | GET | Vaccine hesitancy research demo |
| `/api/simulations/templates/nested-simulation-demo` | GET | Nested simulation (PhoneGameMaster) demo |
| `/api/simulations/templates/grounded-variables-demo` | GET | Grounded variables tracking demo |
| `/api/simulations/templates/phishing-attack-simulation` | GET | Phishing attack simulation (cybersecurity) |
| `/api/simulations/templates/urban-gentrification` | GET | Urban gentrification simulation (housing policy) |

## 🎨 Supported Prefabs

### Entity Prefabs (Agents)

| Prefab | Description | Best For |
|--------|-------------|----------|
| `basic__Entity` | Standard agent with "three key questions" decision framework | Most scenarios |
| `basic_with_plan__Entity` | Adds strategic planning with time horizons | Complex coordination |
| `basic_scripted__Entity` | Follows predefined scripts exactly (goes silent when exhausted) | Testing, demonstrations, exact output |
| `context_aware_scripted__Entity` | Adapts script to context, auto-closes when exhausted | Natural moderators, responsive facilitators |
| `minimal__Entity` | Simplified decision-making | Lightweight simulations |
| `fake_assistant_with_configurable_system_prompt__Entity` | AI assistant with custom system prompt | Simulating AI personas |

### Game Master Prefabs

| Prefab | Description | Best For |
|--------|-------------|----------|
| `generic__GameMaster` | Standard narrative control | Most simulations |
| `dialogic__GameMaster` | Conversation-focused with auto-termination | Dialogue-heavy scenarios |
| `dialogic_and_dramaturgic__GameMaster` | Enhanced dialogue with dramatic structure | Rich conversations |
| `game_theoretic_and_dramaturgic__GameMaster` | Matrix games with payoffs/scores | Strategic negotiations |
| `interviewer__GameMaster` | Administers questionnaires | Surveys, interviews |
| `psychology_experiment__GameMaster` | Experimental protocols | Research scenarios |
| `scripted__GameMaster` | Follows predetermined narrative | Controlled storytelling |
| `marketplace__GameMaster` | Economic trading systems | Market simulations |

### Initializer Prefabs

| Prefab | Description |
|--------|-------------|
| `formative_memories_initializer__GameMaster` | Creates character backgrounds from `player_specific_context` before main simulation |

## 🔧 Configuration Examples

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

### Complex Negotiation

```json
{
  "premise": "Peace negotiation between two conflicting parties.",
  "max_steps": 20,
  "agents": [
    {
      "name": "Party A Representative",
      "goal": "Secure territorial recognition",
      "prefab": "basic__Entity",
      "memories": ["Territory is non-negotiable core interest"]
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

## 🐛 Troubleshooting

### Backend Issues

**ImportError: No module named 'concordia'**
```bash
pip install gdm-concordia --upgrade
```

**CUDA/gpu errors**
```bash
# For systems without GPU, install CPU version:
pip install sentence-transformers --no-deps
pip install transformers torch
```

### Frontend Issues

**Port already in use**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**CORS errors**
- Ensure backend is running on port 8000
- Check frontend `.env` has correct `VITE_API_URL`

### LLM Provider Issues

**API key errors**
- Verify `.env` file is in root directory
- Check API key has sufficient credits
- Try different provider if one is down

**Ollama timeout errors**
- Symptoms: "Timeout on attempt X/3. Retrying in Y seconds..."
- This is common with local models, especially larger ones or on slower hardware
- **Solution**: Use **DeepSeek** instead (fully compatible and reliable)

**DeepSeek connection issues**
- Verify API key is correct and has credits
- Check network connectivity to `https://api.deepseek.com`
- Try model `deepseek-chat` or `deepseek-coder`

## 📂 Project Structure

```
concordia-sim-builder/
├── backend/
│   ├── api/
│   │   └── simulations.py          # API endpoints + analytics
│   ├── models/
│   │   ├── schemas.py              # Pydantic models
│   │   └── llm_wrappers.py         # LLM provider wrappers
│   ├── services/
│   │   ├── simulation_builder.py   # Simulation construction
│   │   ├── simulation_runner.py    # Execution with streaming + logging
│   │   ├── simulation_state.py     # Task state management
│   │   └── llm_factory.py          # LLM provider factory (multi-provider support)
│   └── main.py                      # FastAPI app with .env loading
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SimulationBuilder/   # Builder UI
│   │   │   ├── SimulationRunner/    # Runner UI with progress
│   │   │   │   ├── StatisticalDashboard.tsx    # ✨ Analytics
│   │   │   │   ├── TimelineVisualization.tsx  # ✨ Timeline
│   │   │   │   ├── ActionsView.tsx            # ✨ Actions
│   │   │   │   └── NaturalLanguageSummary.tsx # ✨ Summary
│   │   │   ├── RecentSimulations/  # ✨ Recent logs browser
│   │   │   └── shared/             # Shared components
│   │   ├── contexts/
│   │   │   └── SimulationContext.tsx # Global state
│   │   ├── types/
│   │   │   └── simulation.ts        # TypeScript types
│   │   └── utils/
│   │       └── api.ts              # API client
│   └── package.json
├── logs/                            # Auto-generated simulation logs
├── negotiatepeace.py                # Original CLI simulation
└── requirements.txt                 # Python dependencies
```

## 🔌 LLM Integration Architecture

### Why We Built Our Own LLM Factory

The Simulation Builder includes a custom multi-provider LLM integration layer instead of using Concordia's built-in `GptLanguageModel`. This architectural decision provides significant advantages:

**Business Case:**

1. **Cost Optimization** (10-50× savings)
   - **DeepSeek**: Superior cost alternative to GPT-4-class models at a fraction of the price
   - **Ollama**: Free local execution for privacy-sensitive simulations
   - **Azure OpenAI**: Enterprise pricing and compliance requirements
   - **Model Choice**: Select the right provider for each use case

2. **Geographic & Compliance Flexibility**
   - **Azure OpenAI**: Data residency requirements (EU, Asia, etc.)
   - **Anthropic**: Alternative provider for risk diversification
   - **Gemini**: Google Cloud integration and enterprise agreements
   - **Ollama**: Air-gapped environments and offline operation

3. **Model-Specific Optimizations**
   - **O3/GPT-5 Models**: Automatic detection, correct API parameters (`max_completion_tokens`, no `temperature`)
   - **Token Management**: Generous limits (2k-10k minimum) prevent cutoff responses
   - **Error Handling**: Retry logic, helpful debug warnings, empty response detection

4. **Production Reliability**
   - **Fallback Options**: Switch providers if one is down or rate-limited
   - **Enhanced Logging**: Actionable error messages for troubleshooting
   - **Consistent Interface**: Uniform API across all providers

**Technical Implementation:**

```
backend/models/llm_wrappers.py     # Provider-specific wrappers (OpenAI, Azure, Anthropic, Gemini, GLM)
backend/services/llm_factory.py    # Factory pattern for provider selection
backend/models/schemas.py          # LLMSettings with provider-specific fields
```

**Supported Providers:**
- **OpenAI**: GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
- **Azure OpenAI**: Enterprise-grade OpenAI with data residency
- **DeepSeek**: Cost-effective reasoning models (recommended)
- **Anthropic**: Claude 3.5 Sonnet, Claude Opus
- **Gemini**: Google Gemini 1.5/2.0 models
- **Ollama**: Local LLaMA, Mistral, and other open-source models

**Why Not Concordia's Built-in?**
Concordia's `GptLanguageModel` only supports OpenAI's API, lacks Azure support, has no alternative provider options, and uses a rigid configuration model. Our custom implementation enables the multi-provider flexibility required for production deployments across different organizational needs, cost constraints, and compliance requirements.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Tips

- Add new prefabs in `backend/services/simulation_builder.py`
- Create new templates in `backend/api/simulations.py`
- Frontend components use React Context for state management
- All simulations are automatically saved to `logs/` directory

## 📜 License

This project uses the [Concordia library](https://github.com/google-deepmind/concordia) (Apache-2.0 license).

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 📖 Citation

If you use this software in your research, please cite:

```bibtex
@software{concordia_sim_builder,
  title={Democratizing AI Social Simulation: A No-Code Web Interface for the Concordia Framework},
  author={Ng Chong},
  year={2026},
  url={https://github.com/ngstcf/concordia-sim-builder}
}
```

**OR**

```bibtex
@software{concordia_sim_builder,
  title={Democratizing AI Social Simulation: A No-Code Web Interface for the Concordia Framework},
  author={Chong, Ng S. T.},
  year={2026},
  url={https://github.com/ngstcf/concordia-sim-builder},
  institution={United Nations University}
}
```

## 🙏 Acknowledgments

- **Google DeepMind** for the [Concordia](https://github.com/google-deepmind/concordia) framework
- **Concordia Contributors** for building an amazing simulation library
- **FastAPI** for the excellent web framework
- **React Community** for the amazing ecosystem

## ⚠️ Known Limitations

### Game-Theoretic Simulation Issue

The `game_theoretic_and_dramaturgic__GameMaster` prefab has a confirmed issue where participant turn-taking is not symmetric. In a 2-agent game with 8 steps, instead of alternating (Agent A, Agent B, Agent A, Agent B...), one agent may act only once while the other acts 7 times.

**Impact**: Strategic game simulations (Prisoner's Dilemma, etc.) may not produce expected symmetric outcomes.

**Workaround**: Use generic game master prefabs or manually manage turn sequences for now. See [CONCORDIA_ISSUES.md](CONCORDIA_ISSUES.md) for details.

**Status**: Documented bug in Concordia framework - tracking for upstream fix.

## 🌟 Roadmap

- [x] **Analytics Dashboard** - Statistical analysis and natural language summaries of simulation results ✅
- [x] **Real-time Progress Streaming** - Watch simulations unfold live in the browser with step-by-step progress ✅
- [x] **Console Progress Logging** - Detailed real-time logs during simulation execution ✅
- [x] **Timeline Visualization** - Step-by-step event timeline ✅
- [x] **Actions View** - Per-agent action breakdown with extracted goals ✅
- [x] **Game-Theoretic Analytics** - Robust action extraction for strategic games (Prisoner's Dilemma, Marketplace) ✅
- [x] **Customizable Components System** - Add psychological components (personality, cognitive bias, social identity, emotions, values, TPB) to agents ✅ 
- [x] **Nested Simulations** - PhoneGameMaster pattern for running mini-simulations within simulations ✅ 
- [x] **Grounded Variables Tracking** - Track and update simulation state variables (morale, budget, health, etc.) ✅ 
- [ ] **Visual graph editor for agent relationships** - Drag-and-drop interface to create and visualize agent social networks, influence maps, and communication flows
- [ ] **Simulation comparison tool** - Run multiple simulations with varied parameters and compare outcomes side-by-side with statistical analysis
- [ ] **Export to PDF/Markdown** - Generate publication-ready reports from simulation results in multiple formats
- [ ] **Agent behavior analytics** - Track and visualize agent metrics over time (cooperation rates, sentiment evolution, decision patterns)
- [ ] **Multi-player mode with human agents** - Allow humans to join simulations as agents, interacting with AI agents
- [ ] **Cloud deployment option** - One-click deployment to cloud platforms for collaborative research and shared access

---

**Built using [Concordia](https://github.com/google-deepmind/concordia) by [Ng Chong](https://github.com/ngstcf)**
