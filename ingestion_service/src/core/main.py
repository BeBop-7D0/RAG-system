import logging

from ingestion_service.src.logger import setup_logging


setup_logging()
logger = logging.getLogger(__name__)
logger.info("Сервис запущен")



# todo: файлы окружения свои в какждом микросервисе?
# todo: перенести logs на базовый уровень сервиса
# todo: разобраться с зависимостями torch и torch vision
# todo: разобраться с качиванием и кешированием моделей