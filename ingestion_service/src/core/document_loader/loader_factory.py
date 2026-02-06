from typing import Dict, Type

from logging import Logger

from ingestion_service.src.core.document_loader.data_models.loader_config import LoaderConfig
from ingestion_service.src.core.document_loader.base_loader import BaseLoader
from ingestion_service.src.core.document_loader.loaders.qdrant_loader import QdrantLoader


logger = Logger("LoaderFactory")

class LoaderFactory:
    """Фабрика для создания загрузчиков"""

    loader_classes: Dict[str, Type[BaseLoader]] = {
        'QDRANT': QdrantLoader
    }


    @classmethod
    def create(cls, config: LoaderConfig) -> BaseLoader:

        if config.type not in cls.loader_classes:
            raise ValueError(f"Неизвестный тип загрузчика {config.type}. "
                             f"Доступны следующие: [{list(cls.loader_classes.keys())}]")

        logger.debug(f"Инициализация загрузчика {config.type}")
        loader = cls.loader_classes[config.type]
        return loader(config)

