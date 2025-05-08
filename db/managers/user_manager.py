from ..connect import create_session
from ..models import User


class UserManager:
    """Класс для управления пользователями в базе данных"""
    @staticmethod
    def get_user_by_username(username: str) -> User:
        """Получение пользователя по имени

        :param username: Имя пользователя
        :type username: str
        :raises ValueError: Если пользователя с таким именем не существует
        :return: Объект модели User
        :rtype: User
        """
        with create_session() as db_session:
            user_instance: User | None = db_session.query(User).filter(User.username == username).first()
            if user_instance is None:
                raise ValueError(f'User not found with username: {username}')
            return user_instance

    @staticmethod
    def get_user_by_email(email: str) -> User:
        """Получение пользователя по адресу эл. почты

        :param email: Адрес эл. почты пользователя
        :type email: str
        :raises ValueError: Если пользователя с такой электронной почтой не существует
        :return: Объект модели User
        :rtype: User
        """
        with create_session() as db_session:
            user_instance: User | None = db_session.query(User).filter(User.email == email).first()
            if user_instance is None:
                raise ValueError(f'User not found with email: {email}')
            return user_instance

    @staticmethod
    def add_user(user: User) -> None:
        """Добавление объекта модели User в базу данных

        :param user: Объект модели User
        :type user: User
        """
        with create_session() as db_session:
            try:
                db_session.add(user)
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise

    @staticmethod
    def update_user_info(user: User) -> None:
        """Обновление информации о пользователе в базе данных

        :param user: Объект модели User
        :type user: User
        """
        with create_session() as db_session:
            try:
                db_session.merge(user)
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise

    @staticmethod
    def delete_user(user: User):
        """Удаление пользователя из базы данных

        :param user: Объект модели User
        :type user: User
        """
        with create_session() as db_session:
            try:
                db_session.delete(user)
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise
