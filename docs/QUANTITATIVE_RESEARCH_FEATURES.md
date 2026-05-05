# Quantitative Research Features Guide

This guide covers four features designed for quantitative social science research: structured data export, census-based agent generation, action constraints, and batch runs with parameter sweeps. These features work together to support reproducible, data-driven simulation research.

---

## Table of Contents

1. [Structured Data Export (CSV/JSON)](#1-structured-data-export-csvjson)
2. [Census/Distribution-Based Agent Generation](#2-censusdistribution-based-agent-generation)
3. [Structured Action Constraints](#3-structured-action-constraints)
4. [Batch Runs with Parameter Sweeps](#4-batch-runs-with-parameter-sweeps)
5. [Putting It All Together: A Research Workflow](#5-putting-it-all-together-a-research-workflow)

---

## 1. Structured Data Export (CSV/JSON)

Export per-step agent decisions and grounded variable histories as structured data files for analysis in pandas, R, Excel, or any data tool.

### What Gets Exported

**Agent Actions CSV** — one row per agent per step:

| Column | Description |
|--------|-------------|
| `step` | Simulation step number |
| `agent_name` | Name of the acting agent |
| `action` | What the agent said or did |
| `observation` | The Game Master's response or narration |

**Grounded Variables CSV** — one row per variable per step:

| Column | Description |
|--------|-------------|
| `step` | Simulation step number |
| `variable_name` | Name of the grounded variable |
| `variable_type` | Type (numerical, percentage, boolean, categorical) |
| `value` | The variable's value at that step |

**Combined CSV** — both tables concatenated, with a `data_type` column (`action` or `variable`) to distinguish rows.

**Full JSON** — a structured object containing both datasets:

```json
{
  "agent_actions": [
    {"step": 1, "agent_name": "Maria", "action": "...", "observation": "..."},
    ...
  ],
  "grounded_variables": [
    {"step": 1, "variable_name": "median_rent", "variable_type": "numerical", "value": 1800},
    ...
  ],
  "metadata": {
    "total_steps": 30,
    "agents": ["Maria", "James", "Priya"],
    "variables": ["median_rent", "displacement_rate"]
  }
}
```

### How to Export

1. Run a simulation to completion
2. In the **Results** header area, you will see three buttons next to the HTML log download:
   - **Export CSV** (green) — downloads a combined CSV with both agent actions and grounded variables
   - **Export JSON** (purple) — downloads the full structured JSON
   - **Download** (default) — the original HTML narrative log

The export buttons appear only when results are available and a log file has been saved.

### API Endpoints

For programmatic access:

```
GET /api/logs/{filename}/export-csv?data_type=actions
GET /api/logs/{filename}/export-csv?data_type=variables
GET /api/logs/{filename}/export-csv?data_type=both
GET /api/logs/{filename}/export-json
```

The `data_type` parameter defaults to `both` if omitted.

### Example: Loading in pandas

```python
import pandas as pd

# Agent actions
df = pd.read_csv("simulation_export.csv")
actions = df[df["data_type"] == "action"]
variables = df[df["data_type"] == "variable"]

# Pivot grounded variables into a time series
pivot = variables.pivot(index="step", columns="variable_name", values="value")
pivot.plot(title="Grounded Variables Over Time")
```

---

## 2. Census/Distribution-Based Agent Generation

Generate agents whose demographic attributes follow a specified statistical distribution. This is essential for research that requires representative agent populations rather than hand-crafted individuals.

### When to Use This

- You need 10-50+ agents and cannot hand-write each one
- Agent demographics must match real-world population data (census, survey results)
- You want reproducible sampling with a fixed random seed
- You are studying how population composition affects simulation outcomes

### Accessing the Census Generator

1. In the **Simulation Builder**, go to the **Agents** section
2. Click the **Generate Personas** button (sparkle icon)
3. In the modal, select the **Census / Distribution** tab (next to "LLM Generation")

### Distribution Formats

The census generator accepts two formats:

#### Independent Marginals

Each dimension is sampled independently. Specify categories and their proportions (must sum to 1.0 per dimension):

```json
{
  "age": {"18-25": 0.3, "26-40": 0.4, "41-60": 0.2, "60+": 0.1},
  "income": {"low": 0.4, "medium": 0.35, "high": 0.25},
  "education": {"high_school": 0.3, "bachelors": 0.45, "graduate": 0.25}
}
```

This produces agents with independently sampled values for each dimension. For example, an agent might be age "26-40", income "low", education "graduate".

#### Joint Profiles

Pre-defined combinations with explicit weights. Use this when correlations between dimensions matter:

```json
{
  "joint_profiles": [
    {"weight": 0.3, "age": "18-25", "occupation": "student", "income": "low"},
    {"weight": 0.25, "age": "26-40", "occupation": "engineer", "income": "high"},
    {"weight": 0.25, "age": "41-60", "occupation": "teacher", "income": "medium"},
    {"weight": 0.2, "age": "60+", "occupation": "retired", "income": "low"}
  ]
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| **Number of Agents** | How many agents to generate (1-100) | 10 |
| **Random Seed** | Fixed seed for reproducible sampling. Same seed + same distribution = same agents | (empty = random) |
| **Context** | Optional scenario context that shapes how demographics become memories | (empty) |
| **Enrich with LLM** | Use the configured LLM to convert demographic profiles into natural-language memories and goals | Off |

### Step-by-Step Usage

1. Open the **Census / Distribution** tab in the persona generator
2. Enter or paste your distribution JSON in the text editor. A default example is pre-filled.
3. Alternatively, click **Upload CSV** or **Upload JSON** to load a distribution file
4. Set the number of agents
5. Optionally set a random seed for reproducibility
6. Optionally add context (e.g., "Residents of a coastal fishing village in Southeast Asia")
7. Toggle **Enrich with LLM** if you want natural-language memories instead of factual demographic strings
8. Click **Generate from Distribution**
9. Review the generated personas and the distribution summary table
10. Select the personas you want, then click **Add Selected** to add them as agents

### CSV File Format

If uploading a CSV distribution file, use this format:

```csv
dimension,category,proportion
age,18-25,0.3
age,26-40,0.4
age,41-60,0.2
age,60+,0.1
income,low,0.4
income,medium,0.35
income,high,0.25
```

### With vs. Without LLM Enrichment

**Without enrichment** (fast, no API calls):
- Agent memories are factual demographic statements: "Age group: 26-40", "Income level: medium"
- Goals are generic: "Participate in the simulation based on your background"
- Good for large populations where individual personality is less important

**With enrichment** (slower, requires LLM):
- Demographics are woven into natural-language backstories
- Goals are personalized based on demographic profile and context
- Better for smaller populations (5-20 agents) where individual behavior matters

### API Endpoints

```
POST /api/generate-personas-census   — generate agents from distribution
POST /api/parse-distribution         — parse a CSV or JSON file into a distribution spec
```

---

## 3. Structured Action Constraints

Define a set of allowed actions that agents must choose from, replacing open-ended free-text responses with structured choices. This makes agent behavior more analyzable and comparable across runs.

### When to Use This

- You need agents to choose from a defined action space (like game theory scenarios)
- You want to count how often agents choose each action across multiple runs
- Your research requires categorical action data, not free-text narratives
- You want to constrain agents to realistic options in a policy simulation

### Where to Find It

The **Available Actions** editor appears in the **Simulation Builder**, below the agent list in the left column. It is collapsed by default.

### Defining Actions

1. Click the **Available Actions** header to expand it, or click **+ Add Action**
2. For each action, fill in:

| Field | Required | Description |
|-------|----------|-------------|
| **Name** | Yes | Short action identifier (e.g., "COOPERATE", "VOTE_YES", "INVEST") |
| **Description** | No | Explanation of what this action means in context |
| **Condition** | No | When this action is available (e.g., "only after round 3", "only if funds > $1000") |

3. Add as many actions as needed. Click the X button to remove an action.
4. When collapsed, defined actions appear as blue tag pills for quick reference.

### Example: Policy Voting Scenario

```
Action 1:
  Name: VOTE_APPROVE
  Description: Vote to approve the proposed policy as written
  Condition: (none)

Action 2:
  Name: VOTE_REJECT
  Description: Vote to reject the proposed policy
  Condition: (none)

Action 3:
  Name: PROPOSE_AMENDMENT
  Description: Propose a specific modification to the policy before voting
  Condition: Only available in rounds 1-3

Action 4:
  Name: ABSTAIN
  Description: Abstain from voting, citing insufficient information
  Condition: (none)
```

### How It Works

When actions are defined:

1. **Global injection**: The action list is appended to the simulation premise as an "AVAILABLE ACTIONS" section. All agents see: "Agents should ONLY choose from: [action list]"
2. **Per-agent injection**: If an agent has specific allowed actions (configured in the agent editor), only those actions are injected into that agent's memory as a constraint
3. **Agents are instructed** to select from the defined actions rather than generating free-form responses

### Per-Agent Action Overrides

You can restrict individual agents to a subset of the global actions:

1. Open the **Agent Editor** for a specific agent
2. In the **Available Actions** field, list the action names this agent can use
3. If left empty, the agent can use all globally defined actions

This is useful when different roles have different capabilities. For example, in a legislative simulation, only the chairperson might have a "CALL_VOTE" action.

### Analyzing Constrained Actions

With structured actions, your exported CSV becomes much easier to analyze:

```python
import pandas as pd

df = pd.read_csv("simulation_export.csv")
actions = df[df["data_type"] == "action"]

# Count action frequencies per agent
action_counts = actions.groupby(["agent_name", "action"]).size().unstack(fill_value=0)

# Cooperation rate
total = len(actions)
cooperate = len(actions[actions["action"].str.contains("COOPERATE")])
print(f"Cooperation rate: {cooperate/total:.1%}")
```

---

## 4. Batch Runs with Parameter Sweeps

Run the same simulation configuration multiple times, optionally varying parameters like temperature or step count across runs. Essential for statistical analysis, reproducibility checks, and sensitivity analysis.

### When to Use This

- You need multiple runs to compute averages and confidence intervals
- You want to test how LLM temperature affects outcomes
- You are conducting sensitivity analysis on simulation parameters
- You need to verify that results are robust, not artifacts of a single run

### Accessing Batch Runs

1. In the **Run** panel, configure your LLM settings as usual
2. Click the **Batch** button next to "Run Simulation"
3. The Batch Run modal opens

### Batch Configuration

| Option | Description | Range |
|--------|-------------|-------|
| **Runs per Combination** | How many times to run each parameter combination | 1-50 |
| **Batch Name** | Optional label for this batch (defaults to current date) | Free text |

### Parameter Sweeps

Parameter sweeps let you vary a setting across runs. Each unique combination of sweep values is run the specified number of times.

1. Click **+ Add Parameter** to add a sweep dimension
2. Select the parameter to vary:
   - **Temperature** — LLM sampling temperature (affects creativity/randomness)
   - **Max Steps** — Number of simulation steps
3. Enter comma-separated values to sweep over

**Example:**
- Parameter: Temperature, Values: `0.3, 0.5, 0.7, 1.0`
- Runs per Combination: 3

This produces 4 temperature values x 3 runs = **12 total runs**. The estimated total is shown at the bottom of the configuration panel before you start.

### Running a Batch

1. Configure runs and sweep parameters
2. The summary line shows: "Total runs: **N**" with a breakdown if sweeps are active
3. Click **Start Batch (N runs)**
4. The modal switches to a progress view:
   - A progress bar showing completed/total runs
   - A results table updating in real time with columns: run number, parameters, status, elapsed time
5. Each run executes sequentially — one at a time — using the same execution engine as single runs

### During Execution

- The **progress bar** fills as runs complete (green when done, yellow if cancelled)
- Each completed run appears in the **results table** with its status (completed/failed) and elapsed time
- Click **Cancel Batch** to stop after the current run finishes

### After Completion

When the batch finishes (or is cancelled), three buttons appear:

- **Export CSV** — Downloads an aggregated CSV with results from all runs, using the structured data exporter (Feature 1). Each row includes the run index and parameter values.
- **New Batch** — Reset the modal to configure and start another batch
- **Done** — Close the modal and return to the main interface

### Batch Results CSV

The exported CSV includes:

| Column | Description |
|--------|-------------|
| `run_index` | Which run (0, 1, 2, ...) |
| `parameters` | The parameter values for this run (e.g., `temperature=0.7`) |
| `repeat` | Which repeat within this parameter combination |
| `status` | `completed` or `failed` |
| `elapsed_seconds` | How long this run took |
| `log_filename` | Path to the individual run's HTML log |
| `error` | Error message if the run failed |

Individual run logs are saved with the prefix `batch_{batch_id}_run{index}_` in the `logs/` directory.

### API Endpoints

For programmatic or automated batch execution:

```
POST /api/batch/execute         — SSE stream of batch progress events
GET  /api/batch/list            — list all batches
GET  /api/batch/{id}/status     — current batch state
POST /api/batch/{id}/cancel     — cancel remaining runs
GET  /api/batch/{id}/export-csv — aggregated CSV from all completed runs
```

The SSE stream emits these event types:
- `batch_start` — includes `batch_id` and `total_runs`
- `run_complete` — includes `run_result` and `completed_runs` count
- `batch_complete` — all runs finished
- `batch_cancelled` — batch was cancelled

### Example: Temperature Sensitivity Study

**Goal:** Test whether LLM temperature affects cooperation rates in a Prisoner's Dilemma.

1. Configure a Prisoner's Dilemma scenario (or load the template)
2. Open **Batch Run**
3. Set **Runs per Combination** to 5
4. Add parameter sweep: **Temperature** = `0.1, 0.3, 0.5, 0.7, 1.0`
5. Start the batch (25 total runs)
6. Export the aggregated CSV
7. Analyze:

```python
import pandas as pd

df = pd.read_csv("batch_results.csv")

# Group by temperature, compute cooperation rate per group
for temp, group in df.groupby("parameters"):
    completed = group[group["status"] == "completed"]
    print(f"{temp}: {len(completed)}/{len(group)} completed, "
          f"avg time: {completed['elapsed_seconds'].mean():.1f}s")
```

For deeper analysis, load each individual run's exported CSV (using Feature 1's endpoint with each `log_filename`) to examine per-step agent behavior across temperature conditions.

---

## 5. Putting It All Together: A Research Workflow

Here is how the four features combine for a complete quantitative research workflow.

### Step 1: Design Your Population (Census Generator)

Define your agent population using real demographic data:

```json
{
  "age": {"18-30": 0.35, "31-50": 0.40, "51+": 0.25},
  "education": {"secondary": 0.40, "tertiary": 0.45, "postgraduate": 0.15},
  "income": {"below_median": 0.55, "above_median": 0.45}
}
```

Generate 20 agents with a fixed seed (e.g., `42`) for reproducibility. Enable LLM enrichment to give each agent a distinct backstory aligned with their demographic profile.

### Step 2: Define the Action Space (Action Constraints)

Set up structured actions so you can count and compare choices:

```
SUPPORT_POLICY — Vote in favor of the proposed regulation
OPPOSE_POLICY — Vote against the proposed regulation
NEGOTIATE — Propose a compromise or amendment
DEFER — Delay decision, request more information
```

### Step 3: Configure Grounded Variables

Track the quantitative outcomes you care about:

- `policy_support_percentage` — percentage of agents supporting the policy
- `negotiation_rounds` — how many rounds of negotiation occurred
- `compromise_adopted` — boolean, whether a compromise was reached

### Step 4: Run Batch with Sweeps (Batch Runner)

Run 5 repetitions at each of 3 temperature settings:

- Temperature: `0.3, 0.5, 0.8`
- Runs per combination: 5
- Total: 15 runs

### Step 5: Export and Analyze (Data Export)

1. Export the batch CSV for run-level summaries
2. For each run, export the detailed CSV for step-by-step agent actions and variable trajectories
3. Load into your analysis tool:

```python
import pandas as pd
import glob

# Load all individual run exports
all_runs = []
for f in glob.glob("logs/batch_*_export.csv"):
    df = pd.read_csv(f)
    df["source"] = f
    all_runs.append(df)

combined = pd.concat(all_runs)

# Analyze action frequencies by demographic group
actions = combined[combined["data_type"] == "action"]
# ... join with agent demographic data for cross-tabulation
```

### Summary

| Research Need | Feature |
|--------------|---------|
| Representative agent populations | Census Generator |
| Categorical action data | Action Constraints |
| Quantitative outcome tracking | Grounded Variables + Data Export |
| Statistical robustness | Batch Runs |
| Sensitivity analysis | Parameter Sweeps |
| Reproducibility | Census seed + fixed temperature |

---

## Further Reading

- [Simulation Building Guide](SIMULATION_BUILDING_GUIDE.md) — Full guide to building simulations, including grounded variables, critical decision points, and engine types
- [Simulation Templates Guide](SIMULATION_TEMPLATES_GUIDE.md) — Documentation of all built-in templates and prefab types
- [Grounded Variables Post-Processing](GROUNDED_VARIABLES_POST_PROCESSING.md) — Advanced analysis of grounded variable data
