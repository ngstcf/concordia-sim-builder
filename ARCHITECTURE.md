# Concordia Simulation Builder - Architecture Documentation

## Overview

The Concordia Simulation Builder is a web-based tool for creating, running, and analyzing multi-agent social simulations using Google DeepMind's Concordia framework. It provides a React frontend with a Flask/FastAPI backend for building agent-based simulations with various game master prefabs and grounded variables.

**Key Capabilities:**
- Create simulations with multiple agents and different game master types
- Run simulations with configurable steps (1-100+)
- View simulation results with interactive HTML logs
- Analyze agent actions, cooperation rates, and grounded variables over time
- Support for game-theoretic, dramaturgical, and generic simulation types

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Backend Structure](#backend-structure)
3. [Frontend Structure](#frontend-structure)
4. [Simulation Templates](#simulation-templates)
5. [Grounded Variables System](#grounded-variables-system)
6. [Key Design Decisions](#key-design-decisions)
7. [Extension Guide](#extension-guide)
8. [Common Tasks](#common-tasks)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Builder    │  │   Runner     │  │  Analytics   │      │
│  │   Component  │  │  Component   │  │  Components  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Flask/FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  |   API        │  │   Service    │  │    Prefabs   │      │
│  |  Endpoints   │  │   Layer      │  │  Components  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                         │                                     │
│                         ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Concordia Framework                         │   │
│  │  (Agent-based simulation engine)                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Structure

### Directory Layout

```
backend/
├── api/
│   └── simulations.py          # ALL simulation templates & API endpoints
├── services/
│   ├── simulation_builder.py  # Builds simulation from config
│   └── simulation_runner.py   # Runs simulations & saves results
├── prefabs/
│   ├── grounded_variables.py # Grounded variables component
│   └── (future prefab components)
├── models/
│   └── schemas.py             # Pydantic models for API
└── main.py                    # Flask/FastAPI application entry
```

### Key Files Explained

#### `backend/api/simulations.py`
**Purpose:** Defines ALL simulation templates and API endpoints.

**Why templates are here (not separate files):**
- Templates are data structures (Python dicts), not logic
- Easy to compare and modify templates in one place
- Fast access without file I/O overhead
- Templates share common structures and can be copy-pasted

**Key Functions:**
- `get_simulation_templates()` - Returns list of all available templates
- `get_[template_name]_template()` - Individual template getters (e.g., `get_prisoners_dilemma_template()`)
- `/api/simulations/templates` - API endpoint to fetch templates
- `/api/simulations/run` - API endpoint to run simulation
- `/api/simulations/analytics/<filename>` - Extract analytics from simulation HTML

**Template Structure:**
```python
{
    "name": "Template Name",
    "description": "Human-readable description",
    "config": {
        "premise": "Scenario description",
        "max_steps": 30,
        "shared_memories": ["memory1", "memory2"],
        "agents": [
            {
                "id": "agent_id",
                "name": "Agent Name",
                "prefab": "basic__Entity",
                "goal": "Agent's goal",
                "memories": ["memory1", "memory2"],
                "randomize_choices": True
            }
        ],
        "game_master": {
            "prefab": "generic__GameMaster",
            "name": "Game Master Name",
            "acting_order": "game_master_choice",
            "parameters": {},
            "grounded_variables": [...]  # Optional
        }
    }
}
```

#### `backend/services/simulation_builder.py`
**Purpose:** Converts template config into runnable Concordia simulation.

**Key Functions:**
- `build_simulation(config, model)` - Main entry point
- `create_agent(agent_config, model)` - Creates individual agents
- `create_game_master(gm_config, agents, model, extra_components)` - Creates game master

**Grounded Variables Integration:**
```python
# Lines 262-286: Attaches grounded variables component
if config.game_master.grounded_variables:
    from backend.prefabs.grounded_variables import create_grounded_variables_component

    # Convert VariableConfig to dicts
    variable_configs = [var.model_dump() for var in config.game_master.grounded_variables]

    # Create component
    grounded_vars_component = create_grounded_variables_component(model, variable_configs)

    # Add to game master extra_components
    gm_params['extra_components']['grounded_variables_component'] = grounded_vars_component
```

#### `backend/services/simulation_runner.py`
**Purpose:** Runs simulation and saves results (HTML + metadata).

**Key Functions:**
- `run_simulation(config, model)` - Main entry point
- `save_simulation_metadata()` - Saves sidecar JSON with simulation config

**Grounded Variables History Extraction:**
```python
# Lines 228-272: Extracts history after simulation
grounded_variables_history = None
if sim.game_masters and config.game_master.grounded_variables:
    # Find the component in game master
    for component_name in gm.get_component_names():
        component = gm.get_component(component_name)
        if component.__class__.__name__ == 'GroundedVariablesComponent':
            # Get history for each variable
            for var_config in config.game_master.grounded_variables:
                history = component.get_history(var_name)
                # Format: List of (step, value) tuples
                formatted_history = [{"step": s, "value": v} for s, v in history]
                grounded_variables_history[var_name] = formatted_history
```

**Debug Output Added (lines 231-247):**
```python
print(f"[DEBUG] Grounded variables configured: {len(config.game_master.grounded_variables)} variables")
print(f"[DEBUG] Game master components: {component_names}")
print(f"[DEBUG] Component '{component_name}' is of type '{class_name}'")
```

#### `backend/prefabs/grounded_variables.py`
**Purpose:** Component that tracks simulation state variables over time.

**How It Works:**
1. **Initialization** (lines 71-97): Sets up variables with default values and empty history
2. **Update Detection** (lines 145-165): After each step:
   - Records current values in history
   - Uses LLM to analyze event and detect which variables should change
   - Applies validated changes
3. **LLM Prompt** (lines 190-220): Asks LLM to identify variable updates based on event text

**Example Variable Config:**
```python
{
    "name": "median_monthly_rent",
    "variable_type": "numerical",  # or "percentage", "boolean", "categorical"
    "description": "Median monthly rent for a 2-bedroom apartment",
    "default_value": 1800,
    "min_value": 800,
    "max_value": 5000,
    "update_rule": "Increases with development approvals, decreases with rent control"
}
```

#### `backend/models/schemas.py`
**Purpose:** Pydantic models for type-safe API.

**Key Models:**
- `SimulationConfig` - Complete simulation configuration
- `AgentConfig` - Agent configuration
- `GameMasterConfig` - Game master configuration
- `VariableConfig` - Grounded variable configuration

---

## Frontend Structure

### Directory Layout

```
frontend/
├── src/
│   ├── components/
│   │   ├── SimulationBuilder/
│   │   │   ├── SimulationBuilder.tsx     # Main builder UI
│   │   │   ├── AgentEditor.tsx           # Agent CRUD
│   │   │   └── GameMasterEditor.tsx      # Game master config
│   │   ├── SimulationRunner/
│   │   │   ├── SimulationRunner.tsx      # Main runner UI
│   │   │   ├── SimulationLog.tsx         # HTML log viewer
│   │   │   ├── ActionsView.tsx           # Agent actions timeline
│   │   │   ├── TimelineVisualization.tsx # Event timeline
│   │   │   ├── GroundedVariablesChart.tsx # Variable time-series
│   │   │   └── CooperationRateChart.tsx  # Game-theoretic metrics
│   │   └── SimulationList/
│   │       └── SimulationList.tsx        # Simulation library
│   ├── utils/
│   │   ├── api.ts                        # API client functions
│   │   └── types.ts                      # TypeScript type definitions
│   ├── App.tsx                           # Root component
│   └── main.tsx                          # Entry point
└── package.json
```

### Key Components

#### `SimulationBuilder.tsx`
**Purpose:** Form-based UI for creating/editing simulations.

**State Management:**
- Uses React hooks for local state
- No global state management (simple enough to not need Redux)

**Features:**
- Template selection
- Agent add/edit/delete
- Game master configuration
- Grounded variables editor (advanced mode)

#### `SimulationRunner.tsx`
**Purpose:** Run simulations and view results.

**Tabs:**
- Simulation Log - Full HTML output from Concordia
- Actions - Per-agent action timeline
- Timeline - Event visualization
- Grounded Variables - Time-series charts
- Cooperation - For game-theoretic simulations

**Key Logic:**
```typescript
// Tab navigation state
const [activeTab, setActiveTab] = useState<'log' | 'actions' | 'timeline' | 'variables' | 'cooperation'>('log');

// Auto-select first agent when analytics load
useEffect(() => {
  if (analytics && analytics.agents.length > 0) {
    setSelectedAgent(analytics.agents[0]);
  }
}, [analytics]);
```

#### `GroundedVariablesChart.tsx`
**Purpose:** Display time-series charts for grounded variables.

**Empty State Diagnostics:**
```typescript
if (!hasChartData) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
      <p className="text-xs text-yellow-800">
        <strong>Backend Issue Detected:</strong> Grounded variables exist but have no history data.
      </p>
    </div>
  );
}
```

#### `CooperationRateChart.tsx`
**Purpose:** Display cooperation/defection rates for game-theoretic simulations.

**Detection Logic:**
```typescript
const isGameTheoretic = analytics?.gm_prefab?.includes('game_theoretic');

// Keyword matching in agent actions
if (text.includes('cooperate') || text.includes('share') || text.includes('help')) {
  cooperationCount++;
}
```

#### `utils/api.ts`
**Purpose:** API client with TypeScript types.

**Key Functions:**
- `getSimulationTemplates()` - Fetch available templates
- `runSimulation(config)` - Run simulation
- `getSimulationFiles()` - List saved simulations
- `getSimulationAnalytics(filename)` - Extract analytics from HTML

---

## Simulation Templates

### Where Templates Are Defined

**File:** `backend/api/simulations.py`
**Lines:** 150-3000+

### How to Add a New Template

1. **Create a new function** in `simulations.py`:

```python
async def get_my_new_template():
    """
    Template: My New Simulation

    Brief description of what this demonstrates.
    """
    return {
        "name": "My Template Name",
        "description": "Human-readable description",
        "config": {
            "premise": "Scenario description",
            "max_steps": 30,
            "shared_memories": ["memory1", "memory2"],
            "agents": [
                # ... agent configs
            ],
            "game_master": {
                # ... game master config
            }
        }
    }
```

2. **Add to template list** in `get_simulation_templates()`:

```python
templates = [
    await get_prisoners_dilemma_template(),
    await get_urban_gentrification_template(),
    await get_my_new_template(),  # Add here
]
```

### Available Templates

| Template | Game Master | Agents | Steps | Purpose |
|----------|-------------|--------|-------|---------|
| Prisoner's Dilemma | `game_theoretic_and_dramaturgic__GameMaster` | 2 | 10 | Game theory, cooperation |
| Urban Gentrification | `generic__GameMaster` | 6 | 30 | Grounded variables, policy |
| Vaccine Hesitancy | `generic__GameMaster` | 5 | 25 | Psychology, public health |
| Workplace Dynamics | `basic__GameMaster` | 4 | 20 | Social dynamics, hierarchy |

### Template Copy-Paste Pattern

Most templates follow this pattern. Copy an existing one and modify:

```python
# Copy from Prisoner's Dilemma for game-theoretic
# Copy from Urban Gentrification for grounded variables
# Copy from Vaccine Hesitancy for psychological components
```

---

## Grounded Variables System

### Purpose

Track simulation state variables over time to study longitudinal dynamics.

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. Simulation Step Completes                           │
│     - Agent takes action                                │
│     - Game master generates event                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. GroundedVariablesComponent.post_act(event)          │
│     - Records current values in history                 │
│     - Prompts LLM: "Which variables should change?"     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. LLM Analyzes Event                                  │
│     - Looks for variable-relevant keywords              │
│     - Returns: "median_monthly_rent=2000" or "None"     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Component Validates & Applies Changes               │
│     - Checks min/max constraints                        │
│     - Updates current value                             │
│     - Returns to simulation                            │
└─────────────────────────────────────────────────────────┘
```

### Variable Types

| Type | Description | Example | Min/Max |
|------|-------------|---------|---------|
| `numerical` | Continuous number | Rent: $1800 | Optional |
| `percentage` | 0-100 range | Displacement: 15% | 0-100 |
| `boolean` | True/False | Rent control: False | N/A |
| `categorical` | Enum values | Character: "transitional" | Required list |

### LLM Detection Tips

The LLM detects variable changes better when:

1. **Use capital letters** for action keywords:
   - "INCREASE RENT", "PREVENT DISPLACEMENT", "CLOSE BUSINESS"

2. **Include current values** in premise/memories:
   - "Current median rent is $1800"
   - "15% of households have been displaced"

3. **Mention variable names explicitly**:
   - "median_monthly_rent", "displacement_rate", "business_survival"

4. **Provide context** in update_rule:
   - "Increases when development proposals are approved"

Example from Urban Gentrification template:
```python
"premise": "...The Council will debate policies that may \
  INCREASE RENT PRICES, DISPLACE RESIDENTS, CLOSE BUSINESSES, \
  AFFECT COMMUNITY COHESION, INCREASE PROPERTY VALUES..."
```

### History Tracking

**Format:** List of `{"step": int, "value": any}` objects

```python
# Example history for median_monthly_rent
[
    {"step": 1, "value": 1800},
    {"step": 2, "value": 1800},  # No change
    {"step": 3, "value": 1950},  # Rent increased!
    {"step": 4, "value": 1950},
    # ...
]
```

**Metadata Storage:** Saved in `.metadata.json` sidecar file

**Extraction:** Done in `simulation_runner.py` lines 228-272

---

## Key Design Decisions

### 1. Why Templates in Code (Not Files)?

**Decision:** Templates defined as Python dicts in `simulations.py`

**Rationale:**
- Templates are data structures, not logic
- Easy to copy-paste and modify
- No file I/O overhead
- Type-safe with Pydantic validation
- Can be generated programmatically if needed

**Alternative Considered:** JSON/YAML files
**Rejected Because:** More complex, no real benefit for this use case

### 2. Why Generic Game Master for Grounded Variables?

**Decision:** Use `generic__GameMaster` with `extra_components` parameter

**Rationale:**
- Grounded variables work with any game master type
- `extra_components` is the standard Concordia extension mechanism
- Separates concerns (GM runs simulation, component tracks state)

**Code:**
```python
gm_params['extra_components']['grounded_variables_component'] = component
```

### 3. Why HTML Output + JSON Metadata?

**Decision:** Save both HTML log and JSON metadata

**Rationale:**
- **HTML:** Human-readable, works with Concordia's existing logging
- **JSON:** Machine-readable, easy to parse for analytics
- **Separation:** Keeps logic separate from presentation

### 4. Why LLM-Based Variable Updates?

**Decision:** Use LLM to detect when variables should change

**Rationale:**
- Flexible: Works with any simulation scenario
- Context-aware: Understands semantic meaning
- No manual rules needed

**Trade-off:** Can miss updates if event text is vague

**Mitigation:** Enhanced templates with explicit keywords (see Urban Gentrification)

### 5. Why React with TypeScript?

**Decision:** Frontend in React + TypeScript

**Rationale:**
- **React:** Component-based, great for forms and dashboards
- **TypeScript:** Type safety catches bugs early
- **Tailwind CSS:** Rapid UI development
- **No Redux:** Simple enough for local state

### 6. Why Flask/FastAPI Hybrid?

**Decision:** Started with Flask, migrating to FastAPI

**Current State:** Flask app with async support

**Future:** Full FastAPI migration for better async/await support

---

## Extension Guide

### Adding a New Simulation Template

**Time:** 15-30 minutes

1. **Choose base template** to copy from
2. **Edit `backend/api/simulations.py`**
3. **Create new function** following naming pattern: `get_[topic]_template()`
4. **Modify config:**
   - `premise`: Set scenario
   - `agents`: Add relevant characters
   - `game_master`: Choose prefab type
   - `grounded_variables` (optional): Add variables to track
5. **Add to `get_simulation_templates()`** return list
6. **Test:** Run from frontend builder

### Adding a New Visualization

**Time:** 1-2 hours

1. **Create component** in `frontend/src/components/SimulationRunner/`
2. **Follow pattern** of existing visualizations:
   ```typescript
   export default function MyVisualization({ filename }: Props) {
     const [analytics, setAnalytics] = useState(null);
     const [loading, setLoading] = useState(false);

     useEffect(() => {
       if (filename) loadAnalytics();
     }, [filename]);

     // Your visualization logic here
   }
   ```
3. **Add tab** in `SimulationRunner.tsx`:
   ```typescript
   <button onClick={() => setActiveTab('myviz')}>My Viz</button>
   ```
4. **Render conditionally:**
   ```typescript
   {activeTab === 'myviz' && <MyVisualization filename={selectedFile} />}
   ```

### Adding a New Game Master Prefab

**Time:** 2-4 hours (requires understanding Concordia)

1. **Check if prefab exists** in Concordia framework
2. **Add to `GameMasterConfig`** in `models/schemas.py`
3. **Update builder** in `services/simulation_builder.py` if needed
4. **Add template** using new prefab
5. **Test** with simple simulation first

### Adding a New Variable Type

**Time:** 30 minutes

1. **Add enum** to `VariableType` in `prefabs/grounded_variables.py`:
   ```python
   class VariableType(str, Enum):
       NUMERICAL = "numerical"
       CATEGORICAL = "categorical"
       BOOLEAN = "boolean"
       PERCENTAGE = "percentage"
       YOUR_TYPE = "your_type"  # Add here
   ```

2. **Add validation** in `_validate_value()` method
3. **Update frontend** to handle new type in `GroundedVariablesChart.tsx`
4. **Test** with a template using the new type

---

## Common Tasks

### Debug Why Variables Aren't Changing

**Symptoms:** Grounded variables stay at default values

**Debug Steps:**

1. **Check debug output:**
   ```bash
   # Run simulation and look for:
   [DEBUG] Grounded variables configured: N variables
   [DEBUG] Game master components: [...]
   [DEBUG] Component 'xxx' is of type 'GroundedVariablesComponent'
   ```

2. **Check metadata file:**
   ```bash
   # Look for history field in .metadata.json
   cat logs/20250108_*.metadata.json | grep -A 5 '"history"'
   ```

3. **Analyze simulation events:**
   ```bash
   # Use the analysis script
   python3 analyze_simulation.py logs/20250108_*.html
   ```

4. **Check event text:**
   - Are there explicit variable mentions?
   - Are action keywords in caps?
   - Is there enough context?

**Solutions:**
- Add more explicit language to template (see Urban Gentrification example)
- Run more steps (30 vs 10)
- Check if component is being found (debug output)

### Add Grounded Variables to Existing Template

**Time:** 10 minutes

1. **Open template** in `backend/api/simulations.py`
2. **Add `grounded_variables` key** to `game_master` config:
   ```python
   "game_master": {
       "prefab": "generic__GameMaster",
       # ... other config
       "grounded_variables": [
           {
               "name": "my_variable",
               "variable_type": "numerical",
               "description": "What this tracks",
               "default_value": 100,
               "min_value": 0,
               "max_value": 1000,
               "update_rule": "When/how it changes"
           }
       ]
   }
   ```
3. **Enhance premise/memories** with variable language
4. **Test** and check debug output

### Export Simulation Data

**Options:**

1. **HTML log:** Full simulation output in `logs/*.html`
2. **JSON metadata:** Config + history in `logs/*.metadata.json`
3. **API analytics:** Extracted data via `/api/simulations/analytics/<filename>`

**To export to CSV:**
```python
import json
import csv

# Load metadata
with open('logs/simulation.metadata.json') as f:
    data = json.load(f)

# Extract variable history
for var in data['game_master']['grounded_variables']:
    if 'history' in var:
        with open(f'{var['name']}.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['step', 'value'])
            writer.writerows([(h['step'], h['value']) for h in var['history']])
```

### Change Simulation Steps

**Builder UI:** Use "Max Steps" input field

**Code:** Edit template's `max_steps` value:
```python
"max_steps": 30,  # Change this
```

**Recommendations:**
- 5-10: Quick demos, testing
- 20-30: Standard simulations (most templates)
- 50-100: Complex scenarios, research
- 100+: Longitudinal studies (caution: slow/expensive)

---

## Performance Considerations

### Backend

- **Simulation speed:** ~1-5 seconds per step (depends on LLM)
- **Memory usage:** ~100-500MB per simulation
- **Concurrent sims:** Limited by API rate limits

### Frontend

- **Large HTML logs:** Can be 5-10MB (use iframe)
- **Chart rendering:** SVG for <1000 points, consider aggregation for more
- **Analytics extraction:** Can take 1-2 seconds for large simulations

### Optimization Tips

1. **Limit steps** during development
2. **Use pagination** for agent actions (not implemented yet)
3. **Cache analytics** extraction results
4. **Compress** old HTML logs (gzip)

---

## Data Extraction from Concordia HTML

### Overview

Concordia framework generates highly variable HTML output that contains simulation logs, agent actions, game master events, and state information. The Challenge Analyzer uses sophisticated parsing techniques to extract structured data from this unstructured HTML.

### Why HTML Extraction is Hard

1. **Variable Structure:** HTML structure changes based on game master prefab, simulation type, and Concordia version
2. **Nested Details:** Agent memories, actions, and observations are deeply nested in `<details>` elements
3. **Mixed Formats:** Text appears in various HTML elements (`<li>`, `<p>`, `<summary>`, etc.)
4. **Dynamic Content:** Number of agents, steps, and interactions varies per simulation
5. **No Stable API:** Concordia doesn't provide a structured JSON output format

### Extraction Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Raw HTML File (5-10MB)                                 │
│  - Deeply nested <details> elements                     │
│  - Variable structure based on GM prefab                │
│  - Agent actions, memories, observations                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  ChallengeAnalyzer Class                                │
│  /Users/cio/gai/concordia/backend/challenge_analyzer.py │
│                                                           │
│  Primary Methods:                                        │
│  - parse_agent_action_counts()                           │
│  - extract_agent_actions()                               │
│  - extract_timeline()                                    │
│  - extract_game_theoretic_data()                         │
│  - extract_grounded_variables()                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Parsers & Heuristics                                    │
│  - BeautifulSoup for HTML parsing                       │
│  - Regex patterns for data extraction                   │
│  - Heuristic rules for handling variations              │
│  - Fallback logic for missing/empty fields              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Structured JSON Analytics                              │
│  {                                                        │
│    "agents": ["Agent 1", "Agent 2"],                     │
│    "agent_actions": {"Agent 1": 10, "Agent 2": 8},       │
│    "agent_details": {                                    │
│      "Agent 1": {                                       │
│        "actions": [{"step": 1, "text": "..."}],        │
│        "goal": "...",                                   │
│        "memories": ["..."]                              │
│      }                                                  │
│    },                                                   │
│    "timeline": [{"step": 1, "description": "..."}],     │
│    "grounded_variables": [...],                          │
│    "game_theoretic_data": {...}                          │
│  }                                                        │
└─────────────────────────────────────────────────────────┘
```

### Key Extraction Functions

#### File Location
**`backend/challenge_analyzer.py`** - Main extraction class (3000+ lines)

#### 1. Agent Action Extraction

**Method:** `extract_agent_actions(html_content)`

**Challenge:** Actions are nested differently for each GM prefab

**Strategy:** Multiple fallback parsers

```python
# Pseudo-code showing the multi-strategy approach
def extract_agent_actions(self, html_content):
    strategies = [
        self._extract_from_generic_gm,      # Try generic GM format
        self._extract_from_dramaturgic_gm,  # Try dramaturgical GM
        self._extract_from_basic_gm,        # Try basic GM
        self._extract_fallback_pattern      # Last resort: regex patterns
    ]

    for strategy in strategies:
        try:
            result = strategy(html_content)
            if result and self._validate_extraction(result):
                return result
        except Exception:
            continue

    return self._get_empty_result()
```

**HTML Pattern Examples:**

**Generic GM Format:**
```html
<details>
  <summary>Step 1</summary>
  <ul>
    <li>Agent Name</li>
    <li>
      <details>
        <summary>Action</summary>
        <ul>
          <li>Value: Agent did something...</li>
        </ul>
      </details>
    </li>
  </ul>
</details>
```

**Extraction Logic:**
```python
# Find all agent action blocks
agent_blocks = soup.find_all('li', text=lambda t: t and 'Agent' in str(t))

for block in agent_blocks:
    # Navigate nested structure
    action_details = block.find('details', summary=lambda s: 'Action' in s.text)
    if action_details:
        action_text = action_details.find('li', class_='Value')
        if action_text:
            # Extract step number
            step_elem = block.find_previous('summary')
            step = self._extract_step_number(step_elem)

            actions.append({
                'step': step,
                'text': action_text.text.strip()
            })
```

#### 2. Timeline Extraction

**Method:** `extract_timeline(html_content)`

**Challenge:** Timeline events scattered across multiple HTML sections

**Strategy:** Look for specific patterns

**Patterns Searched:**
```python
# Pattern 1: Step headers with descriptions
# <summary>Step 5</summary> Event: Description here

# Pattern 2: Game master events
# <li>City Council Moderator --- Event: **Event text**</li>

# Pattern 3: Resolution sections
# <ul>__resolution__</ul><li>Event: ...</li>
```

**Extraction Code:**
```python
events = []

# Strategy 1: Look for GM events
gm_events = soup.find_all(string=re.compile(r'--- Event:'))
for event in gm_events:
    # Extract step number from context
    step_match = re.search(r'Step (\d+)', event.find_previous('summary').text)
    step = int(step_match.group(1)) if step_match else None

    # Extract event text (remove markdown)
    text = re.sub(r'--- Event:\s*\*\*(.*?)\*\*', r'\1', event)

    events.append({
        'step': step,
        'description': text.strip(),
        'type': 'step' if step else 'event'
    })

# Strategy 2: Look for action summaries
# ... (additional patterns)
```

#### 3. Grounded Variables Extraction

**Method:** `extract_grounded_variables(html_content)`

**Challenge:** Variables displayed in free text, not structured format

**Strategy:** Pattern matching + validation

**HTML Pattern:**
```html
Current grounded variable values:
  - median_monthly_rent: 1800 (numerical)
    Description: Median monthly rent for a 2-bedroom apartment in Elmwood
  - low_income_displacement_rate: 15 (percentage)
    Description: Percentage of households displaced...
```

**Extraction Code:**
```python
def extract_grounded_variables(self, html_content):
    # Find the section with grounded variables
    section_pattern = r'Current grounded variable values:(.*?)(?=\n\n|$)'
    match = re.search(section_pattern, html_content, re.DOTALL)

    if not match:
        return []

    variables = []
    lines = match.group(1).split('\n')

    for line in lines:
        # Pattern: "- variable_name: value (type)"
        var_match = re.match(r'\s*-\s+(\w+):\s+(\S+)\s+\((\w+)\)', line)

        if var_match:
            name = var_match.group(1)
            value = self._parse_value(var_match.group(2))
            var_type = var_match.group(3)

            # Get description from next line
            desc_match = re.search(r'Description:\s*(.+)', lines[idx+1])
            description = desc_match.group(1) if desc_match else ""

            variables.append({
                'name': name,
                'type': var_type,
                'description': description.strip(),
                'current_value': value
            })

    return variables
```

**Value Parsing:**
```python
def _parse_value(self, value_str):
    """Parse value string to appropriate type"""
    # Boolean
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'

    # Number (int or float)
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # String (categorical)
    return value_str.strip()
```

#### 4. Game-Theoretic Data Extraction

**Method:** `extract_game_theoretic_data(html_content)`

**Challenge:** Format varies by game type (Prisoner's Dilemma, Public Goods, etc.)

**Strategy:** Detect game type first, then use specific parser

**Game Type Detection:**
```python
def detect_game_type(self, html_content):
    """Detect which game-theoretic simulation was run"""

    if 'prisoner' in html_content.lower():
        return 'prisoners_dilemma'
    elif 'public goods' in html_content.lower():
        return 'public_goods'
    elif 'marketplace' in html_content.lower():
        return 'marketplace'
    else:
        # Look for specific HTML patterns
        if '<summary>Choose your action:</summary>' in html_content:
            return 'prisoners_dilemma'
        # ... more patterns

    return 'unknown'
```

**Extraction by Game Type:**
```python
# Prisoner's Dilemma specific patterns
# Look for action choice sections
action_pattern = r'<summary>(\w+)\'s move</summary>.*?<li>Value:\s*(\w+)'

# Public Goods patterns
contribution_pattern = r'<summary>Contribution decision</summary>.*?<li>Amount:\s*(\d+)'
```

### Heuristic Rules & Fallbacks

#### Rule 1: Agent Name Normalization

**Problem:** Names appear in various formats:
- "Agent Name"
- "Agent Name (Player 1)"
- "Entity [Agent Name]"

**Solution:**
```python
def normalize_agent_name(self, raw_name):
    """Extract base agent name from various formats"""
    # Remove player numbers
    name = re.sub(r'\s*\(Player\s*\d+\)', '', raw_name)
    # Remove entity markers
    name = re.sub(r'Entity\s*\[(.*?)\]', r'\1', name)
    # Strip whitespace
    name = name.strip()

    return name
```

#### Rule 2: Step Number Inference

**Problem:** Step numbers not always explicit

**Solution:** Infer from position
```python
def infer_step_number(self, element, all_elements):
    """Infer step number from element's position in list"""
    idx = all_elements.index(element)

    # Try to extract from nearby elements
    for offset in [-1, -2, 1, 2]:
        nearby = all_elements[idx + offset] if 0 <= idx + offset < len(all_elements) else None
        if nearby:
            step_match = re.search(r'Step\s*(\d+)', str(nearby))
            if step_match:
                return int(step_match.group(1))

    # Fallback: return position + 1
    return idx + 1
```

#### Rule 3: Action Text Cleaning

**Problem:** Action text contains HTML entities, markdown, extra whitespace

**Solution:**
```python
def clean_action_text(self, raw_text):
    """Clean and normalize action text"""
    # Convert HTML entities
    text = html.unescape(raw_text)

    # Remove markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
```

#### Rule 4: Missing Data Handling

**Problem:** Not all simulations have all data types

**Solution:** Return empty defaults
```python
def get_empty_analytics(self):
    """Return empty analytics structure"""
    return {
        'agents': [],
        'agent_actions': {},
        'agent_details': {},
        'timeline': [],
        'grounded_variables': [],
        'game_theoretic_data': None,
        'total_steps': 0,
        'total_observations': 0
    }
```

### Validation & Quality Assurance

#### Validation Checks

```python
def validate_extraction(self, analytics):
    """Validate extracted data for consistency"""
    errors = []

    # Check 1: Agent count consistency
    if len(analytics['agents']) != len(analytics['agent_details']):
        errors.append(f"Agent count mismatch: {len(analytics['agents'])} vs {len(analytics['agent_details'])}")

    # Check 2: Step sequence integrity
    steps = [e['step'] for e in analytics['timeline']]
    if steps != sorted(steps):
        errors.append(f"Timeline steps not in order: {steps}")

    # Check 3: Action count consistency
    for agent in analytics['agents']:
        action_count = analytics['agent_actions'].get(agent, 0)
        detail_count = len(analytics['agent_details'].get(agent, {}).get('actions', []))
        if action_count != detail_count:
            errors.append(f"Action count mismatch for {agent}: {action_count} vs {detail_count}")

    # Check 4: Grounded variables have required fields
    for var in analytics['grounded_variables']:
        required = ['name', 'type', 'description']
        missing = [f for f in required if not var.get(f)]
        if missing:
            errors.append(f"Variable {var.get('name', 'unknown')} missing fields: {missing}")

    return errors
```

### Performance Optimization

#### Caching Strategy

```python
class ChallengeAnalyzer:
    def __init__(self):
        self._cache = {}

    def get_simulation_analytics(self, filename):
        # Check cache first
        if filename in self._cache:
            return self._cache[filename]

        # Extract and cache
        analytics = self._extract_from_html(filename)
        self._cache[filename] = analytics

        return analytics
```

#### Lazy Evaluation

```python
def get_agent_details(self, html_content):
    """Only extract agent details if requested"""
    # Check if we actually need agent details
    if not self._needs_agent_details():
        return {}

    # Expensive extraction only when needed
    return self._extract_agent_details_expensive(html_content)
```

### Common Extraction Patterns

#### Pattern 1: Nested Details Elements

**HTML:**
```html
<details>
  <summary>Agent Name</summary>
  <ul>
    <li>
      <details>
        <summary>Goal</summary>
        <ul>
          <li>Value: Agent's goal text</li>
        </ul>
      </details>
    </li>
  </ul>
</details>
```

**Extraction:**
```python
# Navigate to value element
summary = soup.find('summary', text='Agent Name')
if summary:
    details = summary.find_parent('details')
    goal_details = details.find('summary', text='Goal')
    if goal_details:
        goal_value = goal_details.find_parent('details').find('li', class_='Value')
        if goal_value:
            return goal_value.text
```

#### Pattern 2: List-Based Data

**HTML:**
```html
<ul>
  <li>Key: value1</li>
  <li>Key: value2</li>
  <li>Key: value3</li>
</ul>
```

**Extraction:**
```python
items = soup.find_all('li')
data = {}
for item in items:
    if ':' in item.text:
        key, value = item.text.split(':', 1)
        data[key.strip()] = value.strip()
```

#### Pattern 3: Table Data

**HTML:**
```html
<table>
  <tr><th>Agent</th><th>Actions</th></tr>
  <tr><td>Agent 1</td><td>10</td></tr>
</table>
```

**Extraction:**
```python
table = soup.find('table')
rows = table.find_all('tr')
headers = [th.text for th in rows[0].find_all('th')]

data = []
for row in rows[1:]:
    cells = [td.text for td in row.find_all('td')]
    data.append(dict(zip(headers, cells)))
```

### Testing Extraction Logic

#### Test HTML Samples

Store test HTML files for different simulation types:
```
backend/test_data/
  ├── prisoners_dilemma_10steps.html
  ├── urban_gentrification_30steps.html
  ├── vaccine_hesitancy_25steps.html
  └── edge_cases/
      ├── empty_actions.html
      ├── missing_steps.html
      └── malformed_html.html
```

#### Unit Tests

```python
def test_agent_action_extraction():
    """Test agent action extraction from known HTML"""
    analyzer = ChallengeAnalyzer()

    with open('test_data/prisoners_dilemma_10steps.html') as f:
        html = f.read()

    analytics = analyzer.get_simulation_analytics(html)

    assert 'Alice' in analytics['agents']
    assert 'Bob' in analytics['agents']
    assert len(analytics['agent_details']['Alice']['actions']) == 10

def test_grounded_variable_extraction():
    """Test grounded variable extraction"""
    analyzer = ChallengeAnalyzer()

    # Test with known HTML
    analytics = analyzer.get_simulation_analytics(test_html)

    assert len(analytics['grounded_variables']) == 11
    assert analytics['grounded_variables'][0]['name'] == 'median_monthly_rent'
    assert analytics['grounded_variables'][0]['current_value'] == 1800
```

### Debugging Extraction Issues

#### Enable Debug Logging

```python
import logging

class ChallengeAnalyzer:
    def __init__(self, debug=False):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def _log_extraction(self, step, data):
        if self.debug:
            logging.debug(f"[{step}] Extracted: {data}")
```

#### Visual Inspection

Create tool to visualize extraction:
```python
def visualize_extraction(html_file):
    """Show what was extracted from HTML"""
    analyzer = ChallengeAnalyzer()

    with open(html_file) as f:
        html = f.read()

    analytics = analyzer.get_simulation_analytics(html)

    print(f"Agents found: {analytics['agents']}")
    print(f"Total actions: {sum(analytics['agent_actions'].values())}")
    print(f"Timeline events: {len(analytics['timeline'])}")
    print(f"Grounded variables: {len(analytics['grounded_variables'])}")

    # Show sample extraction
    for agent, details in analytics['agent_details'].items():
        print(f"\n{agent}:")
        print(f"  Actions: {len(details['actions'])}")
        if details['actions']:
            print(f"  First action: {details['actions'][0]['text'][:100]}...")
```

### API Endpoint

**File:** `backend/api/simulations.py`
**Function:** `get_simulation_analytics(filename)`

**Flow:**
```python
@app.route('/api/simulations/analytics/<path:filename>', methods=['GET'])
def get_simulation_analytics(filename):
    """
    Extract analytics from simulation HTML file.

    Returns structured JSON with:
    - Agents and their actions
    - Timeline of events
    - Grounded variables
    - Game-theoretic data (if applicable)
    """
    try:
        html_path = os.path.join(LOGS_DIR, filename.replace('.metadata.json', '.html'))

        if not os.path.exists(html_path):
            return jsonify({'error': 'HTML file not found'}), 404

        # Use ChallengeAnalyzer to extract
        analyzer = ChallengeAnalyzer()
        analytics = analyzer.get_simulation_analytics(html_path)

        # Validate extraction
        errors = analyzer.validate_extraction(analytics)
        if errors:
            print(f"[WARNING] Extraction validation errors: {errors}")

        return jsonify(analytics)

    except Exception as e:
        print(f"[ERROR] Analytics extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
```

### Key Learnings

1. **Always have fallbacks:** HTML structure varies widely, never rely on a single parsing strategy
2. **Validate everything:** Check counts, types, and required fields
3. **Log extensively:** When extraction fails, log the HTML snippet for debugging
4. **Test with diverse samples:** Use multiple simulation types in tests
5. **Handle edge cases:** Empty actions, missing steps, malformed HTML
6. **Cache results:** Extraction is expensive, cache when possible
7. **Provide diagnostics:** Help users understand why extraction failed

### Future Improvements

1. **Machine Learning Extraction:** Train model to extract data from any HTML format
2. **Concordia Patch:** Submit PR to Concordia for JSON output option
3. **Streaming Parser:** Process large HTML files in chunks
4. **Incremental Updates:** Update analytics as simulation runs
5. **Diff-Based Extraction:** Only re-extract changed portions

---

## Troubleshooting

### Common Issues

#### Issue: "Component not found in game master"

**Cause:** Grounded variables component not attached

**Fix:** Check `simulation_builder.py` lines 262-286, ensure `extra_components` is set correctly

#### Issue: "History is empty in metadata"

**Cause:** Extraction failed or component wasn't found

**Fix:** Check debug output, verify component class name matches

#### Issue: "Variables never change"

**Cause:** LLM can't detect changes from event text

**Fix:** Enhance template with explicit keywords (see Urban Gentrification)

#### Issue: "Frontend can't load simulation"

**Cause:** File path issues or backend not running

**Fix:** Check console, verify backend is running on correct port

### Debug Mode

**Enable detailed logging:**
```python
# In simulation_runner.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check simulation logs:**
```bash
tail -f logs/*.log
```

---

## Future Improvements

### Planned Features

1. **Real-time progress updates** during simulation run
2. **Batch simulation runs** for parameter sweeps
3. **Export to CSV/Excel** for analysis in R/Python
4. **Comparison view** for multiple simulations
5. **Custom variable update rules** (not just LLM-based)
6. **FastAPI migration** for better async support
7. **Database storage** for simulation metadata
8. **User authentication** for multi-tenant deployments

### Technical Debt

1. **Remove duplicate code** in template definitions
2. **Add error boundaries** in React components
3. **Implement caching** for analytics extraction
4. **Add unit tests** for critical functions
5. **Document API** with OpenAPI/Swagger

---

## Resources

### Concordia Framework

- **GitHub:** https://github.com/google-deepmind/concordia
- **Paper:** "Concordia: A platform for simulating social dynamics"
- **Documentation:** See Concordia README

### Key Papers

1. **Grounded Variables:** Original Concordia paper
2. **Game-Theoretic GM:** Prisoner's Dilemma implementations
3. **Psychological Components:** Theory of Planned Behavior

### Related Projects

- **Frontend:** React, TypeScript, Tailwind CSS
- **Backend:** Flask, FastAPI (migration in progress)
- **LLM:** Claude, GPT-4, or other models via API

---

## Quick Reference

### File Locations

| What You Need | File | Line Range |
|---------------|------|------------|
| Add template | `backend/api/simulations.py` | New function at end |
| Edit agents | `backend/api/simulations.py` | Template `agents` list |
| Add variables | `backend/api/simulations.py` | Template `grounded_variables` list |
| Component logic | `backend/prefabs/grounded_variables.py` | 145-165 (update logic) |
| History extraction | `backend/services/simulation_runner.py` | 228-272 |
| Charts | `frontend/src/components/SimulationRunner/` | Various files |
| API types | `backend/models/schemas.py` | All models |
| Frontend types | `frontend/src/utils/types.ts` | All types |

### Common Commands

```bash
# Run backend
cd backend && python main.py

# Run frontend
cd frontend && npm run dev

# Check logs
ls -la logs/*.html logs/*.metadata.json

# Analyze simulation
python3 analyze_simulation.py logs/20250108_*.html

# Run tests (when implemented)
npm test
pytest tests/
```

---

## Contributing

### Code Style

- **Backend:** PEP 8, Black formatter
- **Frontend:** ESLint, Prettier
- **Commits:** Conventional commits (`feat:`, `fix:`, `docs:`)

### Pull Request Process

1. Create feature branch from `main`
2. Make changes with clear commit messages
3. Test thoroughly (manually for now)
4. Submit PR with description
5. Code review and merge

---

## License

This project uses code from Google DeepMind's Concordia framework, which is under the Apache 2.0 License.

---

## Contact

For questions or issues:
1. Check this documentation first
2. Review code comments
3. Check existing GitHub issues
4. Create new issue with details

---

**Last Updated:** 2025-01-08

**Version:** 0.1.0 (Alpha)

**Status:** Active Development
