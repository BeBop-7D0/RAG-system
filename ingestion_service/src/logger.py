import json
import logging.config
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv()


logger_settings_path  = Path(__file__).parent / 'logger_settings.json'

with open(logger_settings_path, 'rb') as setting_binary:
    logger_settings = json.load(setting_binary)

print(logger_settings)

def setup_logging():
    log_level = logger_settings.get("log_level", "DEBUG").upper()
    log_path = logger_settings.get('log_dir', './logs')
    log_path.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,   # версия формата
        "disable_existing_loggers": False,  # не отключать существующие логгеры. Если True, то все логеры, созданные до
        # вызова dictConfig будут отключены
        "formatters": {
            "standard": {
                "format": logger_settings.get("format"),
                "datefmt": logger_settings.get("datefmt"),
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
                "maxBytes": logger_settings.get("max_bytes"),
                "backupCount": logger_settings.get("backup_count"),
                "formatter": "standard"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ['console', 'file']
        }

    }


    logging.config.dictConfig(logging_config)