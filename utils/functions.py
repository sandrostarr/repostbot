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
