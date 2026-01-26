import logging
from pathlib import Path

from ingestion_service.src.logger import setup_logging
from ingestion_service.src.core.document_processors.doc_processor_factory import DocProcessorFactory
from ingestion_service.src.core.document_vectorizer.vectorizer_factory import VectorizerFactory
from ingestion_service.src.core.document_vectorizer.config import config as vectorizer_config


setup_logging()
logger = logging.getLogger(__name__)
logger.info("Сервис запущен")



file_path = Path(__file__).parent.parent.parent / 'test_files/simple_file.docx'

with open(file_path, 'rb') as f:
    binary_file = f.read()

doc_processor_factory = DocProcessorFactory()
vectorizer = VectorizerFactory.create(vectorizer_config)
processor = doc_processor_factory['.docx']
chunks = processor.parse(binary_file, 'test_file')
logger.debug(len(chunks))

logger.debug(vectorizer.model_info)




