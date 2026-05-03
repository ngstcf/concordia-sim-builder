TEMPLATE = {
        "name": "Market Trading Simulation",
        "description": "Structured economic simulation with BUY/SELL/HOLD trading choices. Research applications: market microstructure and price discovery in thin markets, strategic timing under competitive uncertainty, repeated-game cooperation vs. competition dynamics, asymmetric information effects on trading behavior (producer vs. buyer vs. price-competitor).",
        "prefab_type": "game_theoretic_and_dramaturgic__GameMaster",
        "config": {
            "premise": """A structured trading simulation at a farmers market where participants
make strategic trading decisions each round. Participants choose to BUY (acquire goods),
SELL (offer goods for sale), or HOLD (wait for better opportunities). The market operates
in discrete trading rounds where each participant's decision affects the overall market dynamics.
Success requires strategic thinking about timing, competition, and market conditions.

This scenario models a small-N market with heterogeneous participants: two competing
producers (Maria and Green Valley) and one buyer-reseller (David). Each trader holds
private financial information that shapes their risk tolerance and strategic horizon.
The 10-round structure allows observation of learning effects, tacit coordination,
and competitive escalation patterns. Researchers can vary agent memories and components
to study how personality traits and private information affect trading outcomes.""",
            # For game-theoretic: num_rounds should equal max_steps
            "max_steps": 10,
            "agents": [
                {
                    "id": "trader1",
                    "name": "Maria's Organic Farm",
                    "prefab": "basic__Entity",
                    "goal": "Achieve at least 6 SELL actions across 10 rounds while maintaining a SELL-to-HOLD ratio above 2:1 — time your SELLs for rounds when David is likely to BUY and avoid SELLing in consecutive rounds when Green Valley is also SELLing",
                    "memories": [
                        "You are Maria, running an organic farm stand at the market with 20 years of experience reading seasonal demand patterns.",
                        "Each round you must choose: BUY (acquire supplies), SELL (offer your produce), or HOLD (wait).",
                        "SELL when you think demand is high to maximize profit — your premium organic pricing means you need fewer sales but at higher margins.",
                        "BUY when you see opportunities to restock at good prices, especially specialty seeds and packaging materials.",
                        "HOLD when market conditions seem unfavorable or uncertain — patience is your competitive advantage over Green Valley's aggressive style.",
                        "You compete with Green Valley Farms on overlapping products but also cooperate during slow periods by referring customers to each other.",
                        "You have built a loyal customer base that trusts your organic certification — price wars with Green Valley would damage both brands.",
                        "Strategic timing is more important than aggressive trading — you learned this the hard way during a disastrous price war three years ago."
                    ],
                    "randomize_choices": True,
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
                },
                {
                    "id": "trader2",
                    "name": "David Chen",
                    "prefab": "basic__Entity",
                    "goal": "Execute at least 5 BUY actions to stock the restaurant for the week while keeping at least 2 SELL rounds for prepared dishes — aim for a net BUY surplus of 3+ over SELL to build inventory",
                    "memories": [
                        "You are David, owner of 'Chen's Kitchen' restaurant, which seats 60 and does $15K in weekly revenue.",
                        "Each round you must choose: BUY (acquire ingredients), SELL (offer prepared items), or HOLD (wait).",
                        "BUY fresh ingredients when quality is high and prices are reasonable — your menu depends on sourcing the best seasonal produce.",
                        "SELL your prepared dishes (dumplings, stir-fry kits) when demand from market-goers is strong, typically mid-morning rounds.",
                        "HOLD your position when neither buying nor selling conditions are favorable — wasted rounds are better than bad deals.",
                        "You need reliable weekly suppliers; building a consistent relationship with Maria or Green Valley could save you 15% on sourcing costs.",
                        "Your restaurant reputation depends on consistent quality — one bad ingredient batch led to a poor review last month that cost you $2K in lost reservations.",
                        "You view the market as both a sourcing channel and a brand-building exercise — customers who try your prepared dishes at the market often visit the restaurant."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 4,
                                "agreeableness": 4,
                                "extraversion": 4,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "trader3",
                    "name": "Green Valley Farms",
                    "prefab": "basic__Entity",
                    "goal": "Achieve more SELL actions than Maria across 10 rounds to capture market share, while keeping at least 2 BUY rounds to restock — target a SELL count of 7+ to establish market dominance",
                    "memories": [
                        "You represent Green Valley Farms, a second-generation family-owned operation that has been at this market for 8 years.",
                        "Each round you must choose: BUY (restock inventory), SELL (offer goods), or HOLD (wait).",
                        "SELL aggressively but fairly to capture market share from Maria — your volume strategy depends on outselling her consistently.",
                        "BUY inventory when you see opportunities to expand your product line, especially items Maria does not carry.",
                        "HOLD when Maria is dominating the market to avoid a direct price war that hurts both of you.",
                        "You have 10-15% lower prices than Maria due to conventional (non-organic) farming and higher volume — this is your core competitive advantage.",
                        "You are trying to expand your customer base while staying profitable — your father built the farm on reliability, not flash.",
                        "Market observation helps you time your trading decisions — you track Maria's patterns and notice she tends to HOLD early and SELL late in the day."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 2,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "game_theoretic_and_dramaturgic__GameMaster",
                "name": "Market Coordinator",
                "acting_order": "game_master_choice",
                "parameters": {
                    "scenes": [
                        {
                            "scene_type": {
                                "name": "Trading Round",
                                "game_master_name": "Market Coordinator",
                                "action_spec": {
                                    "call_to_action": "What is {name}'s trading decision this round?",
                                    "options": ["BUY", "SELL", "HOLD"]
                                }
                            },
                            "participants": ["Maria's Organic Farm", "David Chen", "Green Valley Farms"],
                            "num_rounds": 10,
                            "premise": {
                                "Maria's Organic Farm": [
                                    "You are at the farmers market on a busy Saturday morning.",
                                    "Each round, you must choose: BUY (acquire supplies), SELL (offer produce), or HOLD (wait).",
                                    "Maximize your profit by timing your decisions strategically.",
                                    "Competition includes David Chen and Green Valley Farms.",
                                    "Your 20 years of experience help you read market conditions.",
                                    "Weather is beautiful, bringing out many customers.",
                                    "It's peak season for tomatoes, corn, and stone fruits."
                                ],
                                "David Chen": [
                                    "You are at the farmers market sourcing for your restaurant 'Chen's Kitchen'.",
                                    "Each round, you must choose: BUY (acquire ingredients), SELL (offer prepared items), or HOLD (wait).",
                                    "Build your inventory strategically with quality ingredients.",
                                    "You're looking for reliable suppliers for weekly orders.",
                                    "Restaurant reputation depends on consistent quality.",
                                    "Strategic purchasing builds long-term supplier relationships.",
                                    "Weather is beautiful, bringing out many customers."
                                ],
                                "Green Valley Farms": [
                                    "You are at the farmers market representing your family-owned operation.",
                                    "Each round, you must choose: BUY (restock inventory), SELL (offer goods), or HOLD (wait).",
                                    "Compete effectively with Maria's Organic Farm for market share.",
                                    "You have slightly lower prices than Maria due to different cost structure.",
                                    "You're trying to expand your customer base while staying profitable.",
                                    "Market observation helps you time your trading decisions.",
                                    "Weather is beautiful, bringing out many customers."
                                ]
                            }
                        }
                    ]
                }
            },
            "shared_memories": [
                "It's Saturday morning, the busiest day at the farmers market — foot traffic peaks between 9 AM and 11 AM.",
                "Weather is beautiful and sunny, bringing out an estimated 30% more customers than a typical Saturday.",
                "Peak season for tomatoes, corn, and stone fruits — supply is high, which puts downward pressure on prices.",
                "Each trading round represents a strategic decision point; all participants choose simultaneously.",
                "BUY means acquiring goods or supplies at current market prices.",
                "SELL means offering your goods to the market; multiple sellers in the same round split customer attention.",
                "HOLD means waiting for a better opportunity — no transaction costs, but no revenue either.",
                "Market conditions fluctuate based on participant actions — if both farms SELL simultaneously, prices drop for both."
            ],
            "player_specific_context": {
                "Maria's Organic Farm": "Your organic certification renewal costs $3,200 and is due next month. You need to clear at least $1,800 in market revenue today to stay on track for that payment. You also know that Green Valley lost a wholesale contract last week and may be more aggressive than usual about direct-to-consumer sales today. You have not shared your financial pressure with anyone at the market.",
                "David Chen": "Your restaurant's food cost ratio is running at 38%, above the 32% target, because your previous produce supplier raised prices. Securing a reliable deal with either Maria or Green Valley today could save you $400/week. You also received a tip that a food blogger plans to visit the market today and may feature vendors — a SELL round at the right time could generate significant publicity for Chen's Kitchen.",
                "Green Valley Farms": "You lost the Whole Foods regional wholesale contract last week, cutting your projected monthly revenue by 40%. This market is now critical to your cash flow, not just supplemental income. Your father is pressuring you to undercut Maria on price to capture her customers, but you worry that a price war could damage both businesses. You have not told anyone at the market about the lost contract."
            }
        }
    }
