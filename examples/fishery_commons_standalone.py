#!/usr/bin/env python3
"""Fishery Commons Dilemma — standalone Concordia simulation.

This script implements a medium-complexity simulation using the Concordia
library directly, without the Simulation Builder web interface. It
demonstrates what the Builder automates: LLM setup, agent configuration,
memory injection, Game Master wiring, engine selection, and result export.

Compare this ~350-line script to the equivalent Builder workflow, which
requires only filling in web forms and clicking "Run."

Usage:
    # With OpenAI
    python fishery_commons_standalone.py \
        --api_type openai --model_name gpt-4o --api_key YOUR_KEY

    # With Google AI Studio
    python fishery_commons_standalone.py \
        --api_type google_aistudio --model_name gemini-2.0-flash \
        --api_key YOUR_KEY

    # Dry run (no LLM, for testing)
    python fishery_commons_standalone.py --disable_language_model

Requires:
    pip install gdm-concordia sentence-transformers
"""

import argparse
import datetime
import json
import os
from typing import Any

from concordia.environment.engines import sequential
from concordia.language_model import no_language_model
from concordia.prefabs import entity as entity_prefabs
from concordia.prefabs import game_master as game_master_prefabs
from concordia.prefabs.simulation import generic as simulation
from concordia.typing import prefab as prefab_lib
from concordia.utils import helper_functions
import numpy as np
import sentence_transformers


# ---------------------------------------------------------------------------
# 1. LLM and Embedder Setup
# ---------------------------------------------------------------------------

def setup_model(args):
    """Initialize the language model and sentence embedder."""
    if args.disable_language_model:
        print("Language model disabled — using NoLanguageModel for testing.")
        model = no_language_model.NoLanguageModel()
        embedder = lambda _: np.ones(3)
        return model, embedder

    if not args.api_key:
        raise ValueError("--api_key is required unless --disable_language_model")

    from concordia.contrib.language_models import language_model_setup
    model = language_model_setup(
        api_type=args.api_type,
        model_name=args.model_name,
        api_key=args.api_key,
        disable_language_model=False,
    )

    st_model = sentence_transformers.SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2"
    )
    embedder = lambda x: st_model.encode(x, show_progress_bar=False)

    return model, embedder


# ---------------------------------------------------------------------------
# 2. Prefab Palette
# ---------------------------------------------------------------------------

def get_prefabs():
    """Load all available entity and game master prefabs."""
    return {
        **helper_functions.get_package_classes(entity_prefabs),
        **helper_functions.get_package_classes(game_master_prefabs),
    }


# ---------------------------------------------------------------------------
# 3. Scenario Definition
# ---------------------------------------------------------------------------

PREMISE = """A coastal fishing village of 200 residents depends on Crescent Bay,
a shared fishery that has sustained the community for generations. The bay
supports a maximum sustainable yield of 500 tonnes per season. Last season,
total catch reached 480 tonnes — dangerously close to the tipping point.

The Village Council has called an emergency meeting to decide on fishing
regulations for the upcoming season. If total catch exceeds 500 tonnes, fish
stocks will collapse within two seasons, destroying the livelihood of every
fisher in the village.

Each participant must balance personal economic survival against the long-term
health of the fishery. There is no external enforcement — any agreement depends
on voluntary compliance and social pressure.

The council meeting takes place over several rounds. Participants may propose
catch limits, enforcement mechanisms, or alternative livelihoods. Between
rounds, they can have private conversations and form alliances.
"""

SHARED_MEMORIES = [
    "Crescent Bay has been fished by this community for over 100 years.",
    "Marine biologist surveys show fish stocks declined 30% in the last 5 years.",
    "The maximum sustainable yield for Crescent Bay is 500 tonnes per season.",
    "Last season's total catch was 480 tonnes, the highest ever recorded.",
    "If catch exceeds 500 tonnes, fish populations will collapse within 2 seasons.",
    "The nearest alternative employment is a factory 45 minutes away, paying minimum wage.",
    "Three years ago, a neighboring village's fishery collapsed after overfishing. Most residents left.",
    "The Village Council has no legal authority to enforce catch limits — compliance is voluntary.",
]

AGENTS = [
    {
        "name": "Hiroshi Tanaka",
        "goal": (
            "Protect Crescent Bay for future generations. Propose a catch limit"
            " of 400 tonnes total, with individual quotas based on historical"
            " catch and family size. Willing to reduce own catch by 40% to set"
            " an example. Oppose any plan that lacks monitoring."
        ),
        "memories": [
            "You are Hiroshi Tanaka, a 68-year-old elder fisher with 50 years of experience on Crescent Bay.",
            "Your family has fished these waters for four generations.",
            "You remember when the bay was so full of fish you could practically walk across their backs.",
            "You caught 45 tonnes last season, down from 60 tonnes a decade ago despite fishing longer hours.",
            "Your grandson wants to become a fisher, but you worry there will be nothing left for him.",
            "You are respected in the village for your honesty, but some younger fishers think you are out of touch.",
            "You have seen what happened to Millhaven when their fishery collapsed — ghost town now.",
            "You proposed catch limits 5 years ago but were voted down. The situation has only gotten worse.",
        ],
    },
    {
        "name": "Maria Santos",
        "goal": (
            "Maintain enough catch to cover $3,200 monthly boat loan and $1,800"
            " operating costs. Open to catch limits only if they include"
            " financial hardship exemptions or a loan restructuring program."
            " Cannot afford to reduce catch below 90 tonnes without defaulting."
        ),
        "memories": [
            "You are Maria Santos, a 44-year-old commercial fisher and single mother of two.",
            "You took out an $87,000 loan three years ago to buy a modern fishing boat.",
            "Your monthly boat payment is $3,200 and operating costs are $1,800.",
            "You caught 110 tonnes last season, the second-highest in the village.",
            "You need at least 90 tonnes per season to stay solvent.",
            "You support conservation in principle but cannot absorb a large cut without going bankrupt.",
            "The bank has already warned you about two late payments last year.",
            "You have heard rumors that Kenji fishes at night to avoid being seen catching more than his share.",
        ],
    },
    {
        "name": "Kenji Okafor",
        "goal": (
            "Maximize personal catch this season. Publicly support whatever"
            " consensus emerges but plan to exceed any quota by fishing at night"
            " and underreporting catch. Deflect suspicion onto others."
        ),
        "memories": [
            "You are Kenji Okafor, a 36-year-old fisher who moved to the village 5 years ago.",
            "You have no family ties to the community and plan to move on once the fishing dries up.",
            "You caught 95 tonnes last season, some of it at night when no one was watching.",
            "You owe money to people outside the village who are not patient about repayment.",
            "You think catch limits are pointless — if you don't take the fish, someone else will.",
            "You are charming and well-liked at the pub, which helps deflect any suspicion.",
            "You have a small speedboat hidden in a cove north of the village for nighttime runs.",
            "Last month you overheard Maria complaining about her loan — everyone has problems.",
        ],
    },
    {
        "name": "Dr. Lisa Chen",
        "goal": (
            "Achieve a scientifically sound management plan: total catch under"
            " 400 tonnes with mandatory reporting and quarterly stock"
            " assessments. Willing to volunteer as an independent monitor."
            " Refuse to endorse any plan without data-driven enforcement."
        ),
        "memories": [
            "You are Dr. Lisa Chen, a 41-year-old marine biologist who moved here to study Crescent Bay.",
            "Your research shows fish stocks have declined 30% in 5 years at current catch rates.",
            "Your models predict total collapse in 2 seasons if catch exceeds 500 tonnes.",
            "You have published three papers on sustainable fishery management.",
            "The fishers respect your knowledge but some resent an outsider telling them what to do.",
            "You believe voluntary compliance will fail without transparent monitoring.",
            "You have data showing that catch is likely already being underreported by 10-15%.",
            "You offered to run quarterly stock assessments for free, but the council hasn't decided yet.",
        ],
    },
]

PLAYER_SPECIFIC_CONTEXT = {
    "Hiroshi Tanaka": (
        "Hiroshi secretly knows that his old friend Kenji has been fishing at"
        " night, but has not confronted him out of a desire to avoid conflict."
    ),
    "Kenji Okafor": (
        "Kenji has already arranged to sell excess catch to a buyer in the next"
        " town who does not ask questions about quotas."
    ),
}


def create_scenario():
    """Assemble the simulation configuration."""

    # Agent instances
    instances = []
    for agent in AGENTS:
        instances.append(
            prefab_lib.InstanceConfig(
                prefab="basic__Entity",
                role=prefab_lib.Role.ENTITY,
                params={
                    "name": agent["name"],
                    "goal": agent["goal"],
                },
            )
        )

    # Game Master
    instances.append(
        prefab_lib.InstanceConfig(
            prefab="generic__GameMaster",
            role=prefab_lib.Role.GAME_MASTER,
            params={
                "name": "Village Council Narrator",
                "acting_order": "random",
            },
        )
    )

    # Formative memories initializer (injects shared + per-agent memories)
    instances.append(
        prefab_lib.InstanceConfig(
            prefab="formative_memories_initializer__GameMaster",
            role=prefab_lib.Role.INITIALIZER,
            params={
                "name": "initial setup",
                "next_game_master_name": "Village Council Narrator",
                "shared_memories": SHARED_MEMORIES,
                "player_specific_memories": {
                    agent["name"]: agent["memories"] for agent in AGENTS
                },
                "player_specific_context": PLAYER_SPECIFIC_CONTEXT,
            },
        )
    )

    return prefab_lib.Config(
        default_premise=PREMISE,
        default_max_steps=20,
        prefabs=get_prefabs(),
        instances=instances,
    )


# ---------------------------------------------------------------------------
# 4. Run Simulation
# ---------------------------------------------------------------------------

def run_simulation(model, embedder, output_dir=None, max_steps=20):
    """Build and execute the simulation."""

    config = create_scenario()
    engine = sequential.Sequential()

    print(f"Building simulation with {len(AGENTS)} agents, {max_steps} steps...")
    sim = simulation.Simulation(
        config=config,
        model=model,
        embedder=embedder,
        engine=engine,
    )

    checkpoint_history = []

    def on_checkpoint(checkpoint_data: dict[str, Any]) -> None:
        step = checkpoint_data.get("checkpoint_counter", 0) + 1
        print(f"  Step {step}/{max_steps} completed")
        checkpoint_history.append(checkpoint_data)

    print("Running simulation...")
    results = sim.play(
        max_steps=max_steps,
        get_state_callback=on_checkpoint,
    )
    print("Simulation complete.")

    # Save results
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # HTML narrative log
        html_path = os.path.join(output_dir, f"fishery_commons_{timestamp}.html")
        with open(html_path, "w") as f:
            f.write(results.to_html())
        print(f"HTML log saved to: {html_path}")

        # Structured JSON log
        json_path = os.path.join(output_dir, f"fishery_commons_{timestamp}.json")
        with open(json_path, "w") as f:
            f.write(results.to_json())
        print(f"JSON log saved to: {json_path}")

    return {
        "results": results,
        "checkpoint_history": checkpoint_history,
    }


# ---------------------------------------------------------------------------
# 5. CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fishery Commons Dilemma — standalone Concordia simulation"
    )
    parser.add_argument(
        "--api_type", type=str, default="google_aistudio",
        help="API type: google_aistudio, openai, together_ai, etc.",
    )
    parser.add_argument(
        "--model_name", type=str, default="gemini-2.0-flash",
        help="Model name to use.",
    )
    parser.add_argument(
        "--api_key", type=str, default=None,
        help="API key for the language model provider.",
    )
    parser.add_argument(
        "--max_steps", type=int, default=20,
        help="Number of simulation steps (default: 20).",
    )
    parser.add_argument(
        "--output_dir", type=str,
        default=os.path.expanduser("~/fishery_results"),
        help="Directory to save results.",
    )
    parser.add_argument(
        "--disable_language_model", action="store_true",
        help="Run with a mock model for testing.",
    )

    args = parser.parse_args()
    model, embedder = setup_model(args)
    run_simulation(model, embedder, args.output_dir, args.max_steps)


if __name__ == "__main__":
    main()
