"""WeChat API helpers for login and payment."""

import httpx

from ..config import settings

WECHAT_API_BASE = "https://api.weixin.qq.com"


async def code_to_session(code: str) -> dict:
    """Exchange WeChat login code for session info.

    Returns dict with: openid, session_key, unionid (optional)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WECHAT_API_BASE}/sns/jscode2session",
            params={
                "appid": settings.WECHAT_APPID,
                "secret": settings.WECHAT_SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            },
        )
        data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise ValueError(f"WeChat login failed: {data.get('errmsg', 'unknown error')}")

        return {
            "openid": data["openid"],
            "session_key": data.get("session_key"),
            "unionid": data.get("unionid"),
        }


async def get_access_token() -> str:
    """Get WeChat access token (valid 2 hours, should be cached in production)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WECHAT_API_BASE}/cgi-bin/token",
            params={
                "appid": settings.WECHAT_APPID,
                "secret": settings.WECHAT_SECRET,
                "grant_type": "client_credential",
            },
        )
        data = response.json()
        if "access_token" not in data:
            raise ValueError(f"Failed to get access token: {data}")
        return data["access_token"]
