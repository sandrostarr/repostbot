import requests
import re


def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_action_price(action_type: str):
    actions_prices = {
        'LIKE': 2,
        'RECAST': 4,
        'FOLLOW': 6,
    }
    return actions_prices[action_type]


def get_action_earning(action_type: str):
    actions_earnings = {
        'LIKE': 1,
        'RECAST': 2,
        'FOLLOW': 3,
    }
    return actions_earnings[action_type]


def check_cast_from_user(casts, startHash):
    for value in casts:
        if value.startswith(startHash):
            return True, value
    return False


def get_username_from_url(url):
    username = url.rsplit('/', 1)[0]
    return username


def get_hash_from_url(url):
    cast_hash = url.rsplit('/', 1)[-1]
    return cast_hash


def is_hex_string(s):
    if s.startswith("0x"):
        s = s[2:]
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    return bool(hex_pattern.match(s))


# рассчет сколько заплатить должны токенов
def get_token_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return data['price']


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
