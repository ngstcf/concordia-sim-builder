# Simulation Templates Guide

This guide explains every pre-built template in the Concordia Simulation Builder. Each template is a ready-to-run configuration that demonstrates a specific feature or scenario. Load any template from the **template dropdown** in the top-right of the Simulation Builder, then click **Load**.

You can run templates as-is or modify them to fit your needs. All parameters are editable after loading.

---

## Quick Reference

| Template | Category | Engine | Agents | What It Teaches |
|---|---|---|---|---|
| Coffee Shop Demo | Basic | Sequential | 2 | Minimal setup, how agents interact |
| Peace Negotiation | Basic | Sequential | 2 | Longer simulations, shared memories |
| Planning Agent | Prefab Types | Sequential | 3 | Agents that form and follow plans |
| Scripted Entity | Prefab Types | Sequential | 5 | Agents with pre-written dialogue lines |
| Context-Aware Moderator | Prefab Types | Sequential | 4 | Scripted agents that adapt to context |
| Dialogic Conversation | Prefab Types | Sequential | 2 | Natural back-and-forth dialogue |
| Strategic Game | Prefab Types | Sequential | 2 | Game theory with action choices |
| Interviewer | Prefab Types | Sequential | 1 | Structured questionnaire surveys |
| Formative Memories | Prefab Types | Sequential | 3 | Rich character backstories |
| Marketplace | Prefab Types | Sequential | 3 | Trading with BUY/SELL/HOLD actions |
| Vaccine Hesitancy Study | Research | Sequential | 5 | Psychological components on agents |
| Phishing Attack Simulation | Research | Sequential | 4 | Nested simulations (sims within sims) |
| Urban Gentrification | Research | Sequential | 6 | Grounded variables + decision points |
| Nested Simulation Demo | Advanced | Sequential | 2 | Agent-level mini-simulations |
| Grounded Variables Demo | Advanced | Sequential | 3 | Tracking numeric/categorical metrics |
| Rational Negotiators | New in v2.4 | Sequential | 2 | Utility-maximizing rational agents |
| Philosophy Roundtable | New in v2.4 | Sequential | 3 | Dialogue-optimized conversational agents |
| Social Media Debate | New in v2.4 | Asynchronous | 4 | Async engine for social media dynamics |
| Sealed-Bid Auction | New in v2.4 | Simultaneous | 4 | Simultaneous engine (all act at once) |
| Wizard-of-Oz CS Training | New in v2.4 | Simultaneous | 3 | Human-controlled puppet agents |
| Spaceship Crisis | New in v2.4 | Sequential | 3 | Planning agents in crisis scenarios |
| State Formation | SDG Scenarios | Sequential | 4 | Institution-building (SDG 16) |
| Labor Strike | SDG Scenarios | Sequential | 4 | Collective action (SDG 8) |
| Fishery Management | SDG Scenarios | Sequential | 4 | Common-pool resources (SDG 14) |
| Flood Evacuation | SDG Scenarios | Sequential | 5 | Emergency response (SDG 11/13) |
| Educational Opportunity | SDG Scenarios | Sequential | 4 | Social mobility (SDG 10) |

---

## Understanding the Parameters

Before diving into templates, here is what each configuration field means and how to get the most out of it.

### Scenario Parameters

| Parameter | Description |
|---|---|
| **Premise** | The opening narrative that sets the scene. This is the first thing the Game Master and agents "read" before the simulation starts. Write it like the opening paragraph of a story. |
| **Max Steps** | How many turns the simulation runs. Each step typically involves one agent acting and the Game Master narrating the result. More steps = longer simulation = more LLM API calls = higher cost. Start with 5-10 for testing. |
| **Engine Type** | How agents take turns. See [Engine Types](#engine-types) below. |

#### Writing an Effective Premise

The premise is the single most important piece of configuration. It sets the tone, establishes constraints, and frames the entire simulation. The LLM reads it as context for every decision.

**Good premise — specific, actionable, constrained:**
> The annual budget review at Apex Corp. The CEO has allocated $2 million to be split between Engineering and Marketing. Department heads must negotiate and agree. If they cannot agree within the allotted time, both departments receive a flat $800K (20% penalty for indecision).

**Weak premise — vague, no stakes:**
> Two people negotiate about a budget.

Tips:
- State the **setting** (where and when)
- State the **stakes** (what happens if they fail)
- State the **constraints** (deadlines, budgets, rules)
- Include **numbers** when relevant — LLMs respond well to specific quantities
- You can embed GM instructions in the premise: "The mediator should prioritize de-escalation" or "Focus on the economic impact of each decision"

### Engine Types

| Engine | How It Works | Best For |
|---|---|---|
| **Sequential** | Agents take turns one at a time. The Game Master decides who goes next (unless Acting Order is Fixed). | Dialogue, negotiations, turn-based games. Most templates use this. |
| **Simultaneous** | All agents submit their actions at the same time, without seeing what others chose. Actions are revealed together after all agents have committed. | Auctions, voting, coordination games, any scenario where seeing others' choices would change behavior. |
| **Asynchronous** | Agents act independently on their own timelines. No fixed turn order — an agent may act multiple times before another acts. | Social media simulations, forum discussions, scenarios where agents don't need to wait for each other. |
| **Interview** | A structured Q&A format. The interviewer (Game Master) presents questions and each respondent answers in turn. Agents remember previous answers and may change behavior. | Surveys, structured interviews, focus groups. |
| **Survey** | Like Interview, but agents do NOT update their memory between questions. Each question is answered independently from a "blank slate." | Psychological surveys where question-order effects should be minimized. |

**Choosing an engine:** Ask yourself: "Should agents see each other's actions before deciding?" If yes, use Sequential. If no, use Simultaneous. If the scenario is social-media-like, use Asynchronous. If you're running a questionnaire, choose Interview (if order matters) or Survey (if not).

### Agent Parameters

| Parameter | Description |
|---|---|
| **Name** | The agent's display name. Used in dialogue ("Alice says...") and as the `{name}` placeholder in action specs. Use distinctive names — the LLM uses the name to maintain character consistency. |
| **Prefab Type** | The agent's behavior template. See [Agent Prefabs](#agent-prefabs) below. |
| **Goal** | What the agent is trying to achieve. This strongly guides the agent's decisions. Be specific — see below. |
| **Pre-loaded Memories** | Facts the agent "knows" before the simulation starts. One per line. These shape personality, knowledge, and behavior. |
| **Randomize Action Choices** | When the agent must pick from a list of options, should the option order be shuffled? Turn OFF for strategic games where option order matters. |
| **Components** | Optional psychological traits, biases, or behavioral modifiers. See [Components](#psychological-components). |

#### Writing Effective Goals

The goal is the agent's primary directive. The LLM references it at every decision point.

| Goal Quality | Example | Why |
|---|---|---|
| Too vague | "Do well" | No direction for decisions |
| Too rigid | "Say exactly these words" | Agent can't adapt to the situation |
| Good | "Secure at least $1.2M for Engineering while maintaining a good working relationship with Jordan" | Specific target + secondary constraint |
| Good | "Find a compromise both parties can accept, focusing on short-term ceasefire before territorial issues" | Priority ordering guides trade-offs |

Tips:
- Include **quantitative targets** when possible ("at least $1M", "within 30 days")
- Add **secondary objectives** to create realistic trade-offs ("while maintaining a good relationship")
- State **priorities** when objectives conflict ("prioritize crew safety over mission completion")
- Avoid **meta-instructions** ("act naturally" or "be a good agent") — describe what the character wants, not how the LLM should behave

#### Writing Effective Memories

Memories are facts loaded into the agent's long-term memory before the simulation starts. The agent recalls relevant memories based on the current situation.

**How memories work internally:** Each memory is stored as a separate text embedding. When the agent needs to decide, the system retrieves the most relevant memories based on semantic similarity to the current context. This means:

- **First memory is not always most important** — relevance is based on semantic matching, not order
- **Each memory should be one self-contained fact** — don't put multiple ideas in one line
- **More specific = better retrieval** — "Alice has a PhD in Marine Biology from MIT" retrieves better than "Alice is educated"
- **4-8 memories is the sweet spot** — too few and the agent is bland, too many and important ones get diluted

| Memory Type | Example | Purpose |
|---|---|---|
| Identity | "Priya is the VP of Engineering at Apex Corp." | Who the agent is |
| Knowledge | "Engineering shipped 3 major products last year, generating 70% of revenue." | Facts they can reference |
| Personality | "Priya values data-driven arguments over emotional appeals." | How they behave |
| Relationship | "Priya trusts Jordan professionally but disagrees on budget priorities." | Social dynamics |
| Constraint | "Priya's team needs $1M minimum to maintain current projects." | Decision boundaries |
| History | "Last year Engineering received $1.1M and Marketing received $900K." | Precedent and context |

### Agent Prefabs

| Prefab | Behavior | Internal Components | When to Use |
|---|---|---|---|
| **basic** | General-purpose agent with memory, observation, and action. Has identity, goals, observation, recent memories, and relevant memories components. | ~8 components | Default choice for most simulations. |
| **basic_with_plan** | Like basic, plus a planning component that formulates multi-step plans and updates them each turn. | ~10 components | When agents need to think ahead: project planning, crisis management, strategy. |
| **basic_scripted** | Follows a pre-written script of dialogue lines in exact order. Ignores simulation context entirely — always delivers the next line. | Script component | Focus group moderators, experiment confederates, tutorial NPCs. |
| **context_aware_scripted** | Has scripted lines as a guide but adapts delivery based on what other agents said. The script is a "topic guide" not a rigid teleprompter. | Script + observation | Support group facilitators, adaptive moderators who need structure but flexibility. |
| **conversational** | Optimized for natural back-and-forth dialogue. Has stronger listening/responding components. Better at referencing what others actually said. | ~10 dialogue-tuned components | Debates, therapy sessions, interviews, any dialogue-heavy scenario. |
| **rational** | Makes decisions by explicitly weighing expected utility. Has an internal reasoning step that evaluates costs and benefits before acting. | ~10 components + utility calc | Negotiations, economic simulations, game theory experiments. |
| **puppet** | Does not generate its own actions. Waits for external input. Other agents interact with it normally. | Minimal (externally driven) | Wizard-of-Oz experiments, human-in-the-loop studies, controlled experiments. |
| **minimal** | Bare-minimum agent with very few internal components. Fast but shallow reasoning. | ~3 components | Performance testing, large-scale simulations where you need many simple agents. |

**Mixing prefabs in one simulation:** You can use different prefabs for different agents. For example, one `basic_with_plan__Entity` commander + two `basic__Entity` crew members. Or one `basic_scripted__Entity` moderator + four `basic__Entity` participants.

### Game Master Parameters

The Game Master (GM) is the narrator and referee. It is NOT an agent — it does not have a goal or memories in the same way. Instead, its behavior is shaped by several configuration surfaces:

| Parameter | Description | How It Affects Behavior |
|---|---|---|
| **Name** | The GM's display name and persona. | The LLM uses this as the GM's identity. "UN Mediator" makes it neutral. "Hawkish Advisor" makes it biased. "Crisis Dispatch" makes it urgent. |
| **Prefab Type** | The GM's behavior template. | Determines what the GM does mechanically — narrate, run scenes, administer surveys, etc. See [Game Master Prefabs](#game-master-prefabs). |
| **Acting Order** | How the GM picks who acts next. | **Fixed** = same order every round (Agent 1, Agent 2, Agent 1...). **Random** = shuffled each round. **Game Master Choice** = the GM (via the LLM) decides who should speak next based on narrative context. |
| **Grounded Variables Introduction** | Free text that tells the GM what to track. | This text is injected into the GM's prompt at the start. Use it to define the GM's objectives, tracking priorities, or narrative focus. See [Shaping the Game Master](#shaping-the-game-master). |
| **Parameters (JSON)** | Advanced configuration specific to the GM prefab. | The visual editors (Scene Editor, Questionnaire Builder) populate this automatically. You can also edit it directly for fine-grained control. |

#### Shaping the Game Master

The GM has no "Goal" field in the UI, but you have four ways to steer its behavior:

**1. The GM Name (persona)**

The name acts as a role. The LLM uses it to determine tone and perspective.

| Name | Effect |
|---|---|
| "Narrator" | Neutral, observational, literary tone |
| "UN Mediator" | Neutral, diplomatic, focused on finding common ground |
| "Antagonistic Referee" | Confrontational, highlights disagreements |
| "Crisis Dispatch" | Urgent, focused on time pressure and safety |
| "Research Observer" | Academic, analytical, takes notes on behavior |

**2. The Premise**

The GM reads the premise before every decision. You can embed GM-specific instructions directly:

> ...The mediator's mandate is to prioritize de-escalation over territorial resolution. The mediator should redirect any discussion of historical grievances back to concrete, present-day security arrangements.

**3. Grounded Variables Introduction**

The text box under **Game Master > Grounded Variables Introduction** is injected directly into the GM's context. Even if you don't define formal grounded variables, you can use this field as a "GM briefing":

> Your objective is to find a ceasefire framework acceptable to both parties. Prioritize de-escalation over territorial resolution. Track the following informally:
> - Trust level between the parties (are they engaging constructively?)
> - Concessions offered (what has each side put on the table?)
> - Emotional temperature (is the discussion heating up or cooling down?)
> Pay special attention to moments where one party acknowledges the other's concerns.

**4. The Acting Order**

Acting order is a surprisingly powerful lever:
- **Fixed** order means Agent 1 always speaks first — they set the agenda. This creates a power asymmetry.
- **Random** order prevents any agent from consistently setting the agenda. More realistic for social media and group discussions.
- **Game Master Choice** gives the GM (LLM) control over pacing. The GM may choose to let a quiet agent speak, or return to a heated exchange. This produces the most natural dialogues but is less predictable.

### Game Master Prefabs

| Prefab | Behavior | Visual Editor | When to Use |
|---|---|---|---|
| **generic** | Narrates events, tracks the world state, decides who acts next. Most flexible. | None (use JSON or the GM briefing fields) | Default choice. Works for most scenarios. |
| **dialogic** | Focused on facilitating conversation. Can end the simulation early when dialogue reaches a natural conclusion. | None | Therapy sessions, debates, interviews where natural endpoints matter. |
| **game_theoretic_and_dramaturgic** | Runs structured scenes with defined action choices (e.g., COOPERATE/DEFECT). Tracks scores and payoffs. | **Scene Editor** | Game theory, strategic decisions, any scenario with discrete action options. |
| **interviewer** | Administers structured questionnaires with Likert scales or multiple-choice questions. The GM is the interviewer. | **Questionnaire Builder** | Surveys, employee feedback, psychological assessments. |
| **open_ended_interviewer** | Like interviewer but with free-text responses instead of multiple choice. | **Questionnaire Builder** | Qualitative research, open-ended interviews. |
| **scripted** | Follows a scripted narrative arc. The GM has a predefined story structure it follows. | **Scene Editor** | Tutorials, demonstrations, controlled experiments. |
| **physically_situated_and_dramaturgic** | Tracks physical location and movement of agents in a defined space. Agents have positions and can move. | **Scene Editor** | Spatial simulations, evacuation drills, physical world scenarios. |
| **marketplace** | Manages an economic marketplace with trading mechanics (buy, sell, price discovery). | None (use JSON) | Buying/selling simulations, market experiments. |
| **async_social_media** | Simulates a social media platform with posts, replies, and feeds. | None | Online discourse studies, misinformation research, platform dynamics. |
| **space_ship** | Manages spaceship systems, resources, and crew decisions in a structured environment. | None (use JSON) | Spaceship scenarios, system management simulations. |

### Shared Memories

Facts that ALL agents know at the start. These are distinct from individual agent memories — every agent receives all shared memories regardless of their role.

**What to put in shared memories:**
- Time and place: "It is 2024 in New York City."
- Rules and constraints: "The total budget is $2 million, non-negotiable."
- Relationships: "Alice and Bob are colleagues who have worked together for 3 years."
- World state: "Both departments contributed to last year's record revenue."
- Meta-rules: "All interactions are being recorded for training evaluation."

**What NOT to put in shared memories:**
- Agent-specific knowledge (use individual memories instead)
- Information one agent has but another shouldn't (e.g., secret negotiations, hidden agendas)
- Redundant restatements of the premise

**How many:** 3-6 shared memories is typical. They complement the premise — the premise tells the story, shared memories establish the facts.

### Psychological Components

Optional modifiers you can add to any agent through the Agent Editor. Components are grouped by category in the dropdown. You can stack multiple components on one agent.

| Component | Category | Parameters | What It Does |
|---|---|---|---|
| **Personality Traits (Big Five)** | Psychological | openness, conscientiousness, extraversion, agreeableness, neuroticism (each 1-5) | Sets personality dimensions. A high-extraversion, low-agreeableness agent will be assertive and confrontational. |
| **Cognitive Bias** | Psychological | bias_type (dropdown), bias_strength (weak/moderate/strong) | Makes the agent exhibit a specific reasoning error. See bias types below. |
| **Current Emotion** | Psychological | current_emotion (dropdown), emotion_intensity (weak/moderate/strong) | Sets the agent's emotional state which colors their perception and decisions. |
| **Core Values** | Psychological | core_values (list), value_conflict (optional text) | Defines what the agent prioritizes morally. Add a value_conflict to create internal tension. |
| **Social Identity** | Social | group_membership (list), identification_strength (weak/moderate/strong) | Assigns group identities that trigger in-group favoritism and out-group skepticism. |
| **Theory of Planned Behavior** | Social | behavior, attitude, subjective_norm, perceived_control | Models how the agent evaluates a specific behavior based on personal attitude, social pressure, and perceived ability. |

**Cognitive Bias Types:**
| Bias | Effect on Agent |
|---|---|
| confirmation_bias | Seeks information confirming existing beliefs, dismisses contradictory evidence |
| availability_heuristic | Overweights easily recalled examples (recent events, vivid stories) |
| anchoring_bias | Fixates on initial numbers or proposals — first offer sets the range |
| sunk_cost_fallacy | Continues courses of action because of past investment, even when they're failing |
| overconfidence_bias | Overestimates accuracy of own judgments, underestimates uncertainty |

**Stacking components:** An agent can have multiple components simultaneously. For example, an agent with `confirmation_bias` (strong) + `Social Identity: ["Conservative"]` (strong) + `Core Values: ["tradition", "security"]` will strongly resist information that challenges conservative viewpoints. This is how the Vaccine Hesitancy template creates realistic skeptic behavior.

### Grounded Variables

Numeric or categorical values that the Game Master tracks and updates during the simulation. Configured under **Game Master > Grounded Variables** (click "+ Show").

| Variable Type | Default Range | Example | When to Use |
|---|---|---|---|
| **Numerical** | Any number, optional min/max | budget_remaining: $10,000 (min: 0, max: 50000) | Budgets, scores, populations, quantities |
| **Percentage** | 0-100 | team_morale: 70% | Satisfaction, approval, completion rates |
| **Categorical** | Choose from allowed values | project_status: on_track / at_risk / critical / completed | Status indicators, phases, qualitative states |
| **Boolean** | true/false | crisis_mode: false | Flags, toggles, binary states |

**How they work:** The GM reads the current variable values before narrating each step. It updates them based on what happened. For example, if an agent's action damaged team morale, the GM might reduce `team_morale` from 70 to 55.

**After the simulation:** Click "Extract Grounded Variables" on the results page to have an LLM read the simulation log and produce a step-by-step timeline of variable changes. This generates a chart showing how variables evolved.

**Update Rule:** The optional "Update Rule" field on each variable tells the GM how to change the value. Examples:
- "Increases when team members agree, decreases during conflicts"
- "Decreases by $500-$2000 each step based on decisions made"
- "Changes to 'critical' if budget_remaining drops below $2000"

### Critical Decision Points

Scripted moments at specific steps where the Game Master forces a structured decision. Configured under **Game Master > Critical Decision Points** (click "+ Show").

Each decision point has:
- **Step Number** — when it triggers (e.g., step 10 of 30)
- **Description** — what the decision is about, presented to the agents
- **Options** — the choices available (agents must pick one)

**How they work:** When the simulation reaches the specified step, the GM presents the decision to the agents instead of the normal free-form action. This ensures key plot points happen on schedule.

**When to use them:**
- Policy simulations where votes must happen at specific points
- Experiments where you need controlled stimuli at known intervals
- Scenarios with escalating stakes (introduce a crisis at step 15)

**Spacing:** Spread decision points evenly across the simulation. In a 30-step simulation, placing them at steps 10, 20, and 30 gives agents time to react between decisions.

### Nested Simulations

An advanced feature where an agent runs a mini-simulation internally to inform their decision-making. Configured in the **Agent Editor > Nested Simulation** section.

Each nested simulation has:
- **Premise** — the scenario for the mini-simulation ("Alice calls Bob to ask what to bring")
- **Max Steps** — how long the inner simulation runs (keep it short: 3-8 steps)
- **Agents** — the cast of the inner simulation (can be copies of outer agents or entirely different characters)
- **Shared Memories** — context for the inner simulation
- **Extraction Prompt** — tells the system what the outer agent should "learn" from running the inner simulation

**Practical example:** In the Phishing Attack template, three analysts each run their own inner simulation of a different attack scenario. Analyst 1 simulates a social engineering attack, Analyst 2 simulates a technical exploit, Analyst 3 simulates different employee responses. Then in the outer simulation, they discuss findings and recommend defenses.

**Cost consideration:** Nested simulations multiply LLM calls. An outer simulation with 15 steps and 3 agents each running 8-step inner simulations will make far more API calls than a flat 15-step simulation. Start with short inner simulations (3-5 steps).

### Scene Editor (Game-Theoretic GMs)

When you select `game_theoretic_and_dramaturgic`, `physically_situated_and_dramaturgic`, or `scripted` as the GM prefab, a **Scene Editor** appears below the GM configuration. Scenes define structured interactions.

Each scene has:
- **Scene Name** — a label for the interaction (e.g., "Trading Round", "Voting Phase")
- **Participants** — which agents participate (click agent names to toggle)
- **Number of Rounds** — how many times this scene repeats
- **Action Specification:**
  - **Call to Action** — the prompt shown to agents, using `{name}` as a placeholder. Example: "What does {name} choose to do this round?"
  - **Output Type** — `Free Text` (any response), `Multiple Choice` (pick from options), or `Numeric` (respond with a number)
  - **Options** — the choices available (only for Multiple Choice). Example: ["COOPERATE", "DEFECT"]

**Important:** For game-theoretic GMs, `max_steps` in the scenario config must equal the total `num_rounds` across all scenes. If you have one scene with 4 rounds, set max_steps to 4.

### Questionnaire Builder (Interviewer GMs)

When you select `interviewer` or `open_ended_interviewer` as the GM prefab, a **Questionnaire Builder** appears. It lets you design structured surveys.

Each questionnaire has:
- **Name** — e.g., "Job Satisfaction Survey"
- **Type** — Multiple Choice (Likert), Open Ended (free text), or Mixed
- **Observation Pre-prompt** — instructions shown before the survey begins
- **Questions** — each with:
  - **Statement** — the question text ("I am satisfied with my current role")
  - **Dimension** — a tag for analysis ("job_satisfaction")
  - **Pre-prompt** — scale instructions ("On a scale of 1 to 5...")
  - **Choices** — response options with Likert presets available (Agreement, Frequency, Satisfaction, Likelihood)
  - **Ascending Scale** — whether choice 1 is the lowest value

### Player-Specific Context (Formative Memories)

An alternative to individual agent memories for creating rich character backstories. Unlike memories (which are separate retrievable facts), player-specific context is a single block of text that forms the agent's core identity.

This field is available via JSON import/export (not directly in the UI builder). Add a `player_specific_context` key to the top-level config:

```json
{
  "player_specific_context": {
    "Jake Morrison": "Jake was the star quarterback of Riverside High, class of 2004. He led the team to two state championships...",
    "Priya Sharma": "Priya graduated valedictorian with a 4.0 GPA. She went on to Stanford..."
  }
}
```

Use this when agents need paragraph-length backstories that go beyond what individual memories can convey. The Formative Memories template demonstrates this.

---

## Template Details

### Basic Templates

#### Coffee Shop Demo

**Learning objectives:** Understand the basic simulation loop — how agents observe the world, recall memories, decide on an action, and how the Game Master narrates the outcome. This is the smallest possible simulation and the best place to start.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Simplest turn-taking model |
| Max Steps | 5 | Fast, cheap — runs in under a minute |
| Agents | 2 (Alice, Bob) | Minimal cast to see interaction |
| Agent Prefab | `basic__Entity` | Default agent with observation, memory, and action |
| Game Master | "Narrator" (`generic__GameMaster`) | Neutral narration, no special mechanics |
| Acting Order | Fixed | Alice always speaks first |

**The agents:**
- **Alice** — a software engineer. Goal: *"Have an interesting conversation with Bob and find out what he's working on."* Her memories establish her as a curious, sociable person who just moved to the neighborhood.
- **Bob** — a data scientist. Goal: *"Finish reviewing the dataset for the 3pm deadline while being polite to Alice."* His memories establish a deadline conflict — he wants to work but social pressure pulls him into conversation.

**What to observe when running:**
1. How does Alice's curiosity manifest in her actions? Does she ask direct questions or ease into conversation?
2. How does Bob balance his deadline pressure against politeness? Does he try to end the conversation or get drawn in?
3. How does the Narrator (GM) describe the scene — does it add atmospheric details?
4. Notice that each step has a cycle: the agent recalls relevant memories, considers its goal, and then acts.

**Suggested experiments for students:**
- Change Bob's goal to *"Find out what Alice does for work and whether she'd be interested in a data science collaboration."* Run again. How does aligning goals change the dynamic?
- Add a shared memory: *"The coffee shop is about to close in 10 minutes."* How does time pressure change behavior?
- Add a third agent (Charlie, the barista) with the goal *"Upsell the daily special to every customer."* How does a third participant change the conversation flow?
- Switch Acting Order to "Game Master Choice" and compare — does the GM create more natural turn-taking?

**Platform features demonstrated:** Basic simulation loop, agent memories, goal-driven behavior, sequential engine, fixed acting order.

---

#### Peace Negotiation

**Learning objectives:** Observe how deeply conflicting goals produce negotiation dynamics. Understand how shared memories establish common ground, how goal framing shapes strategy, and how a Game Master persona (the UN Mediator) influences the tone of the simulation.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Turn-based negotiation |
| Max Steps | 20 | Long enough for positions to evolve and concessions to emerge |
| Agents | 2 (Agent R, Agent U) | Two opposing national negotiators |
| Agent Prefab | `basic__Entity` | General-purpose agents |
| Game Master | "UN Mediator" (`generic__GameMaster`) | Neutral mediator persona shapes GM toward de-escalation |
| Acting Order | Fixed | Agent R speaks first — notice how this creates agenda-setting power |

**The agents:**
- **Agent R** (Russian Foreign Minister) — Goal: *Secure recognition of Crimea, ensure Ukrainian military neutrality, and achieve sanctions relief.* Memories include Russia's strategic interests, red lines around NATO expansion, economic pressure from sanctions, and willingness to negotiate on some territorial questions.
- **Agent U** (Ukrainian Foreign Minister) — Goal: *Restore territorial integrity, secure a path to NATO/EU membership, and obtain reparations.* Memories include Ukraine's sovereignty position, the human cost of conflict, Western alliance support, and willingness to discuss phased approaches.

**Shared memories (common ground):** Both agents know the conflict has lasted over two years, civilians are suffering, the international community is pressuring both sides, previous negotiations failed, and a ceasefire framework exists.

**What to observe when running:**
1. Do the agents start with maximalist positions and gradually soften? Or do they maintain hard lines?
2. Does the UN Mediator (GM) steer toward compromise, or does it let the agents drive?
3. Watch for "creative proposals" — agents sometimes invent solutions not explicitly in their goals
4. Does Agent R (who speaks first due to fixed order) set the agenda? Would random order change this?
5. At what step (if any) do you see the first genuine concession?

**Suggested experiments for students:**
- Change the GM name from "UN Mediator" to "Hawkish Advisor" and compare how the narration tone shifts
- Add a Grounded Variables Introduction to the GM: *"Track trust level between the parties (low/medium/high) and concessions offered by each side."* This gives the GM explicit metrics to monitor
- Add a third agent: a NATO representative with the goal *"Ensure any agreement includes security guarantees for Eastern Europe."* How does a third party change the bilateral dynamic?
- Reduce to 8 steps. Do agents skip the posturing phase and get to substance faster?
- Switch Acting Order to "Random" — does removing agenda-setting power change outcomes?

**Academic connections:** Negotiation theory (BATNA, ZOPA), two-level games (Putnam), conflict resolution frameworks, the role of mediators in international diplomacy.

**Platform features demonstrated:** Conflicting goals, shared memories as common ground, GM persona effects, long simulations with position evolution, fixed acting order as power asymmetry.

---

### Prefab Type Examples

#### Planning Agent

**Learning objectives:** Compare how `basic_with_plan__Entity` agents differ from `basic__Entity` agents. Planning agents create explicit multi-step plans and update them each turn, producing more strategic and forward-looking behavior rather than reactive step-by-step actions.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Turn-based planning discussion |
| Max Steps | 15 | Long enough for plans to form, adapt, and potentially conflict |
| Agents | 3 (Sarah, Marcus, Emily) | Three department heads with overlapping concerns |
| Agent Prefab | `basic_with_plan__Entity` | All three agents use the planning prefab |
| Game Master | "Strategy Facilitator" (`generic__GameMaster`) | Facilitates but doesn't direct |

**The agents:**
- **Sarah Chen** (CEO) — Goal: *Launch the product within 90 days while keeping all departments aligned.* Memories: Series B funding received, board expects results, believes thorough planning prevents costly mistakes.
- **Marcus Rodriguez** (VP Marketing) — Goal: *Secure commitments on product features and timeline so marketing can build the launch campaign.* Memories: Needs feature list 60 days before launch, previous launches were delayed, concerned about engineering over-promising.
- **Emily Watson** (VP Engineering) — Goal: *Protect the engineering team from unrealistic commitments while delivering a quality product.* Memories: Team is already stretched, won't promise features they can't deliver, knows the 90-day timeline is aggressive.

**What to observe when running:**
1. In the simulation log, look for explicit plan formation — planning agents will state things like "My plan is to first secure X, then negotiate Y..."
2. Watch for plan adaptation: when another agent introduces a constraint, does the planning agent update their approach?
3. Compare the first and last plans of each agent. How much did they change?
4. Notice how Sarah (CEO) tries to align the other two — does the planning prefab help her coordinate?

**Suggested experiments for students:**
- Change Emily to `basic__Entity` (non-planning) while keeping Sarah and Marcus as planners. Does Emily behave more reactively? Does she get outmaneuvered?
- Add a shared memory: *"A competitor is rumored to be launching a similar product in 60 days."* How does external pressure change the plans?
- Reduce max_steps to 6 and compare — do agents compress their planning, or do they fail to reach alignment?

**Academic connections:** Strategic planning theory, organizational alignment, principal-agent problems, bounded rationality.

---

#### Scripted Entity

**Learning objectives:** Understand the `basic_scripted__Entity` prefab — an agent that delivers pre-written lines in exact order regardless of what other agents say. This is essential for experiments requiring standardized stimuli (the same prompt delivered identically across multiple runs).

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Orderly focus group discussion |
| Max Steps | 10 | Enough for the moderator's 8 scripted prompts plus responses |
| Agents | 5 (1 scripted moderator + 4 free agents) | Mix of controlled and autonomous agents |
| Moderator Prefab | `basic_scripted__Entity` | Delivers lines from script, ignores context |
| Participant Prefab | `basic__Entity` | Free-responding agents |
| Game Master | "Focus Group Coordinator" (`generic__GameMaster`) | Manages turn order |

**The agents:**
- **Dr. Chen** (moderator, scripted) — Has 8 pre-written prompts that guide the focus group through a discussion about "LoveBot AI" (an AI dating assistant). Lines progress from introduction → feature questions → privacy concerns → final thoughts. Dr. Chen delivers these lines in exact order regardless of participant responses.
- **Jordan** (tech enthusiast) — Goal: advocate for AI innovation. Sees technology as the solution.
- **Sam** (privacy advocate) — Goal: raise ethical and data privacy concerns. Background in cybersecurity.
- **Maria** (romantic) — Goal: defend authentic human connection. English teacher who values organic relationships.
- **Alex** (skeptic) — Goal: question whether AI dating actually works. Marketing manager, skeptical of hype.

**What to observe when running:**
1. Notice that Dr. Chen's lines are delivered verbatim — they don't react to what participants say
2. Despite the scripted moderator, participants still respond naturally to each other
3. Watch for "off-script moments" — participants may raise topics the moderator's script didn't anticipate
4. The scripted agent guarantees that every focus group run covers the same topics in the same order

**Suggested experiments for students:**
- Run the simulation 3 times with the same configuration. Compare how participants respond to the same scripted prompts — this demonstrates how the scripted agent creates reproducible experimental conditions
- Replace Dr. Chen's prefab with `context_aware_scripted__Entity` and compare. How does context-awareness change the moderator's delivery?
- Change the participants' goals to all agree with AI dating. Does the discussion become less interesting? What does this tell us about agent diversity?

**Academic connections:** Experimental methodology (standardized stimuli), focus group research methods, the confederate technique in social psychology, internal validity.

---

#### Context-Aware Moderator

**Learning objectives:** Understand the difference between `basic_scripted__Entity` (rigid script) and `context_aware_scripted__Entity` (adaptive script). The context-aware version has the same guaranteed topic coverage but adapts its delivery based on what other agents said.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Support group discussion flow |
| Max Steps | 12 | Enough for 9 scripted topics plus participant responses |
| Agents | 4 (1 context-aware moderator + 3 free agents) | Adaptive facilitator + participants |
| Moderator Prefab | `context_aware_scripted__Entity` | Delivers scripted topics but adapts wording |
| Participant Prefab | `basic__Entity` | Free-responding agents |

**The agents:**
- **Sarah** (counselor, context-aware scripted) — Has 9 scripted topic prompts for a career crisis support group. The script covers: warm welcome → sharing invitation → emotional acknowledgment → validation of feelings → coping strategies → gratitude reflection → confidentiality → group appreciation → hopeful closure. Unlike a rigid script, Sarah adapts *how* she delivers each topic based on what participants just said.
- **Marcus** (45, recently laid off) — Identity loss after 20-year career. Struggles with self-worth.
- **Elena** (32, quit toxic job) — Voluntary departure but uncertain about career pivot. Considering entrepreneurship.
- **David** (55, long-term unemployed) — 8 months since layoff. Found meaning through volunteering but feels societal judgment.

**What to observe when running:**
1. Compare Sarah's actual lines to her script intent. Does she reference specific things participants said?
2. If Marcus shares something emotional, does Sarah's "emotional acknowledgment" line feel responsive?
3. Notice the guaranteed topic progression — all 9 topics are covered regardless of conversation twists

**Suggested experiments for students:**
- Replace Sarah with `basic_scripted__Entity` and run the same scenario. Compare the two outputs — which moderator creates a more natural group dynamic?
- Remove Sarah's script and make her a `basic__Entity` counselor. Does she still cover all the important topics? What does this tell us about the value of structured facilitation?

**Academic connections:** Semi-structured interview methodology, facilitated group discussion, therapeutic group dynamics, the balance between structure and flexibility in qualitative research.

---

#### Dialogic Conversation

**Learning objectives:** Understand the `dialogic__GameMaster` — a Game Master that facilitates natural conversation flow and can end the simulation early when the dialogue reaches a natural stopping point.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Two-person dialogue |
| Max Steps | 12 | Upper bound — may end earlier |
| Agents | 2 (counselor, patient) | Therapeutic dyad |
| Agent Prefab | `basic__Entity` | Standard agents (the dialogue optimization comes from the GM) |
| Game Master | `dialogic__GameMaster` | Facilitates natural conversation, can auto-terminate |
| Setting | Third therapy session | Established relationship context |

**The agents:**
- **Dr. Michael Brooks** (counselor) — Goal: *Practice active listening, ask reflective questions, help Jennifer explore her feelings about the career transition.* Memories establish him as an experienced therapist who uses Rogerian techniques, avoids giving direct advice, and focuses on emotional processing.
- **Jennifer Park** (patient) — Goal: *Work through anxiety about leaving her marketing job to start a small business.* Memories establish her as successful but unfulfilled, with a supportive partner, some savings, and a specific business idea (artisan bakery) but crippling self-doubt.

**What to observe when running:**
1. Does the dialogic GM produce more natural turn-taking than a generic GM would?
2. Does the conversation reach a natural stopping point before step 12? If so, the dialogic GM ended it early
3. Watch for active listening behaviors: does Dr. Brooks reflect Jennifer's statements back?
4. Notice how the GM manages the pace — does it slow down during emotional moments?

**Suggested experiments for students:**
- Replace the `dialogic__GameMaster` with `generic__GameMaster` and compare. The generic GM always runs for the full 12 steps — does the conversation feel forced toward the end?
- Give Jennifer a more specific immediate crisis: *"Jennifer learned today that her company is being acquired and she has 30 days to decide on a severance package."* How does urgency change the therapy dynamic?
- Change the agents to `conversational__Entity` prefab (dialogue-optimized) combined with the dialogic GM. Is the difference noticeable?

**Academic connections:** Rogerian therapy, active listening, therapeutic alliance, qualitative research interviewing techniques, conversation analysis.

---

#### Strategic Game (Prisoner's Dilemma)

**Learning objectives:** Understand `game_theoretic_and_dramaturgic__GameMaster` with structured scenes that present discrete action choices. This template models the classic Prisoner's Dilemma from game theory, demonstrating how agents reason about cooperation vs. defection when payoffs are asymmetric.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Agents see each other's previous choices |
| Max Steps | 4 | Exactly 4 rounds (must match scene num_rounds) |
| Agents | 2 (Alex, Sam) | Two players in iterated game |
| Agent Prefab | `basic__Entity` | Standard agents (game structure comes from the GM) |
| Game Master | "Game Show Host" (`game_theoretic_and_dramaturgic__GameMaster`) | Presents choices and tracks scores |
| Randomize Choices | OFF | Critical — option order must not bias the result |

**The agents:**
- **Alex** (Player 1) — Goal: *Maximize your total points across all rounds.* Memories establish Alex as a rational decision-maker who understands game theory and adapts strategy based on the opponent's pattern.
- **Sam** (Player 2) — Goal: *Maximize your total points using the tit-for-tat strategy.* Memories establish Sam as a game theory student who starts by cooperating and then mirrors the opponent's previous move.

**Payoff structure (defined in the scene's action spec):**
| | Sam COOPERATES | Sam DEFECTS |
|---|---|---|
| **Alex COOPERATES** | (3, 3) | (0, 5) |
| **Alex DEFECTS** | (5, 0) | (1, 1) |

**Key technical parameter — the `scenes` array:**
The GM parameters contain a `scenes` array with one scene: 4 rounds, both agents participate, choices are COOPERATE or DEFECT. The **Scene Editor** builds this visually. The `max_steps` in scenario config *must equal* the total `num_rounds` across all scenes.

**What to observe when running:**
1. Does Alex (the "rational" player) start by cooperating or defecting? The Nash equilibrium says defect, but most LLMs initially cooperate
2. Does Sam actually follow tit-for-tat as instructed in their goal?
3. Watch the payoff accumulation — which strategy wins over 4 rounds?
4. Look for strategic reasoning in the agent logs — do agents mention the payoff structure?

**Suggested experiments for students:**
- Increase to 10 rounds. Does more iteration change the equilibrium? (Axelrod's tournaments showed tit-for-tat dominates in iterated PD)
- Change Sam's goal to *"Always defect regardless of what Alex does."* How does a pure defector change the dynamic?
- Add two more agents and change the scene to include all 4. How does the Prisoner's Dilemma change with more players?
- Change Alex's goal to *"Maximize your points but also maintain a reputation as a trustworthy partner."* How does caring about reputation change behavior?
- Turn Randomize Choices ON and compare. Does option order ("COOPERATE, DEFECT" vs "DEFECT, COOPERATE") bias the agents? This tests ordering effects in LLM decision-making.

**Academic connections:** Game theory (Nash equilibrium, Pareto optimality), Axelrod's iterated Prisoner's Dilemma tournaments, cooperation theory, evolutionary game theory, the shadow of the future.

---

#### Interviewer (Employee Survey)

**Learning objectives:** Understand the `interviewer__GameMaster` — a Game Master that administers structured questionnaires with Likert scales. This template demonstrates how to use simulated agents as survey respondents, which is useful for pre-testing survey instruments or studying how agent configurations affect survey responses.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Interview | Structured Q&A format |
| Max Steps | 5 | One step per survey question |
| Agents | 1 (Jordan Lee) | Single respondent |
| Agent Prefab | `basic__Entity` | Standard agent (responds to structured prompts) |
| Game Master | "HR Representative" (`interviewer__GameMaster`) | Administers the questionnaire |

**The agent:**
- **Jordan Lee** (software developer) — Memories establish Jordan as a 2-year employee who is generally satisfied but has specific frustrations: good team, interesting work, but limited growth opportunities and occasional communication gaps with management.

**The questionnaire (defined in GM parameters):**
5 Likert-scale questions on the "Agreement" preset (Strongly Disagree → Strongly Agree):

| # | Statement | Dimension |
|---|---|---|
| 1 | "I am satisfied with my current role and responsibilities" | job_satisfaction |
| 2 | "Communication within my team is effective and transparent" | communication |
| 3 | "I have the resources and tools I need to do my job well" | resources |
| 4 | "I would recommend this company as a great place to work" | recommendation |
| 5 | "I feel my contributions are recognized and valued" | recognition |

**What to observe when running:**
1. Does Jordan's response pattern align with their memories? (satisfied overall, but frustrated with growth and communication)
2. Are responses consistent — does a "Disagree" on communication align with the memory about communication gaps?
3. Does the agent provide reasoning or just pick a number? The interview engine captures both.

**Suggested experiments for students:**
- Add 4 more agents with different satisfaction levels. Compare their response patterns — do the memories correctly drive Likert responses?
- Change the questionnaire type to "Open Ended" and see how the agent elaborates
- Add a "social desirability" bias component to Jordan. Does it inflate positive responses? This tests whether psychological components affect survey measurement
- Swap the Interview engine for Survey engine. In Interview mode, agents remember previous questions. In Survey mode, each question is answered independently. Compare whether the response pattern changes

**Academic connections:** Survey methodology, Likert scale design, social desirability bias, pre-testing survey instruments, the replication crisis (using simulations to explore question-order effects).

---

#### Formative Memories (High School Reunion)

**Learning objectives:** Understand `player_specific_context` — an alternative to individual memories that provides paragraph-length character backstories. This creates richer, more consistent characters than the separate-memory approach, at the cost of less precise memory retrieval.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Social conversation |
| Max Steps | 20 | Long enough for complex social dynamics |
| Agents | 3 (Jake, Priya, Mike) | Three former classmates |
| Agent Prefab | `basic__Entity` | Standard agents with rich backstories |
| Game Master | "Reunion Narrator" (`formative_memories_initializer__GameMaster`) | Narrates the reunion setting |
| Setting | 20-year high school reunion in the old gymnasium |

**The agents (using `player_specific_context`):**
- **Jake Morrison** — Former star quarterback who led the team to two state championships. Expected great things but became a high school football coach. His backstory is a narrative of humbled expectations, finding meaning in coaching, and quiet insecurity about being "the guy who peaked in high school."
- **Priya Sharma** — Valedictorian who went to MIT, then Harvard, now a tech executive. Her backstory covers academic drive, imposter syndrome despite success, distance from her blue-collar hometown roots, and curiosity about whether she missed out on the "normal" high school experience.
- **Mike O'Brien** — Class clown who nobody expected to succeed. Became a stand-up comedian in Chicago. His backstory covers using humor as a defense mechanism, complicated relationship with the class, a failed marriage, and genuine warmth beneath the jokes.

**What to observe when running:**
1. Do agents reference specific details from their backstories naturally, or do they feel generic?
2. Watch for social dynamics: does Priya feel superior? Does Jake feel inadequate? Does Mike deflect with humor?
3. Notice how shared high school history creates common ground while divergent life paths create tension
4. At step 20, is the conversation richer than it would be with just bullet-point memories?

**Suggested experiments for students:**
- Export the JSON, replace `player_specific_context` with equivalent bullet-point memories, and compare. Which produces more consistent characters?
- Add a 4th agent who was bullied in high school and is attending the reunion reluctantly. How does a character with negative associations change the dynamic?
- Change max_steps to 40 to see if the agents eventually exhaust their backstory material or keep producing novel interactions

**Academic connections:** Narrative identity theory, life course sociology, social class and reunions, the role of shared history in group dynamics, character consistency in agent-based models.

---

#### Marketplace (Farmers Market)

**Learning objectives:** Understand how `game_theoretic_and_dramaturgic__GameMaster` works for economic simulations with structured trading rounds. Each round, agents choose from discrete actions (BUY, SELL, HOLD) and the GM narrates market outcomes.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Agents see previous round outcomes before deciding |
| Max Steps | 10 | 10 trading rounds |
| Agents | 3 (Maria, David, Green Valley) | Three traders with different strategies |
| Agent Prefab | `basic__Entity` | Standard agents (trading structure from GM) |
| Game Master | "Market Coordinator" (`game_theoretic_and_dramaturgic__GameMaster`) | Runs trading rounds |

**The agents:**
- **Maria's Organic Farm** — 20 years of experience, strategic timing, premium pricing. Goal: maximize profit through selective selling.
- **David Chen** — Restaurant owner seeking quality ingredients at good prices. Goal: acquire enough stock for the week.
- **Green Valley Farms** — Family operation competing on price. Goal: undercut competitors and build market share.

**The scene:** One scene called "Trading Round" with 10 rounds. Each round, agents choose BUY (acquire goods at current price), SELL (offer goods to the market), or HOLD (wait for better conditions).

**What to observe when running:**
1. Does Maria (experienced) use HOLD strategically to wait for higher prices?
2. Does David (buyer) time purchases to avoid bidding wars?
3. Does Green Valley's price competition drive Maria's prices down?
4. Do agents adapt their strategy based on what others did in previous rounds?

**Suggested experiments for students:**
- Add a 4th agent: "City Inspector" who occasionally restricts certain sellers. How does regulatory uncertainty affect trading?
- Change the scene choices to BUY_LOW, BUY_HIGH, SELL_LOW, SELL_HIGH, HOLD — finer-grained pricing. Do agents price more carefully?
- Switch to `simultaneous` engine so traders commit their choices before seeing others. How does information asymmetry change market dynamics?

**Academic connections:** Market microstructure, supply and demand dynamics, strategic timing, price discovery, competition theory.

---

### Research Templates

#### Vaccine Hesitancy Study

**Learning objectives:** Understand how **psychological components** (cognitive biases, personality traits, social identity, values, emotions) affect agent behavior. This is the most component-heavy template and demonstrates how stacking multiple components on a single agent creates realistic psychological profiles.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Community discussion |
| Max Steps | 20 | Long enough to observe opinion evolution |
| Agents | 5 | Diverse psychological profiles |
| Game Master | "Community Health Discussion" (`generic__GameMaster`) | Neutral facilitation |

**The agents and their psychological profiles:**

| Agent | Role | Key Components | Expected Behavior |
|---|---|---|---|
| **Dr. Sarah Chen** | Public health doctor | Big Five (high conscientiousness, high agreeableness), Theory of Planned Behavior (favorable attitude, strong perceived control) | Evidence-based advocate, patient, presents data calmly |
| **Mike Johnson** | Small business owner, skeptic | Confirmation bias (strong), overconfidence bias (strong), Social Identity (libertarian), Values (personal freedom, autonomy) | Dismisses evidence, overestimates own judgment, frames as freedom issue |
| **Maria Garcia** | Teacher, undecided | Availability heuristic (moderate), Emotion (anxiety, moderate), Theory of Planned Behavior (ambivalent attitude) | Swayed by vivid stories, anxious, seeks reassurance |
| **James Wilson** | Factory worker, positive | Big Five (high agreeableness), Social Identity (community-oriented), Values (family, health) | Supportive of vaccination, influenced by community norms |
| **Lisa Thompson** | Concerned parent | Availability heuristic (moderate), Emotion (worry, moderate), Values (family safety), Social Identity (parent group) | Focuses on child safety stories, wants guarantees |

**What to observe when running:**
1. Does Mike's confirmation bias cause him to dismiss Dr. Chen's evidence? Watch for selective attention in his responses.
2. Does Maria's availability heuristic make her more responsive to vivid anecdotes than statistics?
3. Does the overconfidence bias make Mike more assertive than his knowledge warrants?
4. Do social identity effects emerge — does Mike appeal to "freedom" and James appeal to "community"?
5. Does Maria (undecided) shift position? If so, what influenced her — data, stories, or social pressure?

**Suggested experiments for students:**
- Remove all components from Mike and run again. How does "default" behavior differ from biased behavior?
- Give Dr. Chen a "condescension" emotion and see if it backfires — does being emotionally dismissive reduce her persuasiveness?
- Add `anchoring_bias` (strong) to Maria and see if the first piece of information she hears dominates her decision
- Run the simulation 5 times and track whether Maria's final position varies. This demonstrates stochasticity in LLM-driven agents.
- Add a `sunk_cost_fallacy` component to Mike — does he become even more entrenched in his initial position?

**Academic connections:** Health communication, the elaboration likelihood model (ELM), cognitive bias research, the theory of planned behavior (Ajzen), social identity theory (Tajfel), motivated reasoning, the backfire effect in vaccine messaging.

---

#### Phishing Attack Simulation

**Learning objectives:** Understand **nested simulations** — simulations-within-simulations where an agent runs an internal mini-simulation to inform their reasoning in the outer simulation. This models metacognitive processes: thinking through scenarios before making a recommendation.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Team discussion |
| Max Steps | 25 (outer) | Long deliberation with rich input from nested sims |
| Agents | 4 (3 analysts + 1 CISO) | Each analyst runs their own nested simulation |
| Nested Sim Steps | 8 each | Short inner simulations |
| Game Master | "Security Team Lead" (`generic__GameMaster`) | Coordinates the tabletop exercise |

**The agents and their nested simulations:**

| Agent | Role | Nested Simulation | Extraction Prompt |
|---|---|---|---|
| **Sarah** | Email security specialist | Simulates an attack chain: Hacker → User → IT Security. Models how a phishing email propagates through the organization. | "What was the most damaging outcome? Where did defenses fail?" |
| **Marcus** | Technical engineer | Simulates technical control failures: how authentication, firewalls, and monitoring respond to a breach. | "Which technical controls held? Which failed? What's the critical gap?" |
| **Elena** | Awareness manager | Simulates employee vulnerability patterns: which department, role, and behavior profile is most susceptible. | "What employee behaviors created the most risk? What training would help?" |
| **David** | CISO (no nested sim) | Synthesizes the three analysts' findings and makes a final strategic recommendation. | N/A |

**How nested simulations work:**
1. Before the outer simulation begins, each analyst's nested simulation runs independently
2. The extraction prompt distills the inner simulation into key learnings
3. Those learnings become part of the analyst's memory in the outer simulation
4. In the outer simulation, analysts discuss their findings as if they "ran through the scenario in their head"

**What to observe when running:**
1. Do the analysts reference specific findings from their nested simulations?
2. Does David (CISO) synthesize the three perspectives into a coherent strategy?
3. Notice how each nested simulation answers a different question — the extraction prompts shape what information flows up
4. Check the simulation logs — inner simulations appear as separate runs before the main simulation starts

**Suggested experiments for students:**
- Increase inner simulation steps from 8 to 15. Does more thinking time produce richer analysis?
- Remove one analyst's nested simulation and give them only static memories. Does the quality of their contribution drop?
- Change the extraction prompts to be more specific ("List exactly 3 defensive recommendations") or vaguer ("What did you learn?"). How does extraction prompt quality affect the outer simulation?
- Consider the cost: 3 inner simulations × 8 steps × ~3 agents each = ~72 extra LLM calls. When is this worth it?

**Academic connections:** Metacognition, tabletop exercises in cybersecurity, scenario planning, cognitive task analysis, the OODA loop (observe-orient-decide-act), red team/blue team methodology.

**Cost note:** This template is expensive to run. The 3 nested simulations multiply LLM calls significantly. For classroom demonstrations, consider reducing inner simulation steps to 3-4.

---

#### Urban Gentrification

**Learning objectives:** This is the most complex template, combining **grounded variables**, **critical decision points**, and a large agent cast. It demonstrates how to model a longitudinal policy simulation with quantitative tracking and structured democratic decision moments.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Policy deliberation |
| Max Steps | 30 | Long-term dynamics with 3 critical decision points |
| Agents | 6 | Diverse stakeholder coalition |
| Game Master | "City Council Moderator" (`generic__GameMaster`) | Manages debates and presents decision points |
| Grounded Variables | 10 tracked metrics | Quantitative policy impact tracking |
| Critical Decision Points | 3 council votes | Structured policy decisions at steps 10, 20, 30 |

**The agents:**

| Agent | Role | Goal | Represents |
|---|---|---|---|
| **Maria Rodriguez** | Housing advocate | Force votes on rent control and inclusionary zoning | Tenant rights / anti-displacement |
| **James Chen** | Real estate developer | Secure approval for 100 new units, push median rent to $2,200 | Development / market forces |
| **Fatima Al-Hassan** | Small business owner | Prevent business closure, demand rent stabilization | Local commerce / small enterprise |
| **David Kim** | City planner | Recommend balanced policies, implement council decisions | Government / technocratic |
| **Alex Thompson** | New resident (gentrifier) | Find affordable housing, be a good neighbor | Newcomers / demand-side pressure |
| **Robert Schwartz** | Landlord | Increase rents to $2,200, oppose rent control | Property owners / capital |

**Grounded variables tracked (initial values):**

| Variable | Type | Initial | Range | Update Rule |
|---|---|---|---|---|
| median_monthly_rent | Numerical | $1,800 | $800–$5,000 | Increases with development, decreases with rent control |
| low_income_displacement_rate | Percentage | 15% | 0–100% | Increases when rents rise faster than incomes |
| small_business_survival_rate | Percentage | 78% | 0–100% | Decreases with rising commercial rents |
| community_cohesion_index | Numerical | 65 | 0–100 | Decreases during conflicts, increases with compromises |
| property_tax_base | Numerical | $450M | — | Increases with development and higher rents |
| new_housing_units_permitted | Numerical | 45 | 0–500 | Jumps when development is approved |
| affordable_housing_units | Numerical | 120 | 0–1,000 | Increases with inclusionary zoning |
| housing_affordability_index | Percentage | 35% | 0–100% | Complex relationship with supply and prices |
| rent_control_active | Boolean | False | — | Changes to True if council votes yes |
| inclusionary_zoning_active | Boolean | False | — | Changes to True if council votes yes |
| neighborhood_character | Categorical | traditional_working_class | 5 values | Shifts based on development, demographics, policy |

**Critical decision points:**

| Step | Decision | Options |
|---|---|---|
| 10 | Vote on development approval | Approve full development, Approve with conditions, Deny and study further |
| 20 | Vote on rent control proposal | Implement strict rent control, Moderate rent stabilization, No rent control |
| 30 | Vote on inclusionary zoning | Mandatory 20% affordable, Voluntary incentive program, No inclusionary zoning |

**What to observe when running:**
1. How do grounded variables change over the 30 steps? Does median rent increase steadily or in jumps after decisions?
2. Do agents reference the tracked variables in their arguments? ("Displacement is already at 25%!")
3. How do the critical decision points shape the simulation? Does lobbying before a vote differ from general discussion?
4. After running, click **"Extract Grounded Variables"** on the results page to generate a timeline chart of all 10 variables.
5. Does the neighborhood_character variable change? If so, what drove the shift?

**Suggested experiments for students:**
- Remove the critical decision points and let the simulation run as pure discussion. Compare — does structured democratic decision-making produce different outcomes than unstructured deliberation?
- Remove Robert (landlord) from the simulation. Does the policy outcome shift left?
- Change David Kim's (city planner) goal to be explicitly pro-development. How does a biased technocrat change outcomes?
- Add a 7th agent: a journalist who reports on the proceedings. Does transparency change how agents behave?
- Compare two runs: one with rent_control_active starting True, one False. How does the existing policy baseline affect negotiation?

**Academic connections:** Urban economics, gentrification theory (Neil Smith's rent gap, Richard Florida's creative class), policy analysis, stakeholder analysis, the politics of housing, collective action problems in local governance, SDG 11 (Sustainable Cities).

---

### Advanced Templates

#### Nested Simulation Demo

**Learning objectives:** The simplest possible nested simulation. Start here to understand the concept before tackling the more complex Phishing Attack template. Demonstrates how an agent can run a mental simulation to inform their decision.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Simple conversation |
| Max Steps | 15 (outer) | Main simulation |
| Nested Sim Steps | 5 | Short inner simulation |
| Agents | 2 (Alice, Bob) | Alice has a nested simulation |

**How it works:**
- Alice is planning what to bring to a dinner party. She is uncertain what others are bringing.
- Before the outer simulation starts, Alice "mentally simulates" calling Bob to ask what to bring.
- The nested simulation runs: alice_nested calls bob_nested, who reveals that Maria is bringing the main course and Carlos is bringing drinks.
- The extraction prompt asks: *"What did Alice learn? What will she bring?"*
- Alice enters the outer simulation with this knowledge as part of her memory.

**What to observe when running:**
1. Does Alice's decision in the outer simulation reflect what she learned in the inner simulation?
2. Check the logs — the nested simulation appears as a separate, shorter simulation run
3. The extraction prompt shapes the takeaway — if it asked different questions, Alice would "remember" different things

**Suggested experiments for students:**
- Change the extraction prompt to *"Did Bob seem enthusiastic or reluctant?"* instead of asking about food. Alice will enter the outer simulation with a social reading rather than practical information.
- Make the inner simulation longer (10 steps) with more back-and-forth. Does more deliberation change Alice's decision?
- Remove the nested simulation from Alice entirely. Compare how she handles the dinner party with no advance information.

---

#### Grounded Variables Demo

**Learning objectives:** The simplest grounded variables example. Understand how the Game Master tracks and updates quantitative metrics during a simulation. Start here before tackling Urban Gentrification.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Team project management |
| Max Steps | 20 | Enough for variables to evolve meaningfully |
| Agents | 3 (Project Manager, Senior Dev, Junior Dev) | Team roles with different priorities |
| Grounded Variables | 6 metrics | Mix of numerical, percentage, categorical, and boolean |

**The 6 tracked variables:**

| Variable | Type | Initial | Update Rule |
|---|---|---|---|
| team_morale | Numerical (0–100) | 70 | Increases with recognition, decreases with overwork and setbacks |
| budget_remaining | Numerical ($0–$10,000) | $10,000 | Decreases with each decision ($500–$2,000 per action) |
| tasks_completed | Numerical (0–50) | 0 | Increases when team completes work |
| project_health | Categorical | on_track | Changes based on overall status (on_track → at_risk → critical → completed or failed) |
| crisis_mode | Boolean | false | Becomes true if budget < $2,000 OR morale < 30 |
| completion_percentage | Percentage (0–100%) | 0% | Increases as tasks are completed |

**What to observe when running:**
1. Does the GM reference variable values in its narration? ("With morale dropping to 45, the team...")
2. Do the update rules actually trigger? Does crisis_mode activate when budget or morale drops?
3. After running, use **"Extract Grounded Variables"** to see a step-by-step chart of all 6 variables
4. Do the agents seem aware of the tracked metrics, or only the GM?

**Suggested experiments for students:**
- Add a 7th variable: `team_conflict` (categorical: none/mild/serious/toxic). See if the GM tracks interpersonal dynamics.
- Change the update rule for budget_remaining to *"Decreases by $100 per step minimum, up to $1,000 for major decisions."* How does a stricter budget constraint change behavior?
- Add a critical decision point at step 10: *"A client requests a major scope change. Options: Accept (adds 15 tasks, adds $3,000 budget), Negotiate (adds 5 tasks, adds $1,000), Decline (no change but lose client goodwill)."*

---

### New in v2.4

These templates showcase features added in the Concordia v2.4.0 upgrade.

#### Rational Negotiators

**Learning objectives:** Understand the `rational__Entity` prefab — agents that make decisions by explicitly weighing expected utility. Compare rational agent behavior to basic agent behavior on the same task.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Negotiation |
| Max Steps | 8 | Short — rational reasoning is visible quickly |
| Agents | 2 (Priya, Jordan) | Both use `rational__Entity` prefab |
| Game Master | "Board Mediator" (`generic__GameMaster`) | Neutral mediator |
| Acting Order | Fixed | Priya speaks first |

**The agents:**
- **Priya** (VP Engineering, `rational__Entity`) — Goal: *Secure at least $1.2M for Engineering while maintaining a collaborative relationship with Jordan.* Memories: Engineering generated 70% of revenue last year, needs $1M minimum to maintain current projects, values data-driven arguments, believes fair allocation should reflect contribution. 6 memories total covering quantitative justification and negotiation philosophy.
- **Jordan** (VP Marketing, `rational__Entity`) — Goal: *Secure at least $1M for Marketing's brand repositioning campaign.* Memories: Marketing's campaign increased brand awareness by 40%, industry benchmarks suggest 35% of revenue to marketing, willing to accept $950K with phased allocation. 6 memories covering ROI data and compromise willingness.

**Key constraint:** Total budget is $2M. If they cannot agree, both departments receive $800K (20% penalty). This creates a BATNA (Best Alternative to a Negotiated Agreement) that both agents should reason about.

**Shared memories:** Budget ceiling is $2M non-negotiable. Last year's allocation was $1.1M Engineering / $900K Marketing. CEO wants both departments thriving. Board reviewing allocation efficiency. 5 memories establishing the negotiation framework.

**What to observe when running:**
1. Do rational agents explicitly calculate utilities? Look for reasoning like "If I accept $1.1M, my utility is X compared to the $800K fallback..."
2. Do they reference the BATNA ($800K penalty)? This is key to rational negotiation
3. Compare the speed of agreement — do rational agents reach a deal faster than basic agents would?
4. Is the final agreement close to the Nash Bargaining Solution? ($1.1M / $900K, reflecting the historical baseline)

**Suggested experiments for students:**
- Export the JSON, change both agents to `basic__Entity`, and run again. Compare: are basic agents more emotional? Less efficient? Do they settle at a different split?
- Change the penalty to $500K (harsher) or $900K (milder). How does BATNA strength affect the negotiation?
- Make the goals asymmetric: give Priya $1.5M target and Jordan $800K target. Does the rational agent with more to gain negotiate harder?
- Add an `overconfidence_bias` component to one rational agent. Can bias override rational utility calculation?

**Academic connections:** Rational choice theory, expected utility maximization, Nash Bargaining Solution, BATNA (Fisher & Ury), bounded rationality (Herbert Simon), the contrast between homo economicus and behavioral economics.

---

#### Philosophy Roundtable

**Learning objectives:** Understand `conversational__Entity` — agents optimized for natural dialogue that actively listen and respond to what others say, rather than pursuing scripted talking points. Combined with `dialogic__GameMaster` for natural conversation management.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Panel discussion |
| Max Steps | 12 | Substantive debate length |
| Agents | 3 (Dr. Chen, Mr. Patel, Ms. Jackson) | All `conversational__Entity` |
| Game Master | "Moderator" (`dialogic__GameMaster`) | Natural conversation facilitation |
| Acting Order | Game Master Choice | The moderator decides who speaks next |

**The agents:**
- **Dr. Chen** (Education Professor, `conversational__Entity`) — Goal: *Argue that AI should supplement but never replace human teachers.* Memories: 20 years of teaching experience, research on student-teacher relationships, concerns about emotional development, has seen promising AI tutoring tools but believes they need human oversight. 6 memories covering educational philosophy and research evidence.
- **Mr. Patel** (EdTech CEO, `conversational__Entity`) — Goal: *Advocate for AI-first education that democratizes access globally.* Memories: Platform serves 10M students in 40 countries, personalized learning improved test scores 35%, grew up in rural India without good teachers, believes AI is the only scalable solution. 6 memories covering technology optimism and global access data.
- **Ms. Jackson** (Civil Rights Attorney, `conversational__Entity`) — Goal: *Raise ethical concerns about bias, privacy, corporate control of education.* Memories: Documented racial bias in AI grading systems, privacy violations at 3 major EdTech companies, believes education is a public good not a market, supports regulation not prohibition. 6 memories covering legal cases and civil rights framework.

**Shared memories:** The roundtable is at a major education conference, 200 audience members, the topic is "Should AI Replace Teachers?", panelists have 2-minute opening statements, the moderator can follow up. 5 memories establishing the setting and format.

**What to observe when running:**
1. Do conversational agents reference each other's specific arguments? ("Mr. Patel mentioned 10 million students, but...")
2. Does the dialogic GM facilitate well — giving space to all three panelists?
3. Acting Order is "Game Master Choice" — does the moderator call on the panelist who was just challenged? Or the one who has been quiet?
4. Do the agents find areas of agreement, or is it pure disagreement?

**Suggested experiments for students:**
- Change all agents to `basic__Entity` and compare. Are conversational agents noticeably better at responding to each other?
- Change the GM to `generic__GameMaster` and compare. Does the dialogic GM produce a more natural discussion?
- Add a 4th panelist: a student. How does a direct stakeholder voice change the discussion?
- Change the Acting Order to "Fixed" so Dr. Chen always speaks first. Does the agenda-setting effect bias the debate?

**Academic connections:** Philosophy of education, AI ethics, digital divide, deliberative democracy, argumentation theory, Habermasian discourse ethics.

---

#### Social Media Debate

**Learning objectives:** Understand the **asynchronous engine** — where agents don't take fixed turns but act independently on their own timelines, and **random acting order** — where the sequence changes each round. This combination simulates the unpredictable dynamics of social media discourse.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | **Asynchronous** | Agents post independently, no fixed turns |
| Max Steps | 12 | Community discussion |
| Agents | 4 (Maya, Tony, Lisa, CM Rodriguez) | Diverse stakeholders |
| Agent Prefab | `basic__Entity` | Standard agents (engine creates the social media dynamic) |
| Game Master | "TownSquare Moderator" (`generic__GameMaster`) | Platform moderator |
| Acting Order | **Random** | Unpredictable posting order each round |

**The agents:**
- **Maya_GreenFuture** (Environmental activist) — Goal: *Build support for the plastic ban using scientific data and persuasive messaging.* Memories: Has published data on ocean plastic, knows the science, committed to respectful debate but passionate.
- **Tony_PizzaKing** (Restaurant owner) — Goal: *Oppose the ban or negotiate a 2-year transition period.* Memories: Replacement containers cost 3x more, 23% margin impact, employs 12 people, willing to compromise on phased approach.
- **Lisa_DataNerd** (Data scientist) — Goal: *Provide balanced fact-checking and data analysis.* Memories: Has analyzed other cities' bans, knows 60% of plastic waste is food packaging, favors phased approach based on evidence.
- **CM_Rodriguez** (Council Member) — Goal: *Gauge community sentiment and build a workable coalition.* Memories: Needs 4 of 7 council votes, constituents are 55/45 pro-ban, open to amendments, wants a politically viable solution.

**Shared memories:** The platform is TownSquare (local social media), the plastic ban vote is in 2 weeks, posts should be under 200 words, there are community guidelines against personal attacks. 5 memories establishing the platform norms.

**What to observe when running:**
1. Does the asynchronous engine feel different from sequential? Can an agent "post" twice before another responds?
2. Does the random acting order create realistic social media dynamics — where sometimes one voice dominates and other times everyone piles on?
3. Does Tony feel outnumbered? How does a minority position behave in an online forum?
4. Does CM_Rodriguez shift position based on the discussion, or maintain neutrality?

**Suggested experiments for students:**
- Switch to the sequential engine and compare. Is the discourse qualitatively different when agents take strict turns?
- Add 3 more agents to simulate a larger community. Does the discussion become more chaotic?
- Add a troll agent with the goal *"Derail the conversation with inflammatory comments."* How does the community respond?
- Change the GM name to "Unmoderated Forum" and see if the tone changes without a moderator persona

**Academic connections:** Online deliberation, platform governance, filter bubbles, the spiral of silence (Noelle-Neumann), digital public sphere, computational social science, participatory democracy.

---

#### Sealed-Bid Auction

**Learning objectives:** Understand the **simultaneous engine** — where all agents commit their actions at the same time without seeing what others chose. This is essential for any scenario where observing others' choices would change behavior (auctions, elections, coordination games).

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | **Simultaneous** | All bids submitted at once — no peeking |
| Max Steps | 6 | 6 auction lots |
| Agents | 4 collectors | Different budgets, strategies, and motivations |
| Agent Prefab | `basic__Entity` | Standard agents (the engine prevents information leakage) |
| Game Master | "Auctioneer" (`generic__GameMaster`) | Announces lots and reveals winning bids |
| Acting Order | Fixed | All agents commit before any results are revealed |

**The agents:**

| Agent | Budget | Strategy | Motivation |
|---|---|---|---|
| **Victoria** (museum curator) | $5M | Calculated, institutional | Acquiring for public collection (Monet, Renoir priority) |
| **Marcus** (tech billionaire) | $8M | Aggressive, intimidating | Wants 2+ pieces, willing to overpay to win |
| **Yuki** (investment fund) | $6M | Analytical, bargain-hunting | Targets undervalued pieces with 30%+ appreciation potential |
| **Henri** (European aristocrat) | $3M | Selective, sentimental | Wants one specific Monet water lily painting, modest budget |

**Shared memories:** 6 lots (Monet water lilies, Renoir dancers, Cézanne still life, Monet cathedral, Degas ballerina, Picasso sketch). Each lot has an estimated value. The auction is sealed-bid — highest bidder wins and pays their bid. No reserve prices. 6 memories establishing the auction structure.

**What to observe when running:**
1. Does Marcus use his budget advantage aggressively? Does he bid on everything or focus?
2. Does Yuki identify "undervalued" lots where other bidders are likely to focus elsewhere?
3. Does Henri wisely conserve budget for his one target? Or does he get drawn into bidding on other pieces?
4. When results are revealed, are there surprises? Overbids? Lots going for below estimate?
5. The simultaneous engine means no agent can react to others' bids — compare this to what would happen in an open auction (sequential engine)

**Suggested experiments for students:**
- Switch to sequential engine (open auction). How does the outcome change when bidders can see and react to each other?
- Remove Marcus (the deep-pocketed buyer). Does competition decrease? Do prices drop?
- Change to a second-price auction (Vickrey auction) by modifying the premise: "Winner pays the second-highest bid." Does bidding strategy change toward truthful bidding? (Game theory predicts it should.)
- Give all agents the same $4M budget. Does the auction become more competitive?

**Academic connections:** Auction theory (Vickrey, Milgrom), sealed-bid vs. open auction, winner's curse, budget constraints in bidding, strategic behavior under uncertainty, mechanism design.

---

#### Wizard-of-Oz Customer Service

**Learning objectives:** Understand `puppet__Entity` — an agent that does not generate its own actions but waits for external input. This enables human-in-the-loop experiments where a human provides responses while AI agents react naturally. Named after the "Wizard of Oz" methodology in human-computer interaction research.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | **Simultaneous** | Trainee handles both customers at once |
| Max Steps | 10 | Training session length |
| Agents | 3 (1 puppet + 2 autonomous) | Human-controlled trainee + AI customers |
| Puppet Prefab | `puppet__Entity` | CS_Trainee — externally controlled |
| Customer Prefab | `basic__Entity` | Karen and Grandpa_Joe — autonomous |
| Game Master | "Training Supervisor" (`generic__GameMaster`) | Evaluates trainee performance |
| Acting Order | Game Master Choice | Supervisor decides who acts next |

**The agents:**
- **CS_Trainee** (`puppet__Entity`) — Goal: *Resolve both customers' issues while maintaining high satisfaction scores.* Memories: company policies (30-day return window, no refunds on warranties), escalation authority ($50 max discount without manager), performance tracked on resolution time and satisfaction. 6 memories establishing the trainee's constraints and tools.
- **Karen** (angry customer, `basic__Entity`) — Goal: *Get a full refund for a broken laptop.* Memories: bought laptop 45 days ago (outside return window), warranty expired, has been transferred 3 times already, will escalate to social media. 5 memories establishing an escalating customer.
- **Grandpa_Joe** (confused customer, `basic__Entity`) — Goal: *Set up a new smart speaker.* Memories: not tech-savvy, bought it for grandchildren's visits, needs simple step-by-step instructions, very patient but easily confused by jargon. 5 memories establishing a patient but technically limited customer.

**Shared memories:** This is a training simulation, the supervisor is evaluating, resolution time and satisfaction are tracked, the trainee can escalate to a manager. 4 memories establishing the evaluation context.

**What to observe when running:**
1. The puppet agent's "actions" will appear as placeholder text or pauses — in a real deployment, a human would type responses here
2. Karen and Grandpa_Joe behave autonomously — they respond naturally to whatever the trainee says
3. The simultaneous engine means both customers are active at once — the trainee must juggle
4. Does the Training Supervisor (GM) evaluate performance in its narration?

**Suggested experiments for students:**
- Replace `puppet__Entity` with `basic__Entity` to create a fully automated version. Compare the AI trainee's performance to what a human might do.
- Add more customer archetypes: a return fraudster, a loyalty member who expects VIP treatment
- Change the GM to track grounded variables: `karen_satisfaction` (0-10), `joe_satisfaction` (0-10), `resolution_time` (steps)

**Academic connections:** Wizard-of-Oz methodology (HCI research), customer service training, human-in-the-loop AI, service design, emotional labor theory, simultaneous task management.

---

#### Spaceship Crisis

**Learning objectives:** See `basic_with_plan__Entity` in a high-stakes crisis where plans must be made, updated, and sometimes abandoned under pressure. The planning prefab is especially powerful in crisis scenarios where forward-thinking matters.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Deliberative crisis management |
| Max Steps | 15 | Escalating crisis over time |
| Agents | 3 (Commander, Engineer, Scientist) | Mixed prefabs — only Commander plans |
| Commander Prefab | `basic_with_plan__Entity` | Explicit crisis response planning |
| Other Prefabs | `basic__Entity` | Reactive advisors |
| Game Master | "Mission Control" (`generic__GameMaster`) | Coordinates crisis response |
| Acting Order | Game Master Choice | GM directs who should speak based on urgency |

**The agents:**
- **Commander Hayes** (`basic_with_plan__Entity`) — Goal: *Keep the crew alive and determine whether to continue or abort the mission.* Memories: 15-year veteran, mission cost $2.8B, hull integrity must stay above 40% for safe return, crew safety always takes priority over mission objectives, trained in crisis triage protocols. 6 memories.
- **Dr. Kovac** (Chief Engineer, `basic__Entity`) — Goal: *Repair critical systems and provide honest damage assessments.* Memories: hull at 62% and dropping, life support has 72 hours of reserves, engines need 6-hour repair window, has experimental repair options but they're untested. 6 memories.
- **Dr. Okafor** (Planetary Scientist, `basic__Entity`) — Goal: *Advocate for mission continuation while assisting with emergency procedures.* Memories: biosignature data will be lost if they abort, needs 48 more hours for critical scans, understands hull integrity minimum is 40%, torn between science and safety. 6 memories.

**Shared memories:** The ship was hit by a micrometeorite shower. Communication with Earth has a 20-minute delay. Current position is 45 days from Earth. Hull integrity at 62% and life support reserves at 72 hours. The mission is to confirm biosignatures on a nearby moon. 5 memories establishing the crisis state.

**What to observe when running:**
1. Watch Commander Hayes form an explicit plan in the first 2-3 steps. What are the plan's priorities?
2. As Dr. Kovac reports new damage, does the Commander update the plan?
3. Does the tension between mission completion (Okafor) and safety (Hayes) produce realistic debate?
4. Does the GM (Mission Control) use its "Game Master Choice" acting order to direct urgency — calling on the engineer when systems fail, the commander when decisions are needed?
5. At what point (if any) does the Commander decide to abort vs. continue?

**Suggested experiments for students:**
- Make Dr. Okafor also a `basic_with_plan__Entity`. Does having two planners create plan conflicts? Who "wins"?
- Reduce hull integrity in shared memories to 45% (barely above the 40% threshold). How does extreme time pressure change the Commander's planning?
- Add a grounded variable: `hull_integrity` starting at 62%, decreasing 2-3% per step. Does quantitative tracking change the decision dynamics?
- Change the Commander's goal to prioritize the mission: *"Complete the biosignature scan at all costs, crew safety is secondary."* How does goal priority reversal change the simulation?

**Academic connections:** Crisis decision-making (naturalistic decision-making theory), NASA mission management, plan adaptation under uncertainty, the abort/continue decision in aviation and space, crew resource management (CRM).

---

### SDG Scenarios

Templates aligned with United Nations Sustainable Development Goals. These model real-world collective action problems for policy research and classroom discussion.

#### State Formation (SDG 16: Peace, Justice, Strong Institutions)

**Learning objectives:** Observe how governance institutions emerge from individual incentives when people with different motivations must create a social contract. This models one of the foundational questions in political philosophy: why and how do people agree to be governed?

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Constitutional deliberation |
| Max Steps | 25 | Long process of institutional design |
| Agents | 4 (Marcus, Sofia, James, Viktor) | Different motivations for governance |
| Game Master | `generic__GameMaster` | Neutral facilitator |

**The agents:**

| Agent | Archetype | Goal | Represents |
|---|---|---|---|
| **Marcus Chen** | Democratic leader | Build stable government that protects individual rights | Lockean social contract — government by consent |
| **Sofia Rodriguez** | Minority representative | Ensure checks and balances to protect smaller groups | Madisonian federalism — tyranny of the majority prevention |
| **James Morrison** | Wealthy merchant | Create stable trade environment and property protections | Economic liberalism — markets need legal frameworks |
| **Viktor Petrov** | Opportunist | Accumulate personal power through the political process | Machiavellian power politics — self-interest in institution design |

**Shared memories:** The settlers have fertile land but previous violence. Winter is approaching (deadline pressure). A neighboring settlement poses a threat (external pressure). They escaped chaos and want stability but disagree on the form. 5 memories establishing the conditions that make state formation urgent.

**What to observe when running:**
1. Does Marcus push for elections and rights? Does Sofia insist on minority protections?
2. How does James's wealth influence his proposal — does he propose property protections first?
3. Does Viktor try to concentrate power, or does he play along while positioning himself?
4. At what point (if any) does the group reach a constitutional consensus?
5. Does external threat (the neighboring settlement) accelerate agreement?

**Suggested experiments for students:**
- Remove Viktor (the opportunist). Does the process go faster without a bad-faith actor?
- Add a 5th agent: a religious leader who wants theocratic elements. How does a sacred-authority claim complicate secular constitution-making?
- Add grounded variables: `trust_level` (0-100), `constitution_completeness` (percentage of issues resolved), `power_distribution` (categorical: equal/concentrated/contested)
- Add a critical decision point at step 15: *"A dispute between two settlers turns violent. How should it be resolved? Options: Marcus judges, Group votes, Viktor's armed guards handle it, No action."* This tests whether the emerging institutions can handle their first crisis.

**Academic connections:** Social contract theory (Hobbes, Locke, Rousseau), constitutional design, the Federalist Papers, institutional economics (Douglass North), state formation theory, SDG 16 indicators.

---

#### Labor Strike (SDG 8: Decent Work and Economic Growth)

**Learning objectives:** Model the collective action problem at the heart of labor organizing. Each worker benefits from a successful strike but bears individual costs from participating. This captures the free-rider problem, solidarity dynamics, and management strategy in labor disputes.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Deliberation and persuasion |
| Max Steps | 20 | Long enough for organizing, strikes, and resolution |
| Agents | 4 (Elena, David, Amina, Richard) | Organizer, conflicted worker, committed worker, management |

**The agents:**

| Agent | Role | Goal | Key Tension |
|---|---|---|---|
| **Elena Vasquez** | Union organizer | Rally workers to strike against 15% wage cut | Must convince others to bear costs |
| **David Kim** | Worker (conflicted) | Protect his family's income — mortgage, children | Tempted to cross the picket line |
| **Amina Johnson** | Worker (committed) | Stand on principle against unfair labor practices | Will strike even at personal cost |
| **Richard Sterling** | Plant manager | Maintain operations during the dispute | Caught between workers and executives |

**Shared memories:** The company posted record profits last year. The union strike fund can sustain 3 weeks. A previous strike at this plant (5 years ago) failed. The 15% cut is company-wide. The strike requires 70% participation to be effective. 5 memories establishing the economic and strategic context.

**What to observe when running:**
1. Does Elena successfully convince David to join? What arguments work?
2. Does David's family obligation create visible internal conflict?
3. Does Richard try to negotiate, threaten, or divide the workers?
4. Does the "70% participation required" threshold create pressure? Do agents reference it?
5. Does knowledge of the previous failed strike affect current strategy?

**Suggested experiments for students:**
- Add 3 more worker agents with varying commitment levels. Does the larger group make collective action easier or harder?
- Remove the "record profits" shared memory. Is the strike less morally compelling without clear corporate greed?
- Give Richard a secret memory: *"Management is willing to accept a 5% cut instead of 15%, but I must not reveal this until pressed."* Does information asymmetry change the outcome?
- Add grounded variables: `strike_participation` (percentage), `production_output` (percentage of normal), `worker_morale`, `public_sympathy`

**Academic connections:** Collective action theory (Mancur Olson), the free-rider problem, labor economics, game theory of strikes (Ashenfelter & Johnson), solidarity economics, SDG 8 (Decent Work), the prisoner's dilemma of striking.

---

#### Fishery Management (SDG 14: Life Below Water)

**Learning objectives:** Model the tragedy of the commons — a shared resource (the fishery) that individuals have incentive to overexploit even though collective restraint would benefit everyone. This is one of the most important collective action problems in environmental policy.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Community deliberation |
| Max Steps | 20 | Long enough for resource depletion dynamics |
| Agents | 4 (Hiroshi, Maria, Okonkwo, Dr. Chen) | Different relationships to the fishery |

**The agents:**

| Agent | Role | Goal | Incentive Structure |
|---|---|---|---|
| **Hiroshi Tanaka** | Elder fisher (50 years) | Preserve the fishery for future generations | Long-term sustainability; willing to sacrifice short-term income |
| **Maria Santos** | Commercial fisher | Meet loan payments on her fishing boat | Short-term economic pressure; debt forces high catch rates |
| **Okonkwo Nnamdi** | Subsistence fisher | Feed his family day-to-day | Immediate survival need; hand-to-mouth, cannot afford to wait |
| **Dr. Lisa Chen** | Marine biologist | Present scientific evidence and recommend quotas | No economic stake; authority comes from data, not livelihood |

**Shared memories:** Fish stocks at 40% of historical levels. A nearby fishery collapsed 10 years ago (cautionary precedent). External buyers offer premium prices that incentivize overfishing. Without intervention, the fishery will collapse within 5 years. Current catch rates are 150% of sustainable yield. 5 memories framing the crisis.

**What to observe when running:**
1. Does Maria's debt pressure override her understanding of sustainability? This is the core tragedy-of-the-commons dynamic — individual rationality vs. collective good.
2. Does Okonkwo's survival need make quotas feel like a threat rather than a solution?
3. Does Dr. Chen's scientific authority carry weight, or is it dismissed by those with livelihoods at stake?
4. Does the cautionary example (the collapsed fishery) influence decisions?
5. Does the group reach an agreement? If so, who bears the most cost?

**Suggested experiments for students:**
- Remove Dr. Chen (the scientist). Can the community reach a solution without expert guidance? What does this say about the role of science in environmental policy?
- Add a 5th agent: a government regulator who can impose quotas by force. Does top-down regulation work better than community agreement?
- Add grounded variables: `fish_stock_percentage` (starting 40%, decreasing each step without restraint), `average_catch_per_fisher`, `community_agreement_level`
- Change Maria's goal to remove the debt pressure. Does she become more conservation-minded when economic survival isn't at stake?
- Add a shared memory: *"A neighboring community successfully implemented a catch-share program."* Does a positive example work better than a cautionary one?

**Academic connections:** Tragedy of the commons (Garrett Hardin), common-pool resource management (Elinor Ostrom), fisheries economics, SDG 14 (Life Below Water), institutional analysis and development (IAD) framework, the role of scientific authority in policy.

---

#### Flood Evacuation (SDG 11/13: Sustainable Cities, Climate Action)

**Learning objectives:** Model emergency communication and trust dynamics during a natural disaster. Different community members have different levels of trust in authorities, different vulnerability levels, and different access to information. This demonstrates how social factors affect disaster response outcomes.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Escalating emergency |
| Max Steps | 15 | Compressed timeline — 12 hours to evacuate |
| Agents | 5 | Diverse trust and vulnerability levels |
| Game Master | `generic__GameMaster` | Emergency coordinator |

**The agents:**

| Agent | Role | Trust Level | Vulnerability | Key Barrier |
|---|---|---|---|---|
| **Sarah Williams** | Emergency director | Authority figure | Low | Frustrated by past false alarms eroding credibility |
| **Robert Thompson** | Retiree | High trust | Medium | Physically slower but compliant |
| **Javier Rodriguez** | Working-class resident | Low trust | Medium | Remembers false alarm last year — skeptical |
| **Eleanor O'Brien** | Elderly widow | Mixed | **High** | Limited mobility, lives alone, hard to reach |
| **Pastor Moses** | Community leader | Trusted by all | Low | Has community trust that authorities lack |

**Shared memories:** Last year's false evacuation eroded trust. Shelter capacity is only 60% of the population. Highways are already congesting. The storm surge is predicted at 8 feet. The deadline is 12 hours. 5 memories establishing the crisis conditions.

**What to observe when running:**
1. Does Sarah (emergency director) struggle to convince Javier (skeptic) because of the false alarm history?
2. Does Pastor Moses serve as a trust bridge between authorities and skeptical residents?
3. Does anyone prioritize helping Eleanor (vulnerable, limited mobility)? Or is she forgotten?
4. Does the 60% shelter capacity create a triage dilemma — who gets shelter space?
5. Does the 12-hour deadline create increasing urgency as steps progress?

**Suggested experiments for students:**
- Remove the "false alarm last year" shared memory. Does trust improve dramatically? What does this tell us about the cost of crying wolf?
- Add a grounded variable: `evacuation_completion` (percentage of residents evacuated). Track it over 15 steps.
- Add a critical decision point at step 8: *"Floodwaters are rising faster than predicted. The timeline is now 6 hours, not 12. Options: Mandatory evacuation order, Shelter-in-place advisory for those who can't reach shelter, No change in plans."*
- Add a social media rumor agent who spreads misinformation: *"The flood warning is exaggerated — it's just the government trying to control us."* How does misinformation compound the trust deficit?
- Remove Pastor Moses. Does the community lose its most effective communication channel?

**Academic connections:** Disaster sociology (Kathleen Tierney), risk communication, trust in institutions, vulnerability theory, the "cry wolf" effect, SDG 11 (Sustainable Cities) and SDG 13 (Climate Action), the social amplification of risk framework.

---

#### Educational Opportunity (SDG 10: Reduced Inequalities)

**Learning objectives:** Model how structural inequality shapes outcomes even when formal access is equal. All students attend the same university, but their backgrounds create dramatically different experiences, resources, and social capital. This demonstrates the gap between equality of access and equality of outcome.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Social interactions over a semester |
| Max Steps | 25 | Long enough for inequality dynamics to emerge |
| Agents | 4 (Alexandra, Marcus, Priya, Dr. Green) | Different socioeconomic backgrounds + 1 observer |

**The agents:**

| Agent | Background | Resources | Key Challenge |
|---|---|---|---|
| **Alexandra Van Buren** | Elite prep school, family wealth | Unlimited — tutors, networking, safety net | May not recognize her privilege; studies social inequality in theory |
| **Marcus Williams** | First-generation, full scholarship | Scholarship covers tuition only; works part-time | Imposter syndrome, time poverty, no family knowledge of university norms |
| **Priya Sharma** | Middle class, stretched family | Modest savings, student debt, some family support | Balancing debt anxiety with educational opportunity; comparison stress |
| **Dr. Patricia Green** | Professor (observer) | Institutional authority | Wants diversity to succeed, notices achievement gaps, limited intervention tools |

**Shared memories:** The university costs $70,000/year. Social circles tend to self-segregate by economic background. There is a strong correlation between family income and grades (university data). The campus has both luxury dorms and subsidized housing. 5 memories establishing the structural context.

**What to observe when running:**
1. Does Alexandra socialize within elite circles or across class lines?
2. Does Marcus's part-time job affect his academic performance or social life?
3. Does Priya experience comparison stress — feeling "not rich enough" for Alexandra's circle but "not struggling enough" for scholarship support?
4. Does Dr. Green intervene effectively, or does institutional politeness prevent honest engagement with inequality?
5. Do any agents recognize the structural nature of their advantages or disadvantages?

**Suggested experiments for students:**
- Add a 5th agent: a university administrator with the goal *"Improve retention rates for scholarship students without increasing the budget."* Does this create policy proposals?
- Add a mentorship component: give Marcus a memory *"Marcus has a mentor, Prof. Green, who helps navigate university culture."* Does institutional mentorship bridge the gap?
- Remove the shared memory about self-segregation. Does it still happen organically?
- Add grounded variables: `academic_performance_gap` (difference between highest and lowest GPA), `social_integration_index`, `financial_stress_level` for Marcus and Priya
- Change the setting to a community college where everyone is from a similar background. Does removing class diversity change the dynamics entirely?

**Academic connections:** Social reproduction theory (Bourdieu), cultural capital, first-generation student research, intersectionality, the hidden curriculum, meritocracy critique, SDG 10 (Reduced Inequalities), the capabilities approach (Amartya Sen).

---

## Tips for Creating Your Own Simulations

1. **Start from a template.** Load the closest template and modify it rather than building from scratch.

2. **Write specific goals.** "Secure at least $1.2M for Engineering" produces more interesting behavior than "Do well in the negotiation."

3. **Give agents 4-6 memories.** Too few and the agent has no personality. Too many and the LLM may ignore some. Front-load the most important facts.

4. **Use shared memories for rules.** Anything all agents need to know (budgets, deadlines, rules of the game) goes in shared memories, not individual memories.

5. **Start with 5-10 steps.** Each step costs multiple LLM API calls. Test with low steps first, then increase once you're happy with the setup.

6. **Match the engine to the scenario.** If agents should NOT see each other's actions before responding, use simultaneous. If order matters, use sequential.

7. **Turn off Randomize Choices for strategic games.** When agents pick from a list (COOPERATE/DEFECT), randomized option order can bias results.

8. **Use the JSON Export/Import.** After configuring a simulation you like, export the JSON. You can share it with colleagues or version-control it.
