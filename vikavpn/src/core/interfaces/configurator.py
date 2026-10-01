from abc import ABC, abstractmethod

from src.db.models import Users


class Configurator(ABC):
    @abstractmethod
    def apply(self, users: Users):
        """ Применить список пользователей для ендпоинта """
        pass
