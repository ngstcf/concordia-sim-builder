# Concordia Compatibility Changelog

## Version 2.4.0 (Current - 2026-05-05)

Upgraded from gdm-concordia 2.1.0 to 2.4.0. Major platform expansion with new simulation engines, GM components, a redesigned frontend, and quantitative research features.

### Breaking Changes from v2.1.0
- Concordia v2.4 removed `concordia.utils.html` — replaced all `PythonObjectToHTMLConverter` calls with `SimulationLog.to_html()`
- `sim.play()` now returns a `SimulationLog` object instead of raw HTML
- v2.4 structured log format embeds `ENTRIES`/`CONTENT_STORE` JSON in `<script>` tags — analytics parser updated to handle both formats

### New Features

**Simulation Engines**
- Step Controller engine — play/pause/step/stop control over running simulations with 4 REST endpoints, SSE events, and toolbar UI
- Interactive step-by-step execution with per-step action log

**Game Master Components**
- Registry and factory for 5 contrib GM components: Death, GMWorkingMemory, NpcEventGenerator, LocationBasedFilter, SpaceshipSystem
- `GameMasterSimultaneous` prefab registered from contrib — simultaneous event resolution with location tracking, NPC events, working memory, and time-based pacing
- Picker UI in GM config panel
- Separate GM LLM provider — independent model selection for GM via UI toggle or .env fallback (`GM_LLM_PROVIDER`, `GM_LLM_MODEL`)

**Agent System**
- Formative memories endpoint with Generate Backstory button in agent editor
- Measurements injection for all engine types with Component Logs tab in results
- Nested simulation auto-triggers in pre_act with safeguards
- Agent drag-to-reorder, duplicate, prefab badges, component count display
- Player-specific context editor, persona generator, custom reasoning steps, emotional stance component
- `player_specific_memories` field — per-character memory lists passed to formative memories initializer alongside `player_specific_context`
- Grouped component dropdown by category in AgentEditor

**Builder UX**
- Save/Load configurations — named configs stored on server, "My Configs" panel with load/delete, overwrite-on-save support
- Export/Import JSON — full config including LLM settings, backward-compatible with legacy config-only files
- Scene editor and questionnaire builder visual editor components
- Searchable template picker with filtering, sorting, and tags
- Configurable checkpoint interval (1-100, default 5) with UI control
- Early termination toggle (`can_terminate_simulation` flag)
- Clock configuration in builder — supports `multi_interval`, `fixed_increment`, and `generative` clock modes from Concordia upstream
- Collapsible left sidebar with viewport-filling simulation log
- Request timeout configuration per simulation
- Removed redundant Advanced JSON Configuration panel (visual builders cover all GM parameters)

**Live Log Streaming**
- Real-time terminal output mirrored to frontend via SSE (`stdout` tee interceptor)
- Two log panels: Main Log (system + debug) and LLM Log (separate)
- Color-coded messages: observations (cyan), actions (emerald), warnings (yellow), watchdog (orange), analyzer (purple), progress (amber), completions (green), LLM (blue)
- Auto-scroll with scroll-lock toggle, 500-line buffer
- Gated by `DEBUG_ENABLED` and `LLM_LOGGING_ENABLED` env vars

**Results & Analytics**
- 9 result tabs: Simulation Log, Statistical Dashboard, Timeline, Grounded Variables, Cooperation, Actions & Observations, Summary, Analysis, Component Logs
- Markdown rendering (react-markdown + remark-gfm) in Analysis and Summary tabs
- Save Report download button for Analysis and Summary
- LLM provider, model, and duration metadata bar in results header
- Grounded variables parser rewritten for v2.4 ENTRIES JSON with `<details>` tag fallback
- Summary with agent overview table, participation imbalance detection, per-phase timeline
- Analysis prompts rewritten with full simulation metadata context, anti-fabrication guardrails
- Per-agent observation extraction from v2.4 `__observation__` entries with cyan-styled display in Actions & Observations tab
- AI Analysis prompts now receive observations, grounded variable definitions, and cooperation/game-theoretic data when available — conditional prompt sections adapt to each simulation's configuration

**Checkpoint System**
- Checkpoint metadata saved alongside every checkpoint (regular, watchdog, emergency) with agents, LLM info, premise
- Analytics endpoint resolves checkpoint filenames to base metadata
- Emergency checkpoint filenames now include scenario context (agent names + premise)
- `is_checkpoint` flag in analytics response

**LLM Providers**
- Ollama Remote provider (separate from Ollama Local, uses `OLLAMA_BASE_URL` and `OLLAMA_API_KEY`)
- Anthropic Opus 4.7+ temperature fix (extended thinking rejects temperature parameter)
- `llm_print()` added to Anthropic, Gemini, and GLM providers (respects `LLM_LOGGING_ENABLED`)
- OpenAI model list filtering: drops below GPT-4, preview, audio, transcribe, codex, image models
- GLM models updated to current lineup (GLM-5.1, GLM-5, GLM-4.7, etc.)
- DeepSeek models updated from deprecated deepseek-chat/coder to v4 models
- Default max tokens increased from 3500 to 9000
- LLM activity tracker and watchdog integration for call monitoring

**Simulation Management**
- Effective cancellation mid-run: step callbacks check `should_cancel` and raise `SimulationCancelled`
- LLM-level cancel interrupt — cancel flag checked before every LLM call via `TemperatureConfiguredModel`, reducing blind window from an entire step (~8-12 LLM calls) to a single call (~5-30s)
- Partial results saved on cancel (HTML log + metadata)
- Per-simulation delete endpoint (`DELETE /api/simulations/logs/{filename}`)
- Server shutdown endpoint and Kill Server button

**Codebase**
- Refactored `simulations.py` (6200 → 2100 lines): 38 templates extracted into `backend/api/templates/` package
- Templates registered via dynamic `router.add_api_route()`

**Quantitative Research Features**
- Structured data export (CSV/JSON) — export agent actions and grounded variable histories as tabular data from any simulation log; REST endpoints `GET /api/simulations/logs/{filename}/export-csv` and `GET /api/simulations/logs/{filename}/export-json`; Export CSV/JSON buttons in results header
- Census/distribution-based agent generation — generate agents from statistical distributions (independent marginals or joint profiles); CSV/JSON file upload; deterministic seeding; optional LLM enrichment; new "Census / Distribution" tab in persona generator modal; REST endpoints `POST /generate-personas-census`, `POST /parse-distribution`
- Structured action constraints — define available actions globally (name, description, condition) injected into premise as AVAILABLE ACTIONS section; per-agent action overrides injected as memories; new Available Actions editor in simulation builder
- Batch runs with parameter sweeps — run simulations N times with optional sweep over temperature/max_steps; SSE progress streaming; live progress bar and results table; batch metadata and per-run logs saved to `logs/`; aggregated CSV export; REST endpoints `POST /api/simulations/batch/execute`, `GET /api/simulations/batch/{id}/status`, `POST /api/simulations/batch/{id}/cancel`, `GET /api/simulations/batch/{id}/export-csv`
- Batch reliability (ICC3,1) — questionnaire/interviewer-style batches now compute reliability when applicable, show ICC in the frontend, and support reliability JSON export; non-applicable scenarios report explicit "ICC not applicable"
- Live batch run telemetry — batch stream now forwards per-run lifecycle and step progress (`run_start`, `run_status`, `run_progress`, `run_error`) and frontend shows current run step/ETA/parameters in real time
- New files: `backend/utils/data_exporter.py`, `backend/services/census_generator.py`, `backend/services/batch_runner.py`, `frontend/src/components/SimulationBuilder/AvailableActionsEditor.tsx`, `frontend/src/components/SimulationRunner/BatchRunner.tsx`
- New documentation: [Quantitative Research Features Guide](docs/QUANTITATIVE_RESEARCH_FEATURES.md)

**Template Expansion**
- Added Mastodon influence experiment template for social-media persuasion studies, including role-specific activity rates and support for malicious vs. counter-messaging behavior

### Bug Fixes
- Fixed grounded variables not updating during simulation — GM was not instructed to output variable changes, so the component's post_act extraction always returned empty. Injected tracking instructions into the premise (visible to the event resolution chain), added fast `[VARIABLES: k=v]` tag parsing before LLM fallback, and fixed history recording to capture post-update values
- Fixed checkpoint saves failing silently — local `import re` inside `run_simulation_stream` shadowed the module-level import, causing a `NameError` in the checkpoint callback closure
- Fixed off-by-one step numbering — Concordia's `checkpoint_counter` is 0-indexed; progress now correctly shows Step 1/N through N/N
- Fixed SSE progress stream dropping during long simulations — added 5-second keepalive heartbeats between steps to prevent idle connection timeouts
- Added automatic polling recovery when SSE stream disconnects — frontend detects the drop, shows a "Connection lost" banner, and polls `/status/{task_id}` every 5 seconds until results are available
- Completed simulations now retained in backend state (last 20) so the status endpoint returns results even after the SSE stream ends
- Added mount-time recovery — on page refresh or Vite HMR reload, frontend checks `/status` for running simulations and auto-reconnects with polling
- Fixed observation count showing 0 in Statistical Dashboard — v2.4 parser checked `entry_type` and `summary` fields but observations are stored under `__observation__` key in resolved `deduplicated_data.value` dicts
- Fixed step controller buttons (Play/Pause/Step/Stop) not updating UI state — API calls succeeded but frontend never updated `controllerState` from the response
- Fixed Step button giving no visual feedback — added "Stepping" state with pulsing indicator while waiting for LLM, and removed 120-char action text truncation in Step Log
- Fixed Stop button not actually ending the simulation — now calls `cancelSimulation()` in addition to stopping the step controller
- Fixed Kill Server button not killing all worker processes — replaced single-process `os.kill` with port-based `lsof`/`kill` to catch reloader + all workers
- Fixed duplicate messages in Live Logs — React StrictMode double-mount opened two SSE connections to `/logs/stream`; now closes existing connection before opening a new one
- Fixed batch streaming robustness on frontend — batch requests now use the configured API base URL, surface HTTP/body errors, and parse `data:` lines consistently
- Fixed batch backend event parsing — now correctly parses nested SSE from simulation runs so completion/error/log filename state is captured reliably

### Templates (38 total)

**Original (v2.1.0) — 20 templates across 5 categories:**

*Basic Templates:*
1. Coffee Shop Demo - Quick 5-step test
2. Peace Negotiation - Russia-Ukraine talks with UN mediator (20 steps)

*Prefab Type Examples:*
3. Planning Agent - Strategic product launch (`basic_with_plan__Entity`)
4. Scripted Entity - Focus group moderator (`basic_scripted__Entity`)
5. Context-Aware Moderator - Support group facilitator (`context_aware_scripted__Entity`)
6. Dialogic Conversation - Therapy session (`dialogic__GameMaster`)
7. Strategic Game - Prisoner's Dilemma (`game_theoretic__GameMaster`)
8. Marketplace - Farmers market trading
9. Interviewer - Employee survey (`interviewer__GameMaster`)
10. Formative Memories - High school reunion with LLM-generated backstories

*Research Studies:*
11. Vaccine Hesitancy Study - 5 agents with full psychological profiles
12. Phishing Attack Simulation - Nested simulations modeling attack chains
13. Urban Gentrification - 6 stakeholders with 11 grounded variables

*Advanced Features:*
14. Nested Simulation Demo - PhoneGameMaster pattern
15. Grounded Variables Demo - Numerical and categorical metric tracking

*SDG Scenarios:*
16. State Formation - SDG 16 (Peace & Justice)
17. Labor Strike - SDG 8 (Decent Work)
18. Fishery Management - SDG 14 (Life Below Water)
19. Flood Evacuation - SDG 11/13 (Cities & Climate)
20. Educational Opportunity - SDG 10 (Reduced Inequalities)

**Added in v2.4.0 (18 new templates):**

*General Scenarios:*
21. Rational Negotiators - Structured budget negotiation
22. Philosophy Roundtable - Structured argumentation (`conversational_debate`)
23. Social Media Discourse - Online policy debate
24. Puppet (Wizard-of-Oz) - Controlled customer service entity
25. Spaceship Crisis - Team crisis management
26. Sealed-Bid Auction - Economic mechanism design

*Advanced Scenarios:*
27. Hostage Negotiation - Step controller engine demo
28. Colony Survival - Contrib GM components demo
29. Bookstore Reunion - Formative memories demo
30. Clinical Trial Ethics Board - Measurements demo
31. Diplomatic Crisis - Nested simulation strategy demo
32. Music Career Crossroads - Career deliberation with financial planning

*Research:*
33. AI Policy Red Team - Devil's advocate policy stress-test

*Upstream Examples (adapted from Google DeepMind's Concordia):*
34. Robot Alchemy Forum - Async social media forum debate (4 agents)
35. Philosophy Exam Prep - Gen Z student + AI tutor dialogic conversation
36. Romantic Trig Tutor - AI math tutor with hidden upselling motive
37. General Store: Crime & Punishment - 7-agent simultaneous workplace drama with GameMasterSimultaneous
38. Pub Coordination: London - Game-theoretic pub choice with scenes

---

## Version 2.1.0 (Validated 2025-01-07)

### What Works
- ✅ All entity prefabs (basic, basic_with_plan, basic_scripted, minimal, etc.)
- ✅ All game master prefabs (generic, dialogic, game_theoretic, etc.)
- ✅ Custom LLM wrappers (OpenAI, DeepSeek, Gemini, Anthropic, GLM, Ollama)
- ✅ Template system with 20 templates across 5 categories
- ✅ Scripted entity prefab (`basic_scripted__Entity`)
- ✅ SSE streaming for simulation execution
- ✅ Analytics and recent simulations endpoints
- ✅ Grounded variables tracking with AI-powered post-processing
- ✅ Checkpoint management for long-running simulations
- ✅ Watchdog monitoring with configurable timeouts
- ✅ Dashboard visualizations (Timeline, Statistical Dashboard, Natural Language Summary)
- ✅ Cooperation rate chart and grounded variables chart
- ✅ Responsive UI design for all screen sizes

### Template List (20 templates across 5 categories)

*Basic Templates:*
1. Coffee Shop Demo - Quick 5-step test
2. Peace Negotiation - Russia-Ukraine talks with UN mediator (20 steps)

*Prefab Type Examples:*
3. Planning Agent - Strategic product launch (`basic_with_plan__Entity`)
4. Scripted Entity - Focus group moderator (`basic_scripted__Entity`)
5. Context-Aware Moderator - Support group facilitator (`context_aware_scripted__Entity`)
6. Dialogic Conversation - Therapy session (`dialogic__GameMaster`)
7. Strategic Game - Prisoner's Dilemma (`game_theoretic__GameMaster`)
8. Marketplace - Farmers market trading
9. Interviewer - Employee survey (`interviewer__GameMaster`)
10. Formative Memories - High school reunion with LLM-generated backstories

*Research Studies:*
11. Vaccine Hesitancy Study - 5 agents with full psychological profiles
12. Phishing Attack Simulation - Nested simulations modeling attack chains
13. Urban Gentrification - 6 stakeholders with 11 grounded variables

*Advanced Features:*
14. Nested Simulation Demo - PhoneGameMaster pattern
15. Grounded Variables Demo - Numerical and categorical metric tracking

*SDG Scenarios:*
16. State Formation - SDG 16 (Peace & Justice)
17. Labor Strike - SDG 8 (Decent Work)
18. Fishery Management - SDG 14 (Life Below Water)
19. Flood Evacuation - SDG 11/13 (Cities & Climate)
20. Educational Opportunity - SDG 10 (Reduced Inequalities)

### Breaking Changes from Future Versions
(To be filled when upgrading)

---

## Upgrade Procedure

When upgrading gdm-concordia:

1. **Create test branch**
   ```bash
   git checkout -b test-concordia-upgrade
   ```

2. **Update version in requirements.txt**

3. **Install new version**
   ```bash
   source env/bin/activate
   pip install -r requirements.txt
   ```

4. **Run validation tests**
   ```bash
   # Test each template
   curl http://localhost:8000/api/simulations/templates/coffee-shop
   curl http://localhost:8000/api/simulations/templates/scripted-entity
   # ... test all templates
   ```

5. **Run actual simulations**
   - Coffee shop (5 steps, 2 agents)
   - Scripted entity (15 steps, 5 agents)
   - Strategic game (4 steps, 2 agents)

6. **Check for errors**
   - Empty agent responses?
   - API compatibility issues?
   - Import errors?

7. **Document any changes needed**
   - Update this CHANGELOG
   - Update code if Concordia APIs changed
   - Update templates if needed

8. **If tests pass, merge to main**

---

## Notes for Developers

### Key Files That Depend on Concordia

- `backend/services/simulation_builder.py` - Prefab loading and instantiation
- `backend/models/schemas.py` - Pydantic models matching Concordia types
- `backend/api/simulations.py` - Template definitions using prefab params
- `backend/models/llm_wrappers.py` - LLM wrappers implementing Concordia API

### Critical Concordia APIs We Use

```python
from concordia.language_model import language_model
from concordia.prefabs import prefab_lib
from concordia.prefabs.entity import basic_scripted
from concordia.associative_memory import basic_associative_memory
from concordia.framework.agents import basic_agent
```

### Custom Components We've Added

1. **Custom LLM Wrappers** - Wrap OpenAI-compatible APIs for Concordia
2. **Temperature Configured Model** - Allows runtime temperature control
3. **Scripted Act Component** - Already in Concordia, we use it
4. **Template System** - Our addition, not in core Concordia
5. **SSE Streaming** - Our addition for real-time progress
