import time

import requests
from requests.exceptions import Timeout, ConnectionError

warp_api = "https://client.warpcast.com/v2/"
warp_api_node = "http://84.247.186.17:2281/v1/"


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



#исправлено
def get_casts_from_user(
        username: str,
):
    try:
        fid = get_fid_from_username(username=username)
        # param = f"profile-casts?fid={fid}"
        #
        # response = requests.get(warp_api + param)
        #
        # hash_list = [cast['hash'] for cast in response.json()['result']['casts']]

        param = f"castsByFid?fid={fid}"
        response = requests.get(warp_api_node + param)
        cast_list = response.json()
        hash_list = [message['hash'] for message in cast_list['messages']]
        return hash_list
    except:
        return None

# print(get_casts_from_user("0x0nion"))

#исправлено
def get_cast_hash(
        username: str,
        hash_prefix: str,
):
    try:
        hash_list = get_casts_from_user(username=username)
        cast_hash_list = [address for address in hash_list if address.startswith(hash_prefix)]
        cast_hash = ''.join(cast_hash_list)
        return cast_hash
    except:
        return None
    # param = f"user-cast?username={username}&hashPrefix={hash_prefix}"
    # try:
    #     response = requests.get(warp_api + param)
    #     cast_hash = response.json()['result']['cast']['hash']
    #     return cast_hash
    # except:
    #     return None


#исправлено
def get_followers(
        username: str = '',
        creator_fid: int = 0
):
    fid = get_fid_from_username(username)
    param = f"linksByTargetFid?target_fid={fid}"
    try:
        response = requests.get(warp_api_node + param)
        followers = response.json()
        followers_ids = [message['data']['fid'] for message in followers['messages']]
        return followers_ids
    except:
        return None

#исправил сразу проверяет есть ли лайк от пользователя или нет
def get_cast_likers(
        cast_hash: str,
        fid_task_creator: int,
        fid_liker: int,


):

    try:
        param = f"reactionById?fid={fid_liker}&reaction_type=1&target_fid={fid_task_creator}&target_hash={cast_hash}"
        response = requests.get(warp_api_node + param)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        print("None")
        return None

    #cтарый код
    # param = f"cast-likes?cursor={cursor}&castHash={cast_hash}&limit={limit}"
    # try:
    #     response = requests.get(warp_api + param)
    #     likers = response.json()
    #     likers_fids = [like['reactor']['fid'] for like in likers['result']['likes']]
    #
    #     try:
    #         cursor = (likers['next']['cursor'])
    #     except:
    #         cursor = None
    #
    #     return likers_fids, cursor
    # except:
    #     return None

#рекасты появляются почти сразу проверил создал пост и проверку в течении 1 минуты все работает
def get_cast_recasters(
        cast_hash: str,
        fid_task_creator: int,
        fid_recaster: int,

):
    try:
        param = f"reactionById?fid={fid_recaster}&reaction_type=2&target_fid={fid_task_creator}&target_hash={cast_hash}"
        response = requests.get(warp_api_node + param)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        print("None")
        return None
    #
    # param = f"cast-recasters?cursor={cursor}&castHash={cast_hash}&limit={limit}"
    # try:
    #     response = requests.get(warp_api + param)
    #     recasters = response.json()
    #     recasters_fids = [user['fid'] for user in recasters['result']['users']]
    #     try:
    #         cursor = (recasters['next']['cursor'])
    #     except:
    #         cursor = None
    #
    #     return recasters_fids, cursor
    # except:
    #     return None

