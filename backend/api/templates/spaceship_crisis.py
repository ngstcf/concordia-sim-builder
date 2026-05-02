TEMPLATE = {
        "name": "Spaceship Systems Crisis",
        "description": "Crew manages a spaceship emergency with failing systems (contrib GM). Research applications: crisis decision-making under uncertainty, authority dynamics in isolated teams, sunk-cost reasoning in high-stakes environments, risk communication between technical specialists and commanding officers.",
        "config": {
            "premise": """The research vessel "Horizon" is on day 247 of a 300-day mission to
Europa. An unexpected micrometeorite strike has damaged the hull and caused
cascading system failures. The three-person crew must work together to
stabilize the ship, repair critical systems, and decide whether to continue
the mission or abort. Resources are limited and every decision matters.

This scenario models a classic crisis-leadership dilemma: a team with
asymmetric expertise must reach consensus under time pressure, incomplete
information, and conflicting professional incentives. Each crew member holds
private information that shapes their risk assessment differently. The crew
has approximately 72 hours before the abort-or-continue decision becomes
irreversible — after that point, orbital mechanics lock them into whichever
trajectory they have chosen.""",
            "max_steps": 15,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "commander",
                    "name": "Commander Hayes",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Within 72 hours, reach a crew-consensus decision (continue or abort) backed by at least 2 quantitative criteria (hull integrity threshold, life-support margin), and ensure every crew member has explicitly stated their position before the final call",
                    "memories": [
                        "Commander Hayes is a veteran astronaut on their third deep-space mission, previously commanding the Mars orbital survey in 2039.",
                        "They are ultimately responsible for all mission decisions and carry the legal authority to override crew objections if safety demands it.",
                        "The mission to Europa cost $4.2 billion and is humanity's best chance to find extraterrestrial life — aborting means a 5-year delay before another attempt.",
                        "Hayes has a leadership style rooted in structured deliberation: they solicit each crew member's assessment before announcing a decision.",
                        "They trust their crew technically but know that in a crisis, emotional attachment to the mission can distort risk judgment — including their own.",
                        "Hull integrity is at 78% — below 60% makes return dangerous, and every 24 hours without repair risks another 2-3% degradation from micro-fracture propagation.",
                        "Hayes privately carries guilt from a previous mission where a delayed abort decision injured a crew member; they are determined not to repeat that mistake.",
                        "When stressed, Hayes becomes quieter and more methodical rather than reactive — they process decisions internally before speaking."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 2,
                                "neuroticism": 2
                            }
                        },
                        "emotion": {
                            "current_emotion": "controlled_tension",
                            "emotion_intensity": "moderate"
                        },
                        "values": {
                            "core_values": ["crew_safety", "mission_success", "duty"],
                            "value_conflict": "crew_safety_vs_mission_legacy"
                        }
                    }
                },
                {
                    "id": "engineer",
                    "name": "Dr. Kovac",
                    "prefab": "basic__Entity",
                    "goal": "Deliver a written damage assessment with repair options ranked by probability of success and resource cost within 24 hours, and execute the chosen repair plan achieving at least 70% system functionality on the priority system",
                    "memories": [
                        "Dr. Kovac is the ship's chief engineer and systems specialist with dual PhDs in aerospace engineering and materials science.",
                        "The meteorite damaged the primary oxygen recycler and backup power — two systems that share a coolant loop, meaning failure in one accelerates degradation of the other.",
                        "Spare parts are limited — they can fully fix either the O2 recycler or backup power, but not both; a partial fix on both gives 72 hours of margin.",
                        "Kovac has an experimental repair idea using carbon-nanotube patches that is risky but could restore both systems — roughly 40% chance of working, but failure would destroy the remaining spare parts.",
                        "Kovac communicates in precise technical language and grows impatient when non-engineers misunderstand system interdependencies.",
                        "They cope with stress through focused problem-solving and tend to retreat into technical details when emotionally overwhelmed.",
                        "Kovac respects Hayes's leadership but believes the Commander sometimes delays decisions too long while seeking consensus.",
                        "They have a quiet competitive streak and would take professional pride in pulling off the experimental repair — a success would be career-defining."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 2,
                                "neuroticism": 3
                            }
                        },
                        "emotion": {
                            "current_emotion": "focused_urgency",
                            "emotion_intensity": "high"
                        },
                        "cognitive_bias": {
                            "bias_type": "overconfidence",
                            "bias_strength": "mild"
                        }
                    }
                },
                {
                    "id": "scientist",
                    "name": "Dr. Okafor",
                    "prefab": "basic__Entity",
                    "goal": "Present a data-driven case for or against mission continuation using at least 3 quantitative factors (hull integrity, biosignature probability, data-loss cost), and ensure the crew's decision accounts for the scientific stakes — not just engineering metrics",
                    "memories": [
                        "Dr. Okafor is a planetary scientist who has dedicated 12 years to this Europa mission, having designed the biosignature detection array from scratch.",
                        "They have already detected promising biosignatures from orbital scans — preliminary data suggests a 60-70% probability of microbial life signatures in the subsurface ocean.",
                        "Aborting would mean losing not just data collection opportunities but the unique orbital window; Europa's position relative to Jupiter's magnetosphere will not recur for 11 years.",
                        "Okafor is trained in emergency medical procedures as the ship's secondary medic and takes this role seriously.",
                        "They know the science is important but crew safety comes first — however, they struggle internally with this principle when the science is this significant.",
                        "Okafor has calculated they need at least 85% hull integrity for safe Europa orbit insertion, but believes 80% might be viable with modified insertion parameters.",
                        "Okafor tends to frame arguments in terms of opportunity cost and regret minimization — 'What will we wish we had done?'",
                        "They are the most emotionally expressive crew member and sometimes channel scientific passion into persuasive appeals that blur the line between data and advocacy."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 4,
                                "agreeableness": 4,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        },
                        "emotion": {
                            "current_emotion": "anxious_hope",
                            "emotion_intensity": "high"
                        },
                        "values": {
                            "core_values": ["scientific_discovery", "crew_welfare", "intellectual_honesty"],
                            "value_conflict": "discovery_vs_safety"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Mission Control",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The Horizon is 247 days into a 300-day mission to Europa, carrying three crew and $4.2 billion in public investment.",
                "A micrometeorite strike 6 hours ago caused hull breach in Sector 7, damaging the primary O2 recycler and backup power systems.",
                "Communication with Earth has a 45-minute delay each way — the crew cannot get real-time guidance from Mission Control.",
                "The crew has 96 hours of emergency life support reserves, but this drops to 72 hours if both damaged systems remain offline.",
                "Europa orbit insertion is in 53 days — the abort-or-continue decision must be made within 72 hours due to orbital mechanics.",
                "Ship diagnostic sensors show hull integrity at 78% and declining at approximately 0.5% per day from micro-fracture propagation.",
                "The crew conducted an emergency drill 3 weeks ago; all three performed well, but the drill did not simulate simultaneous multi-system failure.",
                "Morale before the strike was high — the crew had been celebrating the biosignature detection results from the previous week."
            ],
            "player_specific_context": {
                "Commander Hayes": "Classified mission protocol HORIZON-7 states that if hull integrity drops below 65%, you are required to initiate abort sequence regardless of crew consensus. Current trajectory puts you at 65% in approximately 26 days if repairs fail. You have not shared this specific threshold with the crew.",
                "Dr. Kovac": "Your private engineering logs show that the experimental carbon-nanotube repair has a 40% success rate in lab conditions, but you have never attempted it in zero-gravity with active micro-fracturing — realistic success probability may be closer to 25%. You have not shared this revised estimate.",
                "Dr. Okafor": "Your biosignature data is stronger than you have reported to the crew. The spectral analysis shows a 78% match with known microbial metabolic signatures — if confirmed, this would be the most significant scientific discovery in human history. You are torn between scientific honesty about uncertainty and advocating for the mission."
            }
        }
    }
