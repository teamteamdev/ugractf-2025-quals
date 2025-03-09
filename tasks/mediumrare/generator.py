from kyzylborda_lib.secrets import get_token
import requests


def generate():
    token = get_token()
    res = requests.post(f"https://mediumrare.q.2025.ugractf.ru/{token}/__reset_db__/")
    if res.status_code != 200:
        raise ValueError("Failed to generate")
