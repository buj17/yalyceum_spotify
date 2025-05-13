from ..connect import create_session
from ..models import User
from ..s3manager import S3Manager


class EmailAlreadyExistsError(Exception):
    """Данная ошибка возникает в случае попытки добавить в базу данных уже существующий email"""


class UserManager:
    """Класс для управления пользователями в базе данных"""

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Получение пользователя по id

        :param user_id: id пользователя
        :type user_id: int
        :raises ValueError: Если пользователя с данным user_id не существует
        :return: Объект модели User
        :rtype: User
        """
        with create_session() as db_session:
            user_instance: User | None = db_session.get(User, user_id)
            if user_instance is None:
                raise ValueError(f'User not found with id: {user_id}')
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

    def add_user(self, user: User) -> None:
        """Добавление объекта модели User в базу данных

        :param user: Объект модели User
        :type user: User
        :raises EmailAlreadyExistsError: Если пользователь с таким email уже существует
        """
        if self._email_exists(user.email):
            raise EmailAlreadyExistsError(f'Email already exists: {user.email}')

        with create_session() as db_session:
            try:
                db_session.add(user)
                db_session.commit()
                db_session.refresh(user)
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

    @staticmethod
    def _email_exists(email: str) -> bool:
        with create_session() as db_session:
            user_instance: User | None = db_session.query(User).filter(User.email == email).first()
            return user_instance is not None

    @staticmethod
    def upload_avatar(user_id: int, content: bytes):
        """

        :param user_id:
        :param content:
        :return:
        """

        with (create_session() as db_session,
              S3Manager() as s3_manager):
            s3_manager.upload_file()

    @staticmethod
    def get_avatar_url(user_id: int) -> str:
        pass

    @staticmethod
    def add_favorite_track(user_id: int, music_id: int):
        pass

    @staticmethod
    def get_favorite_tracks(user_id: int):
        pass

    @staticmethod
    def remove_favorite_track(user_id: int, music_id: int):
        pass
