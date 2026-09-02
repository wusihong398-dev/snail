import asyncio
import os
from pathlib import Path
import unittest
import uuid

import asyncpg
from sqlalchemy import select, func
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import Base
from app.models.user import User
from app.models.group import Group
from app.models.system_setting import SystemSetting
from app.models.order import CoinTransaction
from app.models.commercial import Agent, RedeemCode
from app.routers.commercial import create_agent, create_code, redeem_code
from app.schemas.commercial import AgentCreate, RedeemCodeCreate, RedeemRequest


class AssetTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "stageb_" + uuid.uuid4().hex
        url = make_url(os.environ["TEST_DATABASE_URL"])
        assert url.database == "snail_stageb_test" and url.port != 5432
        self.admin = await asyncpg.connect(url.set(drivername="postgresql").render_as_string(hide_password=False))
        await self.admin.execute(f'CREATE SCHEMA "{self.schema}"')
        await self.admin.execute(f'GRANT USAGE ON SCHEMA "{self.schema}" TO snail_admin')
        self.engine = create_async_engine(url, connect_args={"server_settings": {
            "search_path": self.schema, "lock_timeout": "5000", "statement_timeout": "10000"}})
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda c: Base.metadata.create_all(c, tables=[
                User.__table__, Group.__table__, SystemSetting.__table__, CoinTransaction.__table__]))
        await self.admin.execute(f'SET search_path TO "{self.schema}"')
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        # Exact immutable production migration, followed by the proposed additive migration.
        await self.admin.execute((migrations / "020_commercial_platform.sql").read_text())
        await self.before_stage_b()
        await self.admin.execute((migrations / "021_commercial_operations.sql").read_text())

    async def before_stage_b(self):
        pass

    async def asyncTearDown(self):
        await self.engine.dispose()
        assert self.schema.startswith("stageb_")
        await self.admin.execute(f'DROP SCHEMA "{self.schema}" CASCADE')
        await self.admin.close()

    async def agent(self, quota=1000, licenses=10, mode="prepaid"):
        async with self.sessions() as db:
            return await create_agent(AgentCreate(name="Test", agent_code=uuid.uuid4().hex,
                diamond_quota=quota, license_balance=licenses, agent_type=mode), db=db, operator_name="test-admin")

    async def code(self, agent_id, value=100, uses=1, kind="diamonds", **extra):
        async with self.sessions() as db:
            return await create_code(RedeemCodeCreate(code_type=kind, agent_id=agent_id,
                value=value, max_uses=uses, **extra), db=db, operator_name="test-admin")

    async def redeem(self, code, wx="test-user", request_id=None, group=None):
        async with self.sessions() as db:
            return await redeem_code(RedeemRequest(code=code, wx_user_id=wx,
                wx_group_id=group, request_id=request_id), db=db)

    async def row(self, model, row_id):
        async with self.sessions() as db:
            return await db.get(model, row_id)

    async def count(self, model, *criteria):
        async with self.sessions() as db:
            return (await db.execute(select(func.count()).select_from(model).where(*criteria))).scalar_one()

    async def user(self, wx="test-user", paid=0, bonus=0):
        async with self.sessions() as db:
            user = User(wx_user_id=wx, paid_diamonds=paid, bonus_diamonds=bonus)
            db.add(user)
            await db.commit()
            return user

    async def parallel(self, *operations):
        start = asyncio.Event()
        async def run(op):
            await start.wait()
            return await op()
        tasks = [asyncio.create_task(run(op)) for op in operations]
        start.set()
        return await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=20)
