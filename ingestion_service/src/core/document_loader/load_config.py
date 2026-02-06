import json
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from ingestion_service.src.core.document_loader.data_models.loader_config import LoaderConfig


load_dotenv()

settings_path  = Path(__file__).parent / 'settings.json'

with open(settings_path, 'rb') as setting_binary:
    settings = json.load(setting_binary)


config = LoaderConfig(
    type=str(settings.get('type', 'qdrant')).upper(),
    batch_size=settings.get('batch_size', 15),
    https = settings.get('https', False),
    prefix=settings.get('prefix', ""),
    timeout=settings.get('timeout', 10),
    api_key=getenv('INGESTION_SERVICE_LOADER_API_KEY', ''),
    port=getenv('INGESTION_SERVICE_LOADER_PORT', 6333),
    host=getenv('INGESTION_SERVICE_LOADER_HOST', '127.0.0.1')
)
