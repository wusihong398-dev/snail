"use client";
import { Button, DatePicker, Form, Input, Select, Space } from "antd";
import { useState } from "react"; import { DataTable, withDateRange } from "./common"; import { usePaged } from "./usePaged";
export default function UsageManagement() {
  const [filters, setFilters] = useState<Record<string, unknown>>({}); const data = usePaged("/commercial/code-usages", filters);
  return <><Form layout="inline" onFinish={(v) => setFilters(withDateRange(v))}><Form.Item name="agent_id"><Input placeholder="代理ID" allowClear /></Form.Item><Form.Item name="customer_id"><Input placeholder="客户ID" allowClear /></Form.Item><Form.Item name="wx_user_id"><Input placeholder="微信用户" allowClear /></Form.Item>
    <Form.Item name="wx_group_id"><Input placeholder="微信群" allowClear /></Form.Item><Form.Item name="usage_type"><Select allowClear placeholder="类型" style={{width:130}} options={["group_license","diamonds"].map(value=>({value}))}/></Form.Item>
    <Form.Item name="success"><Select allowClear placeholder="结果" style={{width:100}} options={[{value:true,label:"成功"},{value:false,label:"失败"}]}/></Form.Item>
    <Form.Item name="date_range"><DatePicker.RangePicker showTime /></Form.Item>
    <Space><Button htmlType="submit" type="primary">搜索</Button><Button onClick={()=>setFilters({})}>重置</Button></Space></Form>
    <DataTable {...data} onPage={data.load} onRefresh={()=>data.load()} columns={[{title:"ID",dataIndex:"id"},{title:"代理",dataIndex:"agent_id"},{title:"客户",dataIndex:"customer_id"},{title:"微信用户",dataIndex:"wx_user_id"},{title:"微信群",dataIndex:"wx_group_id"},{title:"类型",dataIndex:"usage_type"},{title:"成功",dataIndex:"success",render:v=>v?"是":"否"},{title:"时间",dataIndex:"used_at"}]} /></>;
}
