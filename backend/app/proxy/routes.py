from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

import time
import httpx


from app.database import get_db

from app.models.proxy import ProxyConfig


from app.proxy.link_parser import parse_link


from app.proxy.xray_manager import (
    create_xray_config,
    start_xray,
    stop_xray,
    status_xray
)



router = APIRouter(
    prefix="/proxy",
    tags=["AI网络出口"]
)



# =========================
# 节点列表
# =========================

@router.get("/list")
async def list_proxy(

    db:AsyncSession=Depends(get_db)

):

    result = await db.execute(

        select(ProxyConfig)

    )

    return result.scalars().all()





# =========================
# 新增节点
# =========================

@router.post("/create")
async def create_proxy(

    data:dict,

    db:AsyncSession=Depends(get_db)

):

    url=data.get("url")

    name=data.get(
        "name",
        "代理节点"
    )


    if not url:

        raise HTTPException(
            400,
            "缺少代理链接"
        )


    node=parse_link(url)


    proxy=ProxyConfig(

        name=name,

        protocol=node.get(
            "protocol"
        ),

        url=url,

        server=node.get(
            "server"
        ),

        port=node.get(
            "port"
        ),

        status="未测试"

    )


    db.add(proxy)

    await db.commit()

    await db.refresh(proxy)


    return proxy






# =========================
# 启动代理
# =========================

@router.post("/start/{proxy_id}")
async def start_proxy(

    proxy_id:int,

    db:AsyncSession=Depends(get_db)

):

    proxy=await db.get(
        ProxyConfig,
        proxy_id
    )


    if not proxy:

        raise HTTPException(
            404,
            "节点不存在"
        )


    node=parse_link(
        proxy.url
    )


    create_xray_config(
        node
    )


    result=start_xray()



    if result:


        proxy.status="运行中"

        proxy.enabled=True

        await db.commit()



        return {

            "status":"success",

            "message":
            "代理启动成功"

        }



    return {

        "status":"error",

        "message":
        "启动失败"

    }







# =========================
# 停止代理
# =========================

@router.post("/stop/{proxy_id}")
async def stop_proxy(

    proxy_id:int,

    db:AsyncSession=Depends(get_db)

):


    stop_xray()


    proxy=await db.get(

        ProxyConfig,

        proxy_id

    )


    if proxy:

        proxy.status="已停止"

        proxy.enabled=False

        await db.commit()



    return {

        "status":"success"

    }







# =========================
# Xray状态
# =========================

@router.get("/status/{proxy_id}")
async def status_proxy(

    proxy_id:int

):

    return status_xray()







# =========================
# 真实代理测试
# =========================

@router.post("/real-test/{proxy_id}")
async def real_test(

    proxy_id:int,

    db:AsyncSession=Depends(get_db)

):


    proxy=await db.get(

        ProxyConfig,

        proxy_id

    )


    if not proxy:

        raise HTTPException(
            404,
            "节点不存在"
        )



    try:


        node=parse_link(
            proxy.url
        )


        create_xray_config(
            node
        )


        start_xray()



        start=time.time()



        async with httpx.AsyncClient(

            proxy="socks5://127.0.0.1:10808",

            timeout=15

        ) as client:


            response=await client.get(

                "https://ipinfo.io/json"

            )



        latency=int(

            (time.time()-start)*1000

        )



        data=response.json()



        proxy.status="可用"


        await db.commit()



        return {


            "status":"success",


            "protocol":
            proxy.protocol,


            "ip":
            data.get("ip"),


            "country":
            data.get("country"),


            "region":
            data.get("region"),


            "latency":
            latency


        }




    except Exception as e:



        proxy.status="失败"


        await db.commit()



        return {


            "status":"error",


            "message":
            str(e)

        }







# =========================
# 当前出口IP
# =========================

@router.get("/outbound-ip")
async def outbound_ip():


    try:


        async with httpx.AsyncClient(

            timeout=10

        ) as client:


            r=await client.get(

                "https://ipinfo.io/json"

            )


        return r.json()



    except Exception as e:


        return {

            "error":
            str(e)

        }






# =========================
# 删除
# =========================

@router.delete("/{proxy_id}")
async def delete_proxy(

    proxy_id:int,

    db:AsyncSession=Depends(get_db)

):


    proxy=await db.get(

        ProxyConfig,

        proxy_id

    )


    if proxy:

        await db.delete(proxy)

        await db.commit()



    return {

        "message":
        "删除成功"

    }
