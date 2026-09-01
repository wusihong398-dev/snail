from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_setting import SystemSetting


async def get_setting_string(
    db: AsyncSession,
    key: str,
    default: str
) -> str:

    result = await db.execute(
        select(SystemSetting.setting_value)
        .where(
            SystemSetting.setting_key == key
        )
    )

    value = result.scalar_one_or_none()

    if value is None:
        return default

    return str(value)


async def get_setting_int(
    db: AsyncSession,
    key: str,
    default: int
) -> int:

    value = await get_setting_string(
        db,
        key,
        str(default)
    )

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


async def get_setting_float(
    db: AsyncSession,
    key: str,
    default: float
) -> float:

    value = await get_setting_string(
        db,
        key,
        str(default)
    )

    try:
        return float(value)

    except (TypeError, ValueError):
        return default
