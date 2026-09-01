from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.database import get_db

from app.models.admin import Admin

from app.auth.password import verify_password

from app.auth.jwt import create_token



router = APIRouter(
    prefix="/auth",
    tags=["管理员认证"]
)



@router.post("/login")
async def login(

    username:str,

    password:str,

    db:AsyncSession=Depends(get_db)

):


    result = await db.execute(

        select(Admin)
        .where(
            Admin.username == username
        )

    )


    admin = result.scalar_one_or_none()



    if not admin:

        raise HTTPException(
            status_code=401,
            detail="账号不存在"
        )


    if not verify_password(
        password,
        admin.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="密码错误"
        )



    token=create_token(
        username
    )


    return {

        "access_token":token,

        "token_type":"bearer"

    }
