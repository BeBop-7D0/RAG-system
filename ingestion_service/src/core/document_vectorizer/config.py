import os
from dotenv import load_dotenv
from ingestion_service.src.core.document_vectorizer.data_models.embedding_config import EmbeddingConfig, EmbeddingModelType

load_dotenv()

model_type_str = os.getenv('INGESTION_SERVICE_EMBEDDING_MODEL_TYPE').upper()
model_type = EmbeddingModelType[model_type_str]

config = EmbeddingConfig(
    model_type=model_type,
    model_name=os.getenv('INGESTION_SERVICE_EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2'),
    batch_size=os.getenv('INGESTION_SERVICE_EMBEDDING_MODEL_BATCH_SIZE', 32),
    normalize_embeddings=os.getenv('INGESTION_SERVICE_EMBEDDING_MODEL_NORMALIZE_EMBEDDINGS', 'True').lower() == 'true',
    device=os.getenv('INGESTION_SERVICE_EMBEDDING_MODEL_DEVICE', 'cpu'),
    api_key=os.getenv('INGESTION_SERVICE_EMBEDDING_API_KEY', 'test'),
    cache_dir=os.getenv('INGESTION_SERVICE_EMBEDDING_CACHE_DIR', 'test'),
    max_seq_length=os.getenv('INGESTION_SERVICE_EMBEDDING_MAX_SEQ_LENGTH', None)
)
