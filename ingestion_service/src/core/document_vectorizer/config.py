import os
from dotenv import load_dotenv
from data_models.embedding_config import EmbeddingConfig, EmbeddingModelType

load_dotenv()

model_type_str = os.getenv('EMBEDDING_MODEL_TYPE').upper()
model_type = EmbeddingModelType[model_type_str]

config = EmbeddingConfig(
    model_type=model_type,
    model_name=os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2'),
    batch_size=os.getenv('EMBEDDING_MODEL_BATCH_SIZE', 32),
    normalize_embeddings=os.getenv('EMBEDDING_MODEL_NORMALIZE_EMBEDDINGS', 'True').lower() == 'true',
    device=os.getenv('EMBEDDING_MODEL_DEVICE', 'cpu'),
    api_key=os.getenv('EMBEDDING_API_KEY', 'test'),
    cache_dir=os.getenv('EMBEDDING_CACHE_DIR', 'test'),
    max_seq_length=os.getenv('EMBEDDING_MAX_SEQ_LENGTH', None)
)
