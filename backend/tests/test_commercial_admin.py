from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from app.models.commercial import Agent, Customer, MembershipPlan, MembershipProduct
from app.routers.commercial import (
    adjust_license, adjust_quota, disable_agent, enable_agent, update_agent,
    get_customer, customer_groups, update_customer, renew_customer, pause_customer, resume_customer,
    list_codes, list_code_usages, list_diamond_transactions,
    freeze_code, unfreeze_code, void_code, refund_code_reservation,
    create_membership_product, list_membership_products, update_membership_product,
    list_agent_license_transactions, list_agent_quota_transactions,
)
from app.schemas.commercial import (
    AgentUpdate, BalanceAdjustment, OperationRequest, CustomerUpdate, CustomerRenewRequest,
    CodeStatusRequest, CodeRefundRequest,
    MembershipProductCreate, MembershipProductUpdate,
)
from tests.support import AssetTestCase


class TestCommercialAdminOperations(AssetTestCase):
    async def test_agent_ledgers_and_membership_product_operations(self):
        agent = await self.agent(quota=100, licenses=2)
        async with self.sessions() as db:
            license_page = await list_agent_license_transactions(
                page=1, page_size=1, agent_id=agent.id, operation="initial",
                actor="test-admin", request_id=None, started_at=None, ended_at=None, db=db)
            quota_page = await list_agent_quota_transactions(
                page=1, page_size=1, agent_id=agent.id, operation="initial",
                actor="test-admin", request_id=None, started_at=None, ended_at=None, db=db)
            plan = (await db.execute(select(MembershipPlan).where(MembershipPlan.code == "vip"))).scalar_one()
            product = await create_membership_product(MembershipProductCreate(
                plan_id=plan.id, name="VIP 30", duration_days=30, price_cents=990,
                diamond_price=100, bonus_diamonds=10, enabled=True), db=db)
        self.assertEqual((license_page["total"], quota_page["total"]), (1, 1))
        update = MembershipProductUpdate(
            plan_id=product.plan_id, name="VIP 30 updated", duration_days=30,
            price_cents=1090, diamond_price=120, bonus_diamonds=20,
            bonus_grant_mode="monthly", enabled=False, sort_order=5,
            reason="catalog update", request_id="product-update-1")
        async with self.sessions() as db:
            first = await update_membership_product(product.id, update, db, "admin")
        async with self.sessions() as db:
            replay = await update_membership_product(product.id, update, db, "admin")
            products = await list_membership_products(db)
        self.assertEqual((first.name, replay.name, replay.enabled),
                         ("VIP 30 updated", "VIP 30 updated", False))
        self.assertEqual(sum(item.id == product.id for item in products), 1)
        self.assertEqual(await self.count(MembershipProduct, MembershipProduct.id == product.id), 1)

    async def test_agent_edit_toggle_adjust_and_idempotency(self):
        agent = await self.agent(quota=100, licenses=2)
        async with self.sessions() as db:
            await update_agent(agent.id, AgentUpdate(name="Edited", agent_type="hybrid", commission_rate=.2,
                reason="contract", request_id="agent-edit-1"), db, "admin")
        request = BalanceAdjustment(change=-2, reason="sale", request_id="license-adjust-1")
        async with self.sessions() as db: first = await adjust_license(agent.id, request, db, "admin")
        async with self.sessions() as db: replay = await adjust_license(agent.id, request, db, "admin")
        self.assertEqual((first["before"], first["change"], first["after"]), (2, -2, 0))
        self.assertEqual(replay["after"], 0)
        async with self.sessions() as db:
            with self.assertRaises(HTTPException):
                await adjust_quota(agent.id, BalanceAdjustment(change=-101, reason="bad", request_id="q-bad"), db, "admin")
        op = OperationRequest(reason="risk", request_id="toggle-1")
        async with self.sessions() as db: await disable_agent(agent.id, op, db, "admin")
        async with self.sessions() as db: await enable_agent(agent.id, OperationRequest(reason="clear", request_id="toggle-2"), db, "admin")
        current = await self.row(Agent, agent.id)
        self.assertEqual((current.name, current.agent_type, float(current.commission_rate), current.enabled), ("Edited", "hybrid", .2, True))

    async def test_customer_detail_groups_renew_pause_resume_and_group_limit(self):
        agent = await self.agent(licenses=1)
        code = await self.code(agent.id, value=30, kind="group_license")
        redeemed = await self.redeem(code.code, group="stage-c-group")
        async with self.sessions() as db:
            detail = await get_customer(redeemed.customer_id, db)
            groups = await customer_groups(redeemed.customer_id, db)
        self.assertEqual((detail["current_groups"], len(groups)), (1, 1))
        async with self.sessions() as db:
            with self.assertRaises(HTTPException):
                await update_customer(redeemed.customer_id, CustomerUpdate(name="x", agent_id=agent.id,
                    plan_code="basic", max_groups=0, reason="invalid", request_id="customer-edit-bad"), db, "admin")
        async with self.sessions() as db:
            await renew_customer(redeemed.customer_id, CustomerRenewRequest(duration_days=30, reason="paid", request_id="renew-1"), db, "admin")
        async with self.sessions() as db: await pause_customer(redeemed.customer_id, OperationRequest(reason="hold", request_id="pause-1"), db, "admin")
        async with self.sessions() as db: await resume_customer(redeemed.customer_id, OperationRequest(reason="ok", request_id="resume-1"), db, "admin")
        self.assertTrue((await self.row(Customer, redeemed.customer_id)).enabled)

    async def test_code_status_refund_and_paginated_lists(self):
        agent = await self.agent(quota=500)
        code = await self.code(agent.id, value=100, uses=5)
        async with self.sessions() as db: await freeze_code(code.id, CodeStatusRequest(reason="risk", request_id="freeze-1"), db, "admin")
        async with self.sessions() as db: await unfreeze_code(code.id, CodeStatusRequest(reason="clear", request_id="unfreeze-1"), db, "admin")
        async with self.sessions() as db: await void_code(code.id, CodeStatusRequest(reason="cancel", request_id="void-1"), db, "admin")
        refund = CodeRefundRequest(reason="refund", idempotency_key="refund-1")
        async with self.sessions() as db: await refund_code_reservation(code.id, refund, db, "admin")
        async with self.sessions() as db: await refund_code_reservation(code.id, refund, db, "admin")
        async with self.sessions() as db:
            with self.assertRaises(HTTPException):
                await unfreeze_code(code.id, CodeStatusRequest(reason="unsafe", request_id="unfreeze-after-refund"), db, "admin")
        async with self.sessions() as db:
            pages = [await list_codes(page=1, page_size=20, db=db), await list_code_usages(page=1, page_size=20, db=db),
                     await list_diamond_transactions(page=1, page_size=20, db=db)]
        for page in pages: self.assertEqual(set(("items", "total", "page", "page_size")) - page.keys(), set())
