import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .base import Base


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
        nullable=False
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

    favorites = sqlalchemy.orm.relationship(
        "Favorite",
        back_populates="user",
    )
