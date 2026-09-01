from datetime import (
    datetime,
    timedelta,
    timezone
)

from uuid import uuid4


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.database import get_db

from app.models.product import ShopProduct
from app.models.user import User

from app.models.order import (
    ShopOrder,
    CoinTransaction
)

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

from app.schemas.order import (
    CoinPurchaseRequest,
    OrderResponse,
    CoinTransactionResponse
)


router = APIRouter(
    prefix="/shop",
    tags=["商城管理"]
)


def make_order_no() -> str:

    now = datetime.now(
        timezone.utc
    )

    return (
        "SN"
        + now.strftime(
            "%Y%m%d%H%M%S"
        )
        + uuid4().hex[:10].upper()
    )


def extend_membership(
    user: User,
    member_level: str,
    member_days: int
):

    now = datetime.now(
        timezone.utc
    )

    if member_level not in {
        "vip",
        "svip"
    }:

        raise HTTPException(
            status_code=400,
            detail="会员等级不正确"
        )

    if member_days <= 0:

        raise HTTPException(
            status_code=400,
            detail="会员有效天数必须大于0"
        )


    current_expire = (
        user.member_expire_at
        if (
            user.member_expire_at
            and user.member_expire_at > now
        )
        else now
    )


    if (
        not user.member_level
        or user.member_level == "normal"
        or user.member_started_at is None
    ):

        user.member_started_at = now


    user.member_level = (
        member_level
    )

    user.member_expire_at = (
        current_expire
        + timedelta(
            days=member_days
        )
    )


@router.get(
    "/products",
    response_model=list[ProductResponse]
)
async def list_products(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(ShopProduct)
        .order_by(
            ShopProduct.sort_order.asc(),
            ShopProduct.id.asc()
        )
    )

    return result.scalars().all()


@router.post(
    "/products",
    response_model=ProductResponse
)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):

    if data.product_type == "member":

        if data.member_level not in {
            "vip",
            "svip"
        }:

            raise HTTPException(
                status_code=400,
                detail="会员商品必须设置VIP或SVIP"
            )

        if (
            not data.member_days
            or data.member_days <= 0
        ):

            raise HTTPException(
                status_code=400,
                detail="会员有效天数必须大于0"
            )


    product = ShopProduct(

        name=
            data.name,

        product_type=
            data.product_type,

        member_level=
            data.member_level,

        member_days=
            data.member_days,

        price_cents=
            max(
                0,
                data.price_cents
            ),

        coin_price=
            max(
                0,
                data.coin_price
            ),

        enabled=
            data.enabled,

        sort_order=
            data.sort_order,

        description=
            data.description
    )


    db.add(product)

    await db.commit()

    await db.refresh(product)

    return product


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):

    product = await db.get(
        ShopProduct,
        product_id
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )


    values = data.model_dump(
        exclude_unset=True
    )


    for key, value in values.items():

        if (
            key in {
                "price_cents",
                "coin_price"
            }
            and value is not None
        ):

            value = max(
                0,
                int(value)
            )

        setattr(
            product,
            key,
            value
        )


    await db.commit()

    await db.refresh(product)

    return product


@router.patch(
    "/products/{product_id}/enabled",
    response_model=ProductResponse
)
async def toggle_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):

    product = await db.get(
        ShopProduct,
        product_id
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )


    product.enabled = (
        not bool(
            product.enabled
        )
    )


    await db.commit()

    await db.refresh(product)

    return product


@router.delete(
    "/products/{product_id}"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):

    product = await db.get(
        ShopProduct,
        product_id
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )


    await db.delete(product)

    await db.commit()


    return {
        "success": True,
        "message": "商品已删除"
    }


# =========================
# 蜗币购买商品
# =========================

@router.post(
    "/purchase/coins",
    response_model=OrderResponse
)
async def purchase_with_coins(
    data: CoinPurchaseRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        # 锁定用户，避免并发重复扣款
        result = await db.execute(
            select(User)
            .where(
                User.id
                == data.user_id
            )
            .with_for_update()
        )

        user = (
            result.scalar_one_or_none()
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


        # 锁定商品
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
                detail="商品不存在"
            )


        if not product.enabled:

            raise HTTPException(
                status_code=400,
                detail="商品已下架"
            )


        coin_price = int(
            product.coin_price or 0
        )


        if coin_price <= 0:

            raise HTTPException(
                status_code=400,
                detail="该商品未设置蜗币价格"
            )


        balance_before = int(
            user.coins or 0
        )


        if (
            balance_before
            < coin_price
        ):

            raise HTTPException(
                status_code=400,
                detail="蜗币余额不足"
            )


        balance_after = (
            balance_before
            - coin_price
        )


        order = ShopOrder(

            order_no=
                make_order_no(),

            user_id=
                user.id,

            product_id=
                product.id,

            product_name=
                product.name,

            product_type=
                product.product_type,

            member_level=
                product.member_level,

            member_days=
                product.member_days,

            payment_method=
                "coins",

            amount_cents=
                int(
                    product.price_cents
                    or 0
                ),

            coin_amount=
                coin_price,

            status=
                "paid",

            paid_at=
                datetime.now(
                    timezone.utc
                )
        )


        db.add(order)

        await db.flush()


        # 扣除蜗币
        user.coins = (
            balance_after
        )


        transaction = (
            CoinTransaction(

                user_id=
                    user.id,

                transaction_type=
                    "purchase",

                amount=
                    -coin_price,

                balance_before=
                    balance_before,

                balance_after=
                    balance_after,

                order_id=
                    order.id,

                description=
                    f"购买商品：{product.name}"
            )
        )


        db.add(transaction)


        # 会员商品自动开通
        if (
            product.product_type
            == "member"
        ):

            if (
                not product.member_level
                or not product.member_days
            ):

                raise HTTPException(
                    status_code=500,
                    detail="会员商品配置不完整"
                )


            extend_membership(

                user=user,

                member_level=
                    product.member_level,

                member_days=
                    int(
                        product.member_days
                    )
            )


        await db.commit()

        await db.refresh(order)

        return order


    except HTTPException:

        await db.rollback()

        raise


    except Exception as exc:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"购买失败：{exc}"
        )


# =========================
# 订单列表
# =========================

@router.get(
    "/orders",
    response_model=list[OrderResponse]
)
async def list_orders(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(ShopOrder)
        .order_by(
            ShopOrder.id.desc()
        )
    )

    return result.scalars().all()


# =========================
# 用户订单
# =========================

@router.get(
    "/orders/user/{user_id}",
    response_model=list[OrderResponse]
)
async def list_user_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(ShopOrder)
        .where(
            ShopOrder.user_id
            == user_id
        )
        .order_by(
            ShopOrder.id.desc()
        )
    )

    return result.scalars().all()


# =========================
# 单个订单
# =========================

@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):

    order = await db.get(
        ShopOrder,
        order_id
    )

    if order is None:

        raise HTTPException(
            status_code=404,
            detail="订单不存在"
        )

    return order


# =========================
# 蜗币流水
# =========================

@router.get(
    "/coin-transactions",
    response_model=list[CoinTransactionResponse]
)
async def list_coin_transactions(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(CoinTransaction)
        .order_by(
            CoinTransaction.id.desc()
        )
    )

    return result.scalars().all()


# =========================
# 用户蜗币流水
# =========================

@router.get(
    "/coin-transactions/user/{user_id}",
    response_model=list[CoinTransactionResponse]
)
async def list_user_coin_transactions(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(CoinTransaction)
        .where(
            CoinTransaction.user_id
            == user_id
        )
        .order_by(
            CoinTransaction.id.desc()
        )
    )

    return result.scalars().all()
