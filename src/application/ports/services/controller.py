from abc import ABC, abstractmethod


class Controller(ABC):
    @property
    @abstractmethod
    def status(self) -> bool:
        """ Статус сервиса (запущен/нет) """
        pass

    @abstractmethod
    def start(self):
        """ Запустить сервис """
        pass

    @abstractmethod
    def stop(self):
        """ Остановить сервис """
        pass

    @abstractmethod
    def restart(self):
        """ Перезапустить сервис """
        pass

    @abstractmethod
    def reload(self):
        """ Перезагрузить конфиги сервиса """
        pass
