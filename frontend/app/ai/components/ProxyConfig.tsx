"use client";


import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Space,
  Tag,
  message
} from "antd";


import {
  useEffect,
  useState
} from "react";


import api from "../../lib/api";




export default function ProxyConfig(){


const [list,setList]=useState<any[]>([]);

const [open,setOpen]=useState(false);

const [loading,setLoading]=useState<number|null>(null);

const [result,setResult]=useState<any>({});

const [form]=Form.useForm();






async function load(){


try{


const res=
await api.get(
"/proxy/list"
);


setList(
res.data || []
);



}catch(e){

message.error(
"读取网络出口失败"
);

}


}




useEffect(()=>{


load();


},[]);







async function save(){


try{


const value=
await form.validateFields();



await api.post(

"/proxy/create",

{

name:value.name,

url:value.url

}

);



message.success(
"保存成功"
);


setOpen(false);

form.resetFields();

load();



}catch(e:any){


message.error(

e?.response?.data?.detail
||
"保存失败"

);


}


}








async function test(id:number){


setLoading(id);


try{


const res=
await api.post(

`/proxy/real-test/${id}`

);



if(
res.data.status==="success"
){


setResult({

...result,

[id]:res.data

});


message.success(
"测试成功"
);


}else{


message.error(
res.data.message
||
"测试失败"
);

}



}catch(e){

message.error(
"测试失败"
);

}



setLoading(null);


}








async function start(id:number){


try{


await api.post(

`/proxy/start/${id}`

);


message.success(
"启动成功"
);


load();



}catch(e){

message.error(
"启动失败"
);

}

}







async function stop(id:number){


try{


await api.post(

`/proxy/stop/${id}`

);


message.success(
"停止成功"
);


load();



}catch(e){

message.error(
"停止失败"
);

}


}







async function remove(id:number){


Modal.confirm({

title:"删除节点",


async onOk(){


await api.delete(

`/proxy/${id}`

);


message.success(
"删除成功"
);


load();


}

});


}






const columns=[


{
title:"名称",

dataIndex:"name"

},



{
title:"协议",

dataIndex:"protocol",

render:(v:string)=>(

<Tag color="blue">

{v || "未知"}

</Tag>

)

},



{
title:"服务器",

dataIndex:"server"

},



{
title:"端口",

dataIndex:"port"

},



{
title:"状态",

dataIndex:"status",

render:(v:string)=>(


v==="可用"

?

<Tag color="green">
可用
</Tag>


:

v==="运行中"

?

<Tag color="blue">
运行中
</Tag>


:

<Tag>
{v || "未测试"}
</Tag>


)

},




{
title:"测试结果",

render:(_:any,r:any)=>{


const d=result[r.id];


if(!d)

return "-";



return (

<div>

<div>
IP:{d.ip}
</div>

<div>
国家:{d.country}
</div>

<div>
延迟:{d.latency}ms
</div>

</div>

)

}


},




{
title:"操作",

render:(_:any,r:any)=>(

<Space wrap>


<Button

loading={
loading===r.id
}

onClick={()=>test(r.id)}

>

测试

</Button>



<Button

type="primary"

onClick={()=>start(r.id)}

>

启动

</Button>



<Button

onClick={()=>stop(r.id)}

>

停止

</Button>



<Button

danger

onClick={()=>remove(r.id)}

>

删除

</Button>



</Space>

)

}


];








return (

<div>


<Button

type="primary"

onClick={()=>setOpen(true)}

>

新增网络出口

</Button>





<Table

style={{

marginTop:20

}}

rowKey="id"

columns={columns}

dataSource={list}

pagination={false}

locale={{

emptyText:"暂无网络出口"

}}

/>







<Modal

title="新增网络出口"

open={open}

onOk={save}

onCancel={()=>setOpen(false)}

>



<Form

form={form}

layout="vertical"

>



<Form.Item

name="name"

label="节点名称"

initialValue="代理节点"

>

<Input/>

</Form.Item>



<Form.Item

name="url"

label="代理链接"

rules={[

{

required:true,

message:"请输入代理链接"

}

]}

>

<Input.TextArea

rows={6}

placeholder="
vmess://
vless://
trojan://
hysteria2://
"

/>

</Form.Item>



</Form>


</Modal>



</div>

);


}
