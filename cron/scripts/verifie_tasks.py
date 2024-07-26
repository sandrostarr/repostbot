#проверяем задания на выполнение можно разбить на 3 файла чтоб проверять каждый отдельно
#можно сделать фильтры по заданиям, тогда можно пачкой проверки делать, а не ходить за каждой отдально но это на потом
#а еще я накурился марихуаны и пишу тут книги
from utils.functions import get_action_earning
from warpcast import api
from database import orm_query as q


"""
task_data = {
        'Task.type': "follow",
        'Task.user_id': 2342342,  # "user_id"
        'Task.creator_fid': "creator_fid",
        'Task.cast_hash': "0xHEX",
        'Task.actions_completed': "20",
        'TaskAction.user_fid': 3423,  # "user_fid"

    }
    data = [task_data, task_data]
"""


def process_task(
        session,
        task
):
    reward = get_action_earning(task['Task.type'])

    if task['Task.type'] == 'follow':
        is_verified = api.get_followers(creator_fid=task['creator_fid'], target_fid=task['user_fid'])
    elif task['Task.type'] == 'like':
        is_verified = api.get_cast_likers(cast_hash=task['cast_hash'], fid_task_creator=task['creator_fid'],
                               fid_liker=task['user_fid'])
    elif task['Task.type'] == 'recast':
        is_verified = api.get_cast_recasters(cast_hash=task['cast_hash'], fid_task_creator=task['creator_fid'],
                                  fid_recaster=task['user_fid'])
    else:
        return

    if is_verified:
        complete_task(session, task, reward)
    else:
        rollback_task(session, task, reward)


def complete_task(session, task, reward):
    q.orm_verify_task_action(session, task_action=task['task_action'])
    q.orm_write_off_user_freeze_balance(session=session, fid=task['TaskAction.user_fid'], balance_change=reward)
    q.orm_top_up_user_balance_tg_ig(session=session, telegram_id=task['Task.user_id'], balance_change=reward)


def rollback_task(session, task, reward):
    q.orm_write_off_user_freeze_balance(session=session, fid=task['TaskAction.user_fid'], balance_change=reward)
    q.decrease_task_actions_completed_count(session=session,task=Task)
    q.orm_remove_complete_task_action(session=session, task_action=task['task_action'])


def process_tasks(data):
    for task in data:
        process_task(session, task)

