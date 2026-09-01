"use client";

import type {
  ReactNode
} from "react";

import {
  useMemo,
  useState
} from "react";

import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Breadcrumb,
  Button
} from "antd";

import {
  DashboardOutlined,
  ApiOutlined,
  RobotOutlined,
  UserOutlined,
  TeamOutlined,
  GiftOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BarChartOutlined,
  HeartOutlined,
  SmileOutlined,
  KeyOutlined
} from "@ant-design/icons";

import AuthGuard from "../components/AuthGuard";

import AiTabs from "../ai/components/AiTabs";

import WechatCenter from "./components/WechatCenter";
import GroupCenter from "./components/GroupCenter";
import UserCenter from "./components/UserCenter";
import ShopCenter from "./components/ShopCenter";
import LoveCenter from "./components/LoveCenter";
import BabyCenter from "./components/BabyCenter";
import CommercialCenter from "./components/CommercialCenter";
import SettingsCenter from "./components/SettingsCenter";


const {
  Header,
  Sider,
  Content
} = Layout;


type ModuleKey =
  | "dashboard"
  | "ai"
  | "wechat"
  | "users"
  | "shop"
  | "love"
  | "baby"
  | "commercial"
  | "settings";


type SubKey =
  | "home"
  | "statistics"
  | "ai-center"
  | "wechat-account"
  | "groups"
  | "users-list"
  | "shop-main"
  | "love-main"
  | "baby-main"
  | "commercial-main"
  | "settings-main";


type ModuleConfigItem = {

  title: string;

  icon: ReactNode;

  children: {
    key: SubKey;
    label: string;
    icon?: ReactNode;
  }[];

};


const moduleConfig: Record<
  ModuleKey,
  ModuleConfigItem
> = {


  dashboard: {

    title:
      "数据中心",

    icon:
      <DashboardOutlined />,

    children: [

      {
        key:
          "home",

        label:
          "数据首页",

        icon:
          <DashboardOutlined />
      },

      {
        key:
          "statistics",

        label:
          "数据统计",

        icon:
          <BarChartOutlined />
      }

    ]

  },


  ai: {

    title:
      "AI中心",

    icon:
      <ApiOutlined />,

    children: [

      {
        key:
          "ai-center",

        label:
          "AI管理",

        icon:
          <ApiOutlined />
      }

    ]

  },


  wechat: {

    title:
      "微信机器人",

    icon:
      <RobotOutlined />,

    children: [

      {
        key:
          "wechat-account",

        label:
          "机器人账号",

        icon:
          <RobotOutlined />
      },

      {
        key:
          "groups",

        label:
          "微信群管理",

        icon:
          <TeamOutlined />
      }

    ]

  },


  users: {

    title:
      "用户中心",

    icon:
      <UserOutlined />,

    children: [

      {
        key:
          "users-list",

        label:
          "用户管理",

        icon:
          <UserOutlined />
      }

    ]

  },


  shop: {

    title:
      "商业中心",

    icon:
      <GiftOutlined />,

    children: [

      {
        key:
          "shop-main",

        label:
          "商城管理",

        icon:
          <GiftOutlined />
      }

    ]

  },


  love: {

    title:
      "恋爱系统",

    icon:
      <HeartOutlined />,

    children: [

      {
        key:
          "love-main",

        label:
          "亲密关系管理",

        icon:
          <HeartOutlined />
      }

    ]

  },


  baby: {

    title:
      "宝宝系统",

    icon:
      <SmileOutlined />,

    children: [

      {
        key:
          "baby-main",

        label:
          "宝宝管理",

        icon:
          <SmileOutlined />
      }

    ]

  },


  commercial: {

    title:
      "代理授权",

    icon:
      <KeyOutlined />,

    children: [

      {
        key:
          "commercial-main",

        label:
          "代理授权中心",

        icon:
          <KeyOutlined />
      }

    ]

  },


  settings: {

    title:
      "系统设置",

    icon:
      <SettingOutlined />,

    children: [

      {
        key:
          "settings-main",

        label:
          "系统设置",

        icon:
          <SettingOutlined />
      }

    ]

  }

};


function DashboardHome() {

  return (

    <div>

      <h1
        style={{
          marginTop: 0
        }}
      >
        🐌 蜗牛群聊精灵
      </h1>


      <p
        style={{
          color:
            "#888"
        }}
      >
        微信群智能机器人管理平台
      </p>


      <div
        style={{
          display:
            "grid",

          gridTemplateColumns:
            "repeat(auto-fit, minmax(220px, 1fr))",

          gap:
            16,

          marginTop:
            24
        }}
      >


        <div
          style={{
            background:
              "#fff",

            borderRadius:
              10,

            padding:
              22
          }}
        >

          <div
            style={{
              color:
                "#888"
            }}
          >
            微信机器人
          </div>

          <div
            style={{
              fontSize:
                30,

              fontWeight:
                700,

              marginTop:
                8
            }}
          >
            0
          </div>

        </div>


        <div
          style={{
            background:
              "#fff",

            borderRadius:
              10,

            padding:
              22
          }}
        >

          <div
            style={{
              color:
                "#888"
            }}
          >
            微信群
          </div>

          <div
            style={{
              fontSize:
                30,

              fontWeight:
                700,

              marginTop:
                8
            }}
          >
            0
          </div>

        </div>


        <div
          style={{
            background:
              "#fff",

            borderRadius:
              10,

            padding:
              22
          }}
        >

          <div
            style={{
              color:
                "#888"
            }}
          >
            注册用户
          </div>

          <div
            style={{
              fontSize:
                30,

              fontWeight:
                700,

              marginTop:
                8
            }}
          >
            0
          </div>

        </div>


        <div
          style={{
            background:
              "#fff",

            borderRadius:
              10,

            padding:
              22
          }}
        >

          <div
            style={{
              color:
                "#888"
            }}
          >
            智能调用
          </div>

          <div
            style={{
              fontSize:
                30,

              fontWeight:
                700,

              marginTop:
                8
            }}
          >
            0
          </div>

        </div>


      </div>

    </div>

  );

}


function StatisticsCenter() {

  return (

    <div
      style={{
        background:
          "#fff",

        padding:
          24,

        borderRadius:
          10
      }}
    >

      <h1>
        📊 数据统计
      </h1>

      <p>
        后续这里接入机器人消息量、群活跃度、用户增长、智能调用量等真实统计数据。
      </p>

    </div>

  );

}


export default function AdminPage() {

  const [collapsed, setCollapsed] =
    useState(false);


  const [moduleKey, setModuleKey] =
    useState<ModuleKey>(
      "dashboard"
    );


  const [subKey, setSubKey] =
    useState<SubKey>(
      "home"
    );


  const currentModule =
    moduleConfig[
      moduleKey
    ];


  const sidebarItems =
    useMemo(
      () =>

        currentModule
          .children
          .map(
            item => ({

              key:
                item.key,

              label:
                item.label,

              icon:
                item.icon

            })
          ),

      [
        currentModule
      ]
    );


  function changeModule(
    key: ModuleKey
  ) {

    setModuleKey(
      key
    );


    const firstItem =
      moduleConfig[
        key
      ].children[0];


    setSubKey(
      firstItem.key
    );

  }


  function logout() {

    localStorage.removeItem(
      "token"
    );

    window.location.href =
      "/login";

  }


  function renderContent() {

    switch (
      subKey
    ) {


      case "home":

        return (
          <DashboardHome />
        );


      case "statistics":

        return (
          <StatisticsCenter />
        );


      case "ai-center":

        return (

          <div
            style={{
              background:
                "#fff",

              padding:
                20,

              borderRadius:
                10
            }}
          >

            <h1
              style={{
                marginTop:
                  0
              }}
            >
              🧠 AI中心
            </h1>

            <AiTabs />

          </div>

        );


      case "wechat-account":

        return (
          <WechatCenter />
        );


      case "groups":

        return (
          <GroupCenter />
        );


      case "users-list":

        return (
          <UserCenter />
        );


      case "shop-main":

        return (
          <ShopCenter />
        );


      case "love-main":

        return (
          <LoveCenter />
        );


      case "baby-main":

        return (
          <BabyCenter />
        );


      case "commercial-main":

        return (
          <CommercialCenter />
        );


      case "settings-main":

        return (
          <SettingsCenter />
        );


      default:

        return (
          <DashboardHome />
        );

    }

  }


  return (

    <AuthGuard>

      <Layout
        style={{
          minHeight:
            "100vh"
        }}
      >


        <Sider
          theme="dark"
          width={230}
          collapsed={
            collapsed
          }
          collapsible
          trigger={null}
        >


          <div
            style={{
              height:
                64,

              display:
                "flex",

              alignItems:
                "center",

              justifyContent:
                "center",

              color:
                "#fff",

              fontSize:
                collapsed
                  ? 20
                  : 18,

              fontWeight:
                700,

              whiteSpace:
                "nowrap",

              overflow:
                "hidden"
            }}
          >

            {
              collapsed
                ? "🐌"
                : "🐌 蜗牛群聊精灵"
            }

          </div>


          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[
              subKey
            ]}
            items={
              sidebarItems
            }
            onClick={
              event =>
                setSubKey(
                  event.key as SubKey
                )
            }
          />


        </Sider>


        <Layout>


          <Header
            style={{
              background:
                "#fff",

              padding:
                "0 20px",

              display:
                "flex",

              alignItems:
                "center",

              gap:
                18,

              borderBottom:
                "1px solid #f0f0f0"
            }}
          >


            <Button
              type="text"
              icon={
                collapsed
                  ? (
                    <MenuUnfoldOutlined />
                  )
                  : (
                    <MenuFoldOutlined />
                  )
              }
              onClick={() =>
                setCollapsed(
                  !collapsed
                )
              }
            />


            <Menu
              mode="horizontal"
              selectedKeys={[
                moduleKey
              ]}
              style={{
                flex:
                  1,

                minWidth:
                  0,

                borderBottom:
                  "none"
              }}
              items={[
                {
                  key: "dashboard",
                  icon: moduleConfig.dashboard.icon,
                  label: moduleConfig.dashboard.title
                },
                {
                  key: "ai",
                  icon: moduleConfig.ai.icon,
                  label: moduleConfig.ai.title
                },
                {
                  key: "wechat",
                  icon: moduleConfig.wechat.icon,
                  label: moduleConfig.wechat.title
                },
                {
                  key: "users",
                  icon: moduleConfig.users.icon,
                  label: moduleConfig.users.title
                },
                {
                  key: "shop",
                  icon: moduleConfig.shop.icon,
                  label: moduleConfig.shop.title
                },
                {
                  key: "love",
                  icon: moduleConfig.love.icon,
                  label: moduleConfig.love.title
                },
                {
                  key: "baby",
                  icon: moduleConfig.baby.icon,
                  label: moduleConfig.baby.title
                },
                {
                  key: "commercial",
                  icon: moduleConfig.commercial.icon,
                  label: moduleConfig.commercial.title
                },
                {
                  key: "settings",
                  icon: moduleConfig.settings.icon,
                  label: moduleConfig.settings.title
                }
              ]}
              onClick={
                event =>
                  changeModule(
                    event.key as ModuleKey
                  )
              }
            />


            <Dropdown
              menu={{
                items: [

                  {
                    key:
                      "logout",

                    icon:
                      <LogoutOutlined />,

                    label:
                      "退出登录",

                    onClick:
                      logout
                  }

                ]
              }}
            >

              <Avatar
                style={{
                  cursor:
                    "pointer"
                }}
                icon={
                  <UserOutlined />
                }
              />

            </Dropdown>


          </Header>


          <Content
            style={{
              padding:
                20,

              background:
                "#f5f7fa",

              minHeight:
                "calc(100vh - 64px)"
            }}
          >


            <Breadcrumb
              items={[
                {
                  title:
                    "蜗牛群聊精灵"
                },

                {
                  title:
                    currentModule.title
                },

                {
                  title:
                    currentModule
                      .children
                      .find(
                        item =>
                          item.key
                          === subKey
                      )
                      ?.label
                }
              ]}
            />


            <div
              style={{
                marginTop:
                  20
              }}
            >

              {
                renderContent()
              }

            </div>


          </Content>


        </Layout>


      </Layout>

    </AuthGuard>

  );

}
