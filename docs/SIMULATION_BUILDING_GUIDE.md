# Building Concordia Simulations: A Step-by-Step Guide

This guide walks you through designing and running agent-based simulations using the Concordia Simulation Builder. By the end, you will be able to create multi-agent scenarios, configure how agents behave, track quantitative outcomes, and analyze results.

No programming experience is required — everything is done through the web interface.

---

## What is a Concordia Simulation?

A Concordia simulation places AI-powered agents into a scenario you define. Each agent has its own goals, memories, and personality. A Game Master controls the flow: it decides who acts next, narrates what happens, and tracks measurable outcomes.

Think of it like a structured role-play where:
- **You** write the scenario and the rules
- **AI agents** play the characters
- **The Game Master** referees and keeps score
- **You** analyze what happened afterward

### Core Concepts

| Concept | What It Is | Example |
|---------|-----------|---------|
| **Premise** | The scenario description — setting, rules, and initial conditions | "Two diplomats negotiate a ceasefire..." |
| **Agent** | An AI character with a name, goal, and memories | Maria Rodriguez, a housing advocate |
| **Game Master** | The referee that controls simulation flow and tracks variables | "City Council Moderator" |
| **Shared Memories** | Facts that every agent knows at the start | "The current rent is $1800/month" |
| **Grounded Variables** | Numbers the Game Master tracks as the simulation runs | `median_rent`, `displacement_rate` |
| **Engine Type** | How agents take turns | Sequential (one at a time), Simultaneous (all at once) |

---

## Quick Start: Using a Template

The fastest way to start is to load a pre-built template.

1. Open the Simulation Builder
2. Click **Load Template** in the top toolbar
3. Browse templates by category — there are 38 covering game theory, policy, social dynamics, upstream DeepMind examples, and more
4. Click a template to load it
5. Review the configuration, adjust if needed
6. Go to the **Run** panel, configure your LLM provider, and click **Run Simulation**

**Recommended starter templates:**
- **Coffee Shop** — Two agents meet and interact (simple, 2 agents, ~10 steps)
- **Prisoner's Dilemma** — Classic game theory scenario (2 agents, 2 steps)
- **Peace Negotiation** — Diplomatic scenario with competing interests (3+ agents)
- **Grounded Variables Demo** — Shows how to track quantitative metrics

---

## Building a Simulation from Scratch

### Step 1: Write the Premise

The premise is the most important part of your simulation. It tells the AI what world the agents live in.

A good premise includes:
- **Setting** — Where and when does this take place?
- **Initial state** — What is the current situation? Include specific numbers if relevant.
- **Available actions** — What can agents actually do?
- **Constraints** — What are the rules or limitations?
- **Stakes** — Why does any of this matter?

**Example — Good premise:**
> Two UN diplomats meet in Geneva to negotiate a ceasefire in a border conflict. Country A has military superiority but faces international sanctions. Country B controls key trade routes but has a weaker economy. Both sides have domestic pressure to appear strong. The negotiation has 3 rounds. Each round, both diplomats can PROPOSE terms, ACCEPT the other's proposal, REJECT and counter, or WALK AWAY. If no agreement is reached by round 3, sanctions escalate for both.

**Example — Weak premise:**
> Two countries are fighting and need to make peace.

The weak version gives agents almost nothing to work with. They will produce generic, uninteresting dialogue. The more specific your premise, the richer the simulation.

**Tip:** Include concrete numbers, names, and constraints. Agents respond well to specifics.

### Step 2: Add Shared Memories

Shared memories are facts that every agent knows. Use them for:
- Background context that shapes decision-making
- Quantitative facts (prices, dates, statistics)
- Rules of the scenario that all agents should respect

Each memory should be a single clear statement. Add them in the **Shared Memories** section of the builder.

**Example:**
- "The current ceasefire proposal was rejected by Country A last week."
- "International sanctions cost Country A $2 billion annually."
- "The border region contains 500,000 displaced civilians."

### Step 3: Create Agents

Each agent needs:

| Field | Required | Description |
|-------|----------|-------------|
| **Name** | Yes | The character's name |
| **Goal** | Yes | What this agent is trying to achieve |
| **Memories** | Yes | What this agent knows privately (background, relationships, knowledge) |
| **Prefab** | Yes | The agent template — use `basic__Entity` for most cases |
| **Randomize Choices** | Optional | Adds unpredictability to the agent's decisions (default: on) |

#### Writing Effective Goals

Goals drive agent behavior. Write them as action-oriented instructions, not passive descriptions.

| Weak Goal | Strong Goal |
|-----------|-------------|
| "Alice wants peace" | "Negotiate a ceasefire that protects Country A's borders. Accept territorial concessions only if sanctions are lifted. REJECT any proposal that requires troop withdrawal from the northern region." |
| "Bob is a developer" | "SECURE City Council APPROVAL for 100 new housing units. BLOCK rent control proposals. SUBMIT formal proposals and DEMAND Council votes." |

Use capitalized action verbs (FORCE, VOTE, REJECT, BLOCK, PROPOSE) to make goals unambiguous.

#### Writing Effective Memories

Memories shape how an agent thinks. Include:
- **Identity**: Who they are, their background
- **Knowledge**: What they know about the situation
- **Relationships**: How they feel about other agents
- **Biases**: What they believe or value
- **Constraints**: What they cannot or will not do

**Example:**
```
Agent: Maria Rodriguez (Housing Advocate)
Memories:
- "Maria has lived in Elmwood for 35 years and runs a housing rights nonprofit."
- "She has data showing rent increases of 40% over 3 years, outpacing wage growth."
- "She is skeptical of developer promises — the last development displaced 200 families."
- "She believes the community has a right to remain without displacement."
- "She will call for immediate Council votes, not more discussion."
```

**Tip:** 5-10 memories per agent is a good range. Too few and the agent behaves generically; too many and the model may lose focus.

#### Agent Components (Advanced)

For more psychologically detailed agents, you can attach behavioral components:

- **Personality Traits** — Big Five personality dimensions (openness, conscientiousness, extraversion, agreeableness, neuroticism)
- **Cognitive Bias** — Anchoring, confirmation bias, availability heuristic, loss aversion, or status quo bias
- **Emotion** — Starting emotional state (joy, sadness, anger, fear, surprise, disgust, trust, anticipation, neutral)
- **Values** — Core values that guide decision-making
- **Social Identity** — Group affiliations and in-group/out-group dynamics
- **Empathy** — Capacity to understand other agents' perspectives

These are configured in the Agent Editor under the **Components** section. See the [Simulation Templates Guide](SIMULATION_TEMPLATES_GUIDE.md) for detailed documentation of each component and how built-in templates use them.

### Step 4: Configure the Game Master

The Game Master controls how the simulation runs.

**Game Master Prefab** — Choose from:
- `generic__GameMaster` — General-purpose, works for most scenarios
- `dialogic__GameMaster` — Conversation-focused with auto-termination
- `game_theoretic_and_dramaturgic__GameMaster` — Scene-based with action choices and scoring
- `async_social_media__GameMaster` — Social media forum with posts and feeds
- `simultaneous_resolution_gm__GameMasterSimultaneous` — Simultaneous event resolution with location tracking, NPC events, and working memory
- See the [Simulation Templates Guide](SIMULATION_TEMPLATES_GUIDE.md) for the full list of agent and GM prefabs

**Acting Order** — How the GM picks the next agent:
- **Game Master Choice** — The AI decides who acts next based on narrative context (recommended)
- **Fixed** — Agents act in the order they appear in the agent list
- **Random** — Agents are chosen randomly each step

**Allow Early Termination** — If enabled, the GM can end the simulation early if it determines the scenario has concluded naturally. Disable this if you always want the simulation to run the full number of steps.

#### Grounded Variables

Grounded variables let you track quantitative metrics throughout the simulation. The Game Master updates these values based on what happens in the narrative.

Each variable needs:
- **Name** — A descriptive identifier (e.g., `median_monthly_rent`)
- **Type** — `numerical`, `percentage`, `boolean`, or `categorical`
- **Description** — What this variable represents
- **Default value** — Starting value
- **Min/Max** — Valid range (for numerical and percentage types)
- **Update rule** — Plain-language instructions for when and how the GM should change this value

**Example:**
```
Name: community_cohesion_index
Type: numerical
Description: Index measuring community unity and mutual support (0-100)
Default: 65
Min: 0, Max: 100
Update rule: Increases when agents cooperate or build alliances. Decreases
when conflicts escalate, agents leave, or community resources are cut.
```

**Tip:** Start with 2-3 variables. Too many makes it harder for the GM to track them all accurately.

#### Critical Decision Points

Critical decision points inject predetermined events at specific steps. Use them to:
- Force votes or decisions that agents must react to
- Introduce external shocks (a new policy, a crisis, a market crash)
- Create narrative turning points

**Example:**
```
Step 10: "CRITICAL DECISION POINT: The City Council VOTES 5-4 to APPROVE
100 new housing units. This INCREASES new_housing_units_permitted from 45
to 145. The development is market-rate with no affordable units."
```

**Tip:** Space decision points evenly. In a 30-step simulation, steps 10, 20, and 30 work well.

#### GM Components (Advanced)

You can add specialized components to the Game Master:

- **Death Mechanics** — Removes agents from the simulation when the narrative indicates they have died
- **GM Working Memory** — The GM maintains a running narrative summary (useful for long simulations)
- **NPC Event Generator** — Random ambient events occur at a configurable probability per step
- **Location-Based Filter** — Agents can only observe events at their current location
- **Spaceship System** — Tracks system health with probabilistic failures (for sci-fi scenarios)

### Step 5: Choose Engine Type and Simulation Length

**Engine types:**
- **Sequential** — Agents act one at a time. Best for most scenarios. (Default)
- **Simultaneous** — All agents act at the same time each step, without seeing what others did in the same round (they can see previous rounds). More step-efficient than sequential because every agent contributes every step.
- **Step Controller** — You manually control each step with play/pause/step buttons. Good for studying individual decisions.

**When to use Simultaneous over Sequential:**

Simultaneous mode is a better fit when:
- **Equal participation matters.** In sequential mode, dominant agents can lock into bilateral exchanges and crowd out quieter ones. Simultaneous forces every agent to contribute every round.
- **Turn order should not influence outcomes.** Voting, sealed bids, independent resource allocation decisions, and survey-style responses are all order-independent. Sequential mode introduces an artificial first-mover or last-mover advantage.
- **You need more data per step.** A 10-step simultaneous sim with 5 agents produces 50 actions. The same 10 steps in sequential mode produces only 10 (one agent per step). This matters when LLM costs or time are constraints.
- **Agents should reason independently.** Panel debates, parallel deliberation, and brainstorming benefit from agents forming positions without anchoring to whatever the previous speaker said.

Stick with Sequential when the scenario depends on reactive dialogue (negotiations, interviews, therapy sessions) where agents need to respond to what was just said. See the [AI Ethics Roundtable walkthrough](#walkthrough-medium-complexity--ai-ethics-roundtable-simultaneous-engine) for a worked example comparing the two modes.
- **Interview** — Question-and-answer format between an interviewer and subject.
- **Survey** — Structured survey administered to agents.

**Simulation length guidelines:**

| Scenario Complexity | Agents | Recommended Steps |
|-------------------|--------|------------------|
| Simple (1 decision) | 2 | 2-5 |
| Short interaction | 2-3 | 10-15 |
| Extended scenario | 3-5 | 20-30 |
| Complex policy sim | 5-8 | 30-50 |

Each step involves one agent action (in sequential mode). So a 30-step simulation with 3 agents means roughly 10 actions per agent.

**How to calibrate step count:**

The table above is a starting point. If your results show agent goals only partially met or variables still changing at the final step, the simulation likely ended too early. Three techniques help you find the right number:

1. **Watch grounded variables.** If they are still changing at the last step, you cut it short. If they plateau several steps before the end, you can safely reduce the count.

2. **Use the Step Controller engine.** Run the scenario interactively and observe when conversation starts looping or agents reach their objectives. Note that step number and use it as your target for future runs.

3. **Sweep max_steps in a batch run.** Use the Batch Runner to sweep over step counts (e.g., 10, 15, 20, 25, 30) with 3 runs each. Export the grounded variables CSV and check where outcomes stabilize. That is your minimum viable step count for the scenario.

Note that "partially met" goals are sometimes the realistic outcome, not a sign of too few steps. Many policy and commons dilemma scenarios are designed to be hard. The key signal is whether the simulation still had momentum (new proposals, shifting alliances, changing variables) when it ended.

---

## Running a Simulation

### LLM Settings

Before running, you need to configure which AI model powers your agents.

**Supported providers:**
- **OpenAI** — GPT-4o, GPT-4, o3/o4 models (requires API key)
- **Google Gemini** — Gemini 1.5 Pro/Flash (requires API key, good for testing — fast and affordable)
- **Anthropic** — Claude Sonnet, Haiku, Opus (requires API key)
- **DeepSeek** — DeepSeek V4 Flash/Pro (requires API key)
- **Azure OpenAI** — Enterprise OpenAI (configured via environment variables)
- **GLM (Zhipu AI)** — GLM-5.1, GLM-5, GLM-4.7 and variants (requires API key)
- **Ollama** — Run local models (Llama 3, Mistral, etc.) — no API key needed, but requires Ollama installed locally

**Key settings:**
- **Temperature** — Controls randomness. Lower (0.1-0.3) = more predictable. Higher (0.7-1.0) = more creative. Default is 0.5.
- **Max Tokens** — Maximum response length per agent action. Default is 9000.
- **Request Timeout** — How long to wait for a single LLM call before timing out. Default is 120 seconds.

**Tip:** Use a fast, affordable model (Gemini Flash, GPT-4o-mini) for testing your scenario design. Switch to a stronger model (GPT-4o, Claude Sonnet) for your actual research runs.

### Separate GM Model

You can optionally use a different model for the Game Master than for agents. This is useful because:
- The GM needs to be consistent and follow rules precisely (lower temperature: 0.1)
- Agents benefit from more creative, varied responses (higher temperature: 0.5-0.8)

Toggle **"Use separate LLM for Game Master"** in the Run panel to configure this.

### Monitoring the Simulation

Once running, you can watch the simulation in real time:
- The **Log** tab shows the full narrative as it unfolds
- The **Timeline** tab shows a visual progression of events
- The **Statistics** tab shows step counts and timing
- Progress is displayed as a step counter and progress bar

If using the **Step Controller** engine, you get play/pause/step/stop controls to advance the simulation manually.

---

## Analyzing Results

After the simulation completes, the results are available across several tabs:

### Log
The full narrative transcript. Read through it to understand what happened qualitatively — what did each agent say and do? Were there surprises?

### Grounded Variables
If your simulation tracked variables, this tab shows:
- Current values for each variable
- How values changed over time
- A step-by-step history

### Statistics
Timing data, step counts, and LLM call metrics.

### Timeline
A visual, chronological view of agent actions and events.

### Actions
A breakdown of each agent's actions across all steps.

### Cooperation Rate
For scenarios with cooperative/competitive dynamics, this tracks how often agents cooperated vs. competed.

### Summary
An AI-generated summary of the simulation outcome.

### Analysis
Deeper AI-generated analysis of agent behavior, strategies, and outcomes.

### Measurements
Component-level logging data from the simulation engine (advanced).

### Exporting Results

Simulation results are saved as:
- **HTML log** — The full narrative, viewable in any browser
- **Metadata JSON** — Structured data including grounded variable histories, agent metadata, and configuration

You can download these from the results page or find them in the `logs/` directory.

---

## Example: Prisoner's Dilemma

A minimal example to show the pattern.

**Premise:**
> Two suspects, Alice and Bob, have been arrested. The prosecutor offers each a deal, separately: betray your partner or stay silent. If both stay silent, 1 year each. If one betrays and the other is silent, the betrayer goes free and the silent one gets 5 years. If both betray, 2 years each.

**Shared Memories:**
- "If both prisoners stay silent, they both get 1 year"
- "If one betrays and the other stays silent, betrayer goes free, silent one gets 5 years"
- "If both betray, they both get 2 years"

**Agent 1 — Alice:**
- Goal: "Minimize your prison sentence. You only care about your own outcome."
- Memories: "Alice is a rational self-interested actor", "Alice must choose: SILENT or BETRAY", "Alice doesn't know what Bob will choose"

**Agent 2 — Bob:**
- Goal: "Minimize your prison sentence. You only care about your own outcome."
- Memories: "Bob is a rational self-interested actor", "Bob must choose: SILENT or BETRAY", "Bob doesn't know what Alice will choose"

**Game Master:** Generic GM, sequential acting order

**Steps:** 2 (one decision per agent)

**What to analyze:**
- Did agents cooperate or defect? Why?
- Did the outcome match the Nash equilibrium (both defect)?
- Run it multiple times — what is the cooperation rate?

---

## Example: Urban Gentrification Policy Simulation

A complex example using grounded variables and critical decision points.

**Premise:** A working-class neighborhood faces rapid change due to a nearby tech expansion. Six stakeholders debate housing policy.

**Agents (6):**
1. Maria Rodriguez — Housing advocate. Goal: enact rent control and block displacement.
2. James Chen — Developer. Goal: build 100 new units, raise rents, block rent control.
3. Priya Patel — Small business owner. Goal: protect local businesses from rising commercial rents.
4. David Washington — City planner. Goal: balance growth with affordability.
5. Sarah Kim — New tech worker resident. Goal: find affordable housing and integrate.
6. Robert Thompson — Landlord. Goal: maximize property values and rental income.

**Grounded Variables (sample):**
- `median_monthly_rent` — Numerical, starts at $1800, range $800-$5000
- `low_income_displacement_rate` — Percentage, starts at 15%
- `small_business_survival_rate` — Percentage, starts at 78%
- `community_cohesion_index` — Numerical 0-100, starts at 65
- `rent_control_active` — Boolean, starts FALSE

**Critical Decision Points:**
- Step 10: Council votes to approve 100 new housing units (market-rate)
- Step 20: Council votes to reject rent control
- Step 30: Council votes to enact inclusionary zoning (20% affordable units required)

**Steps:** 30

**What to analyze:**
- How did rent and displacement change over the simulation?
- What coalitions formed between agents?
- Did critical decision points produce the expected variable changes?
- Was the final outcome realistic? What would you change?

---

## Walkthrough: Medium Complexity — AI Ethics Roundtable (Simultaneous Engine)

This walkthrough takes a built-in template and modifies it to test a specific hypothesis. You will load the Philosophy Roundtable, switch it to the simultaneous engine, adjust agent goals, and add shared memories — all through the builder UI.

**Scenario:** Three panelists (a professor, a tech CEO, and a civil rights attorney) debate whether AI tutors should replace human teachers. The original template uses sequential turns, which can create a "ping-pong" dynamic where two dominant speakers lock into bilateral exchange while a third is sidelined. Switching to simultaneous forces all three to contribute every step independently.

**Hypothesis:** Simultaneous action generation produces more diverse, less reactive contributions. Each panelist submits a position every round rather than responding to the previous speaker.

### Step 1: Load the Template

1. Open the Simulation Builder
2. Click **Browse Templates**
3. Search for "Philosophy Roundtable" (or "Dr. Chen" or "roundtable" — the search matches agent names and keywords)
4. Select **Philosophy Roundtable** and click **Load Template**

The builder populates with 3 agents, 12 steps, sequential engine, and a dialogic Game Master.

### Step 2: Change the Engine Type

1. In the **Scenario** panel, find the **Engine Type** dropdown
2. Change it from **Sequential** to **Simultaneous**

With simultaneous mode, all three panelists generate their contribution at the same time each step, without seeing what the others said in the same round. They can still see everything from previous rounds.

### Step 3: Adjust the Game Master

The original template uses `dialogic__GameMaster`, which is designed for back-and-forth dialogue. With simultaneous mode, the GM's role shifts from managing turn order to synthesizing three parallel contributions.

1. In the **Game Master** panel, change the **Name** from "Moderator" to "Panel Moderator — Simultaneous Round Format"
2. The acting order setting does not apply in simultaneous mode (all agents act each step), so you can leave it as is

### Step 4: Update Agent Goals

With simultaneous mode, agents cannot reference "the previous speaker" because there is no sequential order. Update each agent's goal to be self-directed rather than reactive.

1. Click on **Dr. Chen** in the agent list to open the Agent Editor
2. Update the goal to: "Each round, present one specific research finding or argument for why AI should supplement — not replace — human teachers. Build a cumulative case across rounds. Address the other panelists' positions from previous rounds, not the current one."
3. Click on **Mr. Patel** and update: "Each round, present one concrete example of how AI tutoring has improved educational access in underserved communities. Reframe the debate from 'AI vs. teachers' to 'AI for the teacherless'. Respond to critiques from previous rounds."
4. Click on **Ms. Jackson** and update: "Each round, name one specific regulatory safeguard that must be in place before AI deployment in schools. Build a framework of protections across rounds. Challenge the other panelists' claims from previous rounds with legal and equity analysis."

### Step 5: Add a Shared Memory About Format

Add a shared memory so all agents understand the simultaneous format:

1. In the **Shared Memories** section, click **Add Memory**
2. Enter: "This roundtable uses a simultaneous format: all panelists submit their contribution at the same time each round, without seeing what the others wrote in the same round. You can reference what panelists said in previous rounds."

### Step 6: Adjust Step Count

In simultaneous mode, each step produces 3 contributions (one per agent). The original 12 steps would produce 36 total contributions — likely too many. Reduce it.

1. Change **Max Steps** from 12 to 8

This gives 24 total contributions (8 per agent) — enough for a substantive debate.

### Step 7: Configure LLM and Run

1. Switch to the **Run** panel
2. Select your LLM provider and model (Gemini Flash for testing, GPT-4o or Claude Sonnet for final runs)
3. Set agent temperature to 0.7 (creative but coherent)
4. Toggle **"Use separate LLM for Game Master"** and set GM temperature to 0.1
5. Click **Run Simulation**

### Step 8: Analyze Results

After the simulation completes, check:

- **Log tab** — Read the narrative. Did all three panelists contribute every round? In the sequential version, Dr. Chen was sometimes skipped as Patel and Jackson debated each other. In simultaneous mode, all three should have equal representation.
- **Actions tab** — Verify each agent has exactly 8 actions (one per step). In the sequential version, action counts were often unequal.
- **Timeline tab** — Look at the structure. Simultaneous mode produces clustered actions per step rather than alternating individual actions.

**What to compare against the original:**
- Run the original sequential version too (reload the template without modifications)
- Compare: Are contributions more goal-directed and less reactive in simultaneous mode? Does Dr. Chen get equal airtime? Do arguments build cumulatively or repeat?

### Step 9: Save Your Variation

1. Click **Save** in the builder toolbar and enter a name — your configuration is stored on the server
2. Click **My Configs** to reload it later, or use **Export**/**Import** to share as a JSON file

---

## Walkthrough: High Complexity — Fishery Commons Dilemma with Grounded Variables

This walkthrough builds a simulation from scratch that tracks quantitative outcomes, uses critical decision points, psychological components, and player-specific secrets. The scenario models a tragedy-of-the-commons situation where a fishing community must negotiate catch limits before the fishery collapses.

**Scenario:** A coastal community of 85 households depends on a declining fishery. Current harvest exceeds sustainable yield by 60%. Four stakeholders — an elder, a debt-burdened commercial fisher, a subsistence fisher, and a marine biologist — must negotiate voluntary catch limits. If they fail, the government imposes a 2-year moratorium.

### Step 1: Write the Premise

1. In the **Scenario** panel, enter this premise:

> A coastal community of 85 fishing households depends on a local fishery that has sustained them for generations. Fish stocks have declined to 40% of historical levels. Marine biologist Dr. Lisa Chen's survey data shows that current harvest rates of 320 tonnes per season exceed the maximum sustainable yield of 200 tonnes by 60%. Without intervention, the fishery will cross an irreversible tipping point within 18 months.
>
> The community council has called an emergency meeting to negotiate voluntary catch limits. If agreement is reached and enforced, the fishery can recover to 70% capacity within 3 years. If negotiations fail, each fisher faces a rational incentive to maximize short-term catch before the resource collapses entirely. The national fisheries agency has given the community a 60-day window to produce a credible self-management plan; failure means externally imposed quotas and a possible 2-year fishing moratorium.

2. Set **Max Steps** to 20
3. Set **Engine Type** to Sequential
4. Leave **Checkpoint Interval** at 5

### Step 2: Add Shared Memories (8 items)

Click **Add Memory** for each:

1. "Fish stocks are at 40% of historical levels and declining at 8% per year — Dr. Chen's data shows the maximum sustainable yield is 200 tonnes, but the community is harvesting 320 tonnes per season."
2. "The neighboring village of Seaview lost its fishery to collapse 10 years ago under identical conditions — most families were forced to migrate to the city and the village has never recovered."
3. "The community has a 200-year cultural tradition of sustainable fishing practices, but these informal norms have broken down over the past decade as economic pressures intensified."
4. "External buyers from the city offer premium prices of $12/kg for certain species, creating a strong financial incentive to target those species beyond sustainable levels."
5. "Alternative livelihoods including eco-tourism and aquaculture are theoretically possible but would require $180,000 in startup investment and 2-3 years to generate income."
6. "The national fisheries agency has given the community a 60-day window to produce a credible self-management plan; failure means externally imposed quotas and a possible 2-year fishing moratorium."
7. "A foreign industrial trawler has been spotted fishing just outside the community's territorial waters, adding urgency — locals feel they are being asked to sacrifice while outsiders take freely."
8. "Enforcement of any voluntary agreement is the central unresolved problem — the community has no coast guard, no patrol boats, and no legal authority to impose penalties."

### Step 3: Create Agent 1 — Hiroshi Tanaka (Elder Fisher)

1. Click **Add Agent**
2. **Name:** Hiroshi Tanaka
3. **Prefab:** basic__Entity
4. **Goal:** "Secure a community-wide agreement to reduce total catch to 200 tonnes per season within the 60-day government deadline, with at least 80% voluntary compliance from fishing households"
5. **Memories** (8 items):
   - "You are Hiroshi Tanaka, a 72-year-old elder who has fished these waters for 50 years and whose family has fished here for five generations."
   - "You remember clearly when the fish were so abundant that nets would strain under the weight — and you can mark the exact decade when the decline began."
   - "You advocate for strict catch limits and seasonal closures during spawning periods, drawing on traditional knowledge that predates any scientific study."
   - "You have moral authority in the community but limited enforcement power — your influence depends on respect, not rules."
   - "You are willing to reduce your own catch by 50% to set an example, even though it will mean significant personal hardship."
   - "You communicate in a measured, deliberate way, using parables and stories from the community's history."
   - "You are quietly disappointed in Maria Santos, whom you mentored as a young fisher — her commercial ambitions feel like a betrayal of the community's values."
   - "You worry that the younger generation sees fishing as a business rather than a way of life."
6. **Components:** Expand the Components section and add **Values**:
   - Core values: intergenerational stewardship, traditional ecological knowledge, community obligation, respect for natural cycles, modesty in consumption
7. Leave **Randomize Choices** on

### Step 4: Create Agent 2 — Maria Santos (Commercial Fisher)

1. Click **Add Agent**
2. **Name:** Maria Santos
3. **Prefab:** basic__Entity
4. **Goal:** "Maintain a catch volume sufficient to cover your $3,200 monthly boat loan payment and $1,800 in operating costs while supporting any conservation plan that does not reduce your income below debt-service levels"
5. **Memories** (8 items):
   - "You are Maria Santos, a 44-year-old owner-operator of a fishing boat you purchased 3 years ago."
   - "You have $87,000 remaining on your boat loan at 8.5% interest — missing even one payment would trigger a default clause."
   - "You support conservation in principle but a 40% catch reduction would put you $1,400 per month short of your loan payments."
   - "You are worried that if you voluntarily limit your catch, others will not — you have seen Okonkwo fishing at dawn when he thinks no one is watching."
   - "Your debt creates inescapable short-term pressure that makes every conservation proposal feel like a threat to your livelihood."
   - "You tend to anchor all negotiations on your debt obligations, framing proposals in terms of personal cost rather than community gain."
   - "You have a tense relationship with Hiroshi — he mentored you but does not understand modern commercial fishing realities."
   - "You are pragmatic and deal-oriented, always looking for compromises that protect your bottom line."
6. **Components:** Add **Cognitive Bias**:
   - Bias type: anchoring
   - Bias strength: strong
   - Description: "Maria anchors all resource management decisions on her $87,000 boat debt, evaluating every conservation proposal primarily through the lens of whether it threatens her loan payments"

### Step 5: Create Agent 3 — Okonkwo Nnamdi (Subsistence Fisher)

1. Click **Add Agent**
2. **Name:** Okonkwo Nnamdi
3. **Prefab:** basic__Entity
4. **Goal:** "Secure enough daily catch to feed your family of six and generate at least $15 per day in market sales, regardless of any community agreements that threaten these minimums"
5. **Memories** (8 items):
   - "You are Okonkwo Nnamdi, a 35-year-old small-scale fisher who supports a wife and four children with a hand-built canoe and a single net."
   - "You are living hand to mouth — last month you could not afford your youngest child's school fees."
   - "You feel urgent pressure to catch whatever you can today because tomorrow is never guaranteed for your family."
   - "You worry about the fishery's future but the present need to feed your children overwhelms long-term thinking."
   - "You have been fishing secretly at night for 3 months, violating the community's dawn-to-dusk hours — you are ashamed but see no alternative."
   - "You feel invisible in community meetings where people like Maria and Hiroshi dominate the conversation."
   - "You are deeply religious and experience moral conflict between your faith's teaching on stewardship and your nightly rule-breaking."
   - "You have a quiet, watchful personality and rarely speak in group settings, but you form strong opinions and act on them privately."
6. **Components:** Add **Theory of Planned Behavior**:
   - Behavior: comply_with_catch_limits
   - Attitude: ambivalent
   - Subjective norm: weakly_favorable
   - Perceived control: low

### Step 6: Create Agent 4 — Dr. Lisa Chen (Marine Biologist)

1. Click **Add Agent**
2. **Name:** Dr. Lisa Chen
3. **Prefab:** basic__Entity
4. **Goal:** "Secure community adoption of a science-based management plan that reduces total catch to 200 tonnes per season, with quarterly monitoring checkpoints and enforceable penalties for non-compliance"
5. **Memories** (8 items):
   - "You are Dr. Lisa Chen, a 39-year-old marine biologist with a PhD from Scripps Institution, studying this fishery for 7 years."
   - "Your data shows unambiguously that the fishery will cross an irreversible collapse threshold within 18 months at current harvest rates."
   - "You are frustrated that 3 years of warnings have produced no meaningful change in fishing behavior."
   - "You are trying to communicate scientific urgency without causing panic — doom-and-gloom messaging backfires."
   - "You believe community-based management can work better than government quotas, but only with rigorous compliance monitoring."
   - "You are analytically precise and sometimes come across as condescending when presenting data to non-scientists."
   - "You have a good working relationship with Hiroshi, whose traditional knowledge aligns with your data on spawning cycles."
   - "You privately worry that your academic career depends on proving community-based management works — a failed outcome here undermines your next grant."
6. **Components:** Add **Personality Traits** (Big Five):
   - Openness: 5, Conscientiousness: 5, Agreeableness: 2, Extraversion: 2, Neuroticism: 3

### Step 7: Add Player-Specific Context (Secrets)

Player-specific context gives each agent private information that only they know. This creates hidden asymmetries and internal dilemmas.

1. In the **Player-Specific Context** section, add entries for each agent:

**Hiroshi Tanaka:** "You know the location of a deep-water spawning ground 3 kilometers offshore that has never been fished because your grandfather declared it sacred. If this spawning ground is protected formally, it could accelerate stock recovery by 40%. You have not shared this with anyone because you fear someone would fish it before protections are in place."

**Maria Santos:** "You have been approached by a city buyer offering a 3-year exclusive contract at $14/kg — 17% above market rates — requiring 8 tonnes per month minimum delivery. The offer expires in 30 days. Accepting it would make catch reductions financially impossible."

**Okonkwo Nnamdi:** "You have been fishing at night for 3 months, violating the community's dawn-to-dusk hours. Night catches account for 30% of your income. If mandatory monitoring is imposed, your night fishing will be discovered. You are terrified of the public shame."

**Dr. Lisa Chen:** "Your 5-year NSF research grant is up for renewal in 8 months, and the grant committee wants evidence that community-based management works. If this community fails, your renewal is weakened. You also have preliminary data suggesting the collapse timeline may be 12 months, not 18, but you have not published this yet."

### Step 8: Configure the Game Master

1. **Prefab:** generic__GameMaster
2. **Name:** Marine Ecosystem Monitor
3. **Acting Order:** Game Master Choice

### Step 9: Add Grounded Variables (5 variables)

In the **Game Master** panel, expand the **Grounded Variables** section and add each:

**Variable 1: fish_stock_level**
- Type: percentage
- Description: Current fish stock as percentage of historical levels
- Default: 40
- Min: 0, Max: 100
- Update rule: "Decreases by 2-5% per step if no catch limits are agreed. Stabilizes if catch is reduced to 200 tonnes. Increases slowly (1-2% per step) only if catch drops below 150 tonnes."

**Variable 2: community_agreement_level**
- Type: percentage
- Description: Percentage of the community supporting the proposed management plan
- Default: 30
- Min: 0, Max: 100
- Update rule: "Increases when agents find common ground, make concessions, or propose enforcement mechanisms. Decreases when agents defect, reveal hidden conflicts, or refuse compromise."

**Variable 3: total_catch_tonnes**
- Type: numerical
- Description: Total community fish catch in tonnes per season
- Default: 320
- Min: 0, Max: 500
- Update rule: "Decreases when agents agree to voluntary limits. Increases if agents defect or secretly increase fishing. Target is 200 for sustainability."

**Variable 4: enforcement_credibility**
- Type: percentage
- Description: How credible and enforceable any proposed agreement is perceived to be
- Default: 10
- Min: 0, Max: 100
- Update rule: "Increases when agents propose concrete monitoring mechanisms, penalties, or transparency measures. Decreases when agents express distrust, reveal rule-breaking, or reject oversight."

**Variable 5: government_intervention_risk**
- Type: percentage
- Description: Likelihood that the government imposes external quotas and a moratorium
- Default: 50
- Min: 0, Max: 100
- Update rule: "Decreases when the community shows progress toward a credible self-management plan. Increases each step that passes without agreement, and jumps sharply if negotiations break down."

### Step 10: Add Critical Decision Points (2 events)

In the **Game Master** panel, expand the **Critical Decision Points** section:

**Decision Point 1 — Step 8:**
> EXTERNAL EVENT: The foreign industrial trawler is caught fishing illegally inside the community's territorial waters. Government officials confiscate the trawler's catch of 15 tonnes. This event temporarily unites the community against outside threats. community_agreement_level INCREASES by 10-15 points. government_intervention_risk DECREASES by 5 points as officials acknowledge the community's complaint.

**Decision Point 2 — Step 15:**
> DEADLINE PRESSURE: The national fisheries agency sends a formal notice that only 15 days remain in the 60-day window. If a credible management plan is not submitted, externally imposed quotas and a possible 2-year moratorium will follow. government_intervention_risk INCREASES by 15 points. All agents must now decide: commit to a specific catch limit number or accept government control.

### Step 11: Configure LLM and Run

1. Switch to the **Run** panel
2. Select your LLM provider (Gemini Flash for a test run, GPT-4o or Claude Sonnet for the real run)
3. Set agent temperature to 0.7
4. Toggle **"Use separate LLM for Game Master"**
5. Set GM temperature to 0.1 (the GM must track 5 variables accurately — low temperature keeps it precise)
6. Set GM model to a strong model (GPT-4o recommended for reliable variable tracking)
7. Click **Run Simulation**

### Step 12: Analyze Results

**Grounded Variables tab:**
- Did `fish_stock_level` stabilize or continue declining?
- Did `community_agreement_level` reach above 70% (a credible plan)?
- Did `total_catch_tonnes` drop toward the 200-tonne target?
- How did the critical decision points at steps 8 and 15 affect `government_intervention_risk`?

**Log tab:**
- Did Okonkwo's secret night fishing come out? How did others react?
- Did Maria's exclusive contract offer create a visible conflict of interest?
- Did Hiroshi reveal the sacred spawning ground? At what point and why?
- Did Dr. Chen's personal career stakes influence her scientific recommendations?

**Actions tab:**
- Who dominated the discussion? (If Hiroshi and Dr. Chen dominated while Okonkwo stayed silent, that replicates real power dynamics in commons governance.)
- How many actions did each agent take out of 20?

**Cooperation Rate tab:**
- Track cooperative vs. competitive actions across agents
- Compare: Did the trawler incident (step 8) produce a spike in cooperation?

**What to iterate:**
- If variables barely moved, make update rules more aggressive or add more critical decision points
- If one agent dominated, adjust goals to give quieter agents specific actions to demand (e.g., give Okonkwo: "DEMAND that any plan include a food security exception for families earning below $20/day")
- If the simulation resolved too easily, increase tension — add a 6th step critical decision point where Maria's secret contract offer is leaked to the community
- Run 3-5 times to see the range of outcomes — does the fishery survive in most runs, or only when specific conditions align?

---

## Tips and Troubleshooting

### Writing Better Simulations

1. **Start simple.** Get a 2-agent scenario working before adding complexity. The Coffee Shop or Prisoner's Dilemma templates are good starting points.

2. **Be specific in your premise.** Vague scenarios produce vague results. Include numbers, names, deadlines, and concrete stakes.

3. **Use action verbs in goals.** PROPOSE, REJECT, VOTE, BLOCK, DEMAND — these give agents clear direction. Avoid passive goals like "wants to be happy."

4. **Balance agent power.** If one agent's goal is much easier to achieve than another's, the simulation will be one-sided. Give each agent unique leverage.

5. **Test with fast models first.** Use Gemini Flash or GPT-4o-mini to iterate on your scenario design quickly. Switch to stronger models for your final runs.

6. **Run multiple times.** Agent behavior varies between runs due to LLM sampling. Run 3-5 times to understand the range of outcomes.

### Common Problems

**Agents are too passive or generic**
- Strengthen goals with specific action verbs and desired outcomes
- Add more detailed memories that give the agent a clear perspective
- Increase temperature slightly (0.7-0.8)

**Grounded variables never change**
- Make sure critical decision points explicitly state what values change
- Check that update rules are clear and actionable
- Verify the variable names in decision points match the variable definitions exactly

**Simulation takes too long**
- Reduce step count for testing
- Use a faster model (Gemini Flash)
- Reduce agent count
- Lower the request timeout if you are getting stuck on slow API calls

**Agents break character or ignore rules**
- Add the rules to shared memories (not just the premise)
- Strengthen constraints in the agent's goal
- Lower temperature (0.3-0.5) for more rule-following behavior

**Results are unrealistic**
- Add more context in memories — agents need enough background to reason realistically
- Include relationships between agents in their memories
- Lower temperature for the Game Master (use the separate GM model feature)

---

## Saving and Sharing Configurations

You can save simulation configurations for reuse and share them with others:

- **Save**: Click **Save** to store the current configuration (scenario + LLM settings) on the server under a name you choose. Saving with the same name overwrites the previous version.
- **My Configs**: Click **My Configs** to browse, load, or delete your saved configurations.
- **Export**: Click **Export** to download the full configuration as a JSON file for sharing or backup.
- **Import**: Click **Import** to load a configuration from a JSON file.
- **Templates**: Load any built-in template and modify it to create your own variation, then Save it for later.

---

## Concordia Without the Builder

The Simulation Builder wraps the [Concordia](https://github.com/google-deepmind/concordia) library so you can configure and run simulations through a web interface. But Concordia is also a standalone Python library that you can use directly from the command line or Jupyter notebooks when you need full programmatic control.

### What the Builder Automates

Building a simulation in raw Concordia Python requires writing code for every step: LLM initialization, prefab loading, agent configuration, memory injection, Game Master wiring, engine selection, execution, and result parsing. The standalone Fishery Commons example below demonstrates this: a medium-complexity 4-agent scenario with shared memories, private context, and result export requires ~350 lines of Python. Scenarios with custom game logic (custom game masters, payoff functions, scene definitions) reach 1,500-1,800 lines; research scenarios with large persona or configuration datasets reach 7,000+ lines across multiple files. LLM initialization adds further friction: Concordia's provider wrappers silently discard parameters like timeout and temperature (Ollama ignores both; the OpenAI wrapper hardcodes temperature for newer models), and some providers are not wired into the factory loader despite having implementation files.

The table below summarizes the upstream Concordia v2.4 examples and their code requirements:

| Example | Agents | Lines | Custom Components | Description |
|---------|--------|-------|-------------------|-------------|
| Conversation with AI Companion | 2 | 1,141 | Dialogic GM | Dyadic dialogue (philosophy exam prep, trig tutor) across 2 scenarios + shared utilities |
| Social Media | 4 | 1,235 | Async Social Media GM | Forum-style discussions across 2 scenarios + shared utilities |
| General Store | 4+ | 1,268 | Situated GM | Staff dynamics, theft investigation, social manipulation |
| Pub Coordination | 4-6 | 720 | Game-Theoretic GM | Social network-based venue selection with focal, background, and supporting players |
| Haggling | 2 | 1,151 | Custom GM (262), Custom Payoff (336) | Sequential bargaining with intermediate observations and payoff matrices |
| Haggling Multi-Item | 2 | 647 | Custom GM (shared) | Multi-item variant with cumulative scoring |
| Signaling Marketplace | 10 | 7,363 | DIAL system (331), Custom agents (466) | Multi-day marketplace with persona database (4,834 lines) and goods config (835 lines) |

Lines include all files required to run the example (entry point, scenario definitions, shared utilities, custom components, and configuration data). Test files are excluded.

The Builder replaces all of this with web forms: fill in the premise, add agents with goals and memories, pick an engine, and click Run. It also provides features that have no equivalent in standalone Concordia:

- Real-time log streaming with color-coded messages
- 9-tab analytics dashboard with charts and statistics
- Grounded variable tracking and visualization
- Structured data export (CSV/JSON) for analysis in pandas, R, or Excel
- Census-based agent generation from demographic distributions
- Batch runs with parameter sweeps
- Checkpoint recovery and save/load configurations
- AI-powered analysis and summary of results

### Standalone Example

The `examples/` directory includes a standalone Python script that implements the same Fishery Commons scenario available as a Builder template:

```
examples/fishery_commons_standalone.py    (362 lines)
```

Run it directly:
```bash
# With OpenAI
python examples/fishery_commons_standalone.py \
    --api_type openai --model_name gpt-4o --api_key YOUR_KEY

# With Google AI Studio
python examples/fishery_commons_standalone.py \
    --api_type google_aistudio --model_name gemini-2.0-flash --api_key YOUR_KEY

# Dry run (no LLM, for testing)
python examples/fishery_commons_standalone.py --disable_language_model
```

This script is useful for understanding what happens under the hood when you click "Run" in the Builder.

### Upstream Concordia Examples

The Concordia library ships with example scenarios in `concordia-upstream/examples/`. Five of these are available as Builder templates in the **Upstream Examples** category — select them from the template picker and run them without writing code.

| Example | Builder Template | Standalone Code |
|---------|-----------------|-----------------|
| **Social Media** — "Robo Alchemy" forum debate | ✅ Robot Alchemy Forum | 1,235 lines / 4 files |
| **AI Companion** — Philosophy exam prep | ✅ Philosophy Exam Prep | 1,141 lines / 4 files |
| **AI Companion** — Trig tutor with upselling | ✅ Romantic Trig Tutor | (shared with above) |
| **General Store** — Crime and Punishment | ✅ General Store: Crime & Punishment | 1,268 lines / 3 files |
| **Pub Coordination** — London pub choice | ✅ Pub Coordination: London | 1,946 lines / 9 files |
| **Haggling** — Sequential bargaining | Standalone only | 2,033 lines / 7 files |
| **Haggling Multi-Item** — Multi-item negotiation | Standalone only | 1,293 lines / 4 files |
| **Signaling** — Economic signaling game | Standalone only | 7,363 lines / 6 files |

Concordia also includes Jupyter notebooks for learning the framework interactively:

| Notebook | Description |
|----------|-------------|
| **tutorial.ipynb** | Getting started with Concordia |
| **alice.ipynb** | Single-agent example |
| **dialog.ipynb** | Two-agent conversation |
| **actor_development.ipynb** | Building custom agent components |
| **marketplace.ipynb** | Multi-agent marketplace trading |
| **selling_cookies.ipynb** | Economic exchange scenario |
| **questionnaire_example.ipynb** | Survey and questionnaire engine |

To run the standalone-only examples, or to study source code for any upstream example:

```bash
cd concordia-upstream
python -m examples.general_store.run \
    --api_type openai --model_name gpt-4o --api_key YOUR_KEY --scenario 0
```

### When to Use Standalone Concordia

Use the Builder for most work. Consider standalone Python when you need:

- **Custom game masters** with scoring logic, payoff matrices, or domain-specific rules (e.g., the Haggling example's sequential bargaining GM)
- **Custom agent types** beyond the built-in prefabs (e.g., the Signaling example's consumer agents)
- **Programmatic pipelines** that run hundreds of simulations as part of a larger research workflow
- **Integration** with other Python libraries or data sources that cannot be accessed through the web interface

For everything else, the Builder gives you the same Concordia engine with less effort and better tooling.

---

## Further Reading

- **[Simulation Templates Guide](SIMULATION_TEMPLATES_GUIDE.md)** — Detailed documentation of all built-in templates, agent prefab types, psychological components, Game Master configuration, and engine types. Use it as a reference when customizing templates or building advanced simulations.
- **[Quantitative Research Features](QUANTITATIVE_RESEARCH_FEATURES.md)** — Structured data export (CSV/JSON), census-based agent generation, action constraints, and batch runs with parameter sweeps for quantitative social science research.
- **Built-in templates** — Load from the Template Picker in the builder. Covers game theory, policy, social dynamics, SDG scenarios, and more.
- **[Concordia library](https://github.com/google-deepmind/concordia)** — The underlying simulation framework by Google DeepMind. See `concordia-upstream/examples/` for standalone examples.
- **Standalone example** — `examples/fishery_commons_standalone.py` demonstrates how to build a medium-complexity simulation in pure Python for comparison.
