from contextlib import nullcontext
from datetime import datetime
from uuid import UUID

import pytest
import main as pipeline_main


def test_future_checkpoint_stops_before_extraction(monkeypatch):
    finished_runs = []

    monkeypatch.setattr(pipeline_main, "load_database_settings", lambda: {})
    monkeypatch.setattr(
        pipeline_main,
        "load_settings",
        lambda: ("http://test-api", "test@example.com", "password"),
    )
    monkeypatch.setattr(
        pipeline_main,
        "load_pipeline_settings",
        lambda: {"pipeline_overlap_minutes": 5},
    )
    monkeypatch.setattr(
        pipeline_main, "start_run", lambda *args: UUID(int=1)
    )
    monkeypatch.setattr(
        pipeline_main, "login", lambda *args: "fake-token"
    )
    monkeypatch.setattr(
        pipeline_main,
        "get_wallet",
        lambda *args: {"iban": "TEST_WALLET"},
    )
    monkeypatch.setattr(
        pipeline_main,
        "pipeline_lock",
        lambda *args: nullcontext(),
    )
    monkeypatch.setattr(
        pipeline_main,
        "get_checkpoint",
        lambda *args: datetime(2099, 1, 1),
    )

    def unexpected_call(*args, **kwargs):
        raise AssertionError("Extraction or loading must not run")

    monkeypatch.setattr(
        pipeline_main, "extract_all_transfers", unexpected_call
    )
    monkeypatch.setattr(
        pipeline_main, "load_transfers", unexpected_call
    )
    monkeypatch.setattr(
        pipeline_main,
        "finish_run",
        lambda *args, **kwargs: finished_runs.append(kwargs),
    )

    with pytest.raises(ValueError, match="Checkpoint is later"):
        pipeline_main.main()

    assert len(finished_runs) == 1
    assert finished_runs[0]["status"] == "FAILED"
    assert finished_runs[0]["fetched"] == 0
    assert finished_runs[0]["error_message"] == (
        "Pipeline failed during checkpoint validation: "
        "ValueError: Checkpoint is later than the current UTC time"
    )

def test_full_history_ignores_checkpoint(monkeypatch):
    extracted_params = {}
    finished_statuses = []

    monkeypatch.setattr(pipeline_main, "load_database_settings", lambda: {})
    monkeypatch.setattr(
        pipeline_main,
        "load_settings",
        lambda: ("http://test-api", "test@example.com", "password"),
    )
    monkeypatch.setattr(
        pipeline_main,
        "load_pipeline_settings",
        lambda: {"pipeline_overlap_minutes": 5},
    )
    monkeypatch.setattr(
        pipeline_main, "start_run", lambda *args: UUID(int=2)
    )
    monkeypatch.setattr(
        pipeline_main, "login", lambda *args: "fake-token"
    )
    monkeypatch.setattr(
        pipeline_main,
        "get_wallet",
        lambda *args: {"iban": "TEST_WALLET"},
    )
    monkeypatch.setattr(
        pipeline_main,
        "pipeline_lock",
        lambda *args: nullcontext(),
    )
    monkeypatch.setattr(
        pipeline_main,
        "get_checkpoint",
        lambda *args: datetime(2020, 1, 1),
    )
    monkeypatch.setattr(
        pipeline_main,
        "update_run_context",
        lambda *args: None,
    )

    def fake_extract(*args, **kwargs):
        extracted_params.update(kwargs)
        return []

    monkeypatch.setattr(
        pipeline_main, "extract_all_transfers", fake_extract
    )
    monkeypatch.setattr(
        pipeline_main,
        "load_transfers",
        lambda *args: (0, 0),
    )
    monkeypatch.setattr(
        pipeline_main,
        "finish_run",
        lambda *args, **kwargs: finished_statuses.append(kwargs["status"]),
    )

    pipeline_main.main(full_history=True)

    assert extracted_params["from_date"] is None
    assert isinstance(extracted_params["to_date"], datetime)
    assert finished_statuses == ["SUCCESS"]