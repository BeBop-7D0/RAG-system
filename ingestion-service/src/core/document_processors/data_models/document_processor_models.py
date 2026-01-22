from pydantic import BaseModel, Field


class MetadataModel(BaseModel):
    doc_id: str = Field(..., description="Хэш документа")
    chunk_id: str = Field(..., description="id чанка")
    source: str = Field(..., description="Название файла")

    chunk_index: int = Field(..., description="Порядковый номер чанка в документе")

    char_count: int = Field(..., description="Длинна чанка")
    word_count: int = Field(..., description="Количество слов в чанке")


class ChunkModel(BaseModel):
    text: str = Field(..., description="Исходный нормализованный текст")
    text_sensitive_removed: str = Field(..., description="Текст с удаленными чувствительными данными")
    metadata: MetadataModel
    vectorization_text: str = Field(..., description="Указатель на текст, который будет использоваться для поиска."
                                                     "Это может быть поле text или text_sensitive_removed")