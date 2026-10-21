from pipeline.config import load_settings, load_database_settings
from pipeline.api_client import login
from pipeline.load import load_transfers
from pipeline.transform import transform_transfers
from pipeline.extract import extract_all_transfers


def main():
    db_settings = load_database_settings()
    api_url, email, password = load_settings()

    token = login(api_url, email, password)

    transfers = extract_all_transfers(api_url, token, 2)
    correct, incorrect = transform_transfers(transfers)

    inserted, skipped = load_transfers(db_settings, correct)

    print(f"Fetched: {len(transfers)}")
    print(f"Valid: {len(correct)}, rejected: {len(incorrect)}")
    print(f"Inserted: {inserted}, skipped: {skipped}")


if __name__ == "__main__":
    main()
