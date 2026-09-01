import base64
import json
from urllib.parse import urlparse, parse_qs



def parse_link(url:str):


    if url.startswith("vmess://"):

        return parse_vmess(url)



    if url.startswith("vless://"):

        return parse_vless(url)



    if url.startswith("trojan://"):

        return parse_trojan(url)



    if url.startswith("hysteria2://"):

        return parse_hysteria2(url)



    raise ValueError(
        "暂不支持该协议"
    )





def parse_vmess(url):

    raw=url.replace(
        "vmess://",
        ""
    )


    raw += "=" * (
        4-len(raw)%4
    )


    data=json.loads(

        base64.b64decode(raw)

        .decode("utf-8")

    )


    return {

        "protocol":"vmess",

        "server":
        data.get("add"),

        "port":
        int(data.get("port")),

        "uuid":
        data.get("id"),

        "network":
        data.get("net","tcp"),

        "tls":
        data.get("tls",""),

        "host":
        data.get("host",""),

        "path":
        data.get("path","")

    }







def parse_vless(url):


    u=urlparse(url)


    return {


        "protocol":"vless",

        "server":
        u.hostname,


        "port":
        u.port,


        "uuid":
        u.username,


        "tls":
        parse_qs(
            u.query
        ).get(
            "security",
            [""]
        )[0]


    }







def parse_trojan(url):


    u=urlparse(url)


    return {


        "protocol":"trojan",

        "server":
        u.hostname,


        "port":
        u.port,


        "password":
        u.username

    }







def parse_hysteria2(url):


    u=urlparse(url)


    return {


        "protocol":"hysteria2",

        "server":
        u.hostname,


        "port":
        u.port,


        "password":
        u.username

    }
