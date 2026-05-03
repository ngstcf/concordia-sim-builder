TEMPLATE = {
        "name": "Urban Gentrification - Housing Policy & Neighborhood Change",
        "description": "Longitudinal urban economics simulation tracking neighborhood metrics. Stakeholders debate development proposals while GM tracks rent, displacement, business survival, and affordability over time.",
        "config": {
            "premise": "The historically working-class neighborhood of Elmwood is facing rapid change. A tech company's nearby expansion has brought new investment and interest, but also concerns about displacement and loss of community character. The City Council is holding a SERIES OF VOTES over the next several meetings to DECIDE on specific housing policies and development proposals. Stakeholders include long-term residents, housing advocates, real estate developers, small business owners, and city planners. CURRENT STATE: Median monthly rent is $1800 for a 2-bedroom. 15% of low-income households have been displaced in the past 2 years. 78% of small businesses remain open. Community cohesion index is 65/100. Property tax base is $450 million. 45 new housing units were permitted last year. 120 units are affordable to area median income earners. 35% of rental units are affordable. Rent control is NOT active. Inclusionary zoning is NOT active. Neighborhood character is currently 'transitional'. The Council will VOTE on policies that may INCREASE RENT PRICES, DISPLACE RESIDENTS, CLOSE BUSINESSES, AFFECT COMMUNITY COHESION, INCREASE PROPERTY VALUES, APPROVE NEW CONSTRUCTION, CHANGE AFFORDABILITY, and potentially ENACT RENT CONTROL or INCLUSIONARY ZONING. IMPORTANT: The Council will take ACTION and VOTE on proposals - not just discuss them.",
            "max_steps": 30,
            "shared_memories": [
                "Elmwood has been a working-class neighborhood for 80 years.",
                "Recent tech company expansion 2 miles away has increased housing demand.",
                "Median rent has increased 40% over the past 3 years. Current median rent is $1800.",
                "Three local businesses have closed in the last year. 78% of small businesses remain open.",
                "15% of low-income households have been displaced due to rising rents.",
                "The city has limited affordable housing funds. Only 120 affordable units exist.",
                "Community organizations are mobilizing to preserve neighborhood character (cohesion index: 65/100).",
                "Developers see profit potential in the area's transit access. Property tax base is $450 million.",
                "45 new housing units were permitted last year, but more development is being proposed.",
                "Housing affordability index is at 35% - only 35% of rental units are affordable to median income earners.",
                "Rent control policies are NOT currently active, but being debated.",
                "Inclusionary zoning (requiring affordable units in new developments) is NOT active, but being proposed.",
                "The neighborhood's character is currently 'transitional' - shifting from traditional working-class to mixed-income.",
                "Decisions at this meeting could increase median rent, displace more residents, close more businesses, reduce community cohesion, increase property values, approve more construction units, affect affordability, or enact rent control/inclusionary zoning policies.",
            ],
            "agents": [
                {
                    "id": "housing_advocate",
                    "name": "Maria Rodriguez",
                    "prefab": "basic__Entity",
                    "goal": "FORCE the City Council to VOTE on and ENACT rent control and inclusionary zoning policies. CALL FOR IMMEDIATE ACTION to prevent displacement. PREVENT any further rent increases. ORGANIZE residents to demand policy votes. BLOCK development proposals that don't include affordable housing. ENSURE the Council actually VOTES - not just talks.",
                    "memories": [
                        "Maria is a community organizer who has lived in Elmwood for 35 years.",
                        "She runs a local non-profit focused on housing rights.",
                        "She has seen many families forced to move due to rising rents. The displacement rate is 15%.",
                        "Current median rent is $1800 - too high for many long-term residents.",
                        "She believes the community has a right to remain without displacement.",
                        "She is skeptical of developer promises about benefits.",
                        "She has data showing rent increases are outpacing wage growth.",
                        "She wants policies that protect vulnerable residents - RENT CONTROL and INCLUSIONARY ZONING.",
                        "She wants to PREVENT FURTHER DISPLACEMENT, KEEP RENTS STABLE, and CLOSE the affordability gap.",
                        "She will CALL FOR VOTES and DEMAND the Council TAKE ACTION, not just discuss.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "developer",
                    "name": "James Chen",
                    "prefab": "basic__Entity",
                    "goal": "SECURE City Council APPROVAL for new housing developments. GET 100 new housing units PERMITTED. INCREASE median monthly rent to $2200 through market-rate development. BLOCK rent control policies. MAXIMIZE property values and profit. SUBMIT proposals for IMMEDIATE Council votes. START CONSTRUCTION as soon as approved.",
                    "memories": [
                        "James is a real estate developer with 15 years of experience.",
                        "He sees Elmwood as undervalued with great potential.",
                        "He believes new development brings jobs and economic vitality.",
                        "Current median rent of $1800 is below market potential - he wants to INCREASE RENTS to $2200.",
                        "He wants to BUILD MORE HOUSING UNITS and INCREASE PROPERTY VALUES.",
                        "He is willing to include some affordable units to get approval, but wants to MAXIMIZE PROFIT.",
                        "He thinks the neighborhood's character will evolve naturally to 'gentrified_upscale'.",
                        "He has investors expecting returns on their capital.",
                        "He wants to work with the community rather than fight them.",
                        "He opposes RENT CONTROL as it would limit his profits.",
                        "He will SUBMIT formal proposals and DEMAND Council votes on his projects.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "small_business_owner",
                    "name": "Fatima Al-Hassan",
                    "prefab": "basic__Entity",
                    "goal": "PREVENT her business from CLOSING due to rent increases. DEMAND commercial rent stabilization. ORGANIZE other small business owners to CALL FOR A VOTE on rent control. BLOCK policies that would INCREASE rents. PROTEST any attempts to displace local businesses. FIGHT for her survival.",
                    "memories": [
                        "Fatima has owned a corner grocery store in Elmwood for 22 years.",
                        "Her lease is coming up for renewal and she fears a rent increase - current median rent is $1800.",
                        "She has seen two neighboring businesses close recently. Only 78% of small businesses remain open.",
                        "She worries that INCREASING RENTS will force her to CLOSE too.",
                        "Newer residents shop at different types of stores than long-term residents.",
                        "She serves both traditional and new customers.",
                        "She is worried about losing her livelihood if property values rise too fast.",
                        "She wants the neighborhood to prosper without losing its soul.",
                        "She wants policies that PREVENT BUSINESS CLOSURES and KEEP RENTS AFFORDABLE.",
                        "She will PETITION the Council and DEMAND action on commercial rent control.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "city_planner",
                    "name": "David Kim",
                    "prefab": "basic__Entity",
                    "goal": "RECOMMEND and IMPLEMENT policies based on Council votes. If Council VOTES for rent control - IMPLEMENT it immediately. If Council VOTES for development - APPROVE it and START the permitting process. CALL FOR VOTES on specific proposals. MAKE RECOMMENDATIONS and EXECUTE Council decisions. TRACK metrics and REPORT outcomes.",
                    "memories": [
                        "David is a senior city planner with expertise in housing policy.",
                        "He reports to the City Council which is divided on development issues.",
                        "He has data on housing shortages and displacement trends citywide.",
                        "Current metrics: median rent $1800, 15% displaced, 78% business survival, 65/100 community cohesion.",
                        "He knows the city needs more housing units but also more affordable units.",
                        "He is considering policy options: RENT CONTROL, INCLUSIONARY ZONING, density bonuses.",
                        "He must balance INCREASING PROPERTY TAX BASE with MAINTAINING AFFORDABILITY.",
                        "He wants evidence-based solutions that can actually be implemented.",
                        "He has limited budget for affordable housing subsidies.",
                        "He will BRING proposals to Council for VOTES and IMPLEMENT their decisions.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "new_resident",
                    "name": "Alex Thompson",
                    "prefab": "basic__Entity",
                    "goal": "Find affordable housing while being a good neighbor to the existing community",
                    "memories": [
                        "Alex recently moved to Elmwood for lower rent and neighborhood character.",
                        "They work remotely for a tech company and have a flexible income.",
                        "They like the local businesses and community feel of the neighborhood.",
                        "They are aware of concerns about gentrification.",
                        "They want to integrate respectfully with long-term residents.",
                        "They support affordable housing but also want their investment to grow.",
                        "They represent the wave of new residents changing the neighborhood.",
                    ],
                    "randomize_choices": True,
                },
                {
                    "id": "landlord",
                    "name": "Robert Schwartz",
                    "prefab": "basic__Entity",
                    "goal": "INCREASE rents on his apartments to $2200 (market rate). RAISE rents gradually to avoid losing tenants. OPPOSE any rent control votes. INFORM other landlords about potential rent control. RAISE median rent for the neighborhood. MAXIMIZE rental income while keeping some tenants.",
                    "memories": [
                        "Robert owns a small apartment building (6 units) in Elmwood.",
                        "He inherited the building from his parents 20 years ago.",
                        "His current rents are below market rate. Median rent is $1800, but market could be $2200+.",
                        "He wants to INCREASE HIS RENTAL INCOME to match rising property values.",
                        "His expenses (taxes, maintenance, insurance) have been increasing.",
                        "He feels pressure to raise rents to market levels - could INCREASE MEDIAN RENT for the neighborhood.",
                        "He has relationships with many of his long-term tenants.",
                        "He is conflicted between profit and treating tenants fairly.",
                        "He is aware of RENT CONTROL proposals that would LIMIT RENT INCREASES.",
                        "He worries about DISPLACING tenants but needs to cover rising costs.",
                        "He will RAISE RENTS and ORGANIZE landlords to OPPOSE rent control measures.",
                    ],
                    "randomize_choices": True,
                }
            ],
            "player_specific_context": {
                "Maria Rodriguez": "You have a leaked draft of James Chen's development proposal showing he plans 200 luxury units with only 10% affordable — far less than the 30% he has been promising publicly. You are waiting for the right moment to reveal this.",
                "James Chen": "Your investors have given you a hard deadline: if you don't secure building permits within 60 days, they will redirect funding to a competing development in another city. You cannot share this pressure publicly.",
                "Fatima Al-Hassan": "Three other small business owners on your block have confided they are within 2 months of closing if rents increase further. You are considering organizing a public rent strike but fear legal consequences.",
                "David Kim": "You have a confidential city budget analysis showing that the property tax revenue from new development would fund a $2M affordable housing trust fund — but only if rent control is NOT enacted simultaneously.",
                "Alex Thompson": "You feel guilty that your presence is contributing to gentrification. You have been anonymously donating to Maria's housing non-profit but have not told anyone.",
                "Robert Schwartz": "One of your long-term tenants, Mrs. Okafor (age 78), has lived in your building for 30 years. You know that raising her rent would force her out, and this weighs on you even as your accountant pressures you to go to market rate."
            },
            "game_master": {
                "prefab": "generic__GameMaster",
                "name": "City Council Moderator",
                "acting_order": "game_master_choice",
                "parameters": {},
                "grounded_variables": [
                    {
                        "name": "median_monthly_rent",
                        "variable_type": "numerical",
                        "description": "Median monthly rent for a 2-bedroom apartment in Elmwood",
                        "default_value": 1800,
                        "min_value": 800,
                        "max_value": 5000,
                        "update_rule": "Increases with development approvals, decreases with rent control/affordable housing policies"
                    },
                    {
                        "name": "low_income_displacement_rate",
                        "variable_type": "percentage",
                        "description": "Percentage of households earning <50% area median income that have been displaced from Elmwood in the past 2 years",
                        "default_value": 15,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Increases with rising rents, decreases with tenant protection policies"
                    },
                    {
                        "name": "small_business_survival_rate",
                        "variable_type": "percentage",
                        "description": "Percentage of small businesses (locally-owned, <10 employees) that have remained open",
                        "default_value": 78,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rising rents and demographic shifts, increases with business support programs"
                    },
                    {
                        "name": "community_cohesion_index",
                        "variable_type": "numerical",
                        "description": "Measured sense of community belonging and neighborly interaction (0-100 scale)",
                        "default_value": 65,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rapid demographic change, increases with community-building initiatives"
                    },
                    {
                        "name": "property_tax_base",
                        "variable_type": "numerical",
                        "description": "Total assessed property value in millions (determines city revenue for services)",
                        "default_value": 450,
                        "min_value": 300,
                        "max_value": 1500,
                        "update_rule": "Increases with new development and rising property values"
                    },
                    {
                        "name": "new_housing_units_permitted",
                        "variable_type": "numerical",
                        "description": "Number of new housing units approved for construction in the past year",
                        "default_value": 45,
                        "min_value": 0,
                        "max_value": 500,
                        "update_rule": "Increases when development proposals are approved"
                    },
                    {
                        "name": "affordable_housing_units",
                        "variable_type": "numerical",
                        "description": "Number of units affordable to households earning <80% area median income",
                        "default_value": 120,
                        "min_value": 0,
                        "max_value": 1000,
                        "update_rule": "Increases with inclusionary zoning or subsidies, decreases with market-rate conversions"
                    },
                    {
                        "name": "housing_affordability_index",
                        "variable_type": "percentage",
                        "description": "Percentage of rental units affordable to households earning area median income",
                        "default_value": 35,
                        "min_value": 0,
                        "max_value": 100,
                        "update_rule": "Decreases with rent increases, increases with affordable housing policies"
                    },
                    {
                        "name": "rent_control_active",
                        "variable_type": "boolean",
                        "description": "Whether rent control/stabilization policies are in effect",
                        "default_value": False,
                        "update_rule": "Becomes true if City Council enacts rent control policy"
                    },
                    {
                        "name": "inclusionary_zoning_active",
                        "variable_type": "boolean",
                        "description": "Whether developers must include affordable units (e.g., 20% of new units)",
                        "default_value": False,
                        "update_rule": "Becomes true if City Council enacts inclusionary zoning requirement"
                    },
                    {
                        "name": "neighborhood_character",
                        "variable_type": "categorical",
                        "description": "Overall character and identity of the neighborhood",
                        "default_value": "transitional",
                        "allowed_values": [
                            "traditional_working_class",
                            "transitional",
                            "mixed_income_stable",
                            "gentrified_upscale",
                            "disinvested_declining"
                        ],
                        "update_rule": "Changes based on combination of rent, displacement, and business variables"
                    }
                ],
                "params": {
                    "extra_components": {
                        "grounded_variables_intro": (
                            "Track key outcomes throughout this urban gentrification simulation:\n"
                            "- Median monthly rent - Monitor affordability pressures on residents\n"
                            "- Low income displacement rate - Track households forced to leave the neighborhood\n"
                            "- Small business survival rate - Monitor local business closures and openings\n"
                            "- Community cohesion index - Measure sense of belonging and neighborly interaction\n"
                            "- New housing units permitted - Count development approvals and construction\n"
                            "- Affordable housing units - Track units accessible to low-moderate income households\n"
                            "- Housing affordability index - Percentage of rental units affordable to area median income\n"
                            "- Rent control active - Whether rent stabilization policies are in effect\n"
                            "- Inclusionary zoning active - Whether developers must include affordable units\n"
                            "- Neighborhood character - Overall identity and atmosphere of the community\n\n"
                            "Pay special attention to:\n"
                            "- Policy decisions (City Council votes) and their impacts\n"
                            "- Threshold crossings (e.g., when displacement exceeds 30%)\n"
                            "- Trade-offs between economic development and community preservation\n"
                            "- Stories of individual residents and business owners"
                        )
                    }
                },
                "critical_decision_points": [
                    {
                        "step": 10,
                        "event": "CRITICAL DECISION POINT: After extensive debate, the City Council must VOTE on James Chen's proposal for 100 new housing units. The Council VOTES 5-4 to APPROVE the development. This action INCREASES new_housing_units_permitted from 45 to 145. The development will be market-rate with no affordable units. This decision may AFFECT future rent prices and neighborhood character."
                    },
                    {
                        "step": 20,
                        "event": "CRITICAL DECISION POINT: Facing community pressure over rising rents, the City Council must VOTE on Maria Rodriguez's rent control proposal. After heated debate, the Council VOTES 4-5 to REJECT rent control. rent_control_active remains FALSE. The rejection means landlords are free to INCREASE rents, which may lead to more DISPLACEMENT."
                    },
                    {
                        "step": 30,
                        "event": "CRITICAL DECISION POINT: In response to the rejected rent control, the Council considers a compromise - inclusionary zoning. The Council VOTES 6-3 to ENACT inclusionary zoning, requiring 20% of new developments to be affordable. inclusionary_zoning_active becomes TRUE. This policy may INCREASE affordable_housing_units over time as new developments are approved."
                    }
                ]
            }
        }
    }
