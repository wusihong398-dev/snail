import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal

from app.models.proxy import ProxyConfig



async def migrate():


    async with AsyncSessionLocal() as db:


        result = await db.execute(

            select(ProxyConfig)

        )


        items=result.scalars().all()



        for item in items:


            changed=False



            if not item.protocol:


                item.protocol="vmess"

                changed=True



            if not item.url:


                print(

                    "旧节点缺少原始链接:",

                    item.name

                )


            if changed:


                print(
                    "修复:",
                    item.name
                )


        await db.commit()



if __name__=="__main__":

    asyncio.run(
        migrate()
    )
