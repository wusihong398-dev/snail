import {
  DashboardOutlined,
  RobotOutlined,
  TeamOutlined,
  UserOutlined,
  ApiOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  HeartOutlined,
  CrownOutlined,
  GiftOutlined
} from "@ant-design/icons";


export const moduleMenus:any = {


"/":{

title:"数据中心",

icon:<DashboardOutlined />,

children:[

{
key:"/",
label:"数据首页"
},

]

},



"/ai":{

title:"AI中心",

icon:<ApiOutlined />,

children:[

{
key:"/ai",
label:"接口配置"
},

{
key:"/ai/proxy",
label:"网络出口"
},

{
key:"/ai/personality",
label:"AI角色"
}

]

},



"/wechat":{

title:"微信机器人",

icon:<RobotOutlined />,

children:[

{
key:"/wechat",
label:"机器人账号"
},

{
key:"/groups",
label:"群管理"
}

]

},



"/users":{

title:"用户中心",

icon:<UserOutlined />,

children:[

{
key:"/users",
label:"用户管理"
}

]

},



"/shop":{

title:"商业中心",

icon:<GiftOutlined />,

children:[

{
key:"/shop",
label:"商城管理"
}

]

},



"/settings":{

title:"系统设置",

icon:<SettingOutlined />,

children:[

{
key:"/settings",
label:"系统设置"
}

]

}


};
