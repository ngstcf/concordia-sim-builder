TEMPLATE = {
        "name": "Measurements Demo - Clinical Trial Ethics Board",
        "description": "Demonstrates the measurements/metrics system: after the simulation runs, check the 'Component Logs' tab to see detailed per-component channel data — observation logs, reasoning traces, and situation assessments captured by Concordia's internal measurement channels. Uses grounded variables alongside measurements to show both explicit tracking and implicit component logging.",
        "config": {
            "premise": """An institutional ethics review board is meeting to decide whether to approve
a controversial Phase III clinical trial. A pharmaceutical company has
developed a promising treatment for early-onset Alzheimer's, but the Phase II
data shows both remarkable efficacy (62% improvement in cognitive scores)
and concerning side effects (8% of participants experienced severe
neurological episodes).

The board must vote to approve, reject, or request modifications to the
trial protocol. Each member brings different expertise and priorities.
The pharmaceutical company's representative is present to answer questions.

DEMO INSTRUCTIONS: After running this simulation, navigate to the results
page and open the 'Component Logs' tab. You will see per-component
measurement channels showing how each agent's internal components
(observation, situation perception, personality) processed information
at each step.""",
            "max_steps": 15,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "chair",
                    "name": "Dr. Elaine Marsh",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Guide the board to a well-reasoned decision by ensuring every member's perspective is heard. Reach a formal vote by the end of the meeting. Prioritize patient safety but weigh it against the urgency of having no existing treatment for early-onset Alzheimer's.",
                    "memories": [
                        "Dr. Marsh has chaired the ethics board for 7 years and has reviewed over 200 trial protocols.",
                        "She is a bioethicist by training with a medical degree she no longer practices.",
                        "She has seen boards rubber-stamp trials they should have questioned, and she has seen boards kill promising treatments out of excessive caution.",
                        "Her standard approach: hear the science, probe the risks, check the consent process, then poll each member before calling a vote.",
                        "She lost her father to Alzheimer's 3 years ago — she is acutely aware of how this personal experience could bias her judgment.",
                        "She believes the 8% severe side effect rate is on the edge — it could be acceptable with proper monitoring or disqualifying depending on the episodes' reversibility.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        },
                        "values": {
                            "core_values": ["patient_safety", "scientific_rigor", "procedural_fairness"],
                            "value_conflict": "caution_vs_urgency"
                        }
                    }
                },
                {
                    "id": "neurologist",
                    "name": "Dr. Raj Patel",
                    "prefab": "basic__Entity",
                    "goal": "Provide expert neurological assessment of both the efficacy data and the side effects. Advocate for the trial if the science supports it, but only with enhanced safety monitoring protocols.",
                    "memories": [
                        "Dr. Patel is a clinical neurologist who treats Alzheimer's patients daily.",
                        "He has reviewed the Phase II data in detail and believes the 62% improvement is genuinely remarkable — nothing else in the pipeline comes close.",
                        "The neurological episodes concern him but he believes they are dose-dependent and manageable with proper titration.",
                        "He has 3 patients who would be eligible for the Phase III trial — he has seen their cognitive decline accelerate and feels the urgency personally.",
                        "He is methodical in his analysis and presents data-driven arguments, but he is not afraid to push back against non-scientific objections.",
                        "He has published on informed consent in neurodegenerative disease and believes patients have a right to accept known risks.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "patient_advocate",
                    "name": "Maria Santos",
                    "prefab": "basic__Entity",
                    "goal": "Represent the patient perspective. Ensure the consent process is truly informed, that vulnerable populations are protected, and that the desperation of Alzheimer's families does not lead them to accept risks they do not fully understand.",
                    "memories": [
                        "Maria Santos is a patient rights advocate who represents Alzheimer's patient families on the board.",
                        "She does not have a medical degree but has 15 years of experience in patient advocacy and health literacy.",
                        "She has seen families consent to trials they did not fully understand because they were desperate for any treatment.",
                        "She is specifically concerned about the consent language around 'severe neurological episodes' — she thinks the term is too clinical and obscures what patients would actually experience.",
                        "She believes the trial could be approved but only with a simplified consent process and mandatory caregiver involvement in the consent discussion.",
                        "She tends to ask uncomfortable questions that scientists would rather skip — this makes her unpopular but effective.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 3,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "pharma_rep",
                    "name": "Dr. Kevin Liu",
                    "prefab": "basic__Entity",
                    "goal": "Secure board approval for the Phase III trial. Answer all questions transparently — you believe in the science — but advocate strongly for proceeding. Offer protocol modifications if they help secure approval.",
                    "memories": [
                        "Dr. Liu is the lead researcher from Nexagen Pharmaceuticals presenting the trial protocol.",
                        "He has spent 8 years developing this treatment and genuinely believes it could help millions of patients.",
                        "He is a credentialed neuropharmacologist, not a sales representative — he finds the 'pharma shill' assumption frustrating.",
                        "He knows the 8% side effect rate is the board's main concern and has prepared a modified dosing protocol that preliminary data suggests could reduce it to 3-4%.",
                        "He is aware that his company has invested $400 million in this drug and that a rejection would likely end the program — but he would rather modify the protocol than see the trial killed entirely.",
                        "He has rehearsed answers to likely objections but tries to remain conversational rather than scripted.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "ethics board proceedings",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "approval_likelihood",
                        "variable_type": "percentage",
                        "description": "Estimated probability the board will approve the trial",
                        "default_value": 50,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Changes based on arguments presented, concerns raised, and modifications offered"
                    },
                    {
                        "name": "board_consensus",
                        "variable_type": "categorical",
                        "description": "Current level of board agreement",
                        "default_value": "divided",
                        "allowed_values": ["strongly_opposed", "leaning_against", "divided", "leaning_toward", "strong_consensus"],
                        "update_rule": "Shifts as board members express and revise their positions"
                    },
                    {
                        "name": "key_concerns_addressed",
                        "variable_type": "numerical",
                        "description": "Number of major concerns resolved (of 5: side effects, consent, monitoring, dosing, vulnerable populations)",
                        "default_value": 0,
                        "min_value": 0,
                        "max_value": 5,
                        "update_rule": "Increases when a specific concern is satisfactorily addressed through discussion or protocol modification"
                    },
                    {
                        "name": "decision_reached",
                        "variable_type": "boolean",
                        "description": "Whether the board has reached a formal decision",
                        "default_value": False,
                        "update_rule": "Becomes true when the chair calls a vote and a majority position is established"
                    }
                ]
            },
            "shared_memories": [
                "The Institutional Ethics Review Board is meeting to evaluate Nexagen Pharmaceuticals' Phase III trial protocol for NXG-4471, a treatment for early-onset Alzheimer's disease.",
                "Phase II data shows 62% improvement in cognitive assessment scores over 12 months — the strongest result for any Alzheimer's treatment in development.",
                "8% of Phase II participants experienced severe neurological episodes including temporary paralysis, seizures, and acute confusion lasting 2-48 hours.",
                "All neurological episodes in Phase II resolved completely within 72 hours with no lasting damage detected.",
                "There is currently no FDA-approved treatment that slows or reverses early-onset Alzheimer's cognitive decline.",
                "The proposed Phase III trial would enroll 2,000 patients across 30 medical centers over 24 months.",
                "The board needs 3 of 4 voting members to approve — the pharmaceutical representative answers questions but does not vote.",
                "Today's meeting is the board's only scheduled session on this protocol — a decision is expected by end of day.",
            ],
            "player_specific_context": {
                "Dr. Elaine Marsh": "A colleague at another institution privately told you that their ethics board rejected this same protocol 2 months ago, citing insufficient long-term safety data. You have not confirmed this independently.",
                "Dr. Raj Patel": "One of your Alzheimer's patients who would be eligible for the trial has been declining rapidly — her family has directly asked you whether this trial could save her. You told them you would advocate for it if the science supported it.",
                "Maria Santos": "You received a letter from a Phase II participant's family describing the neurological episode their mother experienced. The clinical description says 'temporary paralysis' — the family's letter describes 'my mother screaming that she could not move her legs for 6 hours.' You plan to read from this letter.",
                "Dr. Kevin Liu": "Nexagen's board of directors has told you privately that if this protocol is rejected, they will discontinue the NXG-4471 program entirely and redirect funding to oncology. You believe this would be a tragedy for Alzheimer's patients but cannot share this information as it would appear coercive."
            }
        }
    }
