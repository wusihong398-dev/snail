"use client";

import {
 Tabs
} from "antd";


import InterfaceConfig from "./InterfaceConfig";
import ProxyConfig from "./ProxyConfig";
import PersonalityConfig from "./PersonalityConfig";



export default function AiTabs(){


return (

<Tabs

items={[

{
key:"interface",
label:"接口配置",
children:
<InterfaceConfig/>
},


{
key:"proxy",
label:"网络出口",
children:
<ProxyConfig/>
},


{
key:"personality",
label:"AI角色",
children:
<PersonalityConfig/>
}


]}

/>

);


}
