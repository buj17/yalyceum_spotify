import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class Artist(Base):
    """Таблица артистов (исполнителей)"""
    __tablename__ = 'artists'

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


class Album(Base):
    """Таблица альбомов"""
    __tablename__ = 'albums'

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


class User(Base, UserMixin):
    """Таблица пользователей"""
    __tablename__ = 'users'

    def __init__(self,
                 *,
                 username: str,
                 email: str,
                 password: str,
                 is_active: bool = True):
        super().__init__()
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_active = is_active

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True
    )
    username = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
        unique=True
    )
    email = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
        unique=True
    )
    password = sqlalchemy.Column(
        sqlalchemy.String(512),
        nullable=False
    )

    is_active = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=True
    )

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'
