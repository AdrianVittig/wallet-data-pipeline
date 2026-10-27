import requests
import psycopg

from decimal import Decimal
from pipeline.extract import get_transfers
from pipeline.transform import transform_transfers
from pipeline.config import load_database_settings
from pipeline.run_history import save_rejected_transfers, start_run
from datetime import datetime
from uuid import uuid4
from pipeline.load import load_transfers

def test_api_amount_retains_exact_decimal_value(monkeypatch):
    response = requests.Response()

    response.status_code = 200

    response._content = (
        b'{"content":[{'
        b'"id":1,'
        b'"amount":123456789012345678.90,'
        b'"fromIban":"TEST_SENDER",'
        b'"toIban":"TEST_RECEIVER",'
        b'"category":"FOOD",'
        b'"createdAt":"2026-01-01T10:30:00"'
        b'}],"last":true}'
    )

    monkeypatch.setattr("pipeline.extract.requests.get",
                        lambda *args, **kwargs: response)

    page = get_transfers("http://test-api", "fake-token", page=0, size=1)

    correct, incorrect = transform_transfers(page["content"])

    assert incorrect == []
    assert len(correct) == 1
    assert str(correct[0]["amount"]) == "123456789012345678.90"
    assert correct[0]["amount"] ==  Decimal("123456789012345678.90")

def test_rejected_decimal_amount_is_stored_as_json_number():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"
    assert db_settings["dbname"] == "wallet_analytics_test"

    run_id = start_run(db_settings, "pytest-amount-precision")

    try:
        save_rejected_transfers(
            db_settings,
            run_id,
            [{
                "record": {
                    "id": 1,
                    "amount": Decimal("123456789012345678.90"),
                },
                "reason": "Test rejection",
            }],
        )
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT jsonb_typeof(record->'amount'),
                    (record->> 'amount')::numeric
                    FROM rejected_transfers
                    WHERE run_id = %s""",
                    (run_id,),
                )
                assert cursor.fetchone() == (
                    "number",
                    Decimal("123456789012345678.90"),
                )
    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM rejected_transfers WHERE run_id = %s",
                               (run_id,)
                )

                cursor.execute("DELETE FROM pipeline_runs WHERE run_id = %s",
                               (run_id,)
                )

def test_exact_amount_is_loaded_into_postgresql():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"
    assert db_settings["dbname"] == "wallet_analytics_test"

    source = f"pytest-amount-load-{uuid4()}"
    wallet_iban = "TEST_AMOUNT_WALLET"
    transfer_id = uuid4().int % (2**63 - 1) + 1
    amount = Decimal("123456789012345678.90")

    transfer = {
        "id": transfer_id,
        "amount": amount,
        "fromIban": wallet_iban,
        "toIban": "TEST_RECIPIENT",
        "category": "FOOD",
        "createdAt": datetime(2026, 1, 1, 10, 30),
    }

    try:
        inserted, skipped = load_transfers(
            db_settings,
            [transfer],
            source,
            wallet_iban,
            datetime(2026, 1, 1, 11, 0),
        )
        assert (inserted, skipped) == (1,0)

        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT amount FROM transfers where source_transfer_id = %s",
                    (transfer_id,),
                )
                assert cursor.fetchone()[0] == amount

    finally:
        with psycopg.connect(**db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM transfers WHERE source_transfer_id = %s",
                               (transfer_id,)
                )

                cursor.execute("DELETE FROM pipeline_checkpoints "
                               "WHERE source = %s AND wallet_iban = %s",
                               (source, wallet_iban),
                )