import logging.config
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv()


def setup_logging():
    log_level = os.getenv('INGESTION_SERVICE_LOG_LEVEL', 'INFO').upper()
    log_path = Path(os.getenv('INGESTION_SERVICE_LOG_PATH', './logs'))
    log_path.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,   # версия формата
        "disable_existing_loggers": False,  # не отключать существующие логгеры. Если True, то все логеры, созданные до
        # вызова dictConfig будут отключены
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s : %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {   # настройки записи логов
            "console": {    # вывод в консоль
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "level": log_level,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_path / "current.log"),
                "maxBytes": 10_000_000,  # 10 MB
                "backupCount": 5,
                "formatter": "standard"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ['console', 'file']
        }

    }


    logging.config.dictConfig(logging_config)