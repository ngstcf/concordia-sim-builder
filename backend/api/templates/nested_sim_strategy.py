TEMPLATE = {
        "name": "Nested Simulation Strategy - Diplomatic Crisis",
        "description": "Demonstrates nested simulation execution where an agent mentally simulates a private conversation before acting in the main scenario. The ambassador runs an internal mini-simulation of a back-channel negotiation to inform their public strategy — modeling anticipatory social cognition in high-stakes diplomacy.",
        "config": {
            "premise": """A territorial dispute in the South China Sea has escalated to the brink of
armed conflict. Three nations — represented by their UN ambassadors — are
meeting for an emergency session at the United Nations Security Council.

Ambassador Nakamura of Japan has requested a private back-channel
conversation with the Chinese delegation before the formal session begins.
This private conversation is modeled as a nested simulation — Nakamura
mentally rehearses the exchange to prepare talking points and gauge likely
Chinese responses before committing to a public position.

The nested simulation runs first, giving Nakamura intelligence about China's
likely stance. Then the main simulation proceeds with all three ambassadors
in the formal UN session.""",
            "max_steps": 15,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "nakamura",
                    "name": "Ambassador Nakamura",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Achieve a 90-day cooling-off period with mutual withdrawal of military assets from the disputed zone. Use insights from your back-channel conversation to anticipate China's red lines and craft proposals that are acceptable to all parties.",
                    "memories": [
                        "Ambassador Nakamura is a veteran diplomat with 25 years in Japan's foreign service.",
                        "She has served as ambassador to China and speaks fluent Mandarin — she understands Chinese diplomatic signaling.",
                        "Japan's position: freedom of navigation must be preserved, but Japan is willing to accept joint patrol arrangements as a face-saving compromise.",
                        "Nakamura's strategy is to find the overlap between what China needs domestically and what the international community can accept.",
                        "She has back-channel relationships with several Chinese diplomats from her time in Beijing.",
                        "She believes that if she can get China to agree to a cooling-off period, the Philippines will follow — the reverse is much harder.",
                        "The Japanese Prime Minister has given her wide latitude but made clear that accepting Chinese sovereignty claims is not an option.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 4,
                                "extraversion": 3,
                                "neuroticism": 1
                            }
                        }
                    },
                    "nested_simulation": {
                        "premise": "Ambassador Nakamura is having a private, off-the-record conversation with Deputy Ambassador Wei of China in the delegates' lounge before the formal UN session. This is a back-channel probe — both sides are testing positions without committing publicly.",
                        "max_steps": 5,
                        "shared_memories": [
                            "This is an informal back-channel conversation, not an official negotiation.",
                            "Both diplomats have a professional relationship from previous postings and communicate with candor.",
                            "Nothing said here is binding — it is a mutual intelligence-gathering exercise.",
                            "The formal UN session begins in 30 minutes."
                        ],
                        "agents": [
                            {
                                "id": "nakamura_bc",
                                "name": "Nakamura",
                                "prefab": "basic__Entity",
                                "goal": "Probe China's actual red lines vs. their public posture. Find out whether a cooling-off period is negotiable and what China would need in return.",
                                "memories": [
                                    "Nakamura wants to understand what China actually needs vs. what they are publicly demanding.",
                                    "She suspects China's military buildup is driven by domestic politics rather than genuine territorial ambition.",
                                    "She is prepared to float the idea of joint patrols as a trial balloon.",
                                ],
                                "randomize_choices": True
                            },
                            {
                                "id": "wei_bc",
                                "name": "Deputy Ambassador Wei",
                                "prefab": "basic__Entity",
                                "goal": "Assess Japan's flexibility without revealing your own. Signal that China is open to pragmatic solutions if sovereignty language is handled carefully.",
                                "memories": [
                                    "Wei has instructions to maintain China's public position but also to identify face-saving off-ramps.",
                                    "Wei knows that Beijing does not want armed conflict — the economic costs would be catastrophic.",
                                    "Wei can hint at flexibility on timelines but cannot concede on sovereignty language.",
                                    "Wei respects Nakamura and trusts that back-channel signals will not be weaponized publicly.",
                                ],
                                "randomize_choices": True
                            }
                        ],
                        "extraction_prompt": "What did Nakamura learn about China's actual position? What are their real red lines vs. public posturing? Is a cooling-off period feasible? What conditions or face-saving gestures would China likely require? What tone should Nakamura take in the formal session?"
                    }
                },
                {
                    "id": "chen",
                    "name": "Ambassador Chen",
                    "prefab": "basic__Entity",
                    "goal": "Defend China's territorial claims while avoiding an outcome that leads to military confrontation. You need a resolution that Beijing can present as a win domestically — the specific terms matter less than the narrative framing.",
                    "memories": [
                        "Ambassador Chen is a senior Chinese diplomat who reports directly to the Foreign Minister.",
                        "Chen's public mandate is to assert China's historical claims in the South China Sea — but privately, he knows Beijing wants de-escalation.",
                        "The Chinese military buildup was a domestic political signal during election season — it has served its purpose and sustained confrontation is economically harmful.",
                        "Chen needs any agreement to include language that does not explicitly deny China's sovereignty claims — the substance can be flexible if the framing is right.",
                        "He has been briefed by Deputy Ambassador Wei about the back-channel conversation with Nakamura but will not acknowledge this in the formal session.",
                        "Chen's preferred outcome: a 'mutual security arrangement' that functionally freezes the dispute while allowing all parties to claim they protected their interests.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 3,
                                "neuroticism": 1
                            }
                        }
                    }
                },
                {
                    "id": "reyes",
                    "name": "Ambassador Reyes",
                    "prefab": "basic__Entity",
                    "goal": "Protect the Philippines' fishing rights and exclusive economic zone. You cannot match China militarily, so you need international frameworks and alliances to enforce the rules. Push for UNCLOS arbitration references in any resolution.",
                    "memories": [
                        "Ambassador Reyes represents the Philippines, the smallest and most vulnerable party in this dispute.",
                        "The Philippines won a landmark UNCLOS arbitration ruling in 2016 that China has ignored — Reyes wants any new agreement to reference this ruling.",
                        "Filipino fishermen have been harassed by Chinese coast guard vessels in disputed waters — this is not abstract geopolitics for Manila.",
                        "Reyes is pragmatic and knows the Philippines cannot dictate terms, but she can shape the narrative by being the voice of international law.",
                        "She is wary of bilateral deals between Japan and China that might trade Philippine interests for great-power accommodation.",
                        "Her strategy: align with Japan on freedom of navigation while insisting on multilateral enforcement mechanisms.",
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
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
                "name": "UN Security Council session",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "escalation_risk",
                        "variable_type": "percentage",
                        "description": "Risk of military escalation (0=peaceful resolution likely, 100=conflict imminent)",
                        "default_value": 65,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with constructive proposals, increases with ultimatums or breakdowns"
                    },
                    {
                        "name": "negotiation_phase",
                        "variable_type": "categorical",
                        "description": "Current phase of the diplomatic process",
                        "default_value": "opening_statements",
                        "allowed_values": ["opening_statements", "position_exchange", "probing", "proposal_phase", "bargaining", "drafting", "vote", "breakdown"],
                        "update_rule": "Advances as the session progresses through diplomatic procedure"
                    },
                    {
                        "name": "consensus_points",
                        "variable_type": "numerical",
                        "description": "Number of points where all three parties agree (of 4: ceasefire, patrol arrangements, arbitration reference, timeline)",
                        "default_value": 0,
                        "min_value": 0,
                        "max_value": 4,
                        "update_rule": "Increases when a specific proposal receives explicit agreement from all three ambassadors"
                    }
                ]
            },
            "shared_memories": [
                "An emergency UN Security Council session has been called to address the South China Sea territorial dispute.",
                "China has deployed 12 coast guard vessels and 3 navy frigates to the disputed Scarborough Shoal area.",
                "Japan has sent 2 maritime self-defense destroyers to conduct 'freedom of navigation' patrols nearby.",
                "Philippine fishing boats have been blocked from traditional fishing grounds for 3 weeks.",
                "The UN Secretary-General has publicly urged all parties to de-escalate and resolve the dispute through dialogue.",
                "UNCLOS (UN Convention on the Law of the Sea) provides the legal framework but China disputes the tribunal's jurisdiction.",
                "Commercial shipping through the South China Sea is worth $5 trillion annually — prolonged instability threatens global trade.",
                "The session is scheduled for 2 hours — the Secretary-General expects a joint statement or resolution by the end.",
            ],
            "player_specific_context": {
                "Ambassador Nakamura": "Your back-channel with Deputy Ambassador Wei suggested China may accept a 90-day mutual standdown if the resolution avoids the word 'withdrawal' and instead uses 'repositioning for confidence-building.' Use this intelligence carefully — revealing the back-channel would embarrass Wei and close that door permanently.",
                "Ambassador Chen": "Beijing has instructed you that if a cooling-off agreement can be reached, China will quietly reduce its coast guard presence by 50% within 2 weeks — but this must not be in the written resolution. It must appear as a unilateral goodwill gesture, not a concession.",
                "Ambassador Reyes": "The US has privately assured the Philippines that it will deploy a carrier group to the region if the dispute is not resolved within 30 days. You can hint at this without naming the US directly — but using this card too early could backfire by provoking China."
            }
        }
    }
