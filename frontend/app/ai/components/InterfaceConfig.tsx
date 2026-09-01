"use client";

import {
  Table,
  Button,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message
} from "antd";

import {
  useEffect,
  useState
} from "react";


import api from "../../lib/api";



const models:any={

deepseek:[
"deepseek-chat",
"deepseek-reasoner"
],

openai:[
"gpt-5",
"gpt-5-mini",
"gpt-4.1"
],

volcengine:[
"doubao-pro",
"doubao-lite"
]

};



export default function InterfaceConfig(){


const [list,setList]=useState<any[]>([]);

const [proxy,setProxy]=useState<any[]>([]);

const [open,setOpen]=useState(false);

const [form]=Form.useForm();




async function load(){


const a=
await api.get(
"/ai/config/list"
);


setList(
a.data || []
);



const p=
await api.get(
"/proxy/list"
);


setProxy(
p.data || []
);


}



useEffect(()=>{

load();

},[]);





async function save(){


try{


const value=
await form.validateFields();


await api.post(

"/ai/config/create",

value

);



message.success(
"保存成功"
);


setOpen(false);

form.resetFields();

load();



}catch(e){

message.error(
"保存失败"
);

}


}






const columns=[


{
title:"名称",
dataIndex:"display_name"
},


{
title:"供应商",
dataIndex:"provider"
},


{
title:"模型",
dataIndex:"model"
},


{
title:"网络出口",

dataIndex:"proxy_id",

render:(v:number)=>{


if(!v)

return <Tag>
直连
</Tag>



const p=
proxy.find(
x=>x.id===v
);


return (

<Tag color="blue">

{p?.name}

</Tag>

)


}

},


{
title:"状态",

dataIndex:"enabled",

render:(v:boolean)=>

v?

<Tag color="green">
启用
</Tag>

:

<Tag>
关闭
</Tag>


}


];






return (

<div>


<Button

type="primary"

onClick={()=>setOpen(true)}

>

新增AI接口

</Button>




<Table

style={{
marginTop:20
}}

rowKey="id"

columns={columns}

dataSource={list}

/>





<Modal

title="新增AI接口"

open={open}

onOk={save}

onCancel={()=>setOpen(false)}

>


<Form

form={form}

layout="vertical"

>



<Form.Item

name="display_name"

label="用户显示名称"

initialValue="蜗牛小精灵"

>

<Input />

</Form.Item>



<Form.Item

name="provider"

label="平台"

>

<Select

options={[

{
label:"DeepSeek",
value:"deepseek"
},

{
label:"OpenAI",
value:"openai"
},

{
label:"火山方舟",
value:"volcengine"
}

]}

/>

</Form.Item>




<Form.Item

name="api_url"

label="API地址"

>

<Input />

</Form.Item>



<Form.Item

name="api_key"

label="API KEY"

>

<Input.Password />

</Form.Item>



<Form.Item

name="model"

label="模型"

>

<Input />

</Form.Item>




<Form.Item

name="proxy_id"

label="网络出口"

>

<Select

allowClear

placeholder="直连"

options={

proxy.map(

(p:any)=>(

{
label:p.name,
value:p.id
}

)

)

}

/>

</Form.Item>



<Form.Item

name="enabled"

label="启用"

valuePropName="checked"

initialValue={true}

>

<Switch/>

</Form.Item>


</Form>


</Modal>


</div>

);


}
