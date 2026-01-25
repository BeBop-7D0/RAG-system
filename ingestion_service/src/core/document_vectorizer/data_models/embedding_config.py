from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EmbeddingModelType(Enum):
    """Типы моделей для эмбедингов"""
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class EmbeddingConfig(BaseModel):
    model_type: EmbeddingModelType
    model_name: str
    batch_size:  int = 32
    normalize_embeddings: bool = True
    device: Optional[str] = None
    api_key: Optional[str] = None
    cache_dir: Optional[str] = None
    max_seq_length: Optional[int] = 512
