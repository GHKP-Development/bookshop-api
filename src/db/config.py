from dataclasses import dataclass


class DBEngineType:
    SQLITE: str = "sqlite"
    POSTGRESQL: str = "postgresql"


@dataclass(repr=False)
class DBConfig:

    db_name: str
    engine: str
    host: str = None
    port: int = None
    username: str = None
    password: str = None

    def __str__(self) -> str:
        match self.engine:
            case DBEngineType.SQLITE:
                return f'sqlite:///{self.db_name}.db'
            case DBEngineType.POSTGRESQL:
                return f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}'
            case _:
                raise ValueError(f"Unrecognized database engine type: {self.engine}")
