from logging import Logger
from typing import Dict, Any, Optional

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Batch, PointStruct

from ingestion_service.src.core.document_loader.base_loader import BaseLoader


logger = Logger("QdrantLoader")


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
