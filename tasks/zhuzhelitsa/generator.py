from kyzylborda_lib.secrets import get_secret, get_token
import requests


DISABLE_AUTOMATIC_URL = True

def generate():
    res = requests.post(
        "https://zhuzhelitsa.q.2025.ugractf.ru/api/_init",
        json={
            "api_key": get_token(),
        },
    )
    if res.status_code != 200:
        raise ValueError("Failed to generate")

    return {
        "flags": [get_secret("flag1")]
    }
