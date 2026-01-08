# Phishing Attack Simulation: Cybersecurity Tabletop Exercise

## Overview

This research use case demonstrates how **nested simulations** enable meta-cognitive reasoning in cybersecurity threat analysis. Security analysts simulate adversarial scenarios to assess phishing risk without actual exposure to threats—a digital "fire drill" for incident response.

**Template Location:** Simulation Builder → Research Studies → "Phishing Attack Simulation"

**Key Concordia Feature:** Nested Simulations (PhoneGameMaster pattern)

---

## Research Context

### The Challenge

Cybersecurity teams face a fundamental paradox: they need to prepare for real attacks but cannot safely expose systems or users to actual threats. Traditional training (phishing simulations, tabletop exercises) has limited realism because participants know it's a simulation.

### Why Nested Simulations?

This template demonstrates **meta-cognitive reasoning**—agents simulating adversarial scenarios to inform decision-making. Each security analyst runs a nested simulation (hacker → user → IT response) to:

1. **Model attack chains** without actual risk
2. **Quantify impact** (infection rate, detection time, cost)
3. **Test defense effectiveness** in a controlled environment
4. **Build mental models** of threat actor behavior

This mirrors real cybersecurity practice: red teams simulate attacks, blue teams practice response, and analysts conduct "what-if" scenario planning.

---

## Simulation Structure

### Main Simulation (25 steps)

**Setting:** A financial services company receives a suspicious email from the CEO's personal email at 2:30 AM, requesting urgent wire transfer instructions.

**Participants:**
- **Sarah** (Senior Security Analyst): Technical analysis of attack mechanics
- **Marcus** (Technical Security Engineer): Assessment of security controls
- **Elena** (Security Awareness Manager): Human factors and training effectiveness
- **David** (CISO): Synthesizes analysis and makes response decisions

### Nested Simulations (8 steps each)

Each analyst runs a mini-simulation modeling:

**Three-Agent Attack Chain:**
1. **Hacker Agent:** Simulates adversarial behavior
   - Tactics: Credential harvesting, malware deployment, lateral movement
   - Constraints: Time pressure, detection avoidance
   - Goals: Establish persistence, exfiltrate data

2. **User/Employee Agent:** Represents potential victims
   - Context: Time pressure, authority cues, fatigue
   - Vulnerabilities: Lack of training, stress, trust in leadership
   - Decision: Click or verify?

3. **IT Security Agent:** Incident response
   - Detection: SIEM alerts, behavioral analytics
   - Response: Isolation, credential reset, forensics
   - Timeline: Average 2-4 hours for triage

### Extraction Prompts

Each nested simulation concludes with:
- **Sarah:** "What happened after the employee clicked the link? How quickly did IT security detect and respond? What was the impact and cost?"
- **Marcus:** "What technical controls failed? How did the hacker bypass security measures? What could have prevented detection earlier?"
- **Elena:** "Which employee was more vulnerable and why? What psychological factors were at play? How effective was security training?"

---

## Grounded Variables (Recommended for Enhancement)

While this template focuses on nested simulations, it could be enhanced with grounded variables to track:

| Variable | Type | Purpose |
|----------|------|---------|
| `suspicion_level` | Numerical (0-100) | Team's confidence that email is phishing |
| `time_elapsed` | Numerical (minutes) | Time since email receipt |
| `users_exposed` | Numerical | Number of employees who received the email |
| `credentials_compromised` | Boolean | Whether credentials were stolen |
| `malware_deployed` | Boolean | Whether malware infected systems |
| `detection_time` | Numerical (minutes) | Time from click to detection |
| `remediation_cost` | Numerical ($) | Cost of incident response |
| `decision_made` | Categorical | Action taken (block, investigate, ignore, warn) |

---

## Research Applications

### 1. Threat Modeling & Risk Assessment

**Research Questions:**
- How do different analyst perspectives (technical, human factors, controls) converge or diverge in risk assessment?
- What factors influence analysts' suspicion levels and response recommendations?
- How does team composition affect decision quality?

**Methodology:**
- Run multiple simulations varying analyst expertise
- Compare extracted risk assessments across conditions
- Measure consensus/divergence in recommendations

### 2. Training Effectiveness Evaluation

**Research Questions:**
- How does security training influence user vulnerability in simulated attacks?
- What psychological factors are most predictive of phishing susceptibility?
- Which training approaches are most effective for different user personas?

**Methodology:**
- Configure nested simulations with different user training levels
- Track click rates, reporting rates, and detection times
- Compare outcomes across training conditions

### 3. Defense-in-Depth Analysis

**Research Questions:**
- Which security controls (MFA, email filtering, SIEM) are most effective?
- How do layered defenses interact in preventing or mitigating attacks?
- What is the cost-benefit tradeoff of different security investments?

**Methodology:**
- Enable/disable controls across simulation runs
- Measure infection rate, detection time, and remediation cost
- Quantify marginal benefit of each control

### 4. Incident Response Planning

**Research Questions:**
- How do response timelines affect overall impact?
- What decision points are most critical in incident response?
- How can communication and coordination be improved?

**Methodology:**
- Vary response capabilities (24/7 SOC, automated containment, etc.)
- Measure impact of faster/slower response
- Identify bottlenecks in response process

---

## Quantitative Metrics

### From Nested Simulations

Each analyst's simulation generates:

- **Attack Success Rate:** Percentage of simulations where attacker achieves goals
- **Mean Time to Detection (MTTD):** Average time from click to detection
- **Mean Time to Containment (MTTC):** Average time to isolate threat
- **Compromise Extent:** Number of systems/accounts affected
- **Financial Impact:** Estimated cost of remediation and lost productivity

### Cross-Simulation Analysis

- **Analyst Agreement:** Inter-rater reliability of risk assessments
- **Decision Consistency:** Similarity of response recommendations
- **Confidence Calibration:** Accuracy of confidence vs. actual outcomes
- **Learning Curve:** Improvement across repeated simulations

---

## Extension Ideas

### 1. Multi-Stage Attack Chains

Add additional nested simulations modeling:
- **Reconnaissance:** Hacker researching targets
- **Lateral Movement:** Spreading through the network
- **Exfiltration:** Data theft and communication with C2 servers
- **Persistence:** Maintaining access after initial compromise

### 2. Social Engineering Variants

Create templates for:
- **Business Email Compromise (BEC):** Fake invoice scams
- **Vishing:** Voice phishing attacks
- **Smishing:** SMS-based phishing
- **Spear Phishing:** Highly targeted attacks

### 3. Organizational Context

Vary contextual factors:
- **Company Size:** Startup vs. enterprise
- **Industry:** Finance, healthcare, retail
- **Culture:** Security-conscious vs. security-fatigued
- **Budget:** Well-funded vs. resource-constrained

### 4. Adversary Profiles

Model different threat actor types:
- **Script Kiddies:** Opportunistic, low-skill attacks
- **Organized Crime:** Financial motivation, professional tactics
- **Advanced Persistent Threats (APTs):** State-sponsored, stealthy
- **Insider Threats:** Privileged access, unique challenges

---

## Connection to Real-World Practice

### Tabletop Exercises

This simulation formalizes the tabletop exercises conducted by real security teams:
- **NIST Cybersecurity Framework:** "Identify, Protect, Detect, Respond, Recover"
- **MITRE ATT&CK:** Tactic and technique simulation
- **ISO 27001:** Incident response testing requirements

### Red Team / Blue Team

- **Red Team:** Adversary simulation (hacker agents)
- **Blue Team:** Defense and response (IT security agents)
- **Purple Team:** Collaboration and knowledge sharing (analysts)

### Policy & Compliance

- **SOC 2 Trust Principles:** Security monitoring and incident response
- **PCI DSS:** Security awareness and phishing training requirements
- **GDPR:** Breach detection and reporting timelines

---

## Advantages Over Traditional Training

### Safe Environment

- **No Real Risk:** Simulations don't expose actual systems
- **Repeatable:** Can run same scenario multiple times
- **Ethical:** No deception of employees (unlike real phishing tests)

### Realistic Scenarios

- **Adversarial Modeling:** Agents simulate real attacker behavior
- **Time Pressure:** Captures stress and urgency
- **Complex Tradeoffs:** Multiple stakeholders with competing interests

### Quantifiable Outcomes

- **Metrics-Driven:** Generates numerical data for analysis
- **Comparative:** Can test different interventions
- **Publishable:** Suitable for research publications

---

## Running This Simulation

### Step-by-Step

1. **Load Template:** Simulation Builder → Research Studies → "Phishing Attack Simulation"
2. **Review Configuration:** 4 agents, 3 with nested simulations
3. **Set LLM Settings:** Gemini 2.0 Flash Exp recommended for speed
4. **Run Simulation:** ~25 steps for main discussion
5. **Analyze Results:** Review nested simulation outcomes and extraction summaries
6. **Compare Runs:** Vary configurations to test hypotheses

### Expected Runtime

- **Main Simulation:** 25 steps × ~30 seconds = ~12-15 minutes
- **Nested Simulations:** 3 analysts × 8 steps × ~20 seconds = ~8 minutes each
- **Total:** Approximately 35-45 minutes

### Analyzing Outputs

1. **Dashboard → Nested Simulations:** View extraction summaries
2. **Actions Tab:** Track analyst recommendations and CISO decision
3. **Natural Language Summary:** Get AI-generated overview of outcomes

---

## References & Further Reading

### Academic Research

- **M. S. Ahmed et al.** (2023). "Phishing Susceptibility: A Meta-Analysis of Cognitive and Psychological Factors." *Computers & Security*.
- **J. I. Silva et al.** (2022). "Tabletop Exercises for Cybersecurity Training: A Systematic Review." *IEEE Transactions on Education*.
- **K. K. Y. Chan & J. J. G. G.** (2021). "Red Teaming as a Learning Tool in Cybersecurity Education." *ACM SIGCSE*.

### Industry Frameworks

- **MITRE ATT&CK:** [https://attack.mitre.org/](https://attack.mitre.org/)
- **NIST Cybersecurity Framework:** [https://www.nist.gov/cyberframework](https://www.nist.gov/cyberframework)
- **SANS Institute:** Tabletop exercise resources and templates

### Concordia Documentation

- **Nested Simulations:** PhoneGameMaster pattern documentation
- **Component System:** Configuring agent capabilities
- **Extraction Prompts:** Designing effective summaries

---

## Citation

If you use this simulation template in research, please cite:

```bibtex
@misc{concordia-phishing-2025,
  title={Phishing Attack Simulation: Cybersecurity Tabletop Exercise},
  author={Concordia Simulation Builder},
  year={2025},
  url={https://github.com/ngstcf/concordia-sim-builder}
}
```

---

**Last Updated:** January 2025
**Concordia Version:** Based on Google DeepMind's Concordia framework
**Template Author:** Concordia Simulation Builder contributors
