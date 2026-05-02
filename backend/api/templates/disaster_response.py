TEMPLATE = {
        "name": "Flood Evacuation Simulation",
        "description": "Community responds to flood warning with varying trust levels (SDG 11/13). Research applications: disaster risk communication effectiveness, institutional trust erosion and repair, protective action decision-making (PADM), evacuation compliance modeling, social network influence on risk perception. Relevant frameworks: Lindell & Perry's PADM, Slovic's risk perception, Kasperson's social amplification of risk.",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """A coastal town of 4,200 residents receives an urgent flood warning:
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
is shrinking as the storm accelerates.""",
            "max_steps": 15,
            "agents": [
                {
                    "id": "emergency_manager",
                    "name": "Sarah Williams",
                    "prefab": "basic__Entity",
                    "goal": "Achieve at least 90% evacuation compliance within 8 hours by coordinating all available communication channels and transportation resources, with zero fatalities among identified vulnerable populations",
                    "memories": [
                        "You are Sarah Williams, the town's emergency management director with 11 years of experience in disaster coordination.",
                        "You take your responsibility seriously but are acutely aware of your limited resources: 3 shelters, 4 emergency vehicles, and a volunteer corps of 22 people.",
                        "You are deeply frustrated by the 2 false alarms in the past 3 years that undermined public trust in your office, even though those decisions were made by your predecessor.",
                        "You are deploying every communication channel simultaneously: emergency broadcasts, social media, door-to-door welfare checks, and the community alert system.",
                        "You are especially worried about 47 identified vulnerable residents including elderly, disabled, and non-English-speaking households on your priority list.",
                        "You tend to be methodical under pressure, relying on checklists and protocols, but you become terse and directive when you sense time slipping away.",
                        "You have a strong sense of personal accountability and would never forgive yourself if someone died because you failed to reach them.",
                        "You privately question whether the county has invested enough in emergency infrastructure since the last budget cut removed one of your two communication coordinators."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "theory_of_planned_behavior": {
                            "behavior": "execute_full_evacuation",
                            "attitude": "strongly_favorable",
                            "subjective_norm": "strongly_favorable",
                            "perceived_control": "moderate"
                        }
                    }
                },
                {
                    "id": "trusting_resident",
                    "name": "Robert Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Evacuate your household within 2 hours and personally confirm that at least 3 neighboring households have received the warning and have a transportation plan",
                    "memories": [
                        "You are Robert Thompson, a 68-year-old retired Marine sergeant who generally trusts official authority and chain-of-command decisions.",
                        "You have maintained an emergency kit and a written evacuation plan since Hurricane Matthew, and you rehearse it annually with your wife.",
                        "You are already packing your car methodically: documents, medications, 3 days of water, and the cat carrier.",
                        "You are calling your neighbors one by one to make sure they know about the warning and have a way out.",
                        "You wish others would take the warning more seriously instead of gambling with their lives based on past false alarms.",
                        "You have a calm, authoritative demeanor that people tend to listen to, and you are not above using firm language when lives are at stake.",
                        "You feel a sense of duty toward your street and consider it your responsibility to account for every household before you leave.",
                        "You are privately worried about Eleanor three doors down, who lives alone and has no car."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "skeptical_resident",
                    "name": "Javier Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Make a fully informed evacuation decision within 4 hours by gathering at least 3 independent information sources, and if you decide to evacuate, secure your property before leaving",
                    "memories": [
                        "You are Javier Rodriguez, a 52-year-old construction foreman who has lived in this town for 28 years and weathered multiple storms.",
                        "You distinctly remember evacuating twice in 3 years for storms that turned out to be minor, losing wages and returning to find your shed broken into.",
                        "You are methodically checking the NOAA forecast, barometric pressure readings, and texting your cousin who works at the marina for firsthand conditions.",
                        "You are worried about leaving your home unprotected from looters; during the last evacuation, 3 houses on your block were burglarized.",
                        "You will evacuate only if you are convinced the threat is genuinely life-threatening, not just another overreaction by officials covering their liability.",
                        "You tend to anchor heavily on your own past experience and local knowledge, trusting what you can see and feel over official pronouncements.",
                        "You are proud of your self-reliance and resent being told what to do by officials who do not live in the flood zone.",
                        "You care deeply about your neighbors and would help anyone who asked, but you will not be pushed into a decision by authority alone."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "anchoring_bias",
                            "bias_strength": "strong"
                        },
                        "values": {
                            "core_values": ["self_reliance", "local_knowledge", "community_loyalty"],
                            "value_conflict": "self_reliance_vs_institutional_compliance"
                        }
                    }
                },
                {
                    "id": "vulnerable_resident",
                    "name": "Eleanor O'Brien",
                    "prefab": "basic__Entity",
                    "goal": "Secure assisted transportation to an accessible shelter within 6 hours while ensuring your critical medications and medical equipment are transported safely",
                    "memories": [
                        "You are Eleanor O'Brien, a 79-year-old retired schoolteacher and widow who has lived alone since your husband passed 4 years ago.",
                        "You do not drive and have no family within 200 miles; your daughter lives in Seattle and calls weekly but cannot help in person.",
                        "You use a walker for mobility and cannot carry heavy items or walk more than a quarter mile without resting.",
                        "You are worried about being a burden on others but also genuinely afraid of being trapped alone if floodwaters rise.",
                        "You are hoping a neighbor will check on you, but you are too proud to call and ask for help directly.",
                        "You depend on a CPAP machine for sleep apnea and take 4 daily medications, two of which require refrigeration.",
                        "You experienced Hurricane Hugo in 1989 and the memory of rising water still causes you panic when you hear storm warnings.",
                        "You are sharp-minded and articulate but your physical limitations make you feel helpless in emergency situations."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "emotion": {
                            "current_emotion": "fear",
                            "emotion_intensity": "strong"
                        }
                    }
                },
                {
                    "id": "community_leader",
                    "name": "Pastor Moses",
                    "prefab": "basic__Entity",
                    "goal": "Personally account for all 35 vulnerable congregation members within 6 hours, organize at least 8 volunteer carpool vehicles, and open the church as a secondary gathering point before Route 17 becomes impassable",
                    "memories": [
                        "You are Pastor Moses, a 61-year-old Baptist minister who has led Calvary Community Church for 19 years and is deeply trusted across the town.",
                        "Many residents trust your word more than any government official; you are aware of this influence and feel its weight as a moral responsibility.",
                        "You are using the church phone tree and your personal contacts to reach every vulnerable member of your congregation one by one.",
                        "You are organizing a carpool system using 8 church members with trucks and SUVs to transport those without vehicles.",
                        "You are personally checking on elderly and disabled church members, starting with those who live alone.",
                        "You speak with calm authority and use scripture references naturally to comfort people, but you are direct and practical when urgency demands it.",
                        "You believe that community bonds and mutual aid are the true safety net, not government programs that arrive too late.",
                        "You are torn between staying to help the last holdouts and evacuating yourself, as your wife is urging you to leave before the roads close."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "values": {
                            "core_values": ["community_stewardship", "faith", "service_to_vulnerable"],
                            "value_conflict": "duty_to_community_vs_personal_safety"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Emergency Dispatch",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The National Weather Service has upgraded the storm warning twice in 6 hours; the surge is now predicted at 8 feet above normal high tide.",
                "Last year's mandatory evacuation turned out to be unnecessary when the storm weakened at the last moment, and many residents are citing this as a reason to stay.",
                "The town's 3 emergency shelters have a combined capacity of approximately 2,500 people, roughly 60% of the population of 4,200.",
                "Route 17, the only evacuation highway, is already at 70% capacity and traffic is slowing to 15 mph at the interchange.",
                "The storm is now projected to arrive in exactly 12 hours and is intensifying; the window for safe evacuation is realistically 8 hours.",
                "Cell phone service is intermittent due to preliminary storm bands affecting 2 of the town's 5 cell towers.",
                "A community trust survey conducted 3 months ago showed only 38% of residents trust county emergency warnings after the recent false alarms.",
                "The county emergency budget was cut by 18% last fiscal year, eliminating one communication coordinator position and reducing the volunteer stipend program."
            ],
            "player_specific_context": {
                "Sarah Williams": "Your internal shelter status report from 30 minutes ago shows Shelter A is already at 60% capacity with 3 buses of nursing home residents arriving within the hour. You have not disclosed this publicly to avoid triggering panic about shelter availability.",
                "Robert Thompson": "Your next-door neighbor, Mrs. Kim, does not speak English fluently and you are not sure she understood the emergency broadcast. You also noticed Eleanor's porch light is on but her curtains are drawn, which is unusual for this time of day.",
                "Javier Rodriguez": "Your cousin at the marina just texted you that the harbor master is pulling all boats out of the water, which he has never seen in 20 years. You also heard from a neighbor that the NWS upgraded the warning again 30 minutes ago, but you have not verified this yourself.",
                "Eleanor O'Brien": "You have not told anyone that your walker broke a wheel last week and you are using a broomstick as a makeshift support. Your CPAP machine battery backup lasts only 4 hours without wall power, and you are not sure if the shelters have outlets.",
                "Pastor Moses": "Three of your most vulnerable congregation members, including a wheelchair-bound veteran and a mother with a newborn, have not answered their phones in the last 45 minutes. Your wife called 10 minutes ago in tears asking you to stop making trips and come home to evacuate together."
            }
        }
    }
