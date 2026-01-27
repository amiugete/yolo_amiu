import requests


def get_auth_session(user: str, pwd: str, auth_url: str) -> requests.Session:
    """Crea una sessione autenticata per le chiamate API REST"""
    session = requests.Session()
    bodyRequest = {
        "username": user,
        "password": pwd
        }
    response = session.post(auth_url, json=bodyRequest)
    result: dict = response.json()
    TOKEN = result["token"]

    session.headers.update({
        "Authorization": f"Bearer {TOKEN}"
    })
    return session
