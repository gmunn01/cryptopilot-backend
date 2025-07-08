from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time
import hmac
import hashlib
import json

app = FastAPI()

class APIKeys(BaseModel):
    api_key: str
    secret_key: str

def generate_signature(secret_key, params):
    param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(secret_key.encode(), param_str.encode(), hashlib.sha256).hexdigest()
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

        params = {
            "apiKey": api_key,
            "timestamp": timestamp,
            "recvWindow": recv_window
        }

        # Merge both sets of parameters
        all_params = {**params, **payload}
        signature = generate_signature(secret_key, all_params)

        headers = {
            "X-BYBIT-API-KEY": api_key,
            "X-BYBIT-API-SIGN": signature,
            "X-BYBIT-API-TIMESTAMP": timestamp,
            "X-BYBIT-API-RECV-WINDOW": recv_window,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


