from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.diamond import DiamondTransaction


def total_diamonds(user: User) -> int:
    return int(user.paid_diamonds or 0) + int(user.bonus_diamonds or 0)


async def add_paid_diamonds(db: AsyncSession, user: User, amount: int, *, transaction_type: str = "purchase", reference_type: str | None = None, reference_id: int | None = None, description: str | None = None):
    amount = int(amount)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="钻石数量必须大于0")
    paid_before = int(user.paid_diamonds or 0)
    bonus_before = int(user.bonus_diamonds or 0)
    user.paid_diamonds = paid_before + amount
    tx = DiamondTransaction(
        user_id=user.id, transaction_type=transaction_type, diamond_type="paid", amount=amount,
        paid_before=paid_before, paid_after=user.paid_diamonds,
        bonus_before=bonus_before, bonus_after=bonus_before,
        reference_type=reference_type, reference_id=reference_id, description=description,
    )
    db.add(tx)
    await db.flush()
    return tx


async def add_bonus_diamonds(db: AsyncSession, user: User, amount: int, *, transaction_type: str = "admin_grant", reference_type: str | None = None, reference_id: int | None = None, description: str | None = None):
    amount = int(amount)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="钻石数量必须大于0")
    paid_before = int(user.paid_diamonds or 0)
    bonus_before = int(user.bonus_diamonds or 0)
    user.bonus_diamonds = bonus_before + amount
    tx = DiamondTransaction(
        user_id=user.id, transaction_type=transaction_type, diamond_type="bonus", amount=amount,
        paid_before=paid_before, paid_after=paid_before,
        bonus_before=bonus_before, bonus_after=user.bonus_diamonds,
        reference_type=reference_type, reference_id=reference_id, description=description,
    )
    db.add(tx)
    await db.flush()
    return tx


async def spend_diamonds(db: AsyncSession, user: User, amount: int, *, transaction_type: str = "consume", reference_type: str | None = None, reference_id: int | None = None, description: str | None = None):
    amount = int(amount)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="消费钻石数量必须大于0")
    paid_before = int(user.paid_diamonds or 0)
    bonus_before = int(user.bonus_diamonds or 0)
    if paid_before + bonus_before < amount:
        raise HTTPException(status_code=400, detail=f"钻石不足，当前共有{paid_before + bonus_before}钻石")
    bonus_used = min(bonus_before, amount)
    paid_used = amount - bonus_used
    user.bonus_diamonds = bonus_before - bonus_used
    user.paid_diamonds = paid_before - paid_used
    dtype = "mixed" if bonus_used and paid_used else ("bonus" if bonus_used else "paid")
    tx = DiamondTransaction(
        user_id=user.id, transaction_type=transaction_type, diamond_type=dtype, amount=-amount,
        paid_before=paid_before, paid_after=user.paid_diamonds,
        bonus_before=bonus_before, bonus_after=user.bonus_diamonds,
        reference_type=reference_type, reference_id=reference_id, description=description,
    )
    db.add(tx)
    await db.flush()
    return tx
