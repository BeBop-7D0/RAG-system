import logging

from vectorization_service.src.logger import setup_logging


setup_logging()
logger = logging.getLogger("Vectorization Service")


def main():

    logger.debug("This is Vectorization Service")


if __name__ == "__main__":
    main()
