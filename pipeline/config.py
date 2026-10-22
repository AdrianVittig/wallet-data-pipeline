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

def load_pipeline_settings() -> dict:
    load_dotenv()
    pipeline_overlap_minutes = os.getenv("PIPELINE_OVERLAP_MINUTES")
    if not pipeline_overlap_minutes:
        raise ValueError("Missing pipeline overlap setting")
    try:
        pipeline_overlap_minutes = int(pipeline_overlap_minutes)
    except ValueError:
        raise ValueError("Pipeline overlap must be an integer!")

    if pipeline_overlap_minutes < 0:
        raise ValueError("Pipeline overlap must be non-negative")
    return {
        "pipeline_overlap_minutes": pipeline_overlap_minutes
    }