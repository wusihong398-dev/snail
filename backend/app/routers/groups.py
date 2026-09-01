from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.group import Group
from app.schemas.groups import (
    GroupCreate,
    GroupUpdate,
    GroupResponse
)


router = APIRouter(
    prefix="/groups",
    tags=["微信群管理"]
)


def serialize_group(
    group: Group
) -> dict:

    return {
        "id": group.id,

        "name":
            group.group_name,

        "group_id":
            group.wx_group_id,

        "robot_id":
            group.robot_id,

        "ai_enabled":
            bool(group.enable_ai),

        "game_enabled":
            bool(group.enable_game),

        "social_enabled":
            bool(group.enable_social),

        "love_enabled":
            bool(group.enable_love),

        "marriage_enabled":
            bool(group.enable_marriage),

        "baby_enabled":
            bool(group.enable_baby),

        "welcome_enabled":
            bool(group.welcome_enabled),

        "welcome_text":
            group.welcome_text,

        "system_prompt":
            group.system_prompt
    }


@router.get(
    "",
    response_model=list[GroupResponse]
)
async def list_groups(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Group).order_by(
            Group.id.asc()
        )
    )

    groups = result.scalars().all()

    return [
        serialize_group(group)
        for group in groups
    ]


@router.get(
    "/{group_id}",
    response_model=GroupResponse
)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):

    group = await db.get(
        Group,
        group_id
    )

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="微信群不存在"
        )

    return serialize_group(group)


@router.post(
    "",
    response_model=GroupResponse
)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db)
):

    if data.group_id:

        result = await db.execute(
            select(Group).where(
                Group.wx_group_id
                == data.group_id
            )
        )

        if result.scalar_one_or_none():

            raise HTTPException(
                status_code=409,
                detail="该微信群已经存在"
            )

    group = Group(

        group_name=data.name,

        wx_group_id=(
            data.group_id
            or None
        ),

        robot_id=data.robot_id,

        enable_ai=data.ai_enabled,

        enable_game=data.game_enabled,

        enable_social=data.social_enabled,

        enable_love=data.love_enabled,

        enable_marriage=data.marriage_enabled,

        enable_baby=data.baby_enabled,

        welcome_enabled=
            data.welcome_enabled,

        welcome_text=
            data.welcome_text,

        system_prompt=
            data.system_prompt
    )

    db.add(group)

    try:

        await db.commit()

    except IntegrityError:

        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="保存失败，微信群ID可能重复"
        )

    await db.refresh(group)

    return serialize_group(group)


@router.put(
    "/{group_id}",
    response_model=GroupResponse
)
async def update_group(
    group_id: int,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db)
):

    group = await db.get(
        Group,
        group_id
    )

    if group is None:

        raise HTTPException(
            status_code=404,
            detail="微信群不存在"
        )

    if data.name is not None:
        group.group_name = data.name

    if data.group_id is not None:
        group.wx_group_id = (
            data.group_id or None
        )

    if data.robot_id is not None:
        group.robot_id = data.robot_id

    if data.ai_enabled is not None:
        group.enable_ai = data.ai_enabled

    if data.game_enabled is not None:
        group.enable_game = data.game_enabled

    if data.social_enabled is not None:
        group.enable_social = data.social_enabled

    if data.love_enabled is not None:
        group.enable_love = data.love_enabled

    if data.marriage_enabled is not None:
        group.enable_marriage = data.marriage_enabled

    if data.baby_enabled is not None:
        group.enable_baby = data.baby_enabled

    if data.welcome_enabled is not None:
        group.welcome_enabled = (
            data.welcome_enabled
        )

    if data.welcome_text is not None:
        group.welcome_text = (
            data.welcome_text
        )

    if data.system_prompt is not None:
        group.system_prompt = (
            data.system_prompt
        )

    try:

        await db.commit()

    except IntegrityError:

        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="修改失败，微信群ID可能重复"
        )

    await db.refresh(group)

    return serialize_group(group)


@router.delete(
    "/{group_id}"
)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):

    group = await db.get(
        Group,
        group_id
    )

    if group is None:

        raise HTTPException(
            status_code=404,
            detail="微信群不存在"
        )

    await db.delete(group)
    await db.commit()

    return {
        "success": True,
        "message": "微信群已删除"
    }
