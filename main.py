from pipeline.config import load_settings
from pipeline.api_client import login, get_transfers
from pipeline.transform import transform_transfers


def main():
    api_url, email, password = load_settings()

    token = login(api_url, email, password)

    transfers = get_transfers(api_url, token, 0, 2)

    print(f"Fetched {len(transfers['content'])} transfers")

    correct, incorrect = transform_transfers(transfers['content'])

    print(f"Valid: {len(correct)}, rejected: {len(incorrect)}")
if __name__ == "__main__":
    main()
