TEMPLATE = {
        "name": "Coffee Shop Encounter",
        "description": "A minimal social interaction demo illustrating spontaneous conversation dynamics, turn-taking, and goal-directed dialogue between acquaintances with competing priorities.",
        "config": {
            "premise": """A sunny Monday morning at "The Daily Grind" coffee shop in downtown Portland.
Alice, a regular customer, walks in and notices Bob sitting at a corner table
working intently on a laptop. The espresso machine just broke, so the barista
is apologetically offering drip coffee only — creating a shared moment of mild
inconvenience. Bob has a presentation deadline in two hours.""",
            "max_steps": 5,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "alice",
                    "name": "Alice",
                    "prefab": "basic__Entity",
                    "goal": "Discover what Bob is working on, assess whether there is a potential collaboration opportunity, and ideally exchange contact information before leaving",
                    "memories": [
                        "Alice is a software engineer at a mid-sized startup specializing in machine learning infrastructure.",
                        "She is naturally curious and tends to ask probing follow-up questions when something interests her.",
                        "She recently read about a novel approach to real-time data pipelines that excited her and she is eager to discuss it.",
                        "She knows Bob casually from previous coffee shop visits but they have never talked about work in detail.",
                        "Alice is warm and direct in conversation; she gets to the point quickly but with genuine friendliness.",
                        "She is looking for collaborators on a side project involving predictive analytics."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "bob",
                    "name": "Bob",
                    "prefab": "basic__Entity",
                    "goal": "Finish your data analysis draft before the noon deadline while remaining polite; deflect extended conversation unless Alice offers something genuinely useful to your project",
                    "memories": [
                        "Bob is a data scientist at a healthcare analytics firm with a presentation due at noon today.",
                        "He is focused and slightly anxious about his deadline, but he is too polite to be dismissive.",
                        "He warms up quickly once he realizes someone genuinely understands his work.",
                        "He is currently struggling with a feature engineering problem in his patient outcomes model.",
                        "Bob prefers structured conversations and tends to steer small talk toward substance.",
                        "He respects people who can offer concrete help rather than vague encouragement."
                    ],
                    "randomize_choices": True
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Narrator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "The coffee shop is quiet with soft jazz playing. It is 10 AM on a Monday.",
                "The espresso machine just broke, so only drip coffee is available — both Alice and Bob noticed the barista's apology.",
                "A help-wanted flyer for a local tech meetup is pinned to the community board near the entrance.",
                "Alice and Bob have exchanged brief greetings on maybe a dozen previous visits but never had a real conversation.",
                "The shop has good WiFi and is popular with remote workers and freelancers."
            ]
        }
    }
