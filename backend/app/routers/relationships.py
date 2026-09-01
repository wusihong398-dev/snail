from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import (
    select,
    or_
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models.user import User
from app.models.relationship import UserRelationship

from app.schemas.relationship import (
    RelationshipResponse,
    RelationshipActionRequest
)

from app.services.system_settings import (
    get_setting_int
)


router = APIRouter(
    prefix="/relationships",
    tags=["恋爱关系"]
)


def normalize_pair(
    user_id_1: int,
    user_id_2: int
) -> tuple[int, int]:

    if user_id_1 < user_id_2:
        return (
            user_id_1,
            user_id_2
        )

    return (
        user_id_2,
        user_id_1
    )


async def get_users_or_fail(
    db: AsyncSession,
    user_id_a: int,
    user_id_b: int
):

    if user_id_a == user_id_b:

        raise HTTPException(
            status_code=400,
            detail="不能和自己建立关系"
        )

    user_a = await db.get(
        User,
        user_id_a
    )

    user_b = await db.get(
        User,
        user_id_b
    )

    if user_a is None:

        raise HTTPException(
            status_code=404,
            detail="用户A不存在"
        )

    if user_b is None:

        raise HTTPException(
            status_code=404,
            detail="用户B不存在"
        )

    return (
        user_a,
        user_b
    )


async def get_relationship_or_fail(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
):

    user_id_a, user_id_b = normalize_pair(
        user_id_1,
        user_id_2
    )

    result = await db.execute(
        select(UserRelationship)
        .where(
            UserRelationship.user_id_a
            == user_id_a,

            UserRelationship.user_id_b
            == user_id_b
        )
    )

    relationship = (
        result.scalar_one_or_none()
    )

    if relationship is None:

        raise HTTPException(
            status_code=404,
            detail="双方尚未建立亲密度关系"
        )

    return relationship


@router.get(
    "",
    response_model=list[RelationshipResponse]
)
async def list_relationships(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(UserRelationship)
        .order_by(
            UserRelationship.intimacy.desc(),
            UserRelationship.id.asc()
        )
    )

    return result.scalars().all()


@router.get(
    "/ranking",
    response_model=list[RelationshipResponse]
)
async def intimacy_ranking(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(UserRelationship)
        .order_by(
            UserRelationship.intimacy.desc(),
            UserRelationship.id.asc()
        )
        .limit(100)
    )

    return result.scalars().all()


@router.get(
    "/user/{user_id}",
    response_model=list[RelationshipResponse]
)
async def user_relationships(
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

    result = await db.execute(
        select(UserRelationship)
        .where(
            or_(
                UserRelationship.user_id_a
                == user_id,

                UserRelationship.user_id_b
                == user_id
            )
        )
        .order_by(
            UserRelationship.intimacy.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/pair/{user_id_1}/{user_id_2}",
    response_model=RelationshipResponse
)
async def get_pair_relationship(
    user_id_1: int,
    user_id_2: int,
    db: AsyncSession = Depends(get_db)
):

    return await get_relationship_or_fail(
        db,
        user_id_1,
        user_id_2
    )


@router.post(
    "/love",
    response_model=RelationshipResponse
)
async def set_love(
    data: RelationshipActionRequest,
    db: AsyncSession = Depends(get_db)
):

    await get_users_or_fail(
        db,
        data.user_id_a,
        data.user_id_b
    )

    relationship = (
        await get_relationship_or_fail(
            db,
            data.user_id_a,
            data.user_id_b
        )
    )

    love_threshold = await get_setting_int(
        db,
        "love_intimacy_threshold",
        100
    )

    if relationship.intimacy < love_threshold:

        raise HTTPException(
            status_code=400,
            detail=(
                f"亲密度不足{love_threshold}，"
                "暂时不能确定恋爱关系"
            )
        )

    relationship.relationship_status = "love"

    relationship.love_started_at = (
        datetime.now(
            timezone.utc
        )
    )

    relationship.married_at = None

    await db.commit()

    await db.refresh(
        relationship
    )

    return relationship


@router.post(
    "/marry",
    response_model=RelationshipResponse
)
async def set_married(
    data: RelationshipActionRequest,
    db: AsyncSession = Depends(get_db)
):

    await get_users_or_fail(
        db,
        data.user_id_a,
        data.user_id_b
    )

    relationship = (
        await get_relationship_or_fail(
            db,
            data.user_id_a,
            data.user_id_b
        )
    )

    if (
        relationship.relationship_status
        != "love"
    ):

        raise HTTPException(
            status_code=400,
            detail="双方需要先建立恋爱关系"
        )

    marriage_threshold = await get_setting_int(
        db,
        "marriage_intimacy_threshold",
        500
    )

    if relationship.intimacy < marriage_threshold:

        raise HTTPException(
            status_code=400,
            detail=(
                f"亲密度不足{marriage_threshold}，"
                "暂时不能结婚"
            )
        )

    relationship.relationship_status = "married"

    relationship.married_at = (
        datetime.now(
            timezone.utc
        )
    )

    await db.commit()

    await db.refresh(
        relationship
    )

    return relationship


@router.post(
    "/reset",
    response_model=RelationshipResponse
)
async def reset_relationship(
    data: RelationshipActionRequest,
    db: AsyncSession = Depends(get_db)
):

    relationship = (
        await get_relationship_or_fail(
            db,
            data.user_id_a,
            data.user_id_b
        )
    )

    relationship.relationship_status = "normal"

    relationship.love_started_at = None
    relationship.married_at = None

    await db.commit()

    await db.refresh(
        relationship
    )

    return relationship
