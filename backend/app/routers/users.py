from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserCoinsUpdate,
    UserExperienceUpdate,
    UserMembershipUpdate,
    UserResponse
)


router = APIRouter(
    prefix="/users",
    tags=["用户管理"]
)


@router.get(
    "",
    response_model=list[UserResponse]
)
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).order_by(
            User.id.asc()
        )
    )

    return result.scalars().all()


@router.post(
    "/create",
    response_model=UserResponse
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(
            User.wx_user_id
            == data.wx_user_id
        )
    )

    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(
        wx_user_id=data.wx_user_id,
        nickname=data.nickname,
        avatar=data.avatar,
        level=1,
        coins=0,
        experience=0,
        is_active=True,
        member_level="normal"
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


@router.get(
    "/id/{user_id}",
    response_model=UserResponse
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    return user


@router.get(
    "/wx/{wx_user_id}",
    response_model=UserResponse
)
async def get_user_by_wxid(
    wx_user_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(
            User.wx_user_id
            == wx_user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    if data.nickname is not None:
        user.nickname = data.nickname

    if data.avatar is not None:
        user.avatar = data.avatar

    if data.level is not None:
        user.level = max(
            1,
            data.level
        )

    if data.coins is not None:
        user.coins = max(
            0,
            data.coins
        )

    if data.experience is not None:
        user.experience = max(
            0,
            data.experience
        )

    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/{user_id}/coins",
    response_model=UserResponse
)
async def change_coins(
    user_id: int,
    data: UserCoinsUpdate,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    user.coins = max(
        0,
        int(user.coins or 0)
        + data.amount
    )

    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/{user_id}/experience",
    response_model=UserResponse
)
async def change_experience(
    user_id: int,
    data: UserExperienceUpdate,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    user.experience = max(
        0,
        int(user.experience or 0)
        + data.amount
    )

    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/{user_id}/membership",
    response_model=UserResponse
)
async def set_membership(
    user_id: int,
    data: UserMembershipUpdate,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    level = data.member_level.lower()

    if level not in {
        "normal",
        "vip",
        "svip"
    }:
        raise HTTPException(
            status_code=400,
            detail="会员等级不正确"
        )

    now = datetime.now(
        timezone.utc
    )

    if level == "normal":

        user.member_level = "normal"
        user.member_started_at = None
        user.member_expire_at = None

    else:

        days = data.days or 30

        if days <= 0:
            raise HTTPException(
                status_code=400,
                detail="会员天数必须大于0"
            )

        current_expire = (
            user.member_expire_at
            if user.member_expire_at
            and user.member_expire_at > now
            else now
        )

        if (
            user.member_level
            == "normal"
            or user.member_started_at
            is None
        ):
            user.member_started_at = now

        user.member_level = level

        user.member_expire_at = (
            current_expire
            + timedelta(days=days)
        )

    await db.commit()
    await db.refresh(user)

    return user


@router.patch(
    "/{user_id}/active",
    response_model=UserResponse
)
async def toggle_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    user.is_active = not bool(
        user.is_active
    )

    await db.commit()
    await db.refresh(user)

    return user


@router.delete(
    "/{user_id}"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    await db.delete(user)
    await db.commit()

    return {
        "success": True,
        "message": "用户已删除"
    }
