"use client";

import {
  Card,
  Form,
  Input,
  Button,
  message
} from "antd";

import {
  useRouter
} from "next/navigation";

import axios from "axios";


export default function LoginPage(){

  const router = useRouter();


  const onFinish = async(values:any)=>{

    try{

      const res = await axios.post(
        "https://jeyav.cn/api/auth/login",
        null,
        {
          params:{
            username:values.username,
            password:values.password
          }
        }
      );


      localStorage.setItem(
        "token",
        res.data.access_token
      );


      message.success(
        "登录成功"
      );


    router.replace("/admin");


    }catch(error){

      message.error(
        "账号或密码错误"
      );

    }

  };


  return (

    <div

      style={{
        height:"100vh",
        display:"flex",
        justifyContent:"center",
        alignItems:"center",
        background:"#f5f7fa"
      }}

    >


      <Card

        title="🐌 蜗牛群聊精灵管理员登录"

        style={{
          width:400
        }}

      >

        <Form

          layout="vertical"

          onFinish={onFinish}

        >


          <Form.Item

            label="管理员账号"

            name="username"

            rules={[
              {
                required:true,
                message:"请输入账号"
              }
            ]}

          >

            <Input />

          </Form.Item>



          <Form.Item

            label="密码"

            name="password"

            rules={[
              {
                required:true,
                message:"请输入密码"
              }
            ]}

          >

            <Input.Password />

          </Form.Item>



          <Button

            type="primary"

            htmlType="submit"

            block

          >

            登录

          </Button>


        </Form>


      </Card>


    </div>

  );

}
