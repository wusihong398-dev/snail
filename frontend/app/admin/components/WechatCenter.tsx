"use client";

import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Switch,
  message
} from "antd";

import {
  ReloadOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useState
} from "react";

import api from "../../lib/api";


type WechatAccount = {
  id: number;
  nickname: string | null;
  wxid: string | null;
  online: boolean | null;
  customer_id: number | null;
  created_at: string | null;
};


export default function WechatCenter() {

  const [list, setList] = useState<WechatAccount[]>([]);

  const [loading, setLoading] = useState(false);

  const [open, setOpen] = useState(false);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [form] = Form.useForm();


  async function load() {

    setLoading(true);

    try {

      const res = await api.get(
        "/wechat/accounts"
      );

      setList(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取微信机器人失败"
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    load();

  }, []);


  function openCreate() {

    setEditingId(null);

    form.resetFields();

    form.setFieldsValue({
      nickname: "未登录机器人",
      wxid: "",
      online: false,
      customer_id: null
    });

    setOpen(true);

  }


  function openEdit(
    account: WechatAccount
  ) {

    setEditingId(account.id);

    form.setFieldsValue({
      nickname:
        account.nickname || "",
      wxid:
        account.wxid || "",
      online:
        Boolean(account.online),
      customer_id:
        account.customer_id
    });

    setOpen(true);

  }


  async function save() {

    try {

      const values =
        await form.validateFields();


      const payload = {
        nickname:
          values.nickname || null,

        wxid:
          values.wxid
            ? values.wxid.trim()
            : null,

        online:
          Boolean(values.online),

        customer_id:
          values.customer_id
            ? Number(values.customer_id)
            : null
      };


      if (editingId) {

        await api.put(
          `/wechat/accounts/${editingId}`,
          payload
        );

        message.success(
          "机器人信息修改成功"
        );

      } else {

        await api.post(
          "/wechat/accounts",
          payload
        );

        message.success(
          "机器人添加成功"
        );

      }


      setOpen(false);

      form.resetFields();

      await load();


    } catch (error:any) {

      if (
        error?.errorFields
      ) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "保存失败"
      );

    }

  }


  async function toggleOnline(
    account: WechatAccount
  ) {

    try {

      const next =
        !Boolean(account.online);

      await api.patch(
        `/wechat/accounts/${account.id}/online`,
        {
          online: next
        }
      );

      message.success(
        next
          ? "已标记为在线"
          : "已标记为离线"
      );

      await load();

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "状态更新失败"
      );

    }

  }


  function remove(
    account: WechatAccount
  ) {

    Modal.confirm({

      title: "删除微信机器人",

      content:
        `确定删除“${account.nickname || "未命名机器人"}”吗？`,

      okText: "删除",

      cancelText: "取消",

      okButtonProps: {
        danger: true
      },

      async onOk() {

        try {

          await api.delete(
            `/wechat/accounts/${account.id}`
          );

          message.success(
            "删除成功"
          );

          await load();

        } catch (error:any) {

          message.error(
            error?.response?.data?.detail
            || "删除失败"
          );

        }

      }

    });

  }


  const columns = [

    {
      title: "微信昵称",
      dataIndex: "nickname",

      render: (
        value: string | null
      ) => (
        value || "未登录机器人"
      )
    },


    {
      title: "微信账号",
      dataIndex: "wxid",

      render: (
        value: string | null
      ) => (
        value || "-"
      )
    },


    {
      title: "状态",
      dataIndex: "online",

      render: (
        value: boolean
      ) => (

        <Tag
          color={
            value
              ? "green"
              : "default"
          }
        >
          {
            value
              ? "在线"
              : "离线"
          }
        </Tag>

      )
    },


    {
      title: "客户ID",
      dataIndex: "customer_id",

      render: (
        value: number | null
      ) => (
        value ?? "-"
      )
    },


    {
      title: "创建时间",
      dataIndex: "created_at",

      render: (
        value: string | null
      ) => {

        if (!value) {
          return "-";
        }

        try {

          return new Date(
            value
          ).toLocaleString();

        } catch {

          return value;

        }

      }
    },


    {
      title: "操作",

      render: (
        _:unknown,
        account:WechatAccount
      ) => (

        <Space wrap>

          <Button
            type="primary"
            onClick={() =>
              toggleOnline(account)
            }
          >
            {
              account.online
                ? "设为离线"
                : "设为在线"
            }
          </Button>


          <Button
            icon={<EditOutlined />}
            onClick={() =>
              openEdit(account)
            }
          >
            编辑
          </Button>


          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() =>
              remove(account)
            }
          >
            删除
          </Button>

        </Space>

      )

    }

  ];


  return (

    <Card>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent:
            "space-between",
          gap: 12,
          marginBottom: 20
        }}
      >

        <div>

          <h1
            style={{
              margin: 0
            }}
          >
            🤖 微信机器人管理
          </h1>

          <div
            style={{
              color: "#888",
              marginTop: 6
            }}
          >
            管理微信机器人账号和登录状态
          </div>

        </div>


        <Space>

          <Button
            icon={<ReloadOutlined />}
            onClick={load}
          >
            刷新
          </Button>


          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openCreate}
          >
            新增机器人
          </Button>

        </Space>

      </div>


      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={list}
        pagination={false}
        locale={{
          emptyText:
            "暂无微信机器人"
        }}
      />


      <Modal
        title={
          editingId
            ? "编辑微信机器人"
            : "新增微信机器人"
        }
        open={open}
        onOk={save}
        onCancel={() => {
          setOpen(false);
          form.resetFields();
        }}
        okText="保存"
        cancelText="取消"
      >

        <Form
          form={form}
          layout="vertical"
        >

          <Form.Item
            label="微信昵称"
            name="nickname"
          >
            <Input
              placeholder="例如：蜗牛小助手"
            />
          </Form.Item>


          <Form.Item
            label="微信账号 / wxid"
            name="wxid"
          >
            <Input
              placeholder="扫码登录成功后可自动写入"
            />
          </Form.Item>


          <Form.Item
            label="所属客户ID"
            name="customer_id"
          >
            <Input
              type="number"
              placeholder="可留空"
            />
          </Form.Item>


          <Form.Item
            label="在线状态"
            name="online"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>


          <div
            style={{
              color: "#999",
              fontSize: 13
            }}
          >
            当前阶段这里管理数据库记录。下一阶段接入微信扫码登录后，昵称、wxid和在线状态会由机器人客户端自动同步。
          </div>

        </Form>

      </Modal>

    </Card>

  );

}
