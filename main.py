from pipeline.config import load_settings
from pipeline.api_client import login, get_transfers

def main():
    api_url, email, password = load_settings()

    token = login(api_url, email, password)

    transfers = get_transfers(api_url, token)

    print(f"Fetched {len(transfers['content'])} transfers")

if __name__ == "__main__":
    main()
