from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    host: str = Field(..., description="адресс хоста для приложения векторизации")
    port: int = Field(..., description="порт хоста для приложения векторизации")
    name: str = Field(..., description="название sanic-приложения")