"use client";

import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Space,
  Tag,
  Descriptions,
  message,
  Spin
} from "antd";

import {
  EditOutlined,
  ReloadOutlined,
  HeartOutlined,
  GiftOutlined,
  SettingOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useState
} from "react";

import api from "../../lib/api";


type SettingItem = {
  id: number;
  setting_key: string;
  setting_value: string;
  value_type: string;
  title: string;
  description: string | null;
  updated_at: string | null;
};


export default function SettingsCenter() {

  const [settings, setSettings] =
    useState<SettingItem[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [editOpen, setEditOpen] =
    useState(false);

  const [current, setCurrent] =
    useState<SettingItem | null>(null);

  const [form] =
    Form.useForm();


  async function loadSettings() {

    setLoading(true);

    try {

      const res =
        await api.get(
          "/system-settings"
        );

      setSettings(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取系统参数失败"
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadSettings();

  }, []);


  function findSetting(
    key:string
  ) {

    return settings.find(
      item =>
        item.setting_key === key
    ) || null;

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


  function openEdit(
    item:SettingItem
  ) {

    setCurrent(
      item
    );

    form.resetFields();


    if (
      item.value_type === "integer"
    ) {

      form.setFieldsValue({
        value:
          Number(
            item.setting_value
          )
      });

    } else if (
      item.value_type === "float"
    ) {

      form.setFieldsValue({
        value:
          Number(
            item.setting_value
          )
      });

    } else {

      form.setFieldsValue({
        value:
          item.setting_value
      });

    }


    setEditOpen(
      true
    );

  }


  async function saveEdit() {

    if (!current) {
      return;
    }

    try {

      const values =
        await form.validateFields();


      let settingValue =
        String(
          values.value
        );


      if (
        current.value_type
        === "integer"
      ) {

        settingValue =
          String(
            Math.floor(
              Number(
                values.value
              )
            )
          );

      }


      if (
        current.value_type
        === "float"
      ) {

        settingValue =
          String(
            Number(
              values.value
            )
          );

      }


      await api.put(
        `/system-settings/${current.setting_key}`,
        {
          setting_value:
            settingValue
        }
      );


      message.success(
        `${current.title}保存成功`
      );


      setEditOpen(
        false
      );

      setCurrent(
        null
      );


      await loadSettings();


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


  function renderValue(
    item:SettingItem | null
  ) {

    if (!item) {

      return (
        <Tag>
          未配置
        </Tag>
      );

    }


    if (
      item.value_type
      === "float"
    ) {

      return (
        <Tag color="blue">
          × {item.setting_value}
        </Tag>
      );

    }


    return (
      <Tag color="purple">
        {item.setting_value}
      </Tag>
    );

  }


  function settingRow(
    item:SettingItem | null
  ) {

    if (!item) {

      return (
        <div>
          参数未找到
        </div>
      );

    }

    return (

      <div
        style={{
          display:"flex",
          justifyContent:"space-between",
          alignItems:"center",
          gap:16
        }}
      >

        <div>

          <div
            style={{
              marginBottom:6
            }}
          >
            {
              renderValue(
                item
              )
            }
          </div>


          <div
            style={{
              color:"#888",
              fontSize:13
            }}
          >
            {
              item.description
              || "-"
            }
          </div>


          <div
            style={{
              color:"#aaa",
              fontSize:12,
              marginTop:4
            }}
          >
            最后更新：
            {
              formatTime(
                item.updated_at
              )
            }
          </div>

        </div>


        <Button
          icon={
            <EditOutlined />
          }
          onClick={() =>
            openEdit(
              item
            )
          }
        >
          编辑
        </Button>

      </div>

    );

  }


  const loveThreshold =
    findSetting(
      "love_intimacy_threshold"
    );

  const marriageThreshold =
    findSetting(
      "marriage_intimacy_threshold"
    );

  const maxPartners =
    findSetting(
      "max_partners"
    );

  const expMultiplier =
    findSetting(
      "gift_exp_multiplier"
    );

  const intimacyMultiplier =
    findSetting(
      "gift_intimacy_multiplier"
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
            ⚙ 系统设置
          </h1>

          <div
            style={{
              color:"#888",
              marginTop:6
            }}
          >
            管理平台基础配置和运营参数
          </div>

        </div>


        <Button
          icon={
            <ReloadOutlined />
          }
          onClick={
            loadSettings
          }
        >
          刷新参数
        </Button>

      </div>


      <Spin
        spinning={
          loading
        }
      >

        <Card
          title={
            <Space>
              <SettingOutlined />
              系统基础设置
            </Space>
          }
          style={{
            marginBottom:20
          }}
        >

          <Descriptions
            bordered
            column={1}
          >

            <Descriptions.Item
              label="系统名称"
            >

              <div>

                <div
                  style={{
                    fontWeight:600
                  }}
                >
                  蜗牛群聊精灵
                </div>

                <div
                  style={{
                    color:"#888",
                    fontSize:13,
                    marginTop:4
                  }}
                >
                  当前后台管理系统名称
                </div>

              </div>

            </Descriptions.Item>


            <Descriptions.Item
              label="API状态"
            >

              <Tag color="green">
                正常
              </Tag>

            </Descriptions.Item>

          </Descriptions>

        </Card>


        <Card
          title={
            <Space>
              <HeartOutlined />
              恋爱与关系参数
            </Space>
          }
          style={{
            marginBottom:20
          }}
        >

          <Descriptions
            bordered
            column={1}
          >

            <Descriptions.Item
              label="恋爱门槛"
            >
              {
                settingRow(
                  loveThreshold
                )
              }
            </Descriptions.Item>


            <Descriptions.Item
              label="结婚门槛"
            >
              {
                settingRow(
                  marriageThreshold
                )
              }
            </Descriptions.Item>


            <Descriptions.Item
              label="最大伴侣数量"
            >
              {
                settingRow(
                  maxPartners
                )
              }
            </Descriptions.Item>

          </Descriptions>

        </Card>


        <Card
          title={
            <Space>
              <GiftOutlined />
              送礼奖励参数
            </Space>
          }
        >

          <Descriptions
            bordered
            column={1}
          >

            <Descriptions.Item
              label="送礼经验倍率"
            >
              {
                settingRow(
                  expMultiplier
                )
              }
            </Descriptions.Item>


            <Descriptions.Item
              label="亲密度倍率"
            >
              {
                settingRow(
                  intimacyMultiplier
                )
              }
            </Descriptions.Item>

          </Descriptions>

        </Card>

      </Spin>


      <Modal
        title={
          current
            ? `编辑 - ${current.title}`
            : "编辑系统参数"
        }
        open={
          editOpen
        }
        onOk={
          saveEdit
        }
        onCancel={() => {

          setEditOpen(
            false
          );

          setCurrent(
            null
          );

        }}
        okText="保存"
        cancelText="取消"
      >

        <Form
          form={
            form
          }
          layout="vertical"
        >

          {
            current
            && current.value_type
            === "integer"
            && (

              <Form.Item
                label={
                  current.title
                }
                name="value"
                rules={[
                  {
                    required:true,
                    message:
                      "请输入数值"
                  }
                ]}
              >

                <InputNumber
                  min={0}
                  precision={0}
                  style={{
                    width:"100%"
                  }}
                />

              </Form.Item>

            )
          }


          {
            current
            && current.value_type
            === "float"
            && (

              <Form.Item
                label={
                  current.title
                }
                name="value"
                rules={[
                  {
                    required:true,
                    message:
                      "请输入倍率"
                  }
                ]}
              >

                <InputNumber
                  min={0}
                  step={0.1}
                  precision={2}
                  style={{
                    width:"100%"
                  }}
                />

              </Form.Item>

            )
          }


          {
            current
            && current.value_type
            !== "integer"
            && current.value_type
            !== "float"
            && (

              <Form.Item
                label={
                  current.title
                }
                name="value"
                rules={[
                  {
                    required:true
                  }
                ]}
              >

                <Input />

              </Form.Item>

            )
          }


          {
            current
            && (

              <div
                style={{
                  background:"#f5f7fa",
                  borderRadius:8,
                  padding:12,
                  color:"#666"
                }}
              >

                {
                  current.description
                  || "暂无说明"
                }

              </div>

            )
          }

        </Form>

      </Modal>

    </Card>

  );

}
