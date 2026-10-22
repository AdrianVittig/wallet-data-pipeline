import pytest
from pipeline.load import load_transfers

import datetime
from decimal import Decimal

import psycopg

from pipeline.config import load_database_settings
from pipeline.checkpoint import refresh_checkpoint as real_refresh_checkpoint, get_checkpoint


def test_loading_failure_rolls_back_transfers_and_checkpoint(monkeypatch):
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"

    source = "pytest-rollback"
    wallet_iban = "TEST_WALLET"
    wallet_iban_r = "TEST_WALLET_R"
    initial_checkpoint = datetime.datetime(2026, 1, 1, 10, 0)
    processed_until = datetime.datetime(2026, 1, 1, 11, 0)
    amount = Decimal(100)
    transfer_id = -58000

    transfer = {
        "id": transfer_id,
        "amount": amount,
        "fromIban": wallet_iban,
        "toIban": wallet_iban_r,
        "category": "FOOD",
        "createdAt": datetime.datetime(2026, 1, 1, 10, 30)
    }

    assert db_settings["dbname"] == "wallet_analytics_test"

    try:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE from transfers WHERE source_transfer_id = %s",
                    (transfer_id,)
                )
                cursor.execute(
                    "INSERT into pipeline_checkpoints (source, wallet_iban, processed_until) "
                    "VALUES (%s, %s, %s) ON CONFLICT (source, wallet_iban) "
                    "DO UPDATE SET processed_until = EXCLUDED.processed_until",
                    (source, wallet_iban, initial_checkpoint)
                )

        def refresh_then_fail(cursor, source, wallet_iban, processed_until):
            real_refresh_checkpoint(cursor, source, wallet_iban, processed_until)
            raise RuntimeError("Simulated failure")

        monkeypatch.setattr(
            "pipeline.load.refresh_checkpoint",
            refresh_then_fail,
        )

        with pytest.raises(RuntimeError, match="Simulated failure"):
            load_transfers(
                db_settings, [transfer], source, wallet_iban, processed_until
            )

        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT source_transfer_id "
                               "FROM transfers "
                               "WHERE source_transfer_id = %s", (transfer_id, ))
                assert cursor.fetchone() is None
                cursor.execute("SELECT processed_until "
                               "FROM pipeline_checkpoints "
                               "WHERE source = %s AND wallet_iban = %s",
                               (source, wallet_iban))
                row = cursor.fetchone()
                assert row is not None
                assert row[0] == initial_checkpoint
    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE from transfers WHERE source_transfer_id = %s",
                               (transfer_id,))
                cursor.execute("DELETE from pipeline_checkpoints WHERE source = %s AND wallet_iban = %s",
                               (source, wallet_iban))

def test_checkpoints_are_independent_per_source_and_wallet():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"
    assert db_settings["dbname"] == "wallet_analytics_test"

    source_a = "pytest-source-a"
    source_b = "pytest-source-b"
    wallet_a = "TEST_WALLET_A"
    wallet_b = "TEST_WALLET_B"

    try:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM pipeline_checkpoints WHERE source = %s AND wallet_iban = %s",
                    (source_b, wallet_b)
                )
                real_refresh_checkpoint(
                    cursor, source_a, wallet_a,
                    datetime.datetime(2026, 1, 1, 10, 0)
                )

                real_refresh_checkpoint(
                    cursor, source_a, wallet_b,
                    datetime.datetime(2026, 2, 1, 10, 0)
                )

                real_refresh_checkpoint(
                    cursor, source_b, wallet_a,
                    datetime.datetime(2026, 3, 1, 10, 0)
                )

        with (psycopg.connect(**db_settings) as conn):
            with conn.cursor() as cursor:
                real_refresh_checkpoint(
                    cursor, source_a, wallet_a,
                    datetime.datetime(2026, 1, 1, 13, 0)
                )

        assert get_checkpoint(db_settings, source_a, wallet_a) == datetime.datetime(2026, 1, 1, 13, 0)
        assert get_checkpoint(db_settings, source_a, wallet_b) == datetime.datetime(2026, 2, 1, 10, 0)
        assert get_checkpoint(db_settings, source_b, wallet_a) == datetime.datetime(2026, 3, 1, 10, 0)
        assert get_checkpoint(db_settings, source_b, wallet_b) is None

    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE from pipeline_checkpoints WHERE source = %s AND wallet_iban = %s",
                               (source_a, wallet_a))
                cursor.execute("DELETE from pipeline_checkpoints WHERE source = %s AND wallet_iban = %s",
                               (source_a, wallet_b))
                cursor.execute("DELETE from pipeline_checkpoints WHERE source = %s AND wallet_iban = %s",
                               (source_b, wallet_a))
