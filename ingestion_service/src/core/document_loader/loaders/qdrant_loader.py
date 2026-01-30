from uuid import uuid4
import sys
import logging
from typing import Dict, Any, Optional, List

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Batch, PointStruct

from ingestion_service.src.core.document_loader.data_models.qdrant_load_statistics import LoadStatisticModel
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

    @staticmethod
    def _chunk_to_point( chunk: ChunkModel, vector: List[float]) -> PointStruct:
        """
        Преобразует чанк в qdrant - точку
        :param chunk: Словарь с данными чанка
        :param vector: Векторное представление текста
        :return: PointStruct для Qdrant
        """

        point_id = chunk.metadata.chunk_id
        if not point_id:
            point_id = str(uuid4())

        payload = {
            "text": chunk.text,
            "text_sensitive_removed": chunk.text_sensitive_removed,
            "doc_id": chunk.metadata.doc_id,
            "chunk_id": chunk.metadata.chunk_id,
            "source": chunk.metadata.source,
            "chunk_index": chunk.metadata.chunk_index,
            "char_count": chunk.metadata.char_count,
            "word_count": chunk.metadata.word_count
        }

        return PointStruct(
            id=point_id,
            vecor=vector,
            payload=payload
        )

    def load_chunks(self,
                    chunks: List[ChunkModel],
                    vectors: List[float],
                    collection_name: str,
                    batch_size: int,
                    max_retries: int
                    ) -> LoadStatisticModel:
        """
        Основной метод загрузки чанков в qdrnat
        :param chunks: Список чанков
        :param vectors: Список векторов (должен соответствовать chunks по порядку)
        :param collection_name: Название коллекции
        :param batch_size: Размер батча для загрузки (оптимально 64-256)[citation:2]
        :param max_retries: Максимальное количество повторных попыток
        :return: Статистика загрузки
        """

        stats = LoadStatisticModel(
            total_chunks=len(chunks),
            successful=0,
            failed=0,
            errors=[]
        )

        if len(chunks) != len(vectors):
            error_msg = f"Количество чанков ({len(chunks)}) не соответсвует количеству векторов ({len(vectors)})"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            return stats

        points = []
        for chunk, vector in zip(chunks, vectors):
            try:
                point = self._chunk_to_point(chunk, vector)
                points.append(point)
            except Exception as e:
                stats.failed += 1
                stats.errors.append(f"Ошибка преобразования чанка {chunk.metadata.chunk_id}: {e}")

        logger.debug(f"Начало загрузки {len(points)} в коллекцию {collection_name}")

        for i in range(0, len(points), batch_size):
            batch = points[i: i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(points) + batch_size - 1) // batch_size

            for attempt in range(max_retries):
                try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=batch,
                        wait=True   # ждем подтверждения
                    )
                    stats.successful += len(batch)
                    logger.debug(f"Батч {batch_num} / {total_batches}  загружен ({len(batch)} точек)")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Попытка {attempt + 1}/{max_retries} "
                                       f"не удалась для батча {batch_num}: {str(e)}")
                    else:
                        stats["failed"] += len(batch)
                        stats["errors"].append(f"Ошибка загрузки батча {batch_num}: {str(e)}")
                        logger.error(f"Не удалось загрузить батч {batch_num} "
                                     f"после {max_retries} попыток: {str(e)}")
        self.__enable_indexing(collection_name)
        return stats

    def __enable_indexing(self, collection_name: str, m: int = 16) -> bool:
        """
        Включение индексации после завершения загрузки.

        :param collection_name: Название коллекции
        :param m: Параметр HNSW (количество связей, обычно 16 или 32)[citation:3][citation:8]
        :return: Успешность операции
        """
        try:
            self.client.update_collection(
                collection_name=collection_name,
                hnsw_config=models.HnswConfigDiff(m=m)
            )
            logger.info(f"Индексация HNSW включена для коллекции {collection_name} с m={m}")
            return True
        except Exception as e:
            logger.error(f"Ошибка включения индексации для {collection_name}: {str(e)}")
            return False

    @property
    def loader_info(self) -> Dict[str, Any]:
        return {
            "name": "QdrantLoader",
            "description": "Загрузчик чанков в векторную БД Qdrant",
            "supports_batch": True,
            "supports_metadata": True,
            "recommended_batch_size": 100
        }

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        if hasattr(self, 'client'):
            self.client.close()



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
    # loader.delete_collection('test_collection')


if __name__ == "__main__":

    main()