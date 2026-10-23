"""API keys must not end up anywhere the platform writes or serves.

Three places used to keep a key typed into the UI: the resumable state file
written at every checkpoint, the saved configuration served back by
GET /configs/{slug}, and the log route, which returned any file under logs/
by name, state files included. These tests pin all three shut. Keys read from
the environment were never written, and resume still works without a stored
key because the provider falls back to the environment.
"""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import simulations as sim_api
from backend.models.schemas import LLMSettings
from backend.services.simulation_runner import _save_resumable_state

SECRET = "sk-test-not-a-real-key-0123456789"


class _Config:
    """Just enough of SimulationConfig for the state writer."""
    engine_type = "sequential"

    def model_dump(self, mode="json"):
        return {"premise": "A town meeting about the new bridge."}


def test_state_file_omits_api_keys(tmp_path):
    llm = LLMSettings(provider="openai", model_name="gpt-4o-mini", api_key=SECRET)
    gm = LLMSettings(provider="deepseek", model_name="deepseek-v4-flash", api_key=SECRET)

    assert _save_resumable_state(tmp_path / "run.html", {"step": 5}, _Config(), llm, gm, 5, 20)

    text = (tmp_path / "run.state.json").read_text()
    assert SECRET not in text
    state = json.loads(text)
    assert "api_key" not in state["llm_settings"]
    assert "api_key" not in state["gm_llm_settings"]
    # The resume endpoint rebuilds settings this way; without a stored key the
    # provider falls back to the environment.
    assert LLMSettings(**state["llm_settings"]).api_key is None
    assert state["llm_settings"]["model_name"] == "gpt-4o-mini"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the log route reads logs/ relative to cwd
    monkeypatch.setattr(sim_api, "SAVED_CONFIGS_DIR", tmp_path / "saved_configs")
    (tmp_path / "saved_configs").mkdir()
    (tmp_path / "logs").mkdir()
    app = FastAPI()
    app.include_router(sim_api.router)
    return TestClient(app)


def test_log_route_serves_only_html(client, tmp_path):
    logs = tmp_path / "logs"
    (logs / "run.html").write_text("<html>log</html>")
    (logs / "run.state.json").write_text(json.dumps({"llm_settings": {"api_key": SECRET}}))
    (logs / "run.metadata.json").write_text("{}")

    ok = client.get("/api/simulations/logs/run.html")
    assert ok.status_code == 200
    assert ok.json()["html_content"] == "<html>log</html>"

    for name in ("run.state.json", "run.metadata.json"):
        refused = client.get(f"/api/simulations/logs/{name}")
        assert refused.status_code == 400
        assert SECRET not in refused.text


def test_saved_config_never_stores_or_serves_a_key(client, tmp_path):
    body = {
        "name": "Bridge meeting",
        "config": {"premise": "p", "agents": []},
        "llm_settings": {"provider": "openai", "model_name": "gpt-4o-mini", "api_key": SECRET},
        "gm_llm_settings": {"provider": "openai", "model_name": "gpt-4o", "api_key": SECRET},
    }
    slug = client.post("/api/simulations/configs", json=body).json()["slug"]

    assert SECRET not in (tmp_path / "saved_configs" / f"{slug}.json").read_text()
    served = client.get(f"/api/simulations/configs/{slug}").json()
    assert "api_key" not in served["llm_settings"]
    assert "api_key" not in served["gm_llm_settings"]
    assert served["llm_settings"]["model_name"] == "gpt-4o-mini"


def test_saved_config_written_before_the_fix_is_served_without_its_key(client, tmp_path):
    legacy = {
        "name": "Old",
        "config": {"premise": "p", "agents": []},
        "llm_settings": {"provider": "openai", "model_name": "gpt-4o-mini", "api_key": SECRET},
        "gm_llm_settings": None,
    }
    (tmp_path / "saved_configs" / "old.json").write_text(json.dumps(legacy))

    served = client.get("/api/simulations/configs/old")
    assert served.status_code == 200
    assert SECRET not in served.text
