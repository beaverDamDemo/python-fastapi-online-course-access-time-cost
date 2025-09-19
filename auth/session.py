from fastapi import Request, Response

# Hardcoded credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"


def login_user(response: Response, username: str):
    response.set_cookie(key="session_user", value=username, httponly=True)


def logout_user(response: Response):
    response.delete_cookie("session_user")


def get_logged_in_user(request: Request):
    return request.cookies.get("session_user")
