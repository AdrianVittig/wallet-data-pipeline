from pipeline.config import load_settings
from pipeline.api_client import login, get_transfers
from pipeline.transform import transform_transfers
from pipeline.config import load_database_settings
from pipeline.database import check_database_connection


def main():
    db_settings = load_database_settings()
    result = check_database_connection(db_settings)
    print(f"Database connection: {result}")

    api_url, email, password = load_settings()

    token = login(api_url, email, password)

    transfers = get_transfers(api_url, token, 0, 2)

    print(f"Fetched {len(transfers['content'])} transfers")

    correct, incorrect = transform_transfers(transfers['content'])

    print(f"Valid: {len(correct)}, rejected: {len(incorrect)}")
if __name__ == "__main__":
    main()
