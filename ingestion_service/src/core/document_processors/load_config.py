import json
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from ingestion_service.src.core.document_processors.data_models.processor_config import ProcessorConfig


load_dotenv()

settings_path  = Path(__file__).parent / 'settings.json'

with open(settings_path, 'rb') as setting_binary:
    settings = json.load(setting_binary)


load_dotenv()

config = ProcessorConfig(
    min_paragraphs_len=settings.get("min_paragraphs_len", 21),
    min_len_for_join=settings.get("min_len_for_join", 36),
    min_len_for_split=settings.get("min_len_for_split", 191),
    max_len_for_chunk=settings.get("max_len_for_chunk", 101),
)
