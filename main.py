from datetime import datetime, timezone, timedelta

from pipeline.config import (load_settings,
                             load_database_settings,
                             load_pipeline_settings)
from pipeline.api_client import login
from pipeline.load import load_transfers
from pipeline.transform import transform_transfers
from pipeline.extract import extract_all_transfers, get_wallet
from pipeline.checkpoint import get_checkpoint


def main():
    db_settings = load_database_settings()
    api_url, email, password = load_settings()

    pipeline_settings = load_pipeline_settings()
    token = login(api_url, email, password)

    wallets = get_wallet(api_url, token)
    wallet_iban = wallets["iban"]
    source = api_url.rstrip("/")
    checkpoint = get_checkpoint(db_settings, source, wallet_iban)

    from_date = (
        checkpoint - timedelta(minutes=pipeline_settings["pipeline_overlap_minutes"])
        if checkpoint is not None
        else None
    )
    to_date = datetime.now(timezone.utc).replace(tzinfo=None)

    transfers = extract_all_transfers(api_url,
                                      token,
                                      size=2,
                                      from_date=from_date,
                                      to_date=to_date)
    correct, incorrect = transform_transfers(transfers)

    if incorrect:
        raise RuntimeError(
            f"Validation failed: {len(incorrect)} rejected transfers"
        )


    inserted, skipped = load_transfers(db_settings,
                                       correct,
                                       source,
                                       wallet_iban,
                                       to_date)

    print(f"Window (UTC): {from_date} -> {to_date}")
    print(f"Fetched: {len(transfers)}")
    print(f"Valid: {len(correct)}, rejected: {len(incorrect)}")
    print(f"Inserted: {inserted}, skipped: {skipped}")

if __name__ == "__main__":
    main()
