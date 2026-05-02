TEMPLATE = {
        "name": "Employee Satisfaction Survey",
        "description": "A structured Likert-scale questionnaire administered by the interviewer GM prefab. Research applications: synthetic survey respondent modeling, attitude measurement methodology, response bias studies (social desirability, acquiescence). Can be used to test how personality traits and organizational context affect survey responses.",
        "prefab_type": "interviewer__GameMaster",
        "config": {
            "premise": """An HR representative at Meridian Technologies (a 200-person software company)
conducts the annual employee satisfaction survey. The survey is presented as
anonymous, though employees sometimes wonder how anonymous it really is.

Organizational context: The company recently went through a reorganization that
merged two engineering teams. Morale is mixed — leadership claims the reorg
improved efficiency, but many employees feel their input was ignored. The CEO
announced a 'listening tour' in response to Glassdoor reviews citing poor
communication. This survey is part of that initiative.

Research note: This template models how an agent's personality, organizational
position, and recent experiences shape survey responses. Researchers can modify
the employee's memories, components, or goal to study response patterns under
different psychological profiles (e.g., high vs. low agreeableness, recent
positive vs. negative work experiences).""",
            "max_steps": 5,
            "agents": [
                {
                    "id": "employee",
                    "name": "Jordan Lee",
                    "prefab": "basic__Entity",
                    "goal": "Provide genuinely honest feedback that reflects your real experience — rate each dimension accurately even if some answers are uncomfortable, while maintaining professional composure",
                    "memories": [
                        "You are Jordan Lee, a mid-level software developer who has been at Meridian Technologies for 2 years.",
                        "Overall you are moderately satisfied — the work is interesting and the flexible remote policy is excellent.",
                        "You are frustrated by communication from management: the recent reorg was announced with zero input from the team, and priorities change without explanation.",
                        "You appreciate your direct manager (who is supportive) but distrust upper leadership's motives.",
                        "You worry slightly that the survey is not truly anonymous and that negative feedback could affect your performance review.",
                        "You tend to give moderate responses (3s and 4s) rather than extremes, even when you feel strongly — a habit you are trying to break.",
                        "Your team recently lost two senior engineers who left citing 'lack of growth opportunities,' which you silently agree with.",
                        "You believe the company has potential but needs to follow through on its promises rather than just announcing initiatives."
                    ],
                    "randomize_choices": False,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 3,
                                "conscientiousness": 4,
                                "agreeableness": 4,
                                "extraversion": 2,
                                "neuroticism": 3
                            }
                        },
                        "emotion": {
                            "current_emotion": "mild_frustration",
                            "emotion_intensity": "moderate"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "interviewer__GameMaster",
                "name": "HR Representative",
                "acting_order": "fixed",
                "parameters": {
                    "player_names": ["Jordan Lee"],
                    "questionnaires": [
                        {
                            "name": "Job Satisfaction",
                            "description": "Annual employee satisfaction survey",
                            "questionnaire_type": "multiple_choice",
                            "observation_preprompt": "Please answer the following questions about your job satisfaction.",
                            "preprompt": "You are participating in an anonymous employee satisfaction survey. Please rate each statement on a scale of 1-5.",
                            "questions": [
                                {
                                    "statement": "I am satisfied with my current role and responsibilities.",
                                    "dimension": "job_satisfaction",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "Communication from management is clear and timely.",
                                    "dimension": "management_communication",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I have the tools and resources I need to do my job effectively.",
                                    "dimension": "resources",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I would recommend this company as a good place to work.",
                                    "dimension": "recommendation",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                },
                                {
                                    "statement": "I feel valued and recognized for my contributions.",
                                    "dimension": "recognition",
                                    "preprompt": "On a scale of 1 (Strongly Disagree) to 5 (Strongly Agree),",
                                    "choices": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                                    "ascending_scale": True
                                }
                            ]
                        }
                    ]
                }
            },
            "shared_memories": [
                "This is an anonymous survey.",
                "The HR representative is friendly and professional.",
                "The company values honest feedback.",
                "Responses will be aggregated for management review."
            ]
        }
    }
