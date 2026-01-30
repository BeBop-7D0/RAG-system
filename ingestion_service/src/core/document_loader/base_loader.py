from typing import Dict, Any, List
from abc import ABC, abstractmethod

from ingestion_service.src.core.document_processors.data_models.document_processor_models import ChunkModel


class BaseLoader(ABC):
    """Базовый класс для загрузчиков документов в БД"""

    @abstractmethod
    def load_chunks(self,
                    chunks: List[ChunkModel],
                    vectors: List[float],
                    collection_name: str,
                    batch_size: int,
                    max_retries: int
                    ):
        """
        Метод для загрузки файла в БД
        :param chunks: словарь с данными чанка
        :param vectors:  векторизованный текст
        :param collection_name:  название коллекции
        :param batch_size: размер батча
        :param max_retries: макс  кол-во попыток
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