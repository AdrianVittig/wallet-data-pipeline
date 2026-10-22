from datetime import datetime

import psycopg

from pipeline.checkpoint import refresh_checkpoint


def load_transfers(db_settings: dict,
                   transfers: list,
                   source: str,
                   wallet_iban: str,
                   processed_until: datetime) -> tuple[int, int]:
    with psycopg.connect(**db_settings) as connection:
        with connection.cursor() as cursor:
            inserted = 0
            skipped = 0
            for transfer in transfers:
                query = '''INSERT INTO transfers 
                (source_transfer_id, amount, 
                from_iban, to_iban, 
                category, description, created_at)
                 VALUES(%s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (source_transfer_id) DO NOTHING'''
                values = (transfer["id"], transfer["amount"],
                          transfer["fromIban"], transfer["toIban"],
                          transfer["category"], transfer.get("description"),
                          transfer["createdAt"])

                cursor.execute(query, values)
                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1
            refresh_checkpoint(cursor, source, wallet_iban, processed_until)

    return inserted, skipped
