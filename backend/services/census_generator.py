"""
Census/distribution-based agent generation.

Samples agent profiles from demographic distributions (independent marginals
or joint profiles) and converts them to GeneratedPersona objects compatible
with the existing persona generation flow.
"""

import csv
import io
import json
import random
from typing import Any, Dict, List, Optional, Tuple

DIVERSE_NAMES = [
    "Aisha", "Brendan", "Carmen", "Dmitri", "Elena", "Farhan", "Gabrielle",
    "Hiroshi", "Isabella", "Jamal", "Keiko", "Liam", "Maria", "Nikolai",
    "Olga", "Paulo", "Qian", "Rashid", "Sofia", "Tariq", "Uma", "Viktor",
    "Wen", "Xander", "Yuki", "Zara", "Adaeze", "Bjorn", "Chiara", "Dayo",
    "Emeka", "Fiona", "Giovanni", "Hana", "Ibrahim", "Jing", "Kofi",
    "Lucia", "Mateo", "Nadia", "Oscar", "Priya", "Rafael", "Sana",
    "Tomoko", "Umar", "Valentina", "Wei", "Xiomara", "Youssef", "Zuri",
    "Amara", "Chen", "Davi", "Esme", "Fatima", "Gael", "Hyun", "Ines",
    "Jun", "Khadija", "Leo", "Mei", "Nico", "Olamide", "Petra",
    "Quinn", "Rosa", "Sven", "Thiago", "Ursula", "Vimal", "Wanda",
    "Yara", "Zhen", "Akiko", "Boris", "Celia", "Diego", "Elia",
    "Freya", "Gita", "Hassan", "Isla", "Javier", "Kaya", "Lars",
    "Mina", "Nora", "Omar", "Paloma", "Ravi", "Sakura", "Tomas",
    "Viola", "Yolanda", "Amina", "Dante", "Eshan", "Flora", "Hugo",
]


def _sample_from_marginals(
    dimensions: Dict[str, Dict[str, float]],
    num_agents: int,
    rng: random.Random,
) -> List[Dict[str, str]]:
    """Sample profiles by independently drawing from each dimension."""
    profiles = []
    for _ in range(num_agents):
        profile = {}
        for dim_name, distribution in dimensions.items():
            categories = list(distribution.keys())
            weights = list(distribution.values())
            profile[dim_name] = rng.choices(categories, weights=weights, k=1)[0]
        profiles.append(profile)
    return profiles


def _sample_from_joint(
    joint_profiles: List[Dict[str, Any]],
    num_agents: int,
    rng: random.Random,
) -> List[Dict[str, str]]:
    """Sample profiles from a joint distribution (weighted profile list)."""
    weights = [p.get('weight', 1.0) for p in joint_profiles]
    chosen = rng.choices(joint_profiles, weights=weights, k=num_agents)
    return [{k: v for k, v in p.items() if k != 'weight'} for p in chosen]


def _assign_names(
    profiles: List[Dict[str, str]],
    rng: random.Random,
) -> List[Dict[str, str]]:
    """Assign diverse names to profiles."""
    pool = list(DIVERSE_NAMES)
    rng.shuffle(pool)
    for i, profile in enumerate(profiles):
        if 'name' not in profile:
            profile['name'] = pool[i % len(pool)] if i < len(pool) else f"Agent_{i + 1}"
    return profiles


def _profile_to_memories(
    profile: Dict[str, str],
    context: str,
) -> List[str]:
    """Convert a demographic profile dict to factual memory strings."""
    name = profile.get('name', 'This person')
    memories = []

    for key, value in profile.items():
        if key == 'name':
            continue
        label = key.replace('_', ' ')
        memories.append(f"{name}'s {label} is {value}.")

    if context:
        memories.append(f"{name} lives in the following context: {context}")

    return memories


def _profile_to_goal(profile: Dict[str, str]) -> str:
    """Generate a simple goal from profile demographics."""
    name = profile.get('name', 'This agent')
    return f"{name} navigates daily life according to their needs and circumstances."


def sample_agents_from_distribution(
    dimensions: Optional[Dict[str, Dict[str, float]]] = None,
    joint_profiles: Optional[List[Dict[str, Any]]] = None,
    num_agents: int = 10,
    seed: Optional[int] = None,
    context: str = "",
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, int]]]:
    """Sample agent personas from a demographic distribution.

    Returns (personas, distribution_summary) where personas is a list of dicts
    with keys: name, goal, memories, description, demographics.
    """
    rng = random.Random(seed)

    if joint_profiles:
        profiles = _sample_from_joint(joint_profiles, num_agents, rng)
    elif dimensions:
        profiles = _sample_from_marginals(dimensions, num_agents, rng)
    else:
        raise ValueError("Either 'dimensions' or 'joint_profiles' must be provided")

    profiles = _assign_names(profiles, rng)

    personas = []
    for profile in profiles:
        name = profile.get('name', 'Unknown')
        memories = _profile_to_memories(profile, context)
        goal = _profile_to_goal(profile)

        demo_parts = [f"{k}: {v}" for k, v in profile.items() if k != 'name']
        description = f"{name} ({', '.join(demo_parts)})" if demo_parts else name

        personas.append({
            'name': name,
            'goal': goal,
            'memories': memories,
            'description': description,
            'demographics': {k: v for k, v in profile.items() if k != 'name'},
        })

    summary: Dict[str, Dict[str, int]] = {}
    dim_keys = set()
    for p in profiles:
        dim_keys.update(k for k in p if k != 'name')
    for dim in dim_keys:
        summary[dim] = {}
        for p in profiles:
            val = p.get(dim, 'unknown')
            summary[dim][val] = summary[dim].get(val, 0) + 1

    return personas, summary


async def enrich_with_llm(
    personas: List[Dict[str, Any]],
    context: str,
    model: Any,
    num_memories: int = 5,
) -> List[Dict[str, Any]]:
    """Use an LLM to enrich sampled demographics into natural-language memories."""
    enriched = []
    for persona in personas:
        name = persona['name']
        demographics = persona.get('demographics', {})
        demo_str = ', '.join(f'{k}: {v}' for k, v in demographics.items())

        prompt = (
            f"Generate {num_memories} short, specific biographical memories for a character named {name} "
            f"with these demographics: {demo_str}. "
            f"Context: {context}\n\n"
            f"Each memory should be one sentence describing a specific experience, habit, or fact "
            f"about {name} that is consistent with their demographic profile. "
            f"Return only the memories, one per line."
        )

        try:
            response = model.sample_text(prompt, max_tokens=1000, temperature=0.8)
            memories = [
                line.strip().lstrip('0123456789.-) ')
                for line in response.strip().split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            if memories:
                persona['memories'] = memories[:num_memories]

            goal_prompt = (
                f"In one sentence, what is the primary daily goal of {name} ({demo_str}) "
                f"in this context: {context}?"
            )
            goal_response = model.sample_text(goal_prompt, max_tokens=200, temperature=0.7)
            if goal_response.strip():
                persona['goal'] = goal_response.strip()
        except Exception as e:
            print(f"[CensusGenerator] LLM enrichment failed for {name}: {e}")

        enriched.append(persona)
    return enriched


def parse_csv_distribution(csv_content: str) -> Dict[str, Any]:
    """Parse a CSV file into a distribution spec.

    Supports two CSV formats:
    1. Marginals: columns are dimension names, first row is categories, second row is weights
       age,occupation,income
       18-25,farmer,low
       0.3,0.4,0.5
       26-40,teacher,medium
       0.4,0.2,0.3
       ...

    2. Joint profiles: columns are dimension names + 'weight', each row is a profile
       weight,age,occupation,income
       0.3,18-25,farmer,low
       0.2,26-40,teacher,medium
       ...
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = reader.fieldnames or []

    if 'weight' in fieldnames:
        profiles = []
        for row in reader:
            profile = {}
            for key, val in row.items():
                if key == 'weight':
                    profile['weight'] = float(val)
                else:
                    profile[key] = val.strip()
            profiles.append(profile)
        return {'joint_profiles': profiles}
    else:
        rows = list(reader)
        dimensions: Dict[str, Dict[str, float]] = {col: {} for col in fieldnames}
        for row in rows:
            for col in fieldnames:
                val = row[col].strip()
                try:
                    weight = float(val)
                    last_cat = list(dimensions[col].keys())[-1] if dimensions[col] else None
                    if last_cat and dimensions[col][last_cat] == 0.0:
                        dimensions[col][last_cat] = weight
                except ValueError:
                    dimensions[col][val] = 0.0

        needs_equal = any(
            all(w == 0.0 for w in dim.values())
            for dim in dimensions.values()
        )
        if needs_equal:
            for dim in dimensions.values():
                n = len(dim)
                if n > 0 and all(w == 0.0 for w in dim.values()):
                    for cat in dim:
                        dim[cat] = 1.0 / n

        return {'dimensions': dimensions}


def parse_json_distribution(json_content: str) -> Dict[str, Any]:
    """Parse a JSON file into a distribution spec.

    Supports:
    1. {"dimensions": {"age": {"18-25": 0.3, ...}, ...}}
    2. {"joint_profiles": [{"weight": 0.3, "age": "18-25", ...}, ...]}
    3. Direct marginals dict: {"age": {"18-25": 0.3, ...}, ...}
    4. Direct joint array: [{"weight": 0.3, "age": "18-25", ...}, ...]
    """
    data = json.loads(json_content)

    if isinstance(data, list):
        return {'joint_profiles': data}

    if isinstance(data, dict):
        if 'dimensions' in data or 'joint_profiles' in data:
            return data
        if all(isinstance(v, dict) for v in data.values()):
            return {'dimensions': data}

    raise ValueError(
        "Unrecognized distribution format. Expected dict of marginals "
        "or list of weighted profiles."
    )
