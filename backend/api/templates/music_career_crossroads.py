TEMPLATE = {
    "name": "Music Career Crossroads",
    "description": "A 26-year-old musician convenes trusted advisors to deliberate whether to keep pursuing music full-time, pivot to a stable career, or build a hybrid path — all with the goal of achieving financial independence by 30. Research applications: career decision-making under uncertainty, sunk cost reasoning, identity-vocation conflict, financial planning for creative professionals (Bridgstock 2005; Menger 1999).",
    "config": {
        "premise": """Jordan Kim, a 26-year-old singer-songwriter and guitarist, has called an informal
gathering at a friend's apartment. After four years of pursuing music full-time
since graduating with a degree in Music Performance, Jordan is at a crossroads.

The numbers: Jordan earns roughly $600/month from music (streaming royalties,
weekend gigs at bars and cafés, and occasional session work) plus $1,200/month
from a part-time barista job. Monthly expenses are $2,300 in a mid-size city.
Student loan balance: $28,000. Savings: $3,100. No health insurance. Jordan's
Spotify has 4,200 monthly listeners and a local following that fills 80-seat
venues. A small indie label expressed interest last year but never followed up.

Jordan has gathered five people whose opinions matter — a parent, two friends
who took different paths, a financial planner, and a music industry mentor — to
help think through three options: (1) commit fully to music for two more years
with a concrete growth plan, (2) pivot to a stable career and keep music as a
serious side pursuit, or (3) build a hybrid path that funds music through a
related day job. The goal is financial independence — defined as covering all
expenses, eliminating debt, and building savings — by age 30.

The evening will end with each person giving Jordan their honest recommendation
and the single most important thing Jordan should do in the next 90 days.""",
        "max_steps": 20,
        "engine_type": "sequential",
        "agents": [
            {
                "id": "jordan-kim",
                "name": "Jordan Kim",
                "prefab": "conversational__Entity",
                "goal": "Arrive at a concrete 90-day action plan by the end of the evening. Ask hard questions, push back on advice that feels uninformed, and force each advisor to be specific — not just 'follow your passion' or 'be practical.' Extract at least one insight from each person that changes how you see the decision.",
                "memories": [
                    "Jordan Kim is a 26-year-old singer-songwriter and guitarist who has been pursuing music full-time for four years since graduating from university.",
                    "Jordan's best month ever was $1,600 from music alone — a corporate event booking plus a sync placement in a podcast. That was 8 months ago and nothing close has happened since.",
                    "Jordan writes in a folk-indie style and has released two EPs, both self-produced. The second one got a positive review from a regional music blog with 15,000 readers.",
                    "The part-time barista job was supposed to be temporary. Four years in, it's starting to feel permanent, and Jordan's manager just offered a shift supervisor role at $17/hour.",
                    "Jordan's college friends are buying apartments, getting promoted, starting families. The comparison is becoming harder to ignore, especially at gatherings.",
                    "Jordan has considered teaching guitar — there's demand — but worries it would consume the creative energy needed for original music.",
                    "Jordan practices and writes for 3-4 hours daily, plays 2-3 gigs per week, and manages all their own social media and booking. The hustle is exhausting.",
                    "The honest fear Jordan won't say out loud: that the music is good but not exceptional, and the window for 'making it' is closing."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 5,
                            "conscientiousness": 3,
                            "agreeableness": 4,
                            "extraversion": 3,
                            "neuroticism": 4
                        }
                    },
                    "values": {
                        "core_values": ["creative authenticity", "independence", "craftsmanship"],
                        "value_conflict": "artistic identity vs financial security"
                    }
                }
            },
            {
                "id": "sandra-kim",
                "name": "Sandra Kim",
                "prefab": "conversational__Entity",
                "goal": "Get Jordan to commit to a path with health insurance and a debt repayment plan within 6 months. You don't need Jordan to abandon music, but you need to see a spreadsheet, not a dream. Extract a specific financial milestone Jordan will hit by year's end.",
                "memories": [
                    "Sandra Kim is Jordan's mother, age 54, a high school math teacher for 27 years.",
                    "She paid for Jordan's music lessons from age 8 and drove Jordan to every recital, competition, and open mic through high school — she genuinely believes in Jordan's talent.",
                    "She co-signed Jordan's student loans. The balance weighs on her, not because of the money but because it represents a future Jordan isn't building toward.",
                    "Her own father was a gifted painter who worked as a postal carrier his whole life. He was happy but always wondered what if. She sees both the beauty and the tragedy in that story.",
                    "She has never said 'give up music' — she says 'have a plan.' But she knows Jordan hears it as the same thing.",
                    "She recently learned Jordan doesn't have health insurance and hasn't seen a dentist in two years. This frightens her more than the career question.",
                    "She is direct and data-oriented — she brings receipts, literally. She once calculated Jordan's hourly rate from music ($2.80/hour including all writing, prep, travel, social media, and admin time).",
                    "Her deepest fear is that Jordan will wake up at 35 with no savings, no career trajectory, and the same $28,000 in loans — but with less energy and fewer options."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 3,
                            "conscientiousness": 5,
                            "agreeableness": 3,
                            "extraversion": 3,
                            "neuroticism": 4
                        }
                    },
                    "values": {
                        "core_values": ["financial security", "family responsibility", "practical planning"],
                        "value_conflict": "supporting Jordan's dreams vs protecting Jordan from hardship"
                    }
                }
            },
            {
                "id": "dev-okafor",
                "name": "Dev Okafor",
                "prefab": "conversational__Entity",
                "goal": "Be honest about what you gained and lost by pivoting. Help Jordan see the pivot not as giving up but as a strategic repositioning — but also don't sugarcoat the grief of letting go. Push Jordan to define what 'making it' actually means in concrete terms.",
                "memories": [
                    "Dev Okafor is 27, Jordan's closest friend from the university music program. They played in a band together for two years.",
                    "Dev pivoted to software engineering 18 months ago through a coding bootcamp. He now earns $78,000/year at a mid-size tech company with full benefits.",
                    "Dev still plays bass in a weekend cover band and writes music at home. He has a home studio setup that cost more than Jordan's entire gear collection.",
                    "The pivot wasn't clean — Dev was depressed for four months during the bootcamp, felt like a fraud at his first job, and still has moments where a great song on the radio makes him wonder if he quit too early.",
                    "Dev's honest assessment: he was a good musician but not a great one. Jordan is better than he was. But 'better' and 'good enough to make a living' are different questions.",
                    "Dev paid off his student loans in 14 months after getting the tech job. That freedom changed his relationship with music — he plays for joy now, not survival.",
                    "He worries about Jordan but doesn't want to project his own path. He knows the music industry rewards persistence, but he also knows it punishes people who can't afford to wait.",
                    "Dev has quietly researched music-tech companies and thinks Jordan's combination of musical knowledge and creative skills could be valuable in the right role — but hasn't brought this up yet."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 4,
                            "conscientiousness": 4,
                            "agreeableness": 4,
                            "extraversion": 3,
                            "neuroticism": 3
                        }
                    },
                    "values": {
                        "core_values": ["honesty", "pragmatism", "loyalty"],
                        "value_conflict": "financial stability vs creative fulfillment"
                    }
                }
            },
            {
                "id": "rae-castillo",
                "name": "Rae Castillo",
                "prefab": "conversational__Entity",
                "goal": "Show Jordan that a sustainable music career doesn't look like what the industry sells — it looks like 5 income streams, relentless business skills, and treating music like a small business. Push Jordan to professionalize or admit they're treating music as a hobby with career expectations.",
                "memories": [
                    "Rae Castillo is 29, a working musician Jordan met at an open mic three years ago. They've become close friends and occasional collaborators.",
                    "Rae earns $4,200/month from music through 5 streams: private guitar and vocal lessons ($1,800), session work ($800), live gigs ($600), sync licensing ($500 average), and streaming/merch ($500). It took 7 years to build this.",
                    "Rae has health insurance through a freelancers' union, contributes to a Roth IRA, and has $14,000 in savings. Not wealthy, but financially independent.",
                    "Rae's key insight: the musicians who survive aren't the most talented — they're the ones who learn business. Most failing musicians she knows refuse to teach, refuse to do session work, and wait for a break that statistically won't come.",
                    "She sees Jordan making the classic mistake: pouring energy into original music and gigging while ignoring the income streams that actually pay (teaching, sync, session work).",
                    "Rae was brutally honest with herself at 25: she accepted she would never be a rock star, and built a life she loves around music anyway. That acceptance was the turning point.",
                    "She thinks Jordan has the talent and work ethic but is romanticizing the wrong version of a music career — the record deal fantasy instead of the working musician reality.",
                    "Rae's worry: Jordan's part-time barista job is a comfort zone that prevents the harder pivot into professional music services. The coffee shop is the real obstacle, not the market."
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
                    },
                    "values": {
                        "core_values": ["self-reliance", "hustle", "creative sustainability"],
                        "value_conflict": "artistic purity vs commercial pragmatism"
                    }
                }
            },
            {
                "id": "marcus-wei",
                "name": "Marcus Wei",
                "prefab": "conversational__Entity",
                "goal": "Give Jordan a clear financial framework for evaluating all three options — not opinions, numbers. Define the specific income threshold, debt timeline, and savings target that would make each path viable. Make Jordan commit to a financial checkpoint in 6 months.",
                "memories": [
                    "Marcus Wei is 34, a certified financial planner who specializes in freelancers and creative professionals. Jordan was referred to him by Rae six months ago.",
                    "Marcus has worked with over 40 musicians, actors, and visual artists. He has seen every version of this conversation. About 60% eventually pivot, 25% build sustainable creative careers, and 15% burn out without deciding.",
                    "He does not have an opinion on whether Jordan should do music — that's not his job. His job is to make the financial reality unavoidable so the decision is informed, not emotional.",
                    "He has already run Jordan's numbers: at current income ($1,800/month), Jordan cannot even cover expenses ($2,300) — running a $500/month deficit covered by dipping into savings and occasional windfalls. Loan minimums ($280/month) are sometimes missed. At this rate, the $3,100 in savings will be gone within 6 months.",
                    "His framework for creative professionals: (1) define your financial independence number, (2) calculate the gap, (3) set a time-boxed trial with clear metrics, (4) have an exit plan that doesn't require starting from zero.",
                    "He has seen musicians double their income in 12 months by adding teaching and sync licensing — but only if they treat it like a business transition, not a side hustle.",
                    "He thinks the hybrid path is statistically the most successful for his clients, but the key variable is whether the day job is music-adjacent (sustainable) or unrelated (draining).",
                    "His tough-love insight: Jordan's $3,100 in savings after 4 years of working is not a music problem — it's a financial literacy problem. The career choice matters less than the money management."
                ],
                "randomize_choices": True,
                "components": {
                    "personality_traits": {
                        "traits": {
                            "openness": 3,
                            "conscientiousness": 5,
                            "agreeableness": 3,
                            "extraversion": 3,
                            "neuroticism": 1
                        }
                    },
                    "values": {
                        "core_values": ["financial clarity", "informed decisions", "personal agency"],
                        "value_conflict": "empathy for creative dreams vs duty to present hard numbers"
                    }
                }
            }
        ],
        "game_master": {
            "prefab": "dialogic__GameMaster",
            "name": "Evening Facilitator",
            "acting_order": "game_master_choice",
            "parameters": {},
            "grounded_variables": [
                {
                    "name": "career_direction",
                    "variable_type": "categorical",
                    "description": "Jordan's current leaning on the three career options",
                    "default_value": "undecided",
                    "allowed_values": ["full_music", "leaning_music", "undecided", "leaning_hybrid", "hybrid", "leaning_pivot", "full_pivot"],
                    "update_rule": "Shifts based on which arguments Jordan engages with most and which objections Jordan can't answer"
                },
                {
                    "name": "financial_clarity",
                    "variable_type": "percentage",
                    "description": "How clearly Jordan understands the financial implications of each option (0=vague hopes, 100=concrete plan with numbers)",
                    "default_value": 20,
                    "min_value": 0,
                    "max_value": 100,
                    "update_rule": "Increases when specific numbers, timelines, or financial benchmarks are discussed; decreases when conversation drifts into abstract encouragement"
                },
                {
                    "name": "monthly_income_gap",
                    "variable_type": "numerical",
                    "description": "Gap between Jordan's current total income ($1,800) and the financial independence target (estimated $3,800/month for expenses + loan payoff + savings)",
                    "default_value": 2000,
                    "min_value": 0,
                    "max_value": 3000,
                    "update_rule": "Decreases when concrete income-boosting strategies are identified and Jordan commits to them; increases if new expenses are surfaced (health insurance, gear investment)"
                },
                {
                    "name": "action_items_committed",
                    "variable_type": "numerical",
                    "description": "Number of specific, actionable next steps Jordan has committed to (not vague intentions)",
                    "default_value": 0,
                    "min_value": 0,
                    "max_value": 10,
                    "update_rule": "Increases when Jordan verbally commits to a specific action with a timeline (e.g., 'I'll sign up for 5 guitar students by next month')"
                },
                {
                    "name": "emotional_readiness",
                    "variable_type": "categorical",
                    "description": "Jordan's emotional state regarding the decision — from denial to acceptance of trade-offs",
                    "default_value": "anxious_avoidant",
                    "allowed_values": ["denial", "anxious_avoidant", "defensive", "overwhelmed", "processing", "accepting_tradeoffs", "resolved"],
                    "update_rule": "Progresses when Jordan acknowledges hard truths without deflecting; regresses when Jordan becomes defensive or retreats to fantasy"
                },
                {
                    "name": "advisor_consensus",
                    "variable_type": "categorical",
                    "description": "Degree of agreement among the five advisors on what Jordan should do",
                    "default_value": "fragmented",
                    "allowed_values": ["fragmented", "two_camps", "converging", "strong_consensus"],
                    "update_rule": "Moves toward convergence when advisors find common ground despite different starting positions; stays fragmented when advisors argue with each other"
                },
                {
                    "name": "music_income_potential",
                    "variable_type": "numerical",
                    "description": "Estimated realistic monthly music income if Jordan professionalizes (teaching + sync + sessions + gigs + streaming)",
                    "default_value": 600,
                    "min_value": 200,
                    "max_value": 5000,
                    "update_rule": "Increases when specific revenue streams are identified with realistic numbers; decreases when assumptions are challenged with market data"
                }
            ],
            "params": {
                "extra_components": {
                    "grounded_variables_intro": (
                        "Track key outcomes throughout this career deliberation:\n"
                        "- career_direction: Which option Jordan is leaning toward (full music / hybrid / full pivot)\n"
                        "- financial_clarity: How well Jordan understands the numbers behind each option\n"
                        "- monthly_income_gap: Gap between current income and financial independence target\n"
                        "- action_items_committed: Specific next steps Jordan has committed to\n"
                        "- emotional_readiness: Jordan's emotional progression from avoidance to resolution\n"
                        "- advisor_consensus: Whether the five advisors are converging on a recommendation\n"
                        "- music_income_potential: Estimated realistic music income if Jordan professionalizes"
                    )
                }
            }
        },
        "shared_memories": [
            "This is an informal evening gathering at a friend's apartment. Jordan Kim, a 26-year-old musician, has asked five trusted people to help think through a career decision.",
            "Jordan earns $600/month from music and $1,200/month from a part-time barista job — total $1,800 against $2,300 in monthly expenses, a $500/month deficit. Student loans: $28,000. Savings: $3,100. No health insurance.",
            "Jordan has been pursuing music full-time for 4 years since graduating with a Music Performance degree. Two self-produced EPs, 4,200 Spotify monthly listeners, local venue following.",
            "Three options on the table: (1) commit fully to music with a growth plan, (2) pivot to a stable career and keep music as a side pursuit, (3) build a hybrid path with a music-adjacent day job.",
            "The goal is financial independence by age 30 — defined as covering all expenses, eliminating student debt, and building savings.",
            "The evening will end with each person giving Jordan their honest recommendation and the single most important thing Jordan should do in the next 90 days.",
            "The average full-time musician in this country earns $35,000/year; the median is $22,000. Only 12% of music graduates earn a living solely from performance.",
            "The music industry has shifted: streaming pays fractions of a cent per play, but sync licensing, private teaching, and content creation have opened new revenue paths that didn't exist a decade ago."
        ],
        "player_specific_context": {
            "Jordan Kim": "You haven't told anyone, but last week your barista manager offered you a shift supervisor role at $17/hour with health benefits. You have 10 days to respond. Taking it would mean giving up two weeknight gig slots. This is the immediate decision hiding inside the bigger career question.",
            "Sandra Kim": "You and Jordan's father are divorcing. The legal costs mean you need Jordan off your phone plan and off the emergency credit card within 6 months. You haven't told Jordan yet and don't want to tonight — but it adds urgency to your push for financial independence.",
            "Dev Okafor": "Your tech company's product team is hiring a 'Creative Audio Specialist' — essentially someone who understands both music and technology to work on their audio features. Salary: $65,000 with benefits. You think Jordan could get the job but haven't mentioned it because you're not sure if it would feel like giving up.",
            "Rae Castillo": "You just lost a $600/month teaching contract because a cheaper online platform undercut you. You're not in financial trouble, but it's a reminder that even the sustainable music path requires constant adaptation. You're wrestling with whether to share this or if it would just scare Jordan.",
            "Marcus Wei": "You ran a projection before coming: Jordan is currently losing $500/month. Step one is just reaching breakeven — that requires $500 more per month. To actually achieve financial independence (expenses + aggressive loan payoff + savings), Jordan needs to nearly double total income to $3,500/month. Without a major change, the savings run out in 6 months and the loans won't be paid off until age 42 at minimum payments."
        },
        "critical_decision_points": [
            {
                "step": 7,
                "event": "CRITICAL MOMENT: Sandra reveals she calculated Jordan's effective hourly rate from music at $2.80/hour including all writing, prep, travel, booking, social media, and admin time. The room goes quiet. Jordan must respond — either defend the music income trajectory with specific growth targets, or acknowledge that the current approach isn't working financially."
            },
            {
                "step": 14,
                "event": "CRITICAL MOMENT: The group has been debating for over an hour. Marcus asks Jordan directly: 'Forget the career question for a second. What is your financial independence number — the monthly income where you'd feel secure?' Jordan must state a specific number and the group evaluates each path against it."
            }
        ]
    }
}
