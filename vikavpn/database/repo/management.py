from database.models import UserManagement
from database.repo.base import BaseRepository


class UserManagementRepository(BaseRepository[UserManagement]):
    model = UserManagement
