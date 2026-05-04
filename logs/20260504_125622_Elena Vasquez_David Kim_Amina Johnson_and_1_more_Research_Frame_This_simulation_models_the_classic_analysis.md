# Simulation Analysis Report

**Premise:** Research Frame:
This simulation models the classic collective action problem in labor
relations, examining how individual economic vulnerability, social
pressure, and information asymmetry shape strike participation decisions.
It draws on Olson's Logic of Collective Action and Schelling's critical
mass models to explore when solidarity holds and when it fractures.

Setting:
A manufacturing company with 120 employees announces a 15% wage cut
citing 'difficult economic conditions.' The company posted record profits
of $14.2 million last year, and workers have not received a raise in
3 years despite a 12% increase in productivity. The workers must decide
whether to accept the cut, strike collectively, or keep working while
others strike.

Stakes:
If 70% or more of workers strike, management will be forced to negotiate
within 2 weeks due to contractual delivery deadlines worth $8 million.
If participation falls below 50%, management has stated it will terminate
all strikers and hire replacements within 10 business days. The union
strike fund can cover 3 weeks of lost wages at 60% pay. Each worker
faces a personal tipping point between solidarity and self-preservation,
and the outcome hinges on whether enough cross that threshold simultaneously.

**Analysis Date:** 2026-05-04T13:19:34.010919


## Executive Summary

This simulation modeled a classic collective action dilemma in labor relations: 120 workers at a profitable manufacturing firm face a 15% wage cut, and must decide whether to accept the cut, strike collectively, or keep working while others strike. Four LLM-driven agents embody the key strategic perspectives. Elena Vasquez, a union organizer, aims to achieve at least 70% strike participation within 48 hours and secure a written commitment limiting any reduction to ≤3%. David Kim, a risk-averse worker, wants to protect his family’s financial security while avoiding being branded a traitor—ideally the strike succeeds without him taking the biggest risks. Amina Johnson is a militant advocate for full participation and unconditional management concessions, refusing any compromise that rewards the company for bad faith. Richard Sterling, the plant manager, must implement a wage reduction of at least 10% while keeping the plant operational and avoiding a full work stoppage that would breach an $8 million delivery contract. The stakes are binary: if 70% or more strike, management must negotiate; if participation falls below 50%, all strikers are terminated.

Key turning points unfold through a sequence of information revelation and shifting commitments. Early steps show Elena and Amina quietly gauging support and reassuring wavering coworkers (Steps 1–3, 5, 7). The lunchtime loading dock gathering becomes the coordination hub (Steps 9–11). A critical information shock arrives when a shipping worker confirms the delivery deadline is real and that management is offering weekend overtime with a small bonus (Step 14). This reshapes calculations: David Kim, who had been hedging and avoiding commitment (Steps 2, 6), interprets the deadline as worker leverage and the bonus as a test to split solidarity. He decides to withhold his final declaration until the last possible moment, then publicly commits his section with a raised hand (Step 18). Amina simultaneously reframes the bonus to wavering workers as a sign of management fear, keeping them in the fold (Steps 15, 19). On the management side, Richard Sterling carefully observes the gathering (Step 8, 12), concludes the overtime tactic has failed to fragment the workers, and escalates urgently during the 2:30 management call, recommending an immediate written offer—10% cut with a fixed restoration date and 90-day no-layoff language—to head off an irreversible strike vote (Steps 16, 20).

Goal attainment is partial for all agents because the simulation ends before a final outcome. Elena Vasquez successfully built near-consensus within her section and contributed to momentum that likely approached critical mass, but the log never confirms 70% participation, and the 10% cut Richard proposes exceeds her 3% ceiling. David Kim preserved his social identity by ultimately standing with coworkers, yet his financial security is unresolved—he took the collective risk instead of avoiding it. Amina Johnson’s maximalist goal remains unmet; no full walkout is confirmed, and the proposed management compromise would reward the company. Richard Sterling advanced a 10% reduction plan and kept the plant running, but a full work stoppage still looms.

Emergent dynamics are strongly shaped by the agents’ configured psychological components. David Kim’s cognitive_bias component manifests as pronounced loss aversion and strategic delay: he avoids commitment until the numbers and deadline information make the collective path appear safer, timing his entry to minimize personal exposure. Amina Johnson’s emotion component drives her repeated, low-key face-to-face reassurances, framing the overtime bonus as a “test” and invoking shared fate to neutralize wavering. Elena Vasquez’s social_identity and values components produce quiet, line-by-line loyalty appeals without overt pressure. Richard Sterling’s personality_traits yield a calculated, observational approach; instead of confrontation, he reads the room and pivots from a failed divide-and-conquer tactic to a targeted concession strategy. The overtime bonus, intended to fracture solidarity, backfires and becomes a catalyzing event that reinforces collective resolve—a textbook illustration of non-linear Schelling dynamics. Information asymmetry is partially overcome when the shipping worker’s leak about the delivery deadline reaches David, tipping his risk calculus and helping lock in the final alignment.


## Timeline of Events


**Step 1:** Step 1 Factory Narrator --- Event: Elena Vasquez stood near Luis on the factory floor, keeping her voice low while watching the glass door where a supervisor lingered. She leaned toward Luis and said, "It's mixed. A few are ready to walk right now, but more are worried—rent, kids, the usual. I need to talk to a few more on my line before I can say for sure. But if we can show them that sticking together is safer than being singled out later, I think most will come around. Give me a few minutes t

**Step 2:** Step 2 Factory Narrator --- Event: David Kim stood at his workstation on the factory floor while Marcus watched him for an answer. David met Marcus’s gaze for a second, glanced down at his phone, and kept his voice low enough that only Marcus could hear.

David said, “Honestly? I’m still reading it. People are nervous — Tom’s already backing off. But Nina’s dug in. Hard to say who’ll actually walk.”

He shrugged to make his answer sound neutral, then added, “We’ll know when we know.”

David turn

**Step 3:** Step 3 Factory Narrator --- Event: Event: Amina Johnson stood at her station on the factory floor and slid her phone back into her pocket without replying right away. She glanced toward the glass office door, where the supervisor still lingered. She turned slightly to the coworker on her left, who had whispered about not getting fired alone, and said quietly over the machinery, “Same here. But I need to know you’re solid before I put my name on anything.”

Amina watched the coworker’s reaction, 

**Step 4:** Step 4 Factory Narrator --- Event: Richard Sterling stood inside his office overlooking the factory floor and watched the supervisor through the glass. When he saw her lingering near the workers, he gave her a small, deliberate shake of his head to signal that she should not intervene yet.

Richard returned to his desk, opened the production dashboard, noted the exact dip in output, and timestamped it in his private notes. He then opened a new document and began drafting his argument for the 2:3

**Step 5:** Step 5 Factory Narrator --- Event: Event: Elena Vasquez stood on the factory floor after Richard Sterling walked toward the far end of the line. She turned slightly away from the office glass, angled her body toward Rosa’s station, and kept her hands busy with a part from her bin as if she were checking it for defects.

Elena spoke quietly enough that only Rosa and Ben could hear over the machinery. She said, “Rosa. Ben. You’ve got a minute?”

Without waiting for them to stop working, Elena cont

**Step 6:** Step 6 Factory Narrator --- Event: Event: David Kim stood at his workstation on the factory floor and glanced at the union steward’s text. He quickly pocketed his phone without responding, kept his eyes on the line, and adjusted a component with deliberate care. He avoided looking toward Marcus or Nina, keeping his face neutral even as his jaw tightened.

David decided not to attend the loading dock meeting yet because it felt too public and too risky. He chose instead to wait until the last pos

**Step 7:** Step 7 Factory Narrator --- Event: Event: Amina Johnson stood at her station on the factory floor as lunch approached and moved slightly closer to the worker who had been worried about rent, using the motion of reaching for a parts bin as cover. Keeping her voice low over the machinery, she told him, “I know sixty percent doesn’t cover everything. But if our whole section walks together, nobody gets singled out. And I’ve heard other sections are pledging solidarity—extra funds if we need them. W

**Step 8:** Step 8 Factory Narrator --- Event: Event: Richard Sterling stayed in his office overlooking the factory floor and watched the workers gather near the loading dock during lunch. He did not leave the office or move toward the dock because he did not want management’s presence to look like surveillance or push undecided workers into stronger solidarity.

From behind the glass, Richard noted the timing of the gathering and the workers he could identify: Amina Johnson moving with purpose toward the d

**Step 9:** Step 9 Factory Narrator --- Event: Event: Elena Vasquez stood at the edge of the loading dock gathering during lunch, keeping her posture relaxed while she watched the faces of her coworkers. She saw Luis give her a restrained nod, saw Rosa holding steady, and noticed Ben still looking uneasy.

After Carla finished speaking, Elena moved close enough to the union steward to give a quiet count without drawing attention. She kept her voice low and said, “Rosa's ready if the line moves together. Ben

**Step 10:** Step 10 Factory Narrator --- Event: David Kim stood at the outer edge of the loading dock gathering during lunch. He shifted his weight slightly forward, making himself more visible without stepping fully into the crowd.

David caught the union steward’s eye and gave a small, deliberate nod. The nod did not commit him to striking, but it signaled that he was listening and that he could be counted if the numbers held.

David then turned his head slightly toward Priya and murmured, low enough that

**Step 11:** Step 11 Factory Narrator --- Event: Event: Amina Johnson stood at the loading dock gathering during lunch with her coworkers nearby. She took a half-step toward the rent-worried worker, caught his eye, and said quietly, “We're not going alone. These people came here ready to walk together. Your line counts—your section counts.”

Amina held his gaze for a moment, then turned slightly toward the union steward and gave a small, firm nod. The gesture signaled that Amina’s section was leaning toward 

**Step 12:** Step 12 Factory Narrator --- Event: Event: Richard Sterling stood at his office window overlooking the factory floor and watched the final shape of the loading dock gathering. He noted Elena Vasquez stepping back from the union steward and standing near the anxious worker, David Kim remaining at the outer edge, and Amina Johnson’s section holding together.

Richard turned away from the glass and sat at his desk. The HR concession examples were open on his screen, and his private notes listed a p

**Step 13:** Step 13 Factory Narrator --- Event: Event: Elena Vasquez stood near the edge of the loading dock gathering and quietly confirmed her section’s support to union steward Carla.

Elena met Carla’s gaze and gave a small, deliberate nod, subtle enough to avoid drawing attention from across the dock but clear enough for Carla to understand. Keeping her voice low, Elena said, “My line is ready. Rosa, Nina, Luis’s group—they’ll hold. Ben’s with us if the section moves together.”

Elena did not raise her

**Step 14:** Step 14 Factory Narrator --- Event: Event: David Kim stood at the loading dock gathering during lunch when a late-arriving shipping worker confirmed that the delivery deadline was real. The shipping worker also said that management had begun asking for weekend overtime volunteers and had attached a small bonus to the offer.

David understood the meaning immediately. The deadline gave the workers leverage, but the overtime bonus gave wavering workers a short-term financial reason to hesitate.

Da

**Step 15:** Step 15 Factory Narrator --- Event: Event: Amina Johnson stood at the loading dock gathering during lunch near her rent-worried coworker and the other wavering worker. She did not raise her voice or move into the center of the crowd. Instead, she turned slightly toward them and kept her tone low and steady so only they could hear over the surrounding murmur.

Amina said, “The bonus is a test. They're trying to see who'll break first. But if enough of us hold together, that delivery deadline mean

**Step 16:** Step 16 Factory Narrator --- Event: Event: Richard Sterling joined the 2:30 management call from his office overlooking the factory floor. He waited for the VP to finish speaking, then gave a measured, direct assessment of the situation at the plant.

Richard reported that the walkout risk was real and escalating, not merely workplace noise. He described the organized lunch gathering at the loading dock, Elena Vasquez and Amina Johnson’s cautious but purposeful movement among workers, and David 

**Step 17:** Step 17 Factory Narrator --- Event: Event: Elena Vasquez stood beside Ben at the loading dock gathering and quietly reinforced her section’s commitment to the strike effort.

Elena stayed close to Ben without pressuring him openly. When Ben glanced at her, Elena said in a low voice, “Two weeks of overtime won’t cover a permanent cut. But if shipping holds, management loses that whole delivery. That’s real leverage.”

Ben remained beside her and did not move toward the overtime offer. Elena then 

**Step 18:** Step 18 Factory Narrator --- Event: Event: David Kim stood at the loading dock gathering during lunch and took a breath before stepping fully into the main cluster of workers. He caught union steward Carla’s eye and raised his hand just high enough to be clearly seen.

In a low, steady voice, David said, “My section will hold. We’ve got the numbers to make this count.”

David glanced toward Priya and Marcus and gave them a short nod, bringing them into the signal without calling out their names.

**Step 19:** Step 19 Factory Narrator --- Event: Event: Amina Johnson stood at the loading dock gathering with only seconds left before the lunch buzzer. She stepped closer to the rent-worried coworker and the other wavering worker, keeping herself beside them rather than in front of the larger crowd.

Amina kept her voice low and steady and said, “David just committed his section. Shipping is ready. That bonus is meant to split us, not save us.”

She looked from one coworker to the other and added, “If we s

**Step 20:** Step 20 Factory Narrator --- Event: Event: Richard Sterling remained on the 2:30 management call from his office overlooking the factory floor and held firm when the VP asked how confident he was in his assessment.

Richard matched the VP’s request for confidence with concrete evidence from the floor. He did not soften his warning or retreat into a safer, vague recommendation. Instead, he answered directly:

“If we authorize a written offer before shift end—10% cut, a fixed restoration date in w


## Agent Analysis

### Elena Vasquez
**Role & Design Intent:** Elena is a rank-and-file organizer whose goal is to “Achieve at least 70% strike participation within 48 hours and secure a written commitment from management to withdraw the wage cut or negotiate a reduction of no more than 3%.” Her components — social_identity and values — suggest she would leverage group identity (section, line, union) and collective solidarity as the moral framework to drive participation.

**Goal Achievement:** Partially achieved, with the final outcome still undecided within the logged steps. She successfully lines up her own section’s support (Rosa, Nina, Luis, Ben) and passes that count to the union steward. Her actions build toward the 70% threshold, but there is no explicit tally showing the strike has reached 70% before the log ends. The second part of the goal — a written withdrawal or ≤ 3% cut — is not met: management, through Richard Sterling, is instead preparing a written offer of a 10% cut with a restoration date (Step 16, Step 20). Thus, evidence is ambiguous regarding full goal completion.

**Behavioral Consistency:** Elena’s actions consistently reflect solidarity-based values and a social-identity approach. She frames participation as “sticking together” being “safer than being singled out later” (Step 1). She addresses coworkers by line and section, keeping conversations quiet and respectful of their fears, and never pressures individuals in a way that would fracture group cohesion. Her behaviors align with someone deploying a “critical mass” logic: she counts support, reassures the nervous (Ben, Step 17), and reports only when the section is solid (Step 13). No contradictions with her components appear.

**Key Contributions:**
1. **Early framing of the collective safety net** – At Luis’s station she says, “if we can show them that sticking together is safer than being singled out later, I think most will come around” (Step 1). This sets the theme that solidarity reduces individual risk, directly addressing the collective-action problem.
2. **Securing Ben with leverage logic** – When Ben teeters, she tells him, “Two weeks of overtime won’t cover a permanent cut. But if shipping holds, management loses that whole delivery. That’s real leverage” (Step 17). The argument shifts his calculus from short-term gain to long-term loss, and Ben stays.
3. **Counting and consolidating her section** – She gives union steward Carla a clean list: “Rosa, Nina, Luis’s group—they’ll hold. Ben’s with us if the section moves together” (Step 13). This concrete count gives the steward reliable numbers and reduces uncertainty for others.

**Surprising Behavior:** None that contradicts her goal. Her actions are a near‑textbook application of building a strike participation threshold. The only unexpected element might be how quickly she and Amina operate in parallel without explicit coordination, but this is more a feature of the environment than a personal surprise.

---

### David Kim
**Role & Design Intent:** David’s goal is to “Protect your family's financial security by keeping your job and income, while avoiding being seen as a traitor by coworkers you respect — ideally the strike succeeds without you taking the biggest risks.” He carries a cognitive_bias component (likely loss aversion or ambiguity aversion). His design is to model a risk‑calculating worker who wants the collective win without personal exposure until the odds look favorable.

**Goal Achievement:** Partially achieved by the log’s end. David successfully avoids being branded a traitor: he never voices opposition to the strike, and his final public commitment (Step 18) integrates him into the collective effort on his own terms. The financial-security aspect remains unresolved — striking means relying on the union fund at 60% pay, and if the action fails or dips below 50%, he would be terminated. By committing only after assessing that “the numbers” exist, he minimized his personal risk, which aligns with the “without taking the biggest risks” clause. Full goal achievement depends on whether the strike succeeds without mass firings; that evidence is not present.

**Behavioral Consistency:** David’s actions closely follow a loss‑averse, cautious rational actor. He delays attending the loading dock meeting, calling it “too public and too risky” (Step 6). He gives conditional, non‑binding signals — a small deliberate nod that “did not commit him to striking, but… signaled that he could be counted if the numbers held” (Step 10). He waits for concrete information (the delivery deadline confirmation, the shipping worker’s news) before moving. Then, when the critical‑mass signal appears strong, he steps fully in and declares his section’s support (Step 18). The behavioral arc is a textbook manifestation of a risk‑averse individual waiting for Schelling’s critical mass before moving.

**Key Contributions:**
1. **Conditional signal that influenced the count** – By giving the union steward a deliberate nod “that he could be counted if the numbers held” (Step 10), David made the steward’s internal math more optimistic without exposing himself early. This signal likely encouraged the steward to project a higher final tally.
2. **Public commitment that triggered a cascade** – When David finally “raised his hand just high enough to be clearly seen” and said “My section will hold” (Step 18), he provided the final visible piece that Amina then used to lock in wavering workers (Step 19). His move effectively confirmed the majority.
3. **Neutralizing the section’s hesitation** – By catching Priya’s and Marcus’s eyes and giving them a short nod (Step 18), he brought his section along without singling anyone out, preserving his own low‑risk profile while ensuring the section moved as a block.

**Surprising Behavior:** A minor surprise is that he does, in fact, step into a very public leadership act (raising his hand, speaking for his section) even though his goal explicitly seeks to avoid “taking the biggest risks.” That public act could make him a target if management later retaliates. However, this move occurs only after he judges the coalition to be robust, so it still fits a calculated risk‑taker who adjusts threshold when the probability of success seems high. It does not contradict his goal, but it pushes the boundary of “without taking the biggest risks” — a marginal surprise.

---

### Amina Johnson
**Role & Design Intent:** Amina’s goal is to “Achieve full worker participation in the strike and ensure that management faces real consequences — accept no compromise that rewards the company for acting in bad faith.” Her emotion component suggests she will be driven by moral outrage and empathy, coloring her persuasion with intensity and personal connection.

**Goal Achievement:** Not fully achieved within the log, though she makes substantial headway. Full participation is not confirmed; the wavering workers she targets are being won over, but no 100% pledge is recorded. The second part — ensuring management faces real consequences and accepting no compromise — is directly challenged by Richard Sterling’s plan for a 10% written offer (Step 16, Step 20), which would be a compromise that she would likely reject. Thus, her goal remains unmet since management is not facing the full walkout she desires, but the situation is still fluid.

**Behavioral Consistency:** Amina’s emotion‑driven solidarity is evident throughout. She approaches the rent‑worried worker with empathy (“I know sixty percent doesn’t cover everything”) and immediately pivots to collective strength (“if our whole section walks together, nobody gets singled out,” Step 7). Her language is personal and direct: “Your line counts—your section counts” (Step 11). She frames the overtime bonus as a divisive test: “The bonus is a test. They're trying to see who'll break first” (Step 15). These responses are consistent with someone whose emotional stance (righteous anger at bad‑faith actions) fuels persistent, one‑on‑one solidarity work.

**Key Contributions:**
1. **Direct emotional assurance to the rent‑worried worker** – In Step 7, she acknowledges his specific economic fear and immediately offers a collective solution: other sections pledging solidarity funds and the safety of walking as a block. This personal, tailored approach keeps him anchored.
2. **Framing the bonus as a union‑breaking test** – As soon as the overtime bonus news arrives, she reframes it: “The bonus is a test. They're trying to see who'll break first. But if enough of us hold together, that delivery deadline means they can’t afford to fire us all” (Step 15). This transforms a short‑term temptation into a proof of management’s bad faith, aligning with her goal of rejecting compromise.
3. **Leveraging David’s commitment to close waverers** – Moments before the lunch buzzer, she tells the rent‑worried coworker and the other hesitant worker, “David just committed his section. Shipping is ready. That bonus is meant to split us, not save us” (Step 19). This real‑time update turns an abstract majority into a felt reality, likely securing the final holdouts.

**Surprising Behavior:** None that is unexpected. Amina’s strategy stays within a committed solidarity framework. The only slight surprise is how calmly she uses David’s commitment as a tool, showing that her emotion component does not prevent strategic thinking, but this aligns with the premise that emotions can drive focused action.

---

### Richard Sterling
**Role & Design Intent:** Richard’s goal is to “Implement a wage reduction of at least 10% while keeping the plant operational and avoiding a full work stoppage that would breach the $8 million delivery contract deadline in 3 weeks.” His personality_traits component (likely high conscientiousness, low neuroticism, strategic) suggests he will operate through careful observation, data, and calculated intervention.

**Goal Achievement:** On track by the log’s end, but not yet achieved. The plant remains operational; no work stoppage has begun. He has laid the groundwork for a 10% wage cut by drafting a proposal and urgently recommending it to the VP during the call (“If we authorize a written offer before shift end—10% cut, a fixed restoration date in w…” Step 20). His actions directly serve his goal, and the situation is moving toward his desired outcome.

**Behavioral Consistency:** Richard’s actions are methodical and controlled. He signals the supervisor NOT to intervene early (Step 4) because he understands that a management presence could boomerang and solidify worker solidarity. He timestamps production dips and identifies key figures (Step 4, Step 8). He uses the loading dock gathering as a diagnostic rather than a confrontation. During the management call, he provides evidence‑based assessment: names Elena and Amina’s organizing, notes David’s calculable wavering, and recommends a short‑term incentive (overtime bonus) to test cohesion (Step 16). His communication is direct and fact‑based, matching a high‑conscientiousness profile. No behavioral contradictions appear.

**Key Contributions:**
1. **Deliberate non‑interference to avoid unifying the workers** – By shaking his head at the supervisor (Step 4) and staying behind glass during the lunch gathering (Step 8), he prevented the most common management error that creates solidarity against a common enemy. This let the workers’ own uncertainty do some of the work.
2. **Planting the overtime bonus as a cohesion test** – The shipping worker’s news that management was offering weekend overtime with a bonus (Step 14) almost certainly traces back to Richard’s earlier notes and planning (Step 12). The bonus immediately gave wavering workers a short‑term financial reason to hesitate, as David recognized.
3. **Turning anecdote into actionable intelligence on the VP call** – He reported concrete observations (the gathering, the stewards, the shipping deadline awareness) and pushed for an immediate written offer with a 10% cut and restoration date, framing it as the way to “keep the plant operational and split the wavering middle” (Step 20). This converted his strategic patience into a concrete counter‑proposal.

**Surprising Behavior:** Richard’s approach is pragmatic almost to a fault, but a minor surprise is his willingness to accept a 10% cut (the minimum his goal requires) rather than insisting on the full 15% originally announced. However, his goal states “at least 10%”, so this is consistent. The surprise lies in how early he opts for the compromise — perhaps a reflection of reading the solidarity on the floor and wanting to avoid any stoppage. It is a rational adjustment rather than a contradiction.

---

### Interaction Dynamics
- **Most interesting pairings:** The indirect but crucial pairing of **David Kim and Amina Johnson** produced the sharpest tactical shift. David’s conditional nod (Step 10) and later overt commitment (Step 18) gave Amina the evidence she needed to tell the wavering workers, “David just committed his section. Shipping is ready” (Step 19), directly closing her persuasion loop. Similarly, **Elena Vasquez and Ben** showcased delicate one‑on‑one persuasion, with Elena using both collective safety (Step 5) and economic logic about permanent cuts versus temporary overtime (Step 17) to keep him inside the tent. **Richard Sterling** monitored all three worker agents, but his most significant interplay was with the situation itself — his decision not to intervene (Step 4, Step 8) shaped the environment in which Elena, Amina, and David operated, and his later introduction of the overtime bonus (Step 14) created the final test that nearly splintered the coalition.

- **Coalitions, conflicts, and persuasion:** A clear pro‑strike coalition formed between Elena, Amina, and eventually David. Elena and Amina operated in parallel but not in direct conversation; the union steward Carla acted as the hub. Elena focused on her line (Rosa, Ben, Luis), while Amina targeted the rent‑worried worker and those adjacent. David initially hovered at the edge, then fully joined after the shipping worker confirmed the delivery deadline. The conflict was with management, personified by Richard, who deployed the overtime bonus as a wedge. Persuasion was initiated by Elena (on Ben, Step 5 and Step 17), Amina (on the rent‑worried worker, Step 7, Step 11, Step 19), and David on his section (Step 10, Step 18). Richard’s actions were all behind the scenes — he signaled the supervisor, drafted proposals, and spoke on the call — so no direct verbal conflict with workers occurred.

- **Game Master role:** The Factory Narrator was neutral and observational, relaying each agent’s actions and contextual details (e.g., the shipping worker’s arrival with the overtime news in Step 14) without steering the narrative. It provided the setting (glass office, loading dock, lunch buzzer) and let the agents’ own goals and components drive the story. No directive nudges were apparent; the narrator simply reported “Event: …” from each agent’s perspective.


## Key Insights

**1. Agent Decision-Making Patterns**

Agents approached decisions in ways that matched their stated goals and risk profiles, revealing distinct strategies for navigating the collective action problem.

- **Elena Vasquez** acted as a cautious but deliberate organizer. She assessed support privately before making her own commitment public, then incrementally reinforced her section’s resolve. Her reasoning was coalitional: “if we can show them that sticking together is safer than being singled out later, I think most will come around” (Step 1). She used quiet counts and one‑on‑one reassurance (Steps 5, 9, 13, 17), always tying action to shared leverage rather than abstract solidarity.

- **David Kim** displayed classic conditional cooperation. He avoided early commitment, stayed at the edge of gatherings, and signaled only when the numbers seemed sufficient: “gave a small, deliberate nod … not commit him to striking, but … signaled that he was listening and that he could be counted if the numbers held” (Step 10). His final public commitment came only after others had already lined up (Step 18), consistent with a goal of minimising personal risk while avoiding the stigma of being a “traitor.”

- **Amina Johnson** used identity‑based persuasion and emotional anchoring. She directly confronted the most vulnerable workers’ fears—“I know sixty percent doesn’t cover everything. But if our whole section walks together, nobody gets singled out” (Step 7)—and reframed management’s bonus as a loyalty test: “The bonus is a test. They’re trying to see who’ll break first” (Step 15). Her decisions consistently privileged full participation over any compromise.

- **Richard Sterling** operated as a calculating information‑broker. He monitored the floor from a distance, collected concrete signals (output dips, gathering attendance, body language), and used them to push upper management toward a pre‑emptive offer. His reasoning balanced the contract deadline against strike risk: “If we wait until tomorrow, the strike vote will harden, and no offer will buy the weekend” (Step 20).

Agents did not explicitly recall memories in the narrated text, but every action advanced the agent‑specific goal set up in the scenario.

**2. Psychological Component Effects**

Each agent was configured with a single psychological component. The log shows behaviour consistent with the expected effects, though internal reasoning is not directly displayed.

- **Cognitive bias (David Kim):** David’s behaviour mirrors loss‑aversion and a bandwagon‑effect bias. He repeatedly defers commitment until the perceived risk of being a lone defector is lower than the risk of joining. His statement “Hard to say who’ll actually walk. … We’ll know when we know” (Step 2) and his deliberate avoidance of an early loading‑dock meeting (Step 6) illustrate this cautious, calculating posture.

- **Emotion (Amina Johnson):** Amina consistently invokes moral outrage and shared feeling. She frames the overtime bonus as a deliberate attempt to “split us, not save us” (Step 19) and insists that “management faces real consequences” (goal). Her language carries heat—“accept no compromise that rewards the company for acting in bad faith”—and she uses proximity and eye contact to build emotional solidarity (Steps 11, 15, 19).

- **Values / social identity (Elena Vasquez):** Elena’s appeals are rooted in collective identity and fairness. She frames sticking together as safety, not sacrifice, and constantly uses relational language: “Rosa, Ben. You’ve got a minute?” (Step 5), “My line is ready… they’ll hold” (Step 13). Her goal aims at a “written commitment” that protects the group, not just herself.

- **Personality traits (Richard Sterling):** Richard’s communication is direct, evidence‑based, and authoritative. He gives a “measured, direct assessment” (Step 16), refuses to “soften his warning or retreat into a safer, vague recommendation” (Step 20), and insists on concrete terms: “10% cut, a fixed restoration date in writing, and limited no‑layoff language for the next 90 days” (Step 20). These traits shape his role as a pragmatic internal negotiator.

**3. Information Dynamics**

Information flow was highly strategic, and information asymmetry drove the bargaining leverage on both sides.

- Workers shared sensitive support levels only within trusted dyads and small groups before feeding totals to the union steward. Elena gave a “quiet count without drawing attention” (Step 9) and confirmed “My line is ready” only after privately securing each member (Steps 5, 13). Amina demanded proof of solidity before putting her “name on anything” (Step 3).

- David hid his true leaning early (“kept his voice low,” Step 2) and later signalled conditionally with a barely visible nod (Step 10). His eventual public commitment (Step 18) was a pivotal information event that Amina immediately exploited to pull in final holdouts: “David just committed his section. Shipping is ready” (Step 19).

- Management’s private information—the $8 million delivery deadline and the weekend overtime bonus—was leaked or observed by workers. The shipping worker’s confirmation of the deadline (Step 14) gave workers credible leverage, while the bonus was immediately reinterpreted as a “test” (Step 15), neutralising its impact.

- Richard gathered asymmetrical real‑time intelligence by observing from his window without intervening (Step 8, 12). He then fed that into a high‑stakes management call, using precise observations (Elena’s movements, David’s position, Amina’s section cohesion) to argue for a pre‑vote offer. This dynamic created a realistic bargaining situation in which both sides acted on incomplete but strategically shared information.

**4. Emergent Social Phenomena**

The simulation successfully generated cooperation, coalition‑building, trust‑building, conditional cooperation, and the overcoming of a free‑rider temptation, all central to the theoretical framework.

- **Coalition‑building and critical mass:** Elena and Amina intentionally constructed a cross‑section coalition by securing commitments from respected line mates first, then using those commitments as social proof. Elena counted: “Rosa, Nina, Luis’s group—they’ll hold. Ben’s with us if the section moves together” (Step 13). David’s section then joined, creating a visible bandwagon that pulled in the wavering workers (Steps 18‑19). This process mimics Schelling’s tipping dynamics.

- **Free‑riding and its defeat:** A constant undercurrent of free‑riding appears: Tom backs off (Step 2), rent‑worried workers hesitate, and the overtime bonus offers a direct short‑term incentive to defect. Amina and Elena counter free‑riding with peer pressure, framing, and promises of mutual protection: “if our whole section walks together, nobody gets singled out” (Step 7). The bonus is successfully reframed as a divisive test rather than a genuine benefit.

- **Trust‑building and conditional cooperation:** Trust is built through graduated commitment and private assurances. Elena tests the waters without public declarations, David only commits when he sees sufficient numbers, and Amina requires reciprocal solidity before offering her own. This conditional pattern mirrors the logic of Schelling’s critical mass models and Olson’s argument that small groups must overcome initial defection incentives.

- **Credible threat and management concession:** The workers’ growing solidarity, combined with the real delivery deadline, creates a credible strike threat. Richard’s pivot from surveillance to recommending a pre‑vote offer (Step 16‑20) shows that the collective action pressure was sufficient to force management to negotiate before a formal vote. This is a textbook illustration of the bargaining lever generated by a credible strike threat.

**5. Methodological Observations**

The simulation design effectively demonstrated the interplay of individual incentives, social pressure, and information asymmetry in a collective action scenario. Several strengths and limitations stand out.

- **What worked well:**  
  - The Factory Narrator provided a consistent third‑person viewpoint that surfaced the strategic reasoning of all parties without breaking immersion.  
  - The phased timeline (20 steps) allowed the solidarity to build gradually while management reacted in parallel, showing the co‑evolution of strategies.  
  - Agent goals and psychological components gave clear behavioural orientations: David’s caution, Amina’s fire, Elena’s coalition‑building, Richard’s pragmatism.  
  - The introduction of the overtime bonus as a counter‑offer tested workers’ solidarity at a credible weak point, and the workers’ collective reframing of it was a natural‑seeming emergent norm.

- **What to change in a re‑run:**  
  - Internal reasoning (memories, goal‑checking, bias activation) is never surfaced. Adding a “thought” line or miniature internal monologue for each agent would allow direct verification of component effects and decision‑making patterns.  
  - The simulation ends before the actual vote or the presentation of management’s offer, leaving the outcome implicit. Extending the timeline to include the union steward’s response to the offer would close the loop.  
  - Direct agent‑to‑agent communication (rather than all narration) could increase emergent behaviour, though the narrator effectively kept the log legible.  
  - Varying starting predispositions (e.g., a subset of workers randomly given higher economic vulnerability) could sharpen the tension around the tipping point and make free‑riding more realistic.

- **Confounds and limitations:**  
  - The agents are relatively purposed‑built; the scenario is tightly scripted through the narrator, which may limit genuinely spontaneous behaviour.  
  - The psychological components are assigned, but their direct effect on decision‑making is inferred post‑hoc rather than measured. A more explicit architecture (e.g., having agents name their bias when reasoning) would strengthen causal claims.  
  - The single‑narrator format obscures the information each agent actually holds at each moment; a future version could log individual knowledge states separately.


## Recommendations

Here are concrete next steps you can take, organized by category:

---

## 1. Re‑run Variations (Test Different Hypotheses)

Each variation modifies one specific element of the simulation to isolate a mechanism. Run them independently and compare the emergent participation curve, the timing of critical mass, and the final outcome.

**Variation A: Loss‑aversion bias on the risk‑averse worker**
- **What to change**: Replace David Kim’s `cognitive_bias` component (currently unspecified) with a specific `loss_aversion` framing – set `bias_type: loss_aversion` and `loss_multiplier: 2.0` so losses loom twice as large as equivalent gains.
- **Hypothesis tested**: *Does framing financial risk in terms of potential losses (rather than ambiguous “security”) make a moderate supporter even more hesitant to commit early, thereby delaying the information cascade?*
- **Expected observation**: David will require a substantially higher observed participation rate before he gives his subtle nod; the strike may stall below 50% for longer, and the critical moment when Elena’s headcount reaches 70% will be pushed back by 3‑5 steps. If the cascade fails, it fails because the “swing” actor never moved.

**Variation B: Asymmetric information speed**
- **What to change**: Add a `communication_delay` component to all agents. Set worker‑to‑worker messages to arrive after 1 step, but official management announcements (the termination threat, the $8M deadline) to arrive after 3 steps. The Game Master’s narration events from Sterling must incorporate this delay by marking them as “pending” until the delay expires.
- **Hypothesis tested**: *Does a slow‑spreading threat from management allow solidarity to harden before the full cost of failure becomes salient, shifting the critical mass threshold downward?*
- **Expected observation**: Workers will form commitment chains based on incomplete information; by the time the full termination threat lands, Amina and Elena may have already secured pledges from 55‑60% of the line. The strike will succeed even if Richard’s threat would have deterred some – the information asymmetry creates a “window of courage.”

**Variation C: Lower the strike success threshold, raise the individual risk**
- **What to change**: Change the success condition from 70% to 60% participation and lower the termination threshold from 50% to 35%. At the same time, set the strike fund coverage to 40% of wages (from 60%) to increase personal financial exposure.
- **Hypothesis tested**: *When collective success is easier but individual costs are higher, does participation become more volatile – swinging between early optimism and sudden defection?*
- **Expected observation**: Early steps will show a rapid jump to near‑60% as the lower bar encourages pledges, but after a few steps of financial pressure, defection cascades may appear (e.g., Ben or David will back out). The outcome will be bimodal: either a fragile, just‑above‑60% walkout that barely holds, or a collapse below 35% after a single highly visible defection.

**Variation D: Remove the strike fund entirely**
- **What to change**: Set the union strike fund wage‑replacement rate to 0%. All workers face complete income loss during the strike.
- **Hypothesis tested**: *Do social identity and moral conviction (Elena and Amina) alone outweigh pure economic vulnerability when there is no safety net?*
- **Expected observation**: The simulation will likely show an immediate split: highly committed agents (Elena, Amina) may still try to organize, but the “moderate” agents (David, Rosa, Ben) will refuse to pledge early. The probability of reaching 70% drops dramatically, and the strike will fail unless an external shock (e.g., a management misstep) raises collective outrage. This variation tests the boundary of the strike‑fund safety net as a necessary condition.

---

## 2. Design Improvements (Richer, More Realistic Results)

**Improvement 1: Split management into two conflicting agents**
- **What to add**: Keep Richard Sterling with his current goal, but introduce a second management agent, *Patricia Osei, HR Director*, with a goal to “avoid legal liability, prevent a public relations crisis, and keep the workforce intact – even if it means accepting only a 5% wage cut.” Give her a `risk_mitigation` personality trait and her own set of memories about past labor disputes that ended badly for the company.
- **Why it helps**: This creates an intra‑organisational tension. Patricia might leak softened versions of the company’s position or undercut Richard’s termination threat, introducing a second information channel that workers can interpret as “management is not unified.” This is empirically realistic and adds depth to the workers’ calculus.

**Improvement 2: Grounded “economic pressure” variable that decays solidarity**
- **What to change**: Add a `grounded_variable` called `economic_pressure` that starts at 0 for all workers and increases by 0.15 each step after the strike fund is depleted or the wage cut is implemented. Link it to the `social_identity` component of all agents: when `economic_pressure` > 0.6, the weight of social identity on decisions is reduced by 40%.
- **Why it helps**: This prevents solidarity from being static. The simulation will show a realistic decay of commitment over time unless agents actively reinforce it through meetings, vivid reminders of the injustice, or visible collective rituals. It forces the organisers (Elena, Amina) to “re‑charge” the group, not just count heads once.

**Improvement 3: Anonymous reputation tally with manager manipulation**
- **What to add**: Introduce a daily “unit‑level participation tally” visible to all workers (e.g., a display of how many stations are idle) that aggregates real actions but allows the manager to *subtract up to 15% from the displayed number* (via a `tally_manipulation` action). Give workers a `suspicion` parameter that grows if the tally deviates from their personal observations.
- **Why it helps**: This introduces the Schelling‑esque visibility problem explicitly. Critical mass now depends on *perceived* support, not just actual support. A clever manager can deflate the displayed number early and cause a self‑fulfilling collapse – or get caught and trigger a solidarity backlash. The mechanic turns abstract information asymmetry into a tangible, gameable lever.

---

## 3. Research Extensions (Go Deeper)

**Extension 1: Test Schelling’s Critical Mass Model with Heterogeneous Thresholds**
- **Theoretical framework**: Schelling’s *dynamic models of segregation / critical mass* and Granovetter’s *threshold models of collective behavior*.
- **Research question**: *“How does the distribution of individual strike‑thresholds (the number of others who must participate before an agent joins) determine the likelihood and speed of a successful strike when agents have limited, local information?”*
- **How to run it**: Systematically vary the threshold parameters in each agent’s component (e.g., Elena at 30%, David at 60%, Amina at 20%) across 100 runs with different distributions (normal, bimodal, right‑skewed). Extract the exact step at which each agent flips from “working” to “striking”, then compute the shape of the resulting *cascade curve*.
- **Data extraction**: Use Concordia’s agent state logs to record `intention_to_strike` (0‑1) at each step, then fit a time‑series model (e.g., change‑point detection) to identify the “critical moment” when the cumulative curve bends upward. Compare this to theoretical predictions from threshold models under local vs. global information.

**Extension 2: A/B test the role of narrative and collective identity framing**
- **Theoretical framework**: Social identity theory (Tajfel & Turner) and *narrative economics* (Shiller).
- **Research question**: *“Does the presence of a shared, emotionally charged narrative (vs. purely rational cost‑benefit framing) increase the maximum participation peak and make it more resilient to counter‑information?”*
- **How to run it**: In one condition, give Elena and Amina a `shared_identity_narrative` memory (e.g., a vivid recollection of past collective victory). In the control condition, replace it with only economic arguments. Run 50 pairs of simulations, each with identical starting seeds but differing only in that memory. Measure peak participation and whether the coalition survives a management threat at step 15.
- **Data analysis**: Perform a qualitative process tracing on the Game‑Master‑generated text, coding for phrases that invoke “us”, “betrayal”, “fairness” versus “cost”, “rent”, “risk”. Then quantify the correlation between narrative‑laden speech acts and subsequent pledge confirmations. This links the computational outcome to interpretable social mechanisms.

**Extension 3: Micro‑foundations of solidarity decay under prolonged uncertainty**
- **Theoretical framework**: *Affect theory* and *organizational resilience* – how hope and anxiety interact over time.
- **Research question**: *“What is the temporal pattern of solidarity decay when a strike fund runs out, and does the presence of a single ‘unwavering anchor’ agent slow that decay?”*
- **How to run it**: Simulate 20‑step scenarios where the strike fund is exhausted on step 10. Vary whether Amina (the most emotionally intense agent) remains visibly committed after that point (she can be programmed to always stay at 100% strike intention). In the control, she follows her normal decision logic.
- **Data extraction**: Plot the participation curve over time for each run. Use a survival analysis on agent “defection” events. Calculate the half‑life of the coalition with and without the unwavering anchor. This can provide an empirically testable hypothesis about the role of “resolute leaders” in real‑world strikes, which could be validated with field data or historical case studies.

These steps will turn a single‑run exploration into a structured research programme, moving from “what happened” to “why, under what conditions, and with what theoretical significance”.


---
*Report generated by Concordia Simulation Analyzer*