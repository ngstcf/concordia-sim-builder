TEMPLATE = {
        "name": "Strategic Planning Scenario",
        "description": "Agents with planning capabilities (basic_with_plan prefab) coordinate a product launch under time pressure. Demonstrates multi-step strategic forethought, inter-departmental negotiation, and planning under uncertainty. Research applications: organizational decision-making, cross-functional coordination, planning bias.",
        "prefab_type": "basic_with_plan__Entity",
        "config": {
            "premise": """NovaTech, a 40-person B2B SaaS startup, has 90 days until the public launch
of their flagship analytics platform. The company raised a $12M Series B
three months ago, and investors expect a strong launch with at least 50 beta
sign-ups in the first week. Three department heads must align on a launch plan
that balances marketing ambition, engineering reality, and the CEO's vision.

Complicating factors: a major competitor (DataPulse) is rumored to be launching
a similar product within 60 days, the engineering team is carrying significant
technical debt from the MVP phase, and the marketing budget ($200K) must cover
both pre-launch awareness and post-launch conversion campaigns.""",
            "max_steps": 15,
            "agents": [
                {
                    "id": "ceo",
                    "name": "Sarah Chen",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Produce a written 90-day launch plan with specific milestones at day 30, 60, and 90 that all three department heads have explicitly agreed to — secure at least 2 concrete commitments from each person",
                    "memories": [
                        "You are Sarah Chen, CEO and co-founder of NovaTech, with a background in product management at two successful startups.",
                        "You excel at synthesizing competing perspectives into a coherent plan and you prefer decisions backed by data.",
                        "You believe in thorough planning before execution — your motto is 'plan the work, then work the plan.'",
                        "You are under pressure from the board to show strong launch metrics; anything less than 50 beta sign-ups will trigger difficult questions.",
                        "You need genuine buy-in from both Marcus and Emily — you have learned the hard way that imposed plans fail.",
                        "You tend to be overly optimistic about timelines and must consciously check this tendency.",
                        "When conflict arises between departments, you prefer structured trade-off discussions over unilateral decisions.",
                        "You privately worry that the DataPulse competitor launch could overshadow yours if you are even two weeks late."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 5,
                                "agreeableness": 3,
                                "extraversion": 4,
                                "neuroticism": 2
                            }
                        }
                    }
                },
                {
                    "id": "marketing",
                    "name": "Marcus Rodriguez",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Secure a marketing budget allocation of at least $120K for pre-launch campaigns and get Emily to commit to 3 demo-ready features by day 60 that marketing can showcase",
                    "memories": [
                        "You are Marcus Rodriguez, VP of Marketing with 12 years of experience in B2B SaaS go-to-market strategy.",
                        "You need to know exactly which features will be demo-ready and by when — vague promises from engineering have burned you before.",
                        "You are concerned that the 90-day timeline is aggressive and that a rushed launch could damage the brand permanently.",
                        "You want to build anticipation gradually through a 3-phase campaign: awareness (day 1-30), engagement (day 30-60), conversion (day 60-90).",
                        "Your marketing budget is $200K total and you are fighting to keep at least $120K for pre-launch rather than having it reallocated to engineering.",
                        "You communicate with energy and persuasive storytelling but sometimes overcommit on deliverables you cannot control.",
                        "You respect Emily's technical judgment but find her conservative timelines frustrating.",
                        "You have data from similar launches showing that companies that launch 2+ weeks after a competitor see 40% fewer sign-ups."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 4,
                                "conscientiousness": 3,
                                "agreeableness": 3,
                                "extraversion": 5,
                                "neuroticism": 3
                            }
                        }
                    }
                },
                {
                    "id": "engineering",
                    "name": "Emily Watson",
                    "prefab": "basic_with_plan__Entity",
                    "goal": "Commit only to milestones your team can realistically deliver without exceeding 45-hour work weeks — push back on any plan that requires more than 5 demo-ready features by day 60",
                    "memories": [
                        "You are Emily Watson, CTO and co-founder, with 15 years of engineering leadership experience.",
                        "You refuse to promise features that cannot be delivered well — you have seen two startups die from shipping buggy products.",
                        "You need clear, frozen requirements from marketing at least 30 days before a feature is due — scope creep is your biggest fear.",
                        "You are protective of your team's work-life balance after the brutal MVP sprint that caused two engineers to burn out.",
                        "The codebase has significant technical debt from the MVP phase that will slow new feature development by roughly 30%.",
                        "You communicate in precise, sometimes blunt terms and back every claim with engineering estimates.",
                        "You privately think the 90-day timeline is doable for core features but not for the full feature set Marcus wants to market.",
                        "You respect Sarah's leadership but will not let her optimism bias override engineering reality."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 2,
                                "neuroticism": 3
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Strategy Facilitator",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "NovaTech raised a $12M Series B three months ago. Investors expect a strong public launch.",
                "Launch deadline is exactly 90 days from today. The board reviews progress monthly.",
                "Total marketing budget is $200K; engineering has a separate $150K quarterly budget for infrastructure and contractors.",
                "Competitor DataPulse is rumored to launch a similar product within 60 days.",
                "The engineering team is carrying significant technical debt from the MVP sprint.",
                "The target is at least 50 beta sign-ups in the first week post-launch.",
                "The team has been working together for 18 months and generally trusts each other, but the last sprint created some tension."
            ],
            "player_specific_context": {
                "Sarah Chen": "The lead investor privately told you that if the launch is delayed past 90 days, they will push for a down-round in the next funding cycle. You have not shared this with Marcus or Emily.",
                "Marcus Rodriguez": "You have a verbal agreement with a tech journalist at TechCrunch for an exclusive launch story, but only if the launch happens within 75 days. Missing this window means competing for coverage with DataPulse.",
                "Emily Watson": "Your best backend engineer gave two weeks notice yesterday. You have not told Sarah or Marcus yet. Losing this person will add 2-3 weeks to the payment integration timeline."
            }
        }
    }
