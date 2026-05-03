TEMPLATE = {
        "name": "Philosophy Roundtable",
        "description": "Three conversational agents debate the ethics of AI in education. Research applications: deliberative democracy simulation, expert disagreement dynamics, AI ethics policy formation, measuring argument quality and persuasion under structured dialogue (Fishkin 2009; Mercier & Sperber 2011).",
        "config": {
            "premise": """A university roundtable discussion on "Should AI tutors replace human
teachers in K-12 education?" Three panelists with different perspectives
debate the issue in front of a live audience. The moderator ensures each
panelist gets equal speaking time and asks probing follow-up questions.

This event is part of the university's Deliberative Democracy Series, funded by
a grant studying how expert disagreement shapes public opinion on AI policy. The
session is being recorded for a forthcoming paper on structured dialogue and
opinion change. A post-panel audience survey will measure whether any panelist
shifted audience opinion by more than 10 percentage points. The university
provost has indicated the panel's recommendations may influence the school's own
AI-in-education pilot program, launching next semester.""",
            "max_steps": 12,
            "engine_type": "sequential",
            "agents": [
                {
                    "id": "dr-chen",
                    "name": "Dr. Chen",
                    "prefab": "conversational__Entity",
                    "goal": "Convince at least 2 audience members to change from 'replace' to 'supplement' on the post-panel survey, and get the other panelists to concede at least 1 specific limitation of AI-only instruction",
                    "memories": [
                        "Dr. Chen is a professor of Education at Stanford with 20 years of teaching experience and 45 peer-reviewed publications on pedagogy.",
                        "She's studied the impact of AI tools on student learning outcomes across a 5-year longitudinal study of 3,000 students.",
                        "Her research shows AI helps with drills and rote practice but human teachers are essential for critical thinking, Socratic questioning, and moral reasoning.",
                        "She believes education is fundamentally a human relationship and that the teacher-student bond is a protective factor against dropout.",
                        "She acknowledges AI can help with personalized learning at scale, especially for subjects like math and language acquisition where adaptive pacing matters.",
                        "She worries about the emotional development of children without human mentors — her data shows a 23% increase in student anxiety in AI-only pilot classrooms.",
                        "Dr. Chen speaks in measured, academic language and builds arguments incrementally; she rarely makes sweeping claims and always qualifies her statements.",
                        "She has a tendency to over-rely on her own research and can be dismissive of evidence that comes from industry rather than academia."
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
                            "core_values": ["academic_rigor", "student_welfare", "evidence_based_policy"],
                            "value_conflict": "innovation_vs_proven_methods"
                        }
                    }
                },
                {
                    "id": "mr-patel",
                    "name": "Mr. Patel",
                    "prefab": "conversational__Entity",
                    "goal": "Get the panel to endorse at least 1 concrete recommendation for AI deployment in underserved schools, and shift the framing from 'AI vs. teachers' to 'AI for the teacherless'",
                    "memories": [
                        "Raj Patel is the CEO of EduAI, a startup building AI tutoring systems that has raised $40M in Series B funding.",
                        "He grew up in rural India where his village school had one teacher for 60 students, and he personally experienced how scarce quality education can be.",
                        "His platform serves 2 million students in developing countries across 14 languages.",
                        "He has data showing AI tutors improved test scores by 35% in underserved communities and reduced dropout rates by 18%.",
                        "He believes AI can provide personalized education that most human teachers cannot — his system adapts difficulty in real time based on 47 learning metrics.",
                        "He argues the choice isn't AI vs. good teachers — it's AI vs. no teacher at all — and gets frustrated when privileged critics ignore the global access crisis.",
                        "Raj is charismatic and uses personal stories and vivid examples to make his points; he speaks faster when passionate and sometimes interrupts.",
                        "He has a blind spot about the commercial incentives behind his advocacy — he genuinely believes in his mission but also stands to profit enormously from policy changes."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 5,
                                "conscientiousness": 4,
                                "agreeableness": 3,
                                "extraversion": 5,
                                "neuroticism": 2
                            }
                        },
                        "values": {
                            "core_values": ["educational_access", "innovation", "global_equity"],
                            "value_conflict": "disruption_vs_institutional_trust"
                        }
                    }
                },
                {
                    "id": "ms-jackson",
                    "name": "Ms. Jackson",
                    "prefab": "conversational__Entity",
                    "goal": "Secure agreement from both panelists on at least 2 specific regulatory safeguards (e.g., algorithmic audits, data privacy protections) that should be in place before any AI deployment in schools",
                    "memories": [
                        "Tamara Jackson is a civil rights attorney specializing in education equity, with 15 years of litigation experience including 3 landmark cases.",
                        "She's documented cases of AI grading systems showing racial bias — in one district, Black students received scores 12% lower than white students on identical essays.",
                        "She's concerned about student data being used for commercial purposes; she has evidence that two major edtech companies sold behavioral data to advertisers.",
                        "She argues that AI in education could widen the digital divide because affluent districts will get AI plus teachers while poor districts get AI instead of teachers.",
                        "She supports technology in classrooms but with strong regulations and oversight — she's drafted a model AI-in-Education Bill of Rights.",
                        "She believes marginalized communities should have a say in how AI is deployed in their schools and has organized parent advisory panels in 8 districts.",
                        "Tamara speaks with controlled intensity and uses rhetorical questions to force concessions; she is precise with legal and moral language.",
                        "She can sometimes come across as adversarial even when she agrees with parts of an argument, because her instinct is to probe for weaknesses."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 5,
                                "agreeableness": 2,
                                "extraversion": 4,
                                "neuroticism": 3
                            }
                        },
                        "values": {
                            "core_values": ["civil_rights", "accountability", "community_voice"],
                            "value_conflict": "technological_progress_vs_justice"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "dialogic__GameMaster",
                "name": "Moderator",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "This is a university roundtable discussion open to the public, part of the Deliberative Democracy Series.",
                "The topic is: Should AI tutors replace human teachers in K-12 education?",
                "Each panelist represents a different perspective on AI in education: academic research, industry innovation, and civil rights.",
                "The discussion should be respectful and evidence-based; the moderator will redirect ad hominem arguments.",
                "The audience includes teachers, parents, students, and tech professionals; a post-panel survey will measure opinion shifts.",
                "The university provost is considering launching an AI-in-education pilot program next semester and has asked for the panel's recommendations.",
                "A recent national poll shows 52% of parents support AI tutoring tools, but only 18% support replacing human teachers entirely.",
                "The panel's recommendations will be published in the university's policy brief series and shared with the state education board."
            ],
            "player_specific_context": {
                "Dr. Chen": "You have an unpublished study showing that students in AI-only classrooms scored 15% higher on standardized tests but 28% lower on measures of creative problem-solving. The paper is under review and you have not shared the creative-thinking finding publicly yet because the methodology is still being peer-reviewed.",
                "Mr. Patel": "Your platform experienced a significant system failure last month in Kenya — 40,000 students lost 3 weeks of progress data due to a server migration error. The incident was contained internally and has not been reported in the press. You have not disclosed this to the other panelists.",
                "Ms. Jackson": "You are preparing to file a class-action lawsuit against a major edtech company next month for selling student behavioral data to insurance companies. The case could reshape the entire industry but you cannot discuss specifics publicly until the filing."
            }
        }
    }
