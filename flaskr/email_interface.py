from abc import ABC, abstractmethod


# pylint: disable=R0903
class EmailInterface(ABC):
    @abstractmethod
    def send_email(self, to_email: str, reset_link: str):
        pass
