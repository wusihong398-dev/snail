"use client";
import { Button, DatePicker, Form, Input, Select, Space } from "antd"; import { useState } from "react";
import { DataTable, withDateRange } from "./common"; import { usePaged } from "./usePaged";
export default function DiamondLedger(){ const [filters,setFilters]=useState<Record<string,unknown>>({}); const data=usePaged("/commercial/diamond-transactions",filters);
 return <><Form layout="inline" onFinish={v=>setFilters(withDateRange(v))}><Form.Item name="user_id"><Input placeholder="用户ID"/></Form.Item><Form.Item name="wx_user_id"><Input placeholder="微信号"/></Form.Item>
 <Form.Item name="diamond_type"><Select allowClear placeholder="钻石类型" style={{width:130}} options={["paid","bonus","mixed"].map(value=>({value}))}/></Form.Item><Form.Item name="transaction_type"><Input placeholder="流水类型"/></Form.Item>
 <Form.Item name="date_range"><DatePicker.RangePicker showTime /></Form.Item>
 <Space><Button type="primary" htmlType="submit">搜索</Button><Button onClick={()=>setFilters({})}>重置</Button></Space></Form><DataTable {...data} onPage={data.load} onRefresh={()=>data.load()} columns={[{title:"ID",dataIndex:"id"},{title:"用户",dataIndex:"user_id"},{title:"微信号",dataIndex:"wx_user_id"},{title:"类型",dataIndex:"diamond_type"},{title:"操作",dataIndex:"transaction_type"},{title:"变动",dataIndex:"amount"},{title:"付费 before/after",render:(_,r)=>`${r.paid_before} / ${r.paid_after}`},{title:"奖励 before/after",render:(_,r)=>`${r.bonus_before} / ${r.bonus_after}`},{title:"时间",dataIndex:"created_at"}]}/></> }
