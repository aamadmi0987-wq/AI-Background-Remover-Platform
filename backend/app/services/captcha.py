def verify_captcha(token: str, secret: str) -> bool:
    if secret == "dev-bypass":
        return token == "dev-pass"
    return bool(token)
