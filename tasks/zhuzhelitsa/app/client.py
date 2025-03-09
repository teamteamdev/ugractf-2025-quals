import json
import requests
import sys
from zhuzhelitsa import VerificationError, Zhuzhelitsa


API_ENDPOINT = "https://zhuzhelitsa.q.2025.ugractf.ru/api"


try:
    with open("bbwallet.json") as f:
        wallet = json.load(f)
        api_key = wallet["api_key"]
        address = wallet["address"]
        private_key = wallet["private_key"]
    print(f"Using account {address}")
except FileNotFoundError:
    print("bbwallet.json not found. Initializing a new account.")

    api_key = input("Enter API key: ")
    hardened = input("Would you like to use hardened cryptography? [y/n] ") == "y"

    print("Creating a new account...")
    res = requests.post(f"{API_ENDPOINT}/register", json={
        "api_key": api_key,
        "hardened": hardened,
    })
    if res.status_code != 200:
        print(res.text)
        sys.exit(1)
    res = res.json()

    address = res["address"]
    private_key = res["private_key"]
    print(f"Account {address} created successfully.")

    with open("bbwallet.json", "w") as f:
        json.dump({
            "api_key": api_key,
            "address": address,
            "private_key": private_key,
        }, f)

res = requests.post(f"{API_ENDPOINT}/status", json={
    "api_key": api_key,
    "address": address,
})
if res.status_code != 200:
    print(res.text)
    sys.exit(1)
res = res.json()
hardened = res["hardened"]
balance = res["balance"]
print("Using", "hardened" if hardened else "default", "cryptography settings")
print(f"Your balance: {balance} BBCoins")

if input("Would you like to buy a flag? [y/n] ") != "y":
    print("Thank you for using BBCoin!")
    sys.exit(0)

subject = f"ОФОРМИТЬ АКТ купли-продажи НАД флагом НА СРЕДСТВА СО СЧЁТА {address}".encode()
signature = Zhuzhelitsa(bytes.fromhex(private_key), hardened).sign(subject)

res = requests.post(f"{API_ENDPOINT}/buy_flag", json={
    "api_key": api_key,
    "address": address,
    "signature": signature.hex(),
})
if res.status_code != 200:
    print(res.text)
    sys.exit(1)
print("Flag:", res.json()["flag"])
