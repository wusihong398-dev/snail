from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import select
from app.models.commercial import Agent, RedeemCode, RedeemCodeUsage, CustomerGroupOwnership, GroupMember
from app.models.order import CoinTransaction
from app.models.commercial_operations import CommercialOperationLog
from app.models.commercial_operations import AgentDiamondQuotaTransaction as QuotaTx, AgentLicenseTransaction as LicenseTx
from app.models.diamond import DiamondTransaction
from app.models.user import User
from app.services.commercial_operations import (
    adjust_agent_diamond_quota,
    grant_bonus_diamonds,
    reservation_summary,
)
from app.services.diamonds import spend_diamonds
from tests.support import AssetTestCase


class TestCommercialAssets(AssetTestCase):
    async def test_group_coin_grant_has_ledger_and_authenticated_operator(self):
        from app.routers.commercial import grant_asset
        from app.schemas.commercial import AssetGrantRequest
        agent = await self.agent()
        code = await self.code(agent.id, value=365, kind="group_license")
        result = await self.redeem(code.code, group="grant-group")
        async with self.sessions() as db:
            await grant_asset(AssetGrantRequest(customer_id=result.customer_id, group_id=result.group_id,
                operator_user_id=result.user_id, target_user_id=result.user_id, asset_type="coins", amount=10),
                db=db, operator_name="authenticated-admin")
        self.assertEqual(await self.count(CoinTransaction), 1)
        self.assertEqual(await self.count(CommercialOperationLog,
            CommercialOperationLog.operator_name == "authenticated-admin"), 1)
        self.assertEqual((await self.row(User, result.user_id)).coins, 10)

    async def test_group_grant_cannot_mint_paid_diamonds_or_cross_customer(self):
        from app.routers.commercial import grant_asset
        from app.schemas.commercial import AssetGrantRequest
        agent = await self.agent()
        code = await self.code(agent.id, value=365, kind="group_license")
        result = await self.redeem(code.code, group="grant-group")
        for asset, customer in [("paid_diamonds", result.customer_id), ("coins", result.customer_id + 99)]:
            async with self.sessions() as db:
                with self.assertRaises(HTTPException):
                    await grant_asset(AssetGrantRequest(customer_id=customer, group_id=result.group_id,
                        operator_user_id=result.user_id, target_user_id=result.user_id, asset_type=asset, amount=10),
                        db=db, operator_name="authenticated-admin")
        self.assertEqual((await self.row(User, result.user_id)).paid_diamonds, 0)
        self.assertEqual(await self.count(CoinTransaction), 0)

    async def test_multi_use_reserves_full_amount(self):
        agent = await self.agent(quota=1100)
        code = await self.code(agent.id, value=100, uses=10)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 100)
        async with self.sessions() as db:
            tx = (await db.execute(select(QuotaTx).where(QuotaTx.redeem_code_id == code.id))).scalar_one()
            self.assertEqual((tx.amount, tx.quota_before, tx.quota_after), (-1000, 1100, 100))
            self.assertEqual(tx.operator_name, "test-admin")
        summary = reservation_summary(await self.row(RedeemCode, code.id))
        self.assertEqual(summary["reserved_total"], 1000)
        self.assertEqual(summary["remaining_reserved"], 1000)

    async def test_insufficient_quota_rolls_back_code_and_ledger(self):
        agent = await self.agent(quota=999)
        with self.assertRaises(HTTPException):
            await self.code(agent.id, value=100, uses=10)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 999)
        self.assertEqual(await self.count(RedeemCode), 0)
        self.assertEqual(await self.count(QuotaTx, QuotaTx.transaction_type == "code_reserve"), 0)

    async def test_commission_agent_also_reserves_quota(self):
        agent = await self.agent(quota=100, mode="commission")
        await self.code(agent.id)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 0)

    async def test_creation_idempotency_rejects_retry_without_deduction(self):
        agent = await self.agent(quota=1000)
        await self.code(agent.id, request_id="create-1")
        with self.assertRaises(HTTPException) as caught:
            await self.code(agent.id, request_id="create-1")
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 900)

    async def test_multi_use_request_replay_and_identity_conflict(self):
        agent = await self.agent()
        code = await self.code(agent.id, uses=10)
        with self.assertRaises(HTTPException):
            await self.redeem(code.code)
        first = await self.redeem(code.code, request_id="message-1")
        replay = await self.redeem(code.code, request_id="message-1")
        self.assertEqual(first, replay)
        self.assertEqual((await self.row(User, first.user_id)).paid_diamonds, 100)
        self.assertEqual(await self.count(RedeemCodeUsage), 1)
        with self.assertRaises(HTTPException) as caught:
            await self.redeem(code.code, wx="impostor", request_id="message-1")
        self.assertEqual(caught.exception.status_code, 409)

    async def test_single_use_legacy_request_without_key(self):
        agent = await self.agent()
        code = await self.code(agent.id)
        await self.redeem(code.code)
        with self.assertRaises(HTTPException):
            await self.redeem(code.code)
        self.assertEqual(await self.count(DiamondTransaction), 1)

    async def test_paid_bonus_separation_and_bonus_first(self):
        user = await self.user(paid=100, bonus=30)
        async with self.sessions() as db:
            current = await db.get(User, user.id)
            await grant_bonus_diamonds(db, current, 20, description="test bonus")
            await spend_diamonds(db, current, 70)
            await db.commit()
        user = await self.row(User, user.id)
        self.assertEqual((user.paid_diamonds, user.bonus_diamonds), (80, 0))
        self.assertEqual(await self.count(DiamondTransaction), 2)

    async def test_adjustment_is_audited_and_idempotent(self):
        agent = await self.agent(quota=10)
        args = dict(transaction_type="admin_adjustment", operator_name="test-admin", reason="test",
                    idempotency_key="adjust-1")
        async with self.sessions() as db:
            first = await adjust_agent_diamond_quota(db, agent.id, 20, **args)
            await db.commit()
        async with self.sessions() as db:
            again = await adjust_agent_diamond_quota(db, agent.id, 20, **args)
            self.assertEqual(first.id, again.id)
            await db.commit()
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 30)
        self.assertEqual(await self.count(QuotaTx), 2)  # real initial + adjustment

    async def test_failure_after_reservation_rolls_back_everything(self):
        agent = await self.agent(quota=100)
        with patch("app.routers.commercial.CommercialOperationLog", side_effect=RuntimeError("injected")):
            with self.assertRaises(RuntimeError):
                await self.code(agent.id)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 100)
        self.assertEqual(await self.count(RedeemCode), 0)
        self.assertEqual(await self.count(QuotaTx, QuotaTx.transaction_type == "code_reserve"), 0)

    async def test_failure_after_credit_rolls_back_everything(self):
        from app.services.commercial_operations import grant_paid_diamonds
        agent = await self.agent()
        code = await self.code(agent.id)
        user = await self.user()
        async def fail(*a, **kw):
            await grant_paid_diamonds(*a, **kw)
            raise RuntimeError("injected after credit")
        with patch("app.routers.commercial.grant_paid_diamonds", side_effect=fail):
            with self.assertRaises(RuntimeError):
                await self.redeem(code.code, request_id="retry")
        self.assertEqual((await self.row(User, user.id)).paid_diamonds, 0)
        self.assertEqual((await self.row(RedeemCode, code.id)).used_count, 0)
        self.assertEqual(await self.count(DiamondTransaction), 0)
        self.assertEqual(await self.count(RedeemCodeUsage), 0)
        await self.redeem(code.code, request_id="retry")
        self.assertEqual((await self.row(User, user.id)).paid_diamonds, 100)

    async def test_group_license_compatibility_and_inventory_audit(self):
        agent = await self.agent(licenses=1)
        code = await self.code(agent.id, value=365, kind="group_license")
        result = await self.redeem(code.code, group="test-group")
        self.assertIsNotNone(result.customer_id)
        self.assertEqual((await self.row(Agent, agent.id)).license_balance, 0)
        self.assertEqual(await self.count(CustomerGroupOwnership), 1)
        self.assertEqual(await self.count(GroupMember, GroupMember.member_role == "owner"), 1)
        self.assertEqual(await self.count(LicenseTx, LicenseTx.transaction_type == "code_reserve"), 1)

    async def test_freeze_void_do_not_release_and_refund_is_explicit_idempotent(self):
        from app.routers.commercial import freeze_code, void_code, refund_code_reservation
        from app.schemas.commercial import CodeStatusRequest, CodeRefundRequest
        agent = await self.agent(quota=1000)
        code = await self.code(agent.id, value=100, uses=5)
        await self.redeem(code.code, request_id="use-1")
        async with self.sessions() as db:
            await freeze_code(code.id, CodeStatusRequest(reason="risk"), db, "test-admin")
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 500)
        async with self.sessions() as db:
            await void_code(code.id, CodeStatusRequest(reason="cancel"), db, "test-admin")
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 500)
        request = CodeRefundRequest(reason="approved unused quota refund", idempotency_key="refund-1")
        async with self.sessions() as db:
            first = await refund_code_reservation(code.id, request, db, "test-admin")
        async with self.sessions() as db:
            replay = await refund_code_reservation(code.id, request, db, "test-admin")
        self.assertEqual(first, replay)
        self.assertEqual(first["released"], 400)
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 900)
        self.assertEqual(await self.count(QuotaTx, QuotaTx.transaction_type == "code_release"), 1)

    async def test_legacy_unknown_reservation_cannot_refund(self):
        from app.services.commercial_operations import release_unused_diamond_quota
        legacy = RedeemCode(id=99, code_type="diamonds", agent_id=1, status="void",
                            value=100, max_uses=10, used_count=2, reserved_total=None)
        async with self.sessions() as db:
            with self.assertRaises(HTTPException):
                await release_unused_diamond_quota(db, legacy, "test-admin", "legacy", "legacy-refund")

    async def test_legacy_unknown_reservation_is_not_fabricated(self):
        code = RedeemCode(value=100, max_uses=10, used_count=2)
        summary = reservation_summary(code)
        self.assertEqual(summary["used_total"], 200)
        self.assertIsNone(summary["reserved_total"])
        self.assertIsNone(summary["remaining_reserved"])


class TestLegacyMigration(AssetTestCase):
    async def before_stage_b(self):
        # Synthetic OLD-format data in the disposable test schema only.
        await self.admin.execute("INSERT INTO agents(id,name,agent_code,diamond_quota,license_balance) VALUES (500,'legacy','legacy',900,9)")
        await self.admin.execute("INSERT INTO redeem_codes(id,code_prefix,code_hash,code_type,agent_id,value,max_uses,used_count,status) VALUES (500,'test','synthetic-legacy-hash','diamonds',500,100,10,2,'active')")
        await self.admin.execute("INSERT INTO agent_license_transactions(agent_id,transaction_type,amount,balance_before,balance_after) VALUES (500,'old',-1,10,9)")

    async def test_migration_preserves_historical_balances_and_unknown_reservation(self):
        agent = await self.row(Agent, 500)
        self.assertEqual((agent.diamond_quota, agent.license_balance), (900, 9))
        code = await self.row(RedeemCode, 500)
        self.assertEqual((code.max_uses, code.used_count, code.status), (10, 2, "active"))
        self.assertIsNone(code.reserved_total)
        self.assertEqual(await self.count(QuotaTx), 0)
        async with self.sessions() as db:
            old = (await db.execute(select(LicenseTx))).scalar_one()
            self.assertIsNone(old.operator_name)
