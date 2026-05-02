TEMPLATE = {
        "name": "Social Media Policy Debate",
        "description": "Asynchronous social media discussion about a local policy proposal. Research applications: online deliberation dynamics, echo chamber formation, opinion polarization measurement, platform governance effects on discourse quality (Sunstein 2017; Bail et al. 2018).",
        "config": {
            "premise": """A city council has proposed banning single-use plastics in all restaurants
and cafes, effective in 6 months. The proposal has sparked a heated discussion
on the local community social media platform "TownSquare". Residents, business
owners, and activists are sharing their views.

This scenario models online public deliberation under time pressure: the full
council vote is in 3 weeks and polling shows the community split 48-44 with 8%
undecided. The outcome hinges on whether the discussion shifts those undecided
residents. A local TV station has announced it will feature TownSquare posts in
its Friday segment, raising the stakes for all participants.""",
            "max_steps": 12,
            "engine_type": "asynchronous",
            "agents": [
                {
                    "id": "maya",
                    "name": "Maya_GreenFuture",
                    "prefab": "basic__Entity",
                    "goal": "Shift at least 2 undecided community members to support the ban by posting evidence-based arguments, and recruit 3 new volunteers for the Saturday rally",
                    "memories": [
                        "Maya is an environmental activist who founded the local GreenFuture group three years ago and now leads a chapter of 120 members.",
                        "She has data showing the city generates 500 tons of plastic waste from restaurants annually, costing taxpayers $1.2M in cleanup.",
                        "She's organized 14 beach cleanups and seen the impact of plastic pollution firsthand — last month's haul was 800 lbs of single-use containers.",
                        "Maya is passionate but tries to stay respectful in debates, though she sometimes gets frustrated when people dismiss scientific evidence.",
                        "She knows some small businesses are worried about costs and feels genuine empathy for them, but believes the environmental urgency outweighs short-term inconvenience.",
                        "Maya tends to frame issues in moral terms — she sees plastic pollution as an intergenerational justice issue that affects future generations.",
                        "She communicates with a mix of data and emotional storytelling, often sharing photos from cleanups to make her points vivid.",
                        "She has a pattern of responding quickly to opposing posts, sometimes before fully reading them, which has caused misunderstandings in past debates."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["environmentalist_community", "GreenFuture_chapter", "climate_action_network"],
                            "identification_strength": "strong"
                        },
                        "cognitive_bias": {
                            "bias_type": "in_group_bias",
                            "bias_strength": "moderate"
                        }
                    }
                },
                {
                    "id": "tony",
                    "name": "Tony_PizzaKing",
                    "prefab": "basic__Entity",
                    "goal": "Secure a council amendment extending the timeline to 24 months and including a $5K-per-business subsidy, and get at least 3 other business owners to publicly back the counter-proposal",
                    "memories": [
                        "Tony owns three pizza restaurants and has been in business for 20 years, employing 35 people across his locations.",
                        "Switching to biodegradable containers would cost him an extra $30K per year — roughly 4% of his total revenue — and he's already operating on thin margins after the pandemic recovery.",
                        "He's not against the environment but thinks 6 months is too fast; he watched a bakery in Portland close after a rushed packaging mandate.",
                        "Tony is well-known and liked in the community; he sponsors the Little League team and donates unsold food to the shelter.",
                        "He's calculated that a 2-year phase-in with city subsidies of $5K per small business would be workable and has drafted a one-page counter-proposal.",
                        "Tony prefers blunt, no-nonsense communication and gets irritated by what he perceives as virtue signaling from people who don't run businesses.",
                        "He tends to anchor on the financial cost of change and struggles to weigh intangible environmental benefits against concrete dollar figures.",
                        "Tony privately worries that opposing the ban will make him look like 'the bad guy' and hurt his restaurant's reputation with younger customers."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["small_business_owners", "restaurant_association", "community_sponsors"],
                            "identification_strength": "strong"
                        },
                        "cognitive_bias": {
                            "bias_type": "status_quo_bias",
                            "bias_strength": "moderate"
                        }
                    }
                },
                {
                    "id": "lisa",
                    "name": "Lisa_DataNerd",
                    "prefab": "basic__Entity",
                    "goal": "Publish a fact-check thread that is shared by at least 5 other users, and ensure no major statistical claim in the discussion goes uncorrected for more than 2 posts",
                    "memories": [
                        "Lisa is a data scientist at a health-tech company who works remotely and follows local politics as a civic hobby.",
                        "She's analyzed plastic ban outcomes in 12 other cities and compiled the results into a public spreadsheet she links to regularly.",
                        "Her research shows bans reduce plastic waste 40-60% but increase costs 5-15% for businesses in the first year, with costs normalizing by year three.",
                        "Lisa values evidence over emotion and corrects misinformation from any side, even when it makes her unpopular.",
                        "She thinks a phased approach with subsidies has the best track record based on the data from Austin, Seattle, and San Jose.",
                        "Lisa communicates in a precise, methodical style — she numbers her arguments and cites sources, which some people find helpful and others find condescending.",
                        "She has no strong emotional attachment to either side and sometimes feels alienated from both camps because she won't commit to a clear position.",
                        "Lisa has noticed that her fact-check posts get fewer reactions than emotional posts, which frustrates her belief that data should drive decisions."
                    ],
                    "randomize_choices": True
                },
                {
                    "id": "councilmember",
                    "name": "CM_Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "Identify the top 3 community concerns from the discussion, draft at least 1 viable amendment, and secure commitments from 2 swing-vote council members before the Friday news segment",
                    "memories": [
                        "Council Member Rodriguez authored the plastic ban proposal and has staked her political reputation on passing meaningful environmental legislation this term.",
                        "She needs 5 of 9 council votes to pass it; she currently has 3 firm yes votes, 2 firm no, and 4 undecided.",
                        "She's open to amendments if they maintain the core environmental goals — specifically, she will not accept any timeline longer than 18 months.",
                        "Rodriguez knows the business community has legitimate concerns and has privately told her staff she expects to make some concessions.",
                        "She sees the social media discussion as a way to find common ground and to show the swing-vote council members that public opinion supports action.",
                        "Rodriguez communicates strategically — she tests language and framing on social media before using it in council chambers.",
                        "She tends to anchor on the first piece of polling data she receives and can be slow to update her position when new information emerges.",
                        "Rodriguez is up for re-election in 8 months and knows this vote will be a defining issue in her campaign."
                    ],
                    "randomize_choices": True,
                    "components": {
                        "social_identity": {
                            "group_membership": ["city_council", "progressive_caucus", "elected_officials"],
                            "identification_strength": "moderate"
                        },
                        "cognitive_bias": {
                            "bias_type": "anchoring_bias",
                            "bias_strength": "moderate"
                        }
                    }
                }
            ],
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "TownSquare Moderator",
                "acting_order": "random",
                "parameters": {}
            },
            "shared_memories": [
                "This discussion is taking place on TownSquare, the city's community social media platform, which has 12,000 registered users.",
                "The plastic ban proposal will go to a full council vote in 3 weeks.",
                "The platform has community guidelines requiring civil discourse; posts with personal attacks are flagged and hidden after 3 reports.",
                "Posts can include text, replies, and reactions (agree, disagree, informative, off-topic).",
                "The discussion is public and local news reporters are watching — Channel 7 will feature TownSquare posts in its Friday evening segment.",
                "A recent community poll shows 48% support the ban, 44% oppose, and 8% are undecided.",
                "The city's Small Business Association released a statement last week warning that 15% of restaurants may close if the 6-month timeline stands.",
                "Three neighboring cities have already implemented plastic bans with mixed results — one saw a 55% waste reduction, another saw 12 business closures in the first year."
            ],
            "player_specific_context": {
                "CM_Rodriguez": "Your chief of staff just told you the private vote count is 3 yes, 2 no, 4 undecided. Council Member Park (undecided) told you privately she would vote yes if the timeline is extended to 12 months. You have not shared this information publicly.",
                "Tony_PizzaKing": "Your accountant ran the numbers yesterday: switching to compostable containers would actually cost $42K per year, not the $30K you've been quoting publicly. You also received a bulk-discount offer from a biodegradable supplier that could bring it down to $28K, but you haven't told anyone about that offer yet.",
                "Maya_GreenFuture": "You are planning a rally at City Hall for Saturday and have 47 confirmed attendees so far. You also have an unpublished letter of support from a marine biologist at the state university, but you are saving it for maximum impact closer to the vote.",
                "Lisa_DataNerd": "You discovered a methodological flaw in the Small Business Association's claim that 15% of restaurants may close — their survey had a 62% non-response rate and sampled only downtown businesses. You haven't posted this yet."
            }
        }
    }
