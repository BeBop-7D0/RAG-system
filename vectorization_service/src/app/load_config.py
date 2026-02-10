import json
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from vectorization_service.src.data_models.app_config import AppConfig


load_dotenv()

settings_path  = Path(__file__).parent / 'settings.json'

with open(settings_path, 'rb') as setting_binary:
    settings = json.load(setting_binary)



port = getenv("VECTORIZATION_SERVICE_APP_PORT")
if not port or not port.isdigit():
    port = 8080

config = AppConfig(
    host=getenv("VECTORIZATION_SERVICE_APP_HOST", "localhost"),
    port=port,
    name=settings.get("VectorizerApp", 'SanicApp')
)
