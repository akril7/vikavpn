from src.domain.models import UserManagement
from src.infrastructure.persistence.repo.base import BaseRepository


class UserManagementRepository(BaseRepository[UserManagement]):
    model = UserManagement
