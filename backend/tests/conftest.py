"""Fail closed: these integration tests must never target production."""
import os
import secrets
from urllib.parse import urlsplit

url = os.environ.get("TEST_DATABASE_URL", "")
parts = urlsplit(url)
if (not url.startswith("postgresql+asyncpg://")
        or parts.hostname not in {"127.0.0.1", "localhost"}
        or parts.port in {None, 5432}
        or parts.path != "/snail_stageb_test"):
    raise RuntimeError("TEST_DATABASE_URL must target disposable localhost, non-5432 snail_stageb_test")
os.environ["DATABASE_URL"] = url
os.environ["JWT_SECRET"] = secrets.token_urlsafe(48)
