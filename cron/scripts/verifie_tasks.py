#проверяем задания на выполнение
from warpcast import api
from database import orm_query as q


def check_all_tasks(
    session,
    task_action,

):
    data = [] # запрос заданий из БД которые не верифицированы
    for task in data:
        if task['task_type']=='follow':
            if api.get_followers(creator_fid=task['creator_fid'], target_fid=task['user_fid']):
                q.orm_verify_task_action(session,task_action) #не понимаю как сюда передать session
                return True
            else:
                return False
        elif task['task_type']=='like':
            if api.get_cast_likers(cast_hash=task['cast_hash'], fid_task_creator=task['creator_fid'], fid_liker=task['user_fid']):
                q.orm_verify_task_action(session,task_action)  # не понимаю как сюда передать session
                return True
            else:
                return False
        elif task['task_type']=='recast':
            if api.get_cast_recasters(cast_hash=task['cast_hash'], fid_task_creator=task['creator_fid'], fid_recaster=task['user_fid']):
                q.orm_verify_task_action(session,task_action)  # не понимаю как сюда передать session
                return True
            else:
                return False
