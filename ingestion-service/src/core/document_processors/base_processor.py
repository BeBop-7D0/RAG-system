from abc import ABC, abstractmethod


class DocProcessor(ABC):

    @abstractmethod
    def __init__(self, file: bytes):
        pass


    @abstractmethod
    def parse(self):
        """метод для парсинга входящего файла"""
        pass