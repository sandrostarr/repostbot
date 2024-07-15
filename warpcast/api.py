import requests
from requests.exceptions import Timeout, ConnectionError

warp_api = "https://client.warpcast.com/v2/"

def get_fid_from_username(
        username: str,

):
    param = f"user-by-username?username={username}"
    try:
        response = requests.get(warp_api+param)
        fid = response.json()['result']['user']['fid']

        return fid
    except:
        return None


def get_casts_from_user(
        username: str,
):
    try:
        fid = get_fid_from_username(username=username)
        param = f"profile-casts?fid={fid}"

        response = requests.get(warp_api+param)

        hash_list = [cast['hash'] for cast in response.json()['result']['casts']]
        print(hash_list)
        return hash_list
    except:
        return None




def get_followers():
    pass


def get_cast_likers():
    pass


def get_recasters():
    pass




get_casts_from_user("kokos-crypto")
