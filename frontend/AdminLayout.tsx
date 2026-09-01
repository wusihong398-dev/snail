"use client";

import { Layout, Menu } from "antd";

import {
  HomeOutlined,
  UserOutlined
} from "@ant-design/icons";


const {Sider,Content}=Layout;


export default function AdminLayout({
children
}:{
children:React.ReactNode
}){


return (

<Layout
style={{
minHeight:"100vh"
}}
>

<Sider>

<Menu
theme="dark"
items={[
{
key:"1",
icon:<HomeOutlined/>,
label:"首页"
},
{
key:"2",
icon:<UserOutlined/>,
label:"用户"
}
]}
/>

</Sider>


<Content
style={{
padding:40
}}
>

{children}

</Content>


</Layout>

)

}
