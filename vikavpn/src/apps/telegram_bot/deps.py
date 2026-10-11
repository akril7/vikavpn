from aiogram.types import CallbackQuery

from src.db.connection import Session
from src.db.models import User
from src.db.repo import UserRepository
from src.db.repo.options import Options

from src.texts.render import render_auth_user_not_found


async def get_user(telegram_id: int, options: Options = ()) -> User | None:
    async with Session() as session:
        repo = UserRepository(session)

        return await repo.get_by_telegram_id(telegram_id, options=options)


async def get_user_or_alert(call: CallbackQuery, options: Options = ()) -> User | None:
    user = await get_user(call.from_user.id, options)
    if user is None:
        await call.answer(render_auth_user_not_found(), show_alert=True)
        return
    return user


def managed_targets(user: User) -> list[tuple[int, str]]:
    return [
        (link.managed.id, link.managed.name)
        for link in user.managed_links
        if link.managed is not None
    ]
