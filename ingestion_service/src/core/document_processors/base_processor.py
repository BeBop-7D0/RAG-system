from typing import List
from abc import ABC, abstractmethod
from ingestion_service.src.core.document_processors.data_models.document_processor_models import ChunkModel


class DocProcessor(ABC):

    @abstractmethod
    def parse(self, file: bytes, filename: str) -> List[ChunkModel]:
        """метод для парсинга входящего файла"""
        pass