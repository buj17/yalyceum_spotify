import datetime

import sqlalchemy

from .base import Base


class Artist(Base):
    """Таблица артистов (исполнителей)"""
    __tablename__ = 'artists'

    def __init__(self,
                 *,
                 name: str,
                 bio: str | None = None,
                 country: str | None = None,
                 created_at: datetime.datetime = datetime.datetime.utcnow()):
        super().__init__()
        self.name = name
        self.bio = bio
        self.country = country
        self.created_at = created_at

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
        unique=True,
    )
    bio = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=True,
    )
    country = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=True,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime,
        default=datetime.datetime.utcnow,
    )
    musics = sqlalchemy.orm.relationship(
        "MusicArtistAssociation",
        back_populates="artist",
    )
