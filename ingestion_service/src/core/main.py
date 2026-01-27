import logging
from pathlib import Path

from ingestion_service.src.logger import setup_logging
from ingestion_service.src.core.document_processors.doc_processor_factory import DocProcessorFactory
from ingestion_service.src.core.document_vectorizer.vectorizer_factory import VectorizerFactory
from ingestion_service.src.core.document_vectorizer.config import config as vectorizer_config
from ingestion_service.src.core.document_processors.config import config as processor_config


setup_logging()
logger = logging.getLogger(__name__)


def main():

    vectorizer = VectorizerFactory.create(vectorizer_config)
    processor = DocProcessorFactory(processor_config)

    file_path = Path(__file__).parent.parent.parent / 'test_files/simple_file.docx'
    file_name = file_path.name
    file_type = file_path.suffix

    with open(file_path, 'rb') as f:
        file_data = f.read()

    chunks = processor.parse(file_type, file_name, file_data)

    vectors = []


if __name__ == "__main__":
    main()