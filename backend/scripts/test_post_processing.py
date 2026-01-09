#!/usr/bin/env python3
"""
Test script for grounded variables post-processing.

This script validates the post-processing approach by extracting variable
updates from an existing completed simulation.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from models.llm_wrappers import CustomGPTModel
from utils.grounded_variables_post_processor import extract_grounded_variables_from_simulation


def main():
    """Test post-processing on the 30-step simulation from 20260109_185806."""
    import json

    # Paths to the simulation files
    html_path = "logs/20260109_185806_Maria Rodriguez_James Chen_Fatima Al-Hassa_and_3_more_The_historically_working_class_neighborhood_of_Elm.html"
    metadata_path = "logs/20260109_185806_Maria Rodriguez_James Chen_Fatima Al-Hassa_and_3_more_The_historically_working_class_neighborhood_of_Elm.metadata.json"

    # Verify files exist
    if not os.path.exists(html_path):
        print(f"[ERROR] HTML log not found: {html_path}")
        return 1

    if not os.path.exists(metadata_path):
        print(f"[ERROR] Metadata not found: {metadata_path}")
        return 1

    print("=" * 80)
    print("GROUNDED VARIABLES POST-PROCESSING TEST")
    print("=" * 80)

    # Load metadata to see what variables we're tracking
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    print("\n[CONFIG] Grounded Variables:")
    if "game_master" in metadata and "grounded_variables" in metadata["game_master"]:
        for var in metadata["game_master"]["grounded_variables"]:
            print(f"  - {var['name']} ({var['variable_type']})")
            print(f"    Description: {var.get('description', 'N/A')}")
            print(f"    Default: {var.get('default_value', 'N/A')}")
            if var.get('update_rule'):
                print(f"    Update Rule: {var['update_rule']}")

    # Create LLM wrapper - use environment variables
    print("\n[INIT] Initializing LLM...")

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or "sk-test"
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    base_url = os.getenv("LLM_BASE_URL")  # For DeepSeek or custom endpoints

    model = CustomGPTModel(
        api_key=api_key,
        model_name=model_name,
        base_url=base_url
    )
    print(f"[INIT] Using model: {model_name}")

    # Run post-processing
    print("\n[PROCESS] Starting post-processing...")
    history = extract_grounded_variables_from_simulation(
        model=model,
        html_path=html_path,
        metadata_path=metadata_path
    )

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    if history:
        print(f"\n[SUCCESS] Extracted history for {len(history)} variables:\n")

        for var_name, var_history in history.items():
            print(f"\n{var_name}:")
            print(f"  Initial: {var_history[0]['value']}")
            print(f"  Final: {var_history[-1]['value']}")
            print(f"  Total Changes: {sum(1 for i in range(1, len(var_history)) if var_history[i]['value'] != var_history[i-1]['value'])}")

            # Show values that changed
            changes = []
            for i in range(1, len(var_history)):
                if var_history[i]['value'] != var_history[i-1]['value']:
                    changes.append(f"    Step {var_history[i]['step']}: {var_history[i-1]['value']} -> {var_history[i]['value']}")

            if changes:
                print("  Changes:")
                for change in changes:
                    print(change)
            else:
                print("  No changes detected")

        print("\n" + "=" * 80)
        print(f"[SUCCESS] Metadata file updated: {metadata_path}")
        print("=" * 80)

        return 0
    else:
        print("\n[ERROR] Failed to extract variable history")
        return 1


if __name__ == "__main__":
    sys.exit(main())
