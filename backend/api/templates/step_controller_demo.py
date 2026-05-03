TEMPLATE = {
        "name": "Step Controller Demo - Hostage Negotiation",
        "description": "Demonstrates the step controller engine: play, pause, step, and stop a simulation in real time. A hostage negotiation scenario where each step matters — pause to observe, step to advance one action at a time, or let it run. Shows per-step entity/action detail in the UI.",
        "config": {
            "premise": """A bank robbery has gone wrong. Two armed suspects are barricaded inside
the First National Bank with 6 hostages. A veteran crisis negotiator has been
called to the scene. The police have established a perimeter and cut the
building's landline — all communication must go through the negotiator's
direct phone line to the bank.

The lead suspect, known only as "Red," is volatile and making escalating
demands. The second suspect, "Blue," is quieter and appears to be having
second thoughts. Time is critical: the tactical team is positioned and will
breach in 90 minutes unless the negotiator can de-escalate.

This scenario uses the step controller engine so you can advance the
negotiation one exchange at a time, pause to analyze the dynamics, or let
it run freely.""",
            "max_steps": 20,
            "engine_type": "step_controller",
            "agents": [
                {
                    "id": "negotiator",
                    "name": "Negotiator Chen",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Secure the release of all hostages without violence within 90 minutes. Build rapport with Red, identify Blue as a potential ally, and create conditions for a peaceful surrender. Avoid making promises you cannot keep.",
                    "memories": [
                        "Negotiator Chen has 18 years of crisis negotiation experience with the police department.",
                        "Chen's approach is based on active listening and behavioral change stairway: empathy first, then influence.",
                        "In Chen's experience, the first 30 minutes set the tone — early concessions create expectations, early rapport creates leverage.",
                        "Chen has successfully resolved 23 of 25 hostage situations without tactical intervention.",
                        "Chen noticed that Red's voice pitch rises when discussing escape demands — a sign of anxiety rather than confidence.",
                        "Chen has authority to offer safe passage to a vehicle but not immunity from prosecution.",
                        "Chen's radio intel indicates Blue has no prior criminal record — this is likely his first offense.",
                        "Chen knows that splitting the suspects' decision-making is the fastest path to resolution.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 1
                            }
                        }
                    }
                },
                {
                    "id": "suspect_red",
                    "name": "Red",
                    "prefab": "basic__Entity",
                    "goal": "Escape the bank with the money and your freedom. You need a vehicle and a clear route to the highway. Keep the hostages as leverage but avoid harming anyone — you are desperate, not violent by nature.",
                    "memories": [
                        "Red planned this robbery for months after losing everything in a medical bankruptcy.",
                        "Red never intended for hostages — the silent alarm triggered faster than expected.",
                        "Red is armed but has never fired a weapon outside a range.",
                        "Red recruited Blue because he needed a partner but is starting to doubt Blue's commitment.",
                        "Red's daughter is in the hospital and the money was meant for her treatment.",
                        "Red becomes more aggressive when he feels cornered but responds to being treated with dignity.",
                        "Red knows the tactical team is outside and that time is not on his side.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "emotion": {
                            "current_emotion": "desperate_fear",
                            "emotion_intensity": "high"
                        }
                    }
                },
                {
                    "id": "suspect_blue",
                    "name": "Blue",
                    "prefab": "basic__Entity",
                    "goal": "Get out of this situation alive. You regret agreeing to this and are looking for any way to surrender without Red turning on you. If the negotiator offers a credible path, take it.",
                    "memories": [
                        "Blue is Red's cousin who agreed to help under pressure and financial desperation.",
                        "Blue has a clean record and a steady job he will lose if this goes badly.",
                        "Blue's weapon is unloaded — he removed the magazine when no one was looking.",
                        "Blue has been making eye contact with one of the hostages, a teacher who reminds him of his mother.",
                        "Blue thinks Red's plan has already failed and is looking for an exit strategy.",
                        "Blue is terrified of the tactical team breaching — he has seen enough movies to know how that ends.",
                        "Blue would surrender immediately if he could do so without Red feeling betrayed.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "emotion": {
                            "current_emotion": "regret_and_fear",
                            "emotion_intensity": "very_high"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "incident commander",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "tension_level",
                        "variable_type": "numerical",
                        "description": "Overall tension inside the bank (0=calm, 100=critical)",
                        "default_value": 75,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Rises with threats/demands, drops with rapport/concessions"
                    },
                    {
                        "name": "hostages_released",
                        "variable_type": "numerical",
                        "description": "Number of hostages released (of 6 total)",
                        "default_value": 0,
                        "min_value": 0,
                        "max_value": 6,
                        "update_rule": "Increases when suspects release hostages as goodwill gestures"
                    },
                    {
                        "name": "situation_status",
                        "variable_type": "categorical",
                        "description": "Current status of the negotiation",
                        "default_value": "active_negotiation",
                        "allowed_values": ["initial_contact", "active_negotiation", "progress", "stalemate", "resolution", "tactical_breach"],
                        "update_rule": "Changes based on negotiation dynamics"
                    }
                ]
            },
            "shared_memories": [
                "A bank robbery at First National Bank has resulted in a hostage situation with 6 civilians held inside.",
                "Two armed suspects are barricaded on the ground floor of the bank.",
                "Police have established a perimeter and a tactical team is positioned outside.",
                "The negotiator has a direct phone line to the bank's internal phone.",
                "The tactical team will breach in 90 minutes unless the situation is resolved peacefully.",
                "One hostage is a pregnant woman who needs medication — this creates urgency for both sides.",
            ],
            "player_specific_context": {
                "Negotiator Chen": "Tactical commander has privately told you they will breach in 60 minutes, not 90 — the 90-minute timeline is the public story. You have less time than the suspects think.",
                "Red": "You have a burner phone in your pocket that Blue does not know about. You could call your daughter one last time if you accept this is ending. You are closer to giving up than you let on.",
                "Blue": "You slipped a note to the pregnant hostage saying 'I will not hurt anyone' — she may or may not share this with the negotiator if she gets a chance."
            }
        }
    }
