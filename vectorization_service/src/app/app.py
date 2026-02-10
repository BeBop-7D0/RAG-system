from sanic import Sanic, Request
from sanic.response import JSONResponse

from vectorization_service.src.app.load_config import config
from vectorization_service.src.app.blueprints.embed import embed_bp


app = Sanic(config.name)

app.blueprint(embed_bp)


@app.get("/rag_system/vectorizer/check_health")
async def health_handler(request:  Request) -> JSONResponse:
    """"Эндпоинт для проверки состояния сервиса векторизации"""

    response = JSONResponse()
    response_body = {
        "message": "OK"
    }

    response.set_body(response_body)
    response.status = 200

    return response
