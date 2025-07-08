from fastapi import FastAPI
from pydantic import BaseModel
import time
import hmac
import hashlib
import requests

app = FastAPI()

class APIKeys(BaseModel):
    api_key: str
    secret_key: str

def generate_signature(secret, message):
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

@app.post("/place-trade")
def place_trade(keys: APIKeys):
    try:
        print("Received API keys:", keys.api_key, keys.secret_key)

        url = "https://api.bybit.com/v5/order/create"
        api_key = keys.api_key
        secret_key = keys.secret_key
        recv_window = "5000"
        timestamp = str(int(time.time() * 1000))

        payload = {
            "category": "spot",
            "symbol": "XRPUSDT",
            "side": "Buy",
            "orderType": "Market",
            "qty": "10"  # Test quantity
        }

        query_string = f"apiKey={api_key}&recvWindow={recv_window}&timestamp={timestamp}"
        signature = generate_signature(secret_key, query_string)

        headers = {
            "X-BYBIT-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        full_url = f"{url}?{query_string}&sign={signature}"

        response = requests.post(full_url, headers=headers, json=payload)
        print("ByBit Response:", response.status_code, response.text)

        return {
            "status": response.status_code,
            "bybit_response": response.json()
        }

    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}
