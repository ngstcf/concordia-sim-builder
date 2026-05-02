TEMPLATE = {
        "name": "Sealed-Bid Art Auction",
        "description": "Agents bid simultaneously in a sealed-bid auction (simultaneous engine). Research applications: first-price sealed-bid auction theory, winner's curse dynamics, private value estimation under incomplete information, budget-constrained bidding strategies. Relevant frameworks: Vickrey auction theory, Riley & Samuelson revenue equivalence, Kagel & Levin's winner's curse experiments.",
        "config": {
            "premise": """A prestigious Christie's evening sale features 6 lots of Impressionist
masterworks, with an estimated combined value of $15-20 million. Four collectors
with asymmetric budgets, divergent motivations, and private valuations submit
sealed bids simultaneously for each lot. The highest bidder wins and pays their
bid price (first-price sealed-bid format).

The collectors have encountered each other at previous auctions and hold beliefs
about each other's strategies and budgets — some accurate, some outdated. The
stakes extend beyond this evening: reputation in the art world, institutional
mandates, investment returns, and family legacy all shape bidding behavior.

Research framing: This scenario tests whether agents exhibit theoretically
predicted behaviors (bid shading, winner's curse avoidance, budget allocation
across sequential lots) and how heterogeneous motivations (institutional,
speculative, sentimental, status-driven) interact in a simultaneous-move
mechanism.""",
            "max_steps": 6,
            "engine_type": "simultaneous",
            "agents": [
                {
                    "id": "collector1",
                    "name": "Victoria",
                    "prefab": "basic__Entity",
                    "goal": "Acquire 2-3 paintings for the National Gallery within the $5M budget, prioritizing the Monet and Renoir, while keeping at least $500K in reserve for an upcoming Sotheby's sale",
                    "memories": [
                        "Victoria is a senior curator at the National Gallery with 18 years of experience and a reputation for disciplined institutional bidding.",
                        "She has a $5 million acquisition budget for this auction season — every dollar spent here reduces what she can bid at the Sotheby's Impressionist sale in 3 weeks.",
                        "She particularly values Monet and Renoir — her board has pre-approved up to $2M for exceptional pieces in these categories.",
                        "She knows the other bidders from previous auctions and has mental models of their strategies, though Marcus recently became harder to predict.",
                        "Victoria prefers to win 2-3 good pieces rather than overpay for one, because her annual performance review weights acquisition count alongside collection quality.",
                        "She suspects Marcus will bid aggressively on Impressionists but believes Yuki will drop out on emotionally priced lots.",
                        "She communicates in precise, measured terms and never reveals her maximum bid — even to her own board — until after the auction.",
                        "She privately worries that if she returns empty-handed, the board will question her judgment and reduce next year's budget."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 2,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "collector2",
                    "name": "Marcus",
                    "prefab": "basic__Entity",
                    "goal": "Win at least 2 Impressionist paintings for the new gallery wing, spending no more than $3M on any single lot, and outbid Victoria on at least 1 piece she visibly wants",
                    "memories": [
                        "Marcus is a tech billionaire who built a $200M personal art collection in 5 years and treats auctions as both passion and competition.",
                        "He has an $8 million budget for this sale and is not afraid to spend it — his ego is tied to winning, not to saving money.",
                        "He wants Impressionist paintings specifically for his new private gallery wing opening in September, and the press will cover which pieces he acquired.",
                        "Marcus tends to bid high early to signal dominance and discourage competitors — a strategy that has worked against budget-constrained institutional bidders.",
                        "He knows Victoria represents a museum with a smaller budget and derives satisfaction from outbidding institutions he views as slow and bureaucratic.",
                        "He is willing to overpay by 15-20% for a piece he really wants, viewing the premium as the cost of certainty.",
                        "He privately considers Yuki a more dangerous competitor than Victoria because her data-driven approach is harder to predict.",
                        "His financial advisor has warned him that his art spending is drawing SEC attention to his stock sales, but he dismisses this as overcaution."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "cognitive_bias": {
                            "bias_type": "overconfidence",
                            "bias_strength": "moderate"
                        }
                    }
                },
                {
                    "id": "collector3",
                    "name": "Yuki",
                    "prefab": "basic__Entity",
                    "goal": "Acquire 1-2 pieces with at least 30% projected 5-year appreciation, spending no more than 85% of estimated fair market value on any lot, and avoid the winner's curse entirely",
                    "memories": [
                        "Yuki is an art investment fund manager from Tokyo who manages $120M in art assets for 40 institutional investors.",
                        "She has a $4 million budget for this sale and treats art purely as an investment vehicle — emotional attachment is a liability in her framework.",
                        "She will only bid if her proprietary model estimates the painting will appreciate 30%+ over 5 years, factoring in provenance, condition, and market trends.",
                        "She has detailed analytics on 15 years of Impressionist auction data and knows the historical price ceiling for each artist in tonight's catalog.",
                        "Yuki prefers to let emotional bidders like Marcus overpay and then pick up the lots they ignore — her returns come from discipline, not spectacle.",
                        "She has identified the Degas ballet study and the lesser-known Cézanne landscape as the best risk-adjusted investments in tonight's catalog.",
                        "She communicates in numbers and probabilities; she finds the art world's emphasis on subjective 'feeling' frustrating but has learned to work within it.",
                        "Her fund's quarterly report is due in 6 weeks — returning with no acquisitions would be harder to explain to investors than overpaying slightly."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 1,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "collector4",
                    "name": "Henri",
                    "prefab": "basic__Entity",
                    "goal": "Win the Monet water lily study (Lot 3) at any price up to your full $3M budget, then withdraw from remaining lots — this is the only piece that matters",
                    "memories": [
                        "Henri is from a European aristocratic family with a centuries-old art collection, and he views this auction as a matter of family honor.",
                        "He has a $3 million budget — modest by tonight's standards — because the family estate generates limited liquid income.",
                        "He only wants one painting: the Monet water lily study (Lot 3) that his grandmother owned before it was sold during the family's financial difficulties in the 1970s.",
                        "Henri will bid his entire budget on that one piece if necessary; losing it to Marcus or a speculator would be personally devastating.",
                        "He is sentimental about art and connects each piece to its human story; he finds Yuki's investment approach to art distasteful.",
                        "He will drop out of bidding on pieces he does not emotionally connect with — the other 5 lots hold no interest for him.",
                        "He carries himself with quiet dignity and rarely raises his voice, but his hands tremble when bidding on the Monet — a tell that experienced bidders have noticed.",
                        "His wife has told him that $2.5M is their absolute maximum without selling other family assets, but he has privately decided he will go to $3M if needed."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "emotion": {
                            "current_emotion": "anxious_determination",
                            "emotion_intensity": "strong"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Auctioneer",
                "acting_order": "fixed",
                "parameters": {}
            },
            "shared_memories": [
                "This is a first-price sealed-bid auction at Christie's evening Impressionist sale.",
                "All bids are submitted simultaneously and sealed — no one sees others' bids until results are announced.",
                "The highest bidder wins each lot and pays their bid price; ties are broken by the house in favor of the earlier-registered bidder.",
                "Tonight's 6 lots include works by Monet (Lots 1 and 3), Renoir (Lot 2), Degas (Lot 4), Cézanne (Lot 5), and Pissarro (Lot 6).",
                "Each collector has a private budget and personal valuations that are not public knowledge.",
                "The art market has been volatile this year — Impressionist prices are up 12% overall but with significant variance by artist and provenance.",
                "A Bloomberg reporter is in the room covering the sale; bidding results will be published tomorrow and affect market sentiment.",
                "Christie's charges a 15% buyer's premium on top of the hammer price, which comes out of the bidder's budget."
            ],
            "player_specific_context": {
                "Victoria": "Your conservation team's confidential report indicates the Renoir (Lot 2) has a hidden restoration that reduces its long-term value by approximately 20%. None of the other bidders know this. You also learned from a gallery contact that Marcus's financial advisor is pressuring him to slow his art spending.",
                "Marcus": "Your art advisor sent you a private appraisal valuing the Monet water lily study (Lot 3) at $3.5M — significantly above the catalog estimate of $2.2-2.8M. You also know from a mutual acquaintance that Henri has a deep personal connection to Lot 3, which means he may bid irrationally high.",
                "Yuki": "Your proprietary model flagged the Cézanne landscape (Lot 5) as severely undervalued — the catalog estimate is $800K-1.2M but your model predicts $2.1M fair value based on comparable sales in Asia. You also have intelligence that a major Japanese museum is planning an Impressionist exhibition next year, which would drive up prices for any pieces you acquire.",
                "Henri": "Your family's former art dealer, now retired, told you confidentially that the Monet water lily study has exceptional provenance — it was briefly owned by Claude Monet's son Michel before your grandmother acquired it. This provenance detail is not in the catalog and would significantly increase the painting's value if made public after purchase."
            }
        }
    }
