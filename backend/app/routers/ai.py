from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai import AIConfig


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class ChatRequest(BaseModel):
    message: str


@router.get("/config/list")
async def list_configs(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AIConfig).order_by(
            AIConfig.priority.asc(),
            AIConfig.id.asc()
        )
    )

    configs = result.scalars().all()

    return configs


@router.post("/chat")
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AIConfig)
        .where(AIConfig.enabled.is_(True))
        .order_by(
            AIConfig.priority.asc(),
            AIConfig.id.asc()
        )
    )

    config = result.scalars().first()

    if config is None:
        raise HTTPException(
            status_code=503,
            detail="暂时没有启用的AI接口"
        )

    try:
        from app.ai.client import ai_request

        result_data = await ai_request(
            config,
            [
                {
                    "role": "user",
                    "content": data.message
                }
            ]
        )

        choices = result_data.get("choices") or []

        if not choices:
            error_data = result_data.get("error")

            if error_data:
                raise HTTPException(
                    status_code=502,
                    detail=str(error_data)
                )

            raise HTTPException(
                status_code=502,
                detail="AI接口没有返回有效内容"
            )

        message_data = (
            choices[0].get("message") or {}
        )

        answer = message_data.get("content")

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="AI接口返回内容为空"
            )

        return {
            "success": True,
            "assistant": (
                getattr(
                    config,
                    "display_name",
                    None
                )
                or "蜗牛小精灵"
            ),
            "message": answer
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI调用失败：{exc}"
        )


@router.get("/health")
async def ai_health():
    return {
        "status": "ok",
        "service": "snail-ai"
    }
