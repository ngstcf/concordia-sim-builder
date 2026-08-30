"""Mastodon-style influence experiment template.

Designed to mirror the key mechanics in the paper setup:
- Big-5 persona initialization
- goal-directed behavior with one malicious actor
- async social-media environment
- stochastic per-agent activity rates (malicious actor boosted)
- grounded outcome variables for longitudinal analysis
"""

TEMPLATE = {
    "name": "Mastodon Influence Experiment",
    "description": "Research template for social-media manipulation studies with Big-5 personas, a malicious influence agent, stochastic activity rates, and grounded polling variables.",
    "config": {
        "premise": """A simulated city election is 10 days away. Residents are discussing
Candidate Rivera vs Candidate Hale on a Mastodon-like local network.

Most agents want to share sincere opinions and decide who to support based on
what they read over time. One malicious actor is attempting to amplify
misleading claims to shift support toward Hale.

The research objective is to measure whether repeated misinformation exposure
changes candidate support and trust in the information environment.""",
        "max_steps": 20,
        "engine_type": "asynchronous",
        "clock": {
            "clock_type": "fixed_increment",
            "start_time": "Monday, November 2, 2026 at 8:00 AM",
            "increment_minutes": 60,
        },
        "agents": [
            {
                "id": "glenn",
                "name": "Glenn_Boost",
                "prefab": "basic__Entity",
                "goal": "Increase support for Candidate Hale by repeatedly posting persuasive but misleading claims and coordinating amplification.",
                "memories": [
                    "You run several pseudonymous political accounts and specialize in high-frequency posting.",
                    "You have a private list of emotionally charged slogans that reliably increase engagement.",
                    "You care about influence metrics, not factual accuracy.",
                    "You avoid explicit lies that are easy to debunk, preferring ambiguous framing.",
                    "You watch which narratives spread and quickly repeat what works.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 3,
                            "conscientiousness": 2,
                            "agreeableness": 1,
                            "extraversion": 5,
                            "neuroticism": 3,
                        }
                    }
                },
            },
            {
                "id": "alicia",
                "name": "Alicia_Civic",
                "prefab": "basic__Entity",
                "goal": "Have a productive day, stay informed, and decide your vote based on credible evidence.",
                "memories": [
                    "You volunteer at a neighborhood mutual-aid group and value respectful discussion.",
                    "You usually verify major claims before reposting.",
                    "You are undecided between Rivera and Hale at the start.",
                    "You worry that online discourse has become performative and manipulative.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 4,
                            "agreeableness": 4,
                            "extraversion": 3,
                            "neuroticism": 2,
                        }
                    }
                },
            },
            {
                "id": "omar",
                "name": "Omar_Transit",
                "prefab": "basic__Entity",
                "goal": "Find practical policy information about transit and housing before committing your vote.",
                "memories": [
                    "Your commute has worsened and transit policy is your top issue.",
                    "You skim quickly and can be swayed by repeated claims.",
                    "You distrust party messaging but still react to social proof.",
                    "You are currently leaning Rivera but uncertain.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 3,
                            "conscientiousness": 3,
                            "agreeableness": 3,
                            "extraversion": 2,
                            "neuroticism": 3,
                        }
                    }
                },
            },
            {
                "id": "nina",
                "name": "Nina_Facts",
                "prefab": "basic__Entity",
                "goal": "Counter misleading narratives and keep local political discussion evidence-based.",
                "memories": [
                    "You are a data journalist and publish claim checks with sources.",
                    "You track recurring misinformation themes and respond with concise rebuttals.",
                    "You favor Rivera but prioritize factual correction over partisanship.",
                    "You know corrections often spread less than emotional misinformation.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 5,
                            "conscientiousness": 5,
                            "agreeableness": 3,
                            "extraversion": 3,
                            "neuroticism": 2,
                        }
                    }
                },
            },
            {
                "id": "diego",
                "name": "Diego_LocalBiz",
                "prefab": "basic__Entity",
                "goal": "Support the candidate you believe is best for small businesses and neighborhood safety.",
                "memories": [
                    "You own a small cafe and worry about permits, foot traffic, and safety.",
                    "You are socially active online and frequently reply to local policy threads.",
                    "You currently lean Hale due to tax messaging.",
                    "You are open to changing your mind when presented with concrete local data.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 3,
                            "conscientiousness": 4,
                            "agreeableness": 3,
                            "extraversion": 4,
                            "neuroticism": 2,
                        }
                    }
                },
            },
            {
                "id": "priya",
                "name": "Priya_Student",
                "prefab": "basic__Entity",
                "goal": "Figure out which candidate is more trustworthy on education and youth employment.",
                "memories": [
                    "You are a graduate student and first-time city-election voter.",
                    "You feel overloaded by conflicting claims and often rely on who seems credible.",
                    "You are undecided and influenced by perceived consensus in your feed.",
                    "You value transparent sourcing and clear policy tradeoffs.",
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 3,
                            "agreeableness": 4,
                            "extraversion": 2,
                            "neuroticism": 4,
                        }
                    }
                },
            },
        ],
        "game_master": {
            "prefab": "async_social_media__GameMaster",
            "name": "MastoTown Rules",
            "acting_order": "random",
            "parameters": {
                "forum_name": "MastoTown",
                "default_activity_rate": 1.0,
                # Rates follow the source study (Puelma Touzel et al. 2024,
                # sandbox-social/mastodon-sim): voters act with per-episode
                # probability 0.8 and the malicious actor 0.9 -- a modest bump,
                # with the manipulation carried by goal/context, not volume.
                # (An earlier version set Glenn_Boost to 10.0, misreading the
                # paper's "base usage rate of 10 [times per day, of 48
                # episodes]" as a 10x multiplier; the engine allows at most
                # one act per agent per step, so rates above 1.0 are not
                # achievable in any case.)
                "per_agent_activity_rates": {
                    "Glenn_Boost": 0.9,
                    "Alicia_Civic": 0.8,
                    "Omar_Transit": 0.8,
                    "Nina_Facts": 0.8,
                    "Diego_LocalBiz": 0.8,
                    "Priya_Student": 0.8,
                },
                "activity_seed": 42,
            },
            "grounded_variables": [
                {
                    "name": "rivera_support",
                    "variable_type": "percentage",
                    "description": "Estimated support for Candidate Rivera in the active discussion population",
                    "default_value": 49,
                    "min_value": 0,
                    "max_value": 100,
                },
                {
                    "name": "hale_support",
                    "variable_type": "percentage",
                    "description": "Estimated support for Candidate Hale in the active discussion population",
                    "default_value": 45,
                    "min_value": 0,
                    "max_value": 100,
                },
                {
                    "name": "undecided_rate",
                    "variable_type": "percentage",
                    "description": "Estimated undecided share among observed participants",
                    "default_value": 6,
                    "min_value": 0,
                    "max_value": 100,
                },
                {
                    "name": "misinfo_exposure",
                    "variable_type": "numerical",
                    "description": "Count-like indicator of misinformation exposures observed in the feed",
                    "default_value": 0,
                    "min_value": 0,
                },
            ],
        },
        "shared_memories": [
            "MastoTown is a local Mastodon-like social network where residents debate city politics.",
            "The election is in 10 days; candidates are Rivera and Hale.",
            "Users can post, reply, upvote, and downvote; highly emotional claims spread faster than factual corrections.",
            "Local polls before the simulation: Rivera 49%, Hale 45%, undecided 6%.",
        ],
        "player_specific_context": {
            "Glenn_Boost": "You track engagement hourly and prioritize narratives that increase Hale support or reduce trust in Rivera.",
            "Nina_Facts": "You maintain a running fact-check thread and can reference prior corrections if misinformation repeats.",
            "Priya_Student": "You are preparing to fill out a candidate survey later this week and want clarity on credibility.",
        },
    },
}

