from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time
import hmac
import hashlib

app = FastAPI()

class APIKeys(BaseModel):
    api_key: str
    secret_key: str

def generate_signature(api_key, secret_key, recv_window, timestamp, params=""):
    query_string = f"{timestamp}{api_key}{recv_window}{params}"
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

@app.post("/place-trade")
def place_trade(keys: APIKeys):
    try:
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
            "qty": "10"
        }

        params_string = ''.join([f"{key}{value}" for key, value in payload.items()])
        signature = generate_signature(api_key, secret_key, recv_window, timestamp, params_string)

        headers = {
            "X-BYBIT-API-KEY": api_key,
            "X-BYBIT-SIGN": signature,
            "X-BYBIT-TIMESTAMP": timestamp,
            "X-BYBIT-RECV-WINDOW": recv_window,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

