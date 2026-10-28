from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import psycopg

from pipeline.config import load_database_settings
from pipeline.load import load_transfers


def test_same_transfer_id_is_independent_per_source():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"
    assert db_settings["dbname"] == "wallet_analytics_test"

    suffix = uuid4().hex
    source_a = f"pytest-source-a-{suffix}"
    source_b = f"pytest-source-b-{suffix}"
    wallet_iban = "TEST_SOURCE_WALLET"
    transfer_id = uuid4().int % (2**63 - 1) + 1
    processed_until = datetime(2026, 1, 1, 11, 0)

    transfer = {
        "id": transfer_id,
        "amount": Decimal("10.50"),
        "fromIban": wallet_iban,
        "toIban": "TEST_RECIPIENT",
        "category": "FOOD",
        "createdAt": datetime(2026, 1, 1, 10, 30),
    }

    try:
        assert load_transfers(
            db_settings, [transfer], source_a, wallet_iban, processed_until
        ) == (1, 0)
        assert load_transfers(
            db_settings, [transfer], source_a, wallet_iban, processed_until
        ) == (0, 1)
        assert load_transfers(
            db_settings, [transfer], source_b, wallet_iban, processed_until
        ) == (1, 0)

        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT source FROM transfers
                       WHERE source_transfer_id = %s
                         AND source IN (%s, %s)
                       ORDER BY source""",
                    (transfer_id, source_a, source_b),
                )
                assert cursor.fetchall() == [(source_a,), (source_b,)]
    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """DELETE FROM transfers
                       WHERE source_transfer_id = %s
                         AND source IN (%s, %s)""",
                    (transfer_id, source_a, source_b),
                )
                cursor.execute(
                    """DELETE FROM pipeline_checkpoints
                       WHERE source IN (%s, %s) AND wallet_iban = %s""",
                    (source_a, source_b, wallet_iban),
                )