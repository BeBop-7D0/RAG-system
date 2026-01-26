import io
import sys
import re
from pathlib import Path
from typing import List
from hashlib import md5
import logging

from docx import Document
from docx.text.paragraph import Paragraph

from ingestion_service.src.core.document_processors.base_processor import DocProcessor
from ingestion_service.src.core.document_processors.data_models.document_processor_models import (MetadataModel,
                                                                                                  ChunkModel)


logger = logging.getLogger("DocParser")


class DOCXProcessor(DocProcessor):
    """Класс, реализующий методы для обработки
    .docx файлов
    """

    @staticmethod
    def __normalize(raw_text: str) -> str:
        """Нормализация текста (удаление лишних пробелов, непечатаемых символов)"""
        # удаление лишних пробелов и переносов
        text = re.sub(r"\s+", " ", raw_text).strip()

        # нормализация пунктуации
        text = re.sub(r"([!?.,:;]){2,}", r"\1", text)

        # стандартизация кавычек
        text = re.sub(r'[«»"”“]', r'"', text)

        return text

    @staticmethod
    def __replace_sensitive_data(raw_text: str) -> str:
        # замена url-ссылок на <URL>
        url_pattern = r'https?://[^\s]+|www\.[^\s]+\b'
        text = re.sub(url_pattern, r"<URL>", raw_text)

        # замена номеров телефона на <PHONE>
        phone_pattern = r'(?:\+7|8)?[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b'
        text = re.sub(phone_pattern, r"<PHONE>", text)

        # замна адресов почты на <EMAIL>
        email_pattern = r'[\w.+%-]+@[\w-]+\.\w{2,}'
        text = re.sub(email_pattern, r"<EMAIL>", text)

        return text

    @staticmethod
    def __join_short_split_long_paragraphs(
            paragraphs: List[Paragraph],
            min_paragraphs_len: int = 20,
            min_len_for_join: int = 70,
            min_len_for_split: int = 200,
            max_len_for_chunk: int = 100
    ) -> List[str]:
        """
        Объединение коротких и разделение длинных параграфов
        :param paragraphs:  Список текстов параграфов
        :param min_paragraphs_len: Минимальная длинна параграфа
        :param min_len_for_join: Минимальная длина для объединения параграфов
        :param min_len_for_split: Максимальная длина параграфа перед разделением
        :param max_len_for_chunk: Максимальный размер чанка после разделения
        :return:
        """
        logger.debug(f"Всего параграфов: {len(paragraphs)}")
        logger.debug(f"Выполняется фильтрация коротких параграфов (менее {min_paragraphs_len} символов), а также"
                     f"слияние параграфов длинной до {min_len_for_join}...")
        cur_chunk = ""
        merged = []
        for paragraph in paragraphs:
            paragraph_stripped = paragraph.text.strip()

            # Пропускаем слишком короткие параграфы
            if not paragraph_stripped or len(paragraph_stripped) < min_paragraphs_len:
                continue

            if len(cur_chunk) <= min_len_for_join:
                if cur_chunk:
                    cur_chunk = f"{cur_chunk} {paragraph_stripped}"
                else:
                    cur_chunk = paragraph_stripped
            else:
                if cur_chunk:
                    merged.append(cur_chunk)
                cur_chunk = paragraph_stripped
        if cur_chunk:
            merged.append(cur_chunk)
        logger.debug(f"Фильтрация и слияние выполнены. Всего параграфов: {len(merged)}")

        final_chunks = []

        logger.debug(f"Выполняется разделение параграфов длинной  от {min_len_for_split} ...")
        for paragraph in merged:
            paragraph_stripped = paragraph.strip()
            if not paragraph_stripped:
                continue

            if len(paragraph_stripped) <= min_len_for_split:
                final_chunks.append(paragraph_stripped)
                continue

            sentences = re.split(r'(?<=[.!?])\s+', paragraph_stripped)
            cur_chunk = ""
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 5:
                    continue

                if sent and all(c in '.,!?;:()[]{}"\' ' for c in sent):
                    continue

                if len(cur_chunk) + len(sent) + 1 <= max_len_for_chunk:
                    if cur_chunk:
                        cur_chunk = f"{cur_chunk} {sent}"
                    else:
                        cur_chunk = sent
                else:
                    if cur_chunk:
                        final_chunks.append(cur_chunk)
                    cur_chunk = sent
            if cur_chunk:
                final_chunks.append(cur_chunk)

        logger.debug(f"Обработка параграфов закончена. Всего параграфов {len(final_chunks)}")

        return final_chunks

    def __create_chunks(self,
                        text: str,
                        filename: str,
                        file_hash: str,
                        paragraph_idx: int
                        ) -> ChunkModel:
        """Создает чанки и наполняет их метаинформацией"""

        normalized_text = self.__normalize(text)
        no_sensitive_text = self.__replace_sensitive_data(normalized_text)

        char_count = len(normalized_text)
        word_count = len(normalized_text.split())

        metadata = MetadataModel(
            doc_id=file_hash,
            chunk_id=f"{file_hash}_chunk_{paragraph_idx}",
            source=filename,
            chunk_index=paragraph_idx,
            char_count=char_count,
            word_count=word_count
        )

        return ChunkModel(
            text=normalized_text,
            text_sensitive_removed=no_sensitive_text,
            metadata=metadata,
            vectorization_text='text_sensitive_removed'
        )

    def parse(self, file: bytes, filename: str = 'test.docx'):
        """
        Извлечение сырого содержимого из .docx
        Структурный анализ документа (выделение заголовков, списков, таблиц)
        Фильтрация нерелевантных элементов (колонтитулы, номера страниц, изображения)
        Реконструкция логического потока текста (соединение разрывов)
        """
        logger.info(f"получен файл {filename}. Выполняется обработка ...")

        binary_file = file
        file = io.BytesIO(binary_file)
        file_hash = md5(binary_file).hexdigest()[:8]

        chunks: List[ChunkModel] = []
        doc = Document(file)
        filtered_paragraphs = self.__join_short_split_long_paragraphs(doc.paragraphs)

        for idx, paragraph in enumerate(filtered_paragraphs):
            chunks.append(self.__create_chunks(text=paragraph,
                                               filename=filename,
                                               file_hash=file_hash,
                                               paragraph_idx=idx
                                               ))


        logger.info(f"Обработка файла {filename} закончена. Извлечено {len(chunks)} чанков.")

        return chunks


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout
    )

    file_path = Path(__file__).parent.parent.parent.parent.parent / 'test_files/simple_file.docx'
    with open(file_path, 'rb') as f:
        binary_file = f.read()

    parser = DOCXProcessor()
    chunks = parser.parse(binary_file)


if __name__ == "__main__":
    main()
