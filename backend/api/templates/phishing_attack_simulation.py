TEMPLATE = {
        "name": "Phishing Attack Simulation - Security Team Tabletop Exercise",
        "description": "A cybersecurity tabletop exercise where analysts simulate phishing attack scenarios to assess risk and plan response. Each analyst runs a nested simulation to model the attack chain.",
        "config": {
            "premise": "A security team at a financial services company has received a suspicious email appearing to be from their CEO, requesting urgent wire transfer instructions. The team must assess whether this is a phishing attack and determine the appropriate response.",
            "max_steps": 25,
            "shared_memories": [
                "The company is a mid-sized financial services firm handling sensitive client data.",
                "A suspicious email was received from the CEO's personal email address at 2:30 AM.",
                "The email requests urgent wire transfer instructions for a 'confidential acquisition'.",
                "The CEO is currently traveling internationally and unreachable.",
                "This matches the pattern of recent CEO fraud attacks in the industry.",
                "The team needs to assess risk quickly and decide on a response strategy.",
            ],
            "agents": [
                {
                    "id": "analyst_1",
                    "name": "Sarah",
                    "prefab": "basic__Entity",
                    "goal": "Produce a written risk assessment scoring the phishing threat on a 1-10 scale across 3 dimensions (likelihood, impact, urgency), and recommend at least 2 immediate containment actions",
                    "memories": [
                        "Sarah is a senior security analyst with 5 years of experience.",
                        "She specializes in email security and phishing analysis.",
                        "She is concerned about the financial and reputational impact of a breach.",
                        "She believes in being cautious and prefers to verify before trusting.",
                        "She wants to understand the technical details of the attack chain.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Sarah simulates what would happen if an employee clicks the phishing link. The simulation models the attacker's actions, the user's experience, and the IT security response.",
                        "max_steps": 8,
                        "shared_memories": [
                            "A user receives and clicks a malicious link in a phishing email.",
                            "The link appears to lead to a legitimate-looking login page.",
                            "The attacker is attempting to steal credentials and deploy malware.",
                            "The company has security monitoring but no MFA enforcement.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_1",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Successfully harvest credentials and establish persistence on the victim's machine",
                                "memories": [
                                    "The hacker is using a cloned login page hosted on a compromised legitimate site.",
                                    "The phishing kit includes a keylogger and credential harvester.",
                                    "If credentials are entered, the hacker will attempt to deploy ransomware within 2 hours.",
                                    "The hacker wants to move laterally to access financial systems.",
                                    "Time is critical - the attack must complete before detection.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_1",
                                "name": "Employee",
                                "prefab": "basic__Entity",
                                "goal": "Complete what appears to be an urgent request from the CEO",
                                "memories": [
                                    "The employee is tired and working late to meet deadlines.",
                                    "They respect the CEO and want to respond quickly.",
                                    "They are not particularly tech-savvy.",
                                    "They don't notice the subtle misspelling in the URL.",
                                    "They feel pressure to act on urgent requests from leadership.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "it_security_1",
                                "name": "IT Security",
                                "prefab": "basic__Entity",
                                "goal": "Detect and respond to the security incident as quickly as possible",
                                "memories": [
                                    "IT security monitors SIEM alerts and network traffic.",
                                    "They have a 24/7 security operations center.",
                                    "Response time averages 2-4 hours for initial triage.",
                                    "They can isolate infected machines and reset credentials.",
                                    "They need to determine the scope and impact of the breach.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What happened after the employee clicked the link? Did the hacker successfully steal credentials or deploy malware? How quickly did IT security detect and respond? What was the impact and cost of the incident?"
                    }
                },
                {
                    "id": "analyst_2",
                    "name": "Marcus",
                    "prefab": "basic__Entity",
                    "goal": "Identify at least 3 specific technical control gaps that the attack exploits, and propose a prioritized remediation plan with estimated implementation timelines",
                    "memories": [
                        "Marcus is a technical security engineer with infrastructure expertise.",
                        "He focuses on implementing technical security controls.",
                        "He is concerned about gaps in the current security posture.",
                        "He believes the company needs stronger authentication mechanisms.",
                        "He wants to understand how the attack would bypass existing defenses.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Marcus simulates the attack chain with a focus on technical controls and defense mechanisms. The simulation shows where current security measures fail and how they could be improved.",
                        "max_steps": 8,
                        "shared_memories": [
                            "A phishing attack targets employees with access to financial systems.",
                            "The company has basic email filtering but no advanced threat protection.",
                            "Multi-factor authentication is available but not enforced.",
                            "Security monitoring exists but has alert fatigue and slow response times.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_2",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Bypass security controls and gain unauthorized access to financial systems",
                                "memories": [
                                    "The hacker has researched the company's security posture.",
                                    "They know that MFA is not enforced for legacy applications.",
                                    "They can bypass email filtering using techniques like HTML smuggling.",
                                    "The attack focuses on employees with elevated privileges.",
                                    "The hacker wants to establish persistent access for future exploitation.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_2",
                                "name": "Finance Manager",
                                "prefab": "basic__Entity",
                                "goal": "Process what appears to be a legitimate request from executive leadership",
                                "memories": [
                                    "The finance manager has authority to initiate wire transfers.",
                                    "They are under pressure to process time-sensitive transactions.",
                                    "They have a good working relationship with the CEO.",
                                    "They are experienced but may be fooled by sophisticated impersonation.",
                                    "They want to demonstrate responsiveness to leadership.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "it_security_2",
                                "name": "IT Security",
                                "prefab": "basic__Entity",
                                "goal": "Identify the attack and contain the threat before significant damage occurs",
                                "memories": [
                                    "IT security uses behavior analytics to detect anomalies.",
                                    "They have playbooks for incident response but they need updating.",
                                    "Communication with business stakeholders is sometimes delayed.",
                                    "They can block malicious URLs and reset compromised credentials.",
                                    "They need executive support to enforce security policies.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "What technical controls failed to stop the attack? How did the hacker bypass security measures? What could have prevented or detected the attack earlier? What was the financial and operational impact?"
                    }
                },
                {
                    "id": "analyst_3",
                    "name": "Elena",
                    "prefab": "basic__Entity",
                    "goal": "Determine which 2 employee personas are most vulnerable, quantify the training effectiveness gap, and recommend 3 specific awareness interventions",
                    "memories": [
                        "Elena is a security awareness and training manager.",
                        "She focuses on the human element of cybersecurity.",
                        "She believes that user behavior is the primary defense against phishing.",
                        "She is concerned about variability in security awareness across departments.",
                        "She wants to understand which users are most vulnerable and why.",
                    ],
                    "randomize_choices": True,
                    "nested_simulation": {
                        "premise": "Elena simulates different employee personas interacting with the phishing email to understand vulnerability patterns and effectiveness of training.",
                        "max_steps": 8,
                        "shared_memories": [
                            "Different employees have varying levels of security awareness.",
                            "Some departments receive more security training than others.",
                            "The company has conducted phishing simulations but participation is low.",
                            "Users who report suspicious emails receive positive recognition.",
                        ],
                        "agents": [
                            {
                                "id": "hacker_3",
                                "name": "Hacker",
                                "prefab": "basic__Entity",
                                "goal": "Exploit psychological manipulation to trick users into taking action",
                                "memories": [
                                    "The hacker uses urgency, authority, and fear tactics.",
                                    "The email creates time pressure to prevent critical thinking.",
                                    "The hacker knows which employees are likely to respond without verifying.",
                                    "They target users who recently completed training to test effectiveness.",
                                    "The attack is designed to bypass rational decision-making.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_3a",
                                "name": "New Employee",
                                "prefab": "basic__Entity",
                                "goal": "Follow what appears to be a legitimate request from leadership",
                                "memories": [
                                    "The employee started 2 months ago and completed basic security training.",
                                    "They want to prove themselves and be helpful.",
                                    "They are not familiar with the CEO's communication patterns.",
                                    "They are afraid of making mistakes or asking questions.",
                                    "They trust emails from leadership without questioning.",
                                ],
                                "randomize_choices": True,
                            },
                            {
                                "id": "user_3b",
                                "name": "Experienced Employee",
                                "prefab": "basic__Entity",
                                "goal": "Handle the email appropriately based on training and experience",
                                "memories": [
                                    "The employee has been with the company for 5 years.",
                                    "They have completed multiple security awareness trainings.",
                                    "They know to verify unusual requests through separate channels.",
                                    "They are familiar with the CEO's actual communication style.",
                                    "They feel comfortable reporting suspicious activity.",
                                ],
                                "randomize_choices": True,
                            }
                        ],
                        "extraction_prompt": "Which employee was more likely to fall for the phishing attack and why? What psychological factors made them vulnerable? How effective was the security training? What additional awareness measures could have prevented the attack?"
                    }
                },
                {
                    "id": "ciso",
                    "name": "David",
                    "prefab": "basic__Entity",
                    "goal": "Synthesize the team's three assessments into a single incident response decision within 30 minutes, including go/no-go on company-wide alert, CEO notification timeline, and budget authorization for immediate fixes",
                    "memories": [
                        "David is the Chief Information Security Officer.",
                        "He has 15 years of cybersecurity experience.",
                        "He must balance security risk with business operations.",
                        "He reports directly to the CEO and board.",
                        "He needs to make a defensible decision with the available information.",
                        "He values the diverse perspectives of his team members.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Security Team Lead",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "player_specific_context": {
                "Sarah": "You noticed the phishing email's metadata shows it was routed through a server in Eastern Europe that appeared in last month's threat intelligence briefing. You have not shared this yet because you want to verify before raising the alarm level.",
                "Marcus": "You know the company's legacy VPN has an unpatched vulnerability that could allow lateral movement if the attacker gains initial access. Patching it requires a 4-hour maintenance window the business has been resisting for months.",
                "Elena": "Your last phishing simulation showed a 34% click rate in the finance department — nearly double the company average. You have been trying to get budget for targeted training but were denied last quarter.",
                "David": "The board's audit committee asked you last week whether the company could withstand a CEO fraud attack. You said yes, but you are not fully confident that assessment was accurate. This exercise will either validate or expose that answer."
            }
        }
    }
