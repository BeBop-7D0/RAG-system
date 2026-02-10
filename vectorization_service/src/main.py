import logging

from vectorization_service.src.app.load_config import config
from vectorization_service.src.logger import setup_logging
from vectorization_service.src.app.app import app

setup_logging()
logger = logging.getLogger("Vectorization Service")


def main():

    logger.debug("This is Vectorization Service")
    app.run(host=config.host, port=config.port, debug=True)


if __name__ == "__main__":
    main()