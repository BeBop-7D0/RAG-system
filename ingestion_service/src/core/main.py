import logging

from ingestion_service.src.logger import setup_logging


setup_logging()
logger = logging.getLogger(__name__)
logger.info("Сервис запущен")