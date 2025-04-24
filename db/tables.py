import datetime
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

Base = declarative_base()


# Таблица артистов (исполнителей)
class Artist(Base):
    __tablename__ = 'artists'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False,
        unique=True,
    )
    bio = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=True,
    )
    country = sqlalchemy.Column(
        sqlalchemy.String,
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


# Таблица альбомов
class Album(Base):
    __tablename__ = 'albums'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
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



# Таблица музыки (треков)
class Music(Base):
    __tablename__ = 'musics'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
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
        sqlalchemy.String,
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


class MusicArtistAssociation(Base):
    __tablename__ = 'music_artist'

    music_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('musics.id'),
        primary_key=True,
    )
    artist_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('artists.id'),
        primary_key=True,
    )
    # Связи с основными таблицами
    music = sqlalchemy.orm.relationship("Music", back_populates="artists")
    artist = sqlalchemy.orm.relationship("Artist", back_populates="musics")
