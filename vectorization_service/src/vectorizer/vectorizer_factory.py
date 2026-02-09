from logging import Logger
from typing import Dict, Type, List

from vectorization_service.src.data_models.embedding_config import EmbeddingConfig
from vectorization_service.src.vectorizer.base_vectorizer import BaseVectorizer
from vectorization_service.src.vectorizer.vectorizers.st_vectorizer import SentenceTransformerEmbedder


logger = Logger("VectorizerFactory")

class VectorizerFactory:

    _vectorizer_classes: Dict[str, Type[BaseVectorizer]] = {
        'sentence_transformers': SentenceTransformerEmbedder
    }

    @classmethod
    def create(cls, config: EmbeddingConfig) -> BaseVectorizer:

        model_type = config.model_type.value

        if model_type not in cls._vectorizer_classes:
            raise ValueError(f"Неизвестный тип: {model_type}")

        logger.debug(f"Инициализация векторизатора {config.model_type.value}")
        vectorizer_class = cls._vectorizer_classes.get(model_type)

        return vectorizer_class(config)


    @classmethod
    def register(cls, model_type: str, vectorizer_class: Type[BaseVectorizer]):
        """Регистрация нового векторизатора"""
        cls._vectorizer_classes[model_type] = vectorizer_class
        logger.debug(f"Модель {model_type} зарегистрирована")

    @classmethod
    def get_available_types(cls) -> List:
        return list(cls._vectorizer_classes.keys())