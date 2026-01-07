# Research Use Case: Vaccine Hesitancy and Social Contagion

## Overview

This study demonstrates how customizable psychological components enable researchers to model complex social phenomena, specifically investigating how different cognitive biases and social identity factors influence vaccine hesitancy spread through communities.

## Research Question

**How do cognitive biases (confirmation bias, availability heuristic) and social identity dynamics interact to affect vaccine acceptance rates in different community types?**

## Theoretical Framework

This study integrates two major psychological theories:

1. **Cognitive Bias Theory** (Tversky & Kahneman, 1974)
   - Confirmation Bias: Seeking information that confirms existing beliefs
   - Availability Heuristic: Overweighting easily recalled examples

2. **Social Identity Theory** (Tajfel & Turner, 1979)
   - In-group favoritism and out-group skepticism
   - Identity-protective cognition

## Simulation Design

### Population Configuration

```json
{
  "agents": [
    {
      "id": "health_worker_1",
      "name": "Dr. Sarah Chen",
      "prefab": "basic__Entity",
      "goal": "Promote public health through vaccination education",
      "components": {
        "personality_traits": {
          "openness": 5,
          "conscientiousness": 5,
          "agreeableness": 4,
          "extraversion": 3,
          "neuroticism": 2
        },
        "theory_of_planned_behavior": {
          "behavior": "recommend vaccination",
          "attitude": "strongly_favorable",
          "subjective_norm": "strongly_favorable",
          "perceived_control": "high"
        }
      }
    },
    {
      "id": "skeptic_1",
      "name": "Mike Johnson",
      "prefab": "basic__Entity",
      "memories": [
        "Read online forums about vaccine side effects",
        "Distrusts pharmaceutical companies",
        "Values personal freedom and autonomy"
      ],
      "components": {
        "cognitive_bias": {
          "bias_type": "confirmation_bias",
          "bias_strength": "strong"
        },
        "social_identity": {
          "group_membership": ["libertarian_community", "natural_health advocates"],
          "identification_strength": "strong"
        },
        "values": {
          "core_values": ["freedom", "autonomy", "natural_living"],
          "value_conflict": "freedom_vs_collectivism"
        }
      }
    },
    {
      "id": "undecided_1",
      "name": "Maria Garcia",
      "prefab": "basic__Entity",
      "memories": [
        "Heard mixed information about vaccines",
        "Trusts her family doctor",
        "Worried about side effects but also about disease"
      ],
      "components": {
        "cognitive_bias": {
          "bias_type": "availability_heuristic",
          "bias_strength": "moderate"
        },
        "emotion": {
          "current_emotion": "anxiety",
          "emotion_intensity": "moderate"
        },
        "theory_of_planned_behavior": {
          "behavior": "get_vaccinated",
          "attitude": "ambivalent",
          "subjective_norm": "neutral",
          "perceived_control": "moderate"
        }
      }
    }
  ]
}
```

### Experimental Conditions

#### Condition 1: Baseline (No Components)
- Standard agents without psychological components
- Measures default persuasion effectiveness

#### Condition 2: Cognitive Bias Only
- Skeptics with confirmation bias
- Tests how biased information processing affects persuasion

#### Condition 3: Full Psychological Model
- Combination of cognitive biases + social identity + values
- Tests interaction effects between multiple psychological factors

### Game Master Configuration

```json
{
  "game_master": {
    "prefab": "generic__GameMaster",
    "name": "Community Health Scenario",
    "extra_components": {
      "grounded_variables": {
        "vaccine_acceptance_rate": {
          "type": "percentage",
          "initial_value": 45,
          "update_rule": "based on agent decisions"
        },
        "misinformation_spread": {
          "type": "count",
          "initial_value": 0,
          "tracking": "mentions of false claims"
        }
      }
    }
  }
}
```

## Hypothesized Outcomes

### Primary Hypotheses

1. **H1**: Agents with confirmation bias will be 40% less likely to change their stance after pro-vaccine information compared to baseline agents.

2. **H2**: When social identity components are activated, in-group messengers (same community membership) will be 2.5x more persuasive than out-group messengers.

3. **H3**: The availability heuristic will cause undecided agents to weight recent anecdotal stories (whether positive or negative) more heavily than statistical evidence.

4. **H4**: Value conflicts (freedom vs. collective good) will create "motivated reasoning" where agents selectively accept information that aligns with their core values.

### Measured Variables

| Variable | Type | Measurement Method |
|----------|------|-------------------|
| Vaccine acceptance | Binary | Agent's stated decision |
| Attitude strength | Ordinal | Pre/post scales (1-7) |
| Information recall | Count | Correct facts remembered |
| Social influence | Network | Which agents persuaded whom |
| Emotional response | Categorical | Fear, anger, hope, neutral |
| Conversation turns | Count | Depth of deliberation |

## Key Manipulations

### Manipulation 1: Messenger Identity
- **In-group messenger**: Same community membership as target
- **Out-group messenger**: Different community membership
- **Authority messenger**: Health professional status

### Manipulation 2: Information Type
- **Statistical evidence**: "CDC data shows 95% effectiveness"
- **Anecdotal evidence**: "My neighbor got vaccinated and had no side effects"
- **Mixed approach**: Combination of both

### Manipulation 3: Emotional Frame
- **Fear appeal**: Focus on disease risks
- **Hope appeal**: Focus on community protection
- **Neutral**: Informational only

## Expected Findings

### Scenario A: Confirmation Bias Dominance

```
Step 1: Health worker presents CDC statistics
  → Mike (confirmation bias: strong)
  → Interprets statistics as "big pharma propaganda"
  → Strengthens original stance (backfire effect)

Step 2: Community member shares personal story
  → Mike (in-group identity activated)
  → More receptive but still skeptical
  → Asks clarifying questions

Step 3: Community member emphasizes freedom of choice
  → Mike (values: freedom, autonomy)
  → "I appreciate that you respect my right to choose"
  → Shows increased openness to discussion
```

### Scenario B: Availability Heuristic Dominance

```
Step 1: Undecided person hears horror story from friend
  → Maria (availability heuristic: moderate)
  → Overweights recent emotional story
  → Temporarily more hesitant

Step 2: Health worker shares statistics
  → Maria (anxiety: moderate)
  → Statistics feel abstract vs. vivid story
  → Limited attitude change

Step 3: Multiple community members share positive experiences
  → Maria (availability heuristic activated)
  → Recent examples shift mental accessibility
  → Positive experiences become more salient
  → Attitude shifts toward acceptance
```

## Research Contributions

### Theoretical Contributions

1. **Mechanism Isolation**: By toggling components on/off, researchers can isolate the causal effect of specific psychological mechanisms

2. **Interaction Testing**: Multiple components can be combined to test theory-driven interactions (e.g., "Does confirmation bias amplify identity-protective cognition?")

3. **Boundary Conditions**: Test when psychological effects are strongest/weakest by varying parameter values (weak/moderate/strong)

### Practical Applications

1. **Message Design**: Identify which message frames work best for different psychological profiles

2. **Messenger Selection**: Determine optimal messenger characteristics for target audiences

3. **Intervention Timing**: Understand when in the decision process interventions are most effective

## Advantages of Component System

### Traditional Approach (Without Components)
```python
# Hard-coded agent behavior
if agent.name == "Mike":
    if "vaccine" in message and "pharma" in message:
        return reject_as_propaganda()
    elif "freedom" in message:
        return consider_message()
```

### Component-Based Approach
```python
# Configurable psychological model
agent.components = {
    "cognitive_bias": {"bias_type": "confirmation_bias", "bias_strength": "strong"},
    "social_identity": {"group_membership": ["libertarians"], "identification_strength": "strong"},
    "values": {"core_values": ["freedom", "autonomy"]}
}
# Behavior emerges from interaction of components
```

### Key Benefits

1. **Rapid Prototyping**: Test different psychological configurations without rewriting code

2. **Theory Alignment**: Components map directly to psychological theories

3. **Replicability**: Exact configurations can be shared and reproduced

4. **Systematic Variation**: Change one parameter at a time to test specific effects

5. **Multi-Dimensional**: Agents can have multiple psychological systems operating simultaneously

## Extension Studies

### Study 1: Cross-Cultural Variation
- Compare individualist vs. collectivist cultures
- Components: `social_identity` with different group norms
- Expected: Individualist cultures show stronger reactance to mandates

### Study 2: Temporal Dynamics
- Track attitude change over multiple conversation rounds
- Components: `emotion` (changing over time)
- Expected: Emotional arousal decreases over time, increasing rational processing

### Study 3: Network Effects
- Vary community structure (tight-knit vs. loose networks)
- Components: `social_identity` with different group overlaps
- Expected: Tight-knit communities show stronger consensus effects

## Publication Strategy

### Target Journals
- **Computational Social Science**: PLOS ONE, Scientific Reports
- **Health Psychology**: Health Psychology, Journal of Health Communication
- **Methodological**: Behavior Research Methods, Journal of Artificial Societies

### Paper Structure
1. **Introduction**: Vaccine hesitancy as a complex socio-cognitive phenomenon
2. **Theoretical Framework**: Cognitive bias + social identity integration
3. **Methods**: Component-based simulation methodology
4. **Results**: Systematic variation of psychological parameters
5. **Discussion**: Theoretical and practical implications
6. **Supplementary**: Complete component configurations for reproducibility

## Data Sharing Plan

All simulation configurations will be shared via:
- Component configuration JSON files
- Parameter values for each condition
- Generated conversation transcripts
- Grounded variable trajectories

## Conclusion

This use case demonstrates how customizable psychological components enable:
- **Theory-driven** agent design
- **Systematic experimentation** with psychological factors
- **Rapid iteration** across conditions
- **Clear documentation** of psychological assumptions

The component system transforms agent-based modeling from "black box" behavior to transparent, theory-grounded simulations that can advance both computational methods and psychological theory.
