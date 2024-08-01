import logging

import requests
from requests.exceptions import Timeout, ConnectionError

warp_api = "https://client.warpcast.com/v2/"

# warp_api_node = "http://84.247.186.17:2281/v1/"
# warp_api_node_1 = "http://176.57.150.251:2281/v1/"

nodes = {
    "http://84.247.186.17:2281/v1/",
    "http://176.57.150.251:2281/v1/"
}


def check_connection():
    for warp_api_node in nodes:
        try:
            param = f"info?dbstats=1"
            response = requests.get(warp_api_node + param)
            if response.status_code == 200:
                return warp_api_node
        except:
            logging.warning(f"200 - {response}")


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
        hash_list: list,
        hash_prefix: str,
):
    try:
        cast_hash_list = [cast_hash for cast_hash in hash_list if cast_hash.startswith(hash_prefix)]
        cast_hash = ''.join(cast_hash_list)
        return cast_hash
    except:
        return None


# исправлено

def get_casts_from_user(
        username: str,
        hash_prefix: str = '',
):
    try:
        try:
            fid = get_fid_from_username(username=username)
        except:
            logging.warning("get_fid_from_username - не работает")
            return None

        param = f"castsByFid?fid={fid}&pageSize=1000"
        hash_list = []
        warp_api_node = check_connection()
        while True:
            response = requests.get(warp_api_node + param)
            if response.status_code != 200:
                logging.warning(f"200 - {response}")
                return None

            cast_list = response.json()

            hash_list.extend(message['hash'] for message in cast_list['messages'])

            if hash_prefix:
                cast_hash = get_cast_hash(hash_list=hash_list, hash_prefix=hash_prefix)
                if cast_hash:
                    return cast_hash

            page_token = cast_list['nextPageToken']
            if not page_token:
                break
            param = f"castsByFid?fid={fid}&pageSize=1000&pageToken={page_token}"
        return hash_list
    except:
        logging.warning("get_casts_from_user - не работает")
        return None


# print(get_casts_from_user("0x0nion"))
# print(get_casts_from_user(username="kevinmfer",hash_prefix='0x2dea8f8'))


#исправлено
def get_followers(
        username: str | None = None,
        creator_fid: int | None = None,
        target_fid: int | None = None,
):
    if creator_fid is None:
        try:
            creator_fid = get_fid_from_username(username=username)
        except:
            logging.warning("get_fid_from_username - не работает")
            return None

    param = f"linkById?fid={target_fid}&target_fid={creator_fid}&link_type=follow"

    warp_api_node = check_connection()

    response = requests.get(warp_api_node + param)
    if response.status_code != 200:
        logging.warning(f"{response}")
        return False
    elif response.status_code == 200:
        return True

# get_followers(creator_fid=5650, target_fid=655208)


#исправил сразу проверяет есть ли лайк от пользователя или нет
def get_cast_likers(
        cast_hash: str,
        fid_task_creator: int | str,
        fid_liker: int | str,

):
    warp_api_node = check_connection()
    try:
        param = f"reactionsByFid?fid={fid_liker}&reaction_type=1"
        while True:
            response = requests.get(warp_api_node + param)
            if response.status_code != 200:
                logging.warning(f"200 - {response}")
                return None
            likers_json = response.json()
            for message in likers_json['messages']:
                if cast_hash == message['data']['reactionBody']['targetCastId']['hash']:
                    fid = message['data']['reactionBody']['targetCastId']['fid']
                    if str(fid) == str(fid_task_creator):
                        return True
            page_token = likers_json['nextPageToken']
            if not page_token:
                break
            param = f"reactionsByFid?fid={fid_liker}&reaction_type=1&pageSize=1000&pageToken={page_token}"
    except:
        return None


#рекасты появляются почти сразу проверил создал пост и проверку в течении 1 минуты все работает
def get_cast_recasters(
        cast_hash: str,
        fid_task_creator: int,
        fid_recaster: int,

):
    warp_api_node = check_connection()
    try:
        param = f"reactionsByFid?fid={fid_recaster}&reaction_type=2"
        while True:
            response = requests.get(warp_api_node + param)
            if response.status_code != 200:
                logging.warning(f"200 - {response}")
                return None

            likers_json = response.json()

            for message in likers_json['messages']:
                if cast_hash == message['data']['reactionBody']['targetCastId']['hash']:
                    fid = message['data']['reactionBody']['targetCastId']['fid']
                    if str(fid) == str(fid_task_creator):
                        return True

            page_token = likers_json['nextPageToken']
            print(f" page = {page_token}")
            if not page_token:
                break
            param = f"reactionsByFid?fid={fid_recaster}&reaction_type=2&pageSize=1000&pageToken={page_token}"
    except:
        return None
