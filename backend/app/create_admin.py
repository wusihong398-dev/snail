import asyncio
import getpass
import os

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.admin import Admin
from app.auth.password import hash_password


async def create_admin():
    username = os.environ.get("INITIAL_ADMIN_USERNAME", "").strip()
    if not username:
        username = input("Admin username: ").strip()
    password = os.environ.get("INITIAL_ADMIN_PASSWORD", "")
    if not password:
        password = getpass.getpass("Admin password: ")
    if not username or not password or password.strip().upper() == "CHANGE_ME":
        raise ValueError("A username and non-placeholder password are required")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Admin).where(Admin.username == username))
        if result.scalar_one_or_none():
            print("管理员已存在")
            return
        admin = Admin(
            username=username, password_hash=hash_password(password),
            role="admin", enabled=True,
        )
        db.add(admin)
        await db.commit()
        print("管理员创建成功（密码不输出）")


if __name__ == "__main__":
    asyncio.run(create_admin())
