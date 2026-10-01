import tomllib
from datetime import datetime, UTC

from loguru import logger
from uuid import UUID

from src.db.connection import Session
from src.db.models import User
from src.db.repo import UserRepository, UserManagementRepository


async def import_users_from_file(path: str) -> int:
    """
    Импорт пользователей из файла.
    Возвращает количество импортированных пользователей
    """
    with open(path, "rb") as f:
        data = tomllib.load(f)

    users_data = data.get("users", [])
    users: list[User] = []

    async with Session() as session:
        user_repo = UserRepository(session)
        manage_repo = UserManagementRepository(session)

        for raw in users_data:
            logger.info(f"Load {raw["name"]}")
            user = await user_repo.create(
                name=raw["name"],
                password=raw["password"],
                sub_expires_at=datetime.strptime(raw["sub_expires"], "%Y-%m-%d").replace(tzinfo=UTC),
                uuid=UUID(raw["uuid"]),
                vpn_user=raw.get("use_vpn", True),
                proxy_user=raw.get("use_proxy", True),
                ios_user=raw.get("use_ios", False),
            )
            users.append(user)

        manager = await user_repo.get_by_name(raw["name"])
        for raw in users_data:
            managed_users = raw.get("managed_users")
            if not managed_users:
                continue

            for username in managed_users:
                managed = await user_repo.get_by_name(username)
                if not (manager and managed):
                    raise RuntimeError(f"manager or managed name is null")

                await manage_repo.create(
                    manager=manager,
                    managed=managed,
                )

        logger.info("Commit")
        await session.commit()

    return len(users)
