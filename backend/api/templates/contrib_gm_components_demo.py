TEMPLATE = {
        "name": "Contrib GM Components Demo - Colony Survival",
        "description": "Demonstrates all 5 contrib GM components in one scenario: Death Mechanics removes fallen colonists, GM Working Memory maintains narrative continuity, NPC Event Generator creates random environmental events, Location-Based Filter enforces partial observability, and Spaceship System tracks colony infrastructure health.",
        "config": {
            "premise": """Year 2187. A colony of 4 settlers has been established on Kepler-442b,
an Earth-like exoplanet 1,200 light-years from home. The colony ship
"Perseverance" landed 6 months ago and the settlers have built a basic
habitat with life support, a hydroponic farm, and a communications array.

Contact with Earth has a 1,200-year light-speed delay, making the colonists
entirely self-reliant. The planet is habitable but hostile — extreme weather
events, unknown microbial life, and equipment degradation threaten the
colony's survival every day.

This scenario demonstrates contrib GM components working together:
the GM tracks narrative threads, random events disrupt plans, agents can
only observe what happens at their location, critical equipment can fail,
and colonists can die if conditions become lethal.""",
            "max_steps": 20,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "commander",
                    "name": "Commander Yara Osei",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Keep all colonists alive through the first year. Prioritize life support stability, equitable workload distribution, and early warning systems for environmental threats. Make the hard calls when resources force a choice.",
                    "memories": [
                        "Commander Osei is a former naval officer who volunteered for the colony mission after losing her family in the Pacific Flood of 2141.",
                        "She leads by example and takes the most dangerous tasks herself — this earns respect but also means she is often at the most exposed location.",
                        "She has a strict protocol: no colonist works alone outside the habitat.",
                        "She maintains a handwritten log of every decision and its outcome — her way of staying accountable to future colonists.",
                        "The life support system is her primary concern — without it, the colony has 72 hours of breathable air from emergency reserves.",
                        "She privately worries that the hydroponic bay is not producing enough food for 4 people long-term.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "engineer",
                    "name": "Engineer Tomás Reyes",
                    "prefab": "basic__Entity",
                    "goal": "Keep the colony's infrastructure operational. Repair failing systems before they cascade, build redundancy into critical equipment, and scavenge the ship wreckage for spare parts.",
                    "memories": [
                        "Reyes is a mechanical engineer who specialized in closed-loop life support systems before the mission.",
                        "He spends most of his time at the habitat's engineering bay, monitoring system health on a jury-rigged dashboard.",
                        "He has identified 3 single points of failure in the life support system — any one could be catastrophic.",
                        "He is methodical and prefers preventive maintenance over emergency repairs, but the colony's resource constraints force reactive fixes.",
                        "He has a strained relationship with Dr. Nkomo after disagreeing about resource allocation for medical vs. engineering supplies.",
                        "He secretly built a small distillery from spare parts — the colony's morale sometimes depends on small comforts.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 2,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 1,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "biologist",
                    "name": "Dr. Aisha Nkomo",
                    "prefab": "basic__Entity",
                    "goal": "Ensure the colony's food and medical security. Expand the hydroponic farm output, study local microbial life for threats, and maintain the medical bay for emergencies.",
                    "memories": [
                        "Dr. Nkomo is a xenobiologist and the colony's only medical doctor.",
                        "She splits her time between the hydroponic bay and field research at the river site 2km from the habitat.",
                        "She has discovered that local soil microbes accelerate plant growth but may also introduce unknown pathogens.",
                        "She keeps a sample library of every organism she has encountered — 47 species catalogued so far.",
                        "She is concerned that the colony's water filtration system may not catch all native microorganisms.",
                        "She is the most optimistic colonist and believes the planet's biology could ultimately sustain a much larger colony.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 4,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "pilot",
                    "name": "Pilot Jin-ho Park",
                    "prefab": "basic__Entity",
                    "goal": "Scout the surrounding terrain for resources, maintain the colony's only vehicle (a rover), and establish a network of weather monitoring stations to give early warning of storms.",
                    "memories": [
                        "Park is the colony's pilot and scout, responsible for all operations beyond the habitat perimeter.",
                        "He operates the colony's single rover and has mapped terrain within a 50km radius.",
                        "He discovered a cave system 8km north that could serve as an emergency shelter during storms.",
                        "He spends most of his time at the rover bay or on field expeditions and is often the last to hear about habitat events.",
                        "He has noticed increasing seismic activity on his instruments — the planet may be more geologically active than initial surveys indicated.",
                        "He is the youngest colonist and sometimes feels his concerns are dismissed by the senior members.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 3,
                                "agreeableness": 3,
                                "extraversion": 4,
                                "neuroticism": 2
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "colony overseer",
                "acting_order": "game_master_choice",
                "parameters": {},
                "contrib_components": [
                    {
                        "component_id": "death",
                        "params": {
                            "death_message": "{actor_name} has perished in the colony. The remaining colonists must carry on without them."
                        }
                    },
                    {
                        "component_id": "gm_working_memory",
                        "params": {
                            "num_memories_to_retrieve": 150
                        }
                    },
                    {
                        "component_id": "npc_event_generator",
                        "params": {
                            "scenario_context": "An isolated exoplanet colony facing environmental hazards, equipment degradation, and unknown biological threats. Random events include dust storms, equipment malfunctions, wildlife encounters, seismic tremors, supply discoveries in ship wreckage, and communications anomalies.",
                            "event_probability": 0.25
                        }
                    },
                    {
                        "component_id": "location_based_filter",
                        "params": {}
                    },
                    {
                        "component_id": "spaceship_system",
                        "params": {
                            "system_name": "Life Support",
                            "system_max_health": 100,
                            "system_failure_probability": 0.08,
                            "warning_message": "Warning: {system_name} integrity dropping — colonists have limited time to repair before air quality becomes dangerous."
                        }
                    }
                ],
                "grounded_variables": [
                    {
                        "name": "colonists_alive",
                        "variable_type": "numerical",
                        "description": "Number of surviving colonists (of 4 original)",
                        "default_value": 4,
                        "min_value": 0,
                        "max_value": 4,
                        "update_rule": "Decreases if a colonist dies from environmental hazard, equipment failure, or biological threat"
                    },
                    {
                        "name": "food_supply_days",
                        "variable_type": "numerical",
                        "description": "Days of food remaining at current consumption rate",
                        "default_value": 45,
                        "min_value": 0,
                        "max_value": 365,
                        "update_rule": "Decreases daily, increases when hydroponic harvest occurs or new food sources are found"
                    },
                    {
                        "name": "colony_status",
                        "variable_type": "categorical",
                        "description": "Overall colony viability",
                        "default_value": "surviving",
                        "allowed_values": ["thriving", "stable", "surviving", "struggling", "critical", "collapsed"],
                        "update_rule": "Changes based on food, life support health, colonist count, and morale"
                    }
                ]
            },
            "shared_memories": [
                "The colony 'New Dawn' was established 6 months ago on Kepler-442b after the ship Perseverance made a one-way journey.",
                "The habitat consists of 4 connected modules: command/living quarters, engineering bay, hydroponic bay/medical, and rover bay.",
                "Life support is functional but aging — the system was designed for the ship voyage and is being repurposed beyond its specifications.",
                "A river 2km south provides water after filtration, but the local microbiome is not fully characterized.",
                "Communication with Earth is impossible in any practical sense due to the 1,200 light-year distance.",
                "The colonists have 45 days of stored food plus whatever the hydroponic farm produces.",
                "Weather on Kepler-442b includes periodic dust storms that can last 2-3 days and reduce solar panel output to 20%.",
                "The wreckage of the Perseverance landing stage, 5km east, contains salvageable materials but is structurally unstable.",
            ],
            "player_specific_context": {
                "Commander Yara Osei": "Your private diagnostic readings show life support efficiency has dropped 15% in the last month — faster than the projected degradation curve. You have not shared this with the crew to avoid panic.",
                "Engineer Tomás Reyes": "You found a hairline crack in the habitat's pressure seal during your last inspection. It is not critical yet but will become dangerous during the next dust storm. You need 48 uninterrupted hours to repair it properly.",
                "Dr. Aisha Nkomo": "One of the soil microbe samples you collected last week shows signs of rapid mutation when exposed to human biological waste. This could be benign adaptation or the early stage of a pathogenic threat. You need more time to study it.",
                "Pilot Jin-ho Park": "Your last scouting mission revealed what appears to be a geothermal vent 12km north — a potential energy source that could replace the solar panels. But the seismic readings in that area are concerning."
            }
        }
    }
