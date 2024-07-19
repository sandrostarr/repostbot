import requests

def get_token_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return data['price']

# s = get_token_price("ETHUSDT")
# print(type(s))

def summ_result(
        tokens_value: float,
        currency: str = "USDT"
) -> float:
    TOKEN_PRICE = 0.1

    if currency == "USDT":
        result = tokens_value * TOKEN_PRICE
        return result
    elif currency == "ETH":
        eth_price = float(get_token_price("ETHUSDT"))
        result = tokens_value * TOKEN_PRICE / eth_price
        return result
    elif currency == "MATIC":
        matic_price = float(get_token_price("MATICUSDT"))
        result = tokens_value * TOKEN_PRICE / matic_price
        return result
    else:
        return 0.1


# s = summ_result(tokens_value=1000,currency="MATIC")
# print(s)