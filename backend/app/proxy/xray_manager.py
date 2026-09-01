import json
import os
import signal
import subprocess
import time


# =========================
# Xray配置
# =========================

XRAY_BIN = "/usr/local/bin/xray"

XRAY_CONFIG = "/tmp/snail-xray.json"

XRAY_PID = "/tmp/snail-xray.pid"

XRAY_LOG = "/tmp/snail-xray.log"





# =========================
# 生成Xray配置
# =========================

def build_stream(node):

    stream = {

        "network": node.get(
            "network",
            "tcp"
        )

    }


    # WebSocket

    if node.get("network") == "ws":

        stream["wsSettings"] = {

            "path": node.get(
                "path",
                "/"
            ),

            "headers": {

                "Host": node.get(
                    "host",
                    ""
                )

            }

        }



    # TLS

    if node.get("tls") in [
        "tls",
        "1"
    ]:

        stream["security"] = "tls"

        stream["tlsSettings"] = {

            "serverName":
                node.get(
                    "sni",
                    node.get(
                        "host",
                        ""
                    )
                )

        }


    return stream






def create_xray_config(node):


    protocol = node.get(
        "protocol"
    )


    outbound = None



    # =====================
    # VMess
    # =====================

    if protocol == "vmess":


        outbound = {

            "protocol": "vmess",

            "settings": {

                "vnext": [

                    {

                        "address":
                            node["server"],


                        "port":
                            int(node["port"]),


                        "users": [

                            {

                                "id":
                                    node["uuid"],


                                "alterId":
                                    int(
                                        node.get(
                                            "alterId",
                                            0
                                        )
                                    ),


                                "security":
                                    node.get(
                                        "security",
                                        "auto"
                                    )

                            }

                        ]

                    }

                ]

            },


            "streamSettings":
                build_stream(node)

        }



    # =====================
    # VLESS
    # =====================

    elif protocol == "vless":


        outbound = {

            "protocol": "vless",

            "settings": {

                "vnext": [

                    {

                        "address":
                            node["server"],


                        "port":
                            int(node["port"]),


                        "users": [

                            {

                                "id":
                                    node["uuid"],


                                "encryption":
                                    "none"

                            }

                        ]

                    }

                ]

            },


            "streamSettings":
                build_stream(node)

        }



    # =====================
    # Trojan
    # =====================

    elif protocol == "trojan":


        outbound = {

            "protocol": "trojan",

            "settings": {

                "servers": [

                    {

                        "address":
                            node["server"],


                        "port":
                            int(node["port"]),


                        "password":
                            node["password"]

                    }

                ]

            },


            "streamSettings":
                build_stream(node)

        }



    # =====================
    # Hysteria2
    # =====================

    elif protocol == "hysteria2":


        outbound = {

            "protocol": "hysteria",

            "settings": {

                "servers": [

                    {

                        "address":
                            node["server"],


                        "port":
                            int(node["port"]),


                        "password":
                            node.get(
                                "password",
                                ""
                            )

                    }

                ]

            }

        }



    else:

        raise ValueError(
            f"不支持协议: {protocol}"
        )





    config = {


        "log": {

            "loglevel":
                "warning"

        },


        # SOCKS5入口

        "inbounds": [

            {

                "listen":
                    "127.0.0.1",


                "port":
                    10808,


                "protocol":
                    "socks",


                "settings": {

                    "udp":
                        True

                }

            }

        ],



        "outbounds": [

            outbound

        ]

    }



    with open(
        XRAY_CONFIG,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            config,

            f,

            indent=2,

            ensure_ascii=False

        )



    return XRAY_CONFIG







# =========================
# 启动Xray
# =========================

def start_xray():


    # 已运行

    if os.path.exists(
        XRAY_PID
    ):

        return True




    log = open(

        XRAY_LOG,

        "w",

        encoding="utf-8"

    )



    process = subprocess.Popen(

        [

            XRAY_BIN,

            "run",

            "-config",

            XRAY_CONFIG

        ],


        stdout=log,

        stderr=log

    )



    time.sleep(2)



    if process.poll() is not None:


        return False




    with open(

        XRAY_PID,

        "w"

    ) as f:


        f.write(

            str(
                process.pid
            )

        )



    return True







# =========================
# 停止Xray
# =========================

def stop_xray():


    if not os.path.exists(
        XRAY_PID
    ):

        return True



    try:


        with open(
            XRAY_PID
        ) as f:


            pid = int(
                f.read()
            )



        os.kill(

            pid,

            signal.SIGTERM

        )



    except Exception:


        pass



    try:


        os.remove(
            XRAY_PID
        )


    except:


        pass



    return True







# =========================
# 状态
# =========================

def status_xray():


    if os.path.exists(
        XRAY_PID
    ):


        return {

            "status":
                "running"

        }



    return {

        "status":
            "stopped"

    }







# =========================
# 日志
# =========================

def get_xray_log():


    if not os.path.exists(
        XRAY_LOG
    ):

        return ""



    with open(

        XRAY_LOG,

        "r",

        encoding="utf-8",

        errors="ignore"

    ) as f:


        return f.read()[-5000:]
