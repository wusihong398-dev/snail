from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.wechat import WechatAccount
from app.schemas.wechat import (
    WechatAccountCreate,
    WechatAccountUpdate,
    WechatOnlineUpdate,
    WechatAccountResponse
)


router = APIRouter(
    prefix="/wechat",
    tags=["微信机器人"]
)


@router.get(
    "/accounts",
    response_model=list[WechatAccountResponse]
)
async def list_wechat_accounts(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WechatAccount).order_by(
            WechatAccount.id.asc()
        )
    )

    return result.scalars().all()


@router.get(
    "/accounts/{account_id}",
    response_model=WechatAccountResponse
)
async def get_wechat_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(
        WechatAccount,
        account_id
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="微信机器人不存在"
        )

    return account


@router.post(
    "/accounts",
    response_model=WechatAccountResponse
)
async def create_wechat_account(
    data: WechatAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    if data.wxid:
        result = await db.execute(
            select(WechatAccount).where(
                WechatAccount.wxid == data.wxid
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="该微信账号已经存在"
            )

    account = WechatAccount(
        nickname=data.nickname or "未登录机器人",
        wxid=data.wxid,
        online=data.online,
        customer_id=data.customer_id
    )

    db.add(account)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="微信账号保存失败，可能存在重复wxid"
        )

    await db.refresh(account)

    return account


@router.put(
    "/accounts/{account_id}",
    response_model=WechatAccountResponse
)
async def update_wechat_account(
    account_id: int,
    data: WechatAccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(
        WechatAccount,
        account_id
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="微信机器人不存在"
        )

    if data.nickname is not None:
        account.nickname = data.nickname

    if data.wxid is not None:
        account.wxid = data.wxid

    if data.online is not None:
        account.online = data.online

    if data.customer_id is not None:
        account.customer_id = data.customer_id

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="更新失败，wxid可能重复"
        )

    await db.refresh(account)

    return account


@router.patch(
    "/accounts/{account_id}/online",
    response_model=WechatAccountResponse
)
async def update_wechat_online(
    account_id: int,
    data: WechatOnlineUpdate,
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(
        WechatAccount,
        account_id
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="微信机器人不存在"
        )

    account.online = data.online

    await db.commit()
    await db.refresh(account)

    return account


@router.delete(
    "/accounts/{account_id}"
)
async def delete_wechat_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    account = await db.get(
        WechatAccount,
        account_id
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="微信机器人不存在"
        )

    await db.delete(account)
    await db.commit()

    return {
        "success": True,
        "message": "微信机器人已删除"
    }


@router.get("/health")
async def wechat_health(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WechatAccount)
    )

    accounts = result.scalars().all()

    online_count = sum(
        1 for account in accounts
        if account.online
    )

    return {
        "status": "ok",
        "total": len(accounts),
        "online": online_count,
        "offline": len(accounts) - online_count
    }
