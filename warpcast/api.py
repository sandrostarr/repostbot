import requests
from requests.exceptions import Timeout, ConnectionError

warp_api = "https://client.warpcast.com/v2/"

def get_fid_from_username(
        username: str,

):
    param = f"user-by-username?username={username}"
    try:
        responce = requests.get(warp_api+param)
        fid = responce.json()['result']['user']['fid']

        return fid
    except:
        return None


def get_casts_from_user(
        username: str,
):
    try:
        fid = get_fid_from_username(username=username)
        param = f"casts?fid={fid}"

        responce = requests.get(warp_api+param)

        hash_list = [cast['hash'] for cast in responce.json()['result']['casts']]

        return hash_list
    except:
        return None




def get_followers():
    pass


def get_cast_likers():
    pass


def get_recasters():
    pass

r = get_casts_from_user("imthedude")
print(r)
res = requests.get("https://client.warpcast.com/v2/user-by-username?username=imthedude")
print(res.json())
