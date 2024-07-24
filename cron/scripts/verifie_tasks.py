#проверяем задания на выполнение
from warpcast import api

def checker():
    tasks_is_completed = [
        {"task_type": 'FOLLOW',
         "url": '0x0nion'}
    ]

    for item in tasks_is_completed:
        task_type = item.get("task_type")
        url = item.get("url")
        if task_type == "FOLLOW":
            followers_count = api.get_followers_number(url)
            follower_ids, cursor = api.get_followers(username=url)

            new_lis, cursor = api.get_followers(username=url, cursor=cursor)

            new_lis_2, cursor = api.get_followers(username=url, cursor=cursor)

            print(follower_ids)
            print(len(follower_ids))
            print(new_lis)
            print(len(new_lis))
            print(new_lis_2)
            print(len(new_lis_2))

checker()


