from abc import abstractmethod, ABC
from typing import List, Dict, Any

import numpy as np

from ingestion_service.src.core.document_vectorizer.data_models.embedding_config import EmbeddingConfig


class BaseVectorizer(ABC):
    """Базовый класс для всех векторизатовров"""
    @abstractmethod
    def embed_single(self, text: str) -> np.ndarray:
        """Создание эмбединга для одного текста"""

    @abstractmethod
    def embed(self,  texts: List[str]) -> np.ndarray:
        """Создание эмбедингов для списка текстов"""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """размерность эмбедингов"""
        pass

    @property
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Получение информации по модели"""
        pass

