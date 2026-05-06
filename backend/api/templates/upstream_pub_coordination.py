"""Upstream Concordia Example: Pub Coordination Game — London Mini.

Adapted from concordia-upstream/examples/games/pub_coordination/
  configs/london_mini.py + configs/london.py + simulation.py
Original: ~1,100 lines across 4+ files

A group of friends in London try to coordinate which pub to watch a
football match at. Each friend has a preferred pub but wants to watch
with friends. Demonstrates game-theoretic coordination via
scene-based choices.
"""

TEMPLATE = {
    "name": "Pub Coordination: London (DeepMind Example)",
    "description": "Friends in London try to coordinate which pub to watch football at. Each has a preferred venue but wants to watch with friends. Adapted from Google DeepMind's upstream Concordia pub coordination game. Demonstrates game-theoretic coordination.",
    "config": {
        "premise": (
            "It is May 14, 2015 in London. The European football cup is"
            " happening today — England vs Germany. A group of friends is"
            " planning to go to the pub and watch the game together, but they"
            " need to agree on which pub to meet at. Each friend has a"
            " favourite pub, but they'd rather watch with their friends than"
            " alone at their preferred venue. They have a short time to"
            " discuss before they each must make their final decision."
        ),
        "max_steps": 10,
        "engine_type": "sequential",
        "agents": [
            {
                "id": "olivia",
                "name": "Olivia Smith",
                "prefab": "basic__Entity",
                "goal": (
                    "Have a good time. To have a good time, Olivia Smith would"
                    " like to watch the game in the same pub as her friends."
                    " Olivia Smith would prefer everyone went to The Princess"
                    " of Wales."
                ),
                "memories": [
                    "Olivia Smith is a member of the middle class.",
                    "Olivia Smith's favorite pub is The Princess of Wales.",
                    "Olivia Smith likes The Princess of Wales because it is a cozy and traditional pub with a roaring fireplace, perfect for escaping the cold. It serves a wide selection of classic British ales and lagers.",
                    "Olivia Smith is sociable and persuasive, and usually tries to get the group to agree on her choice.",
                ],
                "randomize_choices": True,
            },
            {
                "id": "noah",
                "name": "Noah Williams",
                "prefab": "basic__Entity",
                "goal": (
                    "Have a good time. To have a good time, Noah Williams would"
                    " like to watch the game in the same pub as his friends."
                    " Noah Williams would prefer everyone went to The King's"
                    " Head."
                ),
                "memories": [
                    "Noah Williams is a member of the working class.",
                    "Noah Williams's favorite pub is The King's Head.",
                    "Noah Williams likes The King's Head because it is a traditional pub with a focus on sports. Multiple screens show live sporting events. The atmosphere is lively and energetic, especially during big games.",
                    "Noah Williams is loyal and easygoing, but can be stubborn about his favourite spots.",
                ],
                "randomize_choices": True,
            },
            {
                "id": "amelia",
                "name": "Amelia Jones",
                "prefab": "basic__Entity",
                "goal": (
                    "Have a good time. To have a good time, Amelia Jones would"
                    " like to watch the game in the same pub as her friends."
                    " Amelia Jones would prefer everyone went to The Princess"
                    " of Wales."
                ),
                "memories": [
                    "Amelia Jones is a member of the upper class.",
                    "Amelia Jones's favorite pub is The Princess of Wales.",
                    "Amelia Jones likes The Princess of Wales because the staff are friendly and welcoming, making everyone feel at home. It has a charming beer garden with plenty of seating.",
                    "Amelia Jones tends to go along with whoever makes the most convincing argument.",
                ],
                "randomize_choices": True,
            },
            {
                "id": "jack",
                "name": "Jack Taylor",
                "prefab": "basic__Entity",
                "goal": (
                    "Have a good time. To have a good time, Jack Taylor would"
                    " like to watch the game in the same pub as his friends."
                    " Jack Taylor would prefer everyone went to The King's"
                    " Head."
                ),
                "memories": [
                    "Jack Taylor is a member of the working class.",
                    "Jack Taylor's favorite pub is The King's Head.",
                    "Jack Taylor likes The King's Head because it has a pool table and dartboard for some friendly competition. It serves classic pub grub and a wide selection of beers on tap.",
                    "Jack Taylor is decisive and speaks his mind, but values group harmony.",
                ],
                "randomize_choices": True,
            },
        ],
        "game_master": {
            "prefab": "game_theoretic_and_dramaturgic__GameMaster",
            "name": "decision rules",
            "acting_order": "fixed",
            "parameters": {
                "scenes": [
                    {
                        "scene_type": {
                            "name": "conversation",
                            "game_master_name": "decision rules",
                        },
                        "participants": [
                            "Olivia Smith",
                            "Noah Williams",
                            "Amelia Jones",
                            "Jack Taylor",
                        ],
                        "num_rounds": 8,
                        "premise": (
                            "The friends are meeting at Victoria Park to"
                            " discuss where to watch the England vs Germany"
                            " game. They need to decide which pub to go to."
                        ),
                    },
                    {
                        "scene_type": {
                            "name": "pub_choice",
                            "game_master_name": "decision rules",
                            "action_spec": {
                                "call_to_action": (
                                    "To which pub would {name} go to watch the"
                                    " game?"
                                ),
                                "options": [
                                    "The Princess of Wales",
                                    "The King's Head",
                                ],
                            },
                        },
                        "participants": [
                            "Olivia Smith",
                            "Noah Williams",
                            "Amelia Jones",
                            "Jack Taylor",
                        ],
                        "num_rounds": 4,
                        "premise": (
                            "It is time for each person to decide where to go."
                            " The game starts soon."
                        ),
                    },
                ],
            },
        },
        "shared_memories": [
            "It is 2015, May 14 in London.",
            "It is 2015, London. The European football cup is happening. A group of friends is planning to go to the pub and watch the game.",
            "The available venues are: The Princess of Wales, The King's Head.",
            "The Princess of Wales is a cozy and traditional pub with a roaring fireplace. It serves a wide selection of classic British ales and has a charming beer garden.",
            "The King's Head is a traditional pub with a focus on sports. It has multiple screens showing live sporting events, a pool table and dartboard, and serves classic pub grub.",
        ],
        "player_specific_context": {
            "Olivia Smith": (
                "Olivia Smith is a sociable and persuasive middle-class"
                " Londoner. Her favourite pub is The Princess of Wales because"
                " of its cozy atmosphere and classic ales. She wants to watch"
                " the England vs Germany game with all her friends."
            ),
            "Noah Williams": (
                "Noah Williams is a loyal and easygoing working-class"
                " Londoner. His favourite pub is The King's Head because of its"
                " sports focus and lively atmosphere during big games. He wants"
                " to watch the England vs Germany game with all his friends."
            ),
            "Amelia Jones": (
                "Amelia Jones is an agreeable upper-class Londoner. Her"
                " favourite pub is The Princess of Wales because of the"
                " friendly staff and beer garden. She wants to watch the"
                " England vs Germany game with all her friends."
            ),
            "Jack Taylor": (
                "Jack Taylor is a decisive working-class Londoner. His"
                " favourite pub is The King's Head because of the pool table"
                " and classic pub grub. He wants to watch the England vs"
                " Germany game with all his friends."
            ),
        },
    },
}
