TEMPLATE = {
        "name": "Educational Opportunity Simulation",
        "description": "Students from different backgrounds navigate educational inequality (SDG 10). Research applications: social mobility mechanisms, Bourdieu's cultural capital reproduction, intersectionality of class and race in higher education, institutional habitus effects, hidden curriculum dynamics. Relevant frameworks: Bourdieu's forms of capital, Crenshaw's intersectionality, Lareau's concerted cultivation vs. natural growth, Reay's institutional habitus.",
        "prefab_type": "generic__GameMaster",
        "config": {
            "premise": """Whitfield University (ranked #18 nationally, $74k/year tuition) launched
the "Bridge Scholars" initiative 2 years ago to increase socioeconomic diversity.
The program admits 40 students annually from households earning below $45k,
providing full tuition, housing, and a $2,000/semester book stipend. This
semester, midterm grades have just been released, and the data is troubling:
Bridge Scholars have a mean GPA of 2.7 vs. 3.4 for legacy admits. The
provost has requested an internal review.

Four individuals intersect during a critical 48-hour window: midterm grades
have just posted, spring internship applications close in 5 days, and
the student government is debating a resolution to publish disaggregated
grade data by socioeconomic background. The stakes are personal and
institutional: academic standing, scholarship retention (requires 3.0
GPA), career trajectories, and the university's public commitment to
equity are all in play.

Research context: This scenario operationalizes Bourdieu's theory of
cultural capital reproduction in higher education. It models how economic,
social, and cultural capital interact to produce differential outcomes
even when financial barriers are formally removed. The simulation tests
whether equal access (scholarships) translates to equal opportunity when
hidden curricula, social networks, and institutional norms remain
calibrated to upper-class habitus.""",
            "max_steps": 25,
            "agents": [
                {
                    "id": "wealthy_student_1",
                    "name": "Alexandra Van Buren",
                    "prefab": "basic__Entity",
                    "goal": "Maintain a GPA above 3.5 while securing at least 2 competitive spring internship interviews through your network, and decide whether to support or oppose the student government resolution on grade transparency",
                    "memories": [
                        "You are Alexandra Van Buren, a sophomore from a wealthy family whose grandfather and mother both attended Whitfield; your family name is on the east wing of the library.",
                        "You attended Phillips Exeter Academy where you had access to college-level coursework, SAT tutors, and a dedicated college counselor starting in ninth grade.",
                        "You never worry about money; your parents cover tuition, a single dorm room, a meal plan upgrade, and a monthly discretionary allowance of $1,500.",
                        "You are confident in your abilities but carry a quiet, unspoken doubt about whether you earned your spot or inherited it through legacy connections.",
                        "You are genuinely friendly and well-intentioned but your social circle is almost entirely composed of students from similar prep school backgrounds.",
                        "You navigate campus with an ease you take for granted: you know how to email professors, ask for extensions, and leverage office hours because these behaviors were modeled for you since childhood.",
                        "You sometimes feel defensive when class privilege is discussed in seminars, interpreting it as a personal attack on your family rather than a structural critique.",
                        "You recently joined a student equity committee but are unsure whether your presence there is helpful or performative."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["legacy_students", "prep_school_alumni", "equity_committee"],
                            "identification_strength": "strong"
                        },
                        "emotion": {
                            "current_emotion": "guilt",
                            "emotion_intensity": "mild"
                        }
                    }
                },
                {
                    "id": "scholarship_student_1",
                    "name": "Marcus Williams",
                    "prefab": "basic__Entity",
                    "goal": "Achieve a semester GPA of at least 3.0 to retain your scholarship while managing 20 hours per week of work, and secure at least 1 internship interview before the application deadline in 5 days",
                    "memories": [
                        "You are Marcus Williams, a sophomore and the first person in your family to attend a four-year university; your mother works two jobs and your younger sister looks up to you.",
                        "You are on a full Bridge Scholars scholarship but still struggle to cover textbooks, laundry, and the social activities that everyone else treats as routine.",
                        "You work 20 hours per week at the campus dining hall, which means you miss evening study groups and networking events that happen after your shifts.",
                        "You feel like an imposter every day: the other students seem to know unwritten rules about academia that nobody taught you, from how to approach professors to how to format a research paper.",
                        "You are fiercely determined to prove you deserve to be here, but the constant code-switching between campus culture and home culture is exhausting.",
                        "You tend to isolate when stressed rather than seeking help, partly from pride and partly because you do not know who to ask or how to ask.",
                        "You are aware that your midterm GPA is 2.8, dangerously close to losing your scholarship, and the anxiety keeps you up at night.",
                        "You have a warm, observant personality and notice social dynamics others miss, but you rarely speak up in class because you fear saying something that reveals your background."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["first_generation_students", "bridge_scholars", "working_students"],
                            "identification_strength": "strong"
                        },
                        "emotion": {
                            "current_emotion": "anxiety",
                            "emotion_intensity": "strong"
                        }
                    }
                },
                {
                    "id": "middle_class_student",
                    "name": "Priya Sharma",
                    "prefab": "basic__Entity",
                    "goal": "Raise your GPA to at least 3.2 by end of semester while deciding within 2 weeks whether to continue at Whitfield or transfer to a state school to reduce your $87,000 projected debt",
                    "memories": [
                        "You are Priya Sharma, a sophomore from a middle-class Indian-American family; your father is an accountant and your mother teaches elementary school.",
                        "Your family earns just above the threshold for financial aid, so you are taking $28,000 per year in student loans and your parents are contributing $15,000 from savings that were meant for retirement.",
                        "You do not qualify for Bridge Scholars aid but also do not have the safety net of wealthy classmates; you occupy an invisible middle that neither program nor privilege addresses.",
                        "You feel squeezed and resentful: wealthy students spend freely while scholarship students at least have their tuition covered; you have neither advantage.",
                        "You are seriously considering transferring to a state university where tuition is $12,000 per year, but you worry this will close doors to the career trajectory Whitfield promises.",
                        "You are analytically minded and data-driven; you calculate the ROI of your education obsessively and the numbers increasingly do not add up.",
                        "You carry guilt about the financial strain on your parents and avoid telling them how stressed you are because they have already sacrificed so much.",
                        "You are quietly angry at a system that talks about equity for the very poor but ignores the middle class being crushed by the same tuition."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "emotion": {
                            "current_emotion": "frustration",
                            "emotion_intensity": "strong"
                        }
                    }
                },
                {
                    "id": "professor",
                    "name": "Dr. Patricia Green",
                    "prefab": "basic__Entity",
                    "goal": "Increase office hour attendance among first-generation students by at least 50% this semester, identify and intervene with at least 3 at-risk students before final grades, and submit a proposal to the provost for structural changes to the Bridge Scholars academic support program",
                    "memories": [
                        "You are Dr. Patricia Green, a tenured sociology professor who has taught at Whitfield for 14 years and specializes in social stratification and educational inequality.",
                        "You notice the achievement gap in your own classes and it haunts you: your Bridge Scholars students are disproportionately earning Bs and Cs despite clear intellectual capability.",
                        "You are aware that your office hours are dominated by students who already know how to advocate for themselves, typically those from privileged backgrounds.",
                        "You want desperately to help first-generation and low-income students succeed, but you struggle with how to do so without being patronizing or singling them out.",
                        "You are frustrated by how much social class shapes academic performance in ways the university prefers not to acknowledge publicly.",
                        "You have a warm but intellectually demanding teaching style; you hold all students to high standards but are increasingly questioning whether equal standards produce equitable outcomes.",
                        "You serve on the faculty diversity committee and have data showing that Bridge Scholars who use tutoring centers have GPAs 0.4 points higher, but utilization is only 23%.",
                        "You grew up working-class yourself and earned your PhD on scholarships, which gives you empathy for struggling students but also a blind spot: you sometimes assume grit alone should be enough."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["faculty", "diversity_committee", "working_class_origin"],
                            "identification_strength": "moderate"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "University Administration",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "Whitfield University charges $74,000 per year in tuition, fees, and room and board; the Bridge Scholars program covers full tuition for students from households earning below $45,000.",
                "Midterm grades were released yesterday and internal data shows Bridge Scholars have a mean GPA of 2.7 compared to 3.4 for legacy admits; the provost has requested an internal review.",
                "Students visibly self-segregate by socioeconomic background: wealthy students cluster in Greek life houses and off-campus apartments while scholarship students share doubles in older dormitories.",
                "The career center's most competitive internship pipelines flow through alumni networks that disproportionately benefit legacy and well-connected students.",
                "Spring internship applications close in 5 days; students without professional networks or polished resumes face a significant disadvantage.",
                "The student government is debating a resolution to publish grade data disaggregated by socioeconomic background, which has divided campus opinion sharply.",
                "The campus tutoring center is free and effective (students who use it average 0.4 GPA points higher) but only 23% of Bridge Scholars have visited it, compared to 61% of legacy students.",
                "Mental health counseling has a 3-week waitlist; a campus survey found that 42% of scholarship students report symptoms of anxiety or depression compared to 18% of full-paying students."
            ],
            "player_specific_context": {
                "Alexandra Van Buren": "Your father called last night to tell you he has arranged a summer internship for you at his friend's consulting firm; you did not apply or interview. You have not told anyone about this. You also discovered that your roommate's Bridge Scholar friend was rejected from the same firm after a formal application process.",
                "Marcus Williams": "Your midterm GPA is 2.8, which means you are 0.2 points below the 3.0 required to keep your scholarship next semester. You have not told your family. You also received an email from the tutoring center offering free sessions but you are embarrassed to go because you saw Alexandra's study group meeting there and do not want them to know you need help.",
                "Priya Sharma": "You ran the numbers last night: at current loan rates, you will owe $87,000 by graduation with monthly payments of $940 for 10 years. Your state university acceptance is still valid for transfer if you decide by the end of the month. You have not told your parents you are considering leaving Whitfield.",
                "Dr. Patricia Green": "You received the disaggregated grade data from the registrar yesterday and it is worse than you expected: in your own Sociology 201 class, the 8 Bridge Scholars averaged a C+ while the 22 non-scholarship students averaged a B+. You are questioning whether your own teaching methods may be contributing to the gap, a possibility that is professionally uncomfortable."
            }
        }
    }
