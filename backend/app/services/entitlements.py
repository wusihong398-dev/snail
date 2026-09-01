from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entitlement import UserEntitlement


async def get_entitlement_quantity(db: AsyncSession, user_id: int, entitlement_key: str, scope_type: str = "global", scope_id: int | None = None) -> int:
    result = await db.execute(
        select(UserEntitlement).where(
            UserEntitlement.user_id == user_id,
            UserEntitlement.entitlement_key == entitlement_key,
            UserEntitlement.scope_type == scope_type,
            UserEntitlement.scope_id == scope_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return 0
    if item.expires_at is not None and item.expires_at <= datetime.now(timezone.utc):
        return 0
    return max(0, int(item.quantity or 0))


async def add_entitlement(db: AsyncSession, user_id: int, entitlement_key: str, quantity: int = 1, *, scope_type: str = "global", scope_id: int | None = None, source_type: str = "purchase", source_id: int | None = None):
    result = await db.execute(
        select(UserEntitlement).where(
            UserEntitlement.user_id == user_id,
            UserEntitlement.entitlement_key == entitlement_key,
            UserEntitlement.scope_type == scope_type,
            UserEntitlement.scope_id == scope_id,
        ).with_for_update()
    )
    item = result.scalar_one_or_none()
    if item is None:
        item = UserEntitlement(
            user_id=user_id, entitlement_key=entitlement_key, quantity=max(0, int(quantity)),
            scope_type=scope_type, scope_id=scope_id, source_type=source_type, source_id=source_id,
        )
        db.add(item)
    else:
        item.quantity = max(0, int(item.quantity or 0) + int(quantity))
        item.source_type = source_type
        item.source_id = source_id
    await db.flush()
    return item
