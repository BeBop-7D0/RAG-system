from typing import Dict, Any, List
from abc import ABC, abstractmethod

from ingestion_service.src.core.document_processors.data_models.document_processor_models import ChunkModel


class BaseLoader(ABC):
    """Базовый класс для загрузчиков документов в БД"""

    @abstractmethod
    def load_chunks(self, chunks: List[ChunkModel]):
        """
        Метод для загрузки файла в БД
        :param chunks: чанки для загрузки
        :return:
        """
        pass


    @property
    @abstractmethod
    def loader_info(self) -> Dict[str, Any]:
        """
        Получение информации по модели загрузчика
        :return:
        """
        pass