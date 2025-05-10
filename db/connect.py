import sqlalchemy.orm
import sqlalchemy_utils
from sqlalchemy.orm import Session

from . import models
from .db_config import settings

DATABASE_URL = settings.DATABASE_URL
engine = sqlalchemy.create_engine(DATABASE_URL)


def create_db_and_tables():
    """
    Создает базу данных (если она не существует) и таблицы,
    определенные в SQLAlchemy моделях.
    """
    if not sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.create_database(engine.url)

    models.Base.metadata.create_all(engine)


create_db_and_tables()

SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_session() -> Session:
    return SessionLocal()
