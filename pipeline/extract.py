from datetime import datetime

import requests

def get_transfers(url: str,
                  token: str,
                  page: int,
                  size: int,
                  from_date: datetime | None = None,
                  to_date: datetime | None = None) -> dict:
    try:
        params = {
            "page": page, "size": size
        }
        if from_date is not None:
            params["fromDate"] = from_date.isoformat()
        if to_date is not None:
            params["toDate"] = to_date.isoformat()
        response = requests.get(
            url = f"{url}/api/transfers",
            headers = {
                "Authorization": f"Bearer {token}"
            },
            params = params,
            timeout = 15,
        )

    except requests.exceptions.Timeout as e:
        raise RuntimeError("Transfers request timed out") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("Could not connect to Spring API") from e
    if response.status_code != 200:
        raise ValueError(f"Transfers failed with status code {response.status_code}")
    data = response.json()
    return data

def extract_all_transfers(url: str,
                          token: str,
                          size: int,
                          from_date: datetime | None = None,
                          to_date: datetime | None = None
                          ) -> list:
    transfers = []
    page = 0
    while True:
        page_data = get_transfers(url,
                                  token,
                                  page,
                                  size,
                                  from_date=from_date,
                                  to_date=to_date)
        transfers.extend(page_data["content"])
        if page_data["last"]:
            break
        else:
            page += 1

    return transfers

def get_wallet(url: str, token: str) -> dict:
    try:
        response = requests.get(
            f'{url}/api/wallet',
            headers = {
                "Authorization": f"Bearer {token}"
            },
            timeout = 15,
        )

        if response.status_code != 200:
            raise ValueError(f"Wallet failed with status code {response.status_code}")
        data = response.json()
        return data
    except requests.exceptions.Timeout as e:
        raise RuntimeError("Wallet request timed out") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("Could not connect to Spring API") from e