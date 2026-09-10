"use client";
import { Alert, Button, Empty, Space, Table } from "antd";
import type { ColumnsType, TablePaginationConfig } from "antd/es/table";
export type Row = Record<string, unknown> & { id: number };
export type PageData = { items: Row[]; total: number; page: number; page_size: number };
export const requestId = () => `admin-${Date.now()}-${Math.random().toString(36).slice(2)}`;
export const withDateRange = (values: Record<string, unknown>, field = "date_range") => {
  const range = values[field] as Array<{ toISOString: () => string }> | undefined;
  const result = { ...values }; delete result[field];
  if (range?.length === 2) { result.started_at = range[0].toISOString(); result.ended_at = range[1].toISOString(); }
  return result;
};
export const errorText = (error: unknown) => {
  const value = error as { response?: { data?: { detail?: string } }; message?: string };
  return value.response?.data?.detail || value.message || "请求失败";
};
export function DataTable({ rows, total, page, page_size, loading, error, columns, onPage, onRefresh }:
  { rows: Row[]; total: number; page: number; page_size: number; loading: boolean; error?: string;
    columns: ColumnsType<Row>; onPage: (page: number, size: number) => void; onRefresh: () => void }) {
  const pagination: TablePaginationConfig = { current: page, pageSize: page_size, total, showSizeChanger: true };
  return <Space direction="vertical" size="middle" style={{ width: "100%" }}>
    {error && <Alert type="error" showIcon message={error} />}
    <Button onClick={onRefresh} loading={loading}>刷新</Button>
    <Table<Row> rowKey="id" size="small" scroll={{ x: "max-content" }} loading={loading}
      columns={columns} dataSource={rows} locale={{ emptyText: <Empty description="暂无数据" /> }}
      pagination={pagination} onChange={(p) => onPage(p.current || 1, p.pageSize || 20)} />
  </Space>;
}
