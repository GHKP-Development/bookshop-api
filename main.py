from time import sleep

from config import Config
from src.db.connection import Database
from src.utils.logging.logger import Logger


def main():
    cfg = Config.from_file()
    logger = Logger("MAIN", cfg.log_level)
    logger.info("Initializing database...")
    Database(cfg.database, logger.clone("DB"))
    logger.info("Database initialized.")
    sleep(1120)


if __name__ == "__main__":
    main()