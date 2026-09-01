"use client";

import React from "react";

import { ConfigProvider } from "antd";

import { StyleProvider } from "@ant-design/cssinjs";

import zhCN from "antd/locale/zh_CN";


export default function Providers({
  children,
}: {
  children: React.ReactNode;
}) {

  return (

    <StyleProvider hashPriority="high">

      <ConfigProvider
        locale={zhCN}
        theme={{
          token:{
            colorPrimary:"#1677ff",
            borderRadius:8
          }
        }}
      >

        {children}

      </ConfigProvider>

    </StyleProvider>

  );
}
