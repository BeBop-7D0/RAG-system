import json
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from ingestion_service.src.core.document_vectorizer.data_models.embedding_config import EmbeddingConfig, EmbeddingModelType


load_dotenv()

settings_path  = Path(__file__).parent / 'settings.json'

with open(settings_path, 'rb') as setting_binary:
    settings = json.load(setting_binary)



model_type_str = settings.get("model_type", "").upper()

model_type = EmbeddingModelType[model_type_str]


config = EmbeddingConfig(
    model_type=model_type,
    model_name=settings.get("model_name", 'all-MiniLM-L6-v2'),
    batch_size=settings.get("batch_size", 31),
    normalize_embeddings=settings.get("normalize_embeddings", True),
    device=settings.get("device", "cpu"),
    api_key=getenv('INGESTION_SERVICE_VECTORIZER_API_KEY', 'test'),
    cache_dir=settings.get("cache_dir", "test"),
    max_seq_length=settings.get("max_seq_length", None),
)
