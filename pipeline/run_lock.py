import hashlib
from contextlib import contextmanager

import psycopg


def lock_key(source: str, wallet_iban: str) -> int:
    value = f"{source}\0{wallet_iban}".encode("utf-8")
    digest = hashlib.sha256(value).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=True)

@contextmanager
def pipeline_lock(db_settings: dict, source: str, wallet_iban: str):
    key = lock_key(source, wallet_iban)

    with psycopg.connect(**db_settings, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT pg_try_advisory_lock(%s)''', (key,))

            acquired = cursor.fetchone()[0]

        if not acquired:
            raise RuntimeError(
                 f"Pipeline already running for {source} / {wallet_iban}"
            )

        yield
