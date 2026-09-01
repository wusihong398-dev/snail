from datetime import datetime, timezone
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models.user import User
from app.models.product import ShopProduct
from app.models.order import (
    ShopOrder,
    CoinTransaction
)
from app.models.gift import (
    GiftProduct,
    GiftRecord
)
from app.models.relationship import (
    UserRelationship
)

from app.schemas.gift import (
    GiftProductCreate,
    GiftProductUpdate,
    GiftProductResponse,
    GiftSendRequest,
    GiftRecordResponse
)

from app.services.system_settings import (
    get_setting_float
)


router = APIRouter(
    prefix="/gifts",
    tags=["礼物管理"]
)


def make_order_no() -> str:

    now = datetime.now(
        timezone.utc
    )

    return (
        "GF"
        + now.strftime(
            "%Y%m%d%H%M%S"
        )
        + uuid4().hex[:10].upper()
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


async def get_or_create_relationship(
    db: AsyncSession,
    user_id_1: int,
    user_id_2: int
) -> UserRelationship:

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

    if relationship:

        return relationship


    relationship = UserRelationship(

        user_id_a=
            user_id_a,

        user_id_b=
            user_id_b,

        intimacy=
            0,

        relationship_status=
            "normal"
    )


    db.add(
        relationship
    )

    await db.flush()

    return relationship


@router.get(
    "/products",
    response_model=list[GiftProductResponse]
)
async def list_gift_products(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(GiftProduct)
        .order_by(
            GiftProduct.id.asc()
        )
    )

    return result.scalars().all()


@router.post(
    "/products",
    response_model=GiftProductResponse
)
async def create_gift_product(
    data: GiftProductCreate,
    db: AsyncSession = Depends(get_db)
):

    product = await db.get(
        ShopProduct,
        data.product_id
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商城商品不存在"
        )


    if (
        product.product_type
        != "gift"
    ):

        raise HTTPException(
            status_code=400,
            detail="该商城商品不是礼物类型"
        )


    result = await db.execute(
        select(GiftProduct)
        .where(
            GiftProduct.product_id
            == data.product_id
        )
    )

    exists = (
        result.scalar_one_or_none()
    )

    if exists:

        raise HTTPException(
            status_code=409,
            detail="该礼物配置已经存在"
        )


    gift = GiftProduct(

        product_id=
            data.product_id,

        icon_url=
            data.icon_url,

        rarity=
            data.rarity,

        exp_reward=
            max(
                0,
                data.exp_reward
            ),

        intimacy_reward=
            max(
                0,
                data.intimacy_reward
            )
    )


    db.add(gift)

    await db.commit()

    await db.refresh(gift)

    return gift


@router.put(
    "/products/{gift_id}",
    response_model=GiftProductResponse
)
async def update_gift_product(
    gift_id: int,
    data: GiftProductUpdate,
    db: AsyncSession = Depends(get_db)
):

    gift = await db.get(
        GiftProduct,
        gift_id
    )

    if gift is None:

        raise HTTPException(
            status_code=404,
            detail="礼物配置不存在"
        )


    values = data.model_dump(
        exclude_unset=True
    )


    for key, value in values.items():

        if (
            key in {
                "exp_reward",
                "intimacy_reward"
            }
            and value is not None
        ):

            value = max(
                0,
                int(value)
            )


        setattr(
            gift,
            key,
            value
        )


    await db.commit()

    await db.refresh(gift)

    return gift


@router.delete(
    "/products/{gift_id}"
)
async def delete_gift_product(
    gift_id: int,
    db: AsyncSession = Depends(get_db)
):

    gift = await db.get(
        GiftProduct,
        gift_id
    )

    if gift is None:

        raise HTTPException(
            status_code=404,
            detail="礼物配置不存在"
        )


    await db.delete(gift)

    await db.commit()


    return {
        "success": True,
        "message": "礼物配置已删除"
    }


@router.post(
    "/send",
    response_model=GiftRecordResponse
)
async def send_gift(
    data: GiftSendRequest,
    db: AsyncSession = Depends(get_db)
):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="赠送数量必须大于0"
        )


    if (
        data.sender_user_id
        == data.receiver_user_id
    ):

        raise HTTPException(
            status_code=400,
            detail="不能给自己赠送礼物"
        )


    try:

        result = await db.execute(
            select(User)
            .where(
                User.id
                == data.sender_user_id
            )
            .with_for_update()
        )

        sender = (
            result.scalar_one_or_none()
        )


        if sender is None:

            raise HTTPException(
                status_code=404,
                detail="赠送用户不存在"
            )


        if not sender.is_active:

            raise HTTPException(
                status_code=403,
                detail="赠送用户已被禁用"
            )


        result = await db.execute(
            select(User)
            .where(
                User.id
                == data.receiver_user_id
            )
            .with_for_update()
        )

        receiver = (
            result.scalar_one_or_none()
        )


        if receiver is None:

            raise HTTPException(
                status_code=404,
                detail="接收用户不存在"
            )


        if not receiver.is_active:

            raise HTTPException(
                status_code=403,
                detail="接收用户已被禁用"
            )


        result = await db.execute(
            select(ShopProduct)
            .where(
                ShopProduct.id
                == data.product_id
            )
            .with_for_update()
        )

        product = (
            result.scalar_one_or_none()
        )


        if product is None:

            raise HTTPException(
                status_code=404,
                detail="礼物商品不存在"
            )


        if (
            product.product_type
            != "gift"
        ):

            raise HTTPException(
                status_code=400,
                detail="该商品不是礼物"
            )


        if not product.enabled:

            raise HTTPException(
                status_code=400,
                detail="该礼物已经下架"
            )


        result = await db.execute(
            select(GiftProduct)
            .where(
                GiftProduct.product_id
                == product.id
            )
        )

        gift_config = (
            result.scalar_one_or_none()
        )


        if gift_config is None:

            raise HTTPException(
                status_code=400,
                detail="礼物商品尚未完成礼物配置"
            )


        unit_coin_price = int(
            product.coin_price
            or 0
        )


        if unit_coin_price <= 0:

            raise HTTPException(
                status_code=400,
                detail="该礼物未设置蜗币价格"
            )


        total_coin_amount = (
            unit_coin_price
            * data.quantity
        )


        balance_before = int(
            sender.coins
            or 0
        )


        if (
            balance_before
            < total_coin_amount
        ):

            raise HTTPException(
                status_code=400,
                detail="蜗币余额不足"
            )


        balance_after = (
            balance_before
            - total_coin_amount
        )


        exp_multiplier = (
            await get_setting_float(
                db,
                "gift_exp_multiplier",
                1.0
            )
        )


        intimacy_multiplier = (
            await get_setting_float(
                db,
                "gift_intimacy_multiplier",
                1.0
            )
        )


        base_exp = (
            int(
                gift_config.exp_reward
                or 0
            )
            * data.quantity
        )


        base_intimacy = (
            int(
                gift_config.intimacy_reward
                or 0
            )
            * data.quantity
        )


        total_exp_reward = max(
            0,
            int(
                round(
                    base_exp
                    * exp_multiplier
                )
            )
        )


        total_intimacy_reward = max(
            0,
            int(
                round(
                    base_intimacy
                    * intimacy_multiplier
                )
            )
        )


        order = ShopOrder(

            order_no=
                make_order_no(),

            user_id=
                sender.id,

            product_id=
                product.id,

            product_name=
                product.name,

            product_type=
                "gift",

            member_level=
                None,

            member_days=
                None,

            payment_method=
                "coins",

            amount_cents=
                int(
                    product.price_cents
                    or 0
                )
                * data.quantity,

            coin_amount=
                total_coin_amount,

            status=
                "paid",

            paid_at=
                datetime.now(
                    timezone.utc
                )
        )


        db.add(order)

        await db.flush()


        sender.coins = (
            balance_after
        )


        receiver.experience = (
            int(
                receiver.experience
                or 0
            )
            + total_exp_reward
        )


        relationship = (
            await get_or_create_relationship(
                db=db,

                user_id_1=
                    sender.id,

                user_id_2=
                    receiver.id
            )
        )


        relationship.intimacy = (
            int(
                relationship.intimacy
                or 0
            )
            + total_intimacy_reward
        )


        transaction = CoinTransaction(

            user_id=
                sender.id,

            transaction_type=
                "gift",

            amount=
                -total_coin_amount,

            balance_before=
                balance_before,

            balance_after=
                balance_after,

            order_id=
                order.id,

            description=(
                f"赠送礼物：{product.name}"
                f" × {data.quantity}"
                f"，接收用户#{receiver.id}"
            )
        )


        db.add(
            transaction
        )


        gift_record = GiftRecord(

            order_id=
                order.id,

            sender_user_id=
                sender.id,

            receiver_user_id=
                receiver.id,

            product_id=
                product.id,

            gift_name=
                product.name,

            quantity=
                data.quantity,

            coin_amount=
                total_coin_amount,

            exp_reward=
                total_exp_reward,

            intimacy_reward=
                total_intimacy_reward
        )


        db.add(
            gift_record
        )


        await db.commit()

        await db.refresh(
            gift_record
        )


        return gift_record


    except HTTPException:

        await db.rollback()

        raise


    except Exception as exc:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"赠送礼物失败：{exc}"
        )


@router.get(
    "/records",
    response_model=list[GiftRecordResponse]
)
async def list_gift_records(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(GiftRecord)
        .order_by(
            GiftRecord.id.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/records/sender/{user_id}",
    response_model=list[GiftRecordResponse]
)
async def list_sender_records(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(GiftRecord)
        .where(
            GiftRecord.sender_user_id
            == user_id
        )
        .order_by(
            GiftRecord.id.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/records/receiver/{user_id}",
    response_model=list[GiftRecordResponse]
)
async def list_receiver_records(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(GiftRecord)
        .where(
            GiftRecord.receiver_user_id
            == user_id
        )
        .order_by(
            GiftRecord.id.desc()
        )
    )

    return result.scalars().all()
