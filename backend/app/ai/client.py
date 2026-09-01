import httpx


from app.proxy.xray_manager import start_xray




DEFAULT_SYSTEM_PROMPT = """
你是蜗牛小精灵。

交流规则：

1. 称呼用户为“宝子”
2. 语气亲切、温暖、有耐心
3. 回复自然，不要机械化
4. 不透露底层模型名称
5. 不提及 DeepSeek、ChatGPT、OpenAI 等平台
6. 不说自己是语言模型
7. 像一个贴心的小助手一样帮助用户

示例：

宝子你好呀～😊
有什么问题都可以告诉我哦～
我来帮你看看。
"""





async def ai_request(

    config,

    messages

):


    proxy=None


    if config.proxy_id:


        start_xray()


        proxy="socks5://127.0.0.1:10808"





    final_messages=[


        {

            "role":"system",

            "content":

            config.system_prompt
            or
            DEFAULT_SYSTEM_PROMPT

        }

    ]



    final_messages.extend(
        messages
    )





    async with httpx.AsyncClient(

        proxy=proxy,

        timeout=60

    ) as client:


        response=await client.post(

            config.api_url
            +
            "/chat/completions",


            headers={

                "Authorization":

                f"Bearer {config.api_key}",


                "Content-Type":

                "application/json"

            },


            json={

                "model":

                config.model,


                "messages":

                final_messages

            }

        )


        return response.json()
