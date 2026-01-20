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
    def __filter_short_paragraphs(paragraphs: List[Paragraph], min_len: int = 20) -> List[str]:
        filtered_list = list(filter(lambda x: len(x.text.strip()) >= min_len, paragraphs))
        return list(map(lambda x: x.text, filtered_list))

    @staticmethod
    def __join_short_split_long_paragraphs(
            paragraphs: List[str],
            min_len_for_join: int = 70,
            min_len_for_split: int = 200,
            max_len_for_chunk: int = 100
    ) -> List[str]:

        merged = []
        i = 0
        while i < len(paragraphs):
            current = paragraphs[i]
            if len(current) <= min_len_for_join and i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1]
                combined = current + " " + next_para
                merged.append(combined)
                i += 2
            else:
                merged.append(current)
                i += 1

        # Этап 2: Разбиение длинных чанков
        result = []
        # Используем finditer, чтобы сохранить знаки препинания
        sentence_endings = re.compile(r'[.!?]+')

        for chunk in merged:
            if len(chunk) <= min_len_for_split:
                result.append(chunk)
            else:
                # Получаем позиции концов предложений
                sentences = []
                start = 0
                for match in sentence_endings.finditer(chunk):
                    end = match.end()  # включаем знак препинания
                    sentence = chunk[start:end].strip()
                    if sentence:
                        sentences.append(sentence)
                    start = end

                # Добавляем остаток текста (если есть)
                remainder = chunk[start:].strip()
                if remainder:
                    sentences.append(remainder)

                # Собираем чанки до max_len_for_chunk
                current_chunk = ""
                for sent in sentences:
                    # Если предложение само слишком длинное — добавляем как есть
                    if len(sent) > max_len_for_chunk:
                        if current_chunk:
                            result.append(current_chunk)
                            current_chunk = ""
                        result.append(sent)
                        continue

                    # Проверяем, поместится ли предложение в текущий чанк
                    new_chunk = current_chunk + (" " if current_chunk else "") + sent
                    if len(new_chunk) <= max_len_for_chunk:
                        current_chunk = new_chunk
                    else:
                        # Сохраняем текущий чанк и начинаем новый
                        if current_chunk:
                            result.append(current_chunk)
                        current_chunk = sent

                # Не забываем последний чанк
                if current_chunk:
                    result.append(current_chunk)

        return result

    def parse(self):
        """
        Извлечение сырого содержимого из .docx
        Структурный анализ документа (выделение заголовков, списков, таблиц)
        Фильтрация нерелевантных элементов (колонтитулы, номера страниц, изображения)
        Реконструкция логического потока текста (соединение разрывов)
        """

        doc = Document(self.file)
        filtered_paragraphs = self.__filter_short_paragraphs(doc.paragraphs)

        for paragraph in filtered_paragraphs:
            normalized_text = self.__normalize(paragraph)
            no_sensitive_text = self.__replace_sensitive_data(normalized_text)
            # print(len(normalized_text))

        filtered_paragraphs = self.__join_short_split_long_paragraphs(filtered_paragraphs)

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
