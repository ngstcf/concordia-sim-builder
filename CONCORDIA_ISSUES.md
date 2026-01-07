# Concordia Framework Issues

This document tracks known issues with the Concordia framework that affect this simulation builder.

## Issue: `NextActingFromSceneSpec` Not Cycling Through Participants Correctly

**Severity**: High
**Status**: Confirmed - Concordia Framework Bug
**First Reported**: 2026-01-06
**Affected Component**: `concordia.components.game_master.next_acting.NextActingFromSceneSpec`

### Description

In game-theoretic simulations using `game_theoretic_and_dramaturgic__GameMaster`, the `NextActingFromSceneSpec` component fails to properly cycle through all participants. Instead of alternating between agents (e.g., Alex, Sam, Alex, Sam...), it selects the first agent once, then only selects the second agent for all remaining steps.

### Expected Behavior

With `num_rounds=8`, `participants=["Alex", "Sam"]`:
- Step 1: Alex acts
- Step 2: Sam acts
- Step 3: Alex acts
- Step 4: Sam acts
- Step 5: Alex acts
- Step 6: Sam acts
- Step 7: Alex acts
- Step 8: Sam acts

### Actual Behavior

- Step 1: Alex acts
- Step 2: Sam acts
- Step 3: Sam acts ❌ (should be Alex)
- Step 4: Sam acts ❌ (should be Alex)
- Step 5: Sam acts ❌ (should be Alex)
- Step 6: Sam acts ❌ (should be Alex)
- Step 7: Sam acts ❌ (should be Alex)
- Step 8: Sam acts ❌ (should be Alex)

### Root Cause Analysis

Looking at `NextActingFromSceneSpec.pre_act()` (lines 390-403):

```python
def pre_act(self, action_spec: entity_lib.ActionSpec,) -> str:
    result = ''
    if action_spec.output_type == entity_lib.OutputType.NEXT_ACTING:
        scene_participants = self._get_current_scene_participants()
        idx = self._counter % len(scene_participants)
        result = scene_participants[idx]
        self._counter += 1
        self._currently_active_player = result
    return result
```

The logic appears correct - it should cycle through participants using modulo. However, the issue suggests that either:
1. `scene_participants` is being modified (Alex removed after first action)
2. The `_counter` is being reset or corrupted
3. `get_participants()` is returning a different list after the first round

### Investigation Steps Taken

1. ✅ Verified `max_steps` and `num_rounds` are correctly matched (8)
2. ✅ Verified simulation runs for full 8 steps
3. ✅ Verified action extraction correctly identifies which agent acted
4. ❌ Unable to identify why `NextActingFromSceneSpec` stops cycling

### Workarounds

#### Option 1: Use `NextActingInFixedOrder` Instead

Instead of relying on `NextActingFromSceneSpec`, manually specify the acting sequence:

```python
from concordia.components.game_master import next_acting

next_actor = next_acting.NextActingInFixedOrder(
    sequence=["Alex", "Sam", "Alex", "Sam", "Alex", "Sam", "Alex", "Sam"]
)
```

However, this requires modifying the `game_theoretic_and_dramaturgic__GameMaster` prefab.

#### Option 2: Use Different Game Master Prefab

For simple strategic games, consider using `generic__GameMaster` with manual turn management instead of the game-theoretic prefab.

#### Option 3: Accept Current Behavior

Document that game-theoretic games are currently single-agent dominant and use analytics to interpret results accordingly.

### Impact on This Simulation Builder

1. **Analytics Extraction**: ✅ Working correctly - accurately reports what happened
2. **Template Configuration**: ⚠️ Game-theoretic templates produce asymmetric results
3. **User Expectations**: ⚠️ Users expect symmetric play but get asymmetric play

### Recommendation

**Short-term**:
- Add warning in UI that game-theoretic games may have asymmetric agent participation
- Document the workaround in README

**Long-term**:
- File issue with Concordia GitHub repository
- Consider forking `NextActingFromSceneSpec` to fix the bug
- Alternatively, create a custom game master prefab for this builder

### Related Files

- `/env/lib/python3.13/site-packages/concordia/components/game_master/next_acting.py` (lines 342-419)
- `/env/lib/python3.13/site-packages/concordia/components/game_master/scene_tracker.py` (lines 130-137)
- `/env/lib/python3.13/site-packages/concordia/prefabs/game_master/game_theoretic_and_dramaturgic.py` (lines 214-223)

### Test Cases to Reproduce

```python
# Configuration
max_steps = 8
num_rounds = 8
participants = ["Alex", "Sam"]
prefab = "game_theoretic_and_dramaturgic__GameMaster"

# Expected: Alex acts 4 times, Sam acts 4 times
# Actual: Alex acts 1 time, Sam acts 7 times
```

See simulation log: `logs/20260106_023240_Alex_Sam_Two_players_engage_in_an_iterated_Prisoners_Dilem.html`

---

## Issue: Scene Premise Type Mismatch

**Severity**: High
**Status**: Fixed in templates, but prone to user error
**First Reported**: 2026-01-06
**Affected Component**: `concordia.components.game_master.scene_tracker.SceneTracker`

### Description

The `scene_tracker.py` component expects scene `premise` to be a dictionary mapping participant names to their individual context lists, but the error message is unclear when a string is provided instead.

### Error Message

```
TypeError: string indices must be integers, not 'str'
  File "concordia/components/game_master/scene_tracker.py", line 145, in _get_premise
    premises = scene.premise[participant]
```

### Root Cause

Code expects:
```python
premise = {
  "Agent1": ["Context line 1", "Context line 2"],
  "Agent2": ["Context line 1", "Context line 2"]
}
premises = premise[participant]  # Returns list of strings
```

But receives:
```python
premise = "A single string describing the scene"
premises = premise[participant]  # TypeError: string indices must be integers
```

### Solution

Always use dictionary format in scene configurations:

```json
{
  "scenes": [{
    "premise": {
      "Agent1": ["Context for Agent1"],
      "Agent2": ["Context for Agent2"]
    }
  }]
}
```

All templates in this simulation builder have been fixed to use the correct format.

---

## Issue: Component Access After Simulation

**Severity**: Medium
**Status**: Workaround implemented
**First Reported**: 2026-01-06

### Description

After simulation completes, access to game master components (like PayoffMatrix) is lost, making it impossible to extract game-theoretic data directly from components.

### Attempted Solutions

1. **Direct Component Access**: `gm._components` → AttributeError (private attribute)
2. **Get Component Method**: `gm.get_component_names()` → Returns empty list
3. **Component Iteration**: Loop through available components → 0 components found

### Root Cause

Concordia doesn't expose component access API after simulation completion. Components are either:
- Garbage collected after simulation
- Stored in private inaccessible structures
- Not designed for post-simulation inspection

### Workaround Implemented

Parse HTML logs using BeautifulSoup and regex to extract:
- Agent actions from `__act__` tags
- Choices from action summaries
- Goals from entity sections

This three-tier extraction strategy is robust and works across different LLM outputs.

### Recommendation

Concordia should expose a `get_components()` API or save game-theoretic data to metadata during simulation for later retrieval.

---

## Issue: GLM Model Incompatibility

**Severity**: High for GLM users
**Status**: Documented, not recommended
**First Reported**: 2026-01-06

### Description

GLM (Zhipu AI) models frequently return empty responses for Concordia prompts, causing simulations to fail with "empty response" errors.

### Observed Behavior

- GLM works for basic text generation
- GLM fails for Concordia agent observations and decisions
- Failure rate: ~30-50% depending on prompt type
- No clear pattern to which prompts fail

### Likely Root Cause

GLM's training data and prompt format expectations differ from OpenAI-style prompts. Concordia's prompt engineering may be optimized for GPT-family models.

### Workaround

**Use DeepSeek instead**:
- Fully compatible with Concordia
- Broadly reported to be 20×–50× cheaper than GPT-4 (often quoted as orders of magnitude cheaper in many API pricing benchmarks)
- Similar quality for most tasks
- More reliable than GLM

GLM remains available for experimentation but is documented as "not recommended" in the UI.

---

## Configuration Guidelines

### `num_rounds` vs `max_steps` in Game-Theoretic Games

**Correct Configuration (Updated 2026-01-06):**

In Concordia's game-theoretic games:
- `max_steps` = Number of **game rounds** (each participant acts once per round)
- `num_rounds` in scene parameters = Must **equal** `max_steps`
- **Formula**: `num_rounds = max_steps` (NOT multiplied by participants)

Example for 4-round Prisoner's Dilemma with 2 agents:
```json
{
  "max_steps": 4,  // 4 game rounds
  "game_master": {
    "parameters": {
      "scenes": [{
        "num_rounds": 4  // MUST equal max_steps (not 4 × 2 = 8)
      }]
    }
  }
}
```

**Total individual actions** = num_rounds × participants = 4 × 2 = 8 actions

**Common Mistake:**
```json
// WRONG - Don't multiply by participants
"max_steps": 8,
"num_rounds": 8  // This creates 8 rounds, not 4
```

This is documented in the simulation builder UI and README to help users configure correctly.
