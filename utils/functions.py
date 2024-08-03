import random

import requests
import re


def is_number(string) -> bool:
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


def get_answer_t(task_type: str):
    answers_ts = {
        'LIKE': ['пост', 'https://warpcast.com/vitalik.eth/0xf2fb9ef7'],
        'RECAST': ['пост', 'https://warpcast.com/vitalik.eth/0xf2fb9ef7'],
        'FOLLOW': ['профиль', 'https://warpcast.com/vitalik.eth'],
    }
    return answers_ts[task_type]


def get_t_type(task_type: str):
    task_types = {
        'LIKE': 'лайк',
        'RECAST': 'рекаст',
        'FOLLOW': 'подпичик',
    }
    return task_types[task_type]


def get_action_earning(action_type: str):
    actions_earnings = {
        'LIKE': 1,
        'RECAST': 2,
        'FOLLOW': 3,
    }
    return actions_earnings[action_type]


def check_cast_from_user(casts, start_hash):
    for value in casts:
        if value.startswith(start_hash):
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


# расчёт сколько заплатить должны токенов
def get_token_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return data['price']


def summ_result(
        tokens_value: float,
        currency: str = "USDT"
) -> float:
    token_price = 0.1

    if currency == "USDT":
        result = tokens_value * token_price
        return result
    elif currency == "ETH":
        eth_price = float(get_token_price("ETHUSDT"))
        result = tokens_value * token_price / eth_price
        return result
    elif currency == "MATIC":
        matic_price = float(get_token_price("MATICUSDT"))
        result = tokens_value * token_price / matic_price
        return result
    else:
        return token_price


def get_hello():
    data = [
        "Hello",
        "Hola",
        "Bonjour",
        "Hallo",
        "Ciao",
        "Olá",
        "Привет",
        "你好 (Nǐ hǎo)",
        "こんにちは (Konnichiwa)",
        "안녕하세요 (Annyeong haseyo)",
        "مرحبا (Marhaban)",
        "Γειά σας (Geiá sas)",
        "Merhaba",
        "Hej",
        "Hei",
        "Ahoj",
        "Cześć",
        "Szia"
    ]

    return data[random.randint(0, len(data))]
