import hmac
from json import JSONDecodeError

from aiohttp import web, ContentTypeError

from src.db.connection import Session
from src.db.repo import UserRepository


async def handle_auth(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except (JSONDecodeError, ContentTypeError):
        return web.json_response({"ok": False, "msg": "access denied"}, status=200)

    auth = data.get("auth", "")
    if ":" not in auth:
        return web.json_response({"ok": False, "msg": "access denied"}, status=200)

    raw_username, raw_password = auth.split(":", 1)
    username = raw_username.strip()
    password = raw_password.strip()

    async with Session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_name(username)

    if user and hmac.compare_digest(user.password, password) and user.is_active:
        return web.json_response({"ok": True, "id": username}, status=200)

    return web.json_response({"ok": False, "msg": "access denied"}, status=200)
