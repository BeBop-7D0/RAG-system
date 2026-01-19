import io
import re

from docx import Document


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

    def parse(self):
        """
        Извлечение сырого содержимого из .docx
        Структурный анализ документа (выделение заголовков, списков, таблиц)
        Фильтрация нерелевантных элементов (колонтитулы, номера страниц, изображения)
        Реконструкция логического потока текста (соединение разрывов)
        """

        doc = Document(self.file)
        for paragraph in doc.paragraphs[:5]:
            normalized_text = self.__normalize(paragraph.text)
            no_sensitive_text = self.__replace_sensitive_data(normalized_text)



def main():

    with open("../../../test_files/simple_file.docx", 'rb') as f:
        binary_file = f.read()

    parser = DOCXProcessor(binary_file)
    parser.parse()


    print(text)





if __name__ == "__main__":
    main()