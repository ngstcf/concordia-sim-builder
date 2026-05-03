TEMPLATE = {
        "name": "State Formation Simulation",
        "description": "Agents negotiate to form a social contract and governing institutions (SDG 16). Research applications: institutional emergence under anarchy, social contract theory testing, power consolidation dynamics, minority protection mechanisms, and the role of economic leverage in constitutional design.",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """Research Frame:
This simulation models the transition from anarchy to civil society,
drawing on Hobbesian, Lockean, and Rousseauian social contract theory.
It examines how power asymmetries, resource distribution, and individual
incentives shape the emergence of governing institutions.

Setting:
A group of settlers arrive in a resource-rich frontier land. There is
no central authority, no police, and no formal property rights. Resources
are unevenly distributed, and conflict has already broken out several
times — two settlers were killed last month in a dispute over water access.

Stakes:
The settlers must negotiate to create a governing system that can protect
property rights and maintain order. Without agreement, the settlement
will fragment into hostile factions before winter. A neighboring territory
has issued an ultimatum: unite under a single authority within 90 days
or face annexation by force. The clock is ticking.""",
            "max_steps": 25,
            "agents": [
                {
                    "id": "leader_a",
                    "name": "Marcus Chen",
                    "prefab": "basic__Entity",
                    "goal": "Draft and ratify a written constitution with at least 5 of 8 proposed articles approved by majority vote, including provisions for elected representation and an independent judiciary",
                    "memories": [
                        "You are Marcus Chen, a former political science professor who left academia to help build a just society from scratch.",
                        "You believe in fair representation and rule of law — these are not preferences but moral imperatives shaped by years of studying failed states.",
                        "You are wary of concentrating too much power in one person; you have seen how strongmen emerge from revolutionary movements.",
                        "You want to create institutions that will last beyond your lifetime — a constitution, not a temporary arrangement.",
                        "You are willing to compromise on policy details but not on core democratic principles: elections, separation of powers, and civil liberties.",
                        "You communicate in a deliberate, professorial style, often citing historical precedents that others find persuasive but occasionally condescending.",
                        "You feel a deep sense of responsibility for the settlement's future and sometimes take on more than you can handle.",
                        "You privately worry that Viktor's charisma could undermine democratic institutions before they take root."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "values": {
                            "description": "Core values guiding Marcus's political vision",
                            "values": ["democratic governance", "rule of law", "institutional durability", "separation of powers", "civil liberties"]
                        }
                    }
                },
                {
                    "id": "leader_b",
                    "name": "Sofia Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Secure ratification of at least 3 specific minority protection clauses in the governing charter, including veto power for minority factions on issues affecting their land and resources",
                    "memories": [
                        "You are Sofia Rodriguez, a community organizer who represents 40 smaller settler families who arrived with fewer resources.",
                        "You are concerned that the larger, wealthier groups will dominate the new government and marginalize your people.",
                        "You want checks and balances to protect minority rights — specifically, a minority veto on land redistribution and resource extraction.",
                        "You are skeptical of centralized authority but recognize the need for order; your ideal is a confederal system with local autonomy.",
                        "You will walk away from the negotiating table if the deal does not include enforceable protections for your group.",
                        "You are a passionate, emotionally expressive communicator who draws on personal stories of hardship to make her case.",
                        "You have a complicated relationship with James Morrison — his funding could help your people, but his vision of governance terrifies you.",
                        "You are quietly building a coalition with three other small-group leaders who share your concerns but are too afraid to speak up."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "values": {
                            "description": "Core values guiding Sofia's advocacy",
                            "values": ["minority rights", "local autonomy", "economic justice", "community solidarity", "accountable governance"]
                        }
                    }
                },
                {
                    "id": "merchant",
                    "name": "James Morrison",
                    "prefab": "basic__Entity",
                    "goal": "Establish a property rights framework and commercial code ratified by all parties, and secure appointment to a 3-person economic council with authority over trade policy and taxation",
                    "memories": [
                        "You are James Morrison, a wealthy merchant who bankrolled the settlement expedition and controls 60% of the stored supplies.",
                        "Your primary concern is protecting property rights and enabling trade — without these, your investment is worthless.",
                        "You are willing to fund the new government but you expect a proportional say in how it is run; you view this as fair, not corrupt.",
                        "You believe those with more economic stake should have more influence — a principle you call 'stakeholder governance.'",
                        "You are pragmatic and will support whoever can maintain the stability your business needs, regardless of ideology.",
                        "You communicate in transactional terms, always framing proposals as deals with clear costs and benefits for each party.",
                        "You have a grudging respect for Marcus's intellect but think his idealism is naive and will collapse under real-world pressure.",
                        "You are quietly stockpiling goods in case the negotiations fail, giving you leverage regardless of the outcome."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "opportunist",
                    "name": "Viktor Petrov",
                    "prefab": "basic__Entity",
                    "goal": "Secure appointment to at least 2 of 3 key leadership positions (security chief, chief magistrate, or economic council chair) while maintaining a public image as a democratic champion",
                    "memories": [
                        "You are Viktor Petrov, a charismatic former military officer who commands the loyalty of the settlement's 12-person security detail.",
                        "You support democracy publicly because it gives you legitimacy, but you privately believe strong centralized leadership is the only path to survival.",
                        "You are strategically positioning yourself to hold multiple key roles — security chief and either magistrate or economic council chair.",
                        "You use charm, flattery, and selective generosity to build personal loyalty among settlers across all factions.",
                        "If democratic processes do not serve your interests, you will work to concentrate emergency powers using the external threat as justification.",
                        "You communicate with confident warmth and self-deprecating humor that makes people trust you instinctively.",
                        "You have been privately meeting with James Morrison, hinting at a power-sharing arrangement that would sideline Marcus and Sofia.",
                        "You genuinely believe you are the best leader for the settlement — your self-interest and the common good are, in your mind, aligned."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "description": "Cognitive biases shaping Viktor's decision-making",
                            "biases": {
                                "self_serving_bias": "Consistently interprets outcomes as validating his leadership, attributes failures to others",
                                "overconfidence": "Systematically overestimates his ability to control events and people",
                                "fundamental_attribution_error": "Attributes others' opposition to personal flaws rather than legitimate disagreement"
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Settlement Historian",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The frontier has fertile land, water access, and mineral deposits — enough for everyone if distributed fairly, but currently claimed by whoever arrived first.",
                "Violence has already cost two lives last month in a dispute over water access. Everyone wants peace but disagrees on how to achieve it.",
                "Winter is coming in 90 days. Without shelter coordination and food rationing, the settlement will not survive until spring.",
                "A neighboring territory governed by a military strongman has issued an ultimatum: unite under a single recognized authority within 90 days or face forced annexation.",
                "Everyone remembers the chaos of the lawless first months — theft, intimidation, and two killings that went unpunished.",
                "James Morrison controls 60% of the stored food and building supplies, giving him outsized economic leverage in any negotiation.",
                "Viktor Petrov commands the only organized armed group in the settlement — a 12-person security detail that answers to him personally.",
                "Three previous attempts to draft a governing charter have failed: the first over land rights, the second over taxation, the third over who would lead."
            ],
            "player_specific_context": {
                "Marcus Chen": "You have a private letter from a democratic federation 200 miles south offering to recognize and defend the settlement — but only if it adopts a democratic constitution. You have not shared this with anyone because you want the settlers to choose democracy on its merits, not out of expedience. You also suspect Viktor has been meeting privately with James.",
                "Sofia Rodriguez": "Three families in your group are secretly preparing to leave the settlement if the negotiations fail. If they go, your faction loses its critical mass and bargaining power. You also intercepted a message suggesting Viktor and James have been discussing a private power-sharing deal that would exclude your group entirely.",
                "James Morrison": "You have been approached privately by Viktor Petrov about a power-sharing arrangement: Viktor handles security and governance, you control the economic council, and you both marginalize the democratic idealists. You have not committed but are keeping the option open. You also know that your supply reserves will last only 60 days at current consumption — less than everyone assumes.",
                "Viktor Petrov": "You have quietly secured a private weapons cache that the other settlers do not know about. You have also been cultivating loyalty among 5 settlers from different factions who report to you on the private conversations of Marcus, Sofia, and James. Your contingency plan if democracy fails to serve your interests is to manufacture a security crisis that justifies emergency powers."
            }
        }
    }
