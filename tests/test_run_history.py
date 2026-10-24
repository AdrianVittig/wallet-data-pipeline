import datetime

import psycopg
import pytest
import main as pipeline_main

from pipeline.config import load_database_settings
from pipeline.checkpoint import refresh_checkpoint, get_checkpoint


def test_validation_failure_preserves_rejected_record(monkeypatch):
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"

    source = "http://pytest-run-history"

    wallet_iban = "TEST_RUN_HISTORY_WALLET"

    initial_checkpoint = datetime.datetime(2026, 1, 1, 10, 0)

    assert db_settings["dbname"] == "wallet_analytics_test"

    monkeypatch.setattr(
        pipeline_main, "load_database_settings", lambda: db_settings
    )

    monkeypatch.setattr(
        pipeline_main,
        "login",
        lambda url, email, password: "fake-token",
    )

    monkeypatch.setattr(
        pipeline_main,
        "get_wallet",
        lambda url, token: {"iban": wallet_iban}
    )

    monkeypatch.setattr(
        pipeline_main, "load_settings",
        lambda: (source, "test@example.com", "test-password"),
    )

    monkeypatch.setattr(
        pipeline_main, "load_pipeline_settings",
        lambda: {"pipeline_overlap_minutes": 5},
    )

    transfer = {
        "id": -59000,
        "amount": "abc",
        "createdAt": "2026-01-01T10:30:00",
    }

    monkeypatch.setattr(
        pipeline_main,
        "extract_all_transfers",
        lambda *args, **kwargs: [transfer],
    )
    try:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                refresh_checkpoint(
                    cursor, source, wallet_iban, initial_checkpoint
                )


        with pytest.raises(RuntimeError, match="Validation failed"):
            pipeline_main.main()

        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT run_id, status, fetched, valid, rejected, inserted, skipped FROM pipeline_runs WHERE source = %s ORDER BY started_at DESC LIMIT 1", (source,))
                row = cursor.fetchone()
                assert row is not None

                run_id = row[0]
                assert row[1] == "FAILED"
                assert row[2:] == (1,0,1,0,0)
                cursor.execute("SELECT record, reason FROM rejected_transfers WHERE run_id = %s", (run_id,))

                rows = cursor.fetchall()

                assert len(rows) == 1
                assert rows[0][0] == transfer
                assert rows[0][1] == "Invalid amount format"

                assert get_checkpoint(db_settings, source, wallet_iban) == initial_checkpoint

    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    DELETE FROM rejected_transfers
                        WHERE run_id IN (
                        SELECT run_id FROM pipeline_runs WHERE source = %s
                        )
                        ''', (source,)
                )

                cursor.execute('''
                    DELETE FROM pipeline_runs WHERE source = %s''', (source,)
                )

                cursor.execute(
                    '''DELETE FROM pipeline_checkpoints
                    WHERE source = %s AND wallet_iban = %s''', (source, wallet_iban),
                )

def test_loading_failure_preserves_run_history(monkeypatch):
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"

    source = "http://pytest-loading-failure"
    wallet_iban = "TEST_LOADING_FAILURE_WALLET"

    initial_checkpoint = datetime.datetime(2026, 1, 1, 10, 0)

    assert db_settings["dbname"] == "wallet_analytics_test"

    monkeypatch.setattr(
        pipeline_main, "load_database_settings", lambda: db_settings
    )

    monkeypatch.setattr(
        pipeline_main,
        "login",
        lambda url, email, password: "fake-token",
    )

    monkeypatch.setattr(
        pipeline_main,
        "get_wallet",
        lambda url, token: {"iban": wallet_iban}
    )

    monkeypatch.setattr(
        pipeline_main, "load_settings",
        lambda: (source, "test@example.com", "test-password"),
    )

    monkeypatch.setattr(
        pipeline_main, "load_pipeline_settings",
        lambda: {"pipeline_overlap_minutes": 5},
    )

    transfer = {
        "id": -59001,
        "amount": "100.00",
        "fromIban": wallet_iban,
        "toIban": "TEST_RECIPIENT",
        "category": "FOOD",
        "description": "Rollback test",
        "createdAt": "2026-01-01T10:30:00",
    }

    monkeypatch.setattr(
        pipeline_main,
        "extract_all_transfers",
        lambda *args, **kwargs: [transfer],
    )

    def refresh_then_fail(cursor, source, wallet_iban, processed_until):
        refresh_checkpoint(cursor, source, wallet_iban, processed_until)
        raise RuntimeError("Simulated loading failure")

    monkeypatch.setattr(
        "pipeline.load.refresh_checkpoint",
        refresh_then_fail,
    )
    try:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM transfers WHERE source_transfer_id = %s",
                    (transfer["id"],),
                )
                refresh_checkpoint(
                    cursor, source, wallet_iban, initial_checkpoint
                )



        with pytest.raises(RuntimeError, match="Simulated loading failure"):
            pipeline_main.main()

        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT run_id, status, fetched, valid, rejected, inserted, skipped FROM pipeline_runs WHERE source = %s ORDER BY started_at DESC LIMIT 1",
                    (source,))
                row = cursor.fetchone()
                assert row is not None

                run_id = row[0]
                assert row[1] == "FAILED"
                assert row[2:] == (1, 1, 0, 0, 0)
                cursor.execute("SELECT record, reason FROM rejected_transfers WHERE run_id = %s", (run_id,))

                rows = cursor.fetchall()

                assert rows == []
                cursor.execute(
                    "SELECT source_transfer_id FROM transfers WHERE source_transfer_id = %s",
                    (transfer["id"],),
                )
                assert cursor.fetchone() is None

                assert (
                        get_checkpoint(db_settings, source, wallet_iban)
                        == initial_checkpoint
                )


    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                                    DELETE FROM rejected_transfers
                                        WHERE run_id IN (
                                        SELECT run_id FROM pipeline_runs WHERE source = %s
                                        )
                                        ''', (source,)
                               )

                cursor.execute('''
                                    DELETE FROM pipeline_runs WHERE source = %s''', (source,)
                               )

                cursor.execute(
                    '''DELETE FROM pipeline_checkpoints
                    WHERE source = %s AND wallet_iban = %s''', (source, wallet_iban),
                )

                cursor.execute(
                    "DELETE FROM transfers WHERE source_transfer_id = %s",
                    (transfer["id"],),
                )

