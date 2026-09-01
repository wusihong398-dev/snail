import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import jwt


load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
SECRET_KEY = os.environ.get("JWT_SECRET", "")
if not SECRET_KEY or SECRET_KEY.strip().upper() == "CHANGE_ME":
    raise RuntimeError("JWT_SECRET must be configured with a non-placeholder secret")

ALGORITHM = "HS256"


def create_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode(
        {"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM
    )
