from fastapi import FastAPI, Request
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
    print("\n==> Received API keys")
    api_key = req.api_key
    secret_key = req.secret_key

    # Sample order params (XRPUSDT spot order)
    symbol = "XRPUSDT"
    side = "Buy"
    order_type = "Market"
    qty = "5"  # Adjust as needed
    category = "spot"  # spot/linear/inverse

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

    # Step 1: Sort params alphabetically
    sorted_params = dict(sorted(params.items()))
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params.items()])

    # Step 2: Sign it
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

    print("==> Sending request to ByBit...")
    print("POST", BYBIT_URL + TRADE_ENDPOINT)
    print("Headers:", headers)
    print("Body:", json.dumps(params))

    try:
        response = requests.post(
            BYBIT_URL + TRADE_ENDPOINT,
            headers=headers,
            data=json.dumps(params)
        )

        print("==> ByBit response status code:", response.status_code)
        print("==> ByBit response body:", response.text)

        return {"status": "ok", "bybit_response": response.json()}

    except Exception as e:
        print("Error placing trade:", e)
        return {"status": "error", "message": str(e)}
