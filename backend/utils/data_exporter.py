"""
Structured data exporter for simulation results.

Exports simulation data as CSV or JSON for quantitative analysis.
Parses Concordia v2.4 HTML logs (ENTRIES/CONTENT_STORE format)
and metadata JSON files.
"""

import csv
import io
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _extract_entries(html: str) -> List[Dict]:
    match = re.search(r'const ENTRIES = (\[.*?\]);\s*\n', html, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return []


def _extract_content_store(html: str) -> Dict[str, str]:
    match = re.search(r'const CONTENT_STORE = (\{.*?\});\s*\n', html, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return {}


def _resolve_ref(obj: Any, store: Dict[str, str], depth: int = 0) -> Any:
    if depth > 5:
        return obj
    if isinstance(obj, dict):
        if '_ref' in obj:
            return _resolve_ref(store.get(obj['_ref'], obj), store, depth + 1)
        return {k: _resolve_ref(v, store, depth + 1) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_ref(item, store, depth + 1) for item in obj]
    return obj


def _parse_agent_actions_from_html(html_content: str) -> List[Dict[str, Any]]:
    """Parse per-step per-agent actions and observations from HTML log."""
    entries = _extract_entries(html_content)
    content_store = _extract_content_store(html_content)

    rows = []
    for entry in entries:
        if entry.get('entry_type') != 'entity':
            continue
        entity = entry.get('entity_name', '')
        step = entry.get('step', 0)
        if not entity:
            continue

        dedup = entry.get('deduplicated_data', {})
        resolved = _resolve_ref(dedup, content_store)
        value_data = resolved.get('value', {})
        if not isinstance(value_data, dict):
            continue

        action_text = ''
        observation_text = ''

        if '__act__' in value_data:
            act_data = value_data['__act__']
            action_text = act_data.get('Value', '') if isinstance(act_data, dict) else str(act_data)

        if '__observation__' in value_data:
            obs_data = value_data['__observation__']
            obs_values = obs_data.get('Value', []) if isinstance(obs_data, dict) else []
            if obs_values and isinstance(obs_values, list):
                last_obs = obs_values[-1]
                observation_text = re.sub(
                    r'^\[observation\]\s*(\[\w+\]\s*)?', '', str(last_obs)
                ).strip()

        if not action_text and entry.get('component_name') == 'entity_action':
            action_text = entry.get('summary', '')

        if action_text or observation_text:
            rows.append({
                'step': step,
                'agent_name': entity,
                'action': action_text,
                'observation': observation_text,
            })

    rows.sort(key=lambda r: (r['step'], r['agent_name']))
    return rows


def _parse_gm_narrations_from_html(html_content: str) -> List[Dict[str, Any]]:
    """Parse per-step game master narrations from HTML log."""
    entries = _extract_entries(html_content)
    content_store = _extract_content_store(html_content)

    rows = []
    for entry in entries:
        if entry.get('entry_type') not in ('game_master', 'scene'):
            continue
        step = entry.get('step', 0)
        summary = entry.get('summary', '')

        if not summary:
            dedup = entry.get('deduplicated_data', {})
            resolved = _resolve_ref(dedup, content_store)
            value_data = resolved.get('value', {})
            if isinstance(value_data, dict):
                for key in ('__resolution__', 'display_events', '__make_observation__'):
                    if key in value_data:
                        val = value_data[key]
                        summary = val.get('Value', '') if isinstance(val, dict) else str(val)
                        if summary:
                            break

        if summary:
            rows.append({
                'step': step,
                'narration': summary[:3000],
            })

    rows.sort(key=lambda r: r['step'])
    return rows


def export_agent_actions_csv(
    html_path: str, metadata_path: Optional[str] = None
) -> str:
    """Export per-step agent actions as CSV string.

    Columns: step, agent_name, action, observation
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    rows = _parse_agent_actions_from_html(html_content)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['step', 'agent_name', 'action', 'observation'],
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_grounded_variables_csv(metadata_path: str) -> str:
    """Export grounded variable histories as CSV string.

    Columns: step, variable_name, variable_type, value
    """
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    gm = metadata.get('game_master', {})
    variables = gm.get('grounded_variables', [])

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['step', 'variable_name', 'variable_type', 'value'],
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()

    for var in variables:
        name = var.get('name', '')
        vtype = var.get('variable_type', 'numerical')
        for entry in var.get('history', []):
            writer.writerow({
                'step': entry.get('step', 0),
                'variable_name': name,
                'variable_type': vtype,
                'value': entry.get('value', ''),
            })

    return output.getvalue()


def export_combined_csv(
    html_path: str, metadata_path: str
) -> str:
    """Export both agent actions and grounded variables in a single CSV.

    Agent actions section followed by a blank row and grounded variables section.
    """
    actions_csv = export_agent_actions_csv(html_path, metadata_path)
    variables_csv = ''

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        gm = meta.get('game_master', {})
        if gm.get('grounded_variables'):
            variables_csv = export_grounded_variables_csv(metadata_path)

    if variables_csv:
        return actions_csv + '\n' + variables_csv
    return actions_csv


def export_full_json(
    html_path: str, metadata_path: str
) -> Dict[str, Any]:
    """Export full structured JSON combining agent actions, GM narrations,
    grounded variables, and simulation metadata."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    agent_rows = _parse_agent_actions_from_html(html_content)
    gm_rows = _parse_gm_narrations_from_html(html_content)

    metadata = {}
    grounded_variables = []
    game_theoretic = {}

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        gm = metadata.get('game_master', {})
        for var in gm.get('grounded_variables', []):
            grounded_variables.append({
                'name': var.get('name', ''),
                'variable_type': var.get('variable_type', 'numerical'),
                'description': var.get('description', ''),
                'history': var.get('history', []),
            })

        game_theoretic = metadata.get('game_theoretic', {})

    result = {
        'simulation': {
            'timestamp': metadata.get('timestamp', ''),
            'premise': metadata.get('premise', ''),
            'engine_type': metadata.get('engine_type', ''),
            'elapsed_seconds': metadata.get('elapsed_seconds', 0),
            'llm': metadata.get('llm', {}),
            'gm_llm': metadata.get('gm_llm', {}),
        },
        'agents': [
            {
                'id': a.get('id', ''),
                'name': a.get('name', ''),
                'prefab': a.get('prefab', ''),
                'goal': a.get('goal', ''),
            }
            for a in metadata.get('agents', [])
        ],
        'agent_actions': agent_rows,
        'gm_narrations': gm_rows,
        'grounded_variables': grounded_variables,
    }

    if game_theoretic:
        result['game_theoretic'] = game_theoretic

    return result
