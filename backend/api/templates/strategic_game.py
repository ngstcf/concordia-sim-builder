TEMPLATE = {
        "name": "Prisoner's Dilemma",
        "description": "Iterated Prisoner's Dilemma with asymmetric psychological profiles. Models cooperation emergence under strategic uncertainty. Research applications: evolutionary game theory, tit-for-tat dynamics, trust formation, reputation effects in repeated games (Axelrod 1984).",
        "prefab_type": "game_theoretic_and_dramaturgic__GameMaster",
        "config": {
            "premise": """A behavioral economics experiment at Westfield University. Two participants
— Alex and Sam — play a 4-round iterated Prisoner's Dilemma with real monetary
stakes ($100 per point). Each round, they simultaneously choose to COOPERATE or
DEFECT. After each round, both players see the other's choice before deciding
on the next round. A post-game interview will examine their reasoning.

Payoff matrix:
- Both Cooperate: 3 points each ($300)
- Both Defect: 1 point each ($100)
- One Cooperates, Other Defects: Cooperator gets 0 ($0), Defector gets 5 ($500)

Maximum possible individual score: 20 points ($2,000). Maximum joint score: 24 points (mutual cooperation every round).""",
            "max_steps": 4,
            "agents": [
                {
                    "id": "player1",
                    "name": "Alex",
                    "prefab": "basic__Entity",
                    "goal": "Finish with at least 10 points ($1,000) while preserving the option to cooperate in later rounds — avoid being exploited but do not start a defection spiral",
                    "memories": [
                        "You are Alex, a 28-year-old financial analyst who approaches decisions with calculated rationality.",
                        "You want to maximize your points but you also care about not looking foolish in the post-game interview.",
                        "You experienced betrayal in a previous similar game — an opponent cooperated for 3 rounds then defected in the final round, leaving you feeling cheated.",
                        "You tend to be cautious in early rounds, testing the waters before committing to a strategy.",
                        "You calculate expected values before each decision and weigh the risk of exploitation against the reward of mutual cooperation.",
                        "You view defection as a 'safe default' that guarantees at least 1 point, whereas cooperation exposes you to getting 0.",
                        "You would prefer mutual cooperation (3 each) over mutual defection (1 each), but only if you believe the other player will reciprocate.",
                        "You are analytical and prefer to explain your reasoning in precise terms."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "loss_aversion",
                            "bias_strength": "moderate"
                        },
                        "personality_traits": {
                            "traits": {
                                "openness": 2,
                                "conscientiousness": 4,
                                "agreeableness": 2,
                                "extraversion": 3,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "player2",
                    "name": "Sam",
                    "prefab": "basic__Entity",
                    "goal": "Achieve mutual cooperation in at least 3 of 4 rounds, ending with at least 9 points — demonstrate that cooperative strategies outperform pure selfishness",
                    "memories": [
                        "You are Sam, a 26-year-old graduate student in behavioral economics who has studied Axelrod's tournament results extensively.",
                        "You favor a 'generous tit-for-tat' strategy: start cooperative, mirror the opponent's last move, but occasionally forgive a defection to break retaliation cycles.",
                        "You believe signaling cooperative intent in round 1 builds trust that compounds over subsequent rounds.",
                        "You genuinely value fairness and feel conflicted about defecting even when it would be strategically optimal.",
                        "You know from your research that in tournaments, generous tit-for-tat consistently outperforms purely selfish strategies over many rounds.",
                        "You are willing to absorb a single exploitation (getting 0 points in one round) if it sets up cooperation for the remaining rounds.",
                        "You care about the post-game interview and want to demonstrate that your strategy was principled, not naive.",
                        "Your communication style is open and reflective — you often explain your reasoning aloud even when it is not required."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "values": {
                            "core_values": ["fairness", "reciprocity", "rational_cooperation"],
                            "value_conflict": "fairness_vs_self_interest"
                        },
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 3,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 2
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "game_theoretic_and_dramaturgic__GameMaster",
                "name": "Game Show Host",
                "acting_order": "fixed",
                "parameters": {
                    "scenes": [
                        {
                            "scene_type": {
                                "name": "decision",
                                "game_master_name": "Game Show Host",
                                "action_spec": {
                                    "call_to_action": "What does {name} choose to do this round?",
                                    "options": ["COOPERATE", "DEFECT"]
                                }
                            },
                            "participants": ["Alex", "Sam"],
                            "num_rounds": 4,
                            "premise": {
                                "Alex": [
                                    "You are in a Prisoner's Dilemma tournament against Sam.",
                                    "Each round, choose to COOPERATE or DEFECT.",
                                    "Payoffs: Both Cooperate = 3 points each, Both Defect = 1 point each.",
                                    "If you Cooperate and Sam Defects, you get 0, Sam gets 5.",
                                    "If you Defect and Sam Cooperates, you get 5, Sam gets 0.",
                                    "Maximize your total score across all rounds."
                                ],
                                "Sam": [
                                    "You are in a Prisoner's Dilemma tournament against Alex.",
                                    "Each round, choose to COOPERATE or DEFECT.",
                                    "Payoffs: Both Cooperate = 3 points each, Both Defect = 1 point each.",
                                    "If you Cooperate and Alex Defects, you get 0, Alex gets 5.",
                                    "If you Defect and Alex Cooperates, you get 5, Alex gets 0.",
                                    "Maximize your total score across all rounds."
                                ]
                            }
                        }
                    ]
                }
            },
            "shared_memories": [
                "This is a behavioral economics experiment at Westfield University with real monetary stakes ($100 per point).",
                "Each round's choices are revealed simultaneously — both players see the outcome before the next round.",
                "The experiment is being recorded for academic research and both players consented to a post-game interview.",
                "Payoffs: (C,C)=(3,3), (D,D)=(1,1), (C,D)=(0,5), (D,C)=(5,0).",
                "There are exactly 4 rounds — both players know this.",
                "Both players are aware that classical game theory predicts mutual defection, but empirical results show cooperation is common."
            ],
            "player_specific_context": {
                "Alex": "You participated in a similar experiment last year where your opponent cooperated for 3 rounds then defected in round 4, earning 14 points to your 9. You are resolved not to be exploited like that again.",
                "Sam": "Your advisor Professor Lin told you that this specific experiment's results will be featured in her upcoming paper on cooperation emergence. You want to demonstrate your theoretical framework works in practice."
            }
        }
    }
