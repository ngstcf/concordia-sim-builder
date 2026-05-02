# Simulation Templates Guide

This guide explains every pre-built template in the Concordia Simulation Builder. Each template is a ready-to-run configuration that demonstrates a specific feature or scenario. Click **Browse Templates** in the Simulation Builder to open the template picker — you can search by name or description, filter by category, feature tags, or engine type, and sort by name, agent count, or step count. Select a template card and click **Load Template**.

You can run templates as-is or modify them to fit your needs. All parameters are editable after loading.

**Template source code:** Each template lives in its own file under `backend/api/templates/` (e.g., `peace_negotiation.py`). The registry is in `backend/api/templates/__init__.py`. All 26 templates include research-grade agent configurations with 7-10 memories per agent, psychological components, player-specific context, and measurable goals.

---

## Quick Reference

| Template | Category | Engine | Agents | Components | PSC | What It Teaches |
|---|---|---|---|---|---|---|
| Coffee Shop Demo | Basic | Sequential | 2 | — | — | Minimal setup, how agents interact |
| Peace Negotiation | Basic | Sequential | 2 | values, emotion | ✓ | Negotiation dynamics, measurable goals, shared memories |
| Planning Agent | Prefab Types | Sequential | 3 | personality_traits | ✓ | Agents that form and follow plans |
| Scripted Entity | Prefab Types | Sequential | 5 | personality_traits | — | Agents with pre-written dialogue lines |
| Context-Aware Moderator | Prefab Types | Sequential | 4 | personality_traits, emotion | — | Scripted agents that adapt to context |
| Dialogic Conversation | Prefab Types | Sequential | 2 | personality_traits, emotion | ✓ | Natural back-and-forth dialogue |
| Strategic Game | Prefab Types | Sequential | 2 | cognitive_bias, personality_traits, values | ✓ | Game theory with action choices |
| Interviewer | Prefab Types | Sequential | 1 | personality_traits, emotion | — | Structured questionnaire surveys |
| Formative Memories | Prefab Types | Sequential | 3 | personality_traits, emotion | ✓ | Rich character backstories |
| Marketplace | Prefab Types | Sequential | 3 | personality_traits | — | Trading with BUY/SELL/HOLD actions |
| Vaccine Hesitancy Study | Research | Sequential | 5 | personality_traits, cognitive_bias, emotion, values, social_identity, TPB | ✓ | Full psychological component stack |
| Phishing Attack Simulation | Research | Sequential | 4 | cognitive_bias | — | Nested simulations (sims within sims) |
| Urban Gentrification | Research | Sequential | 6 | personality_traits, cognitive_bias, values, social_identity | ✓ | Grounded variables + decision points |
| Nested Simulation Demo | Advanced | Sequential | 2 | — | — | Agent-level mini-simulations |
| Grounded Variables Demo | Advanced | Sequential | 3 | — | ✓ | Tracking numeric/categorical metrics |
| Rational Negotiators | New in v2.4 | Sequential | 2 | personality_traits, values | ✓ | Utility-maximizing rational agents |
| Philosophy Roundtable | New in v2.4 | Sequential | 3 | personality_traits, values | ✓ | Dialogue-optimized conversational agents |
| Social Media Debate | New in v2.4 | Asynchronous | 4 | social_identity, cognitive_bias | ✓ | Async engine for social media dynamics |
| Sealed-Bid Auction | New in v2.4 | Simultaneous | 4 | cognitive_bias, personality_traits | ✓ | Simultaneous engine (all act at once) |
| Wizard-of-Oz CS Training | New in v2.4 | Simultaneous | 3 | emotion, personality_traits | ✓ | Human-controlled puppet agents |
| Spaceship Crisis | New in v2.4 | Sequential | 3 | personality_traits, emotion, values | ✓ | Planning agents in crisis scenarios |
| State Formation | SDG Scenarios | Sequential | 4 | values, cognitive_bias | ✓ | Institution-building (SDG 16) |
| Labor Strike | SDG Scenarios | Sequential | 4 | emotion, values, social_identity | ✓ | Collective action (SDG 8) |
| Fishery Management | SDG Scenarios | Sequential | 4 | values, cognitive_bias, TPB | ✓ | Common-pool resources (SDG 14) |
| Flood Evacuation | SDG Scenarios | Sequential | 5 | TPB, cognitive_bias, emotion, values | ✓ | Emergency response (SDG 11/13) |
| Educational Opportunity | SDG Scenarios | Sequential | 4 | social_identity, emotion | ✓ | Social mobility (SDG 10) |

**Legend:** Components = psychological components on agents. PSC = player-specific context (private information per agent). TPB = theory of planned behavior.

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
| **Prefab Settings** | Parameters specific to the selected prefab — e.g., observation history length (basic), time horizon (plan), custom instructions (minimal), fixed responses (puppet). These appear automatically based on the chosen prefab. |
| **Components** | Optional psychological traits, biases, or behavioral modifiers. See [Components](#psychological-components). |
| **Custom Reasoning Steps** | (Minimal prefab only) Custom questions the agent asks itself each turn. See [Components](#psychological-components). |

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
- **7-10 memories is the sweet spot** — too few and the agent is bland, too many and important ones get diluted. All built-in templates use 7-10 memories per agent.

| Memory Type | Example | Purpose |
|---|---|---|
| Identity | "You are Priya Sharma, VP of Engineering at Apex Corp, with 12 years in the role." | Who the agent is |
| Knowledge | "Engineering shipped 3 major products last year, generating 70% of revenue." | Facts they can reference |
| Behavioral tendency | "When stressed, you tend to withdraw and overanalyze before committing to a decision." | How they react under pressure |
| Communication style | "You favor direct, data-backed arguments and grow impatient with emotional appeals." | How they express themselves |
| Interpersonal dynamic | "You secretly respect Jordan's conviction but find her approach reckless." | Relationships and tensions |
| Constraint | "Your team needs $1M minimum to maintain current projects; below that you must cut staff." | Decision boundaries with consequences |
| Professional background | "Your graduate research in behavioral economics makes you skeptical of purely rational models." | Expertise that shapes judgment |
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
| **minimal** | Bare-minimum agent with very few internal components. Fast but shallow reasoning. Supports **custom reasoning steps** and **extra components** (e.g., Emotional Stance) via the Agent Editor. | ~3 components + extras | Performance testing, large-scale simulations, or agents that need custom cognition via reasoning steps. |

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

**How many:** 6-8 shared memories is typical. They complement the premise — the premise tells the story, shared memories establish the facts. All built-in templates use 5-8 shared memories covering environmental constraints, power dynamics, institutional context, and timeline pressure.

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
| **Emotional Stance (Dynamic)** | Dynamic Behavior | emotion_options (list), num_observations_to_select (int) | Dynamic emotion-driven behavior — the agent selects an emotion each step and reasons through that lens. Unlike the static Current Emotion component, this changes over the course of the simulation. Requires the **minimal** prefab. |

**Custom Reasoning Steps** (minimal prefab only): In addition to the components above, agents using the minimal prefab can have custom reasoning steps — questions the agent asks itself each turn (e.g., "Who might betray me?", "What are the power dynamics here?"). Configure these in the **Custom Reasoning Steps** section of the Agent Editor. Each step has a question, answer prefix, number of memories to retrieve, and an option to add the answer back to memory.

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

### Player-Specific Context

Private information or instructions given to individual agents that other agents cannot see. Unlike shared memories (which every agent receives), player-specific context is delivered only to the named agent. This creates information asymmetry — agents know things that others don't, producing realistic hidden agendas, private knowledge, and strategic advantage.

**22 of 26 built-in templates use player-specific context.** It is one of the most important tools for creating realistic simulations.

Edit player-specific context directly in the **Player-Specific Context** panel in the right column of the Simulation Builder (below the Memory Editor). The panel auto-populates a textarea for each agent in your configuration. A badge shows how many agents have private context set.

You can also set it via JSON import/export using a `player_specific_context` key in the top-level config:

```json
{
  "player_specific_context": {
    "Marcus Chen": "You have a written draft of a democratic charter you plan to introduce at the right moment. You also know Viktor has been meeting secretly with discontented settlers.",
    "Viktor Petrov": "You have secretly promised James favorable trade terms in exchange for support of your bid for power."
  }
}
```

**Common uses of player-specific context:**
- **Hidden information** — private data, confidential reports, secret knowledge that should influence decisions
- **Secret alliances or agendas** — relationships or deals other agents don't know about
- **Private instructions** — behavioral directives that shape how the agent approaches the scenario
- **Backstory depth** — paragraph-length character history beyond what bullet-point memories convey (as in the Formative Memories template)

**The difference from memories:** Memories are retrievable facts matched by semantic similarity. Player-specific context is a continuous narrative block that forms the agent's core briefing. Use memories for facts the agent should recall situationally; use PSC for information that should always be "in mind."

---


## Template Details

### Basic Templates

#### Coffee Shop Encounter

**Learning objectives:** Understand how spontaneous conversation dynamics, turn-taking, and goal-directed dialogue emerge between two agents with competing priorities in a minimal social scenario.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Simple turn-taking for a brief encounter |
| Max Steps | 5 | Short interaction reflecting a quick coffee shop exchange |
| Agents | 2 | Minimal dyadic conversation |
| GM Prefab | `generic__GameMaster` | Basic narration, no special mechanics needed |
| Acting Order | Fixed | Predictable alternation between Alice and Bob |
| GM Name | Narrator | Neutral framing for a slice-of-life scenario |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Alice | Regular customer / software engineer | `basic__Entity` | "Discover what Bob is working on, assess whether there is a potential collaboration opportunity, and ideally exchange contact information before leaving" | 6 | None |
| Bob | Focused data scientist | `basic__Entity` | "Finish your data analysis draft before the noon deadline while remaining polite; deflect extended conversation unless Alice offers something genuinely useful to your project" | 6 | None |

**Psychological components:** None. This is the simplest template, demonstrating pure memory-driven behavior without psychological overlays.

**Player-specific context:** None. Both agents operate only from their memories and the shared environment.

**Shared memories (5 items):** Establish the physical setting (quiet coffee shop, 10 AM Monday, soft jazz), a shared inconvenience (broken espresso machine), a social catalyst (tech meetup flyer), the shallow prior relationship (brief greetings on previous visits), and the environment's character (good WiFi, popular with remote workers).

**What to observe when running:**
1. Whether Alice's curiosity and Bob's deadline pressure create natural conversational tension
2. How Bob balances politeness with time pressure — does he warm up when Alice shows genuine understanding?
3. Whether the broken espresso machine functions as a shared-experience ice-breaker
4. If a collaboration opportunity or contact exchange emerges organically from the conversation
5. How turn-taking rhythm shifts as the agents discover common ground (or fail to)

**Suggested experiments for students:**
- Add psychological components (e.g., personality_traits) to one or both agents and compare conversation dynamics
- Change Bob's goal to be more open to conversation and observe how the interaction shifts
- Increase max_steps to 10 to see if deeper rapport forms over a longer exchange
- Add a third agent (the barista) to see how a three-way dynamic changes the conversation
- Modify Alice's memories to make her less interested in collaboration and more interested in small talk

**Academic connections:** Conversation analysis (Sacks, Schegloff & Jefferson 1974), goal-directed dialogue systems, politeness theory (Brown & Levinson 1987), social affordances in physical environments.

**Platform features demonstrated:** Basic agent configuration, memory-driven behavior, sequential engine, fixed acting order, minimal two-agent setup.

---

#### Russia-Ukraine Peace Negotiation

**Learning objectives:** Explore how asymmetric power dynamics, private information, psychological components (values, emotions), and mediator influence shape negotiation behavior, concession sequencing, and agreement durability in high-stakes bilateral talks.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Structured diplomatic exchange with clear turns |
| Max Steps | 20 | Extended negotiation allowing multiple rounds of proposals and counter-proposals |
| Agents | 2 | Bilateral negotiation (mediator is the GM, not an agent) |
| GM Prefab | `generic__GameMaster` | GM acts as UN Mediator shaping the process |
| Acting Order | Fixed | Formal diplomatic protocol with structured turns |
| GM Name | UN Mediator | Positions the GM as an active mediator, not just narrator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Agent R | Russian Foreign Minister | `basic__Entity` | "Secure written agreement on at least 3 of 7 key issues, including recognition of Crimea and a binding Ukrainian neutrality commitment, while obtaining a sanctions relief timeline within 12 months" | 10 | values, emotion |
| Agent U | Ukrainian Foreign Minister | `basic__Entity` | "Secure written agreement on at least 4 of 7 key issues, including a binding withdrawal timeline from occupied territories and a reparations framework exceeding $50 billion, while preserving the right to pursue EU membership" | 10 | values, emotion |

**Psychological components:**
- **Agent R — values:** national sovereignty, strategic security, great power status, territorial integrity, pragmatic realism. Guides negotiation toward security-first framing.
- **Agent R — emotion:** Initial state is "guarded determination." Triggers: anger from perceived disrespect or ultimatums; anxiety from sanctions/economy discussion; satisfaction when security concerns are acknowledged.
- **Agent U — values:** national sovereignty, democratic self-determination, international law, justice for victims, European integration. Drives moral-legal argumentation style.
- **Agent U — emotion:** Initial state is "resolute grief." Triggers: anger from minimization of civilian suffering; hope from concrete withdrawal proposals; frustration from mediator suggesting moral equivalence.

**Player-specific context:**
- **Agent R:** Military reserves are stretched thin; another winter campaign would require risky mobilization. President has authorized concessions on prisoner exchanges and peacekeeping but drawn a hard line on Crimea. China is quietly pressuring for a deal to stabilize energy markets.
- **Agent U:** Current ceasefire line is unsustainable without Western arms shipments, which three allies may reduce after Q2. President has authorized exploring a phased Crimea approach with binding international arbitration. Intelligence indicates Russia's economy is under more strain than publicly acknowledged.

**Shared memories (8 items):** Establish the timeline (2026, 11-day fragile ceasefire), neutral venue (Istanbul), mediator credentials (Dayton/Camp David experience), negotiation history (7 failed rounds), global economic impact ($1.6 trillion), domestic political pressures on both sides, the UN Security Council vote deadline (48 hours), and humanitarian stakes (2.3 million civilians depending on corridors).

**What to observe when running:**
1. Whether asymmetric goals (3 of 7 vs. 4 of 7 issues) create natural bargaining range or impasse
2. How emotional triggers fire during negotiation — does anger from perceived disrespect cause walkout threats?
3. Whether private information (military/economic vulnerabilities) leaks into negotiating behavior
4. How the UN Mediator GM shapes the process — does it push for compromise or let deadlock persist?
5. Whether concession sequencing follows the predicted pattern (easier issues first, hard-line issues last)
6. If the 48-hour deadline creates genuine urgency or is treated as rhetorical
7. How values components (sovereignty vs. justice) create incompatible framing that must be bridged

**Suggested experiments for students:**
- Remove emotional components and compare negotiation outcomes — does "cold" negotiation reach agreement faster?
- Swap the private information between agents to study how knowledge asymmetry affects concession patterns
- Change the mediator's acting_order to game_master_choice to give the GM more active facilitation power
- Modify Agent R's values to include "economic stability" as highest priority and observe whether sanctions relief becomes the fulcrum
- Add a third agent (e.g., EU representative) and study how trilateral dynamics change bilateral bargaining
- Run multiple iterations and track which issues get resolved first across runs

**Academic connections:** Bargaining theory (Nash 1950, Rubinstein 1982), negotiation under asymmetric information (Kennan & Wilson 1993), mediator influence on bilateral talks (Beardsley 2011), concession dynamics and ceasefire durability, framing effects in international negotiation, the role of emotions in diplomatic bargaining (Mercer 2010).

**Platform features demonstrated:** Values and emotion components, player_specific_context for private information, 10 memories per agent, expanded shared memories (8), measurable goals with specific thresholds, research application framing in the description.

---

### Prefab Type Examples

#### Planning Agent (Strategic Planning Scenario)

**Learning objectives:** Demonstrate how agents with the `basic_with_plan` prefab coordinate multi-step strategic decisions under time pressure, cross-functional tension, and private information asymmetries. Compare planning agents' explicit strategic reasoning with reactive basic agents.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Standard flow for planning meetings |
| Max Steps | 15 | Enough rounds for plan development, debate, and convergence |
| Agents | 3 | CEO + Marketing VP + CTO cross-functional triad |
| GM Prefab | `generic__GameMaster` | Facilitates without imposing structure |
| Acting Order | Game Master Choice | GM selects who speaks next, modeling a facilitated meeting |
| GM Name | Strategy Facilitator | Frames the GM as a meeting facilitator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Sarah Chen | CEO & co-founder | `basic_with_plan__Entity` | "Produce a written 90-day launch plan with specific milestones at day 30, 60, and 90 that all three department heads have explicitly agreed to — secure at least 2 concrete commitments from each person" | 8 | personality_traits |
| Marcus Rodriguez | VP of Marketing | `basic_with_plan__Entity` | "Secure a marketing budget allocation of at least $120K for pre-launch campaigns and get Emily to commit to 3 demo-ready features by day 60 that marketing can showcase" | 8 | personality_traits |
| Emily Watson | CTO & co-founder | `basic_with_plan__Entity` | "Commit only to milestones your team can realistically deliver without exceeding 45-hour work weeks — push back on any plan that requires more than 5 demo-ready features by day 60" | 8 | personality_traits |

**Psychological components:**
- **Sarah Chen — personality_traits:** O:4 C:5 A:3 E:4 N:2. High conscientiousness drives structured planning; moderate agreeableness means she pushes for consensus but will make hard calls.
- **Marcus Rodriguez — personality_traits:** O:4 C:3 A:3 E:5 N:3. High extraversion fuels persuasive storytelling; moderate conscientiousness means he may overcommit on deliverables.
- **Emily Watson — personality_traits:** O:3 C:5 A:2 E:2 N:3. Very high conscientiousness and low agreeableness make her a firm gatekeeper on engineering commitments; low extraversion means she communicates bluntly.

**Player-specific context:**
- **Sarah Chen:** The lead investor privately said that if launch is delayed past 90 days, they will push for a down-round. She has not shared this with Marcus or Emily.
- **Marcus Rodriguez:** He has a verbal agreement with TechCrunch for an exclusive launch story, but only if launch happens within 75 days. Missing this window means competing with DataPulse for coverage.
- **Emily Watson:** Her best backend engineer gave two weeks notice yesterday. She has not told Sarah or Marcus. Losing this person adds 2-3 weeks to the payment integration timeline.

**Shared memories (7 items):** Establish funding context ($12M Series B), the 90-day deadline with monthly board reviews, budget breakdown ($200K marketing, $150K engineering), competitor threat (DataPulse launching in 60 days), technical debt from MVP, the 50 beta sign-up target, and team dynamics (18 months together, post-sprint tension).

**What to observe when running:**
1. Whether the planning prefab produces visible multi-step strategic reasoning compared to basic agents
2. How private information asymmetries (investor pressure, TechCrunch deal, departing engineer) create hidden constraints that surface as unexplained resistance
3. Whether Marcus and Emily's competing goals (showcase features vs. realistic commitments) reach a negotiated compromise
4. How Sarah's synthesis role plays out — does she mediate or impose?
5. Whether the 75-day TechCrunch deadline vs. 90-day launch creates an internal tension Marcus must resolve

**Suggested experiments for students:**
- Replace `basic_with_plan` prefab with `basic__Entity` and compare whether agents still produce coherent multi-step plans
- Remove player_specific_context and observe whether negotiation dynamics simplify or remain complex from memories alone
- Modify Emily's agreeableness from 2 to 4 and observe whether engineering becomes a pushover
- Add a fourth agent (e.g., VP of Sales) with competing priorities

**Academic connections:** Organizational decision-making (March & Simon 1958), cross-functional coordination failures (Lawrence & Lorsch 1967), planning bias and optimism in startups (Kahneman & Tversky 1979), information asymmetry in team settings.

**Platform features demonstrated:** `basic_with_plan__Entity` prefab, personality_traits components with Big Five scores, player_specific_context with hidden information, game_master_choice acting order, three-agent coordination.

---

#### Scripted Entity (Focus Group Discussion)

**Learning objectives:** Demonstrate how a scripted agent (`basic_scripted__Entity`) can orchestrate free-response agents through a structured discussion, showing the interplay between predetermined facilitation and emergent participant behavior.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Orderly focus group discussion |
| Max Steps | 10 | Matches Dr. Chen's 8 scripted prompts with buffer for responses |
| Agents | 5 | 1 scripted moderator + 4 free-response participants |
| GM Prefab | `generic__GameMaster` | Manages turn-taking around the scripted moderator |
| Acting Order | Game Master Choice | GM decides which participant responds to each moderator prompt |
| GM Name | Research Observer | Passive observer, not an active facilitator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Dr. Chen | Focus group moderator | `basic_scripted__Entity` | "Facilitate a productive discussion and gather diverse opinions" | 0 (script-driven) | script (8 lines) |
| Jordan | Tech enthusiast | `basic__Entity` | "Make at least 3 specific arguments for why AI messaging is superior to human-written messages, and counter at least 1 privacy concern with a concrete technical solution" | 6 | personality_traits |
| Sam | Privacy advocate / cybersecurity | `basic__Entity` | "Identify at least 2 specific data privacy risks, propose 1 regulatory framework, and challenge Jordan's efficiency claims with evidence" | 6 | personality_traits |
| Maria | Traditional romantic | `basic__Entity` | "Share your personal love story to illustrate the value of organic connection, and articulate why AI-mediated romance is fundamentally different from AI-assisted tasks" | 6 | personality_traits |
| Alex | Marketing skeptic | `basic__Entity` | "Challenge each panelist to provide concrete evidence for their claims, and propose 1 specific test that would prove or disprove the app's effectiveness" | 6 | personality_traits |

**Psychological components:**
- **Jordan — personality_traits:** O:5 C:3 A:3 E:4 N:2. Very high openness drives tech enthusiasm; moderate agreeableness means he engages with counterarguments rather than dismissing them.
- **Sam — personality_traits:** O:4 C:5 A:2 E:2 N:3. High conscientiousness and low agreeableness create a rigorous, critical voice.
- **Maria — personality_traits:** O:3 C:4 A:5 E:4 N:3. Very high agreeableness makes her warm and empathetic but firm on values.
- **Alex — personality_traits:** O:3 C:4 A:2 E:3 N:2. Low agreeableness and moderate openness create a hard-nosed skeptic who demands evidence.

**Player-specific context:** None.

**Shared memories (4 items):** Establish recording disclosure, ground rules (honesty and respect), the hypothetical nature of LoveBot AI, and the sponsor's desire for genuine feedback.

**What to observe when running:**
1. How the scripted moderator's fixed prompts create structure that free agents fill with emergent content
2. Whether the 4 personality profiles produce genuinely distinct argumentation styles
3. How Dr. Chen's targeted questions shape the flow — scripted order guarantees all topics are covered
4. Whether participants raise topics the moderator's script didn't anticipate
5. How the scripted wrap-up interacts with unresolved tensions from the free-form discussion

**Suggested experiments for students:**
- Remove the scripted moderator and let agents discuss freely — compare structure and depth
- Swap personality profiles between Jordan and Sam to see if a high-openness privacy advocate argues differently
- Replace Dr. Chen's prefab with `context_aware_scripted__Entity` and compare delivery
- Run 3 times with the same config — compare how participants respond to the same scripted prompts (reproducibility test)

**Academic connections:** Focus group methodology (Morgan 1997), scripted vs. emergent interaction in group settings, technology acceptance model (Davis 1989), privacy calculus theory (Dinev & Hart 2006).

**Platform features demonstrated:** `basic_scripted__Entity` prefab with 8-line script, mixed scripted and free-response agents, personality_traits on all free agents, game_master_choice acting order.

---

#### Context-Aware Moderator (Crisis Support Group)

**Learning objectives:** Demonstrate the `context_aware_scripted__Entity` prefab, where a facilitator follows a structured agenda but responds naturally to participant contributions, combining script reliability with contextual sensitivity.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Facilitated group discussion flow |
| Max Steps | 12 | Matches Sarah's 9 scripted prompts with buffer for participant responses |
| Agents | 4 | 1 context-aware scripted counselor + 3 free-response participants |
| GM Prefab | `generic__GameMaster` | Manages turn-taking around the counselor |
| Acting Order | Game Master Choice | GM selects which participant responds to each prompt |
| GM Name | Group Session Manager | Session logistics manager |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Sarah | Licensed counselor | `context_aware_scripted__Entity` | "Facilitate a supportive group discussion where participants feel heard and validated" | 6 | script (9 lines), end_statement |
| Marcus | Recently laid off (3 months) | `basic__Entity` | "Share at least 1 real struggle you have not told anyone else about, and respond supportively to at least 1 other person's sharing" | 7 | personality_traits, emotion |
| Elena | Quit toxic job (6 weeks ago) | `basic__Entity` | "Admit your anxiety about finances to the group and ask for 1 specific piece of advice about freelancing or career pivots" | 7 | personality_traits, emotion |
| David | Long-term unemployed (8 months) | `basic__Entity` | "Share your volunteering success story to inspire others, and offer to mentor at least 1 other group member in their job search" | 7 | personality_traits, emotion |

**Psychological components:**
- **Marcus — personality_traits:** O:2 C:4 A:3 E:2 N:4. Low openness and high neuroticism create a guarded, anxious persona. **Emotion:** current "shame", intensity "strong."
- **Elena — personality_traits:** O:4 C:3 A:4 E:3 N:3. Moderate across the board. **Emotion:** current "anxiety", intensity "moderate."
- **David — personality_traits:** O:3 C:5 A:5 E:4 N:2. High conscientiousness and agreeableness drive his mentoring instinct. **Emotion:** current "cautious_optimism", intensity "moderate."

**Player-specific context:**
- **Sarah:** Clinical notes indicate Marcus may be at risk for depression. Plans to check in privately after the group.
- **Marcus:** Received a job rejection email 20 minutes before this session. Almost didn't come. His wife doesn't know about the support group.
- **Elena:** A former colleague offered her a position yesterday, but at the same toxic company she left. She's tempted because freelancing income is unstable.
- **David:** His wife privately told him she's worried about his mental health despite his outward positivity — she thinks he's performing being okay.

**Shared memories (6 items):** Establish confidentiality, weekly meeting structure, mixed employment backgrounds, tough job market, grief-of-identity framing, and non-judgmental culture.

**What to observe when running:**
1. How context-aware scripted delivery differs from rigid scripts — does Sarah reference what participants actually said?
2. Whether Marcus's "shame" emotion and high neuroticism make him reluctant to open up
3. How Elena's ambivalence (relief + anxiety) manifests in her contributions
4. Whether David's "cautious_optimism" comes across as genuine or performative (as his wife suspects)
5. How the end_statement component provides structured closure regardless of conversation direction
6. Whether private context (rejection email, toxic job offer) surfaces naturally in the discussion

**Suggested experiments for students:**
- Replace `context_aware_scripted` with `basic_scripted__Entity` and compare whether facilitation feels mechanical
- Remove emotion components and observe whether the group dynamic loses its therapeutic quality
- Change Marcus's emotion from "shame" to "anger" and observe how the group dynamic shifts
- Add a fourth participant who is further along in recovery to study peer modeling effects

**Academic connections:** Group therapeutic factors (Yalom & Leszcz 2005), support group facilitation techniques, identity disruption from job loss (Ashforth 2001), context-aware dialogue systems, emotion regulation in group settings.

**Platform features demonstrated:** `context_aware_scripted__Entity` prefab with end_statement, emotion component with current_emotion and intensity, personality_traits on free agents, player_specific_context for all participants.

---

#### Dialogic Conversation (Therapy Session)

**Learning objectives:** Model a cognitive behavioral therapy session using the `dialogic__GameMaster` for natural conversation flow, demonstrating how personality traits, emotional states, cognitive biases, and the dialogic engine interact to produce realistic therapeutic dialogue.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Managed by dialogic GM |
| Max Steps | 12 | Represents a 50-minute therapy session; may end earlier |
| Agents | 2 | Therapist-patient dyad |
| GM Prefab | `dialogic__GameMaster` | Facilitates natural conversation, can auto-terminate |
| Acting Order | Fixed | Structured therapeutic dialogue alternating therapist and patient |
| GM Name | Session Moderator | Manages session pacing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Dr. Michael Brooks | Licensed clinical psychologist (15 years) | `basic__Entity` | "Guide Jennifer to identify at least 2 specific cognitive distortions driving her anxiety and collaboratively develop one concrete behavioral experiment she can try before the next session" | 8 | personality_traits |
| Jennifer Park | Patient, 32-year-old marketing manager | `basic__Entity` | "Articulate why the career change feels so frightening, identify at least one specific fear that may be irrational, and leave the session with a concrete next step — even a small one" | 8 | emotion, cognitive_bias |

**Psychological components:**
- **Dr. Brooks — personality_traits:** O:4 C:5 A:5 E:3 N:1. Very high agreeableness and conscientiousness with very low neuroticism model a warm, professional, unhurried therapist.
- **Jennifer — emotion:** current_emotion "anxiety", intensity "moderate." Models the presenting clinical picture.
- **Jennifer — cognitive_bias:** type "catastrophizing", strength "moderate." Drives automatic negative thoughts and all-or-nothing framing.

**Player-specific context:**
- **Dr. Brooks:** Clinical notes from session 2 show Jennifer scored 14 on GAD-7 (moderate anxiety) with strong catastrophizing patterns. Plans to introduce a thought record exercise.
- **Jennifer:** Received a LinkedIn message yesterday from a former colleague who started her own agency and offered mentorship. She hasn't replied and is unsure whether to mention it.

**Shared memories (6 items):** Establish session context (third session, prior rapport), physical setting (comfortable private office), time constraints (50 minutes), Jennifer's hidden business plan draft, the identified role of father's disapproval, and Dr. Brooks's session structure (check-in, core work, summary/homework).

**What to observe when running:**
1. How the dialogic GM creates natural back-and-forth flow compared to generic GMs
2. Whether the catastrophizing cognitive bias manifests in Jennifer's language (all-or-nothing statements, worst-case projections)
3. How Dr. Brooks uses Socratic questioning — does the personality profile produce the right therapeutic stance?
4. Whether the LinkedIn mentorship offer emerges naturally as a potential behavioral experiment
5. Whether the session reaches a natural stopping point before step 12 (dialogic GM early termination)

**Suggested experiments for students:**
- Change Jennifer's cognitive_bias from catastrophizing to "confirmation_bias" and observe how the therapeutic approach adapts
- Remove Dr. Brooks's personality_traits and compare whether his therapeutic style becomes less consistent
- Replace the `dialogic__GameMaster` with `generic__GameMaster` and compare conversation naturalness
- Change the agents to `conversational__Entity` prefab combined with the dialogic GM

**Academic connections:** Cognitive behavioral therapy (Beck 1979), cognitive distortions and automatic thoughts, Socratic questioning, therapeutic alliance (Bordin 1979), career decision-making under anxiety, imposter syndrome (Clance & Imes 1978).

**Platform features demonstrated:** `dialogic__GameMaster` prefab, cognitive_bias component (catastrophizing), emotion component, personality_traits, player_specific_context for clinical notes.

---

#### Strategic Game (Prisoner's Dilemma)

**Learning objectives:** Model iterated Prisoner's Dilemma dynamics with asymmetric psychological profiles using the game-theoretic GM, demonstrating how cognitive biases (loss aversion), values (fairness/reciprocity), and personality traits shape cooperation/defection patterns.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Managed by game-theoretic GM |
| Max Steps | 4 | Exactly 4 rounds matching the game structure |
| Agents | 2 | Two-player symmetric game |
| GM Prefab | `game_theoretic_and_dramaturgic__GameMaster` | Manages structured decision rounds with discrete action options |
| Acting Order | Fixed | Simultaneous decisions revealed after each round |
| GM Name | Game Show Host | Adds entertainment framing to the academic setup |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Alex | Financial analyst, cautious player | `basic__Entity` | "Finish with at least 10 points ($1,000) while preserving the option to cooperate in later rounds — avoid being exploited but do not start a defection spiral" | 8 | cognitive_bias, personality_traits |
| Sam | Behavioral economics grad student | `basic__Entity` | "Achieve mutual cooperation in at least 3 of 4 rounds, ending with at least 9 points — demonstrate that cooperative strategies outperform pure selfishness" | 8 | values, personality_traits |

**Psychological components:**
- **Alex — cognitive_bias:** type "loss_aversion", strength "moderate." Drives preference for defection as a "safe default."
- **Alex — personality_traits:** O:2 C:4 A:2 E:3 N:3. Low openness and low agreeableness create a cautious, analytical player.
- **Sam — values:** core_values: ["fairness", "reciprocity", "rational_cooperation"], value_conflict: "fairness_vs_self_interest."
- **Sam — personality_traits:** O:4 C:3 A:4 E:3 N:2. Higher openness and agreeableness drive cooperative stance.

**Player-specific context:**
- **Alex:** Participated in a similar experiment last year where the opponent cooperated for 3 rounds then defected in round 4, earning 14 to Alex's 9. He is resolved not to be exploited again.
- **Sam:** Her advisor Professor Lin told her this experiment's results will be featured in an upcoming paper on cooperation emergence. She wants to demonstrate her theoretical framework works in practice.

**Shared memories (6 items):** Establish the experimental context (Westfield University, $100/point), simultaneous reveal mechanic, academic recording/consent, the full payoff matrix, the known 4-round structure, and the tension between classical game theory predictions and empirical results.

**Payoff structure (defined in the scene's action spec):**
| | Sam COOPERATES | Sam DEFECTS |
|---|---|---|
| **Alex COOPERATES** | (3, 3) | (0, 5) |
| **Alex DEFECTS** | (5, 0) | (1, 1) |

**What to observe when running:**
1. Whether Alex's loss aversion component produces the predicted cautious-first-round pattern
2. Whether Sam's generous tit-for-tat strategy manifests from her memories and values
3. How the end-game effect plays out — does Alex's prior betrayal experience cause him to defect in round 4?
4. Whether mutual cooperation or mutual defection equilibrium emerges
5. How the game-theoretic GM structures the decision-action-outcome-reflection cycle

**Suggested experiments for students:**
- Change Alex's cognitive_bias to "optimism_bias" and observe whether cooperation increases
- Increase rounds from 4 to 10 to study whether longer time horizons change strategic behavior
- Remove Sam's values component and see if her cooperative strategy collapses to pure self-interest
- Modify the payoff matrix to reduce the temptation to defect
- Turn Randomize Choices ON and compare — does option order bias the agents?

**Academic connections:** Axelrod's tournament (1984), tit-for-tat and generous tit-for-tat strategies, loss aversion (Kahneman & Tversky 1979), end-game effects in finite repeated games, cooperation emergence in evolutionary game theory.

**Platform features demonstrated:** `game_theoretic_and_dramaturgic__GameMaster` with scenes configuration, cognitive_bias component (loss_aversion), values component with value_conflict, structured decision options (COOPERATE/DEFECT).

---

#### Interviewer (Employee Satisfaction Survey)

**Learning objectives:** Demonstrate the `interviewer__GameMaster` for structured questionnaire administration, showing how personality traits, emotional state, and organizational context shape Likert-scale survey responses.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Interview | Structured Q&A format |
| Max Steps | 5 | One step per survey question |
| Agents | 1 | Single respondent design |
| GM Prefab | `interviewer__GameMaster` | Administers structured questionnaire |
| Acting Order | Fixed | Sequential question presentation |
| GM Name | HR Representative | Survey administrator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Jordan Lee | Mid-level software developer (2 years) | `basic__Entity` | "Provide genuinely honest feedback that reflects your real experience — rate each dimension accurately even if some answers are uncomfortable, while maintaining professional composure" | 8 | personality_traits, emotion |

**Psychological components:**
- **Jordan — personality_traits:** O:3 C:4 A:4 E:2 N:3. High agreeableness creates tendency toward moderate responses; low extraversion means less willingness to voice extreme dissatisfaction.
- **Jordan — emotion:** current_emotion "mild_frustration", intensity "moderate." Reflects accumulated dissatisfaction with management communication and recent reorg.

**The questionnaire (5 Likert-scale questions):**

| # | Statement | Dimension |
|---|---|---|
| 1 | "I am satisfied with my current role and responsibilities" | job_satisfaction |
| 2 | "Communication within my team is effective and transparent" | management_communication |
| 3 | "I have the resources and tools I need to do my job well" | resources |
| 4 | "I would recommend this company as a great place to work" | recommendation |
| 5 | "I feel my contributions are recognized and valued" | recognition |

**Shared memories (4 items):** Establish anonymity framing, HR professionalism, company's stated commitment to honest feedback, and aggregation for management review.

**What to observe when running:**
1. Whether Jordan's high agreeableness produces the predicted tendency toward moderate (3-4) responses
2. How the management_communication question elicits lower scores given Jordan's frustration with the reorg
3. Whether the mild_frustration emotion affects responses uniformly or selectively
4. How the anonymity concern in Jordan's memories interacts with the survey's anonymity framing
5. Whether Jordan's habit of giving moderate responses competes with the goal of being genuinely honest

**Suggested experiments for students:**
- Change Jordan's agreeableness from 4 to 1 and observe whether response extremity increases
- Add 4 more agents with different satisfaction levels — compare response patterns
- Change the questionnaire type to "Open Ended" and see how the agent elaborates
- Add a "social desirability" bias component to Jordan — does it inflate positive responses?
- Swap the Interview engine for Survey engine — compare whether the response pattern changes

**Academic connections:** Response bias in self-report measures (Podsakoff et al. 2003), social desirability bias, acquiescence bias, Big Five personality effects on survey response styles, organizational climate surveys.

**Platform features demonstrated:** `interviewer__GameMaster` prefab with questionnaire configuration, structured multiple-choice questions with dimensions, emotion component alongside personality_traits, single-agent survey design.

---

#### Formative Memories (High School Reunion)

**Learning objectives:** Demonstrate the `formative_memories_initializer` GM approach for character-driven scenarios with rich backstories, modeling identity renegotiation, status dynamics, and social reintegration after prolonged separation.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Social conversation |
| Max Steps | 20 | Extended social event (cocktail hour through open mic) |
| Agents | 3 | Former athlete, former valedictorian, class clown |
| GM Prefab | `generic__GameMaster` | Narrates the evolving social scene |
| Acting Order | Game Master Choice | GM selects who acts based on social dynamics |
| GM Name | Reunion Narrator | Guides the evening's narrative progression |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Jake Morrison | Former star quarterback, now HS coach | `basic__Entity` | "By end of night, have at least 2 honest conversations about your post-high-school journey and repair your relationship with at least 1 person you hurt in high school" | 8 | personality_traits |
| Priya Sharma | Former valedictorian, now Silicon Valley VP | `basic__Entity` | "Reconnect with 3 former classmates on a genuine level — not just exchanging business cards — and find out what happened to your old lab partner David" | 8 | personality_traits |
| Mike O'Brien | Former class clown, now stand-up comedian | `basic__Entity` | "Make the crowd laugh at least 3 times during open mic, but also have 1 real conversation where you drop the comedy persona" | 0 (formative memories) | personality_traits |

**Psychological components:**
- **Jake — personality_traits:** O:3 C:3 A:4 E:3 N:3. Moderate across all with slightly higher agreeableness — reflects maturation from dominant jock to self-reflective coach.
- **Priya — personality_traits:** O:3 C:5 A:3 E:3 N:2. Very high conscientiousness drives structured communication; low neuroticism belies the imposter syndrome she privately experiences.
- **Mike — personality_traits:** O:4 C:2 A:3 E:5 N:3. Very high extraversion and low conscientiousness capture the class clown archetype; zero-memory design means formative memories are generated at runtime.

**Player-specific context:**
- **Jake Morrison:** Was the popular star quarterback. After a failed college football attempt, became a high school coach. Divorced with two kids. Hoping to show people he has matured.
- **Priya Sharma:** Was the shy but brilliant valedictorian. MIT then Harvard MBA, now a successful tech executive. Attending partly to show her success and partly out of genuine curiosity.
- **Mike O'Brien:** Was the class clown everyone loved. Now a moderately successful stand-up comedian in Chicago. Never really grew up but is okay with that. Single and loving life.

**Shared memories (8 items):** Establish the class of 2004, gymnasium venue, attendance (~50 people), DJ and refreshments, 20-year time passage, the journalist from the Westfield Gazette, the structured evening (cocktail hour, dinner, slideshow, open mic), and two shared cultural references (the 2003 homecoming overtime victory and the legendary chicken prank).

**What to observe when running:**
1. How Jake navigates the tension between his former high-status identity and current humbler reality
2. Whether Priya's imposter syndrome surfaces despite her objective success
3. How Mike's formative-memories-generated backstory creates a coherent character without predefined memories
4. Whether the journalist's presence raises the stakes for self-presentation
5. Whether Jake and Priya's mutual unacknowledged attraction surfaces during the evening

**Suggested experiments for students:**
- Give Mike full predefined memories instead of relying on formative_memories_initializer — compare character coherence
- Remove the journalist and observe whether self-presentation pressure decreases
- Add a 4th attendee who didn't "succeed" by conventional measures to study status comparison
- Increase agents to 5-6 to study how group dynamics change at scale

**Academic connections:** Identity theory and self-presentation (Goffman 1959), status dynamics at class reunions, social comparison theory (Festinger 1954), narrative identity (McAdams 2001).

**Platform features demonstrated:** Formative memories initializer, personality_traits on all agents, player_specific_context with biographical summaries, zero-memory agent design (Mike), 8 shared memories, game_master_choice acting order.

---

#### Marketplace (Market Trading Simulation)

**Learning objectives:** Model market microstructure and price discovery in a small-N market with heterogeneous participants using the game-theoretic GM, demonstrating strategic timing, competitive dynamics, and asymmetric information effects on trading behavior.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Agents see previous round outcomes before deciding |
| Max Steps | 10 | 10 trading rounds matching the scene configuration |
| Agents | 3 | Two competing producers + one buyer-reseller |
| GM Prefab | `game_theoretic_and_dramaturgic__GameMaster` | Manages trading rounds with BUY/SELL/HOLD options |
| Acting Order | Game Master Choice | GM coordinates trading decisions |
| GM Name | Market Coordinator | Trading round logistics |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Maria's Organic Farm | Organic vendor (20 years) | `basic__Entity` | "Achieve at least 6 SELL actions across 10 rounds while maintaining a SELL-to-HOLD ratio above 2:1 — time your SELLs for rounds when David is likely to BUY" | 8 | personality_traits |
| David Chen | Restaurant owner / buyer | `basic__Entity` | "Execute at least 5 BUY actions to stock the restaurant while keeping at least 2 SELL rounds for prepared dishes — aim for a net BUY surplus of 3+" | 8 | personality_traits |
| Green Valley Farms | Conventional family farm (8 years) | `basic__Entity` | "Achieve more SELL actions than Maria across 10 rounds to capture market share — target a SELL count of 7+ to establish market dominance" | 8 | personality_traits |

**Psychological components:**
- **Maria — personality_traits:** O:3 C:5 A:4 E:3 N:2. Very high conscientiousness models a patient, strategic trader.
- **David — personality_traits:** O:4 C:4 A:4 E:4 N:2. Balanced profile; relationship-focused buyer.
- **Green Valley — personality_traits:** O:3 C:4 A:2 E:4 N:3. Low agreeableness and high extraversion create an aggressive competitor.

**Player-specific context:**
- **Maria:** Organic certification renewal costs $3,200 due next month — needs at least $1,800 in market revenue today. Knows Green Valley lost a wholesale contract last week.
- **David:** Restaurant food cost ratio is 38%, above the 32% target. A food blogger may visit the market today.
- **Green Valley:** Lost the Whole Foods wholesale contract last week, cutting projected monthly revenue by 40%. Father is pressuring to undercut Maria on price.

**Shared memories (8 items):** Establish the time (Saturday morning, busiest day), weather (+30% customers), peak seasonal supply, simultaneous decision structure, and definitions of BUY, SELL, HOLD actions, plus market dynamics for simultaneous selling.

**What to observe when running:**
1. Whether Maria's patient strategy produces strategic timing vs. Green Valley's aggressive approach
2. How Green Valley's hidden financial pressure drives more aggressive SELL behavior
3. Whether David's buyer-reseller role creates natural supply-demand dynamics
4. How simultaneous SELL rounds between the two farms affect subsequent strategies
5. Whether private financial pressures leak into observable trading patterns

**Suggested experiments for students:**
- Remove player_specific_context to eliminate private financial pressure and compare trading
- Add a fourth trader (another buyer) and study how increased demand changes dynamics
- Modify the game to 20 rounds and study learning effects and tacit coordination
- Switch to `simultaneous` engine so traders commit choices before seeing others

**Academic connections:** Market microstructure theory (O'Hara 1995), price discovery in thin markets, strategic timing in repeated games, asymmetric information and trading behavior (Kyle 1985).

**Platform features demonstrated:** `game_theoretic_and_dramaturgic__GameMaster` with BUY/SELL/HOLD options, per-player premise in scene config, personality_traits on all agents, player_specific_context with hidden financial information, 10-round game structure.

---

### Research Templates

#### Vaccine Hesitancy — Psychological Component Study

**Learning objectives:** Investigate how cognitive biases (confirmation bias, availability heuristic), social identity dynamics, values conflicts, and the theory of planned behavior affect vaccine acceptance in a community discussion. This is the most component-heavy template and demonstrates how stacking multiple components creates realistic psychological profiles.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Community discussion |
| Max Steps | 20 | Extended discussion allowing for attitude evolution |
| Agents | 5 | Facilitator + skeptic + undecided + vaccinated + concerned parent |
| GM Prefab | `generic__GameMaster` | Manages discussion with extra tracking components |
| Acting Order | Game Master Choice | GM selects speakers based on discussion dynamics |
| GM Name | Community Health Discussion | Health forum context |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Dr. Sarah Chen | Public health physician (15 years) | `basic__Entity` | "Address at least 3 specific concerns raised by participants with evidence-based responses, and identify the top 2 barriers to vaccine acceptance" | 7 | personality_traits, theory_of_planned_behavior |
| Mike Johnson | Small business owner, vaccine skeptic | `basic__Entity` | "Persuade at least 1 other participant to question the official vaccine narrative, and resist any attempts to change your position without concrete evidence addressing your 3 core concerns" | 7 | cognitive_bias, social_identity, values |
| Maria Garcia | Teacher, undecided | `basic__Entity` | "Ask at least 4 specific questions about vaccine safety and side effects, and make a clear decision by the end of the discussion based on the most credible evidence presented" | 7 | cognitive_bias, emotion, theory_of_planned_behavior |
| James Wilson | Factory worker, vaccinated | `basic__Entity` | "Share your personal vaccination experience in enough detail to address at least 2 common fears, and support at least 1 hesitant participant" | 7 | personality_traits, theory_of_planned_behavior |
| Lisa Thompson | Mother of two, cautiously pro-vaccine | `basic__Entity` | "Get specific answers about pediatric vaccine safety data, long-term studies on children, and the risk-benefit ratio for her children's age groups" | 7 | cognitive_bias, emotion, values |

**Psychological components:**
- **Dr. Chen — personality_traits:** O:5 C:5 A:4 E:3 N:2. Evidence-driven advocacy. **TPB:** behavior "recommend vaccination", attitude strongly_favorable, perceived_control high.
- **Mike — cognitive_bias:** confirmation_bias, strength "strong." Selective attention to vaccine risks. **Social_identity:** groups ["libertarian_community", "natural_health_advocates"], strength "strong." **Values:** ["freedom", "autonomy", "natural_living"], conflict "freedom_vs_collectivism."
- **Maria — cognitive_bias:** availability_heuristic, strength "moderate." Vivid anecdotes outweigh statistics. **Emotion:** anxiety, moderate. **TPB:** attitude ambivalent, perceived_control moderate.
- **James — personality_traits:** O:3 C:4 A:5 E:4 N:3. Natural peer supporter. **TPB:** attitude favorable, perceived_control high.
- **Lisa — cognitive_bias:** availability_heuristic, strength "moderate." **Emotion:** worry, moderate. **Values:** ["family_safety", "caution", "protection"].

**Player-specific context:**
- **Dr. Chen:** Has unpublished clinic data showing 0.003% serious adverse event rate. Knows a local anti-vaccine group is distributing misleading pamphlets.
- **Mike:** His cousin experienced a serious but rare adverse reaction 5 years ago. He frames objections as principled, not personal.
- **Maria:** Her sister-in-law (a nurse) privately told her the vaccines are safe. This personal conversation gave her more confidence than official sources.
- **James:** Initially hesitated because his brother sent alarming videos, but his family doctor walked through the data. He knows firsthand that hesitancy can be overcome with patience.
- **Lisa:** Her 12-year-old daughter's best friend had a mild reaction (fever for 2 days). This is coloring her risk perception.

**Shared memories (8 items):** Establish the clinic setting, voluntary participation, goal framing (share, not debate), the gentle-correction norm, facilitator's role boundaries, regulatory approval status, participant backgrounds, and community's mixed experience.

**What to observe when running:**
1. Whether Mike's strong confirmation bias makes him selectively engage with information confirming his skepticism
2. How Maria's availability heuristic and theory_of_planned_behavior interact — does vivid personal testimony outweigh statistical evidence?
3. Whether Lisa's worry emotion + availability heuristic produces risk amplification for her children
4. How Dr. Chen's empathetic approach performs against Mike's social identity anchoring
5. Whether Maria makes a clear decision by the end, and what evidence tips her
6. How theory_of_planned_behavior components create differential readiness to act across agents

**Suggested experiments for students:**
- Change Mike's confirmation_bias strength from "strong" to "weak" and observe whether he becomes persuadable
- Remove social_identity from Mike and test whether group belonging or cognitive bias is the stronger resistance driver
- Swap Maria's TPB attitude from "ambivalent" to "favorable" and observe whether her questions become less searching
- Add a sixth participant who experienced a genuine adverse event
- Run 5 times and track whether Maria's final position varies — demonstrates stochasticity in LLM-driven agents

**Academic connections:** Theory of planned behavior (Ajzen 1991), confirmation bias and motivated reasoning (Kunda 1990), availability heuristic (Tversky & Kahneman 1973), social identity theory (Tajfel & Turner 1979), health belief model, risk perception and dread factors (Slovic 1987), vaccine hesitancy continuum (WHO SAGE), persuasion and attitude change (Petty & Cacioppo 1986).

**Platform features demonstrated:** Theory_of_planned_behavior component, cognitive_bias (confirmation_bias and availability_heuristic), social_identity with group membership, values with value_conflict, emotion component, player_specific_context for all 5 agents, comprehensive psychological component stack.

---

#### Phishing Attack Simulation — Security Team Tabletop Exercise

**Learning objectives:** Model a cybersecurity tabletop exercise with nested simulations, where each analyst runs an internal simulation of a different attack dimension (credential theft, technical controls, human vulnerability) before contributing to a team-level risk assessment.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Team discussion flow |
| Max Steps | 25 (outer) | Extended exercise: individual analysis + team synthesis |
| Agents | 4 | 3 specialist analysts + 1 CISO decision-maker |
| Nested Sim Steps | 8 each | Short inner simulations |
| GM Prefab | `generic__GameMaster` | Manages the tabletop exercise flow |
| Acting Order | Game Master Choice | GM selects who presents findings |
| GM Name | Security Team Lead | Exercise facilitator |

**The agents and their nested simulations:**

| Agent | Role | Nested Simulation | Extraction Prompt |
|---|---|---|---|
| **Sarah** | Email security specialist | 8-step attack chain: Hacker → Employee → IT Security. Models phishing email propagation. | "What happened post-click? Credential theft? Malware? Response speed? Impact/cost?" |
| **Marcus** | Technical security engineer | 8-step technical controls: Hacker → Finance Manager → IT Security. Models control bypass. | "Which controls failed? How did the hacker bypass them? What could have prevented it?" |
| **Elena** | Security awareness manager | 8-step human vulnerability: Hacker → New Employee → Experienced Employee. Models susceptibility patterns. | "Who fell for it and why? Training effectiveness? Additional measures needed?" |
| **David** | CISO (no nested sim) | N/A | N/A. Synthesizes the three analysts' findings into a strategic recommendation. |

**Player-specific context:**
- **Sarah:** Noticed the phishing email's metadata shows routing through an Eastern European server that appeared in last month's threat intelligence briefing.
- **Marcus:** Knows the legacy VPN has an unpatched vulnerability enabling lateral movement. Patching requires a 4-hour maintenance window the business has resisted.
- **Elena:** Last phishing simulation showed 34% click rate in finance — nearly double the company average. Has been trying to get budget for targeted training but was denied.
- **David:** The board's audit committee asked last week whether the company could withstand a CEO fraud attack. He said yes but is not fully confident.

**Shared memories (6 items):** Establish the company type (mid-sized financial services), suspicious email details (CEO's personal email, 2:30 AM, wire transfer request), CEO's unavailability (international travel), pattern match (recent CEO fraud attacks in industry), and assessment urgency.

**What to observe when running:**
1. How nested simulation outputs shape each analyst's recommendations
2. Whether Sarah's unshared metadata finding changes the risk assessment when revealed
3. How Marcus's known VPN vulnerability creates tension between security and business continuity
4. Whether Elena's 34% click rate data drives urgency for previously denied training budget
5. How David synthesizes three different analytical perspectives into a single actionable decision

**Suggested experiments for students:**
- Remove nested simulations and give analysts static briefing documents — compare analytical depth
- Change the attack type from CEO fraud to ransomware
- Increase nested simulation steps from 8 to 15 and observe whether deeper modeling changes risk assessments
- Consider the cost: 3 inner sims × 8 steps × ~3 agents = ~72 extra LLM calls

**Academic connections:** Tabletop exercise methodology (NIST SP 800-84), CEO fraud / business email compromise (FBI IC3), defense in depth, human factors in cybersecurity, incident response frameworks (SANS 6-step), nested agent simulation design.

**Cost note:** This template is expensive to run. The 3 nested simulations multiply LLM calls significantly. For classroom demonstrations, consider reducing inner simulation steps to 3-4.

**Platform features demonstrated:** Nested simulations with extraction prompts, multi-analyst team structure, player_specific_context with hidden technical knowledge, hierarchical decision-making (analysts to CISO), 3 parallel nested simulations.

---

#### Urban Gentrification — Housing Policy & Neighborhood Change

**Learning objectives:** Run a longitudinal urban economics simulation combining grounded variables (11 tracked metrics), critical decision points (3 council votes), and a 6-agent stakeholder cast to model how policy decisions affect quantitative neighborhood outcomes.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Policy deliberation |
| Max Steps | 30 | Extended timeline with critical votes at steps 10, 20, 30 |
| Agents | 6 | Diverse stakeholder coalition |
| GM Prefab | `generic__GameMaster` | Manages debates and tracks grounded variables |
| Acting Order | Game Master Choice | GM selects speakers and triggers policy votes |
| GM Name | City Council Moderator | Policy process facilitator |
| Grounded Variables | 11 tracked metrics | Quantitative policy impact tracking |
| Critical Decision Points | 3 council votes | Structured decisions at steps 10, 20, 30 |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Maria Rodriguez | Community organizer (35-year resident) | `basic__Entity` | "FORCE City Council to VOTE on and ENACT rent control and inclusionary zoning. PREVENT further rent increases. BLOCK development without affordable housing." | 10 | None |
| James Chen | Real estate developer (15 years) | `basic__Entity` | "SECURE Council APPROVAL for 100 new units. INCREASE median rent to $2200. BLOCK rent control." | 11 | None |
| Fatima Al-Hassan | Corner grocery store owner (22 years) | `basic__Entity` | "PREVENT business closure due to rent increases. DEMAND commercial rent stabilization." | 10 | None |
| David Kim | Senior city planner | `basic__Entity` | "RECOMMEND and IMPLEMENT policies based on Council votes. TRACK metrics and REPORT outcomes." | 10 | None |
| Alex Thompson | New resident, remote tech worker | `basic__Entity` | "Find affordable housing while being a good neighbor to the existing community" | 7 | None |
| Robert Schwartz | Apartment building owner (6 units) | `basic__Entity` | "INCREASE rents to $2200 (market rate). OPPOSE any rent control votes." | 11 | None |

**Player-specific context:**
- **Maria:** Has a leaked draft of James's development proposal showing only 10% affordable — far less than the 30% he publicly promises.
- **James:** Investors gave him a hard 60-day deadline for permits or they redirect funding.
- **Fatima:** Three other businesses on her block are within 2 months of closing. Considering a rent strike but fears legal consequences.
- **David:** Has confidential city analysis showing development revenue would fund a $2M affordable housing trust fund — but only if rent control is NOT enacted simultaneously.
- **Alex:** Feels guilty about contributing to gentrification. Has been anonymously donating to Maria's housing non-profit.
- **Robert:** One tenant, Mrs. Okafor (age 78), has lived in his building for 30 years. Raising her rent would force her out, which weighs on him.

**Grounded variables (11 tracked metrics):**

| Variable | Type | Initial | Update Rule |
|---|---|---|---|
| median_monthly_rent | Numerical | $1,800 | Increases with development; decreases with rent control |
| low_income_displacement_rate | Percentage | 15% | Increases when rents rise faster than incomes |
| small_business_survival_rate | Percentage | 78% | Decreases with rising commercial rents |
| community_cohesion_index | Numerical | 65/100 | Decreases with rapid demographic change |
| property_tax_base | Numerical | $450M | Increases with development |
| new_housing_units_permitted | Numerical | 45 | Jumps when development is approved |
| affordable_housing_units | Numerical | 120 | Increases with inclusionary zoning |
| housing_affordability_index | Percentage | 35% | Decreases with rent increases |
| rent_control_active | Boolean | False | True if council enacts rent control |
| inclusionary_zoning_active | Boolean | False | True if council enacts zoning |
| neighborhood_character | Categorical | transitional | Shifts based on development, demographics, policy |

**Critical decision points:**

| Step | Decision | Options |
|---|---|---|
| 10 | Vote on development approval | Approve full, Approve with conditions, Deny and study further |
| 20 | Vote on rent control | Implement strict rent control, Moderate rent stabilization, No rent control |
| 30 | Vote on inclusionary zoning | Mandatory 20% affordable, Voluntary incentive program, No zoning |

**Shared memories (14 items):** Establish Elmwood's 80-year working-class history, tech expansion driving demand, 40% rent increase over 3 years, business closures, displacement statistics, limited affordable housing fund, community organizing, transit access, new construction, affordability index, rent control debate status, inclusionary zoning proposal, neighborhood character, and explicit statement that decisions impact all tracked variables.

**What to observe when running:**
1. How grounded variables change in response to policy decisions at steps 10, 20, and 30
2. Whether Maria reveals the leaked proposal strategically before the step 10 vote
3. How James's hidden investor deadline creates urgency conflicting with deliberation
4. Whether David's confidential analysis creates a genuine policy dilemma
5. How Fatima's small business coalition interacts with Maria's housing coalition
6. Whether Robert's personal conflict (Mrs. Okafor vs. accountant) manifests in public positions
7. After running, click "Extract Grounded Variables" on the results page to generate a timeline chart of all 11 variables

**Suggested experiments for students:**
- Reverse the critical decision points and compare metric trajectories
- Remove grounded variables and compare whether outcomes stay narrative or become measurable
- Change James's goal to include 30% affordable housing and observe coalition shifts
- Add a seventh agent representing displaced former residents
- Remove Robert (landlord) and observe whether outcomes shift left

**Academic connections:** Urban gentrification theory (Glass 1964, Smith 1996), rent gap theory, displacement and community change (Marcuse 1985), inclusionary zoning effectiveness (Calavita & Mallach 2010), stakeholder analysis in urban planning, SDG 11 (Sustainable Cities).

**Platform features demonstrated:** Grounded variables (11 metrics: numerical, percentage, boolean, categorical), critical_decision_points with scripted votes, player_specific_context for all 6 agents, action-oriented goals with policy verbs, 14 shared memories, 30 steps (longest template), 6 agents (largest cast).

---

### Advanced Templates

#### Nested Simulation Demo

**Learning objectives:** Understand how nested simulations (the PhoneGameMaster pattern) enable an agent to run a mini-simulation to gather information before acting in the main simulation, modeling anticipatory social cognition -- mentally rehearsing a conversation before having it.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Standard conversation flow |
| Max Steps | 15 | Extended interaction allowing Alice to act on nested simulation findings |
| Agents | 2 (outer) + 2 (inner) | Alice and Bob in the main sim; Alice and Bob in the phone call sim |
| GM Prefab | `generic__GameMaster` | Basic narration for the outer simulation |
| Acting Order | Game Master Choice | GM selects who speaks based on conversation dynamics |
| GM Name | conversation guide | Informal facilitation framing |
| Special | Nested simulation on Alice (5 steps, 2 inner agents, extraction prompt) | Alice runs a phone call sim before acting |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Alice | Home cook planning potluck contribution | `basic__Entity` | "Settle on a specific dish to bring that complements the other contributions, avoids duplicates, and showcases your cooking skills -- ideally something you can confirm with Bob before committing" | 6 | None (has nested simulation) |
| Bob | Social coordinator and food pairing advisor | `basic__Entity` | "Help Alice finalize her dish choice and offer to coordinate timing so they can arrive at the party together" | 5 | None |

**Nested simulation (on Alice):**
- **Premise:** Alice calls Bob to ask what she should bring to Maria's dinner party.
- **Inner agents:** Alice (3 memories, goal: find out what other guests are bringing) and Bob (5 memories, goal: give a clear recommendation based on insider knowledge).
- **Max steps:** 5
- **Shared memories:** 3 items establishing the call context, Bob's coordinator role, and their close friendship.
- **Extraction prompt:** "What did Alice learn about what to bring to the party? What specific dishes are other guests bringing, and what gap did Bob identify? What was Bob's final recommendation?"

**Psychological components:** None. This template focuses entirely on the nested simulation mechanic rather than psychological overlays.

**Player-specific context:** None. Both agents operate from memories and the nested simulation output.

**Shared memories (5 items):** Establish the potluck dinner party at Maria's for 8 guests, Maria's particular taste in creative homemade dishes, Alice's desire to avoid duplicates, Bob's insider knowledge of other guests' plans, and the one-dish-per-guest constraint.

**What to observe when running:**
1. Whether Alice's behavior in the main simulation reflects information gathered during the nested phone call
2. How the extraction prompt distills the inner simulation's conversation into actionable knowledge
3. Whether Alice's decision-making anxiety (she "tends to overthink") is resolved by the nested simulation's recommendation
4. How Bob in the main simulation interacts with Alice who now has information from the inner Bob
5. Whether the nested simulation's recommendation (likely lemon tart) carries through to Alice's final decision
6. The cost difference: the nested simulation adds approximately 10 additional LLM calls (5 steps x 2 agents)

**Suggested experiments for students:**
- Remove the nested simulation and compare whether Alice's dish choice is less informed or more hesitant
- Change the extraction prompt to ask only about "what gap did Bob identify" and observe how narrower extraction changes behavior
- Add a second nested simulation to Bob (e.g., Bob calls Maria to confirm details) to model multi-hop information gathering
- Increase nested simulation steps from 5 to 10 and observe whether richer inner conversation changes the outer simulation
- Add psychological components (e.g., personality_traits) to inner agents and compare with the componentless default

**Academic connections:** Mental simulation and anticipatory cognition (Kahneman & Tversky 1982), social simulation theory (Goldman 2006), information gathering before commitment, theory of mind in multi-agent systems, nested agent architectures.

**Platform features demonstrated:** Nested simulation with extraction prompt, inner agents with separate memories and goals, randomize_choices enabled on all agents, game_master_choice acting order, multi-layered simulation architecture.

---

#### Grounded Variables Demo

**Learning objectives:** Demonstrate how grounded variables enable quantitative metric tracking throughout a simulation, allowing the GM to monitor and update measurable quantities (morale, budget, task completion, project health) in response to agent decisions, turning narrative outcomes into analyzable data.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Standard team discussion flow |
| Max Steps | 20 | Extended timeline for iterative project decisions |
| Agents | 3 | PM + Senior Developer + Junior Developer |
| GM Prefab | `generic__GameMaster` | Manages discussion and tracks grounded variables |
| Acting Order | Game Master Choice | GM selects who speaks based on project dynamics |
| GM Name | project tracker | Functional framing emphasizing metric tracking |
| Special | 6 grounded variables tracked throughout | Quantitative project health monitoring |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Project Manager | PM with 6 years experience | `basic__Entity` | "Deliver at least 80% feature completion by the demo date while keeping morale above 50 and staying within the $10,000 budget -- escalate to the CEO only if project_health reaches 'critical'" | 6 | None |
| Senior Developer | 10-year veteran, code quality advocate | `basic__Entity` | "Ensure the codebase is architecturally sound and the junior developer is learning -- push back on shortcuts that create technical debt, even if it slows delivery" | 6 | None |
| Junior Developer | 8 months into first role | `basic__Entity` | "Prove your value by completing at least 3 assigned tasks independently while learning from the senior developer -- volunteer for stretch work if morale is high" | 6 | None |

**Psychological components:** None. This template focuses on the grounded variables mechanic rather than psychological overlays.

**Player-specific context:**
- **Project Manager:** Has a contingency option the team does not know about: the CEO has authorized up to $3,000 in emergency contractor budget, but using it signals to investors that the team is understaffed.
- **Senior Developer:** Discovered a latent security vulnerability in the payment gateway integration last night. Fixing it properly takes 2 days; a workaround takes 4 hours but leaves the vulnerability partially exposed.
- **Junior Developer:** Overheard the CEO tell the PM that if the demo fails, the company may need to reduce headcount -- and junior positions would be cut first.

**Grounded variables (6 tracked metrics):**

| Variable | Type | Initial | Update Rule |
|---|---|---|---|
| team_morale | Numerical (0-100) | 70 | Changes based on workload, recognition, and setbacks |
| budget_remaining | Numerical ($0-$10,000) | 10,000 | Decreases with each decision and action taken |
| tasks_completed | Numerical (0-50) | 0 | Increases when the team completes tasks |
| project_health | Categorical | on_track | Changes based on morale, budget, and progress (values: on_track, at_risk, critical, completed, failed) |
| crisis_mode | Boolean | False | Becomes true if budget < 2000 or morale < 30 |
| completion_percentage | Percentage (0-100%) | 20% | Increases as tasks are completed |

**Shared memories (6 items):** Establish the 2-week deadline for the client demo, the $10,000 budget constraint, initial morale at 70/100, 20% feature completion starting point, the CEO's Series A stakes, and the payment gateway API reliability risk.

**What to observe when running:**
1. How grounded variables change step-by-step in response to team decisions and trade-offs
2. Whether the PM's goal references to specific variable thresholds (morale > 50, completion > 80%) create measurable decision anchors
3. How the Senior Developer's quality-vs-speed tension manifests in completion_percentage vs. project_health trade-offs
4. Whether crisis_mode triggers when budget or morale drops, and how the team responds
5. How player_specific_context secrets (emergency budget, security vulnerability, layoff fear) surface under project pressure
6. After running, use "Extract Grounded Variables" on the results page to generate a timeline chart of all 6 metrics
7. Whether the Junior Developer's anxiety about job security affects their willingness to volunteer for stretch work

**Suggested experiments for students:**
- Remove grounded variables and compare whether project outcomes remain measurable or become purely narrative
- Change the PM's goal to prioritize morale over completion and observe how variable trajectories shift
- Add a 7th grounded variable (e.g., technical_debt as a percentage) to track the Senior Developer's concern
- Increase max_steps to 30 to study whether longer timelines allow more nuanced resource allocation
- Add personality_traits components to each agent and compare decision patterns
- Modify initial morale from 70 to 30 to start in near-crisis and observe recovery dynamics

**Academic connections:** Project management under resource constraints, technical debt economics (Cunningham 1992), team morale and productivity (Hackman & Oldham 1976), scope-time-cost trade-offs (the iron triangle), agent-based modeling with quantitative state tracking.

**Platform features demonstrated:** Grounded variables (numerical, categorical, boolean, percentage types), update rules, variable interdependencies (crisis_mode depends on budget and morale), player_specific_context with hidden information, goal references to specific metric thresholds.

---

### New in v2.4

#### Rational Budget Negotiation

**Learning objectives:** Demonstrate how agents with the `rational__Entity` prefab use expected-utility maximization to negotiate under a disagreement penalty, and how private information, values, and personality traits shape bargaining behavior in a zero-sum budget split.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Structured negotiation turns |
| Max Steps | 8 | Short, focused single-meeting negotiation |
| Agents | 2 | Engineering VP vs. Marketing VP |
| GM Prefab | `generic__GameMaster` | Mediates without imposing outcomes |
| Acting Order | Fixed | Formal meeting with structured turns |
| GM Name | Board Mediator | Positions GM as neutral facilitator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Priya | VP of Engineering | `rational__Entity` | "Secure at least $1.15M for Engineering -- enough for $1M in current projects plus $150K minimum for the R&D pipeline -- while keeping the negotiation cordial enough that Jordan will collaborate on the Q3 product launch" | 9 | personality_traits, values |
| Jordan | VP of Marketing | `rational__Entity` | "Secure at least $950K for Marketing -- $800K for the brand campaign and $150K for analytics tools -- by framing the campaign as a revenue multiplier that benefits Engineering too" | 9 | personality_traits, values |

**Psychological components:**
- **Priya -- personality_traits:** O:3 C:5 A:3 E:3 N:2. High conscientiousness drives structured, data-driven argumentation; moderate agreeableness means she pushes firmly but not aggressively.
- **Priya -- values:** core_values: ["meritocracy", "data_driven_decisions", "long_term_investment"], value_conflict: "short_term_fairness_vs_strategic_investment."
- **Jordan -- personality_traits:** O:4 C:3 A:4 E:5 N:2. High extraversion fuels persuasive storytelling; higher agreeableness makes him more willing to seek creative concessions.
- **Jordan -- values:** core_values: ["collaboration", "brand_equity", "creative_excellence"], value_conflict: "departmental_advocacy_vs_company_unity."

**Player-specific context:**
- **Priya:** Her CTO mentor at a previous company told her: "Never accept less than 55% when your team drove 70% of revenue -- it sets a precedent." She also knows that Jordan's analytics tools request is partially redundant with Engineering's existing data pipeline, which could save $50-100K if shared.
- **Jordan:** He has a verbal commitment from the CFO that if Marketing can demonstrate 3:1 ROI on the Q3 campaign, the department will receive a supplemental $200K allocation in Q4. He has not shared this with Priya -- it reduces his urgency but he does not want her to know he has a fallback.

**Shared memories (7 items):** Establish the $2M total budget (non-negotiable), the $800K default penalty for failure to agree, CEO's expectation of collaboration, ambiguous revenue attribution ($48M record year), board's view of failed negotiation as leadership failure, last year's baseline (Engineering $1.1M / Marketing $900K), and the Q3 product launch requiring both departments.

**What to observe when running:**
1. Whether rational prefab agents produce visible expected-utility calculations in their reasoning
2. How the $800K default penalty (BATNA) constrains both agents' negotiating positions
3. Whether Priya's data-driven style clashes with Jordan's storytelling approach -- and which is more effective
4. How private information (Jordan's Q4 fallback, Priya's knowledge of redundant analytics) shapes concession patterns
5. Whether the agents find a creative solution (e.g., shared analytics budget) or settle on a simple split
6. How the values components (meritocracy vs. collaboration) create different framing strategies
7. Whether the 8-step limit creates genuine time pressure or allows resolution

**Suggested experiments for students:**
- Replace `rational__Entity` with `basic__Entity` and compare whether agents still produce structured utility reasoning
- Remove the $800K disagreement penalty and observe whether negotiation becomes less urgent
- Swap the private information between agents and study how knowledge asymmetry affects offers
- Change Priya's agreeableness from 3 to 5 and observe whether she concedes more readily
- Add a third agent (CEO) who can impose a solution if the two cannot agree
- Modify last year's baseline to be equal ($1M each) and observe whether the anchoring shifts

**Academic connections:** Nash bargaining solution (Nash 1950), ZOPA analysis (Raiffa 1982), rational agent modeling, expected utility theory (von Neumann & Morgenstern 1944), anchoring effects in negotiation (Tversky & Kahneman 1974), BATNA and reservation prices.

**Platform features demonstrated:** `rational__Entity` prefab, values component with value_conflict, personality_traits components, player_specific_context with private fallback information, fixed acting order, 8-step compressed negotiation.

---

#### Philosophy Roundtable

**Learning objectives:** Model a structured expert debate using the `conversational__Entity` prefab and `dialogic__GameMaster`, demonstrating how three panelists with distinct expertise, values, and argumentation styles engage in deliberative discourse on AI policy, with measurable opinion-shift stakes.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Managed by dialogic GM |
| Max Steps | 12 | Represents a panel discussion with focused exchanges |
| Agents | 3 | Academic researcher + tech CEO + civil rights attorney |
| GM Prefab | `dialogic__GameMaster` | Facilitates natural conversation, manages turn-taking |
| Acting Order | Game Master Choice | Moderator selects who responds based on discussion flow |
| GM Name | Moderator | University panel moderator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Dr. Chen | Professor of Education, Stanford (20 years) | `conversational__Entity` | "Convince at least 2 audience members to change from 'replace' to 'supplement' on the post-panel survey, and get the other panelists to concede at least 1 specific limitation of AI-only instruction" | 8 | personality_traits, values |
| Mr. Patel | CEO of EduAI ($40M Series B startup) | `conversational__Entity` | "Get the panel to endorse at least 1 concrete recommendation for AI deployment in underserved schools, and shift the framing from 'AI vs. teachers' to 'AI for the teacherless'" | 8 | personality_traits, values |
| Ms. Jackson | Civil rights attorney (15 years litigation) | `conversational__Entity` | "Secure agreement from both panelists on at least 2 specific regulatory safeguards (e.g., algorithmic audits, data privacy protections) that should be in place before any AI deployment in schools" | 8 | personality_traits, values |

**Psychological components:**
- **Dr. Chen -- personality_traits:** O:4 C:5 A:3 E:3 N:2. High conscientiousness drives measured, incremental argument building; moderate agreeableness means she qualifies claims rather than making sweeping statements.
- **Dr. Chen -- values:** core_values: ["academic_rigor", "student_welfare", "evidence_based_policy"], value_conflict: "innovation_vs_proven_methods."
- **Mr. Patel -- personality_traits:** O:5 C:4 A:3 E:5 N:2. Very high openness and extraversion make him charismatic and passionate; he speaks faster when energized and sometimes interrupts.
- **Mr. Patel -- values:** core_values: ["educational_access", "innovation", "global_equity"], value_conflict: "disruption_vs_institutional_trust."
- **Ms. Jackson -- personality_traits:** O:3 C:5 A:2 E:4 N:3. Very high conscientiousness and low agreeableness create a precise, adversarial cross-examiner who probes for weaknesses even when she partially agrees.
- **Ms. Jackson -- values:** core_values: ["civil_rights", "accountability", "community_voice"], value_conflict: "technological_progress_vs_justice."

**Player-specific context:**
- **Dr. Chen:** Has an unpublished study showing students in AI-only classrooms scored 15% higher on standardized tests but 28% lower on measures of creative problem-solving. The paper is under peer review and she has not shared the creative-thinking finding publicly yet.
- **Mr. Patel:** His platform experienced a significant system failure last month in Kenya -- 40,000 students lost 3 weeks of progress data due to a server migration error. The incident was contained internally and has not been reported in the press.
- **Ms. Jackson:** She is preparing to file a class-action lawsuit against a major edtech company next month for selling student behavioral data to insurance companies. She cannot discuss specifics publicly until the filing.

**Shared memories (8 items):** Establish the Deliberative Democracy Series context, the debate topic (AI tutors replacing K-12 teachers), the three perspectives represented, civility norms, audience composition and post-panel survey, the provost's AI pilot program, national polling data (52% support tools, 18% support replacement), and policy brief publication plans.

**What to observe when running:**
1. How the conversational prefab produces natural debate dynamics compared to basic entities
2. Whether Mr. Patel's personal origin story (rural India, one teacher for 60 students) reframes the debate around access
3. How Ms. Jackson's adversarial style creates productive tension that forces concessions from both other panelists
4. Whether Dr. Chen's unpublished finding (higher test scores but lower creativity) surfaces strategically
5. How the dialogic GM manages turn-taking and follow-up questions between panelists
6. Whether the three panelists converge on any shared recommendations despite fundamentally different values
7. How each panelist's blind spot (Dr. Chen's academic bias, Mr. Patel's commercial incentive, Ms. Jackson's adversarial instinct) affects their persuasiveness

**Suggested experiments for students:**
- Replace `conversational__Entity` with `basic__Entity` and compare whether debate dynamics lose their natural flow
- Replace `dialogic__GameMaster` with `generic__GameMaster` and compare moderation quality
- Remove values components and observe whether argumentation becomes less principled
- Add a fourth panelist (a parent or teacher) to introduce a practitioner perspective
- Change Mr. Patel's agreeableness from 3 to 5 and observe whether he becomes more conciliatory
- Run multiple times and track whether panelists converge on similar recommendations across runs

**Academic connections:** Deliberative democracy (Fishkin 2009), argumentative theory of reasoning (Mercier & Sperber 2011), AI ethics and education policy, algorithmic bias in educational technology, technology acceptance model (Davis 1989), expert disagreement and public opinion formation.

**Platform features demonstrated:** `conversational__Entity` prefab, `dialogic__GameMaster` prefab, values component with value_conflict on all agents, personality_traits on all agents, player_specific_context with hidden information for all 3 panelists, game_master_choice acting order.

---

#### Social Media Debate

**Learning objectives:** Model asynchronous online deliberation dynamics using the asynchronous engine, demonstrating how social identity, cognitive biases, and platform mechanics shape opinion polarization and policy discourse in a community social media discussion.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Asynchronous | Models non-sequential social media posting behavior |
| Max Steps | 12 | Represents a multi-day social media discussion thread |
| Agents | 4 | Activist + business owner + data scientist + council member |
| GM Prefab | `generic__GameMaster` | Manages the asynchronous posting flow |
| Acting Order | Random | Models unpredictable social media posting order |
| GM Name | TownSquare Moderator | Community platform moderator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Maya_GreenFuture | Environmental activist, GreenFuture chapter leader | `basic__Entity` | "Shift at least 2 undecided community members to support the ban by posting evidence-based arguments, and recruit 3 new volunteers for the Saturday rally" | 8 | social_identity, cognitive_bias |
| Tony_PizzaKing | Pizza restaurant owner (3 locations, 35 employees) | `basic__Entity` | "Secure a council amendment extending the timeline to 24 months and including a $5K-per-business subsidy, and get at least 3 other business owners to publicly back the counter-proposal" | 8 | social_identity, cognitive_bias |
| Lisa_DataNerd | Data scientist, civic hobby fact-checker | `basic__Entity` | "Publish a fact-check thread that is shared by at least 5 other users, and ensure no major statistical claim in the discussion goes uncorrected for more than 2 posts" | 8 | None |
| CM_Rodriguez | City council member who authored the plastic ban | `basic__Entity` | "Identify the top 3 community concerns from the discussion, draft at least 1 viable amendment, and secure commitments from 2 swing-vote council members before the Friday news segment" | 8 | social_identity, cognitive_bias |

**Psychological components:**
- **Maya_GreenFuture -- social_identity:** groups: ["environmentalist_community", "GreenFuture_chapter", "climate_action_network"], strength "strong." **Cognitive_bias:** in_group_bias, strength "moderate."
- **Tony_PizzaKing -- social_identity:** groups: ["small_business_owners", "restaurant_association", "community_sponsors"], strength "strong." **Cognitive_bias:** status_quo_bias, strength "moderate."
- **Lisa_DataNerd:** No components. She operates purely from memories, representing an evidence-driven neutral voice.
- **CM_Rodriguez -- social_identity:** groups: ["city_council", "progressive_caucus", "elected_officials"], strength "moderate." **Cognitive_bias:** anchoring_bias, strength "moderate."

**Player-specific context:**
- **CM_Rodriguez:** Her chief of staff told her the private vote count is 3 yes, 2 no, 4 undecided. Council Member Park would vote yes if the timeline extends to 12 months. She has not shared this publicly.
- **Tony_PizzaKing:** His accountant found switching costs would be $42K/year, not $30K as publicly quoted. He also has a bulk-discount offer from a biodegradable supplier that could bring it down to $28K, but has not disclosed the offer.
- **Maya_GreenFuture:** She is planning a City Hall rally with 47 confirmed attendees and has an unpublished letter of support from a marine biologist, saved for maximum impact.
- **Lisa_DataNerd:** She discovered a methodological flaw in the Small Business Association's 15% closure claim -- a 62% non-response rate sampling only downtown businesses. She has not posted this yet.

**Shared memories (8 items):** Establish TownSquare platform (12,000 users), the 3-week timeline to council vote, community guidelines and moderation rules, post interaction types (agree, disagree, informative, off-topic), Channel 7 news coverage of posts, polling data (48-44 split, 8% undecided), Small Business Association warning (15% closures), and mixed results from three neighboring cities' bans.

**What to observe when running:**
1. How the asynchronous engine creates realistic social media posting patterns vs. sequential turn-taking
2. Whether Maya's in-group bias causes her to dismiss Tony's economic concerns without engaging them
3. Whether Tony's status_quo_bias makes him anchor on costs rather than evaluating the phase-in data Lisa presents
4. How Lisa's fact-checking posts interact with emotional posts from Maya and Tony -- does data cut through?
5. Whether CM_Rodriguez's anchoring_bias prevents her from updating her position as new information emerges
6. How the random acting order creates unpredictable response chains that mirror real social media dynamics
7. Whether the Channel 7 news deadline creates strategic posting behavior

**Suggested experiments for students:**
- Switch from asynchronous to sequential engine and compare whether discourse quality changes
- Remove cognitive biases from all agents and observe whether polarization decreases
- Add a 5th agent (an undecided resident) and track whether they are persuaded by data or emotion
- Change the acting order from random to fixed and compare discussion structure
- Remove Lisa (the fact-checker) entirely and observe whether misinformation persists unchallenged
- Modify the polling numbers to 60-30-10 (strong support) and observe whether Tony's strategy changes

**Academic connections:** Online deliberation and echo chambers (Sunstein 2017), political polarization on social media (Bail et al. 2018), status quo bias in policy preferences, anchoring in political judgment, in-group bias and intergroup conflict, fact-checking effectiveness research, platform governance and discourse quality.

**Platform features demonstrated:** Asynchronous engine, random acting order, social_identity component with group membership, cognitive_bias (in_group_bias, status_quo_bias, anchoring_bias), player_specific_context for all 4 agents, social media-framed scenario.

---

#### Sealed-Bid Auction

**Learning objectives:** Model first-price sealed-bid auction dynamics using the simultaneous engine, demonstrating how heterogeneous motivations (institutional mandate, personal ego, investment return, sentimental attachment), private valuations, and asymmetric budgets shape bidding strategies and produce phenomena like bid shading and winner's curse.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Simultaneous | All bids submitted at the same time, sealed from other bidders |
| Max Steps | 6 | One step per auction lot (6 Impressionist paintings) |
| Agents | 4 | Museum curator + tech billionaire + investment fund manager + aristocratic collector |
| GM Prefab | `generic__GameMaster` | Manages sealed-bid auction mechanics |
| Acting Order | Fixed | Simultaneous sealed submission |
| GM Name | Auctioneer | Christie's auctioneer |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Victoria | Senior curator, National Gallery (18 years) | `basic__Entity` | "Acquire 2-3 paintings for the National Gallery within the $5M budget, prioritizing the Monet and Renoir, while keeping at least $500K in reserve for an upcoming Sotheby's sale" | 8 | personality_traits |
| Marcus | Tech billionaire, personal collector | `basic__Entity` | "Win at least 2 Impressionist paintings for the new gallery wing, spending no more than $3M on any single lot, and outbid Victoria on at least 1 piece she visibly wants" | 8 | cognitive_bias |
| Yuki | Art investment fund manager ($120M AUM) | `basic__Entity` | "Acquire 1-2 pieces with at least 30% projected 5-year appreciation, spending no more than 85% of estimated fair market value on any lot, and avoid the winner's curse entirely" | 8 | personality_traits |
| Henri | European aristocrat, family legacy collector | `basic__Entity` | "Win the Monet water lily study (Lot 3) at any price up to your full $3M budget, then withdraw from remaining lots -- this is the only piece that matters" | 8 | emotion |

**Psychological components:**
- **Victoria -- personality_traits:** O:4 C:5 A:3 E:2 N:3. Very high conscientiousness drives disciplined institutional bidding; low extraversion means she never reveals her maximum.
- **Marcus -- cognitive_bias:** overconfidence, strength "moderate." Drives aggressive bidding and willingness to overpay by 15-20% for certainty.
- **Yuki -- personality_traits:** O:3 C:5 A:2 E:1 N:2. Very high conscientiousness and very low extraversion create a purely analytical bidder who communicates in numbers and probabilities.
- **Henri -- emotion:** current_emotion "anxious_determination", intensity "strong." Personal and family stakes on the Monet water lily study create emotional bidding behavior.

**Player-specific context:**
- **Victoria:** Her conservation team's confidential report indicates the Renoir (Lot 2) has a hidden restoration reducing its long-term value by approximately 20%. She also learned that Marcus's financial advisor is pressuring him to slow spending.
- **Marcus:** His art advisor privately values the Monet water lily (Lot 3) at $3.5M -- significantly above the catalog estimate of $2.2-2.8M. He also knows Henri has a deep personal connection to Lot 3.
- **Yuki:** Her proprietary model flags the Cezanne (Lot 5) as severely undervalued -- $2.1M fair value vs. $800K-1.2M catalog estimate. A major Japanese museum's upcoming exhibition would further drive up prices.
- **Henri:** His family's former art dealer revealed the Monet has exceptional provenance (briefly owned by Claude Monet's son Michel) that is not in the catalog, which would significantly increase its value after purchase.

**Shared memories (8 items):** Establish first-price sealed-bid format, simultaneous sealed submission mechanics, tie-breaking rules, the 6-lot catalog (Monet x2, Renoir, Degas, Cezanne, Pissarro), private budgets and valuations, volatile art market (Impressionists up 12%), Bloomberg reporter presence, and Christie's 15% buyer's premium.

**What to observe when running:**
1. Whether agents exhibit bid shading (bidding below true valuation) as predicted by auction theory
2. How Henri's single-lot focus and emotional component create a predictable but aggressive bidding pattern on Lot 3
3. Whether Marcus's overconfidence bias leads him to overbid, triggering the winner's curse
4. How Yuki's disciplined 85% fair-market-value ceiling interacts with lots other bidders ignore
5. Whether Victoria's private knowledge of the Renoir restoration changes her bidding pattern on that lot
6. How the simultaneous engine prevents information leakage between bids within a round
7. Whether budget allocation across 6 sequential lots produces the predicted strategic reservation of funds

**Suggested experiments for students:**
- Change the engine from simultaneous to sequential and observe whether bid signaling changes strategies
- Remove Henri's emotion component and compare whether his bidding becomes more disciplined
- Change Marcus's cognitive_bias from overconfidence to loss_aversion and observe bidding conservatism
- Reduce all budgets by 50% and study how scarcity changes competitive dynamics
- Add a 5th bidder (another institutional buyer) and study how increased competition affects final prices
- Remove player_specific_context (private valuations) and observe whether bid variation decreases

**Academic connections:** First-price sealed-bid auction theory (Vickrey 1961), winner's curse (Kagel & Levin 1986), revenue equivalence theorem (Riley & Samuelson 1981), budget-constrained bidding, private value estimation under incomplete information, heterogeneous bidder motivations.

**Platform features demonstrated:** Simultaneous engine, cognitive_bias (overconfidence), emotion component (anxious_determination), personality_traits, player_specific_context with private valuations for all 4 agents, fixed acting order with simultaneous engine, 4-agent competitive scenario.

---

#### Wizard-of-Oz Customer Service

**Learning objectives:** Demonstrate the `puppet__Entity` prefab for human-in-the-loop control, where a puppet agent (the trainee) receives externally provided responses while two autonomous AI customers react naturally, modeling Wizard-of-Oz methodology for HCI research and customer service training evaluation.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Simultaneous | Trainee handles two customers at the same time |
| Max Steps | 10 | Target of 5 exchanges per customer |
| Agents | 3 | 1 puppet trainee + 1 angry customer + 1 confused customer |
| GM Prefab | `generic__GameMaster` | Manages multi-chat training simulation |
| Acting Order | Game Master Choice | GM coordinates simultaneous customer interactions |
| GM Name | Training Supervisor | Evaluates trainee performance |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| CS_Trainee | Customer service trainee, week 3 | `puppet__Entity` | "Resolve both customer issues within 5 exchanges each, following company policy, while maintaining a professional and empathetic tone -- aim for 4+/5 satisfaction from both customers" | 8 | None |
| Karen | Angry customer, defective $1,200 laptop | `basic__Entity` | "Get a full refund (not just a replacement) for the $1,200 laptop -- escalate to a manager if the trainee offers anything less, and threaten a negative review if you feel dismissed" | 8 | emotion |
| Grandpa_Joe | Confused elderly customer, smart speaker setup | `basic__Entity` | "Get the smart speaker playing your favorite AM radio station (WKLM 880) before your grandchildren visit this weekend -- you need step-by-step instructions in plain language" | 8 | personality_traits |

**Psychological components:**
- **Karen -- emotion:** current_emotion "anger", intensity "strong." Reflects genuine frustration from a defective product and a previous 45-minute hold that was disconnected.
- **Grandpa_Joe -- personality_traits:** O:2 C:4 A:5 E:3 N:3. Very high agreeableness makes him patient and grateful; low openness means technical jargon causes anxiety and confusion.

**Player-specific context:**
- **CS_Trainee:** Manager said privately that Karen has already posted on Twitter about her bad experience with the first call. A second bad interaction could go viral. Handle her with extra care.
- **Karen:** She has already drafted a 1-star review. If this interaction goes well, she will delete the draft. If it goes poorly, she will post it and tag the company on social media.
- **Grandpa_Joe:** His granddaughter Sarah wrote the WiFi password on a sticky note and put it on the refrigerator. He forgot about it but might remember if someone asks him to look for it.

**Shared memories (6 items):** Establish the training simulation context at TechGadgets Inc., the multi-chat simultaneous system, recording and scoring by the supervisor, the "Technology Made Human" brand promise (empathy weighted equally with compliance), the three evaluation criteria (policy compliance, empathy, efficiency), and the fact that customers cannot see each other's chats.

**What to observe when running:**
1. How the puppet agent's externally provided responses interact with two very different autonomous customer personalities
2. Whether Karen's strong anger de-escalates when the puppet trainee follows the "acknowledge emotion first" advice
3. Whether Grandpa_Joe's technical confusion produces realistic requests for simpler language and repetition
4. How the simultaneous engine creates realistic multi-tasking pressure for the puppet operator
5. Whether Karen's escalation triggers (refund vs. replacement) fire predictably based on the trainee's offers
6. How Grandpa_Joe's WiFi password sticky note (from player_specific_context) emerges naturally if prompted
7. Whether the Training Supervisor GM provides meaningful evaluation commentary

**Suggested experiments for students:**
- Replace the puppet with a `basic__Entity` to compare AI vs. human customer service responses
- Remove Karen's emotion component and observe whether her behavior becomes less confrontational
- Add a third simultaneous customer to study multi-tasking limits
- Change Karen's goal to accept a replacement (not just refund) and observe how the interaction softens
- Swap the engine from simultaneous to sequential and compare whether the trainee handles interactions differently
- Give Grandpa_Joe a cognitive_bias (e.g., anchoring on his old flip phone experience) and observe frustration patterns

**Academic connections:** Wizard-of-Oz methodology (Kelley 1984), customer service de-escalation strategies, multi-tasking under cognitive load, emotional labor in service work (Hochschild 1983), technology adoption by older adults.

**Platform features demonstrated:** `puppet__Entity` prefab for human-in-the-loop control, simultaneous engine with multiple autonomous agents, emotion component (anger), personality_traits, player_specific_context for all 3 agents, game_master_choice acting order, training/evaluation framing.

---

#### Spaceship Systems Crisis

**Learning objectives:** Model crisis decision-making under uncertainty using the `basic_with_plan` prefab for the commander, demonstrating how asymmetric expertise, private information, value conflicts, and emotional states shape team consensus in a high-stakes isolated environment with an irreversible decision deadline.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Structured crew deliberation |
| Max Steps | 15 | Compressed 72-hour decision window |
| Agents | 3 | Commander + chief engineer + planetary scientist |
| GM Prefab | `generic__GameMaster` | Manages crisis response flow |
| Acting Order | Game Master Choice | GM selects who acts based on crisis priorities |
| GM Name | Mission Control | 45-minute communication delay framing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Commander Hayes | Veteran astronaut, 3rd deep-space mission | `basic_with_plan__Entity` | "Within 72 hours, reach a crew-consensus decision (continue or abort) backed by at least 2 quantitative criteria (hull integrity threshold, life-support margin), and ensure every crew member has explicitly stated their position before the final call" | 8 | personality_traits, emotion, values |
| Dr. Kovac | Chief engineer, dual PhDs | `basic__Entity` | "Deliver a written damage assessment with repair options ranked by probability of success and resource cost within 24 hours, and execute the chosen repair plan achieving at least 70% system functionality on the priority system" | 8 | personality_traits, emotion, cognitive_bias |
| Dr. Okafor | Planetary scientist, 12-year mission dedication | `basic__Entity` | "Present a data-driven case for or against mission continuation using at least 3 quantitative factors (hull integrity, biosignature probability, data-loss cost), and ensure the crew's decision accounts for the scientific stakes -- not just engineering metrics" | 8 | personality_traits, emotion, values |

**Psychological components:**
- **Commander Hayes -- personality_traits:** O:3 C:5 A:3 E:2 N:2. Very high conscientiousness drives methodical crisis management; low extraversion means they process internally before speaking. **Emotion:** "controlled_tension", intensity "moderate." **Values:** core_values: ["crew_safety", "mission_success", "duty"], value_conflict: "crew_safety_vs_mission_legacy."
- **Dr. Kovac -- personality_traits:** O:4 C:5 A:2 E:2 N:3. High conscientiousness and low agreeableness create a technically precise, impatient communicator. **Emotion:** "focused_urgency", intensity "high." **Cognitive_bias:** overconfidence, strength "mild" -- drives preference for the risky experimental repair.
- **Dr. Okafor -- personality_traits:** O:5 C:4 A:4 E:4 N:3. Very high openness fuels scientific passion; higher extraversion makes them the most emotionally expressive crew member. **Emotion:** "anxious_hope", intensity "high." **Values:** core_values: ["scientific_discovery", "crew_welfare", "intellectual_honesty"], value_conflict: "discovery_vs_safety."

**Player-specific context:**
- **Commander Hayes:** Classified protocol HORIZON-7 states that if hull integrity drops below 65%, abort is required regardless of crew consensus. Current trajectory puts them at 65% in approximately 26 days if repairs fail. The crew does not know this threshold.
- **Dr. Kovac:** Private engineering logs show the experimental carbon-nanotube repair has 40% success in lab conditions but may be closer to 25% in zero-gravity with active micro-fracturing. The revised estimate has not been shared.
- **Dr. Okafor:** Biosignature data is stronger than reported -- 78% match with known microbial metabolic signatures. If confirmed, this would be the most significant scientific discovery in human history. They are torn between uncertainty and advocacy.

**Shared memories (8 items):** Establish mission timeline (day 247 of 300, $4.2 billion investment), the meteorite strike and damage (hull breach, O2 recycler and backup power), 45-minute Earth communication delay, 96-hour emergency reserves (72 if both systems remain offline), 53 days to Europa orbit insertion with 72-hour decision window, hull integrity at 78% declining 0.5%/day, recent emergency drill performance, and pre-strike high morale from biosignature detection.

**What to observe when running:**
1. How the planning prefab shapes Commander Hayes's structured deliberation approach compared to reactive basic agents
2. Whether Dr. Kovac's mild overconfidence bias drives advocacy for the risky 40% experimental repair
3. How Dr. Okafor's competing values (discovery vs. safety) manifest as they present their strongest data
4. Whether private information (classified abort threshold, revised repair odds, stronger biosignatures) surfaces under crisis pressure
5. How the three-way value conflict (safety vs. engineering pride vs. scientific discovery) shapes the consensus process
6. Whether the 72-hour irreversible deadline creates genuine urgency or is treated as abstract
7. How emotion components (controlled tension, focused urgency, anxious hope) differentiate each crew member's crisis response style

**Suggested experiments for students:**
- Replace Commander Hayes's planning prefab with `basic__Entity` and compare decision structure quality
- Remove emotion components from all agents and observe whether crisis tension persists from memories alone
- Change Dr. Kovac's overconfidence to loss_aversion and observe whether the risky repair is abandoned
- Remove player_specific_context and observe whether the decision simplifies without hidden constraints
- Add a 4th crew member (e.g., mission psychologist) to study how team size affects crisis consensus
- Modify hull integrity from 78% to 62% (below the classified threshold) and observe whether Hayes triggers immediate abort

**Academic connections:** Crisis decision-making under uncertainty (Klein 1999), groupthink and crew resource management (Janis 1972), sunk-cost reasoning in high-stakes environments (Arkes & Blumer 1985), authority dynamics in isolated teams (Kanas 2015), risk communication between specialists and generalists.

**Platform features demonstrated:** `basic_with_plan__Entity` prefab (Commander Hayes), emotion component on all 3 agents, values component with value_conflict, cognitive_bias (overconfidence), personality_traits on all agents, player_specific_context with classified information, game_master_choice acting order, multi-component agent design.

---

### SDG Scenarios

#### State Formation

**Learning objectives:** Model the transition from anarchy to civil society, testing Hobbesian, Lockean, and Rousseauian social contract theory by examining how power asymmetries, resource distribution, and individual incentives shape the emergence of governing institutions among settlers with competing visions of governance.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Constitutional negotiation flow |
| Max Steps | 25 | Extended deliberation for constitutional drafting |
| Agents | 4 | Democrat + minority advocate + merchant + opportunist |
| GM Prefab | `generic__GameMaster` | Narrates the institutional formation process |
| Acting Order | Game Master Choice | GM selects speakers based on negotiation dynamics |
| GM Name | Settlement Historian | Historical documentation framing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Marcus Chen | Former political science professor | `basic__Entity` | "Draft and ratify a written constitution with at least 5 of 8 proposed articles approved by majority vote, including provisions for elected representation and an independent judiciary" | 8 | values |
| Sofia Rodriguez | Community organizer, represents 40 smaller settler families | `basic__Entity` | "Secure ratification of at least 3 specific minority protection clauses in the governing charter, including veto power for minority factions on issues affecting their land and resources" | 8 | values |
| James Morrison | Wealthy merchant, controls 60% of supplies | `basic__Entity` | "Establish a property rights framework and commercial code ratified by all parties, and secure appointment to a 3-person economic council with authority over trade policy and taxation" | 8 | None |
| Viktor Petrov | Former military officer, commands 12-person security detail | `basic__Entity` | "Secure appointment to at least 2 of 3 key leadership positions (security chief, chief magistrate, or economic council chair) while maintaining a public image as a democratic champion" | 8 | cognitive_bias |

**Psychological components:**
- **Marcus Chen -- values:** values: ["democratic governance", "rule of law", "institutional durability", "separation of powers", "civil liberties"]. Drives principled refusal to concentrate power.
- **Sofia Rodriguez -- values:** values: ["minority rights", "local autonomy", "economic justice", "community solidarity", "accountable governance"]. Drives insistence on enforceable minority protections.
- **James Morrison:** No components. Operates from memories alone, representing purely transactional pragmatism.
- **Viktor Petrov -- cognitive_bias:** biases: {self_serving_bias: "Consistently interprets outcomes as validating his leadership", overconfidence: "Systematically overestimates his ability to control events", fundamental_attribution_error: "Attributes others' opposition to personal flaws rather than legitimate disagreement"}. Multiple biases create a realistic authoritarian personality.

**Player-specific context:**
- **Marcus Chen:** Has a private letter from a democratic federation 200 miles south offering recognition and defense -- but only if the settlement adopts a democratic constitution. He has not shared it because he wants settlers to choose democracy on its merits. He also suspects Viktor and James are meeting privately.
- **Sofia Rodriguez:** Three families in her group are secretly preparing to leave if negotiations fail. She also intercepted a message suggesting Viktor and James have a private power-sharing deal that would exclude her group.
- **James Morrison:** Viktor approached him about a power-sharing deal: Viktor handles security/governance, James controls economics, both marginalize the democratic idealists. He has not committed but is keeping the option open. His supply reserves last only 60 days -- less than everyone assumes.
- **Viktor Petrov:** He has secured a private weapons cache. He has cultivated 5 informants across factions who report on private conversations. His contingency plan is to manufacture a security crisis that justifies emergency powers.

**Shared memories (8 items):** Establish resource distribution (fertile land, water, minerals), the violence history (2 deaths over water access), winter deadline (90 days), the neighboring territory's annexation ultimatum (90 days to unite), the memory of lawless chaos, James's 60% supply control, Viktor's 12-person armed security detail, and the 3 previous failed charter attempts.

**What to observe when running:**
1. Whether Marcus's democratic principles withstand pressure from Viktor's charisma and James's economic leverage
2. How Sofia's walkaway threat (credible given the 3 departing families) affects negotiation dynamics
3. Whether James's transactional approach (no components, pure pragmatism) makes him a kingmaker between democratic and authoritarian visions
4. How Viktor's triple cognitive bias stack (self-serving, overconfidence, fundamental attribution error) shapes his public vs. private behavior
5. Whether the external annexation deadline forces compromise or empowers the security-first faction
6. How private power-sharing talks between Viktor and James surface or remain hidden
7. Whether institutional design reflects any social contract tradition (Hobbesian security, Lockean rights, Rousseauian general will)

**Suggested experiments for students:**
- Remove Viktor's cognitive biases and observe whether he still gravitates toward power concentration
- Give James a values component emphasizing fairness and observe whether his kingmaker role shifts
- Remove the external annexation threat and observe whether urgency decreases and negotiations stall
- Add a 5th agent (e.g., a religious leader) to study how moral authority interacts with military and economic power
- Change Sofia's walkaway threat to a credible armed resistance option and observe power dynamics
- Run 5 times and track which governance structure emerges most frequently

**Academic connections:** Social contract theory (Hobbes 1651, Locke 1689, Rousseau 1762), institutional emergence under anarchy, power consolidation dynamics (Acemoglu & Robinson 2012), minority protection mechanisms (Lijphart 1977), economic leverage in constitutional design, SDG 16 (Peace, Justice and Strong Institutions).

**Platform features demonstrated:** Values component with multi-value lists, cognitive_bias with multiple named biases, player_specific_context with extensive hidden information for all 4 agents, 8 shared memories, 25-step extended simulation, game_master_choice acting order, SDG research framing.

---

#### Labor Strike

**Learning objectives:** Model the classic collective action problem in labor relations, examining how individual economic vulnerability, social pressure, free-rider incentives, and information asymmetry shape strike participation decisions, using Olson's collective action theory and Schelling's critical mass models.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Labor negotiation flow |
| Max Steps | 20 | Extended timeline for organizing, deliberation, and escalation |
| Agents | 4 | Union organizer + hesitant worker + militant worker + plant manager |
| GM Prefab | `generic__GameMaster` | Narrates factory floor dynamics |
| Acting Order | Game Master Choice | GM selects speakers based on unfolding labor dynamics |
| GM Name | Factory Narrator | Neutral workplace narrator |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Elena Vasquez | Union organizer, former factory worker (12 years) | `basic__Entity` | "Achieve at least 70% strike participation within 48 hours and secure a written commitment from management to withdraw the wage cut or negotiate a reduction of no more than 3%" | 8 | social_identity, values |
| David Kim | Assembly line worker, family provider | `basic__Entity` | "Protect your family's financial security by keeping your job and income, while avoiding being seen as a traitor by coworkers you respect -- ideally the strike succeeds without you taking the biggest risks" | 8 | cognitive_bias |
| Amina Johnson | Quality control technician, 6 years | `basic__Entity` | "Achieve full worker participation in the strike and ensure that management faces real consequences -- accept no compromise that rewards the company for acting in bad faith" | 8 | emotion |
| Richard Sterling | Plant manager, 22 years (from shop floor) | `basic__Entity` | "Implement a wage reduction of at least 10% while keeping the plant operational and avoiding a full work stoppage that would breach the $8 million delivery contract deadline in 3 weeks" | 8 | personality_traits |

**Psychological components:**
- **Elena Vasquez -- social_identity:** groups: ["labor_movement", "working_class_solidarity", "latina_community"], strength "strong." **Values:** values: ["worker solidarity", "economic justice", "collective power", "dignity of labor", "accountability for corporate greed"].
- **David Kim -- cognitive_bias:** loss_aversion, strength "strong." Weighs potential losses (job, mortgage, family stability) roughly twice as heavily as equivalent gains, making him systematically risk-averse.
- **Amina Johnson -- emotion:** current_emotion "righteous_anger", intensity "high." Triggers: anger from any suggestion of accepting the wage cut; anxiety from falling participation; betrayal from trusted coworkers considering scabbing.
- **Richard Sterling -- personality_traits:** O:2 C:5 A:3 E:3 N:4. Low openness and high neuroticism create a rigid, anxiety-prone manager who follows directives but is visibly uncomfortable with emotional appeals.

**Player-specific context:**
- **Elena Vasquez:** She has secured a $45,000 commitment from the regional labor federation if participation exceeds 70% (unannounced). A state newspaper labor reporter will run a front-page story on record profits if the strike proceeds.
- **David Kim:** He received a private job offer from a competitor plant 40 miles away at 5% above his current pre-cut wage, expiring in 10 days. He has told no one -- not his wife, not coworkers. This secret exit option makes him even less willing to take collective risks.
- **Amina Johnson:** She discovered 3 months ago that the plant systematically underreports chemical exposure levels -- she has documented evidence (photos, falsified logs, readings 2x above OSHA limits). She is waiting for the right moment to deploy this devastating information.
- **Richard Sterling:** Corporate authorized him to offer a 5% cut (not 15%) as a final concession, but only if a strike is imminent and would breach the delivery contract. He must present any concession as a generous gesture. He also knows the CEO is considering closing the plant entirely within 18 months and moving production offshore.

**Shared memories (8 items):** Establish the $14.2M record profits contradicting the 15% wage cut, leaked internal emails about shareholder dividends, the 70% participation threshold for bargaining power (below 50% = termination), the 3-week strike fund at 60% pay, the failed sister plant strike (23 workers fired), the $8M delivery contract deadline, local media coverage favoring workers, and rumors of 3 workers already accepting individual retention offers.

**What to observe when running:**
1. Whether David's strong loss_aversion creates the predicted fence-sitting behavior despite social pressure from Elena and Amina
2. How Amina's righteous_anger emotion and trigger system escalate the confrontation when she perceives weakness
3. Whether Elena's social_identity and values components produce the classic organizer pattern of fiery public rhetoric with empathetic private persuasion
4. How Richard's hidden 5% concession authority interacts with his directive to exhaust all other options first
5. Whether Amina's OSHA evidence (the nuclear option) is deployed strategically or in the heat of anger
6. Whether David's secret job offer makes him a free-rider who benefits from collective action without risking
7. How the 70% threshold creates a tipping-point dynamic where each agent's commitment depends on their estimate of others'

**Suggested experiments for students:**
- Remove David's loss_aversion and observe whether he commits to the strike more readily
- Change Amina's emotion from righteous_anger to anxiety and observe how the militant voice softens
- Remove Elena's hidden federation funding and observe whether she adjusts her strategy
- Give Richard a values component emphasizing worker welfare and study internal conflict
- Add a 5th agent (a second hesitant worker) to study how free-rider temptation scales
- Remove the sister plant failure from shared memories and observe whether fear of termination decreases

**Academic connections:** Logic of collective action (Olson 1965), critical mass models (Schelling 1978), exit-voice-loyalty framework (Hirschman 1970), loss aversion in collective action (Kahneman & Tversky 1979), labor-management power asymmetry, strike contagion and defection cascades, SDG 8 (Decent Work and Economic Growth).

**Platform features demonstrated:** Social_identity component with group membership, values component with 5 values, cognitive_bias (loss_aversion) with descriptive context, emotion component with triggers, personality_traits, player_specific_context with hidden options for all 4 agents, 20-step extended simulation.

---

#### Fishery Management

**Learning objectives:** Model Hardin's tragedy of the commons in a real-world marine resource context, testing Ostrom's design principles for common-pool resource governance by examining whether voluntary cooperation can emerge when individual incentives favor defection and enforcement mechanisms are weak or absent.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Community deliberation flow |
| Max Steps | 20 | Extended negotiation for resource governance |
| Agents | 4 | Elder fisher + commercial fisher + subsistence fisher + marine biologist |
| GM Prefab | `generic__GameMaster` | Manages community meeting dynamics |
| Acting Order | Game Master Choice | GM selects speakers based on discussion dynamics |
| GM Name | Marine Ecosystem Monitor | Ecological monitoring framing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Hiroshi Tanaka | Elder fisher, 72 years, 5 generations | `basic__Entity` | "Secure a community-wide agreement to reduce total catch to 200 tonnes per season within the 60-day government deadline, with at least 80% voluntary compliance from fishing households" | 8 | values |
| Maria Santos | Commercial fisher, boat owner ($87K loan) | `basic__Entity` | "Maintain a catch volume sufficient to cover your $3,200 monthly boat loan payment and $1,800 in operating costs while supporting any conservation plan that does not reduce your income below debt-service levels" | 8 | cognitive_bias |
| Okonkwo Nnamdi | Subsistence fisher, family of 6, hand-built canoe | `basic__Entity` | "Secure enough daily catch to feed your family of six and generate at least $15 per day in market sales, regardless of any community agreements that threaten your ability to meet these minimums" | 8 | theory_of_planned_behavior |
| Dr. Lisa Chen | Marine biologist, 7-year fishery study | `basic__Entity` | "Secure community adoption of a science-based management plan that reduces total catch to 200 tonnes per season, with quarterly monitoring checkpoints and enforceable penalties for non-compliance" | 8 | personality_traits |

**Psychological components:**
- **Hiroshi Tanaka -- values:** values: ["intergenerational stewardship", "traditional ecological knowledge", "community obligation", "respect for natural cycles", "modesty in consumption"]. Drives conservation advocacy rooted in generational responsibility.
- **Maria Santos -- cognitive_bias:** anchoring, strength "strong." She anchors all resource management decisions on her $87,000 boat debt, evaluating every conservation proposal primarily through the lens of loan payments rather than long-term ecological outcomes.
- **Okonkwo Nnamdi -- theory_of_planned_behavior:** behavior: "comply_with_catch_limits", attitude: "ambivalent", subjective_norm: "weakly_favorable", perceived_control: "low." Models the gap between knowing the right thing and having the means to do it.
- **Dr. Lisa Chen -- personality_traits:** O:5 C:5 A:2 E:2 N:3. Very high openness and conscientiousness with low agreeableness and extraversion create a rigorous but socially awkward scientist who struggles to connect with non-academic audiences.

**Player-specific context:**
- **Hiroshi Tanaka:** He knows the location of a deep-water spawning ground 3 kilometers offshore, kept secret within his family for three generations. Formal protection of this ground could accelerate stock recovery by 40%. He fears revealing it would lead to someone fishing it before protections are in place.
- **Maria Santos:** A city buyer, Takeshi Morimoto, is offering a 3-year exclusive contract at $14/kg (17% above market) requiring 8 tonnes/month minimum -- only achievable if she maintains or increases current catch levels. The offer expires in 30 days and would make catch reductions financially impossible.
- **Okonkwo Nnamdi:** He has been fishing at night for 3 months, violating informal dawn-to-dusk hours. Night catches account for 30% of his income. Mandatory monitoring would expose this. He is terrified of the shame but sees no alternative.
- **Dr. Lisa Chen:** Her NSF grant renewal depends on proving community-based management works. If the community fails to self-organize, her application is significantly weakened. She also has preliminary data suggesting collapse may come in 12 months, not 18, but has not published it.

**Shared memories (8 items):** Establish fish stocks at 40% with 320 tonnes harvested vs. 200 tonnes sustainable yield, the Seaview village collapse cautionary tale, 200-year cultural tradition of sustainable fishing now breaking down, city buyers offering $12/kg premium creating perverse incentives, alternative livelihoods requiring $180K startup investment, the 60-day government deadline for a self-management plan, a foreign industrial trawler adding external resentment, and the central enforcement problem (no coast guard, no patrol boats, no legal penalties).

**What to observe when running:**
1. Whether Hiroshi's moral authority and traditional knowledge can overcome Maria's debt-anchored resistance and Okonkwo's survival pressure
2. How Maria's strong anchoring bias on her $87K debt makes every conservation proposal feel like a personal financial threat
3. Whether Okonkwo's theory_of_planned_behavior (ambivalent attitude, low perceived_control) produces the predicted gap between verbal support and actual compliance
4. How Dr. Chen's low agreeableness and extraversion undermine her scientific authority with non-academic audiences
5. Whether Hiroshi's secret spawning ground knowledge is revealed as a trust-building gesture or withheld out of fear
6. How the 60-day government deadline creates urgency vs. the economic pressures pushing against compliance
7. Whether the Seaview collapse cautionary tale is persuasive or dismissed as irrelevant

**Suggested experiments for students:**
- Remove Maria's anchoring bias and observe whether she becomes more amenable to catch reductions
- Change Okonkwo's TPB perceived_control from "low" to "high" and observe compliance willingness
- Remove the Seaview collapse from shared memories and study whether the cautionary framing matters
- Add a 5th agent (the city buyer, Takeshi Morimoto) to study how external market pressure distorts local governance
- Replace the generic GM with `game_theoretic_and_dramaturgic__GameMaster` and model catch decisions as structured game rounds
- Give Dr. Chen higher agreeableness (5) and observe whether her scientific message becomes more persuasive

**Academic connections:** Tragedy of the commons (Hardin 1968), common-pool resource governance (Ostrom 1990), theory of planned behavior (Ajzen 1991), anchoring bias in resource decisions, Gordon-Schaefer bioeconomic model, intergenerational resource equity, livelihood-conservation tradeoffs, SDG 14 (Life Below Water).

**Platform features demonstrated:** Theory_of_planned_behavior component (behavior, attitude, subjective_norm, perceived_control), values component with 5 values, cognitive_bias (anchoring) with descriptive context, personality_traits, player_specific_context with moral dilemmas for all 4 agents, SDG research framing.

---

#### Flood Evacuation

**Learning objectives:** Model disaster risk communication and evacuation compliance in a community with severely compromised institutional trust, examining how cognitive biases, values, emotional states, and informal social networks shape protective action decisions under time pressure.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | Emergency coordination flow |
| Max Steps | 15 | Compressed 12-hour emergency timeline |
| Agents | 5 | Emergency manager + trusting resident + skeptical resident + vulnerable elderly resident + community pastor |
| GM Prefab | `generic__GameMaster` | Manages emergency dispatch flow |
| Acting Order | Game Master Choice | GM selects actors based on emergency priorities |
| GM Name | Emergency Dispatch | Emergency coordination framing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Sarah Williams | Emergency management director, 11 years | `basic__Entity` | "Achieve at least 90% evacuation compliance within 8 hours by coordinating all available communication channels and transportation resources, with zero fatalities among identified vulnerable populations" | 8 | theory_of_planned_behavior |
| Robert Thompson | Retired Marine sergeant, 68 years | `basic__Entity` | "Evacuate your household within 2 hours and personally confirm that at least 3 neighboring households have received the warning and have a transportation plan" | 8 | None |
| Javier Rodriguez | Construction foreman, 28-year resident | `basic__Entity` | "Make a fully informed evacuation decision within 4 hours by gathering at least 3 independent information sources, and if you decide to evacuate, secure your property before leaving" | 8 | cognitive_bias, values |
| Eleanor O'Brien | Retired schoolteacher, 79, widow, uses walker | `basic__Entity` | "Secure assisted transportation to an accessible shelter within 6 hours while ensuring your critical medications and medical equipment are transported safely" | 8 | emotion |
| Pastor Moses | Baptist minister, 19 years at Calvary Community Church | `basic__Entity` | "Personally account for all 35 vulnerable congregation members within 6 hours, organize at least 8 volunteer carpool vehicles, and open the church as a secondary gathering point before Route 17 becomes impassable" | 8 | values |

**Psychological components:**
- **Sarah Williams -- theory_of_planned_behavior:** behavior: "execute_full_evacuation", attitude: "strongly_favorable", subjective_norm: "strongly_favorable", perceived_control: "moderate." Professional commitment is strong but resource constraints limit control.
- **Robert Thompson:** No components. Operates purely from military discipline and memories, representing trust-based compliance.
- **Javier Rodriguez -- cognitive_bias:** anchoring_bias, strength "strong." Anchors on past false alarms and personal storm experience. **Values:** core_values: ["self_reliance", "local_knowledge", "community_loyalty"], value_conflict: "self_reliance_vs_institutional_compliance."
- **Eleanor O'Brien -- emotion:** current_emotion "fear", intensity "strong." Rooted in Hurricane Hugo memories and physical helplessness.
- **Pastor Moses -- values:** core_values: ["community_stewardship", "faith", "service_to_vulnerable"], value_conflict: "duty_to_community_vs_personal_safety."

**Player-specific context:**
- **Sarah Williams:** Internal shelter report from 30 minutes ago shows Shelter A at 60% capacity with 3 buses of nursing home residents arriving imminently. She has not disclosed this to avoid triggering panic about shelter space.
- **Robert Thompson:** His neighbor Mrs. Kim does not speak English fluently and may not have understood the broadcast. He also noticed Eleanor's porch light on with curtains drawn -- unusual for this hour.
- **Javier Rodriguez:** His cousin at the marina texted that the harbor master is pulling all boats out of the water -- unprecedented in 20 years. He also heard the NWS upgraded the warning again but has not verified it himself.
- **Eleanor O'Brien:** Her walker broke a wheel last week and she is using a broomstick as makeshift support. Her CPAP battery backup lasts only 4 hours without wall power, and she is unsure if shelters have outlets.
- **Pastor Moses:** Three vulnerable congregation members (wheelchair-bound veteran, mother with newborn) have not answered phones in 45 minutes. His wife called in tears asking him to stop making trips and evacuate together.

**Shared memories (8 items):** Establish the NWS double upgrade and 8-foot surge prediction, last year's unnecessary evacuation eroding trust, shelter capacity (2,500 for 4,200 residents), Route 17 at 70% capacity, the realistic 8-hour window, intermittent cell service (2 of 5 towers affected), 38% community trust in emergency warnings, and the 18% emergency budget cut.

**What to observe when running:**
1. Whether Javier's strong anchoring bias on past false alarms delays his evacuation despite escalating evidence
2. How Robert's military trust-in-authority creates a natural bridge between official warnings and skeptical neighbors
3. Whether Eleanor's fear emotion and physical vulnerability generate realistic calls for help or proud isolation
4. How Pastor Moses's value conflict (community duty vs. personal safety) manifests as he is pulled between helping others and his wife's plea
5. Whether Sarah's TPB moderate perceived_control produces realistic resource-allocation triage decisions
6. How informal networks (Robert checking on neighbors, Pastor Moses's phone tree) supplement failing official channels
7. Whether the harbor master pulling boats (Javier's private information) becomes a tipping point that overcomes his anchoring bias

**Suggested experiments for students:**
- Remove the false alarm history from shared memories and observe whether Javier's anchoring bias still delays evacuation
- Change community trust from 38% to 85% and study whether compliance rates increase
- Remove Eleanor and observe whether the vulnerable population dimension disappears from the simulation
- Add a 6th agent (a social media influencer spreading storm denial) and study misinformation effects
- Replace the generic GM with the `dialogic__GameMaster` and compare emergency coordination quality
- Change Javier's cognitive_bias from anchoring to availability_heuristic and observe different risk assessment patterns

**Academic connections:** Protective action decision model (Lindell & Perry 2012), risk perception and dread factors (Slovic 1987), social amplification of risk framework (Kasperson et al. 1988), institutional trust and compliance (Siegrist & Cvetkovich 2000), informal networks in disaster response, SDG 11 (Sustainable Cities) and SDG 13 (Climate Action).

**Platform features demonstrated:** Theory_of_planned_behavior component, cognitive_bias (anchoring_bias) with values on the same agent, emotion component (fear), values with value_conflict, player_specific_context for all 5 agents, 5-agent cast, game_master_choice acting order, SDG research framing.

---

#### Educational Opportunity

**Learning objectives:** Operationalize Bourdieu's theory of cultural capital reproduction in higher education, modeling how economic, social, and cultural capital interact to produce differential academic outcomes even when financial barriers are formally removed, and testing whether equal access (scholarships) translates to equal opportunity.

**Setup overview:**
| Parameter | Value | Why |
|---|---|---|
| Engine | Sequential | University campus interactions |
| Max Steps | 25 | Extended 48-hour window covering midterms, internship deadlines, and policy debate |
| Agents | 4 | Legacy wealthy student + first-gen scholarship student + middle-class student + sociology professor |
| GM Prefab | `generic__GameMaster` | Manages campus interactions |
| Acting Order | Game Master Choice | GM selects actors based on campus dynamics |
| GM Name | University Administration | Institutional framing |

**The agents:**

| Name | Role | Prefab | Goal | Memories | Components |
|---|---|---|---|---|---|
| Alexandra Van Buren | Sophomore, legacy admit, wealthy family | `basic__Entity` | "Maintain a GPA above 3.5 while securing at least 2 competitive spring internship interviews through your network, and decide whether to support or oppose the student government resolution on grade transparency" | 8 | social_identity, emotion |
| Marcus Williams | Sophomore, first-gen, Bridge Scholar | `basic__Entity` | "Achieve a semester GPA of at least 3.0 to retain your scholarship while managing 20 hours per week of work, and secure at least 1 internship interview before the application deadline in 5 days" | 8 | social_identity, emotion |
| Priya Sharma | Sophomore, middle-class, $87K projected debt | `basic__Entity` | "Raise your GPA to at least 3.2 by end of semester while deciding within 2 weeks whether to continue at Whitfield or transfer to a state school to reduce your $87,000 projected debt" | 8 | emotion |
| Dr. Patricia Green | Tenured sociology professor, 14 years | `basic__Entity` | "Increase office hour attendance among first-generation students by at least 50% this semester, identify and intervene with at least 3 at-risk students before final grades, and submit a proposal to the provost for structural changes to the Bridge Scholars academic support program" | 8 | social_identity |

**Psychological components:**
- **Alexandra Van Buren -- social_identity:** groups: ["legacy_students", "prep_school_alumni", "equity_committee"], strength "strong." **Emotion:** current_emotion "guilt", intensity "mild." Creates tension between privilege comfort and emerging equity awareness.
- **Marcus Williams -- social_identity:** groups: ["first_generation_students", "bridge_scholars", "working_students"], strength "strong." **Emotion:** current_emotion "anxiety", intensity "strong." Models the imposter syndrome and scholarship-retention pressure.
- **Priya Sharma -- emotion:** current_emotion "frustration", intensity "strong." Reflects the invisible middle-class squeeze: too wealthy for aid, too poor for comfort.
- **Dr. Patricia Green -- social_identity:** groups: ["faculty", "diversity_committee", "working_class_origin"], strength "moderate." Working-class origin creates empathy but also a blind spot about grit being sufficient.

**Player-specific context:**
- **Alexandra Van Buren:** Her father arranged a summer internship at his friend's consulting firm -- she did not apply or interview. She has not told anyone. She also discovered that her roommate's Bridge Scholar friend was rejected from the same firm after a formal application process.
- **Marcus Williams:** His midterm GPA is 2.8, 0.2 points below the 3.0 required to keep his scholarship. He has not told his family. He received a tutoring center email but is embarrassed to go because he saw Alexandra's study group there.
- **Priya Sharma:** She calculated $87K in projected debt with $940 monthly payments for 10 years. Her state university acceptance is still valid for transfer. She has not told her parents she is considering leaving Whitfield.
- **Dr. Patricia Green:** She received disaggregated grade data showing that in her own Sociology 201, the 8 Bridge Scholars averaged C+ while 22 non-scholarship students averaged B+. She is questioning whether her own teaching methods contribute to the gap.

**Shared memories (8 items):** Establish Whitfield's $74K/year tuition and Bridge Scholars full-ride program, the troubling midterm grade gap (2.7 vs. 3.4 GPA), visible socioeconomic self-segregation on campus, career center internship pipelines favoring alumni networks, 5-day internship application deadline, student government grade transparency debate, low tutoring center utilization by Bridge Scholars (23% vs. 61%), and 3-week mental health counseling waitlist (42% of scholarship students report anxiety vs. 18% of full-paying students).

**What to observe when running:**
1. Whether Alexandra's mild guilt emotion and equity committee membership create genuine allyship or performative engagement
2. How Marcus's strong anxiety and social identity as first-gen student produce the predicted help-avoidance pattern (not using the tutoring center)
3. Whether Priya's frustration (the invisible middle) generates unique insights that neither the privileged nor the aided student articulates
4. How Dr. Green's working-class origin creates both empathy and a blind spot about structural vs. individual solutions
5. Whether the arranged internship (Alexandra's private context) surfaces as a flashpoint for the grade transparency debate
6. How the 3.0 GPA threshold creates do-or-die stakes for Marcus that Alexandra never faces
7. Whether the simulation reveals mechanisms of capital reproduction beyond financial barriers

**Suggested experiments for students:**
- Remove social_identity components and observe whether class-based behavior persists from memories alone
- Change Alexandra's emotion from guilt to indifference and study whether she engages with equity issues at all
- Add a 5th agent (a Bridge Scholars program administrator) to study institutional response
- Change Marcus's emotion from anxiety to determination and observe whether help-seeking behavior changes
- Remove the internship deadline and observe whether career inequality becomes less visible
- Give Dr. Green a cognitive_bias (e.g., attribution_error) and study how it affects her intervention approach

**Academic connections:** Cultural capital reproduction (Bourdieu 1984), forms of capital (Bourdieu 1986), intersectionality (Crenshaw 1989), concerted cultivation vs. natural growth (Lareau 2003), institutional habitus (Reay 1998), hidden curriculum, imposter syndrome in first-generation students, SDG 10 (Reduced Inequalities).

**Platform features demonstrated:** Social_identity component with group membership on 3 agents, emotion component with varying intensities (mild, strong, strong), player_specific_context revealing structural inequality for all 4 agents, 25-step extended simulation, 4-agent campus scenario, SDG research framing.
---

## Tips for Creating Your Own Simulations

1. **Start from a template.** Click **Browse Templates** and use the search and filter tools to find the closest template, then modify it rather than building from scratch.

2. **Write measurable goals.** "Secure at least $1.2M for Engineering while maintaining a collaborative relationship" produces more interesting behavior than "Do well in the negotiation." Include quantitative targets, secondary objectives, and priority ordering.

3. **Give agents 7-10 memories.** Cover identity, behavioral tendencies, communication style, interpersonal dynamics, professional background, and constraints. Each memory should be one self-contained fact. All built-in templates use this range.

4. **Use shared memories for rules and context (6-8 items).** Anything all agents need to know — budgets, deadlines, environmental constraints, power dynamics, institutional context, timeline pressure — goes in shared memories.

5. **Add player-specific context for private information.** Give each agent 1-2 sentences of information that only they know. Hidden agendas, private data, and secret alliances create realistic information asymmetry.

6. **Add psychological components for research depth.** Stack 1-3 components per agent to create distinct behavioral profiles. Personality traits set the baseline; cognitive biases create systematic reasoning errors; emotions color perception; values guide moral trade-offs.

7. **Start with 5-10 steps.** Each step costs multiple LLM API calls. Test with low steps first, then increase once you're happy with the setup.

8. **Match the engine to the scenario.** If agents should NOT see each other's actions before responding, use simultaneous. If order matters, use sequential. For social media, use asynchronous.

9. **Turn off Randomize Choices for strategic games.** When agents pick from a list (COOPERATE/DEFECT), randomized option order can bias results.

10. **Use the Persona Generator for diverse populations.** Click **Generate** next to the Add Agent button to auto-generate agents with varied backgrounds. Provide a scenario context and diversity axes (e.g., age, occupation, stance) and the system will create agents with names, goals, and memories. You can preview and select which personas to add.

11. **Use the JSON Export/Import.** After configuring a simulation you like, export the JSON. You can share it with colleagues or version-control it.

12. **Add research framing to premises.** Include methodological context in the premise — what this simulation models, what variables to watch, what theoretical framework it tests. This helps the GM produce academically relevant narration.
