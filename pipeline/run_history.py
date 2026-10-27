import uuid
from datetime import datetime
from uuid import UUID

import psycopg
import simplejson
from psycopg.types.json import Jsonb


def start_run(db_settings: dict, source: str) -> UUID:
    run_id = uuid.uuid4()
    status = "RUNNING"
    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO pipeline_runs 
            (run_id, source, status) VALUES
            (%s, %s, %s)''', (run_id, source, status))

    return run_id

def update_run_context(db_settings: dict, run_id: UUID,
                       wallet_iban: str,
                       from_date: datetime | None, to_date: datetime) -> None:
    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''UPDATE pipeline_runs 
            SET wallet_iban=%s, from_date=%s, to_date=%s 
            WHERE run_id=%s
            ''', (wallet_iban, from_date, to_date, run_id))

def finish_run(db_settings: dict,
               run_id: UUID,
               status: str,
               fetched: int,
               valid: int,
               rejected: int,
               inserted: int,
               skipped: int,
               error_message: str | None = None) -> None:
    if status not in ("SUCCESS", "FAILED"):
        raise ValueError("Incorrect status")
    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''UPDATE pipeline_runs 
            SET status = %s, finished_at = CURRENT_TIMESTAMP,
            fetched = %s,
            valid = %s, 
            rejected = %s,
            inserted = %s,
            skipped = %s,
            error_message = %s
            WHERE run_id=%s ''',
            (status, fetched, valid, rejected, inserted, skipped, error_message, run_id))


def save_rejected_transfers(
        db_settings: dict,
        run_id: UUID,
        rejected_records: list
) -> None:
    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cursor:
            for record in rejected_records:
                cursor.execute(
                    """INSERT INTO rejected_transfers (run_id, record, reason)
                    VALUES (%s, %s, %s)""",
                    (
                        run_id,
                        Jsonb(record["record"], dumps=simplejson.dumps),
                        record["reason"],
                    ),
                )