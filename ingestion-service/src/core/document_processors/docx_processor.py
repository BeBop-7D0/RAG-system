import io
import re
from typing import List

from docx import Document
from docx.text.paragraph import Paragraph

from base_processor import DocProcessor


class DOCXProcessor(DocProcessor):
    """Класс, реализующий методы для обработки
    .docx файлов
    """

    def __init__(self, file: bytes):
        self.file = io.BytesIO(file)

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

        final_chunks = []

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
                if not sent.strip():
                    continue
                sent = sent.strip()

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

        return final_chunks

    def parse(self):
        """
        Извлечение сырого содержимого из .docx
        Структурный анализ документа (выделение заголовков, списков, таблиц)
        Фильтрация нерелевантных элементов (колонтитулы, номера страниц, изображения)
        Реконструкция логического потока текста (соединение разрывов)
        """

        doc = Document(self.file)

        filtered_paragraphs = self.__join_short_split_long_paragraphs(doc.paragraphs)

        for paragraph in filtered_paragraphs:
            normalized_text = self.__normalize(paragraph)
            no_sensitive_text = self.__replace_sensitive_data(normalized_text)
            print(len(normalized_text))



def main():

    with open("../../../test_files/simple_file.docx", 'rb') as f:
        binary_file = f.read()

    parser = DOCXProcessor(binary_file)
    parser.parse()






if __name__ == "__main__":
    main()