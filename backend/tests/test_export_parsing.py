"""Tests for parsing Concordia HTML logs into structured exports.

Both behaviors pinned here failed the same way: an export that was missing
data looked exactly like an export of a run that produced none. A reader has
no way to tell those apart from the JSON, so the parser has to.
"""

import json
import logging

from backend.utils.data_exporter import (
    _extract_content_store,
    _extract_entries,
    _parse_agent_actions_from_html,
    _parse_gm_narrations_from_html,
)


def _log(entries, content_store=None):
    """Build a minimal log page in the ENTRIES / CONTENT_STORE format."""
    return (
        "<html><script>\n"
        f"const ENTRIES = {json.dumps(entries)};\n"
        f"const CONTENT_STORE = {json.dumps(content_store or {})};\n"
        "</script></html>"
    )


# --- Asynchronous game master entries ------------------------------------

ASYNC_GM_ENTRY = {
    "entry_type": "step",
    "entity_name": "MastoTown Rules",
    "component_name": "step",
    "step": 1,
    "summary": "Step 1 MastoTown Rules --- Event: Glenn_Boost created post #0",
    "deduplicated_data": {},
}

AGENT_ENTRY = {
    "entry_type": "entity",
    "entity_name": "Glenn_Boost",
    "component_name": "entity_action",
    "step": 1,
    "summary": "Glenn_Boost posted",
    "deduplicated_data": {},
}


def test_asynchronous_game_master_narrations_are_exported():
    """The asynchronous engine tags game master entries 'step'. Matching only
    'game_master' and 'scene' exported an empty narration list for every
    asynchronous run, which is the entire Mastodon series."""
    rows = _parse_gm_narrations_from_html(_log([ASYNC_GM_ENTRY]))

    assert len(rows) == 1
    assert rows[0]["step"] == 1
    assert "Glenn_Boost created post #0" in rows[0]["narration"]


def test_synchronous_game_master_narrations_still_export():
    entry = {**ASYNC_GM_ENTRY, "entry_type": "game_master"}
    assert len(_parse_gm_narrations_from_html(_log([entry]))) == 1


def test_agent_actions_are_not_counted_as_narrations():
    """The two parsers read disjoint entry types, so widening the narration
    filter must not start picking up what agents did."""
    html = _log([ASYNC_GM_ENTRY, AGENT_ENTRY])

    narrations = _parse_gm_narrations_from_html(html)
    actions = _parse_agent_actions_from_html(html)

    assert [r["narration"] for r in narrations] == [ASYNC_GM_ENTRY["summary"]]
    assert [r["agent_name"] for r in actions] == ["Glenn_Boost"]


# --- A parse failure is not an empty run ---------------------------------

def test_a_corrupt_entries_block_is_reported_not_silently_empty(caplog):
    html = ("<html><script>\nconst ENTRIES = [{\"broken\": ];\n"
            "const CONTENT_STORE = {};\n</script></html>")

    with caplog.at_level(logging.WARNING):
        entries = _extract_entries(html)

    assert entries == []          # partial export beats a failed one
    assert "did not parse" in caplog.text


def test_a_corrupt_content_store_is_reported_not_silently_empty(caplog):
    html = ("<html><script>\nconst ENTRIES = [];\n"
            "const CONTENT_STORE = {\"a\": };\n</script></html>")

    with caplog.at_level(logging.WARNING):
        store = _extract_content_store(html)

    assert store == {}
    assert "did not parse" in caplog.text


def test_a_log_with_no_entries_block_warns_about_nothing():
    """Absent is not corrupt: a log written before any entry exists is a
    legitimate empty read and must not raise or warn."""
    assert _extract_entries("<html></html>") == []
    assert _extract_content_store("<html></html>") == {}
