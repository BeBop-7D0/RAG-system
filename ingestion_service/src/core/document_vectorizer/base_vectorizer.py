from abc import abstractmethod, ABC
from typing import List, Dict, Any

import numpy as np


class BaseVectorizer(ABC):
    """Базовый класс для всех векторизатовров"""
    @abstractmethod
    def embed_single(self, text: str) -> List[float]:
        """Создание эмбединга для одного текста"""

    @abstractmethod
    def embed(self,  texts: List[str]) -> List[List[float]]:
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

