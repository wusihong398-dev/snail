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
from app.models.relationship_request import RelationshipRequest

from app.schemas.relationship_request import (
    RelationshipRequestCreate,
    RelationshipRequestHandle,
    RelationshipRequestResponse
)

from app.services.system_settings import (
    get_setting_int
)
from app.services.entitlements import get_entitlement_quantity


router = APIRouter(
    prefix="/relationship-requests",
    tags=["恋爱与求婚申请"]
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


async def get_user_or_fail(
    db: AsyncSession,
    user_id: int
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

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="用户已被禁用"
        )

    return user


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
        .with_for_update()
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


async def count_active_partners(
    db: AsyncSession,
    user_id: int
) -> int:

    result = await db.execute(
        select(UserRelationship)
        .where(
            or_(
                UserRelationship.user_id_a
                == user_id,

                UserRelationship.user_id_b
                == user_id
            ),

            UserRelationship.relationship_status.in_(
                [
                    "love",
                    "married"
                ]
            )
        )
    )

    relationships = (
        result.scalars().all()
    )

    return len(
        relationships
    )


def get_effective_member_level(
    user: User
) -> str:

    level = str(
        user.member_level
        or "normal"
    ).lower()


    expire_at = (
        user.member_expire_at
    )


    if (
        level in {
            "vip",
            "svip"
        }
        and expire_at is not None
    ):

        now = datetime.now(
            timezone.utc
        )

        if expire_at <= now:

            return "normal"


    if level not in {
        "normal",
        "vip",
        "svip"
    }:

        return "normal"


    return level


async def get_user_partner_limit(
    db: AsyncSession,
    user: User
) -> int:

    level = get_effective_member_level(user)

    if level == "svip":
        base = await get_setting_int(db, "svip_max_partners", 3)
    elif level == "vip":
        base = await get_setting_int(db, "vip_max_partners", 2)
    else:
        base = await get_setting_int(db, "normal_max_partners", 1)

    extra = await get_entitlement_quantity(
        db, user.id, "extra_partner_slots"
    )

    return max(0, int(base)) + max(0, int(extra))


async def ensure_partner_capacity(
    db: AsyncSession,
    user_id: int
):

    user = await get_user_or_fail(
        db,
        user_id
    )


    max_partners = (
        await get_user_partner_limit(
            db,
            user
        )
    )


    current_count = (
        await count_active_partners(
            db,
            user_id
        )
    )


    if (
        current_count
        >= max_partners
    ):

        level = (
            get_effective_member_level(
                user
            )
        )


        level_name = {

            "normal":
                "普通用户",

            "vip":
                "VIP",

            "svip":
                "SVIP"

        }.get(
            level,
            "普通用户"
        )


        raise HTTPException(
            status_code=400,
            detail=(
                f"用户#{user_id}当前为"
                f"{level_name}，"
                f"已有{current_count}个伴侣，"
                f"最多允许{max_partners}个伴侣"
            )
        )


async def ensure_no_pending_request(
    db: AsyncSession,
    sender_user_id: int,
    receiver_user_id: int,
    request_type: str
):

    result = await db.execute(
        select(RelationshipRequest)
        .where(
            RelationshipRequest.request_type
            == request_type,

            RelationshipRequest.status
            == "pending",

            or_(
                (
                    RelationshipRequest.sender_user_id
                    == sender_user_id
                )
                & (
                    RelationshipRequest.receiver_user_id
                    == receiver_user_id
                ),

                (
                    RelationshipRequest.sender_user_id
                    == receiver_user_id
                )
                & (
                    RelationshipRequest.receiver_user_id
                    == sender_user_id
                )
            )
        )
    )

    exists = (
        result.scalar_one_or_none()
    )

    if exists:

        raise HTTPException(
            status_code=409,
            detail="双方已有待处理申请"
        )


@router.get(
    "",
    response_model=list[RelationshipRequestResponse]
)
async def list_requests(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(RelationshipRequest)
        .order_by(
            RelationshipRequest.id.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/user/{user_id}",
    response_model=list[RelationshipRequestResponse]
)
async def list_user_requests(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    await get_user_or_fail(
        db,
        user_id
    )

    result = await db.execute(
        select(RelationshipRequest)
        .where(
            or_(
                RelationshipRequest.sender_user_id
                == user_id,

                RelationshipRequest.receiver_user_id
                == user_id
            )
        )
        .order_by(
            RelationshipRequest.id.desc()
        )
    )

    return result.scalars().all()


@router.post(
    "/love",
    response_model=RelationshipRequestResponse
)
async def create_love_request(
    data: RelationshipRequestCreate,
    db: AsyncSession = Depends(get_db)
):

    if (
        data.sender_user_id
        == data.receiver_user_id
    ):

        raise HTTPException(
            status_code=400,
            detail="不能向自己发起恋爱申请"
        )

    await get_user_or_fail(
        db,
        data.sender_user_id
    )

    await get_user_or_fail(
        db,
        data.receiver_user_id
    )

    relationship = (
        await get_relationship_or_fail(
            db,
            data.sender_user_id,
            data.receiver_user_id
        )
    )

    if (
        relationship.relationship_status
        != "normal"
    ):

        raise HTTPException(
            status_code=400,
            detail="双方当前不是普通关系"
        )

    love_threshold = await get_setting_int(
        db,
        "love_intimacy_threshold",
        100
    )

    if (
        relationship.intimacy
        < love_threshold
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"亲密度不足{love_threshold}，"
                "暂时不能发起恋爱申请"
            )
        )

    await ensure_partner_capacity(
        db,
        data.sender_user_id
    )

    await ensure_partner_capacity(
        db,
        data.receiver_user_id
    )


    await ensure_no_pending_request(
        db,
        data.sender_user_id,
        data.receiver_user_id,
        "love"
    )

    item = RelationshipRequest(

        request_type=
            "love",

        sender_user_id=
            data.sender_user_id,

        receiver_user_id=
            data.receiver_user_id,

        status=
            "pending",

        message=
            data.message
    )

    db.add(
        item
    )

    await db.commit()

    await db.refresh(
        item
    )

    return item


@router.post(
    "/marriage",
    response_model=RelationshipRequestResponse
)
async def create_marriage_request(
    data: RelationshipRequestCreate,
    db: AsyncSession = Depends(get_db)
):

    if (
        data.sender_user_id
        == data.receiver_user_id
    ):

        raise HTTPException(
            status_code=400,
            detail="不能向自己发起求婚申请"
        )

    await get_user_or_fail(
        db,
        data.sender_user_id
    )

    await get_user_or_fail(
        db,
        data.receiver_user_id
    )

    relationship = (
        await get_relationship_or_fail(
            db,
            data.sender_user_id,
            data.receiver_user_id
        )
    )

    if (
        relationship.relationship_status
        != "love"
    ):

        raise HTTPException(
            status_code=400,
            detail="双方必须先处于恋爱关系"
        )

    marriage_threshold = await get_setting_int(
        db,
        "marriage_intimacy_threshold",
        500
    )

    if (
        relationship.intimacy
        < marriage_threshold
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"亲密度不足{marriage_threshold}，"
                "暂时不能发起求婚"
            )
        )

    await ensure_no_pending_request(
        db,
        data.sender_user_id,
        data.receiver_user_id,
        "marriage"
    )

    item = RelationshipRequest(

        request_type=
            "marriage",

        sender_user_id=
            data.sender_user_id,

        receiver_user_id=
            data.receiver_user_id,

        status=
            "pending",

        message=
            data.message
    )

    db.add(
        item
    )

    await db.commit()

    await db.refresh(
        item
    )

    return item


@router.post(
    "/{request_id}/accept",
    response_model=RelationshipRequestResponse
)
async def accept_request(
    request_id: int,
    data: RelationshipRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    item = await db.get(
        RelationshipRequest,
        request_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="申请不存在"
        )

    if (
        item.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="申请已经处理"
        )

    if (
        data.user_id
        != item.receiver_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有接收方可以接受申请"
        )

    relationship = (
        await get_relationship_or_fail(
            db,
            item.sender_user_id,
            item.receiver_user_id
        )
    )

    now = datetime.now(
        timezone.utc
    )

    if (
        item.request_type
        == "love"
    ):

        love_threshold = await get_setting_int(
            db,
            "love_intimacy_threshold",
            100
        )

        if (
            relationship.intimacy
            < love_threshold
        ):

            raise HTTPException(
                status_code=400,
                detail="当前亲密度已低于恋爱门槛"
            )

        if (
            relationship.relationship_status
            != "normal"
        ):

            raise HTTPException(
                status_code=400,
                detail="双方当前关系已发生变化"
            )

        await ensure_partner_capacity(
            db,
            item.sender_user_id
        )

        await ensure_partner_capacity(
            db,
            item.receiver_user_id
        )


        relationship.relationship_status = (
            "love"
        )

        relationship.love_started_at = (
            now
        )

        relationship.married_at = None


    elif (
        item.request_type
        == "marriage"
    ):

        marriage_threshold = await get_setting_int(
            db,
            "marriage_intimacy_threshold",
            500
        )

        if (
            relationship.intimacy
            < marriage_threshold
        ):

            raise HTTPException(
                status_code=400,
                detail="当前亲密度已低于结婚门槛"
            )

        if (
            relationship.relationship_status
            != "love"
        ):

            raise HTTPException(
                status_code=400,
                detail="双方当前已不是恋爱关系"
            )

        relationship.relationship_status = (
            "married"
        )

        relationship.married_at = (
            now
        )


    item.status = (
        "accepted"
    )

    item.handled_at = (
        now
    )

    await db.commit()

    await db.refresh(
        item
    )

    return item


@router.post(
    "/{request_id}/reject",
    response_model=RelationshipRequestResponse
)
async def reject_request(
    request_id: int,
    data: RelationshipRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    item = await db.get(
        RelationshipRequest,
        request_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="申请不存在"
        )

    if (
        item.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="申请已经处理"
        )

    if (
        data.user_id
        != item.receiver_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有接收方可以拒绝申请"
        )

    item.status = (
        "rejected"
    )

    item.handled_at = (
        datetime.now(
            timezone.utc
        )
    )

    await db.commit()

    await db.refresh(
        item
    )

    return item


@router.post(
    "/{request_id}/cancel",
    response_model=RelationshipRequestResponse
)
async def cancel_request(
    request_id: int,
    data: RelationshipRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    item = await db.get(
        RelationshipRequest,
        request_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="申请不存在"
        )

    if (
        item.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="申请已经处理"
        )

    if (
        data.user_id
        != item.sender_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有发起方可以撤回申请"
        )

    item.status = (
        "cancelled"
    )

    item.handled_at = (
        datetime.now(
            timezone.utc
        )
    )

    await db.commit()

    await db.refresh(
        item
    )

    return item
