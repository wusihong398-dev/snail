from fastapi import HTTPException
from app.models.commercial import Agent, RedeemCode, RedeemCodeUsage, CustomerGroupOwnership
from app.models.commercial_operations import AgentDiamondQuotaTransaction as QuotaTx, AgentLicenseTransaction as LicenseTx
from app.models.diamond import DiamondTransaction
from app.models.user import User
from tests.support import AssetTestCase


class TestCommercialConcurrency(AssetTestCase):
    async def test_multi_use_limit_is_enforced_under_concurrency(self):
        agent = await self.agent()
        code = await self.code(agent.id, uses=10)
        results = await self.parallel(*[
            lambda n=n: self.redeem(code.code, request_id=f"message-{n}") for n in range(12)])
        successes = [r for r in results if not isinstance(r, Exception)]
        self.assertEqual(len(successes), 10)
        self.assertEqual((await self.row(User, successes[0].user_id)).paid_diamonds, 1000)
        self.assertEqual((await self.row(RedeemCode, code.id)).used_count, 10)
        self.assertEqual(await self.count(DiamondTransaction), 10)

    async def test_two_codes_same_existing_user_preserve_bonus(self):
        a, b = await self.agent(), await self.agent()
        c1, c2 = await self.code(a.id), await self.code(b.id)
        user = await self.user(paid=40, bonus=30)
        results = await self.parallel(lambda: self.redeem(c1.code, request_id="a"),
                                      lambda: self.redeem(c2.code, request_id="b"))
        self.assertTrue(all(not isinstance(r, Exception) for r in results))
        final = await self.row(User, user.id)
        self.assertEqual((final.paid_diamonds, final.bonus_diamonds), (240, 30))

    async def test_concurrent_code_creation_cannot_overspend_quota(self):
        agent = await self.agent(quota=100)
        results = await self.parallel(*[lambda: self.code(agent.id) for _ in range(8)])
        self.assertEqual(sum(not isinstance(r, Exception) for r in results), 1)
        self.assertTrue(all(not isinstance(r, Exception) or isinstance(r, HTTPException) for r in results))
        self.assertEqual((await self.row(Agent, agent.id)).diamond_quota, 0)
        self.assertEqual(await self.count(QuotaTx, QuotaTx.transaction_type == "code_reserve"), 1)

    async def test_concurrent_inventory_cannot_go_negative(self):
        agent = await self.agent(licenses=1)
        results = await self.parallel(*[lambda: self.code(agent.id, value=365, kind="group_license") for _ in range(8)])
        self.assertEqual(sum(not isinstance(r, Exception) for r in results), 1)
        self.assertEqual((await self.row(Agent, agent.id)).license_balance, 0)
        self.assertEqual(await self.count(LicenseTx, LicenseTx.transaction_type == "code_reserve"), 1)

    async def test_same_message_multi_use_replay_grants_once(self):
        agent = await self.agent()
        code = await self.code(agent.id, uses=10)
        results = await self.parallel(*[lambda: self.redeem(code.code, request_id="same-message") for _ in range(8)])
        self.assertTrue(all(not isinstance(r, Exception) for r in results))
        self.assertEqual((await self.row(User, results[0].user_id)).paid_diamonds, 100)
        self.assertEqual(await self.count(RedeemCodeUsage), 1)
        self.assertEqual(await self.count(DiamondTransaction), 1)

    async def test_single_use_concurrent_different_requests(self):
        agent = await self.agent()
        code = await self.code(agent.id)
        results = await self.parallel(lambda: self.redeem(code.code, request_id="first"),
                                      lambda: self.redeem(code.code, request_id="second"))
        self.assertEqual(sum(not isinstance(r, Exception) for r in results), 1)
        self.assertEqual(await self.count(DiamondTransaction), 1)

    async def test_different_agents_codes_same_new_user_no_lost_credit(self):
        a, b = await self.agent(), await self.agent()
        c1, c2 = await self.code(a.id), await self.code(b.id)
        results = await self.parallel(lambda: self.redeem(c1.code, request_id="one"),
                                      lambda: self.redeem(c2.code, request_id="two"))
        self.assertTrue(all(not isinstance(r, Exception) for r in results), results)
        self.assertEqual(await self.count(User), 1)
        self.assertEqual((await self.row(User, results[0].user_id)).paid_diamonds, 200)
        self.assertEqual(await self.count(DiamondTransaction), 2)

    async def test_two_customers_cannot_claim_same_group(self):
        a, b = await self.agent(), await self.agent()
        c1 = await self.code(a.id, kind="group_license", value=365)
        c2 = await self.code(b.id, kind="group_license", value=365)
        results = await self.parallel(lambda: self.redeem(c1.code, wx="owner-a", group="shared"),
                                      lambda: self.redeem(c2.code, wx="owner-b", group="shared"))
        self.assertEqual(sum(not isinstance(r, Exception) for r in results), 1)
        self.assertEqual(await self.count(CustomerGroupOwnership), 1)
        self.assertEqual(await self.count(RedeemCodeUsage), 1)
