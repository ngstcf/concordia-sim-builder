TEMPLATE = {
        "name": "Focus Group Discussion",
        "description": "A scripted moderator guides diverse participants through a product debate - shows how scripted agents orchestrate free agents",
        "prefab_type": "basic_scripted__Entity",
        "config": {
            "premise": """A market research focus group testing a controversial new app:
an AI-powered dating assistant that selects matches and writes messages for users.

The company has brought together 4 people with very different perspectives:
- A tech enthusiast who loves innovation
- A privacy advocate concerned about data
- A traditional hopeless romantic
- A skeptic who thinks it's all a scam

The moderator's job is to guide the discussion, not dominate it."""
            "",
            # Note: Dr. Chen has 8 scripted prompts. With interviewer game master driving the moderator,
            # max_steps should be ~8-10 to end when script is exhausted.
            # Adjust if you add more scripted prompts.
            "max_steps": 10,
            "agents": [
                {
                    "id": "moderator",
                    "name": "Dr. Chen",
                    "prefab": "basic_scripted__Entity",
                    "goal": "Facilitate a productive discussion and gather diverse opinions",
                    "memories": [],
                    "randomize_choices": False,
                    "components": {
                        "script": [
                            {"name": "Dr. Chen", "line": "Welcome everyone, and thank you for joining our focus group today. We're here to discuss 'LoveBot AI' - a new dating app that uses AI to match people and even write their first messages. Let's go around the table - I'd like each of you to share your initial reaction to this concept."},
                            {"name": "Dr. Chen", "line": "That's a fascinating range of perspectives. Jordan, you mentioned the efficiency aspect - can you elaborate on why you think AI messaging could be better than writing your own?"},
                            {"name": "Dr. Chen", "line": "Thank you. Now Sam, you raised privacy concerns. What specific worries do you have about sharing dating preferences with an AI system?"},
                            {"name": "Dr. Chen", "line": "Excellent point. Maria, as someone who values the romance of traditional dating, how do you feel about AI interfering in what you called the 'magic' of connection?"},
                            {"name": "Dr. Chen", "line": "And Alex, you've been skeptical. After hearing these different viewpoints, has your opinion shifted at all? What would it take to convince you this could actually work?"},
                            {"name": "Dr. Chen", "line": "I'm hearing a tension between convenience and authenticity. Let me ask everyone: If this app could guarantee you'd meet someone compatible within 6 months, but you had to let AI handle your communications, would you use it? Please explain why or why not."},
                            {"name": "Dr. Chen", "line": "This has been incredibly insightful. We have someone who sees it as the future of dating, someone who worries about privacy, someone who misses traditional romance, and someone who remains unconvinced. Before we wrap up, is there anything else anyone wants to add?"},
                            {"name": "Dr. Chen", "line": "Thank you all for sharing your honest thoughts. Your feedback will help shape how this technology develops. That concludes our focus group - you'll each receive a $50 gift card for your participation."}
                        ]
                    }
                },
                {
                    "id": "tech_enthusiast",
                    "name": "Jordan",
                    "prefab": "basic__Entity",
                    "goal": "Make at least 3 specific arguments for why AI messaging is superior to human-written messages, and counter at least 1 privacy concern with a concrete technical solution",
                    "memories": [
                        "You are Jordan, a 28-year-old software engineer who loves all things tech.",
                        "You've used dating apps for years and are tired of ghosting and shallow conversations.",
                        "You believe AI can solve the 'analysis paralysis' of modern dating by making better matches.",
                        "You think people overestimate how 'authentic' their dating messages actually are.",
                        "You're excited about the efficiency potential - no more wasted time on bad matches.",
                        "You're open-minded and tend to be optimistic about new technology."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 3,
                                "agreeableness": 3,
                                "extraversion": 4,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "privacy_advocate",
                    "name": "Sam",
                    "prefab": "basic__Entity",
                    "goal": "Identify at least 2 specific data privacy risks, propose 1 regulatory framework, and challenge Jordan's efficiency claims with evidence",
                    "memories": [
                        "You are Sam, a 32-year-old cybersecurity specialist with a master's in ethics.",
                        "You're deeply concerned about how personal data is collected and used.",
                        "The idea of sharing romantic preferences with an AI company feels invasive to you.",
                        "You worry about bias in AI algorithms - will they only match certain types of people?",
                        "You believe human judgment and serendipity are essential to meaningful connections.",
                        "You're skeptical but willing to have your mind changed with good arguments."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 2,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "romantic",
                    "name": "Maria",
                    "prefab": "basic__Entity",
                    "goal": "Share your personal love story to illustrate the value of organic connection, and articulate why AI-mediated romance is fundamentally different from AI-assisted tasks",
                    "memories": [
                        "You are Maria, a 35-year-old high school English teacher who believes in true love.",
                        "You met your spouse through a chance encounter at a bookstore 10 years ago.",
                        "You think dating apps have already made romance too transactional.",
                        "You believe the magic of romance comes from uncertainty, not optimization.",
                        "The idea of AI writing romantic messages feels deeply wrong to you.",
                        "You're warm and expressive but firm in your traditional values."
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
                        }
                    }
                },
                {
                    "id": "skeptic",
                    "name": "Alex",
                    "prefab": "basic__Entity",
                    "goal": "Challenge each panelist to provide concrete evidence for their claims, and propose 1 specific test that would prove or disprove the app's effectiveness",
                    "memories": [
                        "You are Alex, a 29-year-old marketing manager who's seen too much tech hype.",
                        "You've tried many dating apps and think the problem is people, not algorithms.",
                        "You're skeptical that AI can solve something as complex as human chemistry.",
                        "You suspect this is just another way to monetize loneliness.",
                        "You need concrete evidence, not just promises, to be convinced.",
                        "You're direct and not afraid to challenge assumptions."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 2,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Research Observer",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "The focus group is being recorded for research purposes.",
                "Participants were told to be honest and respectful of differing opinions.",
                "LoveBot AI is a hypothetical app - it doesn't actually exist yet.",
                "The company sponsoring this research wants genuine feedback, not just praise."
            ]
        }
    }
