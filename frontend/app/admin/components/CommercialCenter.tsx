"use client";

import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  message,
  Modal,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tabs,
  Tag,
  Typography
} from "antd";

import {
  DollarOutlined,
  KeyOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  UserOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useMemo,
  useState
} from "react";

import api from "../../lib/api";

const {
  Text,
  Paragraph
} = Typography;


type Agent = {
  id: number;
  name: string;
  agent_code: string;
  agent_type: string;
  commission_rate: number;
  enabled: boolean;
  license_balance: number;
  diamond_quota: number;
  created_at: string | null;
};


type Customer = {
  id: number;
  agent_id: number | null;
  owner_user_id: number;
  name: string | null;
  plan_code: string;
  license_status: string;
  license_started_at: string | null;
  license_expire_at: string | null;
  max_groups: number;
  enabled: boolean;
  created_at: string | null;
};


type CodeItem = {
  id: number;
  code_prefix: string;
  code_type: string;
  agent_id: number | null;
  customer_id: number | null;
  value: number;
  expires_at: string | null;
  max_uses: number;
  used_count: number;
  status: string;
  created_by: string | null;
  created_at: string | null;
};


type Usage = {
  id: number;
  code_id: number;
  agent_id: number | null;
  customer_id: number | null;
  user_id: number | null;
  wx_user_id: string | null;
  group_id: number | null;
  wx_group_id: string | null;
  usage_type: string;
  value: number;
  success: boolean;
  failure_reason: string | null;
  used_at: string | null;
};


type DiamondTransaction = {
  id: number;
  user_id: number;
  transaction_type: string;
  diamond_type: string;
  amount: number;
  paid_before: number;
  paid_after: number;
  bonus_before: number;
  bonus_after: number;
  description: string | null;
  created_at: string | null;
};


type UserItem = {
  id: number;
  wx_user_id: string;
  nickname: string | null;
  paid_diamonds: number;
  bonus_diamonds: number;
};


type MembershipPlan = {
  id: number;
  code: string;
  name: string;
  member_level: string;
  enabled: boolean;
  sort_order: number;
};


type MembershipProduct = {
  id: number;
  plan_id: number;
  name: string;
  duration_days: number;
  price_cents: number;
  diamond_price: number;
  bonus_diamonds: number;
  bonus_grant_mode: string;
  enabled: boolean;
};


export default function CommercialCenter() {

  const [agents, setAgents] =
    useState<Agent[]>([]);

  const [customers, setCustomers] =
    useState<Customer[]>([]);

  const [codes, setCodes] =
    useState<CodeItem[]>([]);

  const [usages, setUsages] =
    useState<Usage[]>([]);

  const [diamondTransactions, setDiamondTransactions] =
    useState<DiamondTransaction[]>([]);

  const [users, setUsers] =
    useState<UserItem[]>([]);

  const [plans, setPlans] =
    useState<MembershipPlan[]>([]);

  const [memberProducts, setMemberProducts] =
    useState<MembershipProduct[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [agentOpen, setAgentOpen] =
    useState(false);

  const [codeOpen, setCodeOpen] =
    useState(false);

  const [newCode, setNewCode] =
    useState<string | null>(null);

  const [agentForm] =
    Form.useForm();

  const [codeForm] =
    Form.useForm();


  const fmt = (
    value: string | null
  ) => {

    if (!value) {
      return "-";
    }

    return new Date(
      value
    ).toLocaleString();

  };


  function getAgentName(
    id: number | null
  ) {

    if (!id) {
      return "-";
    }

    const agent =
      agents.find(
        item => item.id === id
      );

    return agent
      ? agent.name
      : `代理商#${id}`;

  }


  function getUserName(
    id: number | null
  ) {

    if (!id) {
      return "-";
    }

    const user =
      users.find(
        item => item.id === id
      );

    if (!user) {
      return `用户#${id}`;
    }

    return (
      user.nickname
      || user.wx_user_id
      || `用户#${id}`
    );

  }


  function typeName(
    value: string
  ) {

    return ({
      group_license: "群管理授权",
      diamonds: "钻石兑换",
      membership: "会员兑换",
      partner_slot: "伴侣扩容",
      baby_slot: "宝宝扩容"
    } as Record<string, string>)[value]
      || value;

  }


  function statusTag(
    value: string
  ) {

    if (value === "active") {
      return <Tag color="green">未使用</Tag>;
    }

    if (value === "redeemed") {
      return <Tag color="blue">已使用</Tag>;
    }

    if (value === "expired") {
      return <Tag color="orange">已过期</Tag>;
    }

    if (value === "frozen") {
      return <Tag color="red">已冻结</Tag>;
    }

    return <Tag>{value}</Tag>;

  }


  async function loadAll() {

    setLoading(true);

    try {

      const [
        a,
        c,
        k,
        u,
        d,
        usersRes,
        p,
        mp
      ] = await Promise.all([

        api.get(
          "/commercial/agents"
        ),

        api.get(
          "/commercial/customers"
        ),

        api.get(
          "/commercial/codes"
        ),

        api.get(
          "/commercial/code-usages"
        ),

        api.get(
          "/commercial/diamond-transactions"
        ),

        api.get(
          "/users"
        ),

        api.get(
          "/commercial/membership/plans"
        ),

        api.get(
          "/commercial/membership/products"
        )

      ]);

      setAgents(
        Array.isArray(a.data)
          ? a.data
          : []
      );

      setCustomers(
        Array.isArray(c.data)
          ? c.data
          : []
      );

      setCodes(
        Array.isArray(k.data)
          ? k.data
          : []
      );

      setUsages(
        Array.isArray(u.data)
          ? u.data
          : []
      );

      setDiamondTransactions(
        Array.isArray(d.data)
          ? d.data
          : []
      );

      setUsers(
        Array.isArray(usersRes.data)
          ? usersRes.data
          : []
      );

      setPlans(
        Array.isArray(p.data)
          ? p.data
          : []
      );

      setMemberProducts(
        Array.isArray(mp.data)
          ? mp.data
          : []
      );

    } catch (error: any) {

      message.error(
        error?.response?.data?.detail
        || "读取代理授权数据失败"
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadAll();

  }, []);


  async function createAgent() {

    try {

      const values =
        await agentForm.validateFields();

      await api.post(
        "/commercial/agents",
        values
      );

      message.success(
        "代理商创建成功"
      );

      setAgentOpen(false);

      agentForm.resetFields();

      await loadAll();

    } catch (error: any) {

      if (!error?.errorFields) {

        message.error(
          error?.response?.data?.detail
          || "创建代理商失败"
        );

      }

    }

  }


  async function createCode() {

    try {

      const values =
        await codeForm.validateFields();

      const response =
        await api.post(
          "/commercial/codes",
          values
        );

      setNewCode(
        response.data.code
      );

      message.success(
        "授权码生成成功，请立即保存完整代码"
      );

      setCodeOpen(false);

      codeForm.resetFields();

      await loadAll();

    } catch (error: any) {

      if (!error?.errorFields) {

        message.error(
          error?.response?.data?.detail
          || "生成授权码失败"
        );

      }

    }

  }


  const stats =
    useMemo(() => {

      const paidDiamonds =
        users.reduce(
          (
            sum,
            user
          ) =>
            sum
            + Number(
              user.paid_diamonds
              || 0
            ),
          0
        );

      const bonusDiamonds =
        users.reduce(
          (
            sum,
            user
          ) =>
            sum
            + Number(
              user.bonus_diamonds
              || 0
            ),
          0
        );

      return {
        agents:
          agents.length,
        customers:
          customers.length,
        activeCodes:
          codes.filter(
            item =>
              item.status === "active"
          ).length,
        redemptions:
          usages.filter(
            item =>
              item.success
          ).length,
        paidDiamonds,
        bonusDiamonds
      };

    }, [
      agents,
      customers,
      codes,
      usages,
      users
    ]);


  const agentColumns = [

    {
      title: "代理商",
      dataIndex: "name"
    },

    {
      title: "代理编码",
      dataIndex: "agent_code"
    },

    {
      title: "模式",
      dataIndex: "agent_type",
      render: (value: string) => (
        <Tag>
          {
            value === "prepaid"
              ? "预付/买断"
              : value === "hybrid"
                ? "混合模式"
                : "佣金代理"
          }
        </Tag>
      )
    },

    {
      title: "佣金",
      dataIndex: "commission_rate",
      render: (value: number) =>
        `${Number(value || 0) * 100}%`
    },

    {
      title: "授权库存",
      dataIndex: "license_balance"
    },

    {
      title: "钻石销售额度",
      dataIndex: "diamond_quota"
    },

    {
      title: "客户数",
      render: (
        _: unknown,
        record: Agent
      ) =>
        customers.filter(
          customer =>
            customer.agent_id
            === record.id
        ).length
    },

    {
      title: "状态",
      dataIndex: "enabled",
      render: (value: boolean) => (
        <Tag
          color={
            value
              ? "green"
              : "red"
          }
        >
          {
            value
              ? "启用"
              : "停用"
          }
        </Tag>
      )
    },

    {
      title: "创建时间",
      dataIndex: "created_at",
      render: fmt
    }

  ];


  const customerColumns = [

    {
      title: "客户",
      dataIndex: "name",
      render: (
        value: string | null,
        record: Customer
      ) =>
        value
        || `客户#${record.id}`
    },

    {
      title: "所属代理商",
      dataIndex: "agent_id",
      render: getAgentName
    },

    {
      title: "Owner",
      dataIndex: "owner_user_id",
      render: (
        value: number
      ) => (
        <Space direction="vertical" size={0}>
          <span>
            {getUserName(value)}
          </span>
          <Text type="secondary">
            用户ID #{value}
          </Text>
        </Space>
      )
    },

    {
      title: "套餐",
      dataIndex: "plan_code"
    },

    {
      title: "最大群数",
      dataIndex: "max_groups"
    },

    {
      title: "授权状态",
      dataIndex: "license_status",
      render: (value: string) => (
        <Tag
          color={
            value === "active"
              ? "green"
              : "orange"
          }
        >
          {
            value === "active"
              ? "有效"
              : value
          }
        </Tag>
      )
    },

    {
      title: "授权开始",
      dataIndex: "license_started_at",
      render: fmt
    },

    {
      title: "授权到期",
      dataIndex: "license_expire_at",
      render: fmt
    }

  ];


  const codeColumns = [

    {
      title: "ID",
      dataIndex: "id"
    },

    {
      title: "类型",
      dataIndex: "code_type",
      render: (value: string) => (
        <Tag color="blue">
          {typeName(value)}
        </Tag>
      )
    },

    {
      title: "代码前缀",
      dataIndex: "code_prefix"
    },

    {
      title: "所属代理商",
      dataIndex: "agent_id",
      render: getAgentName
    },

    {
      title: "客户ID",
      dataIndex: "customer_id",
      render: (value: number | null) =>
        value
          ? `#${value}`
          : "-"
    },

    {
      title: "数值",
      dataIndex: "value"
    },

    {
      title: "使用次数",
      render: (
        _: unknown,
        record: CodeItem
      ) =>
        `${record.used_count}/${record.max_uses}`
    },

    {
      title: "状态",
      dataIndex: "status",
      render: statusTag
    },

    {
      title: "生成人",
      dataIndex: "created_by",
      render: (
        value: string | null
      ) =>
        value || "-"
    },

    {
      title: "创建时间",
      dataIndex: "created_at",
      render: fmt
    },

    {
      title: "到期时间",
      dataIndex: "expires_at",
      render: fmt
    }

  ];


  const usageColumns = [

    {
      title: "兑换时间",
      dataIndex: "used_at",
      render: fmt
    },

    {
      title: "代码ID",
      dataIndex: "code_id"
    },

    {
      title: "代理商",
      dataIndex: "agent_id",
      render: getAgentName
    },

    {
      title: "类型",
      dataIndex: "usage_type",
      render: (
        value: string
      ) => (
        <Tag color="blue">
          {typeName(value)}
        </Tag>
      )
    },

    {
      title: "微信号",
      dataIndex: "wx_user_id"
    },

    {
      title: "微信群",
      dataIndex: "wx_group_id",
      render: (
        value: string | null
      ) =>
        value || "-"
    },

    {
      title: "客户ID",
      dataIndex: "customer_id",
      render: (
        value: number | null
      ) =>
        value
          ? `#${value}`
          : "-"
    },

    {
      title: "数值",
      dataIndex: "value"
    },

    {
      title: "结果",
      dataIndex: "success",
      render: (value: boolean) => (
        <Tag
          color={
            value
              ? "green"
              : "red"
          }
        >
          {
            value
              ? "成功"
              : "失败"
          }
        </Tag>
      )
    },

    {
      title: "失败原因",
      dataIndex: "failure_reason",
      render: (
        value: string | null
      ) =>
        value || "-"
    }

  ];


  const diamondColumns = [

    {
      title: "时间",
      dataIndex: "created_at",
      render: fmt
    },

    {
      title: "用户",
      dataIndex: "user_id",
      render: (
        value: number
      ) => (
        <Space direction="vertical" size={0}>
          <span>
            {getUserName(value)}
          </span>
          <Text type="secondary">
            #{value}
          </Text>
        </Space>
      )
    },

    {
      title: "类型",
      dataIndex: "diamond_type",
      render: (value: string) => (
        <Tag
          color={
            value === "paid"
              ? "gold"
              : value === "bonus"
                ? "blue"
                : "purple"
          }
        >
          {
            value === "paid"
              ? "付费钻石"
              : value === "bonus"
                ? "奖励钻石"
                : "混合"
          }
        </Tag>
      )
    },

    {
      title: "变动",
      dataIndex: "amount",
      render: (value: number) => (
        <Text
          strong
          type={
            value >= 0
              ? "success"
              : "danger"
          }
        >
          {
            value > 0
              ? `+${value}`
              : value
          }
        </Text>
      )
    },

    {
      title: "付费钻石",
      render: (
        _: unknown,
        record: DiamondTransaction
      ) =>
        `${record.paid_before} → ${record.paid_after}`
    },

    {
      title: "奖励钻石",
      render: (
        _: unknown,
        record: DiamondTransaction
      ) =>
        `${record.bonus_before} → ${record.bonus_after}`
    },

    {
      title: "来源",
      dataIndex: "transaction_type"
    },

    {
      title: "说明",
      dataIndex: "description",
      render: (
        value: string | null
      ) =>
        value || "-"
    }

  ];


  const membershipPlanColumns = [

    {
      title: "方案",
      dataIndex: "name"
    },

    {
      title: "编码",
      dataIndex: "code"
    },

    {
      title: "会员等级",
      dataIndex: "member_level",
      render: (value: string) => (
        <Tag
          color={
            value === "svip"
              ? "gold"
              : value === "vip"
                ? "blue"
                : "default"
          }
        >
          {String(value || "normal").toUpperCase()}
        </Tag>
      )
    },

    {
      title: "状态",
      dataIndex: "enabled",
      render: (value: boolean) => (
        <Tag color={value ? "green" : "red"}>
          {value ? "启用" : "停用"}
        </Tag>
      )
    }

  ];


  const membershipProductColumns = [

    {
      title: "商品",
      dataIndex: "name"
    },

    {
      title: "方案",
      dataIndex: "plan_id",
      render: (value: number) => {
        const plan =
          plans.find(
            item => item.id === value
          );
        return plan
          ? plan.name
          : `方案#${value}`;
      }
    },

    {
      title: "天数",
      dataIndex: "duration_days"
    },

    {
      title: "现金价",
      dataIndex: "price_cents",
      render: (value: number) =>
        `¥${(Number(value || 0) / 100).toFixed(2)}`
    },

    {
      title: "钻石价",
      dataIndex: "diamond_price"
    },

    {
      title: "会员赠钻",
      dataIndex: "bonus_diamonds"
    },

    {
      title: "赠钻方式",
      dataIndex: "bonus_grant_mode",
      render: (value: string) =>
        value === "monthly"
          ? "按月发放"
          : "立即发放"
    },

    {
      title: "状态",
      dataIndex: "enabled",
      render: (value: boolean) => (
        <Tag color={value ? "green" : "red"}>
          {value ? "上架" : "下架"}
        </Tag>
      )
    }

  ];


  return (

    <Card>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16
        }}
      >

        <div>

          <h1 style={{margin: 0}}>
            🔐 代理授权中心
          </h1>

          <div
            style={{
              color: "#888",
              marginTop: 6
            }}
          >
            管理代理商、购买客户、群管理授权码、钻石兑换码、会员商品和完整兑换审计
          </div>

        </div>

        <Space wrap>

          <Button
            icon={<ReloadOutlined />}
            onClick={loadAll}
          >
            刷新
          </Button>

          <Button
            icon={<TeamOutlined />}
            onClick={() => setAgentOpen(true)}
          >
            新增代理商
          </Button>

          <Button
            type="primary"
            icon={<KeyOutlined />}
            onClick={() => setCodeOpen(true)}
          >
            生成授权码
          </Button>

        </Space>

      </div>


      <Row
        gutter={[16, 16]}
        style={{marginBottom: 20}}
      >

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="代理商"
              value={stats.agents}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="购买客户"
              value={stats.customers}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="有效授权码"
              value={stats.activeCodes}
              prefix={<KeyOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="成功兑换"
              value={stats.redemptions}
              prefix={<SafetyCertificateOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="用户付费钻石余额"
              value={stats.paidDiamonds}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="用户奖励钻石余额"
              value={stats.bonusDiamonds}
            />
          </Card>
        </Col>

      </Row>


      <Tabs
        items={[
          {
            key: "agents",
            label: "代理商管理",
            children: (
              <Table
                rowKey="id"
                loading={loading}
                dataSource={agents}
                columns={agentColumns}
                scroll={{x: 1100}}
              />
            )
          },

          {
            key: "customers",
            label: "客户管理",
            children: (
              <Table
                rowKey="id"
                loading={loading}
                dataSource={customers}
                columns={customerColumns}
                scroll={{x: 1150}}
              />
            )
          },

          {
            key: "codes",
            label: "授权码中心",
            children: (
              <Table
                rowKey="id"
                loading={loading}
                dataSource={codes}
                columns={codeColumns}
                scroll={{x: 1350}}
              />
            )
          },

          {
            key: "usages",
            label: "兑换记录",
            children: (
              <Table
                rowKey="id"
                loading={loading}
                dataSource={usages}
                columns={usageColumns}
                scroll={{x: 1350}}
              />
            )
          },

          {
            key: "diamonds",
            label: "钻石流水",
            children: (
              <Table
                rowKey="id"
                loading={loading}
                dataSource={diamondTransactions}
                columns={diamondColumns}
                scroll={{x: 1250}}
              />
            )
          },

          {
            key: "membership",
            label: "会员商品",
            children: (
              <>
                <Card
                  size="small"
                  title="会员方案"
                >
                  <Table
                    rowKey="id"
                    loading={loading}
                    dataSource={plans}
                    columns={membershipPlanColumns}
                    pagination={false}
                  />
                </Card>

                <Card
                  size="small"
                  title="会员售卖商品"
                  style={{marginTop: 16}}
                >
                  <Table
                    rowKey="id"
                    loading={loading}
                    dataSource={memberProducts}
                    columns={membershipProductColumns}
                    scroll={{x: 1050}}
                  />
                </Card>
              </>
            )
          }
        ]}
      />


      <Alert
        style={{marginTop: 16}}
        type="info"
        showIcon
        message="授权码安全规则"
        description="数据库只保存授权码哈希。完整授权码仅在生成成功时显示一次。正式销售的授权码不要通过后台列表重新展示完整内容。"
      />


      <Card
        size="small"
        style={{marginTop: 16}}
        title={
          <Space>
            <SafetyCertificateOutlined />
            群内授权流程
          </Space>
        }
      >

        <Paragraph style={{marginBottom: 0}}>
          代理商生成代码 → 购买者在目标群 <Text code>@机器人 + 授权码</Text> → 微信机器人调用 <Text code>/api/commercial/codes/redeem</Text> → 系统绑定“购买者微信号 + 当前群”，并记录代理商、客户、群、微信号及精确兑换时间。钻石兑换码同样通过此接口到账。
        </Paragraph>

      </Card>


      <Modal
        title="新增代理商"
        open={agentOpen}
        onOk={createAgent}
        onCancel={() => setAgentOpen(false)}
        okText="创建"
        cancelText="取消"
        destroyOnHidden
      >

        <Form
          form={agentForm}
          layout="vertical"
          initialValues={{
            agent_type: "commission",
            commission_rate: 0,
            license_balance: 0,
            diamond_quota: 0
          }}
        >

          <Form.Item
            name="name"
            label="代理商名称"
            rules={[
              {
                required: true,
                message: "请输入代理商名称"
              }
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="agent_code"
            label="代理编码"
            rules={[
              {
                required: true,
                message: "请输入代理编码"
              }
            ]}
          >
            <Input placeholder="例如 YN-LIJIANG-001" />
          </Form.Item>

          <Form.Item
            name="agent_type"
            label="代理模式"
          >
            <Select
              options={[
                {
                  value: "commission",
                  label: "佣金代理"
                },
                {
                  value: "prepaid",
                  label: "预付/买断"
                },
                {
                  value: "hybrid",
                  label: "混合模式"
                }
              ]}
            />
          </Form.Item>

          <Form.Item
            name="commission_rate"
            label="佣金比例（0.2 = 20%）"
          >
            <InputNumber
              min={0}
              max={1}
              step={0.01}
              style={{width: "100%"}}
            />
          </Form.Item>

          <Form.Item
            name="license_balance"
            label="群授权库存"
          >
            <InputNumber
              min={0}
              style={{width: "100%"}}
            />
          </Form.Item>

          <Form.Item
            name="diamond_quota"
            label="钻石销售额度"
          >
            <InputNumber
              min={0}
              style={{width: "100%"}}
            />
          </Form.Item>

        </Form>

      </Modal>


      <Modal
        title="生成授权/兑换码"
        open={codeOpen}
        onOk={createCode}
        onCancel={() => setCodeOpen(false)}
        okText="生成"
        cancelText="取消"
        destroyOnHidden
      >

        <Form
          form={codeForm}
          layout="vertical"
          initialValues={{
            code_type: "group_license",
            expires_hours: 168,
            max_uses: 1,
            value: 365
          }}
        >

          <Form.Item
            name="code_type"
            label="代码类型"
            rules={[
              {
                required: true,
                message: "请选择代码类型"
              }
            ]}
          >
            <Select
              options={[
                {
                  value: "group_license",
                  label: "群管理授权码"
                },
                {
                  value: "diamonds",
                  label: "钻石兑换码"
                },
                {
                  value: "membership",
                  label: "会员兑换码（预留）"
                },
                {
                  value: "partner_slot",
                  label: "伴侣扩容码（预留）"
                },
                {
                  value: "baby_slot",
                  label: "宝宝扩容码（预留）"
                }
              ]}
            />
          </Form.Item>

          <Form.Item
            name="agent_id"
            label="所属代理商"
          >
            <Select
              allowClear
              showSearch
              optionFilterProp="label"
              placeholder="请选择代理商"
              options={
                agents.map(
                  agent => ({
                    value: agent.id,
                    label: `${agent.name}（${agent.agent_code}）`
                  })
                )
              }
            />
          </Form.Item>

          <Form.Item
            name="customer_id"
            label="预绑定客户（可不填）"
          >
            <Select
              allowClear
              showSearch
              optionFilterProp="label"
              placeholder="不预绑定客户"
              options={
                customers.map(
                  customer => ({
                    value: customer.id,
                    label: `${customer.name || `客户#${customer.id}`}（ID ${customer.id}）`
                  })
                )
              }
            />
          </Form.Item>

          <Form.Item
            name="value"
            label="数值"
            extra="群管理授权码：填写授权天数，例如365；钻石兑换码：填写钻石数量。"
          >
            <InputNumber
              min={0}
              style={{width: "100%"}}
            />
          </Form.Item>

          <Form.Item
            name="expires_hours"
            label="授权码有效小时"
          >
            <InputNumber
              min={1}
              max={87600}
              style={{width: "100%"}}
            />
          </Form.Item>

          <Form.Item
            name="max_uses"
            label="最大使用次数"
          >
            <InputNumber
              min={1}
              max={1000}
              style={{width: "100%"}}
            />
          </Form.Item>

          <Form.Item
            name="created_by"
            label="生成人"
          >
            <Input placeholder="例如 平台管理员 / 代理账号" />
          </Form.Item>

        </Form>

      </Modal>


      <Modal
        title="授权码已生成"
        open={!!newCode}
        onCancel={() => setNewCode(null)}
        footer={
          <Button
            type="primary"
            onClick={() => setNewCode(null)}
          >
            已保存
          </Button>
        }
      >

        <Paragraph>
          为了安全，数据库只保存哈希。完整授权码只在生成时显示一次，请现在复制并交给对应购买者：
        </Paragraph>

        <Card>
          <Text
            copyable
            strong
            style={{fontSize: 18}}
          >
            {newCode}
          </Text>
        </Card>

      </Modal>

    </Card>

  );

}
