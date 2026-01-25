from abc import ABC, abstractmethod


class DocProcessor(ABC):

    @abstractmethod
    def parse(self, file: bytes, filename: str):
        """метод для парсинга входящего файла"""
        pass