import sqlalchemy

from .base import Base


class Album(Base):
    """Таблица альбомов"""
    __tablename__ = "albums"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
    )
    description = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )
    year = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
