import re


def validate_email(email: str) -> str:
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if not re.fullmatch(regex, email):
        return "Email not valid!"
    return ""


def validate_password(password: str) -> str:
    if len(password) < 8:
        return "Password too short!"
    elif len(password) > 60:
        return "Password too long!"
    return ""
