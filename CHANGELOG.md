# Concordia Compatibility Changelog

## Version 2.1.0 (Current - Validated 2025-01-07)

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
