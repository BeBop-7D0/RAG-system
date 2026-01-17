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
    def __normalize(text: str) -> str:
        """Нормализация текста (удаление лишних пробелов, непечатаемых символов)"""
        print(text)
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
            clean_text = self.__normalize(paragraph.text)




def main():

    # with open("../../../test_files/simple_file.docx", 'rb') as f:
    #     binary_file = f.read()
    #
    # parser = DOCXProcessor(binary_file)
    # parser.parse()

    bad_tet = """Привет!!! Как твои дела????))  
я вчера купил iPhone 15 Pro Max за 150.000 руб... но он оказался БРАКОВАННЫМ!!! 😡  
Связался со службой поддержки: support@company.ru — НИКТО НЕ ОТВЕЧАЕТ!!!  
Звонил по номеру +7 (999) 123-45-67 и даже писал в WhatsApp (https://wa.me/79991234567).  
P.S. Сайт у них — https://www.company.ru, но он не грузится уже 3 дня...  
#фейл #развод #не_покупайте  

P.P.S. Мой email для обратной связи: ivanov_ivan1990@gmail.com или ivan@ivanov.ru  
(но лучше не пишите — я в отпуске до 01.09.2025!)"""

    step_1 = re.sub(r"\s+"," ", bad_tet)  # удаляем все ли
    step_2 = re.sub(r"([!?*.])\1+", r"\1", step_1)
    print(step_1)

if __name__ == "__main__":
    main()