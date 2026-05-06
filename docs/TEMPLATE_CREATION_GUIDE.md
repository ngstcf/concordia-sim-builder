# Creating Simulation Templates

This guide shows you how to add a new simulation template to the Concordia Simulation Builder. A template is a Python dict that pre-fills the web interface with a ready-to-run scenario — agents, game master, memories, and tracked variables.

---

## Anatomy of a Template

Every template is a single file in `backend/api/templates/` containing a `TEMPLATE` dict:

```python
TEMPLATE = {
    "name": "Template Name",
    "description": "One-paragraph description. Include research applications.",
    "config": {
        "premise": "...",
        "max_steps": 15,
        "engine_type": "sequential",
        "agents": [...],
        "game_master": {...},
        "shared_memories": [...],
        "player_specific_context": {...},
    }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name in the template picker |
| `description` | Yes | Shown in the picker. Mention research applications and key references |
| `config.premise` | Yes | The scenario description — setting, rules, initial conditions |
| `config.max_steps` | No | Range 1-1000, default 100. Steps = simulation turns |
| `config.engine_type` | No | Default `"sequential"`. See Engine Types below |
| `config.agents` | Yes | At least 1 agent. See Agent Config |
| `config.game_master` | Yes | See Game Master Config |
| `config.shared_memories` | No | World knowledge every agent starts with |
| `config.player_specific_context` | No | Private info per character (keyed by agent name) |
| `config.player_specific_memories` | No | Per-character memory lists for the formative memories initializer (keyed by agent name) |
| `config.checkpoint_interval` | No | Range 1-100, default 5. Save every N steps |

---

## Writing the Premise

The premise is the most important field. It tells the LLM what world the agents inhabit. A strong premise includes:

- **Setting** — Where and when
- **Initial state** — Current situation with specific details and numbers
- **Stakes** — What happens if agents succeed or fail
- **Available actions** — What agents can actually do
- **End condition** — How the simulation concludes

Use multi-line strings for readability:

```python
"premise": """A closed-door advisory session at the Ministry of Digital Affairs.
The minister has circulated a draft framework for national AI regulation and
convened three advisors to stress-test it before public consultation..."""
```

---

## Agent Config

Each agent in the `agents` list:

```python
{
    "id": "dr-okafor",                    # Unique slug (required)
    "name": "Dr. Okafor",                 # Display name (required)
    "prefab": "conversational__Entity",   # Behavior template (required)
    "goal": "Defend the framework...",    # Agent's objective
    "memories": [                          # Pre-loaded memories (list of strings)
        "Dr. Okafor is a professor of Technology Law...",
        "She spent 18 months consulting 40 stakeholders...",
    ],
    "randomize_choices": True,             # Add randomness to LLM choices
    "components": {                        # Psychological components (optional)
        "personality_traits": {...},
        "values": {...},
        "emotion": {...},
        "cognitive_bias": {...},
    }
}
```

### Entity Prefabs

| Prefab | Best For |
|--------|----------|
| `basic__Entity` | General-purpose agent with LLM reasoning |
| `basic_with_plan__Entity` | Agents that need multi-step planning |
| `conversational__Entity` | Dialogue-heavy scenarios (debates, discussions) |
| `rational__Entity` | Game-theoretic scenarios with strategic choices |
| `basic_scripted__Entity` | Pre-programmed responses (no LLM for actions) |
| `context_aware_scripted__Entity` | Scripted but adapts to context |
| `puppet__Entity` | Human-controlled via the step controller |

### Psychological Components

All components are optional. Add them to shape agent behavior.

**Personality Traits** (Big Five model):

```python
"personality_traits": {
    "traits": {
        "openness": 4,           # 0-5: curiosity, creativity
        "conscientiousness": 5,  # 0-5: discipline, organization
        "agreeableness": 2,      # 0-5: empathy, cooperation
        "extraversion": 4,       # 0-5: social engagement
        "neuroticism": 2         # 0-5: emotional volatility
    }
}
```

**Values:**

```python
"values": {
    "core_values": ["intellectual_honesty", "practical_effectiveness"],
    "value_conflict": "regulatory_ambition_vs_implementation_reality"
}
```

**Emotion:**

```python
"emotion": {
    "current_emotion": "cautious_optimism",
    "emotion_intensity": "moderate"   # "low", "moderate", "strong", "very_high"
}
```

**Cognitive Bias:**

```python
"cognitive_bias": {
    "bias_type": "sunk_cost_fallacy",
    "effect": "Tends to defend past decisions even when new evidence contradicts them"
}
```

### Writing Good Memories

Memories are the most direct way to shape agent behavior. Each memory is a string that gets loaded into the agent's associative memory.

**Include:**
- Background and expertise (establishes credibility and knowledge domain)
- Specific data points (gives the LLM concrete facts to reference)
- Behavioral tendencies (how the agent argues, reacts, communicates)
- Weaknesses and blind spots (makes agents more realistic)

**Example:**

```python
"memories": [
    "Kwame Mensah is a senior technology strategist with 20 years of private sector experience.",
    "The minister assigned him the devil's advocate role — his job is to break the framework.",
    "He has seen three countries attempt similar frameworks — two were shelved within 18 months.",
    "He uses concrete scenarios and numbers to make critiques visceral.",
    "He can be relentless and occasionally crosses from productive challenge into intimidation.",
]
```

---

## Game Master Config

```python
"game_master": {
    "prefab": "dialogic__GameMaster",
    "name": "Session Facilitator",
    "acting_order": "game_master_choice",
    "parameters": {},
    "grounded_variables": [...],
    "critical_decision_points": [...],
    "contrib_components": [...],
    "allow_early_termination": True,
}
```

### Game Master Prefabs

| Prefab | Best For |
|--------|----------|
| `generic__GameMaster` | Default — works for most scenarios |
| `dialogic__GameMaster` | Conversation-driven scenarios (debates, roundtables) |
| `game_theoretic_and_dramaturgic__GameMaster` | Strategic games with payoff structures |
| `interviewer__GameMaster` | Interview and survey formats |
| `async_social_media__GameMaster` | Social media forum with posts and asynchronous interaction |
| `simultaneous_resolution_gm__GameMasterSimultaneous` | Simultaneous event resolution with location tracking, NPC events, and working memory |
| `space_ship__GameMaster` | Spaceship simulation with system health and failure states |
| `formative_memories_initializer__GameMaster` | Generate agent backstories from context |

The `simultaneous_resolution_gm__GameMasterSimultaneous` prefab accepts these parameters in `game_master.parameters`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_time` | string | — | Simulation start time (e.g. `"Tuesday, March 3, 2026 at 8:30 AM"`) |
| `time_period_minutes` | int | 15 | Real-time minutes each step represents |
| `locations` | string | — | Comma-separated location names |
| `game_rules` | string | — | Detailed game rules for the GM |
| `use_gm_working_memory` | bool | true | Enable GM working memory component |

### Acting Order

| Value | Behavior |
|-------|----------|
| `fixed` | Agents act in the order listed |
| `random` | Random order each step |
| `game_master_choice` | GM decides who acts next (default, most natural) |

---

## Grounded Variables

Track quantitative metrics as the simulation runs. The Game Master updates these based on what happens.

```python
"grounded_variables": [
    {
        "name": "framework_robustness",
        "variable_type": "numerical",
        "description": "How many of the 4 pillars survive scrutiny (0-4)",
        "default_value": 4,
        "min_value": 0,
        "max_value": 4,
        "update_rule": "Decreases when a pillar is shown to have a fundamental flaw"
    },
    {
        "name": "consensus_level",
        "variable_type": "categorical",
        "description": "Current panel alignment",
        "default_value": "divided",
        "allowed_values": ["divided", "partial_agreement", "consensus", "deadlock"],
        "update_rule": "Changes when advisors explicitly agree or disagree on recommendations"
    },
    {
        "name": "amendment_adopted",
        "variable_type": "boolean",
        "description": "Whether at least one concrete amendment has been accepted",
        "default_value": false,
        "update_rule": "Becomes true when both the drafter and at least one other advisor agree on a specific change"
    }
]
```

### Variable Types

| Type | Fields | Example |
|------|--------|---------|
| `numerical` | `min_value`, `max_value` | Team morale (0-100) |
| `categorical` | `allowed_values` | Project status: on_track, at_risk, critical |
| `boolean` | — | Whether a deal was reached |
| `percentage` | `min_value` (0), `max_value` (100) | Public approval rating |

### Grounded Variables Intro

Add a natural-language instruction to the GM parameters telling it what to track:

```python
"parameters": {
    "grounded_variables_intro": (
        "Track key outcomes throughout this session:\n"
        "- Framework robustness: How many pillars survive scrutiny\n"
        "- Flaws identified: Count of concrete weaknesses surfaced\n"
        "- Consensus level: Whether advisors converge or deadlock"
    )
}
```

---

## Critical Decision Points

Inject events at specific steps to change the simulation dynamics:

```python
"critical_decision_points": [
    {
        "step": 8,
        "event": "BREAKING NEWS: A major AI company announces it will relocate to a neighboring country if the registry requirement passes. This changes the political calculus."
    },
    {
        "step": 12,
        "event": "The minister joins the session and asks each advisor for their preliminary recommendation."
    }
]
```

---

## Player-Specific Context

Private information that only one character knows. Keyed by agent name (must match exactly):

```python
"player_specific_context": {
    "Dr. Okafor": "You know the AI Safety Authority section is the weakest pillar — you included it as a political concession, not because you believe in it.",
    "Kwame Mensah": "Two tech companies approached you with valid technical objections to the registry. Use their arguments but do not reveal the source.",
    "Ms. Tanaka": "The minister privately told you she will shelve the framework entirely if the panel cannot reach consensus."
}
```

This creates information asymmetry — agents act on different knowledge, producing realistic dynamics.

---

## Shared Memories

Facts that every agent knows at the start. Use these for world-building:

```python
"shared_memories": [
    "This is a closed-door advisory session convened by the Minister of Digital Affairs.",
    "The framework proposes four pillars: impact assessments, AI registry, sandboxes, and an AI Safety Authority.",
    "One advisor has been explicitly assigned the devil's advocate role.",
    "Three comparable frameworks have been attempted internationally — two were shelved.",
    "Civil society groups demanded regulation after an AI hiring tool was found to discriminate.",
]
```

---

## Engine Types

| Engine | Behavior | Use When |
|--------|----------|----------|
| `sequential` | Agents act one at a time, in GM-chosen order | Most scenarios (default) |
| `simultaneous` | All agents act in the same step | Auctions, votes, simultaneous decisions |
| `asynchronous` | Variable timing between agents | Social media, message-passing |
| `step_controller` | UI play/pause/step/stop buttons | Interactive demos, classroom use |
| `interview` | Structured Q&A format | Surveys, interviews |
| `survey` | Questionnaire format | Survey research |

---

## Advanced: Scenes (Game-Theoretic)

For `game_theoretic_and_dramaturgic__GameMaster`, structure the scenario into scenes with explicit action choices:

```python
"parameters": {
    "scenes": [
        {
            "scene_type": {
                "name": "decision",
                "game_master_name": "Game Show Host",
                "action_spec": {
                    "call_to_action": "What does {name} choose?",
                    "options": ["COOPERATE", "DEFECT"]
                }
            },
            "participants": ["Alex", "Sam"],
            "num_rounds": 4,
            "premise": {
                "Alex": ["You are in a Prisoner's Dilemma...", "Each round you choose..."],
                "Sam": ["You are in a Prisoner's Dilemma...", "Each round you choose..."]
            }
        }
    ]
}
```

**Important:** `num_rounds` must equal `max_steps`. The `premise` must be a dict mapping each participant to a list of context strings (not a plain string).

---

## Advanced: Nested Simulations

An agent can run a mini-simulation as part of its reasoning:

```python
{
    "id": "ambassador",
    "name": "Ambassador Nakamura",
    "prefab": "basic__Entity",
    "nested_simulation": {
        "premise": "A private back-channel conversation...",
        "max_steps": 5,
        "agents": [
            {"id": "n-bc", "name": "Nakamura", "prefab": "basic__Entity", "goal": "..."},
            {"id": "w-bc", "name": "Deputy Wei", "prefab": "basic__Entity", "goal": "..."},
        ],
        "shared_memories": ["This conversation is off the record."],
        "extraction_prompt": "What did Nakamura learn about the other side's real position?"
    }
}
```

The nested simulation runs automatically during the agent's `pre_act` phase and feeds the extracted result back as an observation.

---

## Advanced: Contrib GM Components

Add specialized behaviors to the Game Master:

```python
"contrib_components": [
    {
        "component_id": "death",
        "params": {"death_message": "{actor_name} has perished."}
    },
    {
        "component_id": "gm_working_memory",
        "params": {"num_memories_to_retrieve": 150}
    },
    {
        "component_id": "npc_event_generator",
        "params": {
            "scenario_context": "An isolated colony facing environmental hazards...",
            "event_probability": 0.25
        }
    },
    {
        "component_id": "location_based_filter",
        "params": {}
    },
    {
        "component_id": "spaceship_system",
        "params": {
            "system_name": "Life Support",
            "system_max_health": 100,
            "system_failure_probability": 0.15,
            "warning_message": "WARNING: {system_name} integrity compromised!"
        }
    }
]
```

---

## Registering Your Template

After creating the template file, register it in `backend/api/templates/__init__.py`:

1. Add the import:
```python
from .my_template import TEMPLATE as _my_template
```

2. Add the URL slug mapping:
```python
TEMPLATES: dict[str, dict] = {
    # ... existing templates ...
    "my-template": _my_template,
}
```

The template is now served by the API at `GET /api/simulations/templates/my-template`, but it won't appear in the web UI template picker until you register it in the frontend.

---

## Adding to the Template Chooser

The template picker is a searchable, filterable grid in the Simulation Builder. Three frontend files need updating.

### 1. Add a loader function in `frontend/src/utils/api.ts`

```typescript
export async function getMyTemplate(): Promise<SimulationTemplate> {
  const response = await api.get('/api/simulations/templates/my-template');
  return response.data;
}
```

The function name is arbitrary but should match the pattern `get<Name>Template`.

### 2. Add metadata in `frontend/src/components/SimulationBuilder/templateMetadata.ts`

**Import the loader** at the top of the file:

```typescript
import { ..., getMyTemplate } from '../../utils/api';
```

**Add a metadata entry** to the `TEMPLATES` array:

```typescript
{
  id: 'my-template',              // Must match TEMPLATE_LOADERS key
  name: 'Budget Committee',       // Display name in the picker
  description: 'Three department heads negotiate next year\'s budget allocation.',
  category: 'General Scenarios',  // See categories below
  tags: ['sequential', 'player-context'],  // See tags below
  agentCount: 3,
  stepCount: 10,
  engineType: 'sequential',
  gmPrefab: 'dialogic__GameMaster',
  agentNames: ['Director of Programs', 'Director of Operations', 'Director of Fundraising'],
  keywords: 'budget nonprofit negotiation allocation',  // For search
}
```

**Add the loader** to the `TEMPLATE_LOADERS` map:

```typescript
'my-template': getMyTemplate,
```

### 3. Categories and tags

**Categories** (pick one):

| Category | Use For |
|----------|---------|
| `Quick Start` | Simple 2-agent demos under 10 steps |
| `Prefab Demos` | Showcasing a specific prefab or component |
| `Research` | Research-oriented scenarios |
| `General Scenarios` | General-purpose simulations |
| `Advanced Scenarios` | Templates using advanced features (nested sims, step controller, etc.) |
| `SDG Scenarios` | UN Sustainable Development Goals scenarios |
| `Upstream Examples` | Adapted from Google DeepMind's upstream Concordia examples |

**Feature tags** (include all that apply):

| Tag | When to Use |
|-----|-------------|
| `sequential` / `simultaneous` / `async` / `interview` / `step-controller` | Matches the engine type |
| `player-context` | Template has `player_specific_context` |
| `grounded-vars` | Template has `grounded_variables` |
| `nested-sim` | Any agent has a `nested_simulation` |
| `scenes` | GM uses scene-based structure |
| `game-theory` | Uses `game_theoretic_and_dramaturgic__GameMaster` |
| `scripted` | Uses scripted entity prefabs |
| `questionnaire` | Uses `interviewer__GameMaster` with questionnaires |
| `critical-decisions` | Template has `critical_decision_points` |
| `sdg` | SDG-related scenario |
| `contrib-gm` | Uses `contrib_components` on the GM |
| `formative-mem` | Relies on formative memory generation |
| `measurements` | Designed to showcase measurement channels |
| `upstream` | Adapted from upstream Concordia |

**Keywords** — space-separated terms for free-text search. Include the domain, key concepts, and any non-obvious terms users might search for.

---

## Checklist

Before committing a new template:

- [ ] `name` and `description` are set (description mentions research applications)
- [ ] `premise` includes setting, stakes, and available actions
- [ ] Each agent has a unique `id`, a `name`, a `prefab`, and at least 3-5 memories
- [ ] Agent memories include background, data points, behavioral tendencies, and weaknesses
- [ ] `game_master.prefab` matches the scenario type (dialogic for debates, generic for most others)
- [ ] `shared_memories` establish the world every agent inhabits
- [ ] `max_steps` is appropriate (5-10 for quick demos, 15-25 for full scenarios)
- [ ] Template loads without errors: `python -c "from backend.api.templates import TEMPLATES; print(len(TEMPLATES))"`
- [ ] Registered in `__init__.py` with a URL-friendly slug
- [ ] Loader function added in `frontend/src/utils/api.ts`
- [ ] Metadata entry added in `templateMetadata.ts` (`TEMPLATES` array + `TEMPLATE_LOADERS` map)
- [ ] Category, tags, and keywords are accurate
- [ ] TypeScript compiles: `cd frontend && npx tsc --noEmit`
- [ ] Template count updated in `Readme.md`, `CHANGELOG.md`, and `documentation.html`

---

## Example: Minimal Template

```python
TEMPLATE = {
    "name": "Budget Committee",
    "description": "Three department heads negotiate next year's budget allocation.",
    "config": {
        "premise": """Annual budget meeting at a mid-size nonprofit. Total budget is $2M,
down 10% from last year. Three department heads must agree on allocations.
If they cannot agree in 10 rounds, the CEO will impose cuts evenly.""",
        "max_steps": 10,
        "engine_type": "sequential",
        "agents": [
            {
                "id": "programs",
                "name": "Director of Programs",
                "prefab": "conversational__Entity",
                "goal": "Protect the programs budget from cuts exceeding 5%",
                "memories": [
                    "The Director of Programs oversees 12 active projects serving 5,000 beneficiaries.",
                    "Two flagship projects are mid-cycle and cutting them would waste $300K already spent.",
                    "She has data showing program impact increased 22% last year.",
                ],
            },
            {
                "id": "operations",
                "name": "Director of Operations",
                "prefab": "conversational__Entity",
                "goal": "Secure funding for a critical IT infrastructure upgrade",
                "memories": [
                    "The Director of Operations manages facilities, IT, and HR for 45 staff.",
                    "The current server infrastructure is 8 years old and failed twice last quarter.",
                    "He has a $180K quote for the upgrade and argues it will save $50K/year in maintenance.",
                ],
            },
            {
                "id": "fundraising",
                "name": "Director of Fundraising",
                "prefab": "conversational__Entity",
                "goal": "Increase the fundraising budget to offset the overall shortfall",
                "memories": [
                    "The Director of Fundraising raised $1.8M last year on a $200K budget.",
                    "She has identified three new grant opportunities worth $500K total but needs staff to apply.",
                    "She argues that cutting fundraising to save money is self-defeating.",
                ],
            },
        ],
        "game_master": {
            "prefab": "dialogic__GameMaster",
            "name": "CEO",
            "acting_order": "game_master_choice",
            "parameters": {},
        },
        "shared_memories": [
            "This is the annual budget meeting. Total budget is $2M, down 10% from last year.",
            "If the three directors cannot agree, the CEO will impose equal 10% cuts to all departments.",
            "Last year's allocations: Programs $1.1M, Operations $600K, Fundraising $200K, Reserve $100K.",
        ],
    }
}
```
