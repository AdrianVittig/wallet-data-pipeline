from datetime import datetime
import psycopg

def get_checkpoint(
        db_settings: dict,
        source: str,
        wallet_iban:str
) -> datetime | None:
    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT processed_until FROM pipeline_checkpoints "
                        "WHERE source = %s AND wallet_iban = %s",
                        (source, wallet_iban))
            res = cur.fetchone()

            if res is None:
                return None
            else:
                return res[0]

def refresh_checkpoint(
        cursor: psycopg.Cursor,
        source: str,
        wallet_iban: str,
        processed_until: datetime
):
        cursor.execute("INSERT INTO pipeline_checkpoints (source, wallet_iban,"
            "processed_until) VALUES (%s, %s, %s) "
            "ON CONFLICT (source, wallet_iban) DO UPDATE "
            "SET processed_until = EXCLUDED.processed_until, "
            "updated_at = CURRENT_TIMESTAMP",
             (source, wallet_iban, processed_until))