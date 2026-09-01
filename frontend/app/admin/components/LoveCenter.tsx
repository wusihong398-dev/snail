"use client";

import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Descriptions,
  Statistic,
  Row,
  Col,
  message,
  Tabs
} from "antd";

import {
  ReloadOutlined,
  HeartOutlined,
  CrownOutlined,
  UserOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useMemo,
  useState
} from "react";

import api from "../../lib/api";


type RelationshipItem = {
  id: number;

  user_id_a: number;
  user_id_b: number;

  intimacy: number;

  relationship_status: string;

  love_started_at: string | null;
  married_at: string | null;

  created_at: string | null;
  updated_at: string | null;
};


type UserItem = {
  id: number;
  wx_user_id: string;
  nickname: string | null;
};


type RelationshipRequestItem = {
  id: number;
  request_type: string;
  sender_user_id: number;
  receiver_user_id: number;
  status: string;
  message: string | null;
  created_at: string | null;
  handled_at: string | null;
};




export default function LoveCenter() {

  const [relationships, setRelationships] =
    useState<RelationshipItem[]>([]);

  const [users, setUsers] =
    useState<UserItem[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [current, setCurrent] =
    useState<RelationshipItem | null>(null);


  const [requests, setRequests] =
    useState<RelationshipRequestItem[]>([]);

  const [loveThreshold, setLoveThreshold] =
    useState(100);

  const [marriageThreshold, setMarriageThreshold] =
    useState(500);


  async function loadRelationships() {

    try {

      const res =
        await api.get(
          "/relationships"
        );

      setRelationships(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取关系数据失败"
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


  async function loadThresholds() {

    try {

      const res =
        await api.get(
          "/system-settings"
        );

      const list =
        Array.isArray(res.data)
          ? res.data
          : [];


      const love =
        list.find(
          (item:any) =>
            item.setting_key
            === "love_intimacy_threshold"
        );


      const marriage =
        list.find(
          (item:any) =>
            item.setting_key
            === "marriage_intimacy_threshold"
        );


      if (love) {

        const value =
          Number(
            love.setting_value
          );

        if (
          Number.isFinite(value)
        ) {
          setLoveThreshold(value);
        }

      }


      if (marriage) {

        const value =
          Number(
            marriage.setting_value
          );

        if (
          Number.isFinite(value)
        ) {
          setMarriageThreshold(value);
        }

      }

    } catch {

      // 接口读取失败时保留默认值
      // 恋爱 100 / 结婚 500

    }

  }


  async function loadRequests() {

    try {

      const res =
        await api.get(
          "/relationship-requests"
        );

      setRequests(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取申请记录失败"
      );

    }

  }


  async function loadAll() {

    setLoading(true);

    try {

      await Promise.all([
        loadRelationships(),
        loadUsers(),
        loadThresholds(),
        loadRequests()
      ]);

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadAll();

  }, []);


  const statistics =
    useMemo(() => {

      const love =
        relationships.filter(
          item =>
            item.relationship_status
            === "love"
        ).length;

      const married =
        relationships.filter(
          item =>
            item.relationship_status
            === "married"
        ).length;

      const totalIntimacy =
        relationships.reduce(
          (
            total,
            item
          ) =>
            total
            + Number(
                item.intimacy || 0
              ),
          0
        );

      return {

        total:
          relationships.length,

        love,

        married,

        totalIntimacy

      };

    }, [
      relationships
    ]);


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
      || `用户 #${user.id}`
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


  function renderStatus(
    value:string
  ) {

    if (
      value === "married"
    ) {

      return (
        <Tag color="gold">
          已结婚
        </Tag>
      );

    }

    if (
      value === "love"
    ) {

      return (
        <Tag color="magenta">
          恋爱中
        </Tag>
      );

    }

    return (
      <Tag>
        普通关系
      </Tag>
    );

  }


  function openDetail(
    item:RelationshipItem
  ) {

    setCurrent(
      item
    );

    setDetailOpen(
      true
    );

  }


  async function setLove(
    item:RelationshipItem
  ) {

    try {

      await api.post(
        "/relationships/love",
        {
          user_id_a:
            item.user_id_a,

          user_id_b:
            item.user_id_b
        }
      );

      message.success(
        "已设置为恋爱关系"
      );

      await loadRelationships();

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "设置恋爱关系失败"
      );

    }

  }


  async function setMarried(
    item:RelationshipItem
  ) {

    try {

      await api.post(
        "/relationships/marry",
        {
          user_id_a:
            item.user_id_a,

          user_id_b:
            item.user_id_b
        }
      );

      message.success(
        "已设置为结婚关系"
      );

      await loadRelationships();

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "设置结婚关系失败"
      );

    }

  }


  function resetRelationship(
    item:RelationshipItem
  ) {

    Modal.confirm({

      title:
        "解除当前关系",

      content:
        `确定解除“${getUserName(item.user_id_a)}”与“${getUserName(item.user_id_b)}”当前的恋爱/婚姻关系吗？亲密度不会清零。`,

      okText:
        "解除",

      cancelText:
        "取消",

      okButtonProps: {
        danger:true
      },


      async onOk() {

        try {

          await api.post(
            "/relationships/reset",
            {
              user_id_a:
                item.user_id_a,

              user_id_b:
                item.user_id_b
            }
          );

          message.success(
            "关系已解除"
          );

          await loadRelationships();

        } catch (error:any) {

          message.error(
            error?.response?.data?.detail
            || "解除关系失败"
          );

        }

      }

    });

  }


  const columns = [

    {
      title:
        "双方用户",

      render:(
        _:unknown,
        item:RelationshipItem
      ) => (

        <div>

          <div
            style={{
              fontWeight:600
            }}
          >
            {
              getUserName(
                item.user_id_a
              )
            }
          </div>

          <div
            style={{
              color:"#999",
              margin:"4px 0"
            }}
          >
            ❤️
          </div>

          <div
            style={{
              fontWeight:600
            }}
          >
            {
              getUserName(
                item.user_id_b
              )
            }
          </div>

        </div>

      )
    },


    {
      title:
        "亲密度",

      dataIndex:
        "intimacy",

      sorter:(
        a:RelationshipItem,
        b:RelationshipItem
      ) =>
        a.intimacy
        - b.intimacy,

      render:(
        value:number
      ) => (

        <Tag color="pink">
          {value}
        </Tag>

      )
    },


    {
      title:
        "当前关系",

      dataIndex:
        "relationship_status",

      render:(
        value:string
      ) => (
        renderStatus(
          value
        )
      )
    },


    {
      title:
        "恋爱开始",

      dataIndex:
        "love_started_at",

      render:(
        value:string | null
      ) => (
        formatTime(
          value
        )
      )
    },


    {
      title:
        "结婚时间",

      dataIndex:
        "married_at",

      render:(
        value:string | null
      ) => (
        formatTime(
          value
        )
      )
    },


    {
      title:
        "操作",

      render:(
        _:unknown,
        item:RelationshipItem
      ) => (

        <Space wrap>

          <Button
            type="primary"
            onClick={() =>
              openDetail(
                item
              )
            }
          >
            查看详情
          </Button>


          {
            item.relationship_status
            === "normal"
            && (

              <Button
                icon={
                  <HeartOutlined />
                }
                onClick={() =>
                  setLove(
                    item
                  )
                }
              >
                设为恋爱
              </Button>

            )
          }


          {
            item.relationship_status
            === "love"
            && (

              <Button
                icon={
                  <CrownOutlined />
                }
                onClick={() =>
                  setMarried(
                    item
                  )
                }
              >
                设为结婚
              </Button>

            )
          }


          {
            item.relationship_status
            !== "normal"
            && (

              <Button
                danger
                onClick={() =>
                  resetRelationship(
                    item
                  )
                }
              >
                解除关系
              </Button>

            )
          }

        </Space>

      )
    }

  ];


  const requestColumns = [

    {
      title: "类型",
      dataIndex: "request_type",
      render: (value:string) => (
        <Tag color={value === "love" ? "magenta" : "gold"}>
          {value === "love" ? "恋爱申请" : "求婚申请"}
        </Tag>
      )
    },

    {
      title: "发起用户",
      dataIndex: "sender_user_id",
      render: (value:number) => (
        getUserName(value)
      )
    },

    {
      title: "接收用户",
      dataIndex: "receiver_user_id",
      render: (value:number) => (
        getUserName(value)
      )
    },

    {
      title: "留言",
      dataIndex: "message",
      render: (value:string | null) => (
        value || "-"
      )
    },

    {
      title: "状态",
      dataIndex: "status",
      render: (value:string) => {

        if (value === "accepted") {
          return <Tag color="green">已接受</Tag>;
        }

        if (value === "rejected") {
          return <Tag color="red">已拒绝</Tag>;
        }

        if (value === "cancelled") {
          return <Tag>已撤回</Tag>;
        }

        return <Tag color="orange">待处理</Tag>;
      }
    },

    {
      title: "申请时间",
      dataIndex: "created_at",
      render: (value:string | null) => (
        formatTime(value)
      )
    },

    {
      title: "处理时间",
      dataIndex: "handled_at",
      render: (value:string | null) => (
        formatTime(value)
      )
    }

  ];


  const relationshipContent = (
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
              title="关系总数"
              value={statistics.total}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="恋爱关系"
              value={statistics.love}
              prefix={<HeartOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="婚姻关系"
              value={statistics.married}
              prefix={<CrownOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="累计亲密度"
              value={statistics.totalIntimacy}
            />
          </Card>
        </Col>

      </Row>

      <Card
        size="small"
        title="亲密度规则"
        style={{
          marginBottom:20
        }}
      >
        <Space size={30} wrap>

          <span>
            普通关系：
            <strong>0+</strong>
          </span>

          <span>
            恋爱门槛：
            <strong>{loveThreshold}</strong>
          </span>

          <span>
            结婚门槛：
            <strong>{marriageThreshold}</strong>
          </span>

        </Space>
      </Card>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={relationships}
        scroll={{
          x:1050
        }}
        locale={{
          emptyText:"暂无亲密度关系"
        }}
      />
    </>
  );


  const requestContent = (
    <>
      <Row
        gutter={[16,16]}
        style={{
          marginBottom:20
        }}
      >

        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="申请总数"
              value={requests.length}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="待处理"
              value={
                requests.filter(
                  item => item.status === "pending"
                ).length
              }
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="已接受"
              value={
                requests.filter(
                  item => item.status === "accepted"
                ).length
              }
            />
          </Card>
        </Col>

      </Row>

      <Table
        rowKey="id"
        loading={loading}
        columns={requestColumns}
        dataSource={requests}
        scroll={{
          x:1100
        }}
        locale={{
          emptyText:"暂无恋爱或求婚申请"
        }}
      />
    </>
  );


  return (

    <Card>

      <div
        style={{
          display:"flex",
          alignItems:"center",
          justifyContent:"space-between",
          marginBottom:20
        }}
      >

        <div>

          <h1
            style={{
              margin:0
            }}
          >
            💕 恋爱系统
          </h1>

          <div
            style={{
              color:"#888",
              marginTop:6
            }}
          >
            管理用户亲密度、恋爱关系和婚姻状态
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
        defaultActiveKey="relationships"
        items={[
          {
            key: "relationships",
            label: "亲密关系管理",
            children: relationshipContent
          },
          {
            key: "requests",
            label: "申请管理",
            children: requestContent
          }
        ]}
      />


      <Modal
        title={
          current
            ? `${getUserName(current.user_id_a)} ❤️ ${getUserName(current.user_id_b)}`
            : "关系详情"
        }
        open={
          detailOpen
        }
        footer={null}
        onCancel={() => {

          setDetailOpen(
            false
          );

          setCurrent(
            null
          );

        }}
        width={680}
      >

        {
          current
          && (

            <Descriptions
              bordered
              column={1}
            >

              <Descriptions.Item
                label="用户A"
              >
                {
                  getUserName(
                    current.user_id_a
                  )
                }
                {" "}
                (#{
                  current.user_id_a
                })
              </Descriptions.Item>


              <Descriptions.Item
                label="用户B"
              >
                {
                  getUserName(
                    current.user_id_b
                  )
                }
                {" "}
                (#{
                  current.user_id_b
                })
              </Descriptions.Item>


              <Descriptions.Item
                label="亲密度"
              >
                <Tag color="pink">
                  {
                    current.intimacy
                  }
                </Tag>
              </Descriptions.Item>


              <Descriptions.Item
                label="当前关系"
              >
                {
                  renderStatus(
                    current.relationship_status
                  )
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="恋爱开始时间"
              >
                {
                  formatTime(
                    current.love_started_at
                  )
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="结婚时间"
              >
                {
                  formatTime(
                    current.married_at
                  )
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="关系创建时间"
              >
                {
                  formatTime(
                    current.created_at
                  )
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="最后更新时间"
              >
                {
                  formatTime(
                    current.updated_at
                  )
                }
              </Descriptions.Item>

            </Descriptions>

          )
        }

      </Modal>

    </Card>

  );

}
