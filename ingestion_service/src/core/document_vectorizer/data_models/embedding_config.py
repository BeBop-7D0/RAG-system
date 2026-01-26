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
    batch_size:  int
    normalize_embeddings: bool
    device: Optional[str]
    api_key: Optional[str]
    cache_dir: Optional[str]
    max_seq_length: Optional[int]
