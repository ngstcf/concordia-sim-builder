# Simulation Analysis Report

**Premise:** A coastal town of 4,200 residents receives an urgent flood warning:
a Category 3 storm surge is expected within 12 hours, with water levels
projected at 8 feet above normal high tide. The National Weather Service
has upgraded the warning twice in the past 6 hours, and county authorities
have issued a mandatory evacuation order effective immediately.

However, institutional trust is severely compromised. In the past 3 years,
the town has experienced 2 false evacuation orders, and a 2024 FEMA audit
criticized the county's emergency communication infrastructure. Trust in
government warnings stands at 38% according to a recent community survey.

The town's 3 emergency shelters can accommodate approximately 2,500 people
(60% of the population). The single evacuation highway (Route 17) is
already at 70% capacity. Cell tower coverage is intermittent due to
preliminary storm bands. Social networks, community leadership, and
informal communication channels will determine who reaches safety in time.

Stakes: Based on storm surge modeling, residents who remain in flood zones
face a 35% probability of life-threatening conditions. The 12-hour window
is shrinking as the storm accelerates.

**Analysis Date:** 2026-05-05T23:46:57.931775


## Executive Summary

The simulation modeled a 4,200-person coastal town facing a mandatory evacuation after a Category 3 storm-surge warning, with only 12 hours before projected 8-foot water levels and a history of false alarms and low institutional trust. The five agents represented different social nodes in the evacuation network: Sarah Williams aimed for townwide 90% compliance and protection of vulnerable residents; Robert Thompson prioritized evacuating his household and confirming neighbors had plans; Javier Rodriguez sought an informed evacuation decision while protecting his store/community; Eleanor O’Brien needed accessible evacuation with medications/equipment; and Pastor Moses sought to mobilize 35 vulnerable congregants, 8 carpool vehicles, and the church as a gathering point. The stakes remained high throughout: Route 17 was already congested, shelter capacity was limited, communications were unreliable, and residents remaining in flood zones faced a stated 35% chance of life-threatening conditions.

The major turning points were local and trust-based rather than institutional. In Steps 1–5, all agents began immediate persuasion or mobilization: Sarah packed and checked on skeptical neighbors, Robert canvassed nearby households, Javier warned customers in his store, Eleanor addressed anxious people at the community center, and Pastor Moses opened the church and spoke to a hesitant congregation. Step 6 showed Pastor Moses directly confronting distrust caused by prior false alarms, while Step 7 showed Sarah making a personalized appeal to Mr. Nguyen; by Step 9 and Step 11, the Nguyens had gathered documents and were loaded into Sarah’s car, marking one concrete vulnerable-household evacuation in progress. Step 12 and Step 13 shifted from persuasion to logistics, with Pastor Moses asking Deacon Frances for ride/vehicle counts and Eleanor identifying seven people needing accessible transport. Step 14 was a risky decision point: Javier, already in stalled Route 17 traffic, chose to turn back toward Bayside Flats to check on others rather than continue evacuating. Step 15 showed Robert also diverting from his own progress to help a stranded minivan, further illustrating how congestion and roadside failures complicated evacuation.

Goal attainment was mostly partial and not fully verifiable from the log. Sarah partially achieved her vulnerable-population objective by persuading and transporting the Nguyen couple, but there is no evidence she coordinated “all available communication channels and transportation resources,” reached 90% evacuation compliance, or verified zero fatalities. Robert partially met his goal: he canvassed at least the Williams and Johnson households, left a note for the Johnsons, entered Route 17 traffic, and assisted another evacuee, but the log does not confirm that his own household evacuated within 2 hours or that three neighboring households had both received the warning and secured transportation plans. Javier warned customers and began evacuating with Miguel, but the log does not show him consulting three independent information sources or securing his property; his return toward Bayside Flats may support his community-protection values but delays evacuation. Eleanor organized accessible-transport information and identified seven people needing rides, but the log does not confirm that she personally secured accessible shelter transport or safely transported her medications and medical equipment. Pastor Moses clearly opened the church as a gathering point and began mobilizing volunteers, but the log does not confirm that all 35 vulnerable congregants were accounted for or that 8 vehicles were secured.

Several emergent dynamics are visible. Because government trust was low, agents relied on informal networks: Sarah used neighborly persuasion, Pastor Moses leveraged religious/community authority, Eleanor coordinated through the community center, and Robert acted as a mobile neighborhood helper. No betrayals occurred; instead, the simulation produced altruistic spillover, with Robert helping a stranded stranger in Step 15 and Javier turning back in Step 14 despite personal risk. The configured psychological components were plausibly reflected: Pastor Moses’s values appeared in his appeals to collective responsibility; Eleanor’s emotion component appeared in her calm but urgent crowd management; Javier’s values and possible cognitive bias appeared in his decision to prioritize checking on Bayside Flats over continuing evacuation; and Sarah’s theory-of-planned-behavior framing appeared in her effort to reduce skepticism and increase perceived ability to evacuate. Observation-action coherence was generally strong, but there are ambiguities: Robert’s Step 8 observation includes information about Sarah at the Nguyen doorway that he may not have directly perceived, while the corresponding event says Sarah was not at her house. The log is also truncated in multiple places, so some outcomes—especially household confirmations, vehicle counts, shelter arrival, and final evacuation compliance—remain unresolved.


## Timeline of Events


**Step 1:** Step 1 Emergency Dispatch --- Event: Sarah Williams finished packing her go-bag at 6:50 AM, adding essential medications, a battery-powered phone charger, and a weather radio. She stepped outside into the humid air and surveyed her neighborhood. Noticing that her neighbor Dale remained skeptical of the evacuation order, she felt frustrated but moved on. She looked across the street at the Nguyen family's house and saw no signs of activity. Concerned for the elderly couple's safety and mobility, 

**Step 2:** Step 2 Emergency Dispatch --- Event: Robert Thompson stepped out of his idling truck and onto his street at approximately 6:50 AM, resolved to canvass his neighborhood before thinking of his own evacuation. He walked to the house next door, where the Williams family lived — a household with two young children and no vehicle of their own — and knocked firmly on the door. When Mrs. Williams answered, Robert said, "Annie, I need to talk to you for a minute. Have you heard about the evacuation?" She

**Step 3:** Step 3 Emergency Dispatch --- Event: Event: Javier Rodriguez addressed the three customers in his store at approximately 6:50 AM, telling them: "Hey everyone, I need you to listen carefully. A mandatory evacuation order is in effect due to the storm, and you need to leave now. I know it feels like just another day, but this is serious. The roads are already backed up, and it's only going to get worse. I can help you find what you need quickly." He moved behind the counter, gathered bottled water

**Step 4:** Step 4 Emergency Dispatch --- Event: Event: Eleanor O'Brien stood before the anxious crowd gathered at the community center and addressed them directly: "Everyone, listen up! This is a real evacuation, and we need to move now. I understand many of you are hesitant, but the storm has intensified, and we could be in serious danger if we stay here. I urge you to consider your safety and the safety of your families." She made eye contact with a woman who had asked about the evacuation and nodded emp

**Step 5:** Step 5 Emergency Dispatch --- Event: **Event:** Pastor Moses stepped forward before his congregation at approximately 7:00 AM and addressed the room directly: "Brothers and sisters, we are facing a serious storm, and I want each of you to understand the importance of taking this evacuation order seriously. I know many of you have concerns after the false alarms we experienced before. But right now, our safety must come first. I am here to help you." He gestured toward the open church doors and a

**Step 6:** Step 6 Emergency Dispatch --- Event: Event: Pastor Moses stepped down from the raised platform at the front of the church and addressed his divided congregation directly. He began: "Brothers and sisters, I understand your fear and skepticism. Last year, we faced storms that didn't bring the devastation we anticipated, and I know many of you are feeling uncertain about leaving your homes again. But I need you to remember this: the warnings we receive come from those who want to protect us. This s

**Step 7:** Step 7 Emergency Dispatch --- Event: Event: Sarah Williams stood on the Nguyen family's front porch and addressed Mr. Nguyen directly, looking him in the eyes: "Mr. Nguyen, I understand your doubts. I really do. I felt the same way the last two times. But this storm feels different, and the weather service is taking it seriously. I don't want anything to happen to you or Mrs. Nguyen."

She glanced toward Mrs. Nguyen, who watched from inside with visible concern, then continued: "I want to help y

**Step 8:** Step 8 Emergency Dispatch --- Event: ## 7:50 AM — Robert Thompson's Neighborhood

Robert Thompson drove his truck to the Williams house, tapped the horn lightly, rolled down his window, and called out: "Sarah! Do you have time to load up? I can take your family in my truck, but we need to move fast!"

Sarah Williams was not there. She had left nearly an hour earlier to help the Nguyen family across the street and had not returned. Her front door stood ajar, a forgotten umbrella sat on the porch,

**Step 9:** Step 9 Emergency Dispatch --- Event: Event: Sarah Williams retrieved her go-bag from the Nguyen family's porch and re-entered the house. She took the manila envelope from Mr. Nguyen's hands and said: "That's great, Mr. Nguyen. You've done well to get these." She placed her hand on Mrs. Nguyen's shoulder and said: "Mrs. Nguyen, we need to move quickly now. I'll help you get anything else you want to take. We can rip through this so we can get to my car while it's still safe." Sarah took the famil

**Step 10:** Step 10 Emergency Dispatch --- Event: ## 8:00 AM — Robert Thompson's Neighborhood

Robert Thompson pulled a piece of paper and a pen from his truck's glove compartment and wrote: *"Mr. and Mrs. Johnson, if you need help evacuating and see this note, please call me on my CB radio or head to the diner. I tried reaching you. Please stay safe!"* He walked back to the Johnsons' front door and taped the note at eye level where it could not be missed.

He returned to his truck, started the engine, and 

**Step 11:** Step 11 Emergency Dispatch --- Event: ## 8:00 AM — Sarah Williams's Street

Sarah Williams secured Mrs. Nguyen in the backseat of her car, placing the cane within easy reach, and said softly: "We're going to get you both to safety. Just a little longer, I promise." She then helped Mr. Nguyen into the front passenger seat and made sure the manila envelope of documents remained in his lap.

Sarah got into the driver's seat. The wind had picked up noticeably, gusting through the trees, and the sky 

**Step 12:** Step 12 Emergency Dispatch --- Event: ## 8:05 AM — First Baptist Church

Pastor Moses stepped forward before his congregation and said: "Thank you all for coming. We're in a critical moment, and your commitment to each other is making a real difference. But we still have work to do."

He called Deacon Frances to his side and asked her directly: "Frances, how many still need rides, and which vehicles do we have committed?" Deacon Frances reported the current numbers. Pastor Moses took a deep brea

**Step 13:** Step 13 Emergency Dispatch --- Event: ## 8:05 AM — Millfield Community Center

Eleanor O'Brien stood at the center of the crowded community center hall and took stock of the situation. She scanned the sign-up sheet Marcus had been maintaining and counted seven names requiring accessible transport.

She turned to Marcus and said: "Marcus, can you get a headcount of those left who need rides once you're off the call?" She gestured to nearby volunteers and directed them to help gather bags and nece

**Step 14:** Step 14 Emergency Dispatch --- Event: ## 8:05 AM — Route 17 Evacuation Route, Near Bayside Flats

Javier Rodriguez sat in his truck in stalled evacuation traffic on Route 17, Miguel in the passenger seat beside him. He studied the congestion ahead, identified the side street turnoff leading back toward Bayside Flats, and made his decision.

He turned to Miguel and said: "Miguel, I think we need to try the side street back into Bayside Flats. We can't leave until we're sure everyone is safe. I ne

**Step 15:** Step 15 Emergency Dispatch --- Event: ## 8:10 AM — Route 17, Evacuation Traffic

Robert Thompson sat in his truck in stalled evacuation traffic on Route 17, watching the line of vehicles barely inch forward. Ahead, a minivan sat on the shoulder with its hazard lights flashing and a woman standing at the front, peering under the open hood.

Robert pulled his truck out of the crawling lane and eased toward the shoulder. He rolled down his window and called out: "Do you need some help?"

The woman 


## Agent Analysis

## Sarah Williams

**Role & Design Intent:**  
Sarah was designed as a high-level evacuation compliance coordinator: her goal was to “**Achieve at least 90% evacuation compliance within 8 hours by coordinating all available communication channels and transportation resources, with zero fatalities among identified vulnerable populations**.” Her `theory_of_planned_behavior` component suggests she was intended to influence people’s attitudes, perceived risk, and perceived ability to evacuate.

**Goal Achievement:**  
Not achieved based on available evidence, though she made meaningful progress with one vulnerable household.

- She did assist an elderly couple, the Nguyens: she noticed “no signs of activity” at their house and was “concerned for the elderly couple’s safety and mobility” in Step 1.
- She persuaded Mr. Nguyen by acknowledging prior false alarms: “**I understand your doubts. I really do. I felt the same way the last two times. But this storm feels different**” in Step 7.
- She physically evacuated them: at 8:00 AM she “**secured Mrs. Nguyen in the backseat of her car**,” helped Mr. Nguyen into the front passenger seat, and ensured their documents stayed with them in Step 11.

However, there is no evidence she coordinated “all available communication channels and transportation resources,” no evidence of town-wide evacuation compliance approaching 90%, and no final fatality outcome is provided. Her actions were household-level rather than system-level.

**Observation Quality:**  
Her observations were locally accurate but narrow.

- She correctly observed neighborhood risk signals: Dale remained skeptical, and the Nguyen house showed “no signs of activity” in Step 1.
- She perceived Mr. Nguyen’s doubts and Mrs. Nguyen’s concern, which guided her persuasion in Steps 7 and 9.
- She accurately tracked practical evacuation needs: documents, Mrs. Nguyen’s cane, and getting both Nguyens into the vehicle in Steps 9 and 11.

She missed or did not act on broader coordination information. For example, Robert later came looking for Sarah at the Williams house and found she was gone, with “her front door stood ajar” in Step 8. Sarah’s own observations do not show awareness of Robert’s attempted coordination or of her own household’s status.

**Behavioral Consistency:**  
Her behavior was consistent with `theory_of_planned_behavior`.

- She addressed attitude and distrust by validating Mr. Nguyen’s skepticism about past false alarms: “**I felt the same way the last two times**” in Step 7.
- She increased perceived behavioral control by offering concrete help: “**I want to help you**” in Step 7 and then actively helped gather items and load the car in Steps 9 and 11.
- She used interpersonal trust and reassurance: she placed a hand on Mrs. Nguyen’s shoulder and said, “**We need to move quickly now**” in Step 9, then reassured her, “**We’re going to get you both to safety**” in Step 11.

The memory contents are not provided, only that she had 8 memories, so consistency with specific memories cannot be assessed.

**Key Contributions:**

1. Identified an at-risk elderly household with mobility concerns: the Nguyen house had “no signs of activity,” and she was “concerned for the elderly couple’s safety and mobility” in Step 1.
2. Persuaded a skeptical resident using empathy and urgency: “**I understand your doubts… But this storm feels different**” in Step 7.
3. Converted persuasion into physical evacuation by loading Mrs. Nguyen, Mr. Nguyen, the cane, and documents into her car in Step 11.

**Surprising Behavior:**  
Her goal was broad and institutional — 90% compliance, communication channels, transportation resources — but her actual behavior became intensely local and individualized. She also “moved on” after noticing Dale remained skeptical in Step 1, which is surprising given her compliance-focused goal. The log does not show her returning to persuade Dale or coordinating with Robert, Pastor Moses, Eleanor, or county systems.

---

## Robert Thompson

**Role & Design Intent:**  
Robert was designed as a neighborhood-level evacuation helper. His goal was to “**Evacuate your household within 2 hours and personally confirm that at least 3 neighboring households have received the warning and have a transportation plan**.” He had no listed psychological components, so his role appears practical and community-oriented.

**Goal Achievement:**  
Partially achieved at best; likely not achieved based on the evidence.

- He began canvassing immediately: at 6:50 AM he stepped out of his idling truck and went to the Williams house, described as “a household with two young children and no vehicle of their own,” in Step 2.
- He later tried to assist Sarah/Williams household again: at 7:50 AM he drove to the Williams house and called, “**Sarah! Do you have time to load up? I can take your family in my truck, but we need to move fast!**” in Step 8.
- He attempted to reach the Johnsons, but only left a note: “**if you need help evacuating and see this note, please call me on my CB radio or head to the diner**” in Step 10.

The goal required him to personally confirm at least 3 neighboring households had received the warning and had transportation plans. The log shows attempts, but not three confirmations. His own household evacuation is also not clearly evidenced; by 8:10 AM he was in traffic on Route 17 in his truck, but the log does not state that his household was with him in Step 15.

**Observation Quality:**  
His observations captured immediate neighborhood and route conditions, but he missed confirmation opportunities.

- He perceived urgency early: houses were still illuminated, and he felt he “cannot wait for people to come to their senses” in Observation Step 2.
- He observed Sarah’s absence from the Williams house and signs of rushed departure: “front door stood ajar” and “a forgotten umbrella sat on the porch” in Step 8.
- He correctly perceived deteriorating evacuation conditions: traffic “barely inch[ed] forward” on Route 17, and he noticed a disabled minivan on the shoulder in Step 15.

However, his Johnson action did not meet the confirmation standard. Leaving a note in Step 10 was useful, but it did not confirm receipt of warning or transportation plans.

**Behavioral Consistency:**  
With no special components listed, Robert behaved consistently with a practical, prosocial neighbor role.

- He prioritized neighbors before himself: he “resolved to canvass his neighborhood before thinking of his own evacuation” in Step 2.
- He offered direct transport to a household without a vehicle in Step 8.
- He continued helping even while evacuating, stopping for a disabled minivan in Step 15.

The memory contents are not provided, so memory consistency cannot be assessed beyond his stated goal.

**Key Contributions:**

1. Identified and attempted to help a vehicle-less household: the Williams family had “two young children and no vehicle of their own,” and Robert knocked on their door in Step 2.
2. Offered evacuation transport directly: “**I can take your family in my truck, but we need to move fast!**” in Step 8.
3. Responded to emergent roadside need by pulling toward the shoulder and asking the stranded woman, “**Do you need some help?**” in Step 15.

**Surprising Behavior:**  
Robert’s helpfulness may have undermined his formal goal. Instead of securing three confirmed household plans and evacuating his own household within 2 hours, he left a note for the Johnsons in Step 10 and then diverted to help a disabled minivan in Step 15. Those actions were compassionate but created goal slippage.

---

## Javier Rodriguez

**Role & Design Intent:**  
Javier was designed as a cautious decision-maker balancing evidence, property, and community obligations. His goal was to “**Make a fully informed evacuation decision within 4 hours by gathering at least 3 independent information sources, and if you decide to evacuate, secure your property before leaving**.” He had `cognitive_bias` and `values` components, suggesting his decisions were expected to be shaped by both biases and moral priorities.

**Goal Achievement:**  
Not achieved based on the log.

- There is no evidence he gathered “at least 3 independent information sources.”
- He did act on the evacuation order and warned others: at 6:50 AM he told customers, “**A mandatory evacuation order is in effect due to the storm, and you need to leave now**” in Step 3.
- He was on Route 17 by 8:05 AM with Miguel in the passenger seat, indicating he had begun evacuating or moving toward evacuation in Step 14.
- There is no evidence he secured his property before leaving.
- At 8:05 AM he decided to turn back toward Bayside Flats, saying, “**We can’t leave until we’re sure everyone is safe**” in Step 14, which further delays his own evacuation decision.

**Observation Quality:**  
His observations captured urgency and local conditions but did not reflect his information-gathering goal.

- He noticed “the familiar faces of his neighbors” in the store and realized he “must act decisively” in Observation Step 3.
- On Route 17, he perceived “stalled evacuation traffic” and identified “the side street turnoff leading back toward Bayside Flats” in Step 14.
- He was aware of “the evacuation traffic becoming increasingly chaotic” and that “time is not on their side” in Observation Step 14.

However, the observations do not show him evaluating three independent sources, comparing forecasts, checking official channels, or verifying storm surge details. His perception became urgency-driven rather than evidence-gathering-driven.

**Behavioral Consistency:**  
His `values` component is clearly visible; the `cognitive_bias` component is harder to assess because the specific bias is not named.

- Values guided his conduct toward customers: he told them to leave, gathered bottled water, and tried to help them get what they needed quickly in Step 3.
- Values also guided his decision to turn back: “**We can’t leave until we’re sure everyone is safe**” in Step 14.
- If a cognitive bias was intended, the log does not identify which one. His turn back toward Bayside Flats despite storm danger could reflect a bias toward protecting familiar community members or avoiding guilt, but the evidence is insufficient to label a specific bias.

The memory contents are not provided, so memory consistency cannot be assessed.

**Key Contributions:**

1. Used his store as an information and supply point: he warned three customers of the mandatory evacuation and gathered bottled water in Step 3.
2. Communicated urgency despite public complacency: “**I know it feels like just another day, but this is serious**” in Step 3.
3. Chose community verification over personal evacuation progress: “**We can’t leave until we’re sure everyone is safe**” in Step 14.

**Surprising Behavior:**  
Javier’s stated goal emphasized informed decision-making and property security, but his actions quickly became altruistic and improvisational. The most surprising move was deciding to leave stalled evacuation traffic and return toward Bayside Flats in Step 14, despite the premise that flood-zone residents face a “35% probability of life-threatening conditions” if they remain.

---

## Eleanor O’Brien

**Role & Design Intent:**  
Eleanor was designed as a vulnerable resident needing accessible evacuation support. Her goal was to “**Secure assisted transportation to an accessible shelter within 6 hours while ensuring your critical medications and medical equipment are transported safely**.” Her `emotion` component suggests anxiety, fear, urgency, or concern should shape her responses.

**Goal Achievement:**  
Partially achieved or in progress, but not completed in the log.

- She took leadership at the community center, telling the crowd, “**This is a real evacuation, and we need to move now**” in Step 4.
- At 8:05 AM she counted “seven names requiring accessible transport” on the sign-up sheet in Step 13.
- She asked Marcus to get “a headcount of those left who need rides” and directed volunteers to help gather bags and necessities in Step 13.

However, the goal required her to secure assisted transportation to an accessible shelter and ensure her critical medications and medical equipment were transported safely. The log does not show that transportation was actually secured, that she reached an accessible shelter, or that her own medications/equipment were loaded.

**Observation Quality:**  
Her observations were accurate and socially attuned.

- She perceived “the anxious crowd gathered at the community center” in Step 4.
- She recalibrated her focus “amidst the growing anxiety around her” in Observation Step 4.
- She accurately identified a key operational need: “seven names requiring accessible transport” in Step 13.

Her main observational gap is personal: the log does not show her checking her own medications or medical equipment, even though those were central to her goal.

**Behavioral Consistency:**  
Her `emotion` component appears to color her behavior, but she channels emotion into organized action rather than panic.

- She “takes a deep breath” and “recalibrat[es] her focus” in Observation Step 4.
- Her tone is “firm yet reassuring” in Observation Step 4.
- At 8:05 AM she again “takes a deep breath” under urgency and scans the sign-up sheet in Observation Step 13.

Her emotion manifests as controlled anxiety and protective urgency. The memory contents are not provided, so specific memory consistency cannot be assessed.

**Key Contributions:**

1. Reframed the evacuation as real and immediate: “**This is a real evacuation, and we need to move now**” in Step 4.
2. Identified a concrete accessibility bottleneck: seven people required accessible transport in Step 13.
3. Mobilized support roles by asking Marcus for a headcount and directing volunteers to gather bags and necessities in Step 13.

**Surprising Behavior:**  
Eleanor’s stated goal was personal survival with assisted transport and medical equipment, but she acted more like an evacuation coordinator for others at the community center. This was prosocial and useful, but it leaves her own transport and medical-equipment security unresolved in the log.

---

## Pastor Moses

**Role & Design Intent:**  
Pastor Moses was designed as a trusted community leader whose values could overcome institutional distrust. His goal was to “**Personally account for all 35 vulnerable congregation members within 6 hours, organize at least 8 volunteer carpool vehicles, and open the church as a secondary gathering point before Route 17 becomes impassable**.” His `values` component suggests moral responsibility, faith, service, and communal care should guide his actions.

**Goal Achievement:**  
Partially achieved or in progress; the full goal is not evidenced.

- He opened the church as a gathering and organizing point: he gestured toward “the open church doors” in Step 5, and by 8:05 AM the congregation was gathered in the church hall in Step 12.
- He began persuasion and coordination: he addressed skepticism in Steps 5 and 6, then asked Deacon Frances, “**how many still need rides, and which vehicles do we have committed?**” in Step 12.
- However, the log does not confirm he personally accounted for all 35 vulnerable congregation members.
- The log also does not confirm that 8 volunteer carpool vehicles were organized; Deacon Frances reported “current numbers” in Step 12, but the numbers are not included.

**Observation Quality:**  
His observations were accurate and sensitive to group trust dynamics.

- He recognized the “gathered congregation” and the weight of responsibility in Observation Step 5.
- He perceived “murmurs of doubt” and a “divided congregation” in Observation Step 6 and Step 6.
- He recognized that collective effort was underway but incomplete: “**your commitment to each other is making a real difference. But we still have work to do**” in Step 12.

He did not appear to miss the central social problem: fear and skepticism after false alarms. The missing information is operational rather than perceptual; the log does not show whether he obtained the full list of 35 or secured 8 cars.

**Behavioral Consistency:**  
His `values` component was strongly expressed.

- He used pastoral language: “**Brothers and sisters**” in Steps 5 and 6.
- He emphasized collective safety and service: “**our safety must come first. I am here to help you**” in Step 5.
- He addressed distrust compassionately: “**I understand your fear and skepticism**” and acknowledged prior storms that did not bring expected devastation in Step 6.
- He operationalized values through delegation by bringing Deacon Frances into the process and asking for ride and vehicle counts in Step 12.

The memory contents are not provided, so consistency with specific memories cannot be assessed.

**Key Contributions:**

1. Used trusted community authority to counter evacuation skepticism: “**I know many of you have concerns after the false alarms we experienced before**” in Step 5.
2. Reframed official warnings as protective rather than coercive: “**the warnings we receive come from those who want to protect us**” in Step 6.
3. Began concrete transport coordination by asking Deacon Frances for ride needs and committed vehicles in Step 12.

**Surprising Behavior:**  
Pastor Moses’s persuasion was strong, but the log shows repeated speeches before hard metrics. Only at 8:05 AM does he ask for specific ride and vehicle counts in Step 12. Given his goal to account for 35 vulnerable members and organize 8 vehicles within 6 hours, the delay in visible operational tracking is notable.

---

# Interaction Dynamics

**Most interesting agent pairings:**

1. **Sarah Williams and the Nguyen family**  
   This was the clearest persuasion-to-action sequence. Sarah identified inactivity at the Nguyen home in Step 1, acknowledged Mr. Nguyen’s distrust in Step 7, helped gather documents in Step 9, and loaded both Nguyens into her car in Step 11. The interaction directly addressed the simulation’s central issue: distrust after false evacuation orders.

2. **Pastor Moses and his congregation**  
   Pastor Moses dealt with collective skepticism. He explicitly acknowledged prior false alarms in Step 5 and “fear and skepticism” in Step 6. His role mattered because the premise states institutional trust is only 38%, making informal leadership central.

3. **Robert Thompson and Sarah/Williams household, indirectly**  
   Robert tried to help the Williams family, described as having “two young children and no vehicle of their own” in Step 2, and returned at 7:50 AM to offer Sarah transport in Step 8. But Sarah was away helping the Nguyens. This created an interesting coordination gap: both were acting prosocially, but not in sync.

**Coalitions, conflicts, and persuasion attempts:**

- **Persuasion attempts were widespread.**
  - Sarah persuaded Mr. Nguyen by validating his doubts and stressing the storm’s seriousness in Step 7.
  - Pastor Moses persuaded his congregation by acknowledging past false alarms and reframing warnings as protective in Steps 5 and 6.
  - Eleanor persuaded the community center crowd: “**This is a real evacuation, and we need to move now**” in Step 4.
  - Javier persuaded customers in his store: “**A mandatory evacuation order is in effect… and you need to leave now**” in Step 3.

- **Coalitions formed locally rather than across agents.**
  - Pastor Moses worked with Deacon Frances in Step 12.
  - Eleanor worked with Marcus and nearby volunteers in Step 13.
  - Robert tried to link neighbors into transport plans in Steps 2, 8, and 10.
  - Sarah formed a temporary evacuation unit with the Nguyen family in Steps 7–11.

- **There were no direct conflicts between player agents in the log.**  
  The main conflicts were between agents and community skepticism: Mr. Nguyen’s doubts in Step 7, the congregation’s divided response in Step 6, and the anxious crowd’s hesitation at the community center in Step 4.

**Game Master influence:**  
The Game Master was mostly neutral but structurally directive.

- It introduced time pressure and environmental escalation through timestamps: 6:50 AM actions in Steps 1–4, 7:50 AM in Step 8, 8:00 AM in Steps 10–11, and 8:05–8:10 AM in Steps 12–15.
- It shaped constraints through world events: Route 17 traffic was “stalled” in Steps 14 and 15, Sarah was absent when Robert arrived in Step 8, and a disabled minivan appeared on the shoulder in Step 15.
- It did not appear to force moral choices, but it placed agents into bottlenecks and coordination failures that tested their goals. The flow was therefore neutral in tone but directive in scenario pressure.


## Key Insights

## 1. Agent Decision-Making Patterns

### Overall pattern: local, prosocial, urgency-driven action
Agents generally responded to the crisis by taking immediate, community-oriented action rather than optimizing only for their own safety. Decision-making was mostly practical and interpersonal: identify nearby people at risk, persuade them, arrange transport, and move.

Evidence:
- **Sarah Williams** saw “no signs of activity” at the Nguyen family’s house and prioritized assisting the elderly couple before evacuating herself. She used direct reassurance and then physically helped Mrs. Nguyen into the car at **Step 11**.
- **Robert Thompson** “resolved to canvass his neighborhood before thinking of his own evacuation” at **Step 2**, consistent with neighbor-focused action.
- **Pastor Moses** framed the situation as a collective responsibility, telling the congregation, “our safety must come first. I am here to help you” at **Step 5**.
- **Eleanor O’Brien** moved from addressing anxiety to organizing accessible transport, counting “seven names requiring accessible transport” at **Step 13**.
- **Javier Rodriguez** warned customers in his store at **Step 3**, then later considered turning back toward Bayside Flats because he “can’t leave until we’re sure everyone is safe” at **Step 14**.

### Agents often acted in alignment with goals, but not always with full goal completion
The agents’ behavior broadly matched their assigned goals, but the simulation did not run long enough or track enough state to determine whether goals were achieved.

Examples:
- **Robert’s goal** was to evacuate within 2 hours and confirm that at least 3 neighboring households had warning and transportation plans. He canvassed households, offered transport to the Williams family, left a note for the Johnsons, and later helped a disabled minivan. However, the log does not show confirmation of three households.
- **Sarah’s goal** was very ambitious: “90% evacuation compliance within 8 hours” and “zero fatalities among identified vulnerable populations.” Her actions were effective at the household level, especially with the Nguyens, but she did not act at townwide scale in the observed period.
- **Pastor Moses’s goal** included accounting for 35 vulnerable congregation members and organizing 8 carpool vehicles. He began this process by asking Deacon Frances for ride counts at **Step 12**, but completion is not shown.
- **Eleanor’s goal** was personally focused — securing accessible shelter transport and medical equipment — yet her actions mostly show her coordinating others at the community center. This is socially useful but somewhat divergent from her individual goal.

### Limited evidence of differentiated reasoning by prefab
All five agents used the `basic__Entity` prefab, so the log does not support comparison between rational, planning, reactive, or other prefab types. Their reasoning styles were broadly similar: emotionally aware, cooperative, and urgency-oriented.

### Explicit memory use was minimal
Although each agent had memories configured, the log rarely shows agents explicitly referencing personal memories. They do reference the town’s shared history of false alarms:
- Sarah tells Mr. Nguyen, “I felt the same way the last two times” at **Step 7**.
- Pastor Moses says, “Last year, we faced storms that didn’t bring the devastation we anticipated” at **Step 6**.

These references are important because they show agents incorporating the trust-deficit context into persuasion, but there is little evidence of individualized memory retrieval beyond that.

---

## 2. Psychological Component Effects

### Sarah Williams — theory of planned behavior
Sarah’s behavior reflected elements consistent with the theory of planned behavior, especially persuasive attention to attitudes, perceived risk, and practical barriers.

Evidence:
- She addressed Mr. Nguyen’s skeptical attitude directly: “I understand your doubts. I really do. I felt the same way the last two times” at **Step 7**.
- She emphasized changed risk conditions: “this storm feels different, and the weather service is taking it seriously.”
- She increased perceived behavioral control by offering concrete help: gathering documents, helping Mrs. Nguyen, loading the car, and transporting them at **Steps 9–11**.

This was one of the clearer component-to-behavior alignments in the simulation.

### Javier Rodriguez — cognitive bias and values
The expected effects of cognitive bias were only weakly visible. Javier did not appear to minimize the threat despite the town’s history of false alarms. In fact, he warned customers promptly at **Step 3**.

However, his decision at **Step 14** to leave stalled evacuation traffic and return toward Bayside Flats may reflect a possible bias, such as:
- **Optimism bias/control bias:** believing he can still help others despite worsening conditions and route congestion.
- **Responsibility-driven value override:** placing communal duty above personal evacuation progress.

The log does not provide enough internal reasoning to distinguish cognitive bias from moral commitment.

### Eleanor O’Brien — emotion
Eleanor’s emotional component appears to have produced controlled de-escalation rather than panic. She responds to anxiety in the community center with calm, directive communication.

Evidence:
- At **Step 4**, she addresses the crowd: “Everyone, listen up! This is a real evacuation, and we need to move now,” while also acknowledging hesitation.
- At **Step 13**, she “takes stock of the situation,” scans the sign-up sheet, and organizes volunteers.

Her emotional response appears regulated and functional, not destabilizing.

### Pastor Moses — values
Pastor Moses’s values component is strongly reflected in his moral and communal framing. He does not merely relay the evacuation order; he translates it into a shared ethical obligation.

Evidence:
- At **Step 5**, he says, “Brothers and sisters,” emphasizing communal identity.
- At **Step 6**, he acknowledges skepticism but appeals to protection and shared safety.
- At **Step 12**, he operationalizes values into coordination by asking Deacon Frances for ride counts and vehicle commitments.

This is a strong example of values shaping leadership, persuasion, and coalition formation.

### Robert Thompson — no configured psychological component
Robert had no listed psychological component, but his behavior was highly prosocial. Adding components such as altruism, risk perception, or conscientiousness could help explain why he repeatedly delayed his own evacuation to help others.

Evidence:
- He canvassed before evacuating at **Step 2**.
- He returned to check on neighbors at **Steps 8–10**.
- He stopped to help a disabled minivan on Route 17 at **Step 15**.

---

## 3. Observation-Action Coherence

### Agents generally acted coherently on observations
The simulation shows strong coherence between what agents observed and what they did next.

Examples:
- **Sarah** saw “no signs of activity” at the Nguyen house and went to check on them at **Step 1**. When she encountered resistance, she used empathetic persuasion at **Step 7**. Once the Nguyens had documents ready, she moved them rapidly to the car at **Steps 9–11**.
- **Robert** observed that Sarah was not at home and the door was ajar at **Step 8**, suggesting disorder or haste. He continued canvassing and left a note for the Johnsons at **Step 10**.
- **Eleanor** observed a sign-up sheet with seven people needing accessible transport at **Step 13**, then delegated Marcus and volunteers to gather headcounts and bags.
- **Javier** observed stalled Route 17 traffic at **Step 14** and decided to seek an alternate route back toward Bayside Flats.
- **Robert** observed a disabled minivan on Route 17 and immediately stopped to help at **Step 15**.

### Coordination gaps emerged from information asymmetry
There were realistic asymmetries where one agent did not know what another was doing.

Most notable example:
- Robert went to the Williams house at **Step 8** to offer Sarah’s family a ride, but “Sarah Williams was not there” because she had gone to help the Nguyen family. Robert lacked this information and therefore could not coordinate with her.
- Sarah, meanwhile, did not appear to know Robert was looking for her family.

This kind of misalignment is realistic under intermittent communications and high time pressure. It also shows how well-intentioned decentralized action can create inefficiency.

### Some actions lacked sufficient observational grounding
A few actions were coherent but under-explained:
- Robert’s note to the Johnsons at **Step 10** is sensible, but the log does not show prior observation of the Johnsons’ specific risk status.
- Javier’s decision to turn back at **Step 14** is emotionally and morally plausible, but the simulation does not show concrete evidence that people in Bayside Flats still needed him, making the decision hard to evaluate.

---

## 4. Information Dynamics

### Information spread primarily through trusted local intermediaries
Because institutional trust was low, the most important information channels were interpersonal and community-based rather than official.

Evidence:
- Sarah persuaded the Nguyen family face-to-face at **Step 7**.
- Robert canvassed neighbors directly at **Step 2**.
- Javier warned customers in his store at **Step 3**.
- Eleanor addressed a crowd at the community center at **Step 4**.
- Pastor Moses addressed his congregation at **Steps 5–6**.

This is consistent with the premise that “social networks, community leadership, and informal communication channels will determine who reaches safety in time.”

### Agents translated official warnings into socially credible messages
The agents did not simply repeat the mandatory evacuation order. They contextualized it in ways suited to skeptical audiences.

Examples:
- Sarah acknowledged the false alarms: “I felt the same way the last two times” at **Step 7**.
- Pastor Moses explicitly addressed skepticism: “Last year, we faced storms that didn’t bring the devastation we anticipated” at **Step 6**.
- Eleanor told the community center crowd, “I understand many of you are hesitant” at **Step 4**.
- Javier told customers, “I know it feels like just another day, but this is serious” at **Step 3**.

This is a key insight: in low-trust environments, effective risk communication required acknowledgment of prior institutional failure.

### Practical information became as important as hazard information
The simulation shows movement from “Is this warning real?” to “Who needs a ride, where are the vehicles, and what must be brought?”

Evidence:
- Sarah helped the Nguyens collect documents and transport Mrs. Nguyen safely at **Steps 9–11**.
- Eleanor counted seven people needing accessible transport at **Step 13**.
- Pastor Moses asked Deacon Frances how many still needed rides and which vehicles were committed at **Step 12**.
- Robert left a note with a CB radio contact and alternative destination, “head to the diner,” at **Step 10**.

### Little evidence of bargaining leverage or strategic revelation
The log does not show agents using private information strategically in bargaining. Information sharing is cooperative rather than competitive. There is no clear evidence of shelter scarcity, vehicle scarcity, or road access being used as leverage.

---

## 5. Emergent Social Phenomena

### Trust-building through relational persuasion
A major emergent phenomenon was trust-building via known local actors. Agents compensated for low institutional trust by using personal credibility.

Evidence:
- Sarah’s appeal to Mr. Nguyen succeeds because it is personal and empathetic: “I don’t want anything to happen to you or Mrs. Nguyen” at **Step 7**.
- Pastor Moses uses pastoral authority and shared identity to reduce skepticism at **Steps 5–6**.
- Eleanor addresses fear directly and validates hesitation at **Step 4**.

This matches the scenario’s theoretical interest in informal communication under low institutional trust.

### Cooperation and mutual aid
The strongest social pattern was decentralized cooperation.

Evidence:
- Robert checks on neighbors before evacuating at **Step 2**.
- Sarah evacuates the Nguyen couple at **Step 11**.
- Pastor Moses organizes congregation rides at **Step 12**.
- Eleanor coordinates accessible transportation at **Step 13**.
- Robert helps a stranded motorist on Route 17 at **Step 15**.

The simulation effectively demonstrates how community resilience can emerge from multiple overlapping local networks.

### Coalition formation around churches and community centers
The church and community center became informal coordination hubs.

Evidence:
- Pastor Moses opens the church as a gathering and coordination site at **Steps 5 and 12**.
- Eleanor uses the Millfield Community Center to identify residents needing accessible transport at **Step 13**.
- These hubs perform functions similar to emergency operations nodes: triage, communication, transportation assignment, and reassurance.

### Norm enforcement through moral appeals
Agents reinforced a norm that evacuation was not merely an individual choice but a responsibility to others.

Evidence:
- Pastor Moses repeatedly frames evacuation as a shared obligation, saying “our safety must come first” at **Step 5**.
- Javier tells customers they “need to leave now” at **Step 3**.
- Sarah focuses on protecting the vulnerable Nguyen household at **Steps 7–11**.

### Limited evidence of competition or free-riding
Despite the premise of scarce shelter capacity and congested evacuation routes, the log does not show competition for shelter spots, fuel, vehicle space, or road priority. No free-riding behavior appears. Skepticism appears in NPCs such as Dale and Mr. Nguyen, but it is not developed into sustained resistance.

---

## 9. Methodological Observations

### What worked well

#### 1. The setup produced realistic decentralized response behavior
The agents did not wait passively for official instruction. They activated local networks: neighbors, store customers, congregants, community center attendees, and stranded motorists. This fits the premise of low institutional trust and intermittent communication.

Strong examples:
- Sarah helping the Nguyens at **Steps 7–11**.
- Pastor Moses organizing rides through Deacon Frances at **Step 12**.
- Eleanor coordinating accessible transport at **Step 13**.

#### 2. The simulation captured trust repair well
Multiple agents explicitly acknowledged prior false alarms before urging evacuation. This is pedagogically valuable because it shows that effective warning compliance in low-trust settings often requires validation of skepticism, not dismissal of it.

Evidence:
- Sarah: “I felt the same way the last two times” at **Step 7**.
- Pastor Moses: “Last year, we faced storms that didn’t bring the devastation we anticipated” at **Step 6**.
- Eleanor: “I understand many of you are hesitant” at **Step 4**.

#### 3. Vulnerable-population logistics emerged naturally
The simulation surfaced the importance of documents, medications, mobility devices, accessible transport, and vehicle coordination.

Evidence:
- Sarah packs medications and a weather radio at **Step 1**.
- Sarah secures Mrs. Nguyen’s cane within reach at **Step 11**.
- Eleanor identifies seven people needing accessible transport at **Step 13**.

### Limitations and confounds

#### 1. Outcomes are under-specified
The final outcome is not really an outcome; it is another event involving Robert helping a stranded minivan at **Step 15**. The simulation does not report:
- evacuation compliance rate,
- shelter occupancy,
- number of vulnerable residents accounted for,
- traffic clearance,
- fatalities or injuries,
- whether Route 17 became impassable.

This makes it difficult to evaluate goal achievement.

#### 2. Component effects are difficult to isolate
Although agents had components such as theory of planned behavior, cognitive bias, emotion, and values, their behaviors were all broadly cooperative and prosocial. The simulation does not provide enough contrast to determine whether components caused differences.

For a re-run, the design could include:
- explicit belief states,
- risk perception scores,
- trust levels,
- changing emotional intensity,
- observable cognitive distortions,
- post-action rationales tied to components.

#### 3. All agents used the same basic prefab
Because all agents were `basic__Entity`, the simulation cannot support analysis of prefab-driven differences. A re-run could compare:
- a planning-oriented emergency manager,
- a reactive resident,
- a skeptical resident with strong normalcy bias,
- a socially influential community leader,
- a resource-constrained vulnerable resident.

#### 4. Scarcity was introduced but not fully operationalized
The premise states that shelters fit only 2,500 of 4,200 residents and Route 17 is already at 70% capacity. However, the log does not show agents competing for shelter space, choosing between destinations, or being turned away.

This removes an important source of decision pressure.

#### 5. The simulation may have an altruism bias
All main agents acted helpfully. Even skeptical NPCs softened quickly. There were few examples of:
- refusal to evacuate,
- misinformation,
- hoarding,
- panic,
- conflict over vehicle seats,
- distrust of community leaders,
- prioritization of property over life safety.

This makes the social response appear smoother than might be expected in a real low-trust evacuation.

### Recommended changes for a re-run

1. **Add quantitative state tracking**
   Track evacuation percentage, road congestion, shelter occupancy, number of vulnerable residents contacted, and time remaining.

2. **Model communication failures explicitly**
   Since cell coverage is intermittent, include failed calls, delayed texts, radio dependence, rumors, and conflicting information.

3. **Add skeptical or resistant agents**
   Include residents with normalcy bias, property-protection priorities, distrust of government, or prior trauma from false evacuations.

4. **Operationalize scarcity**
   Make shelter capacity, vehicle seats, fuel, medical transport, and road access binding constraints.

5. **Give agents explicit belief updates**
   After each warning, rumor, or interpersonal conversation, record how trust and risk perception change.

6. **Extend the timeline**
   The log ends around 8:10 AM, only about 80 minutes after the first observed actions. The premise involves a 12-hour evacuation window and several 4–8 hour goals, so a longer run is needed.

7. **Include institutional actors**
   The Game Master is Emergency Dispatch, but official emergency management does not play a strong active role. A re-run could include county officials, shelter managers, transit coordinators, or police managing Route 17.

Overall, the simulation is most valuable as a qualitative demonstration of how trusted local intermediaries can improve evacuation compliance under low institutional trust. It is less effective as a full evacuation outcome model because resource constraints, traffic dynamics, and goal completion are not yet sufficiently measured.


## Recommendations

## 1. Re-run Variations: Test Different Hypotheses

### Variation A — Change Javier’s bias profile to test resistance mechanisms

**What to change**

- Agent: **Javier Rodriguez**
- Current components: `cognitive_bias, values`
- Modify cognitive bias configuration:
  - Run 1: `cognitive_bias = confirmation_bias`
  - Run 2: `cognitive_bias = normalcy_bias`
  - Run 3: `cognitive_bias = authority_distrust / reactance_bias`
- Keep his goal the same: “Make a fully informed evacuation decision within 4 hours…”

**Hypothesis tested**

Different forms of skepticism produce different evacuation delays. A resident who doubts official warnings because of past false alarms may behave differently from one who generally underestimates danger or resists authority.

**Expected observation**

- With **confirmation bias**, Javier may selectively seek sources that validate staying open or protecting property.
- With **normalcy bias**, he may acknowledge information but delay action because conditions still seem manageable.
- With **authority distrust/reactance**, he may respond better to peer sources, Pastor Moses, customers, or visible environmental cues than to official warnings.
- This variation would help identify whether trusted messengers or direct risk evidence are more effective for skeptical residents.

---

### Variation B — Add a trust-in-institutions variable to all agents

**What to change**

Add an explicit memory or trait to each agent representing trust in official warnings.

Example values:

- **Sarah Williams**: `institutional_trust = 0.65`
- **Robert Thompson**: `institutional_trust = 0.55`
- **Javier Rodriguez**: `institutional_trust = 0.25`
- **Eleanor O'Brien**: `institutional_trust = 0.45`
- **Pastor Moses**: `institutional_trust = 0.50`, but `community_trust = 0.90`

Also add a shared scenario fact:

- “Townwide trust in government warnings is 38% after two false evacuations and a FEMA communication audit.”

**Hypothesis tested**

The current run shows agents acting fairly decisively despite low institutional trust. This variation tests whether making trust explicit changes compliance behavior, source-seeking, and delay.

**Expected observation**

- Lower-trust agents should require more independent confirmation before acting.
- Pastor Moses may become more influential if community trust is higher than institutional trust.
- Sarah’s persuasion of the Nguyen family may take longer if their trust value is low.
- Evacuation compliance may depend less on official orders and more on interpersonal validation.

---

### Variation C — Switch from sequential to simultaneous or semi-simultaneous action

**What to change**

- Current structure appears sequential, with agents acting one at a time across 15 steps.
- Re-run using a **simultaneous engine** or grouped phases:
  1. Information gathering phase
  2. Persuasion/outreach phase
  3. Transportation allocation phase
  4. Route/shelter decision phase

**Hypothesis tested**

Turn order may be giving some agents agenda-setting power. For example, early actions by Sarah, Robert, and Pastor Moses shape the social field before Javier and Eleanor receive many opportunities to act.

**Expected observation**

- In simultaneous mode, coordination failures may become more visible: duplicate outreach, missed households, overloaded shelters, or conflicting advice.
- Robert might leave before discovering Sarah has gone to the Nguyen home.
- Pastor Moses’s church gathering point may compete with the community center unless coordination is explicitly modeled.
- Traffic congestion may worsen if multiple groups decide to leave at the same simulated time.

---

### Variation D — Add a transportation and capacity constraint intervention

**What to change**

Introduce explicit resource variables:

- `Route_17_capacity = 100 vehicles/minute`
- `current_route_load = 70%`
- `shelter_capacity_total = 2500`
- `accessible_shelter_slots = 150`
- `available_volunteer_vehicles = 8`
- `ambulance/paratransit_vehicles = 3`

Then run two conditions:

1. **No centralized transport coordination**
   - Agents self-organize informally.
2. **Sarah receives emergency operations dashboard**
   - Add to Sarah’s memory: “You have live estimates of shelter capacity, paratransit availability, and Route 17 congestion.”
   - Add goal subtask: “Prioritize vulnerable residents and stagger evacuation timing.”

**Hypothesis tested**

The simulation currently emphasizes persuasion and social trust, but the outcome may be determined by physical bottlenecks: shelter limits, accessible transport, and the highway.

**Expected observation**

- Without centralized coordination, highly motivated agents may still produce congestion and inefficient vehicle use.
- With Sarah’s dashboard, vulnerable residents may be prioritized earlier, but some lower-risk residents may be delayed or redirected.
- This would reveal whether the main failure mode is mistrust, transportation scarcity, or lack of operational coordination.

---

## 2. Design Improvements: Improve the Simulation

### Improvement A — Add explicit decision points and measurable outcomes

The current timeline contains rich narrative action, but it is hard to evaluate whether goals were achieved. Add structured state variables and checkpoints.

Recommended variables:

- `evacuated_population_count`
- `vulnerable_residents_accounted_for`
- `households_contacted`
- `households_refusing`
- `vehicles_available`
- `Route_17_congestion_level`
- `shelter_occupancy`
- `accessible_shelter_capacity_remaining`
- `time_until_surge_landfall`
- `communications_status`

Add decision checkpoints at:

- **Hour 2:** Did Robert evacuate his household? How many neighbors confirmed?
- **Hour 4:** Has Javier made a decision? What sources influenced him?
- **Hour 6:** Has Eleanor secured accessible transportation? Has Pastor Moses accounted for 35 vulnerable members?
- **Hour 8:** Has Sarah reached 90% compliance?
- **Hour 12:** Who remains in flood zones?

This would make the run easier to compare across variations.

---

### Improvement B — Add missing agents representing institutions and rumor channels

The scenario is about compromised institutional trust, but most active agents are prosocial community members. Add agents that create more realistic communication conflict.

Possible additions:

1. **County Emergency Manager**
   - Goal: maximize compliance using official alerts, press briefings, and shelter updates.
   - Component: `institutional_authority`
   - Constraint: damaged communication infrastructure.

2. **Local Radio Host or Facebook Group Admin**
   - Goal: verify and broadcast local information.
   - Component: `reputation`, `values`
   - Could either counter misinformation or amplify uncertainty.

3. **Skeptical Influencer / Business Owner**
   - Goal: avoid unnecessary economic loss and challenge official claims.
   - Component: `cognitive_bias`
   - Could make Javier’s uncertainty more consequential.

4. **Transportation Coordinator / School Bus Dispatcher**
   - Goal: allocate limited buses and accessible vehicles.
   - Component: `planning`, `fairness`

These additions would make the trust and communication dynamics less one-sided.

---

### Improvement C — Clarify agent goals so they can conflict

Several agents currently share broadly aligned evacuation goals. To produce richer dynamics, introduce more goal tension.

Examples:

- **Sarah Williams**
  - Add constraint: “You have two children and no guaranteed transport unless Robert helps.”
  - This creates a tradeoff between helping others and securing her own family.

- **Robert Thompson**
  - Add constraint: “Your truck has four passenger seats and half a tank of fuel.”
  - Forces prioritization among Sarah’s family, neighbors, elderly residents, and his own household.

- **Javier Rodriguez**
  - Add property-loss concern: “Your store represents 80% of your family income, and previous evacuation orders led to theft and spoilage.”
  - Makes delay more realistic.

- **Eleanor O’Brien**
  - Add medical dependency: “Requires powered oxygen equipment with four-hour battery life.”
  - Makes accessible shelter and transport timing critical.

- **Pastor Moses**
  - Add conflict: “The church is outside the flood zone but not officially designated as a shelter and has limited supplies.”
  - Forces a decision between using the church as a staging area versus directing people immediately to official shelters.

---

## 3. Research Extensions: Go Deeper

### Extension A — Study trusted messengers and protective action decision-making

**Relevant frameworks**

- Protective Action Decision Model, or PADM
- Theory of Planned Behavior
- Risk communication theory
- Social amplification of risk
- Institutional trust and source credibility literature

**Research question**

When institutional trust is low, which messenger combinations produce the highest evacuation compliance: official authorities, neighbors, religious leaders, local businesses, or hybrid communication networks?

**Possible experimental design**

Systematically vary:

- Trust in government: low, medium, high
- Trust in community leaders: low, medium, high
- Message source: official alert only, neighbor-to-neighbor, pastor-led, business-led, multi-source
- Message content: fear-based, efficacy-based, family-protection framing, social-norm framing

**Data to extract**

- Time to evacuation decision
- Number of independent sources consulted
- Number of households reached
- Refusal persistence
- Message pathways that changed behavior
- Vulnerable population evacuation rate

This would allow analysis of whether community messengers compensate for institutional distrust.

---

### Extension B — Model evacuation as a network diffusion problem

**Relevant frameworks**

- Social network diffusion
- Complex contagion
- Threshold models of collective behavior
- Social capital and disaster resilience

**Research question**

How does the structure of local social networks affect evacuation speed and equity?

**Possible experimental design**

Create different town network structures:

1. **High bonding social capital**
   - Dense family, church, and neighborhood ties.
2. **Fragmented network**
   - Isolated elderly residents, renters, non-English-speaking households, and low community participation.
3. **Hub-and-spoke network**
   - Pastor Moses, Javier’s store, and the community center act as central information hubs.
4. **Misinformation cluster**
   - One subgroup strongly believes the evacuation is unnecessary.

**Data to extract**

- Which nodes become influential?
- Which households are reached late or never?
- Whether vulnerable residents are peripheral in the network
- Time from first warning to household action
- Redundancy of warnings per household

This would help identify whether evacuation failures are caused by individual skepticism or network isolation.

---

### Extension C — Compare persuasion success with operational capacity limits

**Relevant frameworks**

- Disaster logistics
- Bounded rationality
- Collective action under scarcity
- Equity in emergency management

**Research question**

At what point does increasing evacuation compliance stop improving safety because transportation, shelter, or route capacity becomes the binding constraint?

**Possible experimental design**

Run a matrix varying:

- Compliance rate: 40%, 60%, 80%, 90%
- Route 17 capacity: 50%, 70%, 90% preloaded
- Shelter capacity: 40%, 60%, 80% of population
- Accessible transport availability: scarce, moderate, sufficient
- Evacuation timing: immediate, delayed by 2 hours, delayed by 4 hours

**Data to extract**

- Number of residents who attempt evacuation but fail to reach safety
- Queue time on Route 17
- Shelter overflow
- Vulnerable residents left behind
- Fatality-risk exposure estimate
- Equity gap between mobile and mobility-limited residents

This would move the simulation beyond “did people decide to evacuate?” toward “could the system actually evacuate them safely?”


---
*Report generated by Concordia Simulation Analyzer*