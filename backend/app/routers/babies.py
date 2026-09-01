from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import (
    select,
    or_,
    and_
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models.user import User
from app.models.relationship import UserRelationship
from app.models.baby import (
    Baby,
    BabyRequest
)

from app.schemas.baby import (
    BabyRequestCreate,
    BabyRequestHandle,
    BabyRequestResponse,
    BabyResponse
)

from app.services.system_settings import (
    get_setting_int
)
from app.services.entitlements import get_entitlement_quantity


router = APIRouter(
    prefix="/babies",
    tags=["宝宝系统"]
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
) -> User:

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


def get_effective_member_level(
    user: User
) -> str:

    level = str(
        user.member_level
        or "normal"
    ).lower()


    if level not in {
        "normal",
        "vip",
        "svip"
    }:
        return "normal"


    if level in {
        "vip",
        "svip"
    }:

        expire_at = (
            user.member_expire_at
        )

        if expire_at is not None:

            now = datetime.now(
                timezone.utc
            )

            if expire_at <= now:
                return "normal"


    return level


async def get_children_per_couple_limit(
    db: AsyncSession,
    user: User
) -> int:

    level = get_effective_member_level(user)

    if level == "svip":
        base = await get_setting_int(db, "svip_max_children_per_couple", 3)
    elif level == "vip":
        base = await get_setting_int(db, "vip_max_children_per_couple", 2)
    else:
        base = await get_setting_int(db, "normal_max_children_per_couple", 1)

    extra = await get_entitlement_quantity(db, user.id, "extra_baby_slots")
    return max(0, int(base)) + max(0, int(extra))


async def get_children_total_limit(
    db: AsyncSession,
    user: User
) -> int:

    level = get_effective_member_level(user)

    if level == "svip":
        base = await get_setting_int(db, "svip_max_children_total", 6)
    elif level == "vip":
        base = await get_setting_int(db, "vip_max_children_total", 4)
    else:
        base = await get_setting_int(db, "normal_max_children_total", 1)

    extra = await get_entitlement_quantity(db, user.id, "extra_baby_slots")
    return max(0, int(base)) + max(0, int(extra))


async def get_married_relationship_or_fail(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
) -> UserRelationship:

    user_id_a, user_id_b = (
        normalize_pair(
            user_id_1,
            user_id_2
        )
    )


    result = await db.execute(
        select(UserRelationship)
        .where(
            UserRelationship.user_id_a
            == user_id_a,

            UserRelationship.user_id_b
            == user_id_b,

            UserRelationship.relationship_status
            == "married"
        )
    )


    relationship = (
        result.scalar_one_or_none()
    )


    if relationship is None:

        raise HTTPException(
            status_code=400,
            detail="双方必须先建立婚姻关系"
        )


    return relationship


async def count_pair_children(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
) -> int:

    user_id_a, user_id_b = (
        normalize_pair(
            user_id_1,
            user_id_2
        )
    )


    result = await db.execute(
        select(Baby)
        .where(
            Baby.parent_user_id_a
            == user_id_a,

            Baby.parent_user_id_b
            == user_id_b
        )
    )


    return len(
        result.scalars().all()
    )


async def count_user_children(
    db: AsyncSession,
    user_id: int
) -> int:

    result = await db.execute(
        select(Baby)
        .where(
            or_(
                Baby.parent_user_id_a
                == user_id,

                Baby.parent_user_id_b
                == user_id
            )
        )
    )


    return len(
        result.scalars().all()
    )


async def ensure_baby_capacity(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
):

    user_1 = await get_user_or_fail(
        db,
        user_id_1
    )

    user_2 = await get_user_or_fail(
        db,
        user_id_2
    )


    user_1_pair_limit = (
        await get_children_per_couple_limit(
            db,
            user_1
        )
    )

    user_2_pair_limit = (
        await get_children_per_couple_limit(
            db,
            user_2
        )
    )


    actual_pair_limit = min(
        user_1_pair_limit,
        user_2_pair_limit
    )


    current_pair_children = (
        await count_pair_children(
            db,
            user_id_1,
            user_id_2
        )
    )


    if (
        current_pair_children
        >= actual_pair_limit
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"这对伴侣当前已有"
                f"{current_pair_children}个宝宝，"
                f"当前会员组合最多允许"
                f"{actual_pair_limit}个宝宝"
            )
        )


    user_1_total_limit = (
        await get_children_total_limit(
            db,
            user_1
        )
    )

    user_2_total_limit = (
        await get_children_total_limit(
            db,
            user_2
        )
    )


    user_1_total = (
        await count_user_children(
            db,
            user_id_1
        )
    )

    user_2_total = (
        await count_user_children(
            db,
            user_id_2
        )
    )


    if (
        user_1_total
        >= user_1_total_limit
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"用户#{user_id_1}当前已有"
                f"{user_1_total}个宝宝，"
                f"其会员等级最多允许"
                f"{user_1_total_limit}个宝宝"
            )
        )


    if (
        user_2_total
        >= user_2_total_limit
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                f"用户#{user_id_2}当前已有"
                f"{user_2_total}个宝宝，"
                f"其会员等级最多允许"
                f"{user_2_total_limit}个宝宝"
            )
        )


async def ensure_no_pending_request(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
):

    result = await db.execute(
        select(BabyRequest)
        .where(
            BabyRequest.status
            == "pending",

            or_(
                and_(
                    BabyRequest.sender_user_id
                    == user_id_1,

                    BabyRequest.receiver_user_id
                    == user_id_2
                ),

                and_(
                    BabyRequest.sender_user_id
                    == user_id_2,

                    BabyRequest.receiver_user_id
                    == user_id_1
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
            detail="双方已有待处理的宝宝申请"
        )


@router.get(
    "",
    response_model=list[BabyResponse]
)
async def list_babies(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Baby)
        .order_by(
            Baby.id.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/user/{user_id}",
    response_model=list[BabyResponse]
)
async def list_user_babies(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    await get_user_or_fail(
        db,
        user_id
    )


    result = await db.execute(
        select(Baby)
        .where(
            or_(
                Baby.parent_user_id_a
                == user_id,

                Baby.parent_user_id_b
                == user_id
            )
        )
        .order_by(
            Baby.id.desc()
        )
    )


    return result.scalars().all()


@router.get(
    "/requests",
    response_model=list[BabyRequestResponse]
)
async def list_baby_requests(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(BabyRequest)
        .order_by(
            BabyRequest.id.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/requests/user/{user_id}",
    response_model=list[BabyRequestResponse]
)
async def list_user_baby_requests(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    await get_user_or_fail(
        db,
        user_id
    )


    result = await db.execute(
        select(BabyRequest)
        .where(
            or_(
                BabyRequest.sender_user_id
                == user_id,

                BabyRequest.receiver_user_id
                == user_id
            )
        )
        .order_by(
            BabyRequest.id.desc()
        )
    )


    return result.scalars().all()


@router.post(
    "/requests",
    response_model=BabyRequestResponse
)
async def create_baby_request(
    data: BabyRequestCreate,
    db: AsyncSession = Depends(get_db)
):

    if (
        data.sender_user_id
        == data.receiver_user_id
    ):

        raise HTTPException(
            status_code=400,
            detail="不能和自己创建宝宝"
        )


    await get_user_or_fail(
        db,
        data.sender_user_id
    )

    await get_user_or_fail(
        db,
        data.receiver_user_id
    )


    await get_married_relationship_or_fail(
        db,
        data.sender_user_id,
        data.receiver_user_id
    )


    await ensure_baby_capacity(
        db,
        data.sender_user_id,
        data.receiver_user_id
    )


    await ensure_no_pending_request(
        db,
        data.sender_user_id,
        data.receiver_user_id
    )


    baby_name = (
        data.baby_name.strip()
        if data.baby_name
        else None
    )


    if (
        baby_name
        and len(baby_name) > 64
    ):

        raise HTTPException(
            status_code=400,
            detail="宝宝名字不能超过64个字符"
        )


    gender = str(
        data.baby_gender
        or "unknown"
    ).lower()


    if gender not in {
        "male",
        "female",
        "unknown"
    }:

        raise HTTPException(
            status_code=400,
            detail="宝宝性别参数不正确"
        )


    request = BabyRequest(

        sender_user_id=
            data.sender_user_id,

        receiver_user_id=
            data.receiver_user_id,

        status=
            "pending",

        baby_name=
            baby_name,

        baby_gender=
            gender,

        message=
            data.message
    )


    db.add(
        request
    )

    await db.commit()

    await db.refresh(
        request
    )


    return request


@router.post(
    "/requests/{request_id}/accept",
    response_model=BabyResponse
)
async def accept_baby_request(
    request_id: int,
    data: BabyRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    request = await db.get(
        BabyRequest,
        request_id
    )


    if request is None:

        raise HTTPException(
            status_code=404,
            detail="宝宝申请不存在"
        )


    if (
        request.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="宝宝申请已经处理"
        )


    if (
        data.user_id
        != request.receiver_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有接收方可以接受宝宝申请"
        )


    await get_married_relationship_or_fail(
        db,
        request.sender_user_id,
        request.receiver_user_id
    )


    await ensure_baby_capacity(
        db,
        request.sender_user_id,
        request.receiver_user_id
    )


    user_id_a, user_id_b = (
        normalize_pair(
            request.sender_user_id,
            request.receiver_user_id
        )
    )


    baby_name = (
        request.baby_name
        or f"宝宝{request.id}"
    )


    baby = Baby(

        name=
            baby_name,

        parent_user_id_a=
            user_id_a,

        parent_user_id_b=
            user_id_b,

        gender=
            request.baby_gender
            or "unknown",

        level=
            1,

        experience=
            0,

        happiness=
            100,

        hunger=
            100,

        health=
            100
    )


    db.add(
        baby
    )


    request.status = (
        "accepted"
    )

    request.handled_at = (
        datetime.now(
            timezone.utc
        )
    )


    await db.commit()

    await db.refresh(
        baby
    )


    return baby


@router.post(
    "/requests/{request_id}/reject",
    response_model=BabyRequestResponse
)
async def reject_baby_request(
    request_id: int,
    data: BabyRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    request = await db.get(
        BabyRequest,
        request_id
    )


    if request is None:

        raise HTTPException(
            status_code=404,
            detail="宝宝申请不存在"
        )


    if (
        request.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="宝宝申请已经处理"
        )


    if (
        data.user_id
        != request.receiver_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有接收方可以拒绝宝宝申请"
        )


    request.status = (
        "rejected"
    )

    request.handled_at = (
        datetime.now(
            timezone.utc
        )
    )


    await db.commit()

    await db.refresh(
        request
    )


    return request


@router.post(
    "/requests/{request_id}/cancel",
    response_model=BabyRequestResponse
)
async def cancel_baby_request(
    request_id: int,
    data: BabyRequestHandle,
    db: AsyncSession = Depends(get_db)
):

    request = await db.get(
        BabyRequest,
        request_id
    )


    if request is None:

        raise HTTPException(
            status_code=404,
            detail="宝宝申请不存在"
        )


    if (
        request.status
        != "pending"
    ):

        raise HTTPException(
            status_code=400,
            detail="宝宝申请已经处理"
        )


    if (
        data.user_id
        != request.sender_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="只有发起方可以撤回宝宝申请"
        )


    request.status = (
        "cancelled"
    )

    request.handled_at = (
        datetime.now(
            timezone.utc
        )
    )


    await db.commit()

    await db.refresh(
        request
    )


    return request
