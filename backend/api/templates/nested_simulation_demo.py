TEMPLATE = {
        "name": "Nested Simulation Demo - Phone Call Planning",
        "description": "Demonstrates nested simulations (PhoneGameMaster pattern) where an agent runs a mini-simulation to gather information before acting in the main simulation. Models anticipatory social cognition — mentally rehearsing a conversation before having it.",
        "config": {
            "premise": """Alice is planning what to bring to a potluck dinner party this Saturday.
The host, Maria, is particular about food and has strong opinions. Alice wants
to bring something that will complement the other dishes without duplicating
anyone else's contribution. She decides to call her friend Bob, who is closer
to Maria and knows what other guests are planning.""",
            "max_steps": 15,
            "shared_memories": [
                "There is a potluck dinner party at Maria's house this Saturday evening for 8 guests.",
                "Maria is a talented home cook who values creative, well-made dishes over store-bought items.",
                "Alice is deciding what to bring and wants to avoid duplicating anyone else's contribution.",
                "Bob has already spoken with Maria and several other guests about their plans.",
                "The host requested each guest bring one dish to share, either savory or sweet.",
            ],
            "agents": [
                {
                    "id": "alice",
                    "name": "Alice",
                    "prefab": "basic__Entity",
                    "goal": "Settle on a specific dish to bring that complements the other contributions, avoids duplicates, and showcases your cooking skills — ideally something you can confirm with Bob before committing",
                    "memories": [
                        "Alice is an enthusiastic home cook who recently completed a French pastry course.",
                        "She is considering bringing either a lemon tart, a charcuterie board, or a Thai green curry.",
                        "She wants to impress Maria specifically, who once complimented her baking.",
                        "Alice tends to overthink decisions and appreciates when someone gives her a clear recommendation.",
                        "She dislikes arriving at a party to discover someone else brought the same thing.",
                        "She has a mild dairy allergy herself but can cook with dairy for others.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Alice calls Bob to ask what she should bring to Maria's dinner party. Bob knows what several other guests are planning to bring and can offer specific advice.",
                        "max_steps": 5,
                        "shared_memories": [
                            "Alice is calling Bob for advice about Maria's dinner party.",
                            "Bob has already coordinated with Maria and knows the guest list.",
                            "They are close friends who often cook together and trust each other's taste.",
                        ],
                        "agents": [
                            {
                                "id": "alice_nested",
                                "name": "Alice",
                                "prefab": "basic__Entity",
                                "goal": "Find out exactly what other guests are bringing so you can choose something complementary",
                                "memories": [
                                    "Alice is torn between a few options and needs Bob's insider knowledge to decide.",
                                    "She trusts Bob's judgment on food pairings and social dynamics.",
                                    "She wants a definitive recommendation, not more options to agonize over.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "bob_nested",
                                "name": "Bob",
                                "prefab": "basic__Entity",
                                "goal": "Give Alice a clear, specific recommendation based on what you know about the other dishes",
                                "memories": [
                                    "Bob knows Maria is making her signature paella as the main course.",
                                    "Bob knows Carlos is bringing two bottles of Spanish wine.",
                                    "Bob heard that Lisa is bringing a green salad and bread.",
                                    "Bob thinks a dessert would be the best gap to fill since no one else has claimed one.",
                                    "Bob remembers Alice's lemon tart was exceptional last time.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What did Alice learn about what to bring to the party? What specific dishes are other guests bringing, and what gap did Bob identify? What was Bob's final recommendation?"
                    }
                },
                {
                    "id": "bob_main",
                    "name": "Bob",
                    "prefab": "basic__Entity",
                    "goal": "Help Alice finalize her dish choice and offer to coordinate timing so they can arrive at the party together",
                    "memories": [
                        "Bob is Alice's close friend and an informal social coordinator in their friend group.",
                        "Bob is knowledgeable about food pairings and enjoys helping people plan.",
                        "He wants Alice to bring her lemon tart because it was a hit at his birthday party.",
                        "Bob tends to be diplomatic but decisive when asked for advice.",
                        "He is also bringing something to the party: a cheese board with local artisanal selections.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "conversation guide",
                "acting_order": "game_master_choice",
                "parameters": {}
            }
        }
    }
