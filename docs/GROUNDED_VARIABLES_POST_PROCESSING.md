# Grounded Variables Post-Processing System

## Overview

The Grounded Variables Post-Processing system is a workaround for Concordia's architectural limitation where `SwitchAct` components never call `post_act()` on context components. This system extracts variable updates from completed simulations by analyzing HTML logs using LLM-based analysis.

### Problem Statement

In Concordia simulations, grounded variables are defined but never updated because:
1. The `SwitchAct` component controls simulation flow
2. `SwitchAct` never calls `post_act()` on context components
3. Variables remain at their initial values throughout the simulation

### Solution

Post-process the simulation after completion to:
1. Extract events from the HTML log
2. Use LLM analysis to identify variable changes
3. Update variable history in the metadata file
4. Enable visualization of variable trends over time

---

## How Post-Processing Works

### 1. Event Extraction

The post-processor parses the simulation HTML log to extract events:

**HTML Structure Requirements:**
```html
<details>
  <summary>Step 1: [Event Title]</summary>
  <div>[Event Content]</div>
</details>
```

**Extraction Logic:**
- Finds all `<details>` tags in the HTML
- Extracts step number from `<summary>` text (pattern: `Step \d+`)
- Filters events with > 50 characters (meaningful content)
- Deduplicates similar events within the same step
- Selects the longest event as the representative

**Critical Decision Point Detection:**
The post-processor looks for markers in the event text:
```
Step X: CRITICAL DECISION POINT
```

If found, it extracts content from this marker to the next step marker.

**Premise Removal:**
Repetitive context/premise text is automatically removed using patterns:
- `IMPORTANT: The Council will take ACTION`
- `CRITICAL DECISION POINTS: -`
- `Step 1: CRITICAL DECISION POINT`

### 2. Batch Processing

Events are processed in batches (default: 10 events per batch) for efficiency:

```python
BATCH_SIZE = 10
for i in range(0, len(events), BATCH_SIZE):
    batch = events[i:i + BATCH_SIZE]
    updates = extract_variable_updates_from_batch(batch)
```

### 3. LLM Analysis

For each batch, the LLM is prompted with:

**Input:**
- Variable descriptions with types, current values, update rules, ranges
- Event descriptions for the batch

**Task:**
Identify variable changes through:
1. **Explicit Changes:** Direct statements (e.g., "rent increases to $1900")
2. **Inferred Changes:** Logical deductions from actions (e.g., "Council approves 100 units" → `new_housing_units_permitted += 100`)
3. **Cumulative Effects:** Gradual changes over multiple steps

**Output Format:**
```json
{
  "5": {"median_monthly_rent": 1950, "low_income_displacement_rate": 20},
  "6": {},
  "7": {"inclusionary_zoning_active": true, "community_cohesion_index": 70}
}
```

### 4. Value Validation

Extracted values are validated against variable configurations:

**Type-Specific Validation:**
- **Boolean:** Converts to `true`/`false`, clamps to range
- **Numerical:** Converts to float, enforces `min_value`/`max_value`
- **Percentage:** Converts to float, enforces 0-100 range
- **Categorical:** Validates against `allowed_values`

**Invalid Values:**
- Out-of-range values are clamped to min/max
- Invalid categorical values keep current value
- Parse failures are logged and skipped

### 5. Metadata Update

Validated updates are stored in the simulation metadata:

```json
{
  "grounded_variables": {
    "median_monthly_rent": {
      "history": [
        {"step": 1, "value": 1800},
        {"step": 5, "value": 1950},
        {"step": 10, "value": 2100}
      ]
    }
  }
}
```

---

## Simulation Template Requirements

### 1. HTML Structure

**Required Format:**
```html
<details>
  <summary>Step 1: CRITICAL DECISION POINT - Council Meeting</summary>
  <div>
    The historically working-class neighborhood of Elm...

    IMPORTANT: The Council will take ACTION...

    CRITICAL DECISION POINTS:
    - Step 1: CRITICAL DECISION POINT
      The Council votes on the proposal...

    - Step 2: CRITICAL DECISION POINT
      Community response...
  </div>
</details>
```

**Key Requirements:**
- Each step must be in a `<details>` tag
- `<summary>` must contain "Step X" (case-insensitive)
- Event content must be > 50 characters

### 2. Critical Decision Point Markers

**Highly Recommended Format:**
```
Step X: CRITICAL DECISION POINT
[Event description]
```

**Alternative Formats (also supported):**
- `Step X: CRITICAL DECISION POINT - [Title]`
- `CRITICAL DECISION POINT - Step X: [Description]`

**Why Markers Matter:**
- Enables precise extraction of step-specific content
- Removes repetitive premise/context text
- Improves LLM accuracy by focusing on relevant actions
- Prevents contamination from adjacent steps

### 3. Variable Configuration

**Required Fields:**
```json
{
  "name": "median_monthly_rent",
  "variable_type": "numerical",  // or "percentage", "boolean", "categorical"
  "description": "Current median rent for a 1-bedroom apartment"
}
```

**Optional but Recommended:**
```json
{
  "default_value": 1800,
  "min_value": 500,
  "max_value": 5000,
  "update_rule": "Increases when luxury housing approved, decreases with rent control",
  "allowed_values": ["low", "medium", "high"]  // for categorical
}
```

**Field Impact:**
- `update_rule`: **CRITICAL** - Guides LLM inference for implicit changes
- `min_value`/`max_value`: Prevents unrealistic values
- `description`: Helps LLM understand variable context
- `default_value`: Initial value if extraction fails

### 4. Event Description Best Practices

**DO:**
- ✅ Be specific about actions and outcomes
- ✅ Use concrete numbers when possible
- ✅ Describe causal relationships clearly
- ✅ Include context about who did what

**Examples:**
```
✅ "The City Council votes 5-4 to approve the developer's request for 150 new luxury housing units.
   This will increase the housing supply but may accelerate gentrification."

✅ "After intense community organizing, the Council passes an inclusionary zoning ordinance requiring
   20% of new units to be affordable for households earning 60% of area median income."
```

**DON'T:**
- ❌ Use vague language ("some changes happened")
- ❌ Omit key decision outcomes
- ❌ Bury actions in lengthy prose
- ❌ Skip quantitative details

**Examples:**
```
❌ "The Council discussed housing issues." (Too vague)

❌ "Some people spoke about the neighborhood." (No actionable info)
```

### 5. Template Structure Example

**Recommended Template Pattern:**
```python
# In your simulation configuration
def create_grounded_variable_configs():
    return [
        {
            "name": "median_monthly_rent",
            "variable_type": "numerical",
            "description": "Current median rent for a 1-bedroom apartment in the neighborhood",
            "default_value": 1800,
            "min_value": 500,
            "max_value": 5000,
            "update_rule": "Increases with luxury development, decreases with rent control"
        },
        {
            "name": "rent_control_active",
            "variable_type": "boolean",
            "description": "Whether rent control regulations are in effect",
            "default_value": False,
            "update_rule": "Becomes true when Council passes rent control ordinance"
        }
    ]
```

---

## Robustness Features

### 1. Error Handling

**HTML Parsing Errors:**
- Gracefully continues if individual steps fail to parse
- Logs warnings but doesn't crash
- Returns partial results if possible

**LLM API Errors:**
- Catches exceptions and returns empty updates
- Logs detailed error messages
- Continues processing subsequent batches

**JSON Parse Errors:**
- Attempts regex fallback if JSON parsing fails
- Tries manual line-by-line parsing
- Logs parse failures for debugging

### 2. Validation Guards

**Type Validation:**
- Enforces boolean/numerical/percentage/categorical types
- Rejects invalid types
- Provides fallback to current value

**Range Validation:**
- Clamps numerical values to min/max
- Prevents negative percentages
- Ensures percentages stay 0-100

**Value Validation:**
- Categorical values checked against allowed list
- Invalid values rejected (keeps current)
- Type coercion for string inputs

### 3. Inference Capabilities

The LLM is explicitly instructed to:

**Be Aggressive with Inference:**
- "If the event describes a relevant action, infer the variable change"
- "Use the update_rule as a guide"
- "Consider both immediate and secondary effects"

**Handle Implicit Changes:**
- Council votes → infer policy outcomes
- Development approved → infer housing unit increases
- Community organizing → infer cohesion changes
- Business closures → infer survival rate decreases

**Examples from Prompt:**
```
✓ Council "approves 100 new housing units" → new_housing_units_permitted += 100
✓ Council "rejects rent control" → rent_control_active = false, rents may increase
✓ "intense community organizing" → community_cohesion_index increases
✓ "businesses closing due to rents" → small_business_survival_rate decreases
✓ "new luxury development approved" → median_monthly_rent increases
```

### 4. Batch Efficiency

**Optimizations:**
- Processes 10 events per LLM call (vs 1-by-1)
- Reduces API calls by 90%
- Maintains context across related events
- Faster overall processing

**Trade-offs:**
- Slightly more complex prompt
- Need to parse multi-step responses
- Better for simulations with 30+ steps

---

## Usage Example

### Backend API

```python
from backend.utils.grounded_variables_post_processor import GroundedVariablesPostProcessor

# Initialize
model, _ = get_model_and_embedder(llm_settings)
processor = GroundedVariablesPostProcessor(model, variable_configs)

# Process simulation
history = processor.process_simulation(
    html_path="logs/simulation.html",
    metadata_path="logs/simulation.metadata.json"
)

# Result:
# {
#     "median_monthly_rent": [
#         {"step": 1, "value": 1800},
#         {"step": 5, "value": 1950},
#         {"step": 10, "value": 2100}
#     ],
#     ...
# }
```

### Frontend Integration

```typescript
// Extract variables
await extractGroundedVariables(
  simulationId,
  filename,
  llmSettings
);

// Retrieve extracted data
const analytics = await getSimulationAnalytics(filename);
// analytics.grounded_variables now has history
```

### Creating Custom Simulations with Grounded Variables

#### Method 1: Export and Modify Existing Template

**Step 1: Export a template with grounded variables**

```bash
# Via API
curl http://localhost:8000/api/simulations/templates/urban-gentrification -o urban_gentrification.json

# Via Web UI
# Builder tab → Load Template → Select "Urban Gentrification" → Export JSON
```

**Step 2: Modify the exported JSON**

```json
{
  "game_master": {
    "prefab": "generic__GameMaster",
    "grounded_variables": [
      {
        "name": "median_monthly_rent",
        "variable_type": "numerical",
        "description": "Current median rent for a 1-bedroom apartment",
        "default_value": 1800,
        "min_value": 500,
        "max_value": 5000,
        "update_rule": "Increases when luxury housing approved, decreases with rent control"
      }
    ],
    "critical_decision_points": [
      {
        "step": 10,
        "event": "CRITICAL DECISION POINT: The City Council votes on the proposal..."
      }
    ]
  }
}
```

**Key fields to modify:**
- **`update_rule`** (CRITICAL): Tells the AI what causes the variable to change
- **`critical_decision_points`** (Optional): Markers for precise event extraction
- **`min_value`/`max_value`**: Prevents unrealistic extracted values

**Step 3: Import your custom simulation**

```bash
# Via Web UI
# Builder tab → Import JSON → Select your modified file
```

#### Method 2: Define Variables in Web UI

**Location:** Builder tab → Game Master section → Grounded Variables

```
┌─────────────────────────────────────────────────────────────┐
│ Game Master Configuration                                    │
├─────────────────────────────────────────────────────────────┤
│ [+ Add Grounded Variable]                                   │
│                                                             │
│ ┌─ Variable 1 ───────────────────────────────────────────┐ │
│ │ Name:        [team_morale                    ]         │ │
│ │ Type:        [Numerical ▼]                            │ │
│ │ Description: [Overall team morale (0-100)    ]         │ │
│ │ Min/Max:     [0      ] / [100    ]                    │ │
│ │ Default:     [70     ]                               │ │
│ │ Update Rule: [Changes based on workload...  ] ← KEY! │ │
│ └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Important Notes:**
1. **`update_rule` is the most important field** - Without it, the LLM cannot infer variable changes from events
2. **`critical_decision_points` are optional** - They improve accuracy but the system works without them
3. **Variable types matter** - Use appropriate types (numerical, percentage, boolean, categorical) for best results

---

## Troubleshooting

### Issue: No Variables Extracted

**Possible Causes:**
1. HTML structure doesn't match expected format
2. Events too short (< 50 characters)
3. Step numbers not found in summaries

**Solutions:**
- Verify HTML has `<details>` tags
- Check `<summary>` contains "Step X"
- Ensure event content is substantive

### Issue: Inaccurate Extractions

**Possible Causes:**
1. Vague event descriptions
2. Missing update rules
3. Insufficient context

**Solutions:**
- Add specific details to events
- Include update_rule in config
- Use CRITICAL DECISION POINT markers

### Issue: Variables Out of Range

**Possible Causes:**
1. No min/max values specified
2. LLM hallucinates extreme values

**Solutions:**
- Always set min_value/max_value
- Add clamping in validation
- Review LLM prompts

### Issue: Parse Errors

**Possible Causes:**
1. Malformed JSON response
2. Invalid value types
3. Missing required fields

**Solutions:**
- Check LLM response format
- Verify variable type configuration
- Enable detailed logging

---

## Best Practices Summary

### For Template Authors

1. **Always use CRITICAL DECISION POINT markers**
   - Format: `Step X: CRITICAL DECISION POINT`
   - Improves extraction accuracy significantly

2. **Provide update rules for all variables**
   - Guides LLM inference
   - Essential for implicit changes

3. **Be specific in event descriptions**
   - Include concrete numbers
   - Describe causal relationships
   - Mention decision outcomes

4. **Set realistic ranges**
   - Prevents extreme values
   - Catches LLM errors

5. **Use proper HTML structure**
   - `<details>` for each step
   - `<summary>` with step number
   - Meaningful content (> 50 chars)

### For Developers

1. **Use batch processing**
   - More efficient than 1-by-1
   - Better context for LLM

2. **Validate all inputs**
   - Type checking
   - Range enforcement
   - Value validation

3. **Handle errors gracefully**
   - Log warnings
   - Continue processing
   - Provide partial results

4. **Test with real simulations**
   - Verify extraction accuracy
   - Check variable trends
   - Validate UI display

---

## Future Improvements

Potential enhancements to the system:

1. **Incremental Processing**
   - Process checkpoints during simulation
   - Update variables in real-time
   - Reduce post-processing time

2. **Confidence Scores**
   - LLM provides confidence for each extraction
   - Low-confidence changes flagged for review
   - Human-in-the-loop validation

3. **Multi-Model Consensus**
   - Use multiple LLMs
   - Compare extractions
   - Vote on best result

4. **Learning from Corrections**
   - Store human corrections
   - Fine-tune prompts
   - Improve accuracy over time

5. **Causal Chain Tracing**
   - Track which events caused which changes
   - Visualize causal relationships
   - Better explainability

---

## References

- **Concordia Framework:** https://github.com/google-deepmind/concordia
- **Implementation:** `backend/utils/grounded_variables_post_processor.py`
- **API Endpoint:** `POST /api/simulations/grounded-variables/extract`
- **Frontend Component:** `frontend/src/components/SimulationRunner/GroundedVariablesChart.tsx`
