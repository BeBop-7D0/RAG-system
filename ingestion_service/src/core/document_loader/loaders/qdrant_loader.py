import sys
import logging
from typing import Dict, Any, Optional, List

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Batch, PointStruct

from ingestion_service.src.core.document_loader.base_loader import BaseLoader
from ingestion_service.src.core.document_processors.data_models.document_processor_models import ChunkModel

logger = logging.Logger("QdrantLoader")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class QdrantLoader(BaseLoader):
    """Класс для загрузки данных в Qdrant"""

    def __init__(self,
                 host: str = "localhost",
                 port: int = 6333,
                 https: bool = False,
                 api_key: Optional[str] = None,
                 prefix: Optional[str] = None,
                 timeout: int = 10
                 ):
        """
        Инициализация клиента Qdrant.

        :param host: Хост Qdrant
        :param port: Порт Qdrant
        :param https: Использовать HTTPS
        :param api_key: API ключ для Qdrant Cloud
        :param prefix: Префикс для URL (для Qdrant Cloud)
        :param timeout: Таймаут подключения
        """
        self.client = QdrantClient(
            url=host if host.startswith('http') else f"{'https' if https else 'http'}://{host}:{port}",
            api_key=api_key,
            prefix=prefix,
            timeout=timeout
        )

    def create_collection(self,
                          collection_name: str,
                          vector_size: int,
                          distance: models.Distance = models.Distance.COSINE,
                          on_disk: bool = False,
                          disable_indexing: bool = True) -> bool:
        """
        Создание коллекции с оптимизацией для  bulk загрузки
        :param collection_name: название коллекции
        :param vector_size: размерность вектора
        :param distance: метрика расстояния (COSINE, EUCLID, DOT)
        :param on_disk: хранить векторы на диске для экономиии RAM
        :param disable_indexing:Отключить индексацию во время загрузки для ускорения
        :return: статус создания
        """

        try:
            # конфигурация hnsw индекса
            hnsw_config = models.HnswConfigDiff()
            if disable_indexing:
                # отключение индексации при загрузке
                hnsw_config.m = 0
                logger.debug(f"Индекс hnsw отключен на время загрузки в коллекцию {collection_name}.")

            # отключение индекса в оптимизаторе
            optimizers_config = models.OptimizersConfigDiff()
            if disable_indexing:
                optimizers_config.indexing_threshold = 0

            vectors_config = models.VectorParams(
                size=vector_size,
                distance=distance,
                on_disk=on_disk
            )

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vectors_config,
                hnsw_config=hnsw_config,
                optimizers_config=optimizers_config
            )

            logger.debug(f"Коллекция {collection_name} создана с параметрами:"
                         f"vector_size={vector_size}, distance={distance}, "
                         f"on_disk={on_disk}, disable_indexing={disable_indexing}")

            return True
        except Exception as error_msg:
            logger.error(f"Не удалось создать коллекцию {collection_name}. Ошибка: {error_msg}")
            return False

    def delete_collection(self,
                          collection_name: str) -> bool:
        """
        Удаление указанной коллекции в qdrant
        :param collection_name:
        :return: статус удаления
        """
        try:
            self.client.delete_collection(
                collection_name=collection_name
            )
            logger.debug(f"Коллекция {collection_name} успешно удалена.")
            return True
        except Exception as error_msg:
            logger.error(f"Ошибка во время удаления коллекции {collection_name}: {error_msg}.")
            return False


    # def _chunk_to_point(self, chunk: ChunkModel, vector: L):

    def load_chunks(self, chunks: List[ChunkModel]) -> bool:
        pass

    def loader_info(self) -> Dict[str, Any]:
        pass


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout
    )

    loader = QdrantLoader()
    loader.create_collection(
        collection_name='test_collection',
        vector_size=512
    )
    loader.delete_collection('test_collection')


if __name__ == "__main__":

    main()