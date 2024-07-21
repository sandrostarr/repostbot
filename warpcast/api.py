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
        cursor: str = '',
        limit: int = 100,
):
    fid = get_fid_from_username(username)
    param = f"followers?cursor={cursor}&fid={fid}&limit={limit}"
    try:
        response = requests.get(warp_api + param)
        followers = response.json()
        followers_ids = [follower['fid'] for follower in followers['result']['users']]

        try:
            cursor = (followers['next']['cursor'])
        except:
            cursor = None

        return followers_ids, cursor
    except:
        return None


def get_cast_likers(
        cast_hash: str,
        cursor: str = '',
        limit: int = 100,
):
    param = f"cast-likes?cursor={cursor}&castHash={cast_hash}&limit={limit}"
    try:
        response = requests.get(warp_api + param)
        likers = response.json()
        likers_fids = [like['reactor']['fid'] for like in likers['result']['likes']]

        try:
            cursor = (likers['next']['cursor'])
        except:
            cursor = None

        return likers_fids, cursor
    except:
        return None


def get_cast_recasters(
        cast_hash: str,
        cursor: str = '',
        limit: int = 100,
):
    param = f"cast-recasters?cursor={cursor}&castHash={cast_hash}&limit={limit}"
    try:
        response = requests.get(warp_api + param)
        recasters = response.json()
        recasters_fids = [user['fid'] for user in recasters['result']['users']]

        try:
            cursor = (recasters['next']['cursor'])
        except:
            cursor = None

        return recasters_fids, cursor
    except:
        return None
