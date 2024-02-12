from time import sleep

from src.db.config import DBConfig, DBEngineType
from src.db.connection import Database


def main():
    Database(DBConfig(
        db_name="bookshop",
        engine=DBEngineType.POSTGRESQL,
        host="postgres",
        port=5432,
        username="postgres",
        password="1234"
    ))
    print("Initialized")
    sleep(120)


if __name__ == "__main__":
    main()