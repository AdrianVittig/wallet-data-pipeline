import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

ALLOWED_CATEGORIES = \
    ["FOOD", "TRANSPORT", "BILLS", "ENTERTAINMENT",
 "SHOPPING", "HEALTH", "EDUCATION", "OTHER"]

def transform_transfers(content: list) -> tuple[list, list]:
    correct = []
    incorrect = []

    seen_ids = set()
    for transfer in content:
        if not isinstance(transfer, dict):
            incorrect.append({
                "record": transfer,
                "reason": "Record must be an object"
            })
            continue

        transfer_id = transfer.get("id")

        if type(transfer_id) is not int or not (
                1 <= transfer_id <= 9223372036854775807
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid transfer ID"
            })
            continue

        if transfer_id in seen_ids:
            incorrect.append({
                "record": transfer,
                "reason": "Duplicate transfer ID"
            })
            continue

        seen_ids.add(transfer_id)

        if transfer.get("amount") is None or transfer.get("createdAt") is None:
            incorrect.append({
                "record": transfer,
                "reason": "Missing required fields"
            })
            continue

        fromIban = transfer.get("fromIban")
        toIban = transfer.get("toIban")

        if(
            not isinstance(fromIban, str)
            or not fromIban.strip()
            or len(fromIban) > 255
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid sender wallet"
            })
            continue

        if(
            not isinstance(toIban, str)
            or not toIban.strip()
            or len(toIban) > 255
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid receiver wallet"
            })
            continue

        if fromIban == toIban:
            incorrect.append({
                "record": transfer,
                "reason": "Sender and receiver must differ"
            })
            continue

        category = transfer.get("category")

        if (
                not isinstance(category, str)
                or category not in ALLOWED_CATEGORIES
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid transfer category"
            })
            continue

        description = transfer.get("description")

        if description is not None and(
            not isinstance(description, str)

            or len(description) > 255
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid transfer description"
            })
            continue

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

        if date.tzinfo is not None:
            incorrect.append({
                "record": transfer,
                "reason": "Timestamp must not include a timezone"
            })
            continue
        if not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?",
                transfer["createdAt"],
        ):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid date format"
            })
            continue

        if not amount.is_finite() or amount <= 0 or amount >= Decimal("1e36"):
            incorrect.append({
                "record": transfer,
                "reason": "Invalid amount"
            })
        else:
            transformed = transfer.copy()
            transformed["createdAt"] = date
            transformed["amount"] = amount
            amount_parts = amount.as_tuple()
            exponent = amount_parts.exponent
            if exponent < -2:
                extra_digits =  -exponent - 2
                if any(amount_parts.digits[-extra_digits:]):
                    incorrect.append({
                        "record": transfer,
                        "reason": "Amount has excess decimal precision"
                    })
                    continue
            correct.append(transformed)


    return correct, incorrect