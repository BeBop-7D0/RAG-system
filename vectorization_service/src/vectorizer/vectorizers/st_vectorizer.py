import sys
from typing import Dict, Any, List
import logging


import torch
from sentence_transformers import SentenceTransformer

from vectorization_service.src.vectorizer.base_vectorizer import BaseVectorizer
from vectorization_service.src.vectorizer.data_models.embedding_config import EmbeddingConfig


logger = logging.getLogger('ChunkVectorizer')


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
                kwargs['cache_folder'] = self.config.cache_dir

            if self.config.device:
                device = self.config.device
            else:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                if device == 'cuda':
                    logger.info(f"Используется устройство CUDA: {torch.cuda.get_device_name(0)}")
            try:
                self.model = SentenceTransformer(
                    model_name_or_path=self.config.model_name,
                    device=device,
                    local_files_only=True,
                    **kwargs
                )
                logger.info(f"Модель загружена из локального кэша: {self.config.model_name}")
            except (OSError, FileNotFoundError) as error_msg:

                logger.info(f"Модель {self.config.model_name} не найдена в локальном кэше, выполняется "
                            f"загрузка с Hugging Face...")

                self.model = SentenceTransformer(
                    model_name_or_path=self.config.model_name,
                    device=device,
                    **kwargs
                )
                logger.info(f"Модель успешно загружена с Hugging Face: {self.config.model_name}")

            if self.config.max_seq_length:
                self.model.max_seq_length = self.config.max_seq_length

            logger.info(f"Загружена модель: {self.config.model_name}")
            logger.info(f"Размерность эмбединга: {self.model.get_sentence_embedding_dimension()}")
            logger.info(f"Максимальная длинна входной последовательности: {self.model.max_seq_length}")

        except Exception as error_msg:
            logger.error(f"Ошибка загрузки модели {self.config.model_name}: {error_msg}")

    def embed(self,  texts: List[str]) -> List[List[float]]:
        """Векторизация батча текста"""

        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                sentences=texts,
                batch_size=self.config.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                convert_to_tensor=False,
                normalize_embeddings=self.config.normalize_embeddings
            )

            return embeddings.tolist()

        except Exception as error_msg:
            logger.error(f"Ошибка во время векторизации: {error_msg}")
            raise

    def embed_single(self, text: str) -> List[float]:
        """Метод для векторизации одного текста"""
        return self.embed([text])[0]

    @property
    def dimension(self) -> int:
        """Возвращает размерность эмбедингов"""
        return self.model.get_sentence_embedding_dimension()

    @property
    def model_info(self) -> Dict[str, Any]:
        """Возвращает информацию по модели"""
        return {
            "model_type": self.config.model_type,
            "model_name": self.config.model_name,
            "dimension": self.dimension,
            "max_seq_length": self.model.max_seq_length,
            "normalize_embeddings": self.config.normalize_embeddings
        }


def main():

    from vectorization_service.src.vectorizer.load_config import config

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout
    )

    vectorizer = SentenceTransformerEmbedder(config)

    texts = [
        'some_text',
        'another text',
        'ou, this is a new text!'
    ]
    single_vector = vectorizer.embed_single(texts[0])

    vectors = vectorizer.embed(texts)


if __name__ == "__main__":
    main()