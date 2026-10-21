from abc import ABC, abstractmethod
import logging

class IUserInteraction(ABC):
    @abstractmethod
    def get_input(self, prompt: str) -> str:
        pass

class ConsoleUserInteraction(IUserInteraction):
    def get_input(self, prompt: str) -> str:
        return input(prompt)

class IExternalService(ABC):
    @abstractmethod
    def send_data(self, data: str) -> bool:
        pass

class MockNotificationService(IExternalService):
    def send_data(self, data: str) -> bool:
        logging.info(f"[Имитация отправки на сервер]: {data}")
        return True