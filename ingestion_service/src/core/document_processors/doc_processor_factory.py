from logging import Logger
from typing import Type, Dict

from ingestion_service.src.core.document_processors.processors.docx_processor import DOCXProcessor
from ingestion_service.src.core.document_processors.base_processor import DocProcessor
from ingestion_service.src.core.document_processors.data_models.processor_config import ProcessorConfig


logger = Logger("DocProcessorFactory")


class DocProcessorFactory:
    """Фабрика для обработчиков документов"""

    _processor_classes:Dict[str, Type[DocProcessor]]  = {
            '.docx': DOCXProcessor,
        }

    def __init__(self, config: ProcessorConfig):
        self.config = config
        self._processors: Dict[str, DocProcessor]  = {}



    def parse(self, file_type: str, file_name: str, file_data: bytes):
        """Парсинг документа"""

        if not file_type.startswith('.'):
            file_type = f'.{file_type}'
        file_type = file_type.lower()

        if file_type not in self._processor_classes:
            available = list(self._processor_classes.keys())
            raise ValueError(f"Неизвестный тип документа: {file_type}. Поддерживаемые типы: {available}")

        if file_type not in self._processors:
            logger.debug(f"Создаем обработчик для {file_type} документов")
            processor = self._processor_classes[file_type]
            processor_instance = processor(self.config)
            self._processors[file_type] = processor_instance


        processor = self._processors.get(file_type)
        return processor.parse(file_data, file_name)
