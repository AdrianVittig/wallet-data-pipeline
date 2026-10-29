from pathlib import Path

import pandas as pd
import psycopg

from pipeline.config import load_database_settings

REPORTS_DIR = Path(__file__).resolve().parent / "sql" / "reports"

def load_report(db_settings: dict, filename: str) -> pd.DataFrame:
    query = (REPORTS_DIR / filename).read_text(encoding="utf-8")

    with psycopg.connect(**db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [column.name for column in cursor.description]
            rows = cursor.fetchall()

    return pd.DataFrame(rows, columns=columns)

def main() -> None:
    db_settings = load_database_settings()

    monthly = load_report(db_settings, "monthly_wallet_summary.sql")
    categories = load_report(db_settings, "spending_by_category.sql")

    print('\n Monthly Wallet Summary:')
    print(monthly.to_string(index=False))

    print('\n Spending By Category:')
    print(categories.to_string(index=False))

    spending_totals = categories.groupby(
        ["source", "wallet_iban"], as_index=False
    )["spent_amount"].sum()

    print("\nTotal outgoing spending by wallet")
    print(spending_totals.to_string(index=False))

if __name__ == "__main__":
    main()