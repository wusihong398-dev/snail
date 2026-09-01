from fastapi import Header, HTTPException
from jose import JWTError, jwt
from app.auth.jwt import SECRET_KEY, ALGORITHM


async def require_admin(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="需要管理员登录")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="登录令牌无效")
        return str(username)
    except JWTError:
        raise HTTPException(status_code=401, detail="登录令牌无效或已过期")
