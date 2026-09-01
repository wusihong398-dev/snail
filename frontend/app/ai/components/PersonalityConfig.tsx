"use client";


import {
  Card,
  Form,
  Input,
  Select,
  Button,
  message
} from "antd";


import {
  useState
} from "react";



export default function PersonalityConfig(){


const [form]=Form.useForm();


const [saving,setSaving]=useState(false);





const defaultPrompt=`

你是蜗牛小精灵。

交流规则：

1. 称呼用户为“宝子”
2. 语气亲切、温暖、有耐心
3. 回复自然，不要机械
4. 不透露底层模型名称
5. 不提及 DeepSeek、ChatGPT、OpenAI 等平台
6. 不说自己是语言模型
7. 像贴心朋友一样帮助用户

示例：

宝子你好呀～😊
有什么问题都可以告诉我哦～
我来帮你看看。

`;





async function save(){


setSaving(true);


try{


// 后续接后端接口

console.log(
await form.validateFields()
);



message.success(
"AI角色保存成功"
);



}catch(e){


message.error(
"保存失败"
);


}


setSaving(false);


}






return (

<Card

title="🤖 AI角色设置"

>


<Form

form={form}

layout="vertical"

initialValues={{

name:"蜗牛小精灵",

nickname:"宝子",

style:"亲切陪伴",

prompt:defaultPrompt

}}

>



<Form.Item

label="角色名称"

name="name"

>

<Input/>

</Form.Item>




<Form.Item

label="用户称呼"

name="nickname"

>

<Input/>

</Form.Item>




<Form.Item

label="交流风格"

name="style"

>

<Select

options={[

{
label:"亲切陪伴",
value:"亲切陪伴"
},

{
label:"专业助手",
value:"专业助手"
},

{
label:"老师模式",
value:"老师模式"
},

{
label:"客服模式",
value:"客服模式"
}

]}

/>

</Form.Item>





<Form.Item

label="系统提示词"

name="prompt"

>

<Input.TextArea

rows={12}

/>

</Form.Item>




<Button

type="primary"

loading={saving}

onClick={save}

>

保存角色

</Button>



</Form>


</Card>

);


}
