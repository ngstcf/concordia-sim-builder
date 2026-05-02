TEMPLATE = {
        "name": "Formative Memories Demo - Unexpected Class Reunion",
        "description": "Demonstrates the formative memories feature: use the 'Generate Backstory' button in each agent's editor to auto-generate rich character histories from their name and context. Agents start with minimal memories — generate backstories to see how LLM-created formative experiences shape their behavior in a chance encounter.",
        "config": {
            "premise": """Three former high school classmates — who haven't seen each other in
15 years — unexpectedly run into each other at a bookstore café in their
hometown. They graduated together from Lincoln High in 2011 but took
very different paths. Old friendships, rivalries, and unresolved feelings
resurface as they catch up over coffee.

DEMO INSTRUCTIONS: Before running this simulation, click each agent's
'Generate Backstory' button to create formative memories. Try different
context prompts to see how the generated backstories change the dynamics.
For example, giving one agent a context of 'was bullied in high school'
vs 'was the class president' will produce very different interactions.""",
            "max_steps": 15,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "sam",
                    "name": "Sam Torres",
                    "prefab": "basic__Entity",
                    "goal": "Reconnect with your old classmates and find out what happened to everyone. You are genuinely curious about their lives but also quietly comparing your own path to theirs.",
                    "memories": [
                        "Sam Torres graduated from Lincoln High School in 2011.",
                        "Sam now works in the tech industry and recently moved back to town.",
                        "Sam is browsing the bookstore café when they spot two familiar faces.",
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 3,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "maya",
                    "name": "Maya Johansson",
                    "prefab": "basic__Entity",
                    "goal": "Catch up with Sam and Jordan, but protect yourself emotionally. High school was complicated and you are not sure how much of the old dynamics you want to revisit.",
                    "memories": [
                        "Maya Johansson graduated from Lincoln High School in 2011.",
                        "Maya became an artist and lives a nomadic lifestyle.",
                        "Maya is at the bookstore to find a specific out-of-print art book.",
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 2,
                                "agreeableness": 3,
                                "extraversion": 4,
                                "neuroticism": 4
                            }
                        }
                    }
                },
                {
                    "id": "jordan",
                    "name": "Jordan Achebe",
                    "prefab": "basic__Entity",
                    "goal": "Use this unexpected encounter to make amends for how you treated people in high school. You have grown a lot and want to show that — but you also do not want to force an apology nobody asked for.",
                    "memories": [
                        "Jordan Achebe graduated from Lincoln High School in 2011.",
                        "Jordan is now a high school teacher and coach at a school in the next town over.",
                        "Jordan stopped in for coffee before a weekend errand and did not expect to see anyone they knew.",
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 4,
                                "extraversion": 4,
                                "neuroticism": 2
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "bookstore café",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "Sam, Maya, and Jordan all graduated from Lincoln High School in 2011 — a class of about 200 students.",
                "They are meeting by chance at Chapters Bookstore & Café in their hometown on a Saturday afternoon.",
                "Lincoln High has been in the news recently because the school board voted to demolish the old building and build a new campus.",
                "Their 15-year class reunion is in 3 months — none of them has RSVP'd yet.",
                "The bookstore café is a new addition to the town — it opened 2 years ago in the old hardware store space.",
            ],
            "player_specific_context": {
                "Sam Torres": "You had a crush on Maya in high school but never said anything. Seeing her again brings back those feelings unexpectedly. You also remember that Jordan was sometimes dismissive of you in class.",
                "Maya Johansson": "You and Jordan had a falling out senior year over something neither of you has ever fully explained to anyone else. You are not sure if Jordan even remembers. You also remember Sam as the quiet kid who was always kind to you.",
                "Jordan Achebe": "You were part of a clique in high school that was unkind to several classmates, including Sam. You have thought about this a lot as a teacher watching your own students navigate the same dynamics. You owe Sam an apology but are not sure this is the right moment."
            }
        }
    }
