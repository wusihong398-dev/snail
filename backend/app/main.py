from fastapi import FastAPI

from sqlalchemy import text


from app.database import engine

from app.redis import redis_client


# =========================
# 业务路由
# =========================

from app.routers import users

from app.routers import ai

from app.routers import wechat

from app.routers import groups

from app.routers import shop
from app.routers import gifts
from app.routers import relationships
from app.routers import relationship_requests
from app.routers import babies
from app.routers import system_settings
from app.routers import commercial

# =========================
# 管理员登录
# =========================

from app.auth import routes as auth_routes


# =========================
# AI 网络出口
# =========================

from app.proxy import routes as proxy_routes



app = FastAPI(

    title="蜗牛群聊精灵",

    description="AI微信群互动机器人平台",

    version="0.3.0",

    root_path="/api"

)


# =========================
# 注册路由
# =========================

app.include_router(
    users.router
)


app.include_router(
    ai.router
)


app.include_router(
    wechat.router
)

app.include_router(
    groups.router
)

app.include_router(
    auth_routes.router
)


app.include_router(
    proxy_routes.router
)


app.include_router(
    shop.router
)

app.include_router(
    gifts.router
)

app.include_router(
    relationships.router
)

app.include_router(
    relationship_requests.router
)

app.include_router(
    babies.router
)

app.include_router(
    system_settings.router
)

app.include_router(
    commercial.router
)

app.include_router(
    commercial.public_router
)
# =========================
# 首页
# =========================

@app.get("/")
async def root():

    return {
        "app": "蜗牛群聊精灵",
        "version": "0.3.0",
        "status": "running"
    }


# =========================
# 健康检测
# =========================

@app.get("/health")
async def health():

    database_status = "error"

    redis_status = "error"


    # PostgreSQL

    try:

        async with engine.connect() as conn:

            await conn.execute(
                text(
                    "SELECT 1"
                )
            )

        database_status = (
            "connected"
        )

    except Exception as exc:

        database_status = str(exc)


    # Redis

    try:

        await redis_client.ping()

        redis_status = (
            "connected"
        )

    except Exception as exc:

        redis_status = str(exc)


    return {

        "app":
            "蜗牛群聊精灵",

        "service":
            "snail-chat-elf-api",

        "version":
            "0.3.0",

        "database":
            database_status,

        "redis":
            redis_status

    }
