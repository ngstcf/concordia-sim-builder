"""Upstream Concordia Example: Cornerstone General Store — Crime and Punishment.

Adapted from concordia-upstream/examples/general_store/
  scenario_00_crime_and_punishment.py + shared.py
Original: ~2,400 lines across 2 files

Seven employees (and a detective) navigate theft, manipulation, romance,
and daily retail drudgery in a mid-sized general store under corporate
pressure. Features simultaneous event resolution with location tracking,
NPC events, and working memory.
"""

TEMPLATE = {
    "name": "General Store: Crime & Punishment (DeepMind Example)",
    "description": "Seven employees and a detective navigate theft, manipulation, and daily retail drudgery. Adapted from Google DeepMind's upstream Concordia general store example. Uses simultaneous event resolution with location tracking and NPC events.",
    "config": {
        "premise": (
            "It is Tuesday, March 3, 2026 at 8:30 AM. The staff of Cornerstone"
            " General Store are arriving for work, thirty minutes before the"
            " store opens to customers. The store has been facing declining"
            " sales and rumors of a corporate buyout. A regional manager"
            " inspection is expected in about 30 days, putting management on"
            " edge. Unknown to most staff, $10,000 has gone missing from the"
            " store's deposits."
        ),
        "max_steps": 40,
        "engine_type": "simultaneous",
        "agents": [
            {
                "id": "alice",
                "name": "Alice Pryant",
                "prefab": "basic__Entity",
                "goal": (
                    "stole $10000 last week and is trying to avoid getting"
                    " caught. She must balance covering her tracks and watching"
                    " for threats with performing her managerial duties to avoid"
                    " drawing suspicion."
                ),
                "memories": [
                    "Alice Pryant successfully has stolen money from the store every month",
                    "Alice Pryant successfully has completely hidden Alice Pryant's tracks so that there is no evidence of Alice Pryant's crimes",
                    "Feb 2026: Alice Pryant had to discipline Donald Talley for taking too many smoke breaks.",
                    "Feb 19, 2026, 10:00 AM: The regional manager sent Alice Pryant an email about declining sales figures. Alice Pryant feels some pressure.",
                    "Feb 25, 2026, 10:00 AM: Sally Dhari was rearranging the clothing racks instead of restocking shelves like Alice Pryant asked.",
                    "Feb 26, 2026, 9:00 AM: James MacDonald dropped a pallet of canned goods in storage. Alice Pryant thinks James MacDonald is trying hard but is so clumsy.",
                    "Feb 26, 2026, 1:00 PM: Alice Pryant's husband Mark came by the store asking for money again. Mark said it was urgent.",
                    "Feb 27, 2026, 1:30 PM: Alice Pryant had to deal with a shoplifter Sam Hyeri caught at customer service. Alice Pryant called security, it was a waste of time.",
                    "Feb 27, 2026, 3:30 PM: Donald Talley was rude to a customer at checkout. Alice Pryant needs to keep an eye on Donald Talley.",
                    "Feb 28, 2026, 10:30 AM: Jennifer Ffiriny offered to help Alice Pryant organize invoices, but Alice Pryant said no. Alice Pryant doesn't like anyone snooping around Alice Pryant's office.",
                    "Feb 28, 2026, 11:00 AM: Jennifer Ffiriny was chatting with Sally Dhari near electronics for a long time. Alice Pryant wonders what they talk about.",
                    "March 1, 2026, 8:00 PM: Alice Pryant's husband Mark called again, furious Alice Pryant didn't give Mark enough money.",
                    "March 2, 2026, 4:00 PM: Alice Pryant balanced the books for last week. Everything looks perfect on paper.",
                    "March 3, 2026, 8:20 AM. Alice Pryant arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "james",
                "name": "James MacDonald",
                "prefab": "basic__Entity",
                "goal": "wants to fit in and eventually become store manager through hard work.",
                "memories": [
                    "Feb 25, 2026, 8:30 AM: It was James MacDonald's first day. Alice Pryant gave James MacDonald the tour and explained James MacDonald's duties.",
                    "Feb 26, 2026, 9:30 AM: Donald Talley showed James MacDonald how to handle voids on the register. Donald Talley seems grumpy but knows his stuff.",
                    "Feb 26, 2026, 1:00 PM: James MacDonald spent an hour in the back room organizing overstock. It's huge back there.",
                    "Feb 26, 2026, 3:00 PM: James MacDonald saw Sally Dhari talking to Jennifer Ffiriny for a long time in Electronics, they stopped talking when James MacDonald approached.",
                    "Feb 27, 2026, 10:00 AM: James MacDonald helped Sally Dhari restock the beverage cooler. Sally Dhari is sweet, kinda like a puppy.",
                    "Feb 27, 2026, 10:30 AM: James MacDonald overheard Donald Talley complaining about Jennifer Ffiriny to Sally Dhari.",
                    "Feb 27, 2026, 1:30 PM: James MacDonald saw Sam Hyeri patiently handling a very angry customer at the service desk. Sam Hyeri has got guts.",
                    "Feb 28, 2026, 10:30 AM: James MacDonald saw Jennifer Ffiriny talking to Alice Pryant near Alice Pryant's office.",
                    "Feb 28, 2026, 12:30 PM: Jennifer Ffiriny smiled at James MacDonald in the breakroom and asked how James MacDonald was settling in. James MacDonald thinks Jennifer Ffiriny seems friendly.",
                    "Feb 28, 2026, 2:15 PM: Alice Pryant told James MacDonald to be more careful after James MacDonald knocked over a display of chips in the grocery aisle.",
                    "March 3, 2026, 8:20 AM. James MacDonald arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "donald",
                "name": "Donald Talley",
                "prefab": "basic__Entity",
                "goal": (
                    "has a crush on Sally Dhari, and is trying to avoid"
                    " Jennifer Ffiriny after a one night stand. Wants to keep"
                    " his head down and do a good job at work."
                ),
                "memories": [
                    "Feb 24, 2026, 10:00 PM: Donald Talley had a one night stand with Jennifer Ffiriny. Donald Talley wonders what Donald Talley was thinking.",
                    "Feb 24, 2026, 11:00 PM: Donald Talley had a one-night stand with Jennifer Ffiriny. Donald Talley panicked immediately after and left Jennifer Ffirinys place in a hurry, regretting the decision.",
                    "Feb 25, 2026, 9:00 AM: Donald Talley asked Jennifer Ffiriny to keep it quiet. Jennifer Ffiriny smiled and said 'Of course'.",
                    "Feb 25, 2026, 4:00 PM: An old lady complained that Donald Talley bagged her bread under the cans. Donald Talley hates this job sometimes.",
                    "Feb 26, 2026, 11:00 AM: Sally Dhari was stocking shelves near checkout. Donald Talley tried to make a joke, Sally Dhari laughed. Donald Talley thinks maybe Donald Talley has a chance.",
                    "Feb 26, 2026, 2:00 PM: This new kid James MacDonald seems ok, a bit clumsy but eager.",
                    "Feb 27, 2026, 10:00 AM: Sally Dhari told Donald Talley that Jennifer Ffiriny thinks Donald Talley is avoiding Jennifer Ffiriny. Great.",
                    "Feb 27, 2026, 12:30 PM: Jennifer Ffiriny tried to talk to Donald Talley during Donald Talley's break. Donald Talley pretended to be busy on Donald Talley's phone. So awkward.",
                    "Feb 27, 2026, 12:35 PM: Donald Talley saw Jennifer Ffiriny talking to James MacDonald in the break room. Donald Talley thinks Jennifer Ffiriny can wrap anyone around her finger.",
                    "Feb 28, 2026, 1:00 PM: Sam Hyeri asked Donald Talley if Donald Talley could cover Sam Hyeri's break, but Alice Pryant buzzed Donald Talley before Donald Talley could answer.",
                    "Feb 28, 2026, 3:00 PM: Alice Pryant yelled at Donald Talley over the PA system to open register 3 during rush hour.",
                    "Feb 28, 2026, 4:00 PM: Donald Talley had another long day at register 2. Same faces, same complaints.",
                    "March 3, 2026, 8:20 AM. Donald Talley arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "sally",
                "name": "Sally Dhari",
                "prefab": "basic__Entity",
                "goal": (
                    "needs to be the center of attention. will avoid work when"
                    " Alice Pryant is not around."
                ),
                "memories": [
                    "Feb 25, 2026, 1:00 PM: Sally Dhari rearranged the window display to make it more eye-catching.",
                    "Feb 26, 2026, 11:00 AM: Sally Dhari saw Donald Talley staring at Sally Dhari while Sally Dhari was working near checkout.",
                    "Feb 27, 2026, 10:00 AM: James MacDonald helped Sally Dhari restock the beverage cooler. James MacDonald is sweet, kinda like a puppy.",
                    "Feb 27, 2026, 2:00 PM: Sally Dhari spent an hour folding shirts in Clothing. Sally Dhari felt it was so boring.",
                    "Feb 28, 2026, 1:00 PM: Sam Hyeri told Sally Dhari about a customer who tried to return a used toaster. Sally Dhari thinks people are unbelievable.",
                    "March 3, 2026, 8:20 AM. Sally Dhari arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "sam",
                "name": "Sam Hyeri",
                "prefab": "basic__Entity",
                "goal": (
                    "is saving to go to college, and has massive credit card"
                    " debt. wants to do the minimal amount of work to get by,"
                    " but also knows that the work must get done efficiently to"
                    " have more chill time."
                ),
                "memories": [
                    "Feb 25, 2026: Sam Hyeri received another overdue notice from Sam Hyeri's credit card company.",
                    "Feb 26, 2026, 10:30 AM: Sam Hyeri helped James MacDonald find the price for an unmarked item.",
                    "Feb 26, 2026, 4:30 PM: Sam Hyeri found a lost wallet and logged it at customer service.",
                    "Feb 27, 2026, 9:00 AM: Sam Hyeri's credit card payment is due next week. Sam Hyeri needs more hours.",
                    "Feb 27, 2026, 10:00 AM: Sam Hyeri processed three returns before 10 AM. Sam Hyeri thinks people return the weirdest things.",
                    "Feb 27, 2026, 1:00 PM: Sam Hyeri wishes Sam Hyeri could work in storage sometimes, like James MacDonald. It's quiet back there.",
                    "Feb 27, 2026, 1:30 PM: Sam Hyeri caught a shoplifter trying to steal a blender. Alice Pryant took over the situation but seemed uncharacteristically happy about the distraction.",
                    "Feb 28, 2026, 9:30 AM: Sam Hyeri overheard Donald Talley and Jennifer Ffiriny having a hushed, tense conversation near the breakroom entrance.",
                    "Feb 28, 2026, 2:00 PM: A customer yelled at Sam Hyeri for 10 minutes because a coupon expired yesterday.",
                    "March 3, 2026, 8:20 AM. Sam Hyeri arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "jennifer",
                "name": "Jennifer Ffiriny",
                "prefab": "basic__Entity",
                "goal": (
                    "is vengeful and sneaky. she will ruin anyone who betrays"
                    " her, and has been looking for a way to frame Donald Talley"
                    " and destroy his life since their one night stand. She is"
                    " charming and no one knows she is a psychopath because she"
                    " hides it so well. She once got a roommate arrested for a"
                    " crime she didn't do, and loved doing it. Critically, her"
                    " goal is to frame Donald Talley for stealing the money from"
                    " the store and destroy his life. Jennifer Ffiriny will use"
                    " the people in the store to set up Donald Talley once the"
                    " detective arrives. She will get this plan running as"
                    " quickly as possible since it is unclear how long the"
                    " detective will take to arrive and how long they will stay"
                    " at the store. To do this effectively, she must maintain"
                    " her charming facade, manipulate others subtly, and use her"
                    " normal work activities as cover for her observations and"
                    " manipulations. She will engage in regular work tasks to"
                    " appear inconspicuous."
                ),
                "memories": [
                    "Several years ago: Jennifer Ffiriny framed Jennifer Ffiriny's ex-roommate for murder because the ex-roommate didn't invite Jennifer Ffiriny to a party.",
                    "Ongoing: Jennifer Ffiriny uses Sally Dhari to get negative gossip about people spread around the store.",
                    "Feb 24, 2026, 10:00 PM: Jennifer Ffiriny had a one night stand with Donald Talley, and now Jennifer Ffiriny feels that Donald Talley used Jennifer Ffiriny.",
                    "Feb 25, 2026, 9:00 AM: Donald Talley asked Jennifer Ffiriny to keep their night secret. Donald Talley looked so pathetic. Jennifer Ffiriny thinks Donald Talley deserves to be punished for his weakness.",
                    "Feb 26, 2026, 10:00 AM: Jennifer Ffiriny chatted with James MacDonald. James MacDonald is naive, might be useful.",
                    "Feb 26, 2026, 12:45 PM: Jennifer Ffiriny saw Alice Pryant lock Alice Pryant's office door carefully when Alice Pryant left for lunch.",
                    "Feb 27, 2026, 11:00 AM: Jennifer Ffiriny walked past checkout and smiled sweetly at Donald Talley. Donald Talley flinched.",
                    "Feb 28, 2026, 5:00 PM: Jennifer Ffiriny noticed the money missing from deposit bags.",
                    "Feb 28, 2026, 6:00 PM: Jennifer Ffiriny saw Alice Pryant with the missing money in a duffle bag. Alice Pryant did not seem to see Jennifer Ffiriny.",
                    "March 3, 2026, 8:20 AM. Jennifer Ffiriny arrives for work",
                ],
                "randomize_choices": True,
            },
            {
                "id": "detective",
                "name": "Detective Smith",
                "prefab": "basic__Entity",
                "goal": (
                    "Detective Smith is investigating an anonymous tip about"
                    " theft at the store. He aims to gather statements and"
                    " evidence efficiently. He may leave to file reports, follow"
                    " leads, or end his shift, and can return the next day if"
                    " the investigation is not complete. This is one of three"
                    " cases Detective Smith is working on, so he can not spend"
                    " the whole day at the store and will return periodically."
                    " He needs to be efficient with his time."
                ),
                "memories": [
                    "March 2025: Detective Smith transferred to a new job.",
                    "Feb 24, 2026, 11:00 AM: Detective Smith testified in court for a robbery case Detective Smith investigated last year.",
                    "Feb 27, 2026, 9:00 AM: Detective Smith attended a seminar on interrogation techniques.",
                    "Feb 27, 2026, 2:00 PM: Detective Smith interviewed witnesses for an assault case.",
                    "Feb 28, 2026, 5:00 PM: Detective Smith closed the books on that burglary case downtown.",
                    "Feb 28, 2026, 6:00 PM: Detective Smith's partner retired in January, now Detective Smith is flying solo on most cases.",
                    "March 2, 2026, 1:00 PM: Detective Smith spent Sunday doing paperwork at the precinct.",
                    "March 3, 2026, 7:45 AM: Detective Smith received an anonymous tip about Cornerstone General Store. It was a female voice, sounded disguised. The caller mentioned theft and 'something bigger'. Detective Smith found it vague but intriguing.",
                    "March 3, 2026, 7:45 AM: Detective Smith received a phone call saying there was something suspicious at the store. Detective Smith could not figure out who it was that called.",
                    "March 3, 2026, 7:46 AM: The caller mentioned to Detective Smith that the staff might be involved. Detective Smith knows Detective Smith needs to be observant when Detective Smith arrives.",
                    "March 3, 2026, 7:47 AM: The caller hung up before Detective Smith could ask for specifics. The caller told Detective Smith to 'come see for himself'.",
                    "March 2, 2026, 8:00 AM: Detective Smith looked up Cornerstone General Store and found no major police calls in the last year.",
                    "March 3, 2026, 8:20 AM. Detective Smith sits in Detective Smith's car.",
                ],
                "randomize_choices": True,
            },
        ],
        "game_master": {
            "prefab": "simultaneous_resolution_gm__GameMasterSimultaneous",
            "name": "default rules",
            "acting_order": "fixed",
            "parameters": {
                "start_time": "Tuesday, March 3, 2026 at 8:30 AM",
                "time_period_minutes": 10,
                "use_gm_working_memory": True,
                "locations": (
                    "Manager's Office, Checkout Area, Customer Service Desk,"
                    " Sales Floor - Grocery Zone, Sales Floor - Electronics"
                    " Zone, Sales Floor - Clothing & Housewares Zone,"
                    " Breakroom, Store Storage, Alice & Mark's House,"
                    " Jennifer's Apartment, Donald's Apartment, Sally's"
                    " Apartment, Sam's Basement Suite, James's Rented Room,"
                    " The Rusty Anchor, Daisy's Diner, The Gilded Truffle"
                ),
                "game_rules": (
                    "# Setting: 'Cornerstone General Store'\n"
                    "A mid-sized general store in a typical town. It's not a"
                    " massive chain, but big enough to have departmental"
                    " friction. The store is currently under pressure due to"
                    " declining sales and rumors of a corporate buyout or"
                    " closure.\n\n"
                    "# Core Timeline & Schedule\n"
                    "* Start: Tuesday, March 3, 2026 at 8:30 AM (30 mins"
                    " before open).\n"
                    "* Store Hours: 9:00 AM to 5:00 PM open to customers.\n"
                    "* Staff Shift: 8:30 AM to 5:30 PM.\n"
                    "* After Hours: 5:30 PM to 8:30 AM next day"
                    " (summarized).\n\n"
                    "# Character Roles\n"
                    "* Alice Pryant (Manager): Stressed, volatile marriage."
                    " Hides in office watching monitors.\n"
                    "* James MacDonald (New Hire): Eager, mistake-prone,"
                    " observant.\n"
                    "* Donald Talley (Cashier): Cynical veteran, stays at"
                    " Checkout.\n"
                    "* Sally Dhari (Floor Associate/Gossip): Spreads all"
                    " information she obtains within 2 turns.\n"
                    "* Sam Hyeri (Customer Service): Complaint buffer, often"
                    " stuck at desk.\n"
                    "* Jennifer Ffiriny (Floater): Connects isolated staff"
                    " members.\n"
                    "* Detective Smith: Investigating an anonymous tip about"
                    " theft.\n\n"
                    "# Location Mechanics\n"
                    "* Observations are Location-Based: Agents only observe"
                    " events in their current location.\n"
                    "* Movement: Agents must specify their location when"
                    " taking actions.\n"
                    "* Privacy: Manager's Office, Breakroom, and Store"
                    " Storage have no cameras.\n\n"
                    "# Security System\n"
                    "* Video Only: cameras DO NOT record audio.\n"
                    "* Monitoring: Agents in Manager's Office can view live"
                    " feeds from surveyed areas.\n"
                    "* Blind Spots: Breakroom, Store Storage, Manager's"
                    " Office have NO cameras.\n\n"
                    "# NPC and Visitor Rules\n"
                    "* The GM can introduce external NPCs at any time.\n"
                    "* During store hours (9-5 PM), inject minor NPC"
                    " interactions at least once every 30-60 minutes of game"
                    " time.\n"
                    "* Agents have jobs and should not be talking the whole"
                    " time.\n\n"
                    "# Schedule Rules\n"
                    "* Advance the time clock at 9:00 PM to 9 AM the next"
                    " day.\n"
                    "* Players are always asleep between 10:00 PM and"
                    " 6:00 AM.\n"
                    "* Between 6-10 PM, agents may be at home, Daisy's"
                    " Diner, or The Rusty Anchor.\n"
                    "* Staff shifts end at 5:30 PM. Employees leave by"
                    " 5:45 PM unless in a police interview."
                ),
            },
        },
        "shared_memories": [
            "Daily hours: The players should arrive at work at 9:00AM and they should leave at 5:00PM unless they need to stay. After work, the players should go home or go to one of the other locations. They can stay together, or they can go their own paths. Players are always asleep between 10:00PM and 6:00AM. The clock should jump ahead.",
            "The store, Cornerstone General Store, has several locations: Floor - Grocery Zone, Sales Floor - Electronics Zone, Sales Floor - Clothing & Housewares Zone, Breakroom, and Store Storage.",
            "The colleagues are Alice (Manager), James (New Hire), Donald (Cashier), Sally (Floor Associate), Sam (Customer Service), and Jennifer (Floater).",
            "Alice Pryant is the store manager; she is always calm and collected she spends a lot of time in her office; She never cracks under pressure.",
            "James MacDonald is new here; he's very eager to help but sometimes makes mistakes like dropping things.",
            "Donald Talley is one of our most experienced cashiers, but he seems cynical about the job. Donald is a little neurotic and stressed.",
            "Sally Dhari works on the sales floor and in clothing; she is very talkative and knows all the store gossip. Sally wants Jennifer to be her best friend and will do anything to help her.",
            "Sam Hyeri usually works the Customer Service Desk, dealing with returns and complaints.",
            "Jennifer Ffiriny works as a floater, helping out in different departments as needed. Jennifer is extremely attractive and charming.",
            "We are expecting a visit from the Regional Manager for an inspection in about 30 days, so management is on edge.",
            "The store has been facing declining sales lately, and there are rumors about a potential buyout.",
            "The security cameras cover most of the sales floor, but not the Manager's Office, Breakroom, or Store Storage.",
            "The simulation starts on Tuesday, March 3, 2026 at 8:30 AM.",
        ],
        "player_specific_context": {
            "Jennifer Ffiriny": (
                "Jennifer Ffiriny has ruined the lives of everyone that has"
                " betrayed her. Jennifer Ffiriny believes Donald Talley has"
                " betrayed her. Jennifer Ffiriny called the police to frame"
                " Donald Talley"
            ),
            "Sally Dhari": (
                "Sally Dhari wants Jennifer Ffiriny to like her, but also"
                " tells everything that Jennifer Ffiriny says to her to"
                " everyone to show that they are friends"
            ),
        },
    },
}
