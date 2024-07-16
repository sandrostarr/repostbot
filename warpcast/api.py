import requests
from requests.exceptions import Timeout, ConnectionError

warp_api = "https://client.warpcast.com/v2/"


def get_fid_from_username(
        username: str,

):
    param = f"user-by-username?username={username}"
    try:
        response = requests.get(warp_api + param)
        fid = response.json()['result']['user']['fid']

        return fid
    except:
        return None


def get_cast_hash(
        username: str,
        hash_prefix: str,
):
    param = f"user-cast?username={username}&hashPrefix={hash_prefix}"
    try:
        response = requests.get(warp_api + param)
        cast_hash = response.json()['result']['cast']['hash']
        return cast_hash
    except:
        return None


def get_casts_from_user(
        username: str,
):
    try:
        fid = get_fid_from_username(username=username)
        param = f"profile-casts?fid={fid}"

        response = requests.get(warp_api + param)

        hash_list = [cast['hash'] for cast in response.json()['result']['casts']]
        return hash_list
    except:
        return None


def get_followers(
        username: str,
):
    fid = get_fid_from_username(username)
    param = f"followers?fid={fid}"
    try:
        response = requests.get(warp_api + param)
        followers = response.json()

        return followers
    except:
        return None


def get_cast_likers(
        cast_hash: str,
):
    param = f"cast-likes?castHash={cast_hash}"
    try:
        response = requests.get(warp_api + param)
        likers = response.json()
        likers_fids = [like['reactor']['fid'] for like in likers['result']['likes']]
        return likers_fids
    except:
        return None


def get_recasters(
        cast_hash: str,
):
    param = f"cast-recasters?castHash={cast_hash}"
    try:
        response = requests.get(warp_api + param)
        recasters = response.json()

        recasters_fids = [user['fid'] for user in recasters['result']['users']]
        return recasters_fids
    except:
        return None



