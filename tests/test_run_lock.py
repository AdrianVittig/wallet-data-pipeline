import pytest

from pipeline.config import load_database_settings
from pipeline.run_lock import pipeline_lock


def test_same_wallet_cannot_run_twice_and_lock_is_released():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"

    source = "pytest-run-lock"
    wallet_iban = "TEST_LOCK_WALLET"

    with pipeline_lock(db_settings, source, wallet_iban):
        with pytest.raises(RuntimeError, match="Pipeline already running"):
            with pipeline_lock(db_settings, source, wallet_iban):
                pass

    with pipeline_lock(db_settings, source, wallet_iban):
        pass

def test_different_wallets_and_sources_have_independent_locks():
    db_settings = load_database_settings()
    db_settings["dbname"] = "wallet_analytics_test"

    with pipeline_lock(db_settings, "source-a", "wallet-a"):
        with pipeline_lock(db_settings, "source-a", "wallet-b"):
            with pipeline_lock(db_settings, "source-b", "wallet-a"):
                pass