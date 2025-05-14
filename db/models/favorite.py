import sqlalchemy

from .base import Base


class Favorite(Base):
    __tablename__ = 'favorite'

    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('users.id'),
        primary_key=True
    )
    music_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('musics.id'),
        primary_key=True
    )
    user = sqlalchemy.orm.relationship("User", back_populates="favorites")
    music = sqlalchemy.orm.relationship("Music", back_populates="favorited_by")

    def __repr__(self):
        return f"{self.user_id} -> {self.music_id}"
