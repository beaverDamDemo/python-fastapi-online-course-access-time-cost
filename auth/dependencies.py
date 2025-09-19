from fastapi import Request, HTTPException
from auth.session import get_logged_in_user


def require_login(request: Request):
    user = get_logged_in_user(request)
    if not user:
        raise HTTPException(
            status_code=302, detail="Redirect", headers={"Location": "/login"}
        )
    return user
