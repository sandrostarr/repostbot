import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import find_dotenv, load_dotenv

from database.models import TaskAction, Task

load_dotenv(find_dotenv())

from database.engine import get_session
from utils.functions import get_action_earning
from warpcast import api
from database import orm_query as q


async def process_task_action(
        session: AsyncSession,
        task_action: TaskAction,
        task: Task,
):
    reward = get_action_earning(task.type)

    if task.type == 'FOLLOW':
        is_verified = api.get_followers(creator_fid=task.creator_fid, target_fid=task_action.user_fid)
    elif task.type == 'LIKE':
        is_verified = api.get_cast_likers(cast_hash=task.cast_hash, fid_task_creator=task.creator_fid,
                                          fid_liker=task_action.user_fid)
    elif task.type == 'RECAST':
        is_verified = api.get_cast_recasters(cast_hash=task.cast_hash, fid_task_creator=task.creator_fid,
                                             fid_recaster=task_action.user_fid)
    else:
        return

    if is_verified:
        await complete_task(session=session, task_action=task_action, reward=reward)
    else:
        await rollback_task(session=session, task=task, task_action=task_action, reward=reward)


async def complete_task(session: AsyncSession, task_action: TaskAction, reward: int):
    await q.orm_verify_task_action(session=session, task_action=task_action)
    await q.orm_write_off_user_freeze_balance(
        session=session,
        telegram_id=task_action.telegram_id,
        balance_change=reward,
    )
    await q.orm_top_up_user_balance_by_tg_id(
        session=session,
        telegram_id=task_action.telegram_id,
        balance_change=reward,
    )


async def rollback_task(session: AsyncSession, task: Task, task_action: TaskAction, reward: int):
    await q.orm_write_off_user_freeze_balance(
        session=session,
        telegram_id=task_action.telegram_id,
        balance_change=reward,
    )
    await q.orm_decrease_task_actions_completed_count(session=session, task=task)
    await q.orm_remove_complete_task_action(session=session, task_action=task_action)


async def process_tasks(session: AsyncSession, task_actions: list, tasks: dict):
    for task_action in task_actions:
        await process_task_action(session=session, task_action=task_action, task=tasks[task_action.task_id])


async def main():
    session = await get_session()
    task_actions = await q.orm_get_task_actions_for_verification(session=session)

    if len(task_actions) == 0:
        print('Нет заданий для проверки')
    else:
        task_ids = [task_action.task_id for task_action in task_actions]
        tasks = await q.orm_get_tasks_by_id(session=session, task_ids=task_ids)
        ordered_tasks = {}
        for task in tasks:
            ordered_tasks[task.id] = task

        await process_tasks(session=session, task_actions=task_actions, tasks=ordered_tasks)


asyncio.run(main())
