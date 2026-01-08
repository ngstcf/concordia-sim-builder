## 1 Software Engineering Scenarios
Code Review Simulation
Scenario: A senior engineer is deciding whether to approve a PR with potential security issues. Main Simulation: Senior engineer reviewing a PR from a junior developer Nested Simulation: Simulate a conversation with the security team to understand the implications

Agent: Security Lead Sarah
Premise: "Should we approve this authentication code change?"
Nested Sim: Run a mini-simulation of a hacker trying to exploit both old and new auth
Result: "New code has 47% fewer attack vectors, approve with minor changes"

## 2. Sprint Planning Poker
Scenario: Tech lead estimating story points for a complex feature. Main Simulation: Team planning meeting discussing story complexity Nested Simulation: Each developer runs a mental simulation of implementing the feature

Agent: Senior Dev Mike
Nested Sim: "Mike simulates himself implementing the API integration"
Result: "Will take 3 days, needs refactoring of existing code first"

## 3. Incident Response Decision
Scenario: DevOps engineer deciding whether to roll back a deployment during an outage. Main Simulation: Incident response call with team Nested Simulation: "What happens if we rollback vs continue with hotfix?"

Agent: SRE Lead
Nested Sim: Simulate user impact for both scenarios over next 2 hours
Result: "Rollback causes 15min disruption, hotfix risks 45min more"
Cybersecurity Scenarios

## 4 Phishing Attack Simulation ⭐ RECOMMENDED
Scenario: Security analyst deciding whether a reported email is a targeted phishing attack. Main Simulation: Security team discussing suspicious email Nested Simulations: Each analyst simulates clicking different links/attachments

Agent: Analyst Chen
Goal: "Determine if this email is a spear-phishing attack"
Nested Sim: Simulate the outcome of clicking the attachment
  - Mini-sim with "hacker" agent and "victim" agent
  - Result: "Attachment drops ransomware, spreads in 3min"

## 5 Penetration Testing Strategy
Scenario: Red team member planning their approach to testing a bank's security. Main Simulation: Red team brainstorming attack vectors Nested Simulation: "Try a SQL injection on the login page"

Agent: Red Team Lead
Nested Sim: Simulate attempting SQL injection with different payloads
Result: "WAF blocks 80%, but time-based blind injection works"

## 6. Security Patch Priority
Scenario: CISO deciding which vulnerabilities to patch first with limited budget. Main Simulation: Executive meeting about security budget Nested Simulation: "Simulate a hacker exploiting each CVE"

Agent: CISO
Nested Sim: Run 5 mini-sims of hackers exploiting different CVEs
Result: "CVE-2024-1234 causes $2M loss in 2 days, prioritize it"

## 7 Research/Science Scenarios
Clinical Trial Design ⭐ RECOMMENDED
Scenario: Research scientist deciding on sample size for a drug trial. **Main Simulation: Research team planning a Phase III trial Nested Simulation: "Simulate the trial with 100 vs 500 vs 1000 participants"

Agent: Dr. Smith
Goal: "Determine optimal sample size to detect 20% effect"
Nested Sim: Run statistical simulation with different sample sizes
Result: "500 participants gives 80% power, 100 gives 40%"

## 8. Peer Review Decision
**Scenario: Journal editor deciding whether to accept a controversial paper. Main Simulation: Editorial board meeting Nested Simulation: "Simulate other researchers trying to reproduce the results"

Agent: Reviewer Jones
Nested Sim: Simulate 3 labs attempting to reproduce the experiment
Result: "2/3 labs fail to reproduce, recommend rejection"

## 9. Grant Proposal Review
Scenario: NSF panelist evaluating a research proposal. Main Simulation: Panel discussion about which proposals to fund Nested Simulation: "Simulate the research outcomes over 3 years"

Agent: Panelist Dr. Lee
Nested Sim: Simulate the research with different funding levels
Result: "With $500K, 70% chance of breakthrough, with $200K only 30%"

