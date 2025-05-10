import sqlalchemy

from .base import Base


class Favorite(Base):
    __tablename__ = 'favorite'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('users.id'),
    )
    music_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('musics.id'),
    )
    user = sqlalchemy.orm.relationship("User", back_populates="favorites")
    music = sqlalchemy.orm.relationship("Music", back_populates="favorited_by")

    def __repr__(self):
        return f"{self.user_id} -> {self.music_id}"
