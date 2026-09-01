import asyncio

from app.database import engine, Base

# 导入所有模型
from app.models import (
    User,
    WechatAccount,
    Group,
    AIConfig,
    GameQuestion
)


async def init_database():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

    print("蜗牛群聊精灵数据库表创建完成")


if __name__ == "__main__":

    asyncio.run(
        init_database()
    )
