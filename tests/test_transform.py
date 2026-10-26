from pipeline.transform import transform_transfers

def test_duplicate_transfer_id_is_rejected():
    transfer = {
        "id": 59002,
        "amount": "10.50",
        "fromIban": "TEST_SENDER",
        "toIban": "TEST_RECEIVER",
        "category": "FOOD",
        "createdAt": "2026-01-01T10:30:00",
    }

    correct, incorrect = transform_transfers([transfer, transfer.copy()])

    assert len(correct) == 1
    assert len(incorrect) == 1
    assert incorrect[0]["reason"] == "Duplicate transfer ID"

def test_order_check():
    transfer = {
        "id": 59002,
        "amount": "10.50",
        "fromIban": "TEST_SENDER",
        "toIban": "TEST_RECEIVER",
        "category": "FOOD",
        "createdAt": "2026-01-01T10:30:00",
    }

    first = transfer.copy()
    del first["amount"]

    correct, incorrect = transform_transfers([first, transfer.copy()])

    assert len(correct) == 0
    assert len(incorrect) == 2
    assert incorrect[0]["reason"] == "Missing required fields"
    assert incorrect[1]["reason"] == "Duplicate transfer ID"
