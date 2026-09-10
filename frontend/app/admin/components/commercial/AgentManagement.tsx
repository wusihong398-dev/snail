"use client";
import { useEffect, useState } from "react";
import { Button, Form, Input, InputNumber, message, Modal, Select, Space, Table } from "antd";
import api from "../../../lib/api";
import { errorText, requestId, Row } from "./common";

export default function AgentManagement() {
  const [rows, setRows] = useState<Row[]>([]); const [loading, setLoading] = useState(false);
  const load = async () => { setLoading(true); try { setRows((await api.get("/commercial/agents")).data); } catch (e) { message.error(errorText(e)); } finally { setLoading(false); } };
  useEffect(() => { void load(); }, []);
  const create = () => { let values = { name: "", agent_code: "", agent_type: "commission", commission_rate: 0, license_balance: 0, diamond_quota: 0 };
    Modal.confirm({ title: "新增代理商", content: <Form layout="vertical" initialValues={values} onValuesChange={(_, all) => values = all}>
      <Form.Item name="name" label="名称" required><Input /></Form.Item><Form.Item name="agent_code" label="代理编码" required><Input /></Form.Item>
      <Form.Item name="agent_type" label="类型"><Select options={["commission", "prepaid", "hybrid"].map(value => ({ value }))} /></Form.Item>
      <Form.Item name="commission_rate" label="佣金比例"><InputNumber min={0} max={1} step={0.01} /></Form.Item>
      <Form.Item name="license_balance" label="初始库存"><InputNumber min={0} /></Form.Item><Form.Item name="diamond_quota" label="初始钻石额度"><InputNumber min={0} /></Form.Item>
    </Form>, async onOk() { try { await api.post("/commercial/agents", values); message.success("新增成功"); await load(); } catch (e) { message.error(errorText(e)); throw e; } } }); };
  const adjust = (r: Row, kind: "license-balance" | "diamond-quota") => { let change = 0, reason = ""; Modal.confirm({ title: kind === "license-balance" ? "调整授权库存" : "调整钻石额度", content: <Space direction="vertical"><InputNumber onChange={v => change = Number(v)} placeholder="正数增加，负数减少" /><Input onChange={e => reason = e.target.value} placeholder="原因" /></Space>, async onOk() { try { await api.post(`/commercial/agents/${r.id}/${kind}`, { change, reason, request_id: requestId() }); message.success("调整成功"); await load(); } catch (e) { message.error(errorText(e)); throw e; } } }); };
  const toggle = (r: Row) => Modal.confirm({ title: r.enabled ? "确认停用代理商？" : "确认启用代理商？", async onOk() { await api.post(`/commercial/agents/${r.id}/${r.enabled ? "disable" : "enable"}`, { reason: "后台状态调整", request_id: requestId() }); message.success("操作成功"); await load(); } });
  const edit = (r: Row) => { let name = String(r.name), agent_type = String(r.agent_type), commission_rate = Number(r.commission_rate), reason = ""; Modal.confirm({ title: "编辑代理商", content: <Space direction="vertical"><Input defaultValue={name} onChange={e => name = e.target.value} /><Select defaultValue={agent_type} style={{ width: 220 }} onChange={v => agent_type = v} options={["commission", "prepaid", "hybrid"].map(value => ({ value }))} /><InputNumber min={0} max={1} step={0.01} defaultValue={commission_rate} onChange={v => commission_rate = Number(v)} /><Input placeholder="原因" onChange={e => reason = e.target.value} /></Space>, async onOk() { await api.put(`/commercial/agents/${r.id}`, { name, agent_type, commission_rate, reason, request_id: requestId() }); message.success("保存成功"); await load(); } }); };
  return <><Space><Button type="primary" onClick={create}>新增代理商</Button><Button onClick={load} loading={loading}>刷新</Button></Space>
    <Table<Row> rowKey="id" loading={loading} scroll={{ x: "max-content" }} dataSource={rows} pagination={{ pageSize: 20 }} columns={[{ title: "名称", dataIndex: "name" }, { title: "编码", dataIndex: "agent_code" }, { title: "类型", dataIndex: "agent_type" }, { title: "佣金", dataIndex: "commission_rate" }, { title: "库存", dataIndex: "license_balance" }, { title: "钻石额度", dataIndex: "diamond_quota" }, { title: "状态", dataIndex: "enabled", render: v => v ? "启用" : "停用" }, { title: "操作", render: (_, r) => <Space><Button onClick={() => edit(r)}>编辑</Button><Button onClick={() => adjust(r, "license-balance")}>调库存</Button><Button onClick={() => adjust(r, "diamond-quota")}>调额度</Button><Button danger={Boolean(r.enabled)} onClick={() => toggle(r)}>{r.enabled ? "停用" : "启用"}</Button></Space> }]} />
  </>;
}
