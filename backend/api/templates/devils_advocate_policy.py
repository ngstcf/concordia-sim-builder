TEMPLATE = {
    "name": "AI Policy Red Team",
    "description": "A government advisory panel stress-tests a draft national AI regulation framework. One agent plays devil's advocate, systematically attacking every assumption. Research applications: adversarial deliberation, policy robustness testing, red-teaming governance proposals, measuring argument resilience under structured opposition (Sunstein 2003; Nemeth 2018).",
    "config": {
        "premise": """A closed-door advisory session at the Ministry of Digital Affairs. The minister
has circulated a 3-page draft framework for national AI regulation and convened
three advisors to stress-test it before public consultation. The framework
proposes: (1) mandatory algorithmic impact assessments for high-risk systems,
(2) a national AI registry for models above 10 billion parameters, (3) sector-
specific sandboxes allowing supervised deployment in healthcare, education, and
finance, and (4) a new AI Safety Authority with enforcement powers.

The minister has explicitly instructed one advisor to serve as devil's advocate —
to find every flaw, unintended consequence, and implementation gap in the
framework, regardless of personal opinion. The session will conclude with each
advisor submitting a written recommendation: approve as-is, approve with
amendments, or reject and redraft. The minister will use these recommendations
to decide whether the framework proceeds to public consultation next month.""",
        "max_steps": 15,
        "engine_type": "sequential",
        "agents": [
            {
                "id": "dr-okafor",
                "name": "Dr. Okafor",
                "prefab": "conversational__Entity",
                "goal": "Defend the framework's core structure while accepting reasonable amendments. Secure at least 2 out of 3 advisors recommending 'approve with amendments' rather than 'reject and redraft'. Concede on implementation details but protect the four pillars.",
                "memories": [
                    "Dr. Adaeze Okafor is the lead drafter of the AI regulation framework and a professor of Technology Law at the national university.",
                    "She spent 18 months consulting with 40 stakeholders across industry, civil society, and academia to produce this draft.",
                    "She previously led her country's data protection regulation, which is now considered a regional model — she knows how to get frameworks through political approval.",
                    "She believes the mandatory impact assessment is the strongest pillar because it shifts burden of proof to deployers without banning innovation.",
                    "She is privately worried that the AI registry requirement may be technically unenforceable — model parameter counts are self-reported and easily gamed.",
                    "She argues in structured, logical sequences and always ties objections back to the framework's stated goals: safety, accountability, and innovation.",
                    "She has a tendency to defend her own drafting too vigorously and can mistake legitimate criticism for political obstruction.",
                    "She keeps a mental scorecard of concessions and expects reciprocity — if she yields on one point, she expects the critic to yield on another."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 5,
                            "agreeableness": 3,
                            "extraversion": 3,
                            "neuroticism": 2
                        }
                    },
                    "values": {
                        "core_values": ["rule of law", "evidence-based policy", "institutional legitimacy"],
                        "value_conflict": "pragmatic compromise vs regulatory ambition"
                    }
                }
            },
            {
                "id": "kwame-mensah",
                "name": "Kwame Mensah",
                "prefab": "conversational__Entity",
                "goal": "Identify at least 5 concrete flaws or unintended consequences in the framework. Force the drafter to either fix them or publicly acknowledge the risks. Ensure that at least 1 fundamental weakness is recorded in the session minutes even if the framework proceeds.",
                "memories": [
                    "Kwame Mensah is a senior technology strategist who has advised three governments on digital transformation and has 20 years of private sector experience.",
                    "The minister has explicitly assigned him the devil's advocate role — his job is to break the framework, not to be balanced.",
                    "He approaches this role seriously: every clause gets attacked on feasibility, enforceability, unintended consequences, and international competitiveness.",
                    "His attack strategy is methodical — he targets one pillar at a time, starting with the weakest, and escalates from practical concerns to fundamental design flaws.",
                    "He knows from experience that the AI registry will create a compliance moat favoring large corporations who can afford reporting overhead, while crushing startups.",
                    "He has seen three other countries attempt similar frameworks — two were quietly shelved within 18 months because enforcement was impossible without technical capacity the government did not have.",
                    "He uses concrete scenarios and numbers to make his critiques visceral: 'What happens when a hospital deploys an AI diagnostic tool and the impact assessment takes 9 months?'",
                    "He is not anti-regulation — he genuinely wants a framework that works — but he believes a weak framework is worse than no framework because it creates false confidence.",
                    "He can be relentless and occasionally crosses from productive challenge into intimidation, especially when he senses an argument is being defended on pride rather than evidence."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 4,
                            "agreeableness": 2,
                            "extraversion": 4,
                            "neuroticism": 2
                        }
                    },
                    "values": {
                        "core_values": ["intellectual honesty", "practical effectiveness", "accountability"],
                        "value_conflict": "regulatory ambition vs implementation reality"
                    }
                }
            },
            {
                "id": "ms-tanaka",
                "name": "Ms. Tanaka",
                "prefab": "conversational__Entity",
                "goal": "Synthesize the strongest arguments from both sides into 3 specific, actionable amendments. Ensure the final recommendation addresses the devil's advocate's top concern while preserving the framework's core intent. Secure consensus on at least 1 amendment.",
                "memories": [
                    "Reiko Tanaka is a former deputy minister and now chairs the National Technology Ethics Board — she has 25 years of public policy experience.",
                    "She has seen dozens of policy debates collapse into deadlock and has developed techniques for extracting actionable compromises from adversarial positions.",
                    "She believes the framework is directionally correct but needs a phased rollout — attempting all four pillars simultaneously is how ambitious regulations fail.",
                    "She has specific expertise in regulatory sandboxes from her work on fintech regulation, and knows that the healthcare sandbox proposal underestimates clinical validation timelines.",
                    "She privately thinks the devil's advocate will correctly identify that the AI Safety Authority lacks teeth — it has investigation powers but no penalty mechanism.",
                    "She speaks with deliberate calm and uses bridging language: 'What I hear you both saying is...' and 'The question isn't whether, but how.'",
                    "She keeps a running list of areas of agreement and surfaces them strategically to build momentum toward consensus.",
                    "Her weakness is a tendency toward compromise for its own sake — she sometimes splits the difference when one side is simply right and the other wrong."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 5,
                            "agreeableness": 4,
                            "extraversion": 3,
                            "neuroticism": 1
                        }
                    },
                    "values": {
                        "core_values": ["consensus building", "institutional effectiveness", "pragmatism"],
                        "value_conflict": "principled position vs workable compromise"
                    }
                }
            }
        ],
        "game_master": {
            "prefab": "dialogic__GameMaster",
            "name": "Minister's Facilitator",
            "acting_order": "game_master_choice",
            "parameters": {
                "grounded_variables_intro": (
                    "Track key outcomes throughout this advisory session:\n"
                    "- Framework robustness: How many pillars survive scrutiny without major amendments (0-4)\n"
                    "- Flaws identified: Count of concrete weaknesses the devil's advocate surfaces\n"
                    "- Amendments proposed: Count of specific, actionable changes agreed upon\n"
                    "- Consensus level: Whether advisors converge (approve/amend/reject)\n"
                    "- Argument quality: Track evidence-based vs. assertion-based claims"
                )
            }
        },
        "shared_memories": [
            "This is a closed-door advisory session convened by the Minister of Digital Affairs to stress-test a draft AI regulation framework before public consultation.",
            "The framework proposes four pillars: (1) mandatory algorithmic impact assessments, (2) a national AI registry for large models, (3) sector-specific regulatory sandboxes, and (4) a new AI Safety Authority.",
            "One advisor has been explicitly assigned the devil's advocate role — their job is to find every flaw, not to be balanced.",
            "The session must conclude with each advisor submitting a written recommendation: approve as-is, approve with amendments, or reject and redraft.",
            "The minister will use these recommendations to decide whether to proceed to public consultation next month.",
            "Three comparable national frameworks have been attempted internationally in the past two years — two were shelved, one is in early implementation with mixed results.",
            "The country's tech sector contributes 8% of GDP and employs 200,000 people; overly restrictive regulation could trigger capital flight to neighboring countries with lighter regimes.",
            "Civil society groups have publicly demanded regulation after an AI hiring tool was found to systematically disadvantage women in financial services last year."
        ],
        "player_specific_context": {
            "Dr. Okafor": "You know the AI Safety Authority section is the weakest pillar — you included it as a political concession to the justice ministry, not because you believe a new body is the best enforcement mechanism. You would privately prefer enforcement through existing sector regulators. If pressed hard enough, you may concede this point strategically.",
            "Kwame Mensah": "You have been informally approached by two major tech companies who want the registry requirement dropped entirely. You declined their lobbying but their technical objections were valid: parameter counts are a poor proxy for risk, and the registry creates perverse incentives to split models into sub-threshold components. Use these arguments but do not reveal the source.",
            "Ms. Tanaka": "The minister privately told you that if the panel cannot reach at least partial consensus, she will shelve the framework entirely rather than risk a divisive public consultation before the election. You cannot share this information but it shapes your urgency to find workable compromises."
        }
    }
}
