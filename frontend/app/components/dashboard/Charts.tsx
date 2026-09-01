"use client";

import React from "react";

import ReactECharts from "echarts-for-react";


export default function Charts(){


const option = {


tooltip:{
trigger:"axis"
},


xAxis:{
type:"category",
data:[
"周一",
"周二",
"周三",
"周四",
"周五",
"周六",
"周日"
]
},


yAxis:{
type:"value"
},


series:[

{

name:"消息数量",

type:"line",

data:[
1200,
2300,
1800,
3500,
4200,
5600,
6800
],

smooth:true

}

]


};



return (

<ReactECharts

option={option}

style={{
height:350
}}

/>

);


}
