from typing import Union, List
from pydantic import BaseModel, Field, ConfigDict


class MetadataModel(BaseModel):
    doc_id: str = Field(..., description="Хэш документа")
    chunk_id: str = Field(..., description="id чанка")
    source: str = Field(..., description="Название файла")

    chunk_index: int = Field(..., description="Порядковый номер чанка в документе")

    char_count: int = Field(..., description="Длинна чанка")
    word_count: int = Field(..., description="Количество слов в чанке")


class ChunkModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    text: Union[str, List[float]] = Field(..., description="Исходный нормализованный текст (Опционально: в виде вектора)")
    text_sensitive_removed: Union[str, List[float]] = Field(..., description="Текст с удаленными чувствительными данными (Опционально: в виде вектора)")
    metadata: MetadataModel
    vectorization_text: str = Field(..., description="Указатель на текст, который будет использоваться для поиска."
                                                     "Это может быть поле text или text_sensitive_removed")

    @property
    def vectorization_value(self):
        if self.vectorization_text == 'text':
            return self.text
        elif self.vectorization_text == 'text_sensitive_removed':
            return self.text_sensitive_removed
        else:
            raise ValueError("Некорректное значение vectorization_text")
