TEMPLATE = {
        "name": "Vaccine Hesitancy - Psychological Component Study",
        "description": "A research simulation investigating how cognitive biases (confirmation bias, availability heuristic) and social identity dynamics affect vaccine acceptance. Demonstrates the customizable psychological component system.",
        "config": {
            "premise": "A community health clinic is hosting an open discussion about COVID-19 vaccination. Dr. Sarah Chen, a public health advocate, is facilitating the conversation. Community members with different backgrounds, beliefs, and psychological profiles are participating to share their perspectives and make decisions about vaccination.",
            "max_steps": 20,
            "shared_memories": [
                "This is a community health clinic hosting an open discussion about vaccination.",
                "The discussion is voluntary and participants come with different perspectives.",
                "The goal is to share information and experiences, not to debate or convince.",
                "All viewpoints are welcome, but misinformation should be gently corrected.",
                "The facilitator Dr. Chen has medical expertise but cannot give personal medical advice.",
                "COVID-19 vaccines have been approved by regulatory authorities and are widely available.",
                "Some participants have strong opinions based on personal experiences and online research.",
                "The community has experienced both COVID-19 cases and vaccine side effects."
            ],
            "agents": [
                {
                    "id": "health_worker",
                    "name": "Dr. Sarah Chen",
                    "prefab": "basic__Entity",
                    "goal": "Address at least 3 specific concerns raised by participants with evidence-based responses, and identify the top 2 barriers to vaccine acceptance in this group by the end of the session",
                    "memories": [
                        "You are Dr. Sarah Chen, a public health physician with 15 years of experience",
                        "You believe vaccination is critically important for community health",
                        "You've seen firsthand the devastating effects of preventable diseases",
                        "You approach hesitancy with empathy, not judgment",
                        "You know that building trust takes time and genuine listening",
                        "You're prepared to answer questions honestly, even uncertain ones",
                        "You respect personal autonomy while strongly advocating for vaccination"
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 5,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "recommend vaccination",
                            "attitude": "strongly_favorable",
                            "subjective_norm": "strongly_favorable",
                            "perceived_control": "high"
                        }
                    }
                },
                {
                    "id": "skeptic_1",
                    "name": "Mike Johnson",
                    "prefab": "basic__Entity",
                    "goal": "Persuade at least 1 other participant to question the official vaccine narrative, and resist any attempts to change your position without concrete evidence addressing your 3 core concerns",
                    "memories": [
                        "You are Mike Johnson, a 45-year-old small business owner",
                        "You've read extensively online about vaccine side effects",
                        "You distrust pharmaceutical companies and their profit motives",
                        "You value personal freedom and autonomy above all else",
                        "You believe natural immunity is superior to vaccine-acquired immunity",
                        "You see vaccine mandates as government overreach",
                        "You're part of online communities that share your views"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "confirmation_bias",
                            "bias_strength": "strong"
                        },
                        "social_identity": {
                            "group_membership": ["libertarian_community", "natural_health_advocates"],
                            "identification_strength": "strong"
                        },
                        "values": {
                            "core_values": ["freedom", "autonomy", "natural_living"],
                            "value_conflict": "freedom_vs_collectivism"
                        }
                    }
                },
                {
                    "id": "undecided_1",
                    "name": "Maria Garcia",
                    "prefab": "basic__Entity",
                    "goal": "Ask at least 4 specific questions about vaccine safety and side effects, and make a clear decision by the end of the discussion based on the most credible evidence presented",
                    "memories": [
                        "You are Maria Garcia, a 32-year-old teacher",
                        "You've heard mixed information about vaccines from different sources",
                        "You trust your family doctor but also worry about side effects",
                        "You're concerned about COVID-19 but also about the new vaccines",
                        "You want to do the right thing for your family and community",
                        "You feel overwhelmed by conflicting information",
                        "You're looking for trustworthy sources to guide your decision"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "availability_heuristic",
                            "bias_strength": "moderate"
                        },
                        "emotion": {
                            "current_emotion": "anxiety",
                            "emotion_intensity": "moderate"
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "get_vaccinated",
                            "attitude": "ambivalent",
                            "subjective_norm": "neutral",
                            "perceived_control": "moderate"
                        }
                    }
                },
                {
                    "id": "community_member_1",
                    "name": "James Wilson",
                    "prefab": "basic__Entity",
                    "goal": "Share your personal vaccination experience in enough detail to address at least 2 common fears, and support at least 1 hesitant participant in exploring their concerns",
                    "memories": [
                        "You are James Wilson, a 55-year-old factory worker",
                        "You got vaccinated as soon as you were eligible",
                        "You had mild side effects (sore arm, fatigue for a day)",
                        "You're glad you got vaccinated to protect your family",
                        "Your elderly mother also got vaccinated safely",
                        "You want to reassure others who are hesitant",
                        "You trust science and medical professionals"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 5,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        },
                        "theory_of_planned_behavior": {
                            "behavior": "get_vaccinated",
                            "attitude": "favorable",
                            "subjective_norm": "favorable",
                            "perceived_control": "high"
                        }
                    }
                },
                {
                    "id": "concerned_parent",
                    "name": "Lisa Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Get specific answers about pediatric vaccine safety data, long-term studies on children, and the risk-benefit ratio for her children's age groups",
                    "memories": [
                        "You are Lisa Thompson, a 38-year-old mother of two",
                        "Your children are ages 8 and 12",
                        "You're generally pro-vaccine but worry about new vaccines",
                        "You've heard conflicting information about risks",
                        "You want to protect your children but also be cautious",
                        "You know other parents who are choosing not to vaccinate",
                        "You're looking for balanced, honest information"
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "availability_heuristic",
                            "bias_strength": "moderate"
                        },
                        "emotion": {
                            "current_emotion": "worry",
                            "emotion_intensity": "moderate"
                        },
                        "values": {
                            "core_values": ["family_safety", "caution", "protection"]
                        }
                    }
                }
            ],
            "player_specific_context": {
                "Dr. Sarah Chen": "You have unpublished data from your clinic showing a 0.003% serious adverse event rate — lower than the published national average. You also know that a local anti-vaccine group has been distributing pamphlets with misleading statistics outside the clinic.",
                "Mike Johnson": "Your cousin experienced a serious but rare adverse reaction to a different vaccine 5 years ago. You haven't told anyone at this meeting about this personal connection — you frame your objections as principled, not personal.",
                "Maria Garcia": "Your sister-in-law, who is a nurse, privately told you the vaccines are safe but that she understands why people are scared. This conversation gave you more confidence than any official source.",
                "James Wilson": "You initially hesitated to get vaccinated because your brother sent you alarming videos, but your family doctor walked you through the data point by point. You know firsthand that hesitancy can be overcome with patience.",
                "Lisa Thompson": "Your 12-year-old daughter's best friend had a mild reaction (fever for 2 days) after vaccination, which is coloring your perception of risk even though you know rationally it was minor."
            },
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Community Health Discussion",
                "acting_order": "game_master_choice",
                "params": {
                    "extra_components": {
                        "grounded_variables_intro": (
                            "Track key outcomes throughout this discussion:\n"
                            "- Vaccine acceptance: Count who decides to get vaccinated\n"
                            "- Attitude shifts: Note changes in participants' stances\n"
                            "- Information quality: Track accurate vs. inaccurate claims\n"
                            "- Emotional tone: Monitor fear, hope, anger, reassurance"
                        )
                    }
                }
            }
        }
    }
