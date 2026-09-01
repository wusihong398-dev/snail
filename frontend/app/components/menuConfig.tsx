import {
  DashboardOutlined,
  ApiOutlined,
  RobotOutlined,
  UserOutlined,
  GiftOutlined,
  SettingOutlined
} from "@ant-design/icons";


export const adminModules:any={


dashboard:{

title:"数据中心",

path:"/",

icon:<DashboardOutlined/>,

children:[

{
key:"/",
label:"数据首页"
},

{
key:"/statistics",
label:"数据统计"
}

]

},




ai:{

title:"AI中心",

path:"/ai",

icon:<ApiOutlined/>,

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
},

{
key:"/ai/statistics",
label:"调用统计"
}

]

},




wechat:{

title:"微信机器人",

path:"/wechat",

icon:<RobotOutlined/>,

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




users:{

title:"用户中心",

path:"/users",

icon:<UserOutlined/>,

children:[

{
key:"/users",
label:"用户管理"
}

]

},





shop:{

title:"商业中心",

path:"/shop",

icon:<GiftOutlined/>,

children:[

{
key:"/shop",
label:"商城管理"
}

]

},




settings:{

title:"系统设置",

path:"/settings",

icon:<SettingOutlined/>,

children:[

{
key:"/settings",
label:"系统设置"
}

]

}


};
