import requests

def login(url: str, email: str, password: str) -> str:
    try:
        response = requests.post(
            url = f'{url}/api/auth/login',
            json = {
                "email": email,
                "password": password
            },
            timeout = 15,
        )
    except requests.exceptions.Timeout as e:
        raise RuntimeError("Login request timed out") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("Could not connect to Spring API") from e
    if response.status_code != 200:
        raise ValueError(f"Login failed with status code {response.status_code}")
    data = response.json()
    return data["token"]