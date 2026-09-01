import base64
import json



def parse_vmess(vmess_url:str):

    if not vmess_url.startswith("vmess://"):

        raise ValueError(
            "无效VMess链接"
        )


    raw = vmess_url.replace(
        "vmess://",
        ""
    )


    raw += "=" * (
        4 - len(raw) % 4
    )


    data = base64.b64decode(
        raw
    )


    config = json.loads(
        data.decode(
            "utf-8"
        )
    )


    return {


        "remark":
            config.get("ps","VMess节点"),


        "address":
            config.get("add"),


        "port":
            int(config.get("port",0)),


        "uuid":
            config.get("id"),


        "alterId":
            int(
                config.get(
                    "aid",
                    0
                )
            ),


        "security":
            config.get(
                "scy",
                "auto"
            ),


        "network":
            config.get(
                "net",
                "tcp"
            ),


        "type":
            config.get(
                "type",
                ""
            ),


        "host":
            config.get(
                "host",
                ""
            ),


        "path":
            config.get(
                "path",
                ""
            ),


        "tls":
            config.get(
                "tls",
                ""
            ),


        "sni":
            config.get(
                "sni",
                ""
            )

    }
