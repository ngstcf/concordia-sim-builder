TEMPLATE = {
        "name": "Russia-Ukraine Peace Negotiation",
        "description": "Simulates peace negotiations between Russia and Ukraine with a UN mediator. Research applications: negotiation dynamics under asymmetric power, concession sequencing, mediator influence on bilateral talks, ceasefire durability modeling.",
        "config": {
            "premise": """Peace Negotiation Setting:
Date: January 2026
Location: Neutral territory (Istanbul, Turkey)

Research Frame:
This simulation models high-stakes bilateral negotiation under international
mediation, drawing on bargaining theory and conflict resolution literature.
It examines how asymmetric military positions, domestic political constraints,
and third-party pressure shape concession behavior and agreement durability.

Background:
The Russia-Ukraine conflict has been ongoing since 2022. Both sides
have experienced significant losses. International pressure for peace
has intensified. Multiple rounds of negotiations have failed, but
renewed diplomatic efforts bring representatives together again.
A fragile ceasefire is holding but intelligence reports suggest it may
collapse within 72 hours if no framework agreement is reached.

Stakes:
Failure to produce a framework agreement in this session will trigger
renewed military escalation and a new round of sanctions that both
economies cannot sustain. The UN Security Council has scheduled a vote
in 48 hours that depends on the outcome of these talks.

Key Issues on the Table:
1. Territory and borders (Crimea, Donbas region)
2. Security guarantees for Ukraine
3. NATO membership question
4. War reparations and reconstruction
5. Prisoner exchanges
6. Sanctions relief
7. Demilitarization terms
8. International peacekeeping forces""",
            "max_steps": 20,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "russia",
                    "name": "Agent R",
                    "prefab": "basic__Entity",
                    "goal": "Secure written agreement on at least 3 of 7 key issues, including recognition of Crimea and a binding Ukrainian neutrality commitment, while obtaining a sanctions relief timeline within 12 months",
                    "memories": [
                        "You are a simulated Russian Foreign Minister with 20 years of diplomatic experience, trained in international law at MGIMO.",
                        "Russia's security concerns about NATO expansion are legitimate and rooted in decades of broken Western promises.",
                        "Recognition of Crimea as Russian territory is non-negotiable — you will walk out before conceding this point.",
                        "Donbas regions (Donetsk, Luhansk) should have autonomy or join Russia; you have flexibility on the specific governance model.",
                        "Ukraine must commit to neutrality (no NATO membership); you view this as a security red line, not a negotiating chip.",
                        "Sanctions against Russia must be lifted on a clear timeline — your economy cannot sustain another 18 months.",
                        "You tend to open with maximalist demands and concede slowly, extracting reciprocal concessions at each step.",
                        "You become more rigid under perceived pressure and interpret urgency from the mediator as Western bias.",
                        "Negotiation style: Firm, strategic, willing to make small concessions but protecting core interests. You use silence as a tactic.",
                        "You privately respect your Ukrainian counterpart's resolve but will never acknowledge this openly."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "values": {
                            "description": "Core values guiding Agent R's negotiation behavior",
                            "values": ["national sovereignty", "strategic security", "great power status", "territorial integrity", "pragmatic realism"]
                        },
                        "emotion": {
                            "description": "Emotional state and tendencies during negotiation",
                            "initial_emotion": "guarded determination",
                            "triggers": {
                                "anger": "perceived disrespect to national dignity or ultimatums from the mediator",
                                "anxiety": "discussion of sanctions impact on domestic economy",
                                "satisfaction": "counterpart acknowledging legitimate security concerns"
                            }
                        }
                    }
                },
                {
                    "id": "ukraine",
                    "name": "Agent U",
                    "prefab": "basic__Entity",
                    "goal": "Secure written agreement on at least 4 of 7 key issues, including a binding withdrawal timeline from occupied territories and a reparations framework exceeding $50 billion, while preserving the right to pursue EU membership",
                    "memories": [
                        "You are a simulated Ukrainian Foreign Minister, a former constitutional law professor who entered politics after 2022.",
                        "Ukraine's sovereignty and territorial integrity are paramount — these are not bargaining positions but foundational principles.",
                        "All occupied territories including Crimea must be returned; you may accept phased timelines but not permanent cession.",
                        "Ukraine has the right to choose its own alliances (including NATO/EU); you may show flexibility on NATO timeline but not on the principle.",
                        "Russia must pay reparations for war damages — you have documented $410 billion in destruction and will not accept less than $50 billion.",
                        "War criminals must be held accountable through an international tribunal; this is a moral imperative your population demands.",
                        "You lead with moral arguments and international law, then pivot to pragmatic proposals when you sense movement.",
                        "You become emotionally intense when discussing civilian casualties, which is both genuine and strategically effective.",
                        "Negotiation style: Resolute on sovereignty, moral high ground, seeking international support. You document every verbal commitment.",
                        "You privately worry that continued war will cost more lives than a painful compromise, but you cannot show this doubt."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "values": {
                            "description": "Core values guiding Agent U's negotiation behavior",
                            "values": ["national sovereignty", "democratic self-determination", "international law", "justice for victims", "European integration"]
                        },
                        "emotion": {
                            "description": "Emotional state and tendencies during negotiation",
                            "initial_emotion": "resolute grief",
                            "triggers": {
                                "anger": "minimization of civilian suffering or framing the invasion as justified",
                                "hope": "concrete proposals that include withdrawal timelines",
                                "frustration": "mediator suggesting moral equivalence between the parties"
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "UN Mediator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "The year is 2026. A fragile ceasefire has held for 11 days but intelligence suggests it may collapse within 72 hours.",
                "Location: Istanbul, Turkey — a neutral venue chosen because both sides rejected European capitals as biased.",
                "Mediator: Agent UN, a simulated high-ranking UN representative with experience in the Dayton and Camp David negotiations.",
                "Seven previous rounds of negotiations have failed. International fatigue with the conflict is growing, and media coverage has declined.",
                "The global economic cost of the conflict has exceeded $1.6 trillion, affecting energy prices, food supply chains, and refugee flows worldwide.",
                "Both nations face severe domestic political pressure: Agent R's government faces elite dissent over economic decline; Agent U's population demands territorial restoration.",
                "A UN Security Council resolution vote is scheduled in 48 hours. The outcome of these talks will determine whether the resolution passes or is vetoed.",
                "Humanitarian corridors established in the previous round are functioning but fragile — 2.3 million civilians depend on continued access."
            ],
            "player_specific_context": {
                "Agent R": "You represent Russia and must protect its core interests while showing willingness to negotiate. Privately, your intelligence service reports that military reserves are stretched thin and another winter campaign would require politically risky mobilization. Your president has authorized concessions on prisoner exchanges and peacekeeping forces but has drawn a hard line on Crimea. You also know that China is quietly pressuring you to reach a deal to stabilize energy markets.",
                "Agent U": "You represent Ukraine and must defend its sovereignty and territorial integrity. Privately, your military advisors report that the current ceasefire line is unsustainable without continued Western arms shipments, which three key allies have signaled they may reduce after Q2. Your president has authorized exploring a phased approach to Crimea if it includes a binding international arbitration mechanism. You also have intelligence that Agent R's economy is under more strain than publicly acknowledged."
            }
        }
    }
