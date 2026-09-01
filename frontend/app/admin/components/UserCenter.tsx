"use client";

import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Tabs,
  Statistic,
  Row,
  Col,
  Select,
  message
} from "antd";

import {
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  MinusOutlined,
  UserOutlined,
  DollarOutlined,
  TrophyOutlined,
  CrownOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useMemo,
  useState
} from "react";

import api from "../../lib/api";


type UserItem = {
  id: number;
  wx_user_id: string;
  nickname: string | null;
  avatar: string | null;

  level: number;
  coins: number;
  paid_diamonds: number;
  bonus_diamonds: number;
  experience: number;

  is_active: boolean;

  member_level: string;
  member_started_at: string | null;
  member_expire_at: string | null;

  created_at: string | null;
};


export default function UserCenter() {

  const [list, setList] =
    useState<UserItem[]>([]);

  const [loading, setLoading] =
    useState(false);


  const [editOpen, setEditOpen] =
    useState(false);

  const [coinsOpen, setCoinsOpen] =
    useState(false);

  const [experienceOpen, setExperienceOpen] =
    useState(false);

  const [memberOpen, setMemberOpen] =
    useState(false);


  const [current, setCurrent] =
    useState<UserItem | null>(null);

  const [memberUser, setMemberUser] =
    useState<UserItem | null>(null);


  const [editForm] =
    Form.useForm();

  const [coinsForm] =
    Form.useForm();

  const [experienceForm] =
    Form.useForm();

  const [memberForm] =
    Form.useForm();


  async function load() {

    setLoading(true);

    try {

      const res =
        await api.get("/users");

      setList(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error: any) {

      message.error(
        error?.response?.data?.detail
        || "读取用户失败"
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    load();

  }, []);


  const statistics =
    useMemo(() => {

      const active =
        list.filter(
          item => item.is_active
        ).length;

      const coins =
        list.reduce(
          (total, item) =>
            total + Number(item.coins || 0),
          0
        );

      const experience =
        list.reduce(
          (total, item) =>
            total
            + Number(item.experience || 0),
          0
        );


      const vip =
        list.filter(
          item =>
            item.member_level === "vip"
        ).length;


      const svip =
        list.filter(
          item =>
            item.member_level === "svip"
        ).length;


      const normal =
        list.filter(
          item =>
            !item.member_level
            || item.member_level === "normal"
        ).length;


      return {
        total: list.length,
        active,
        coins,
        experience,
        vip,
        svip,
        normal
      };

    }, [list]);


  function formatTime(
    value: string | null
  ) {

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


  function getMemberStatus(
    user: UserItem
  ) {

    if (
      !user.member_level
      || user.member_level === "normal"
    ) {

      return {
        label: "未开通",
        color: "default"
      };

    }


    if (!user.member_expire_at) {

      return {
        label: "数据异常",
        color: "red"
      };

    }


    const expired =
      new Date(
        user.member_expire_at
      ).getTime()
      <= Date.now();


    return {

      label:
        expired
          ? "已到期"
          : "有效",

      color:
        expired
          ? "red"
          : "green"

    };

  }


  function openEdit(
    user: UserItem
  ) {

    setCurrent(user);

    editForm.setFieldsValue({

      nickname:
        user.nickname || "",

      avatar:
        user.avatar || "",

      level:
        user.level || 1,

      coins:
        user.coins || 0,

      experience:
        user.experience || 0,

      is_active:
        Boolean(user.is_active)

    });

    setEditOpen(true);

  }


  async function saveEdit() {

    if (!current) {
      return;
    }

    try {

      const values =
        await editForm.validateFields();


      await api.put(
        `/users/${current.id}`,
        {

          nickname:
            values.nickname || "",

          avatar:
            values.avatar || "",

          level:
            Number(
              values.level || 1
            ),

          coins:
            Number(
              values.coins || 0
            ),

          experience:
            Number(
              values.experience || 0
            ),

          is_active:
            Boolean(
              values.is_active
            )

        }
      );


      message.success(
        "用户资料保存成功"
      );


      setEditOpen(false);

      setCurrent(null);

      await load();


    } catch (error: any) {

      if (error?.errorFields) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "保存失败"
      );

    }

  }


  function openCoins(
    user: UserItem
  ) {

    setCurrent(user);

    coinsForm.resetFields();

    coinsForm.setFieldsValue({
      amount: 100
    });

    setCoinsOpen(true);

  }


  async function saveCoins() {

    if (!current) {
      return;
    }

    try {

      const values =
        await coinsForm.validateFields();

      const amount =
        Number(values.amount);


      if (!amount) {

        message.warning(
          "调整数量不能为0"
        );

        return;

      }


      await api.post(
        `/users/${current.id}/coins`,
        {
          amount
        }
      );


      message.success(
        amount > 0
          ? `已增加 ${amount} 蜗币`
          : `已扣除 ${Math.abs(amount)} 蜗币`
      );


      setCoinsOpen(false);

      setCurrent(null);

      await load();


    } catch (error: any) {

      message.error(
        error?.response?.data?.detail
        || "蜗币调整失败"
      );

    }

  }


  function openExperience(
    user: UserItem
  ) {

    setCurrent(user);

    experienceForm.resetFields();

    experienceForm.setFieldsValue({
      amount: 100
    });

    setExperienceOpen(true);

  }


  async function saveExperience() {

    if (!current) {
      return;
    }

    try {

      const values =
        await experienceForm
          .validateFields();

      const amount =
        Number(values.amount);


      if (!amount) {

        message.warning(
          "调整数量不能为0"
        );

        return;

      }


      await api.post(
        `/users/${current.id}/experience`,
        {
          amount
        }
      );


      message.success(
        amount > 0
          ? `已增加 ${amount} 经验`
          : `已扣除 ${Math.abs(amount)} 经验`
      );


      setExperienceOpen(false);

      setCurrent(null);

      await load();


    } catch (error: any) {

      message.error(
        error?.response?.data?.detail
        || "经验调整失败"
      );

    }

  }


  async function toggleActive(
    user: UserItem
  ) {

    try {

      await api.patch(
        `/users/${user.id}/active`
      );


      message.success(
        user.is_active
          ? "用户已禁用"
          : "用户已启用"
      );


      await load();


    } catch (error: any) {

      message.error(
        error?.response?.data?.detail
        || "状态修改失败"
      );

    }

  }


  function removeUser(
    user: UserItem
  ) {

    Modal.confirm({

      title: "删除用户",

      content:
        `确定删除“${
          user.nickname
          || user.wx_user_id
        }”吗？`,

      okText: "删除",

      cancelText: "取消",

      okButtonProps: {
        danger: true
      },


      async onOk() {

        try {

          await api.delete(
            `/users/${user.id}`
          );


          message.success(
            "用户已删除"
          );


          await load();


        } catch (error: any) {

          message.error(
            error?.response?.data?.detail
            || "删除失败"
          );

        }

      }

    });

  }


  function openMembership(
    user: UserItem
  ) {

    setMemberUser(user);


    memberForm.setFieldsValue({

      member_level:

        user.member_level === "svip"
          ? "svip"
          : "vip",

      days:
        30

    });


    setMemberOpen(true);

  }


  async function saveMembership() {

    if (!memberUser) {
      return;
    }

    try {

      const values =
        await memberForm.validateFields();


      await api.post(
        `/users/${memberUser.id}/membership`,
        {

          member_level:
            values.member_level,

          days:
            Number(values.days)

        }
      );


      message.success(
        "会员设置成功"
      );


      setMemberOpen(false);

      setMemberUser(null);

      await load();


    } catch (error: any) {

      if (error?.errorFields) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "会员设置失败"
      );

    }

  }


  function cancelMembership(
    user: UserItem
  ) {

    Modal.confirm({

      title: "取消会员",

      content:
        `确定取消“${
          user.nickname
          || user.wx_user_id
        }”的会员资格吗？`,

      okText:
        "取消会员",

      cancelText:
        "返回",

      okButtonProps: {
        danger: true
      },


      async onOk() {

        try {

          await api.post(
            `/users/${user.id}/membership`,
            {

              member_level:
                "normal",

              days:
                0

            }
          );


          message.success(
            "会员已取消"
          );


          await load();


        } catch (error: any) {

          message.error(
            error?.response?.data?.detail
            || "取消会员失败"
          );

        }

      }

    });

  }


  const columns = [

    {
      title: "用户",

      render: (
        _: unknown,
        user: UserItem
      ) => (

        <div>

          <div
            style={{
              fontWeight: 600
            }}
          >

            {
              user.nickname
              || "未设置昵称"
            }

          </div>


          <div
            style={{
              color: "#999",
              fontSize: 12,
              marginTop: 3
            }}
          >

            {user.wx_user_id}

          </div>

        </div>

      )
    },


    {
      title: "等级",
      dataIndex: "level",

      render: (
        value: number
      ) => (

        <Tag color="blue">
          Lv.{value || 1}
        </Tag>

      )
    },


    {
      title: "会员",

      render: (
        _: unknown,
        user: UserItem
      ) => {

        if (
          user.member_level
          === "svip"
        ) {

          return (
            <Tag color="gold">
              SVIP
            </Tag>
          );

        }


        if (
          user.member_level
          === "vip"
        ) {

          return (
            <Tag color="purple">
              VIP
            </Tag>
          );

        }


        return (
          <Tag>
            普通
          </Tag>
        );

      }
    },


    {
      title: "蜗币",
      dataIndex: "coins",

      render: (
        value: number
      ) => (
        Number(value || 0)
      )
    },


    {
      title: "钻石",
      render: (
        _: unknown,
        user: UserItem
      ) => (
        <div>
          <div>{Number(user.paid_diamonds || 0) + Number(user.bonus_diamonds || 0)}</div>
          <div style={{fontSize:11,color:"#999"}}>付费 {Number(user.paid_diamonds || 0)} / 赠送 {Number(user.bonus_diamonds || 0)}</div>
        </div>
      )
    },


    {
      title: "经验",
      dataIndex: "experience",

      render: (
        value: number
      ) => (
        Number(value || 0)
      )
    },


    {
      title: "状态",
      dataIndex: "is_active",

      render: (
        value: boolean
      ) => (

        <Tag
          color={
            value
              ? "green"
              : "red"
          }
        >

          {
            value
              ? "正常"
              : "已禁用"
          }

        </Tag>

      )
    },


    {
      title: "注册时间",
      dataIndex: "created_at",

      render: (
        value: string | null
      ) => (
        formatTime(value)
      )
    },


    {
      title: "操作",

      render: (
        _: unknown,
        user: UserItem
      ) => (

        <Space wrap>


          <Button
            icon={
              <EditOutlined />
            }
            onClick={() =>
              openEdit(user)
            }
          >
            编辑
          </Button>


          <Button
            icon={
              <DollarOutlined />
            }
            onClick={() =>
              openCoins(user)
            }
          >
            蜗币
          </Button>


          <Button
            icon={
              <TrophyOutlined />
            }
            onClick={() =>
              openExperience(user)
            }
          >
            经验
          </Button>


          <Button
            icon={
              <CrownOutlined />
            }
            onClick={() =>
              openMembership(user)
            }
          >
            会员
          </Button>


          <Button
            onClick={() =>
              toggleActive(user)
            }
          >

            {
              user.is_active
                ? "禁用"
                : "启用"
            }

          </Button>


          <Button
            danger
            icon={
              <DeleteOutlined />
            }
            onClick={() =>
              removeUser(user)
            }
          >
            删除
          </Button>


        </Space>

      )
    }

  ];


  const memberColumns = [

    {
      title: "用户",

      render: (
        _: unknown,
        user: UserItem
      ) => (

        <div>

          <div
            style={{
              fontWeight: 600
            }}
          >

            {
              user.nickname
              || "未设置昵称"
            }

          </div>

          <div
            style={{
              fontSize: 12,
              color: "#999"
            }}
          >

            {user.wx_user_id}

          </div>

        </div>

      )
    },


    {
      title: "会员等级",
      dataIndex: "member_level",

      render: (
        value: string
      ) => {

        if (value === "svip") {

          return (
            <Tag color="gold">
              SVIP
            </Tag>
          );

        }

        if (value === "vip") {

          return (
            <Tag color="purple">
              VIP
            </Tag>
          );

        }

        return (
          <Tag>
            普通用户
          </Tag>
        );

      }
    },


    {
      title: "开通时间",
      dataIndex: "member_started_at",

      render: (
        value: string | null
      ) => (
        formatTime(value)
      )
    },


    {
      title: "到期时间",
      dataIndex: "member_expire_at",

      render: (
        value: string | null
      ) => (
        formatTime(value)
      )
    },


    {
      title: "会员状态",

      render: (
        _: unknown,
        user: UserItem
      ) => {

        const status =
          getMemberStatus(user);

        return (

          <Tag
            color={
              status.color
            }
          >
            {status.label}
          </Tag>

        );

      }
    },


    {
      title: "操作",

      render: (
        _: unknown,
        user: UserItem
      ) => (

        <Space>


          <Button
            type="primary"
            onClick={() =>
              openMembership(user)
            }
          >

            {
              user.member_level
              && user.member_level
              !== "normal"

                ? "续费/升级"

                : "开通会员"
            }

          </Button>


          {
            user.member_level
            && user.member_level
            !== "normal"
            && (

              <Button
                danger
                onClick={() =>
                  cancelMembership(
                    user
                  )
                }
              >
                取消会员
              </Button>

            )
          }


        </Space>

      )
    }

  ];


  const userListContent = (

    <>

      <Row
        gutter={[16, 16]}
        style={{
          marginBottom: 20
        }}
      >


        <Col
          xs={24}
          sm={12}
          lg={6}
        >

          <Card>

            <Statistic
              title="用户总数"
              value={
                statistics.total
              }
              prefix={
                <UserOutlined />
              }
            />

          </Card>

        </Col>


        <Col
          xs={24}
          sm={12}
          lg={6}
        >

          <Card>

            <Statistic
              title="正常用户"
              value={
                statistics.active
              }
            />

          </Card>

        </Col>


        <Col
          xs={24}
          sm={12}
          lg={6}
        >

          <Card>

            <Statistic
              title="蜗币总量"
              value={
                statistics.coins
              }
            />

          </Card>

        </Col>


        <Col
          xs={24}
          sm={12}
          lg={6}
        >

          <Card>

            <Statistic
              title="经验总量"
              value={
                statistics.experience
              }
            />

          </Card>

        </Col>


      </Row>


      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: 16
        }}
      >

        <Button
          icon={
            <ReloadOutlined />
          }
          onClick={load}
        >
          刷新用户
        </Button>

      </div>


      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={list}
        pagination={false}
        scroll={{
          x: 1300
        }}
        locale={{
          emptyText:
            "暂无用户"
        }}
      />


    </>

  );


  const memberContent = (

    <>

      <Row
        gutter={[16, 16]}
        style={{
          marginBottom: 20
        }}
      >


        <Col
          xs={24}
          md={8}
        >

          <Card>

            <Statistic
              title="VIP用户"
              value={
                statistics.vip
              }
            />

          </Card>

        </Col>


        <Col
          xs={24}
          md={8}
        >

          <Card>

            <Statistic
              title="SVIP用户"
              value={
                statistics.svip
              }
            />

          </Card>

        </Col>


        <Col
          xs={24}
          md={8}
        >

          <Card>

            <Statistic
              title="普通用户"
              value={
                statistics.normal
              }
            />

          </Card>

        </Col>


      </Row>


      <Table
        rowKey="id"
        loading={loading}
        columns={memberColumns}
        dataSource={list}
        pagination={false}
        scroll={{
          x: 900
        }}
      />


    </>

  );


  const walletContent = (

    <Card>

      <h2>
        💰 积分与蜗币
      </h2>


      <Row
        gutter={[16, 16]}
      >

        <Col
          xs={24}
          md={12}
        >

          <Statistic
            title="平台蜗币总量"
            value={
              statistics.coins
            }
          />

        </Col>


        <Col
          xs={24}
          md={12}
        >

          <Statistic
            title="平台用户经验总量"
            value={
              statistics.experience
            }
          />

        </Col>

      </Row>


      <p
        style={{
          marginTop: 20,
          color: "#888"
        }}
      >

        在“用户列表”中可以直接为单个用户增加或扣除蜗币、经验。

      </p>


    </Card>

  );


  return (

    <Card>


      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          marginBottom: 16
        }}
      >

        <div>

          <h1
            style={{
              margin: 0
            }}
          >
            👤 用户中心
          </h1>


          <div
            style={{
              color: "#888",
              marginTop: 6
            }}
          >
            管理用户、会员、等级、蜗币和经验
          </div>


        </div>


        <Button
          icon={
            <ReloadOutlined />
          }
          onClick={load}
        >
          刷新
        </Button>


      </div>


      <Tabs
        items={[
          {
            key: "users",
            label:
              "用户列表",
            children:
              userListContent
          },

          {
            key: "members",
            label:
              "会员管理",
            children:
              memberContent
          },

          {
            key: "wallet",
            label:
              "积分与蜗币",
            children:
              walletContent
          }
        ]}
      />


      <Modal
        title="编辑用户"
        open={editOpen}
        onOk={saveEdit}
        onCancel={() => {

          setEditOpen(false);

          setCurrent(null);

        }}
        okText="保存"
        cancelText="取消"
      >


        <Form
          form={editForm}
          layout="vertical"
        >


          <Form.Item
            label="昵称"
            name="nickname"
          >
            <Input />
          </Form.Item>


          <Form.Item
            label="头像地址"
            name="avatar"
          >
            <Input />
          </Form.Item>


          <Form.Item
            label="等级"
            name="level"
          >

            <InputNumber
              min={1}
              style={{
                width: "100%"
              }}
            />

          </Form.Item>


          <Form.Item
            label="蜗币"
            name="coins"
          >

            <InputNumber
              min={0}
              style={{
                width: "100%"
              }}
            />

          </Form.Item>


          <Form.Item
            label="经验"
            name="experience"
          >

            <InputNumber
              min={0}
              style={{
                width: "100%"
              }}
            />

          </Form.Item>


          <Form.Item
            label="启用账号"
            name="is_active"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>


        </Form>


      </Modal>


      <Modal
        title={
          current
            ? `调整蜗币 - ${
                current.nickname
                || current.wx_user_id
              }`
            : "调整蜗币"
        }
        open={coinsOpen}
        onOk={saveCoins}
        onCancel={() => {

          setCoinsOpen(false);

          setCurrent(null);

        }}
        okText="确定"
        cancelText="取消"
      >


        <Form
          form={coinsForm}
          layout="vertical"
        >


          <Form.Item
            label="调整数量"
            name="amount"
            rules={[
              {
                required: true,
                message:
                  "请输入调整数量"
              }
            ]}
            extra="正数增加，负数扣除，例如：100 或 -100"
          >

            <InputNumber
              style={{
                width: "100%"
              }}
            />

          </Form.Item>


          <Space>


            <Button
              icon={
                <PlusOutlined />
              }
              onClick={() =>
                coinsForm.setFieldValue(
                  "amount",
                  100
                )
              }
            >
              +100
            </Button>


            <Button
              icon={
                <MinusOutlined />
              }
              onClick={() =>
                coinsForm.setFieldValue(
                  "amount",
                  -100
                )
              }
            >
              -100
            </Button>


          </Space>


        </Form>


      </Modal>


      <Modal
        title={
          current
            ? `调整经验 - ${
                current.nickname
                || current.wx_user_id
              }`
            : "调整经验"
        }
        open={experienceOpen}
        onOk={saveExperience}
        onCancel={() => {

          setExperienceOpen(false);

          setCurrent(null);

        }}
        okText="确定"
        cancelText="取消"
      >


        <Form
          form={experienceForm}
          layout="vertical"
        >


          <Form.Item
            label="调整数量"
            name="amount"
            rules={[
              {
                required: true,
                message:
                  "请输入调整数量"
              }
            ]}
            extra="正数增加，负数扣除"
          >

            <InputNumber
              style={{
                width: "100%"
              }}
            />

          </Form.Item>


          <Space>


            <Button
              onClick={() =>
                experienceForm.setFieldValue(
                  "amount",
                  100
                )
              }
            >
              +100
            </Button>


            <Button
              onClick={() =>
                experienceForm.setFieldValue(
                  "amount",
                  -100
                )
              }
            >
              -100
            </Button>


          </Space>


        </Form>


      </Modal>


      <Modal
        title={
          memberUser
            ? `会员管理 - ${
                memberUser.nickname
                || memberUser.wx_user_id
              }`
            : "会员管理"
        }
        open={memberOpen}
        onOk={saveMembership}
        onCancel={() => {

          setMemberOpen(false);

          setMemberUser(null);

        }}
        okText="保存"
        cancelText="取消"
      >


        <Form
          form={memberForm}
          layout="vertical"
        >


          <Form.Item
            label="会员等级"
            name="member_level"
            rules={[
              {
                required: true,
                message:
                  "请选择会员等级"
              }
            ]}
          >

            <Select
              options={[
                {
                  label:
                    "VIP",
                  value:
                    "vip"
                },

                {
                  label:
                    "SVIP",
                  value:
                    "svip"
                }
              ]}
            />

          </Form.Item>


          <Form.Item
            label="增加有效期"
            name="days"
            rules={[
              {
                required: true,
                message:
                  "请选择会员有效期"
              }
            ]}
          >

            <Select
              options={[
                {
                  label:
                    "7天",
                  value:
                    7
                },

                {
                  label:
                    "30天",
                  value:
                    30
                },

                {
                  label:
                    "90天",
                  value:
                    90
                },

                {
                  label:
                    "365天",
                  value:
                    365
                }
              ]}
            />

          </Form.Item>


          {
            memberUser
            && memberUser.member_level
            !== "normal"
            && (

              <div
                style={{
                  background:
                    "#f5f7fa",

                  padding:
                    12,

                  borderRadius:
                    6
                }}
              >

                <div>
                  当前会员：
                  <strong>
                    {" "}
                    {
                      memberUser
                        .member_level
                        .toUpperCase()
                    }
                  </strong>
                </div>


                <div
                  style={{
                    marginTop: 8
                  }}
                >

                  当前到期：

                  {" "}

                  {
                    formatTime(
                      memberUser
                        .member_expire_at
                    )
                  }

                </div>

              </div>

            )
          }


        </Form>


      </Modal>


    </Card>

  );

}
