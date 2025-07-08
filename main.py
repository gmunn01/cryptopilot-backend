from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
import hmac
import hashlib
import json

app = FastAPI()

BYBIT_URL = "https://api.bybit.com"
TRADE_ENDPOINT = "/v5/order/create"

class TradeRequest(BaseModel):
    api_key: str
    secret_key: str

@app.post("/place-trade")
async def place_trade(req: TradeRequest):
    api_key = req.api_key
    secret_key = req.secret_key

    symbol = "XRPUSDT"
    side = "Buy"
    order_type = "Market"
    qty = "5"
    category = "spot"

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    params = {
        "category": category,
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "qty": qty,
        "timestamp": timestamp,
        "recvWindow": recv_window
    }

    sorted_params = dict(sorted(params.items()))
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params.items()])

    signature = hmac.new(
        bytes(secret_key, "utf-8"),
        msg=bytes(query_string, "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": api_key,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            BYBIT_URL + TRADE_ENDPOINT,
            headers=headers,
            data=json.dumps(params),
            timeout=10
        )

        print("==> Raw response:")
        print(response.text)

        try:
            return response.json()
        except Exception as e:
            return {"error": "JSON decode failed", "raw_response": response.text}

    except Exception as e:
        return {"error": str(e)}
