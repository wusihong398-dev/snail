from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models.system_setting import (
    SystemSetting
)

from app.schemas.system_setting import (
    SystemSettingResponse,
    SystemSettingUpdate
)


router = APIRouter(
    prefix="/system-settings",
    tags=["系统参数"]
)


def validate_value(
    setting: SystemSetting,
    value: str
):

    try:

        if setting.value_type == "integer":

            number = int(value)

            if number < 0:
                raise ValueError()

            return str(number)


        if setting.value_type == "float":

            number = float(value)

            if number < 0:
                raise ValueError()

            return str(number)


        return str(value)


    except Exception:

        raise HTTPException(
            status_code=400,
            detail=f"{setting.title}的参数格式不正确"
        )


@router.get(
    "",
    response_model=list[SystemSettingResponse]
)
async def list_settings(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(SystemSetting)
        .order_by(
            SystemSetting.id.asc()
        )
    )

    return result.scalars().all()


@router.get(
    "/{setting_key}",
    response_model=SystemSettingResponse
)
async def get_setting(
    setting_key: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(SystemSetting)
        .where(
            SystemSetting.setting_key
            == setting_key
        )
    )

    setting = (
        result.scalar_one_or_none()
    )


    if setting is None:

        raise HTTPException(
            status_code=404,
            detail="系统参数不存在"
        )


    return setting


@router.put(
    "/{setting_key}",
    response_model=SystemSettingResponse
)
async def update_setting(
    setting_key: str,
    data: SystemSettingUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(SystemSetting)
        .where(
            SystemSetting.setting_key
            == setting_key
        )
    )

    setting = (
        result.scalar_one_or_none()
    )


    if setting is None:

        raise HTTPException(
            status_code=404,
            detail="系统参数不存在"
        )


    setting.setting_value = (
        validate_value(
            setting,
            data.setting_value
        )
    )


    await db.commit()

    await db.refresh(
        setting
    )


    return setting
