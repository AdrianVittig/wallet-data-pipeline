import requests

def get_transfers(url: str, token: str, page: int, size: int) -> dict:
    try:
        response = requests.get(
            url = f"{url}/api/transfers",
            headers = {
                "Authorization": f"Bearer {token}"
            },
            params={
                "page": page, "size": size
            },
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

def extract_all_transfers(url: str, token: str, size: int) -> list:
    transfers = []
    page = 0
    while True:
        page_data = get_transfers(url, token, page, size)
        transfers.extend(page_data["content"])
        if page_data["last"]:
            break
        else:
            page += 1

    return transfers