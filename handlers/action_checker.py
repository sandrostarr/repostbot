from warpcast import api


async def check_like_existence(cast_hash: str, fid: int, cursor: str = ''):
    likers_fids, cursor = api.get_cast_likers(cast_hash=cast_hash, cursor=cursor)

    if fid in likers_fids:
        return True
    else:
        if cursor is not None:
            return await check_like_existence(cast_hash=cast_hash, fid=fid, cursor=cursor)
        else:
            return False


async def check_recast_existence(cast_hash: str, fid: int, cursor: str = ''):
    recasters_fids, cursor = api.get_cast_recasters(cast_hash=cast_hash, cursor=cursor)

    if fid in recasters_fids:
        return True
    else:
        if cursor is not None:
            return await check_recast_existence(cast_hash=cast_hash, fid=fid, cursor=cursor)
        else:
            return False


async def check_follow_existence(cast_hash, fid):
    return False
    # likers_fids = api.get_cast_likers(cast_hash=cast_hash)
    # if fid in likers_fids:
    #     return True
    # else:
    #     return False
