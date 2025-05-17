import sqlalchemy

from .base import Base


class MusicArtistAssociation(Base):
    __tablename__ = "music_artist"

    music_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("musics.id"),
        primary_key=True,
    )
    artist_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("artists.id"),
        primary_key=True,
    )
    # Связи с основными таблицами
    music = sqlalchemy.orm.relationship("Music", back_populates="artists")
    artist = sqlalchemy.orm.relationship("Artist", back_populates="musics")
