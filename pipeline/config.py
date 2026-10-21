import os
from dotenv import load_dotenv


def load_settings():
    load_dotenv()

    api_url = os.getenv("WALLET_API_URL")
    email = os.getenv("WALLET_EMAIL")
    password = os.getenv("WALLET_PASSWORD")

    if not api_url or not email or not password:
        raise ValueError("Missing required settings")

    return api_url, email, password

def load_database_settings() -> dict:
    load_dotenv()
    host = os.getenv("ANALYTICS_DB_HOST")
    port = os.getenv("ANALYTICS_DB_PORT")
    dbname = os.getenv("ANALYTICS_DB_NAME")
    user = os.getenv("ANALYTICS_DB_USER")
    password = os.getenv("ANALYTICS_DB_PASSWORD")

    if not host or not port or not dbname or not user or not password:
        raise ValueError("Missing required settings")

    port = int(port)

    return {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password
    }
