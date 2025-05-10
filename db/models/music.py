import sqlalchemy

from .base import Base


class Music(Base):
    """Таблица музыки (треков)"""
    __tablename__ = 'musics'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
    )
    release_year = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    duration = sqlalchemy.Column(
        sqlalchemy.Integer,  # В секундах
        nullable=False,
    )
    explicit_content = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=True,
        default=False,
    )
    language = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
    )
    album_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('albums.id'),
        nullable=True,
    )
    artists = sqlalchemy.orm.relationship(
        "MusicArtistAssociation",
        back_populates="music",
    )
    favorited_by = sqlalchemy.orm.relationship(
        "Favorite",
        back_populates="music",
    )
