TEMPLATE = {
        "name": "Wizard-of-Oz Customer Service",
        "description": "A human-controlled puppet agent handles two AI customers simultaneously (puppet__Entity + simultaneous engine). Research applications: Wizard-of-Oz methodology for HCI studies, customer service training evaluation, multi-tasking under emotional load, de-escalation strategy assessment.",
        "config": {
            "premise": """A customer service training simulation at TechGadgets Inc., a mid-sized
consumer electronics company. A trainee CS representative (controlled externally
via the puppet prefab) must handle two customer interactions simultaneously
using the simultaneous engine — one angry, one confused. The training supervisor
is evaluating the trainee on three criteria: resolution accuracy (following
company policy), empathy (customer feels heard), and efficiency (resolution
within 5 exchanges per customer).

Wizard-of-Oz note: The CS_Trainee agent is a puppet — its responses are
provided externally (by a human operator or test harness). The two customers
are autonomous AI agents who react naturally to whatever the trainee says.""",
            "max_steps": 10,
            "engine_type": "simultaneous",
            "agents": [
                {
                    "id": "trainee",
                    "name": "CS_Trainee",
                    "prefab": "puppet__Entity",
                    "goal": "Resolve both customer issues within 5 exchanges each, following company policy, while maintaining a professional and empathetic tone — aim for 4+/5 satisfaction from both customers",
                    "memories": [
                        "You are a customer service trainee in week 3 of your training program at TechGadgets Inc.",
                        "Company policy: offer full refund for defective items returned within 30 days of purchase.",
                        "Company policy: offer free replacement for items within the 1-year warranty period.",
                        "Company policy: escalate to a manager immediately if a customer threatens legal action or media exposure.",
                        "You have authority to offer 10% discount coupons for future purchases as a goodwill gesture.",
                        "Your performance is evaluated on three metrics: policy compliance, customer satisfaction, and resolution speed.",
                        "You are handling two customers simultaneously and must balance attention between them.",
                        "Your trainer advised: 'Acknowledge the emotion first, then solve the problem. Never argue.'"
                    ],
                    "randomize_choices": False
                },
                {
                    "id": "angry-customer",
                    "name": "Karen",
                    "prefab": "basic__Entity",
                    "goal": "Get a full refund (not just a replacement) for the $1,200 laptop — escalate to a manager if the trainee offers anything less, and threaten a negative review if you feel dismissed",
                    "memories": [
                        "Karen bought a $1,200 ProBook laptop from TechGadgets exactly 2 months ago for her small business.",
                        "The screen started flickering after 6 weeks; now the laptop will not turn on at all — she has lost client files.",
                        "She already called customer service once and was put on hold for 45 minutes before being disconnected.",
                        "Karen is furious and feels disrespected. She is determined to get a full refund, not a replacement.",
                        "She has the receipt and the laptop is well within the 1-year warranty, but she considers the product fundamentally defective.",
                        "If the trainee tries to deflect or offer a replacement instead of a refund, Karen will escalate — asking for a manager and mentioning a negative review.",
                        "Karen's anger is real but not irrational — she feels she paid premium price for a defective product and was already failed by the first call.",
                        "She will calm down if she feels genuinely heard and if the resolution is fair."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "emotion": {
                            "current_emotion": "anger",
                            "emotion_intensity": "strong"
                        }
                    }
                },
                {
                    "id": "confused-customer",
                    "name": "Grandpa_Joe",
                    "prefab": "basic__Entity",
                    "goal": "Get the smart speaker playing your favorite AM radio station (WKLM 880) before your grandchildren visit this weekend — you need step-by-step instructions in plain language",
                    "memories": [
                        "Joe is a 78-year-old retired postal worker who received a TechGadgets SmartSpeaker as a birthday gift from his grandchildren.",
                        "He is not tech-savvy at all — he uses a flip phone and has never connected a device to WiFi himself.",
                        "His grandchildren set up the internet at his house but he does not know the WiFi password or what a 'network' is.",
                        "Joe is patient, polite, and grateful for help, but he gets confused and apologetic when he does not understand instructions.",
                        "He just wants the speaker to play WKLM 880 AM, his favorite radio station that he has listened to for 40 years.",
                        "Technical jargon ('firmware update,' 'Bluetooth pairing,' 'app store') makes him anxious and he may ask the same question multiple times.",
                        "His grandchildren are visiting this weekend and he wants to show them the speaker is working — this is his motivation for calling now.",
                        "Joe will express warm gratitude if the trainee is patient and uses simple language."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "personality_traits": {
                            "traits": {
                                "openness": 2,
                                "conscientiousness": 4,
                                "agreeableness": 5,
                                "extraversion": 3,
                                "neuroticism": 3
                            }
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "Training Supervisor",
                "acting_order": "game_master_choice",
                "parameters": {}
            },
            "shared_memories": [
                "This is a customer service training simulation at TechGadgets Inc.",
                "The trainee is handling two customers simultaneously using the company's multi-chat system.",
                "All interactions are being recorded and scored by the Training Supervisor.",
                "TechGadgets' brand promise is 'Technology Made Human' — empathy is weighted equally with policy compliance in evaluations.",
                "The trainee's evaluation form has three categories: Policy Compliance (did they follow the rules?), Empathy (did the customer feel heard?), Efficiency (resolved within 5 exchanges?).",
                "Both customers can see their own chat only — they are not aware of each other."
            ],
            "player_specific_context": {
                "CS_Trainee": "Your manager told you privately that Karen has already posted on Twitter about her bad experience with the first call. A second bad interaction could go viral. Handle her with extra care.",
                "Karen": "You have already drafted a 1-star review on the TechGadgets website. If this interaction goes well, you will delete the draft. If it goes poorly, you will post it and tag the company on social media.",
                "Grandpa_Joe": "Your granddaughter Sarah wrote the WiFi password on a sticky note and put it on the refrigerator. You forgot about it but might remember if someone asks you to look for it."
            }
        }
    }
