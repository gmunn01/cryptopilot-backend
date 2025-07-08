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

        print("Sending request to Bybit API...")

        response = requests.post(url, headers=headers, params={
            "apiKey": api_key,
            "recvWindow": recv_window,
            "timestamp": timestamp,
            "sign": signature
        }, json=payload)

        print("Bybit response:", response.text)
        return response.json()

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
