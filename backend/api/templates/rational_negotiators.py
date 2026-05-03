TEMPLATE = {
        "name": "Rational Budget Negotiation",
        "description": "Two rational-prefab agents use expected-utility maximization to negotiate a departmental budget split under a disagreement penalty. Research applications: Nash bargaining, ZOPA (zone of possible agreement) analysis, rational agent modeling, and studying how private information affects negotiation outcomes.",
        "config": {
            "premise": """The annual budget review at Apex Corp, a mid-sized enterprise software company.
The CEO has allocated exactly $2 million to be split between the Engineering and
Marketing departments. Department heads Priya (Engineering VP) and Jordan
(Marketing VP) must negotiate and agree on a split in a single meeting.

Stakes: If they cannot reach agreement by the end of this meeting, the board's
default allocation kicks in — both departments receive a flat $800K each
(a 20% penalty for indecision). Neither side wants this outcome.

Context: Apex Corp posted record revenue last year ($48M), driven by 3 new product
launches (Engineering) and a brand campaign that increased inbound leads by 40%
(Marketing). Both departments can legitimately claim credit. The CEO has told
the board she expects 'a collaborative decision that reflects shared success.'""",
            "max_steps": 8,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "priya",
                    "name": "Priya",
                    "prefab": "rational__Entity",
                    "goal": "Secure at least $1.15M for Engineering — enough for $1M in current projects plus $150K minimum for the R&D pipeline — while keeping the negotiation cordial enough that Jordan will collaborate on the Q3 product launch",
                    "memories": [
                        "Priya is the VP of Engineering at Apex Corp with 12 years of experience in tech leadership.",
                        "Engineering shipped 3 major products last year, directly generating 70% of the company's $48M revenue.",
                        "The team needs $1M minimum to maintain current projects; anything below that forces headcount cuts.",
                        "An additional $200K for R&D would fund a prototype that could become next year's flagship product.",
                        "Priya values data-driven arguments and becomes impatient with appeals to emotion or fairness that lack supporting numbers.",
                        "Last year Engineering received $1.1M and Marketing received $900K — Priya views this as the baseline.",
                        "Priya privately believes Marketing's lead increase was partly due to Engineering's product improvements, not just the campaign.",
                        "She prefers finding mutually beneficial outcomes but will not accept less than $1M under any circumstances.",
                        "Her negotiation style is calm, structured, and anchored in quantitative claims."
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
                        },
                        "values": {
                            "core_values": ["meritocracy", "data_driven_decisions", "long_term_investment"],
                            "value_conflict": "short_term_fairness_vs_strategic_investment"
                        }
                    }
                },
                {
                    "id": "jordan",
                    "name": "Jordan",
                    "prefab": "rational__Entity",
                    "goal": "Secure at least $950K for Marketing — $800K for the brand campaign and $150K for analytics tools — by framing the campaign as a revenue multiplier that benefits Engineering too",
                    "memories": [
                        "Jordan is the VP of Marketing at Apex Corp with a background in consumer psychology and brand strategy.",
                        "Marketing's brand campaign drove a 40% increase in qualified leads last quarter, which the sales team converted at record rates.",
                        "The planned Q3 campaign requires $800K minimum for media buys and creative; $200K more for analytics would prove ROI definitively.",
                        "Jordan knows Engineering had a strong year but believes Marketing created the market conditions that made those sales possible.",
                        "Jordan prefers win-win solutions and is willing to make creative concessions (phased spending, shared analytics budget) to reach agreement.",
                        "A failed negotiation ($800K each) would kill the Q3 campaign entirely — an outcome worse than any reasonable compromise.",
                        "Jordan's negotiation style is persuasive and relationship-focused; he uses storytelling and framing rather than raw numbers.",
                        "He privately worries that Priya's data-heavy approach makes his qualitative arguments seem weaker than they are.",
                        "He has prepared a one-page brief showing that for every $1 Marketing spends, Engineering's products see $3.20 in additional sales."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 3,
                                "agreeableness": 4,
                                "extraversion": 5,
                                "neuroticism": 2
                            }
                        },
                        "values": {
                            "core_values": ["collaboration", "brand_equity", "creative_excellence"],
                            "value_conflict": "departmental_advocacy_vs_company_unity"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Board Mediator",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "The total budget is exactly $2 million, non-negotiable. The CEO will not increase the pool.",
                "If no agreement is reached by end of meeting, both departments default to $800K each — a 20% penalty.",
                "The CEO expects a decision today and has told the board she wants 'a collaborative outcome.'",
                "Both departments contributed to last year's record $48M revenue — attribution is genuinely ambiguous.",
                "The board values cross-departmental collaboration and will view a failed negotiation as a leadership failure for both VPs.",
                "Last year's allocation was Engineering $1.1M / Marketing $900K — this is common knowledge.",
                "A major Q3 product launch requires both Engineering capacity and Marketing support to succeed."
            ],
            "player_specific_context": {
                "Priya": "Your CTO mentor at a previous company told you: 'Never accept less than 55% when your team drove 70% of revenue — it sets a precedent.' You also know that Jordan's analytics tools request is partially redundant with Engineering's existing data pipeline, which could save $50-100K if shared.",
                "Jordan": "You have a verbal commitment from the CFO that if Marketing can demonstrate 3:1 ROI on the Q3 campaign, the department will receive a supplemental $200K allocation in Q4. You have not shared this with Priya — it reduces your urgency but you do not want her to know you have a fallback."
            }
        }
    }
