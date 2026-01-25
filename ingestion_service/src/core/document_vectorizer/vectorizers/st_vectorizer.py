from typing import Optional, Dict, Any

import torch
import numpy as np
from sentence_transformers import SentenceTransformer

from ingestion_service.src.core.document_vectorizer.base_vectorizer import BaseVectorizer
from ingestion_service.src.core.document_vectorizer.data_models.embedding_config import EmbeddingConfig


class SentenceTransformerEmbedder(BaseVectorizer):
    """Векторизатор на основе Sentence Transformers"""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self._initialize_model()


    def _initialize_model(self):
        """Инициализация модели"""

        try:
            kwargs = {}

            if self.config.cache_dir:
                kwargs['cashe_folder'] = self.config.cache_dir

            if self.config.device:
                device = self.config.device
            else:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                if device == 'cuda':
                    print(f"Используется устройство CUDA: {torch.cuda.get_device_name(0)}")

            self.model = SentenceTransformer(
                model_name_or_path=self.config.model_name,
                device=device,
                **kwargs
            )

            if self.config.max_seq_length:
                self.model.max_seq_length = self.config.max_seq_length

            print(f"Загружена модель: {self.config.model_name}")
            print(f"Размерность эмбединга: {self.model.get_sentence_embedding_dimension()}")
            print(f"Максимальная длинна входной последовательности: {self.model.max_seq_length}")

        except Exception as error_msg:
            print(f"Ошибка загрузки модели {self.config.model_name}: {error_msg}")