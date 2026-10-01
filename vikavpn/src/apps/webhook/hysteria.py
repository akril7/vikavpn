from aiohttp import web
from loguru import logger

from src.db.connection import Session
from src.db.repo import UserRepository


async def handle_auth(request: web.Request) -> web.Response:
    data = await request.json()

    try:
        username, password = data.get("auth", "").split(":")
    except ValueError:
        msg = {"ok": False, "msg": "access denied"}
        logger.error(msg)
        return web.json_response(msg, status=200)

    async with Session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_name(username)

    if user and user.password == password and user.is_active:
        return web.json_response({"ok": True, "id": username}, status=200)
    else:
        msg = {"ok": False, "msg": "access denied"}
        logger.info(msg)
        return web.json_response(msg, status=200)
