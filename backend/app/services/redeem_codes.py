import hashlib
import secrets


def normalize_code(code: str) -> str:
    return "".join(ch for ch in code.strip().upper() if ch.isalnum())


def hash_code(code: str) -> str:
    return hashlib.sha256(normalize_code(code).encode("utf-8")).hexdigest()


def generate_code(code_type: str) -> tuple[str, str, str]:
    prefix_map = {
        "group_license": "WNA-GRP",
        "diamonds": "WNA-DIA",
        "membership": "WNA-VIP",
        "partner_slot": "WNA-LOVE",
        "baby_slot": "WNA-BABY",
    }
    prefix = prefix_map.get(code_type, "WNA-CODE")
    body = secrets.token_hex(8).upper()
    code = f"{prefix}-{body[0:4]}-{body[4:8]}-{body[8:12]}-{body[12:16]}"
    return code, prefix, hash_code(code)
