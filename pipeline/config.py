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

