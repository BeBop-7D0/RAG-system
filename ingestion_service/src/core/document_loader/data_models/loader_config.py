from typing import Optional
from pydantic import BaseModel, Field


class LoaderConfig(BaseModel):
    type: Optional[str] = Field(None, description="Название базы данных [qdrant]")
    port: Optional[int] = Field(None, description="Порт для подключения к хранилищу")
    host: Optional[str] = Field(None, description="Хост для подключения к хранилищу")
    batch_size: Optional[int] = Field(None, description="Размер батча для загрузки в хранилище")
    https: Optional[bool] = Field(None, description="Использовать https при отправке данных в хранилище")
    api_key: Optional[str] = Field(None, description="API ключ")
    prefix: Optional[str] = Field(None, description="Префикс для URL")
    timeout: Optional[int] = Field(None, description="Таймаут подключения")
