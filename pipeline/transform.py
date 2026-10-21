from decimal import Decimal, InvalidOperation
from datetime import datetime

def transform_transfers(content: list) -> tuple[list, list]:
    correct = []
    incorrect = []
    for transfer in content:
        if transfer.get("id") is None or transfer.get("amount") is None\
                or transfer.get("createdAt") is None:
            incorrect.append({
                "record": transfer,
                "reason": "Missing required fields"
            })
        else:
            try:
                amount = Decimal(str(transfer.get("amount")))
            except (InvalidOperation, ValueError, TypeError):
                incorrect.append({
                    "record": transfer,
                    "reason": "Invalid amount format"
                })
                continue
            try:
                date = datetime.fromisoformat(transfer.get("createdAt"))
            except (ValueError, TypeError):
                incorrect.append({
                    "record": transfer,
                    "reason": "Invalid date format"
                })
                continue

            if not amount.is_finite() or amount <= 0:
                incorrect.append({
                    "record": transfer,
                    "reason": "Invalid amount"
                })
            else:
                transformed = transfer.copy()
                transformed["createdAt"] = date
                transformed["amount"] = amount
                correct.append(transformed)
    return correct, incorrect