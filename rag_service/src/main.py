import logging

from ingestion_service.src.logger import setup_logging


setup_logging()
logger = logging.getLogger("RAG Service")


def main():

    logger.debug("This is RAG Service")


if __name__ == "__main__":
    main()
