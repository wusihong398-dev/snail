"use client";

import {
  Card,
  Button,
  Space,
  Table,
  Modal,
  Form,
  Input,
  Switch,
  Tag,
  Select,
  message
} from "antd";

import {
  PlusOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useState
} from "react";

import api from "../../lib/api";


type GroupItem = {
  id: number;
  name: string | null;
  group_id: string | null;
  robot_id: number | null;

  ai_enabled: boolean;
  game_enabled: boolean;
  social_enabled: boolean;

  love_enabled: boolean;
  marriage_enabled: boolean;
  baby_enabled: boolean;

  welcome_enabled: boolean;

  welcome_text: string | null;

  system_prompt: string | null;
};


type RobotItem = {
  id: number;
  nickname: string | null;
  wxid: string | null;
  online: boolean | null;
};


export default function GroupCenter() {

  const [list, setList] =
    useState<GroupItem[]>([]);

  const [robots, setRobots] =
    useState<RobotItem[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [open, setOpen] =
    useState(false);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [form] = Form.useForm();


  async function loadGroups() {

    setLoading(true);

    try {

      const res =
        await api.get(
          "/groups"
        );

      setList(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取微信群失败"
      );

    } finally {

      setLoading(false);

    }

  }


  async function loadRobots() {

    try {

      const res =
        await api.get(
          "/wechat/accounts"
        );

      setRobots(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch {

      setRobots([]);

    }

  }


  useEffect(() => {

    loadGroups();
    loadRobots();

  }, []);


  function createGroup() {

    setEditingId(null);

    form.resetFields();

    form.setFieldsValue({

      robot_id: null,

      ai_enabled: true,

      game_enabled: true,

      social_enabled: false,

      love_enabled: false,

      marriage_enabled: false,

      baby_enabled: false,

      welcome_enabled: false,

      welcome_text:
        "宝子欢迎加入群聊呀～",

      system_prompt:
        ""

    });

    setOpen(true);

  }


  function editGroup(
    group: GroupItem
  ) {

    setEditingId(group.id);

    form.setFieldsValue({

      name:
        group.name,

      group_id:
        group.group_id,

      robot_id:
        group.robot_id,

      ai_enabled:
        Boolean(
          group.ai_enabled
        ),

      game_enabled:
        Boolean(
          group.game_enabled
        ),

      social_enabled:
        Boolean(
          group.social_enabled
        ),

      love_enabled:
        Boolean(
          group.love_enabled
        ),

      marriage_enabled:
        Boolean(
          group.marriage_enabled
        ),

      baby_enabled:
        Boolean(
          group.baby_enabled
        ),

      welcome_enabled:
        Boolean(
          group.welcome_enabled
        ),

      welcome_text:
        group.welcome_text,

      system_prompt:
        group.system_prompt

    });

    setOpen(true);

  }


  async function save() {

    try {

      const values =
        await form.validateFields();


      const payload = {

        name:
          values.name,

        group_id:
          values.group_id
            ? values.group_id.trim()
            : null,

        robot_id:
          values.robot_id
            ?? null,

        ai_enabled:
          Boolean(
            values.ai_enabled
          ),

        game_enabled:
          Boolean(
            values.game_enabled
          ),

        social_enabled:
          Boolean(
            values.social_enabled
          ),

        love_enabled:
          Boolean(
            values.love_enabled
          ),

        marriage_enabled:
          Boolean(
            values.marriage_enabled
          ),

        baby_enabled:
          Boolean(
            values.baby_enabled
          ),

        welcome_enabled:
          Boolean(
            values.welcome_enabled
          ),

        welcome_text:
          values.welcome_text
            || null,

        system_prompt:
          values.system_prompt
            || null

      };


      if (editingId) {

        await api.put(
          `/groups/${editingId}`,
          payload
        );

        message.success(
          "微信群修改成功"
        );

      } else {

        await api.post(
          "/groups",
          payload
        );

        message.success(
          "微信群添加成功"
        );

      }


      setOpen(false);

      form.resetFields();

      await loadGroups();


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


  function removeGroup(
    group: GroupItem
  ) {

    Modal.confirm({

      title:
        "删除微信群",

      content:
        `确定删除“${group.name || "未命名群"}”吗？`,

      okText:
        "删除",

      cancelText:
        "取消",

      okButtonProps: {
        danger: true
      },

      async onOk() {

        try {

          await api.delete(
            `/groups/${group.id}`
          );

          message.success(
            "删除成功"
          );

          await loadGroups();

        } catch (error:any) {

          message.error(
            error?.response?.data?.detail
            || "删除失败"
          );

        }

      }

    });

  }


  function getRobotName(
    robotId:number | null
  ) {

    if (!robotId) {

      return "未绑定";

    }

    const robot =
      robots.find(
        item =>
          item.id === robotId
      );

    if (!robot) {

      return `机器人 #${robotId}`;

    }

    return (
      robot.nickname
      || robot.wxid
      || `机器人 #${robot.id}`
    );

  }


  const columns = [

    {
      title:
        "群名称",

      dataIndex:
        "name",

      render: (
        value:string | null
      ) => (
        value || "未命名群"
      )
    },


    {
      title:
        "绑定机器人",

      dataIndex:
        "robot_id",

      render: (
        value:number | null
      ) => (

        <Tag
          color={
            value
              ? "blue"
              : "default"
          }
        >
          {
            getRobotName(value)
          }
        </Tag>

      )

    },


    {
      title:
        "AI聊天",

      dataIndex:
        "ai_enabled",

      render: (
        value:boolean
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
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "游戏",

      dataIndex:
        "game_enabled",

      render: (
        value:boolean
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
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "恋爱",

      dataIndex:
        "love_enabled",

      render: (
        value:boolean
      ) => (

        <Tag
          color={
            value
              ? "magenta"
              : "default"
          }
        >
          {
            value
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "结婚",

      dataIndex:
        "marriage_enabled",

      render: (
        value:boolean
      ) => (

        <Tag
          color={
            value
              ? "purple"
              : "default"
          }
        >
          {
            value
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "宝宝",

      dataIndex:
        "baby_enabled",

      render: (
        value:boolean
      ) => (

        <Tag
          color={
            value
              ? "orange"
              : "default"
          }
        >
          {
            value
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "欢迎语",

      dataIndex:
        "welcome_enabled",

      render: (
        value:boolean
      ) => (

        <Tag
          color={
            value
              ? "cyan"
              : "default"
          }
        >
          {
            value
              ? "开启"
              : "关闭"
          }
        </Tag>

      )

    },


    {
      title:
        "操作",

      render: (
        _:unknown,
        group:GroupItem
      ) => (

        <Space wrap>

          <Button
            icon={
              <EditOutlined />
            }
            onClick={() =>
              editGroup(group)
            }
          >
            编辑
          </Button>


          <Button
            danger
            icon={
              <DeleteOutlined />
            }
            onClick={() =>
              removeGroup(group)
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
          display:
            "flex",

          alignItems:
            "center",

          justifyContent:
            "space-between",

          gap:
            12,

          marginBottom:
            20
        }}
      >

        <div>

          <h1
            style={{
              margin: 0
            }}
          >
            👥 微信群管理
          </h1>

          <div
            style={{
              color:
                "#888",

              marginTop:
                6
            }}
          >
            每个微信群都可以独立配置机器人、AI和互动功能
          </div>

        </div>


        <Space>

          <Button
            icon={
              <ReloadOutlined />
            }
            onClick={() => {

              loadGroups();
              loadRobots();

            }}
          >
            刷新群列表
          </Button>


          <Button
            type="primary"
            icon={
              <PlusOutlined />
            }
            onClick={
              createGroup
            }
          >
            新增群
          </Button>

        </Space>

      </div>


      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={list}
        pagination={false}
        scroll={{
          x: 1100
        }}
        locale={{
          emptyText:
            "暂无微信群"
        }}
      />


      <Modal
        title={
          editingId
            ? "编辑微信群"
            : "新增微信群"
        }
        open={open}
        onOk={save}
        onCancel={() => {

          setOpen(false);

          form.resetFields();

        }}
        okText="保存"
        cancelText="取消"
        width={720}
      >

        <Form
          form={form}
          layout="vertical"
        >


          <Form.Item
            label="群名称"
            name="name"
            rules={[
              {
                required:
                  true,

                message:
                  "请输入群名称"
              }
            ]}
          >
            <Input
              placeholder="例如：蜗牛交流群"
            />
          </Form.Item>


          <Form.Item
            label="微信群ID"
            name="group_id"
          >
            <Input
              placeholder="机器人同步后自动写入，也可以暂时留空"
            />
          </Form.Item>


          <Form.Item
            label="绑定机器人"
            name="robot_id"
          >
            <Select

              allowClear

              placeholder={
                robots.length
                  ? "请选择机器人"
                  : "目前没有机器人"
              }

              options={
                robots.map(
                  robot => ({

                    value:
                      robot.id,

                    label:
                      `${
                        robot.nickname
                        || robot.wxid
                        || `机器人 #${robot.id}`
                      } ${
                        robot.online
                          ? "（在线）"
                          : "（离线）"
                      }`

                  })
                )
              }

            />
          </Form.Item>


          <Card
            size="small"
            title="基础功能"
            style={{
              marginBottom:
                16
            }}
          >

            <Space
              size={32}
              wrap
            >

              <Form.Item
                label="AI聊天"
                name="ai_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>


              <Form.Item
                label="游戏"
                name="game_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>


              <Form.Item
                label="社交系统"
                name="social_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>

            </Space>

          </Card>


          <Card
            size="small"
            title="群互动系统"
            style={{
              marginBottom:
                16
            }}
          >

            <Space
              size={32}
              wrap
            >

              <Form.Item
                label="恋爱"
                name="love_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>


              <Form.Item
                label="结婚"
                name="marriage_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>


              <Form.Item
                label="宝宝"
                name="baby_enabled"
                valuePropName="checked"
                style={{
                  marginBottom: 0
                }}
              >
                <Switch />
              </Form.Item>

            </Space>

          </Card>


          <Card
            size="small"
            title="入群欢迎"
            style={{
              marginBottom:
                16
            }}
          >

            <Form.Item
              label="启用欢迎语"
              name="welcome_enabled"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>


            <Form.Item
              label="欢迎语内容"
              name="welcome_text"
            >
              <Input.TextArea
                rows={4}
                placeholder="例如：宝子欢迎加入群聊呀～"
              />
            </Form.Item>

          </Card>


          <Card
            size="small"
            title="群专属AI角色"
          >

            <Form.Item
              label="群专属提示词"
              name="system_prompt"
              extra="留空则使用系统默认的“蜗牛小精灵”角色设置"
            >
              <Input.TextArea
                rows={6}
                placeholder="例如：在这个群里语气活泼一些，称呼成员为宝子……"
              />
            </Form.Item>

          </Card>


        </Form>

      </Modal>

    </Card>

  );

}
