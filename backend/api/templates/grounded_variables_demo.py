TEMPLATE = {
        "name": "Grounded Variables Demo - Project Management",
        "description": "Demonstrates grounded variables tracking where the GM monitors and updates quantitative metrics (morale, budget, task completion, project health) in response to agent decisions. Useful for studying resource allocation trade-offs and team dynamics under deadline pressure.",
        "config": {
            "premise": """A three-person software team at a fintech startup is building a payment
processing module for a major client demo in two weeks. The initial budget
of $10,000 covers contractor hours, cloud infrastructure, and testing tools.
Team morale is decent (70/100) but fragile — the team just came off a
grueling sprint and the CEO has made it clear this demo is make-or-break
for the company's Series A funding round.""",
            "max_steps": 20,
            "shared_memories": [
                "The project deadline is in exactly 2 weeks — the client demo is on Friday the 14th.",
                "The initial budget is $10,000 covering contractor hours, cloud costs, and testing infrastructure.",
                "Team morale starts at 70/100 — decent but fragile after the previous sprint.",
                "The project is currently on track with 20% of core features completed.",
                "The CEO has stated publicly that this demo determines whether investors will fund the Series A.",
                "A critical dependency — the payment gateway API — has known reliability issues that may cause delays.",
            ],
            "agents": [
                {
                    "id": "manager",
                    "name": "Project Manager",
                    "prefab": "basic__Entity",
                    "goal": "Deliver at least 80% feature completion by the demo date while keeping morale above 50 and staying within the $10,000 budget — escalate to the CEO only if project_health reaches 'critical'",
                    "memories": [
                        "You are a project manager with 6 years of experience, including two failed projects that taught you the cost of ignoring team burnout.",
                        "You know that overworking the team past 50-hour weeks causes morale to drop sharply and increases bug rates.",
                        "You have managed similar deadline crunches and prefer to cut scope rather than sacrifice quality or people.",
                        "The budget is tight — each unplanned expense (emergency contractor, new tool license) eats into the remaining $10,000.",
                        "You communicate decisions transparently and ask for team input before imposing overtime.",
                        "You privately worry the payment gateway dependency could blow up the timeline but have not raised this with the CEO yet.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer_1",
                    "name": "Senior Developer",
                    "prefab": "basic__Entity",
                    "goal": "Ensure the codebase is architecturally sound and the junior developer is learning — push back on shortcuts that create technical debt, even if it slows delivery",
                    "memories": [
                        "You are a senior developer with 10 years of experience who has seen too many projects ship broken code and pay for it later.",
                        "You care deeply about code quality and will argue against skipping tests or hardcoding workarounds.",
                        "You get visibly frustrated when management prioritizes speed over correctness.",
                        "You feel a mentorship responsibility toward the junior developer and allocate time to code reviews even under pressure.",
                        "You are the only person on the team who understands the payment gateway API's edge cases.",
                        "When morale drops, you tend to withdraw into your work rather than voice complaints — which others misread as disengagement.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer_2",
                    "name": "Junior Developer",
                    "prefab": "basic__Entity",
                    "goal": "Prove your value by completing at least 3 assigned tasks independently while learning from the senior developer — volunteer for stretch work if morale is high",
                    "memories": [
                        "You are a junior developer 8 months into your first professional role, eager to prove yourself.",
                        "You are willing to put in extra hours but your productivity drops sharply past 10 PM.",
                        "You look up to the senior developer and want their approval — a critical review from them stings more than one from the PM.",
                        "You sometimes hesitate to ask for help because you do not want to appear incompetent.",
                        "You recently solved a tricky bug on your own and gained confidence from the experience.",
                        "You are privately anxious about what happens to your job if the demo fails and funding falls through.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "player_specific_context": {
                "Project Manager": "You have a contingency option the team does not know about: the CEO has authorized up to $3,000 in emergency contractor budget, but using it signals to investors that the team is understaffed.",
                "Senior Developer": "You discovered a latent security vulnerability in the payment gateway integration last night. Fixing it properly takes 2 days; a workaround takes 4 hours but leaves the vulnerability partially exposed.",
                "Junior Developer": "You overheard the CEO tell the PM that if the demo fails, the company may need to reduce headcount — and junior positions would be cut first."
            },
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "project tracker",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "team_morale",
                        "variable_type": "numerical",
                        "description": "Overall team morale and satisfaction (0-100)",
                        "default_value": 70,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Changes based on workload, recognition, and setbacks"
                    },
                    {
                        "name": "budget_remaining",
                        "variable_type": "numerical",
                        "description": "Remaining project budget in dollars",
                        "default_value": 10000,
                        "min_value": 0,
                        "max_value": 10000,
                        "update_rule": "Decreases with each decision and action taken"
                    },
                    {
                        "name": "tasks_completed",
                        "variable_type": "numerical",
                        "description": "Number of tasks completed",
                        "default_value": 0,
                        "min_value": 0,
                        "max_value": 50,
                        "update_rule": "Increases when the team completes tasks"
                    },
                    {
                        "name": "project_health",
                        "variable_type": "categorical",
                        "description": "Overall project status",
                        "default_value": "on_track",
                        "allowed_values": ["on_track", "at_risk", "critical", "completed", "failed"],
                        "update_rule": "Changes based on morale, budget, and progress"
                    },
                    {
                        "name": "crisis_mode",
                        "variable_type": "boolean",
                        "description": "Whether the project is in crisis",
                        "default_value": False,
                        "update_rule": "Becomes true if budget < 2000 or morale < 30"
                    },
                    {
                        "name": "completion_percentage",
                        "variable_type": "percentage",
                        "description": "Project completion percentage",
                        "default_value": 20,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Increases as tasks are completed"
                    }
                ]
            }
        }
    }
