# Simulation Analyzer

LLM-powered analysis tool for Concordia simulation logs. Uses simulation metadata (agents, goals, components, memories) alongside the HTML log to produce analysis grounded in the simulation's design intent.

## Overview

The analyzer generates comprehensive reports covering:

- **Executive Summary** — Scenario, key events, goal attainment, emergent dynamics
- **Agent Effectiveness** — Per-agent goal achievement, behavioral consistency with configured components, interaction dynamics
- **Insights** — Decision-making patterns, psychological component effects, information dynamics, emergent social phenomena, game-theoretic outcomes (when applicable), grounded variable trajectories, nested simulation integration
- **Recommendations** — Re-run variations with specific hypotheses, design improvements, research extensions

Reports are context-aware: prompts adapt based on what data is available (game-theoretic scores, grounded variables, nested simulations, psychological components). When a simulation produces no step data, the analyzer generates a diagnostic report with setup review and concrete fixes instead of fabricating results.

## Usage

### Web UI (Recommended)

In the Results page, open the **Analysis** tab and click **Analyze**. The report renders in-browser with markdown formatting and can be downloaded.

### Web API

```
POST /api/simulations/analyze-simulation
Content-Type: application/json

{"log_filename": "20260503_200122_Agent_R_Agent_U_Peace_Negotiation.html"}
```

### CLI

```bash
# Analyze a simulation log (auto-generates output filename)
python backend/scripts/analyze_simulation.py logs/20260503_200122_simulation.html

# Specify custom output path
python backend/scripts/analyze_simulation.py logs/simulation.html reports/my_analysis.md
```

### Python API

```python
from backend.utils.simulation_analyzer import SimulationAnalyzer
from backend.services.llm_factory import create_llm_client

llm_client = create_llm_client(provider="openai", model="gpt-4o", api_key="sk-xxx")
analyzer = SimulationAnalyzer(llm_client)

analysis = analyzer.analyze_simulation(
    log_path="logs/simulation.html",
    metadata_path="logs/simulation.metadata.json"  # Optional — auto-resolved from log path
)

analyzer.save_report(analysis, "reports/analysis.md")
```

## How It Works

```
HTML Log + Metadata JSON
        │
        ├── Parse v2.4 structured log (ENTRIES/CONTENT_STORE in <script> tags)
        ├── Extract steps, agent actions, outcomes, nested simulations
        ├── Load metadata (agents, goals, components, grounded variables, game-theoretic data)
        │
        ├── Generate Executive Summary (scenario, events, goal attainment, emergent dynamics)
        ├── Analyze Agent Effectiveness (per-agent assessment with component consistency)
        ├── Generate Insights (adapted to available data: game theory, grounded vars, etc.)
        ├── Generate Recommendations (re-run variations, design improvements, research extensions)
        │
        └── Format Markdown Report
```

The analyzer adapts its prompts based on what data is present:
- **Psychological components configured** → Assesses whether cognitive biases, personality, emotions, and values manifested in behavior
- **Game-theoretic simulation** → Compares outcomes to Nash equilibrium and Pareto optimality
- **Grounded variables tracked** → Evaluates variable trajectories against simulation events
- **Nested simulations run** → Checks whether inner simulation findings influenced outer behavior
- **No step data** → Generates diagnostic report with setup review and troubleshooting steps

## Report Structure

### Executive Summary
- Scenario and stakes (premise, agent goals)
- Key events and turning points (with step numbers)
- Per-agent goal attainment assessment
- Emergent dynamics (alliances, betrayals, creative solutions, deadlocks)

### Agent Effectiveness
For each agent:
- **Design Intent** — Goal and configured components
- **Goal Achievement** — Specific assessment with evidence
- **Behavioral Consistency** — Did components (biases, personality, emotions, values) manifest?
- **Key Contributions** — Specific actions that shaped outcomes
- **Surprising Behavior** — Unexpected actions or creative solutions

Plus interaction dynamics: pairings, coalitions, conflicts, GM influence.

### Insights
Categories included based on available data:
1. Agent decision-making patterns
2. Psychological component effects
3. Information dynamics
4. Emergent social phenomena
5. Game-theoretic outcomes (if applicable)
6. Grounded variable trajectories (if applicable)
7. Nested simulation integration (if applicable)
8. Methodological observations

### Recommendations
1. **Re-run Variations** — Specific parameter changes with hypotheses and expected observations
2. **Design Improvements** — Agent configuration, scenario structure, missing elements
3. **Research Extensions** — Theoretical frameworks, research questions, data extraction approaches

## Configuration

The analyzer uses the same LLM providers as the simulation runner. Configure in `.env`:

```bash
# Any supported provider works for analysis
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
ANTHROPIC_API_KEY=sk-xxx
```

All 8 providers are supported: OpenAI, Azure OpenAI, DeepSeek, Anthropic, Gemini, GLM, Ollama Local, Ollama Remote.

## Anti-Fabrication Guardrails

Every LLM prompt includes explicit instructions to:
- Ground claims in specific log evidence with step citations
- State when information is missing or ambiguous rather than speculating
- Never fabricate dialogue, events, or outcomes not in the log
- Skip analysis categories that lack sufficient evidence
- Generate diagnostic reports (not fake results) when no step data exists

## Troubleshooting

**Empty or low-quality reports** — Try a more capable model. Analysis quality depends on LLM reasoning ability.

**LLM timeout errors** — Increase `LLM_TIMEOUT` in `.env` (default: 180s). Analysis prompts can be long.

**"Analysis failed" in UI** — Check terminal for `[Analyzer]` messages. Common causes: invalid API key, model not available, rate limiting.

**Checkpoint files** — Checkpoints can be analyzed too. The analytics endpoint resolves checkpoint filenames to find base metadata when available.
