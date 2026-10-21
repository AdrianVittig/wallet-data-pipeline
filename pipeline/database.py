import psycopg


def check_database_connection(settings_dict: dict):
    with psycopg.connect(**settings_dict) as connection:
        with connection.cursor() as cursor:
            return cursor.execute("SELECT 1").fetchone()

