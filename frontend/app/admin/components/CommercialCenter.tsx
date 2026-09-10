"use client";
import { Tabs, Typography } from "antd";
import AgentManagement from "./commercial/AgentManagement";
import CustomerManagement from "./commercial/CustomerManagement";
import CodeManagement from "./commercial/CodeManagement";
import UsageManagement from "./commercial/UsageManagement";
import DiamondLedger from "./commercial/DiamondLedger";
import AgentLedger from "./commercial/AgentLedger";
import MembershipProductManagement from "./commercial/MembershipProductManagement";
export default function CommercialCenter() {
  return <div style={{ minWidth: 0 }}><Typography.Title level={3}>代理授权中心</Typography.Title>
    <Tabs destroyOnHidden items={[
      ["agents", "代理商", <AgentManagement key="agents" />], ["customers", "客户", <CustomerManagement key="customers" />],
      ["codes", "授权码", <CodeManagement key="codes" />], ["usages", "兑换记录", <UsageManagement key="usages" />],
      ["diamonds", "钻石流水", <DiamondLedger key="diamonds" />], ["agent-ledger", "代理流水", <AgentLedger key="agent-ledger" />],
      ["products", "会员商品", <MembershipProductManagement key="products" />],
    ].map(([key, label, children]) => ({ key: String(key), label, children }))} /></div>;
}
