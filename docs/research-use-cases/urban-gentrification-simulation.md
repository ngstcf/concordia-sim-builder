# Urban Gentrification & Housing Policy Simulation

## Overview

This research use case demonstrates how **grounded variables** enable longitudinal urban economics research. The simulation tracks key neighborhood metrics over time as stakeholders make decisions about housing, development, and community preservation.

**Template Location:** Simulation Builder → Research Studies → "Urban Gentrification"

**Key Concordia Feature:** Grounded Variables (state tracking over time)

---

## Research Context

### The Challenge

Urban gentrification is a complex, multi-stakeholder process with contested outcomes:
- **Economic development** vs. **affordability**
- **New investment** vs. **displacement risk**
- **Neighborhood change** vs. **community preservation**

Researchers struggle to study these dynamics because:
1. **Long time horizons:** Gentrification unfolds over years
2. **Ethical constraints:** Cannot experiment with real communities
3. **Complex feedback loops:** Many interacting variables
4. **Stakeholder conflicts:** Competing legitimate interests

### Why Grounded Variables?

This template uses grounded variables to track neighborhood metrics in real-time as stakeholders debate policies. This enables:

1. **Longitudinal analysis:** Observe how variables evolve across 30 decision points
2. **Counterfactual reasoning:** Test "what if" policy scenarios
3. **Feedback loop modeling:** See how decisions affect future options
4. **Quantifiable tradeoffs:** Measure costs and benefits of different choices

---

## Simulation Structure

### Main Simulation (30 steps)

**Setting:** The historically working-class neighborhood of Elmwood faces rapid change after a tech company's nearby expansion. The City Council holds meetings to decide on housing policies and development proposals.

**Stakeholders:**

| Agent | Role | Core Interests |
|-------|------|----------------|
| **Maria Rodriguez** | Housing Advocate | Prevent displacement, preserve affordability |
| **James Chen** | Real Estate Developer | Profitable development, market-rate housing |
| **Fatima Al-Hassan** | Small Business Owner | Keep business open, preserve neighborhood character |
| **David Kim** | City Planner | Balance development with affordability |
| **Alex Thompson** | New Resident | Affordable housing, good neighbor |
| **Robert Schwartz** | Landlord | Maximize rental income, maintain tenant relationships |

### Grounded Variables Tracked

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `median_monthly_rent` | Numerical | $800-$5,000 | Median rent for 2-bedroom apartment |
| `low_income_displacement_rate` | Percentage | 0-100% | Households earning <50% AMI displaced in 2 years |
| `small_business_survival_rate` | Percentage | 0-100% | Small businesses remaining open |
| `community_cohesion_index` | Numerical | 0-100 | Sense of community belonging |
| `property_tax_base` | Numerical | $300M-$1.5B | Total assessed property value |
| `new_housing_units_permitted` | Numerical | 0-500 | New units approved in past year |
| `affordable_housing_units` | Numerical | 0-1,000 | Units affordable to <80% AMI households |
| `housing_affordability_index` | Percentage | 0-100% | Units affordable to median income households |
| `rent_control_active` | Boolean | True/False | Whether rent control is enacted |
| `inclusionary_zoning_active` | Boolean | True/False | Whether inclusionary zoning is enacted |
| `neighborhood_character` | Categorical | 5 states | Overall identity (traditional, transitional, mixed, gentrified, declining) |

---

## Research Applications

### 1. Gentrification Dynamics

**Research Questions:**
- How do different stakeholder decisions interact to produce gentrification outcomes?
- What are the early warning signs of displacement pressure?
- How does the timing of interventions affect outcomes?

**Methodology:**
- Run multiple simulations with different stakeholder configurations
- Track trajectories of grounded variables over time
- Compare "early intervention" vs. "late intervention" scenarios

**Key Metrics:**
- Displacement rate trajectory (is it accelerating/decelerating?)
- Rent increase rate (is it linear/exponential?)
- Business survival threshold (at what rent level do businesses fail?)

### 2. Housing Policy Evaluation

**Research Questions:**
- What is the effectiveness of rent control vs. inclusionary zoning?
- How do policy combinations interact (e.g., rent control + density bonuses)?
- What are the unintended consequences of well-intentioned policies?

**Methodology:**
- **Condition 1:** Baseline (no interventions)
- **Condition 2:** Rent control only
- **Condition 3:** Inclusionary zoning only
- **Condition 4:** Combined policies

**Outcome Measures:**
- Affordability index (primary effectiveness metric)
- New housing units permitted (supply impact)
- Property tax base (city revenue impact)
- Community cohesion (social impact)

### 3. Displacement Risk Modeling

**Research Questions:**
- Which variables are most predictive of displacement?
- How do rent increases translate to household displacement?
- What tenant protection policies are most effective?

**Methodology:**
- Correlate rent increases with displacement rates
- Test tenant protection interventions (just cause eviction, right to counsel)
- Model household budget constraints vs. rent

**Predictive Modeling:**
```
Displacement Risk = f(
  rent_increase_rate,
  household_income,
  vacancy_rate,
  alternative_housing_supply,
  tenant_protection_strength
)
```

### 4. Economic Development Tradeoffs

**Research Questions:**
- How does new construction affect affordability?
- What is the optimal mix of market-rate and affordable units?
- How do property tax increases fund city services vs. displace residents?

**Methodology:**
- Vary inclusionary zoning percentages (10%, 20%, 30%)
- Track property tax base vs. displacement rate
- Model city budget constraints and service provision

---

## Quantitative Analysis

### Time-Series Visualization

The grounded variables dashboard enables visualizing trajectories:

**Example Analysis:**
```python
# Compare rent control vs. no intervention
plt.plot(steps_no_control['median_monthly_rent'], label='No Control')
plt.plot(steps_rent_control['median_monthly_rent'], label='Rent Control')
plt.ylabel('Median Rent ($)')
plt.xlabel('Simulation Step')
plt.legend()
plt.title('Rent Trajectory: Policy Comparison')
```

### Threshold Analysis

Identify critical thresholds where outcomes change dramatically:

- **Rent threshold:** At what rent level does displacement accelerate?
- **Affordability threshold:** What % of units must be affordable to maintain diversity?
- **Business threshold:** At what rent do small businesses close en masse?

### Composite Indicators

Calculate multi-dimensional metrics:

**Gentrification Pressure Index:**
```
GPI = (rent_increase_weight * rent_change +
       displacement_weight * displacement_rate +
       business_closure_weight * business_loss +
       cohesion_weight * cohesion_loss) / 4
```

**Neighborhood Health Score:**
```
NHS = (affordability_index +
       business_survival_rate +
       community_cohesion_index +
       new_housing_units / 10) / 4
```

---

## Extension Ideas

### 1. Geographic Scale

**Micro-Scale (Block):**
- Single building or block redevelopment
- Direct neighbor-to-neighbor interactions
- Hyper-local displacement

**Meso-Scale (Neighborhood):**
- Current template scope
- Multiple stakeholders and interests
- Policy interventions

**Macro-Scale (City):**
- Citywide housing market dynamics
- Spillover effects between neighborhoods
- City budget and services

### 2. Policy Levers

Add grounded variables for:

- **Community Land Trust:** Non-profit ownership for affordability
- **Density Bonuses:** Extra height for affordability
- **Tax Abatements:** Property tax breaks for affordable units
- **First Source Hiring:** Local hiring requirements for developments
- **Anti-Displacement Tax Funds:** Developer fees fund relocation assistance

### 3. Stakeholder Configurations

Test different power dynamics:

- **Developer-Friendly:** Weak regulations, pro-growth
- **Tenant-Power Strong:** Strong rent control, just cause eviction
- **Balanced:** Mixed policies, stakeholder collaboration
- **Apathetic City:** Limited enforcement, weak planning capacity

### 4. External Shocks

Introduce exogenous events:

- **Economic Recession:** Housing demand drops, unemployment rises
- **Transit Investment:** New subway line increases accessibility
- **Corporate Arrival:** Major employer moves nearby
- **State/Federal Policy:** Changes in housing funding or regulations

---

## Connection to Real-World Research

### Urban Economics Literature

**Gentrification Theories:**
- **Supply-Side:** Production of chic housing (Smith 1979, 1982)
- **Demand-Side:** Consumption preferences (Ley 1980, 1996)
- **Rent Gap:** Difference between actual and potential rent (Smith 1979)

**Displacement Mechanisms:**
- **Direct:** Landlord actions, evictions, rent increases
- **Indirect:** Cultural displacement, business closure, institutional pressure
- **Exclusionary:** New housing unaffordable to existing residents

### Policy Evaluation Studies

**Rent Control:**
- Diamond, McQuade, & Qian (2019). "The Effects of Rent Control Expansion on Tenants, Landlords, and Inequality." *American Economic Review*.
- Autor, Palmer, & Pathak (2020). "Housing Market Spillovers." *AEJ: Economic Policy*.

**Inclusionary Zoning:**
- Schuetz, Meltzer, & Been (2009). "Density Effects of Inclusionary Zoning." *Journal of Urban Economics*.
- Stabrowski (2019). "Inclusionary Housing Policy in New York City." *Housing Policy Debate*.

### Mixed-Methods Approaches

This simulation enables both:
- **Quantitative:** Variable trajectories, threshold analysis, policy comparison
- **Qualitative:** Stakeholder narratives, argumentation, framing, consensus-building

---

## Advantages Over Traditional Methods

### Compared to Case Studies

| | Case Studies | Simulation |
|---|-------------|------------|
| **Time** | Years of data | 30 minutes |
| **Counterfactuals** | Impossible | Easy |
| **Replication** | Difficult | Identical |
| **Causal Inference** | Correlational | Experimental |

### Compared to Econometric Models

| | Econometric Models | Agent-Based Simulation |
|---|-------------------|------------------------|
| **Heterogeneity** | Representative agent | Diverse agents |
| **Dynamics** | Equilibrium focus | Process tracing |
| **Complexity** | Simplifying assumptions | Emergent outcomes |
| **Narratives** | Statistical results | Rich qualitative data |

### Compared to Field Experiments

| | Field Experiments | Simulation |
|---|------------------|------------|
| **Ethics** | Human subjects risks | No real-world impact |
| **Cost** | Very expensive | Minimal |
| **Speed** | Years | Minutes |
| **Control** | Limited | Complete |

---

## Running This Simulation

### Step-by-Step

1. **Load Template:** Simulation Builder → Research Studies → "Urban Gentrification"
2. **Review Configuration:** 6 stakeholders, 11 grounded variables
3. **Set LLM Settings:** Gemini 2.0 Flash Exp recommended for speed
4. **Run Simulation:** ~30 steps for policy deliberations
5. **Analyze Results:** Review grounded variable trajectories
6. **Compare Runs:** Vary policies to test hypotheses

### Expected Runtime

- **Main Simulation:** 30 steps × ~30 seconds = ~15-20 minutes
- **Grounded Variable Updates:** Automatic after each step
- **Total:** Approximately 15-20 minutes

### Analyzing Outputs

1. **Dashboard → Grounded Variables:** View variable histories
2. **Actions Tab:** Track stakeholder proposals and decisions
3. **Natural Language Summary:** Get AI-generated overview of policy outcomes
4. **Export Data:** Download for time-series visualization

### Interpreting Variables

**Key Thresholds to Watch:**

- `median_monthly_rent` > $2,500: Accelerating displacement risk
- `low_income_displacement_rate` > 30%: Severe community disruption
- `small_business_survival_rate` < 60%: Neighborhood character loss
- `housing_affordability_index` < 20%: Housing crisis
- `community_cohesion_index` < 40: Social fabric breakdown

**Categorical States:**

- `traditional_working_class`: Low rent, low displacement, high cohesion
- `transitional`: Rising rents, moderate displacement, mixed signals
- `mixed_income_stable`: Moderate rent, controlled displacement, policies working
- `gentrified_upscale`: High rent, high displacement, low cohesion, high tax base
- `disinvested_declining`: Low rent, low investment, declining services

---

## Example Research Design

### Study: Effectiveness of Tenant Protection Policies

**Hypothesis:** Rent control reduces displacement but decreases new housing construction.

**Conditions:**
1. **Control:** No tenant protections
2. **Rent Control Only:** Rent stabilization enacted
3. **Inclusionary Zoning Only:** 20% affordable requirement
4. **Combined:** Rent control + inclusionary zoning

**Dependent Variables:**
- Primary: `low_income_displacement_rate`
- Secondary: `new_housing_units_permitted`, `housing_affordability_index`

**Replicates:** 10 runs per condition (N=40)

**Analysis:**
- ANOVA comparing displacement rates across conditions
- Time-series analysis of rent trajectories
- Qualitative analysis of stakeholder arguments

**Expected Results:**
- Rent control reduces displacement by 40-60%
- But reduces new construction by 20-30%
- Combined policies balance tradeoffs

---

## References & Further Reading

### Academic Literature

**Gentrification:**
- Freeman, L. (2005). "Displacement or Succession?" *Regional Studies*.
- Zuk, M. et al. (2015). "Gentrification, Displacement, and the Role of Investment." *UC Berkeley*.

**Housing Policy:**
- Desmond, M. (2016). *Evicted: Poverty and Profit in the American City*. Crown.
- Glaeser, E. (2011). *Triumph of the City*. Penguin Press.

**Agent-Based Modeling:**
- Epstein, J. M. (2006). *Generative Social Science*. Princeton University Press.
- Macy, M. & Willer, R. (2002). "From Factors to Actors." *Annual Review of Sociology*.

### Policy Reports

- **Urban Institute:** "Housing Affordability and Displacement" (2022)
- **Brookings Institution:** "Inclusive Revitalization" (2021)
- **Lincoln Institute:** "Managing Neighborhood Change" (2020)

### Data Sources

- **HUD:** Affordability data by metro area
- **Census Bureau:** American Community Survey demographics
- **Zillow/Rental List:** Rent price data
- **Local Governments:** Property tax records, permit data

---

## Citation

If you use this simulation template in research, please cite:

```bibtex
@misc{concordia-gentrification-2025,
  title={Urban Gentrification \& Housing Policy Simulation},
  author={Concordia Simulation Builder},
  year={2025},
  url={https://github.com/ngstcf/concordia-sim-builder}
}
```

---

## Acknowledgments

This template was inspired by:
- Real debates in cities like San Francisco, New York, and Portland
- Research by the Urban Displacement Project (UC Berkeley)
- Policy experiments in inclusionary zoning and rent control

**Last Updated:** January 2026
**Concordia Version:** Based on Google DeepMind's Concordia framework
**Template Author:** Concordia Simulation Builder contributors
