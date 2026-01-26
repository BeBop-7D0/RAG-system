import os
from dotenv import load_dotenv
from ingestion_service.src.core.document_processors.data_models.processor_config import ProcessorConfig

load_dotenv()


config = ProcessorConfig(
    min_paragraphs_len=os.getenv('INGESTION_SERVICE_DOC_PROCESSOR_MIN_PARAGRAPHS_LEN', 20),
    min_len_for_join=os.getenv('INGESTION_SERVICE_DOC_PROCESSOR_MIN_LEN_FOR_JOIN', 35),
    min_len_for_split=os.getenv('INGESTION_SERVICE_DOC_PROCESSOR_MIN_LEN_FOR_SPLIT', 190),
    max_len_for_chunk=os.getenv('INGESTION_SERVICE_DOC_PROCESSOR_MAX_LEN_FOR_CHUNK', 100)
)
