"use client";


import {
  Layout,
  Avatar,
  Dropdown,
  Breadcrumb
} from "antd";


import {
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from "@ant-design/icons";


import {
  usePathname,
  useRouter
} from "next/navigation";


import {
  useState
} from "react";


import AuthGuard from "./AuthGuard";


import AdminTopNav from "./AdminTopNav";

import AdminSidebar from "./AdminSidebar";


import {
  adminModules
} from "./menuConfig";



const {

Header,

Sider,

Content

}=Layout;





export default function AdminLayout({

children

}:{

children:React.ReactNode

}){


const router=useRouter();

const pathname=usePathname();



const [collapsed,setCollapsed]=useState(false);



const logout=()=>{


localStorage.removeItem(
"token"
);


router.replace(
"/login"
);


};





const currentKey =

Object.keys(adminModules)

.find(

key=>

pathname.startsWith(
adminModules[key].path
)

)

||"dashboard";






return (

<AuthGuard>


<Layout

style={{

minHeight:"100vh"

}}

>



<Sider

theme="dark"

width={230}

collapsed={collapsed}

>


<div

style={{

height:64,

display:"flex",

alignItems:"center",

justifyContent:"center",

color:"#fff",

fontWeight:"bold",

fontSize:18

}}

>

🐌 蜗牛群聊精灵

</div>



<AdminSidebar

moduleKey={currentKey}

pathname={pathname}

router={router}

/>



</Sider>





<Layout>




<Header

style={{

background:"#fff",

display:"flex",

alignItems:"center",

padding:"0 20px",

gap:20

}}

>



<div

style={{

fontSize:20,

cursor:"pointer"

}}

onClick={()=>setCollapsed(!collapsed)}

>

{

collapsed

?

<MenuUnfoldOutlined/>

:

<MenuFoldOutlined/>

}

</div>




<AdminTopNav

currentModule={currentKey}

onChange={(key:string)=>{


router.push(

adminModules[key].path

)


}}

/>





<div

style={{

marginLeft:"auto"

}}

>


<Dropdown

menu={{

items:[

{

key:"logout",

label:"退出登录",

icon:<LogoutOutlined/>,

onClick:logout

}

]

}}

>


<Avatar

icon={<UserOutlined/>}

/>


</Dropdown>



</div>



</Header>







<Content

style={{

padding:20

}}

>


<Breadcrumb

items={[

{

title:"蜗牛群聊精灵"

},

{

title:
adminModules[currentKey].title

}

]}

/>



<div

style={{

marginTop:20

}}

>


{children}


</div>



</Content>





</Layout>


</Layout>


</AuthGuard>

);


}
