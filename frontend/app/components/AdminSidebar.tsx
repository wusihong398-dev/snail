"use client";


import {
 Menu
} from "antd";


import {
 adminModules
} from "./menuConfig";



export default function AdminSidebar({

moduleKey,

pathname,

router

}:any){



const config=
adminModules[moduleKey];



return (

<Menu

theme="dark"

mode="inline"

selectedKeys={[pathname]}

items={

config.children

}

/>


);


}
