from sanic import Request
from sanic.response import JSONResponse
from sanic.blueprints import Blueprint

embed_bp = Blueprint('EmbeddingBlueprint', '/rag_system/vectorizer/embed')


@embed_bp.get("/")
async def embed_handler(request: Request) -> JSONResponse:
    """Эндпоинт для векторизации поступающего текста"""

    response = JSONResponse()
    response_body = {
        "message": "OK"
    }

    response.set_body(response_body)
    response.status = 200

    return response


