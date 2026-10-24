from datetime import datetime, timedelta, timezone

from pipeline.api_client import login
from pipeline.checkpoint import get_checkpoint
from pipeline.config import (
    load_database_settings,
    load_pipeline_settings,
    load_settings,
)
from pipeline.extract import extract_all_transfers, get_wallet
from pipeline.load import load_transfers
from pipeline.run_history import (
    finish_run,
    save_rejected_transfers,
    start_run,
    update_run_context,
)
from pipeline.transform import transform_transfers


def main() -> None:
    db_settings = load_database_settings()
    api_url, email, password = load_settings()
    pipeline_settings = load_pipeline_settings()

    source = api_url.rstrip("/")
    run_id = start_run(db_settings, source)

    fetched = valid = rejected = inserted = skipped = 0
    stage = "authentication"
    loading_committed = False

    print(f"Run ID: {run_id}")

    try:
        token = login(source, email, password)

        stage = "wallet extraction"
        wallet = get_wallet(source, token)
        wallet_iban = wallet["iban"]

        stage = "checkpoint lookup"
        checkpoint = get_checkpoint(db_settings, source, wallet_iban)

        to_date = datetime.now(timezone.utc).replace(tzinfo=None)
        from_date = (
            checkpoint
            - timedelta(
                minutes=pipeline_settings["pipeline_overlap_minutes"]
            )
            if checkpoint is not None
            else None
        )

        stage = "run context update"
        update_run_context(
            db_settings, run_id, wallet_iban, from_date, to_date
        )

        stage = "transfer extraction"
        transfers = extract_all_transfers(
            source,
            token,
            size=100,
            from_date=from_date,
            to_date=to_date,
        )
        fetched = len(transfers)

        stage = "transformation"
        correct, incorrect = transform_transfers(transfers)
        valid = len(correct)
        rejected = len(incorrect)

        if incorrect:
            stage = "rejected-record storage"
            save_rejected_transfers(db_settings, run_id, incorrect)

            stage = "validation"
            raise RuntimeError(
                f"Validation failed: {rejected} rejected transfers"
            )

        stage = "transfer loading"
        inserted, skipped = load_transfers(
            db_settings,
            correct,
            source,
            wallet_iban,
            to_date,
        )
        loading_committed = True

    except Exception:
        try:
            finish_run(
                db_settings,
                run_id,
                status="FAILED",
                fetched=fetched,
                valid=valid,
                rejected=rejected,
                inserted=inserted,
                skipped=skipped,
                error_message=f"Pipeline failed during {stage}.",
            )
        except Exception:
            print(f"Could not save failure history for run {run_id}.")

        print(f"Run {run_id}: FAILED during {stage}.")
        raise

    else:
        try:
            finish_run(
                db_settings,
                run_id,
                status="SUCCESS",
                fetched=fetched,
                valid=valid,
                rejected=rejected,
                inserted=inserted,
                skipped=skipped,
            )
        except Exception:
            if loading_committed:
                print(
                    f"Run {run_id}: transfers and checkpoint were committed, "
                    "but success history could not be saved."
                )
            raise

        print(f"Run {run_id}: SUCCESS")
        print(f"Window (UTC): {from_date} -> {to_date}")
        print(f"Fetched: {fetched}")
        print(f"Valid: {valid}, rejected: {rejected}")
        print(f"Inserted: {inserted}, skipped: {skipped}")


if __name__ == "__main__":
    main()