from src.db.models import UserManagement
from src.db.repo.base import BaseRepository


class UserManagementRepository(BaseRepository[UserManagement]):
    model = UserManagement
