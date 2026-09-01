"use client";

import {
  Card,
  Tabs,
  Table,
  Tag,
  Space,
  Statistic,
  Row,
  Col,
  Button,
  message
} from "antd";

import {
  ReloadOutlined,
  SmileOutlined,
  HeartOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useMemo,
  useState
} from "react";

import api from "../../lib/api";


type BabyItem = {
  id: number;
  name: string;
  parent_user_id_a: number;
  parent_user_id_b: number;
  gender: string;
  level: number;
  experience: number;
  happiness: number;
  hunger: number;
  health: number;
  born_at: string | null;
  created_at: string | null;
};


type BabyRequestItem = {
  id: number;
  sender_user_id: number;
  receiver_user_id: number;
  status: string;
  baby_name: string | null;
  baby_gender: string;
  message: string | null;
  created_at: string | null;
  handled_at: string | null;
};


type UserItem = {
  id: number;
  wx_user_id: string;
  nickname: string | null;
};


export default function BabyCenter() {

  const [babies, setBabies] =
    useState<BabyItem[]>([]);

  const [requests, setRequests] =
    useState<BabyRequestItem[]>([]);

  const [users, setUsers] =
    useState<UserItem[]>([]);

  const [loading, setLoading] =
    useState(false);


  async function loadBabies() {

    try {

      const res =
        await api.get(
          "/babies"
        );

      setBabies(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取宝宝数据失败"
      );

    }

  }


  async function loadRequests() {

    try {

      const res =
        await api.get(
          "/babies/requests"
        );

      setRequests(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取宝宝申请失败"
      );

    }

  }


  async function loadUsers() {

    try {

      const res =
        await api.get(
          "/users"
        );

      setUsers(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch {

      setUsers([]);

    }

  }


  async function loadAll() {

    setLoading(true);

    try {

      await Promise.all([
        loadBabies(),
        loadRequests(),
        loadUsers()
      ]);

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadAll();

  }, []);


  function getUserName(
    userId:number
  ) {

    const user =
      users.find(
        item =>
          item.id === userId
      );

    if (!user) {

      return `用户 #${userId}`;

    }

    return (
      user.nickname
      || user.wx_user_id
      || `用户 #${userId}`
    );

  }


  function formatTime(
    value:string | null
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


  function renderGender(
    value:string
  ) {

    if (value === "male") {

      return (
        <Tag color="blue">
          男宝宝
        </Tag>
      );

    }

    if (value === "female") {

      return (
        <Tag color="magenta">
          女宝宝
        </Tag>
      );

    }

    return (
      <Tag>
        未设置
      </Tag>
    );

  }


  function renderRequestStatus(
    value:string
  ) {

    if (value === "accepted") {

      return (
        <Tag color="green">
          已接受
        </Tag>
      );

    }

    if (value === "rejected") {

      return (
        <Tag color="red">
          已拒绝
        </Tag>
      );

    }

    if (value === "cancelled") {

      return (
        <Tag>
          已撤回
        </Tag>
      );

    }

    return (
      <Tag color="orange">
        待处理
      </Tag>
    );

  }


  const statistics =
    useMemo(() => {

      const male =
        babies.filter(
          item =>
            item.gender === "male"
        ).length;

      const female =
        babies.filter(
          item =>
            item.gender === "female"
        ).length;

      const pending =
        requests.filter(
          item =>
            item.status === "pending"
        ).length;

      return {
        total:
          babies.length,

        male,

        female,

        pending
      };

    }, [
      babies,
      requests
    ]);


  const babyColumns = [

    {
      title:"宝宝名称",
      dataIndex:"name"
    },

    {
      title:"父母双方",
      render:(
        _:unknown,
        item:BabyItem
      ) => (

        <Space direction="vertical" size={2}>

          <span>
            {getUserName(item.parent_user_id_a)}
            {" "}
            (#{item.parent_user_id_a})
          </span>

          <span>
            ❤️
          </span>

          <span>
            {getUserName(item.parent_user_id_b)}
            {" "}
            (#{item.parent_user_id_b})
          </span>

        </Space>

      )
    },

    {
      title:"性别",
      dataIndex:"gender",
      render:(
        value:string
      ) => (
        renderGender(value)
      )
    },

    {
      title:"等级",
      dataIndex:"level"
    },

    {
      title:"经验",
      dataIndex:"experience"
    },

    {
      title:"快乐",
      dataIndex:"happiness",
      render:(
        value:number
      ) => (
        <Tag color="green">
          {value}
        </Tag>
      )
    },

    {
      title:"饥饿",
      dataIndex:"hunger",
      render:(
        value:number
      ) => (
        <Tag color="orange">
          {value}
        </Tag>
      )
    },

    {
      title:"健康",
      dataIndex:"health",
      render:(
        value:number
      ) => (
        <Tag color="blue">
          {value}
        </Tag>
      )
    },

    {
      title:"出生时间",
      dataIndex:"born_at",
      render:(
        value:string | null
      ) => (
        formatTime(value)
      )
    }

  ];


  const requestColumns = [

    {
      title:"发起用户",
      dataIndex:"sender_user_id",
      render:(
        value:number
      ) => (
        getUserName(value)
      )
    },

    {
      title:"接收用户",
      dataIndex:"receiver_user_id",
      render:(
        value:number
      ) => (
        getUserName(value)
      )
    },

    {
      title:"宝宝名称",
      dataIndex:"baby_name",
      render:(
        value:string | null
      ) => (
        value || "-"
      )
    },

    {
      title:"性别",
      dataIndex:"baby_gender",
      render:(
        value:string
      ) => (
        renderGender(value)
      )
    },

    {
      title:"留言",
      dataIndex:"message",
      render:(
        value:string | null
      ) => (
        value || "-"
      )
    },

    {
      title:"状态",
      dataIndex:"status",
      render:(
        value:string
      ) => (
        renderRequestStatus(value)
      )
    },

    {
      title:"申请时间",
      dataIndex:"created_at",
      render:(
        value:string | null
      ) => (
        formatTime(value)
      )
    },

    {
      title:"处理时间",
      dataIndex:"handled_at",
      render:(
        value:string | null
      ) => (
        formatTime(value)
      )
    }

  ];


  const babyContent = (

    <>

      <Row
        gutter={[16,16]}
        style={{
          marginBottom:20
        }}
      >

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="宝宝总数"
              value={statistics.total}
              prefix={<SmileOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="男宝宝"
              value={statistics.male}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="女宝宝"
              value={statistics.female}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待处理申请"
              value={statistics.pending}
              prefix={<HeartOutlined />}
            />
          </Card>
        </Col>

      </Row>


      <Table
        rowKey="id"
        loading={loading}
        columns={babyColumns}
        dataSource={babies}
        scroll={{
          x:1200
        }}
        locale={{
          emptyText:"暂无宝宝"
        }}
      />

    </>

  );


  const requestContent = (

    <Table
      rowKey="id"
      loading={loading}
      columns={requestColumns}
      dataSource={requests}
      scroll={{
        x:1100
      }}
      locale={{
        emptyText:"暂无宝宝申请"
      }}
    />

  );


  return (

    <Card>

      <div
        style={{
          display:"flex",
          justifyContent:"space-between",
          alignItems:"center",
          marginBottom:16
        }}
      >

        <div>

          <h1
            style={{
              margin:0
            }}
          >
            👶 宝宝系统
          </h1>

          <div
            style={{
              color:"#888",
              marginTop:6
            }}
          >
            管理宝宝、成长状态和宝宝申请
          </div>

        </div>


        <Button
          icon={
            <ReloadOutlined />
          }
          onClick={
            loadAll
          }
        >
          刷新
        </Button>

      </div>


      <Tabs
        defaultActiveKey="babies"
        items={[
          {
            key:"babies",
            label:"宝宝管理",
            children:babyContent
          },
          {
            key:"requests",
            label:"宝宝申请",
            children:requestContent
          }
        ]}
      />

    </Card>

  );

}
