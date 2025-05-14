from io import BytesIO

from PIL import Image

from ..connect import create_session
from ..models import User, Favorite, Music
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

    def upload_avatar(self, user_id: int, content: bytes):
        """ Загрузка аватарки пользователя в s3 хранилище

        :param user_id: id пользователя
        :type user_id: int
        :param content: Валидные байты, хранящие изображение
        :type content: bytes
        """
        try:
            self.get_user_by_id(user_id)
        except ValueError:
            raise

        converted_content = _convert_image_bytes_to_jpeg(content)

        with S3Manager() as s3_manager:
            s3_manager.upload_file(f'user_avatar_{user_id}.jpg', converted_content, force=True)

    @staticmethod
    def get_avatar_url(user_id: int) -> str | None:
        """Возвращает url на аватарку пользователя

        :param user_id: id пользователя
        :return: url на аватарку пользователя или None, если у данного пользователя нет аватарки
        :rtype: str | None
        """
        with S3Manager() as s3_manager:
            try:
                return s3_manager.get_file_url(
                    f'user_avatar_{user_id}.jpg',
                    content_type='image/jpeg',
                    content_disposition='inline'
                )
            except ValueError:
                return None

    @staticmethod
    def add_favorite_track(user_id: int, music_id: int):
        """Добавляет трек для пользователя в избранное

        :param user_id: id пользователя
        :type user_id: int
        :param music_id: id трека
        :type music_id: int
        :raises ValueError: Если трек уже в избранных
        """
        with create_session() as db_session:
            favorite_instance: Favorite | None = db_session.get(Favorite, (user_id, music_id))
            if favorite_instance is not None:
                raise ValueError('Favorite instance already exists')

            favorite = Favorite(user_id=user_id, music_id=music_id)
            db_session.add(favorite)
            db_session.commit()

    @staticmethod
    def get_favorite_tracks(user_id: int) -> list[Music]:
        """Возвращает список избранных треков пользователя

        :param user_id: id пользователя
        :type user_id: int
        :return: Список объектов модели Music
        :rtype: list[Music]
        """
        with create_session() as db_session:
            user_instance: User | None = db_session.get(User, user_id)
            if user_instance is None:
                raise ValueError(f'User does not exist with id: {user_id}')
            return list(map(lambda favorite: favorite.music, user_instance.favorites))

    @staticmethod
    def remove_favorite_track(user_id: int, music_id: int):
        """Удаляет трек из избранных

        :param user_id: id пользователя
        :type user_id: int
        :param music_id: id трека
        :type music_id: int
        :raises ValueError: Если трека нет в избранных
        """
        with create_session() as db_session:
            favorite_instance: Favorite | None = db_session.get(Favorite, (user_id, music_id))
            if favorite_instance is None:
                raise ValueError('Favorite instance does not exist')

            db_session.delete(favorite_instance)
            db_session.commit()


def _convert_image_bytes_to_jpeg(image_bytes: bytes) -> BytesIO:
    try:
        img = Image.open(BytesIO(image_bytes))
        img = img.convert('RGB')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        return img_bytes

    except Exception as ex:
        raise ValueError('Invalid image data') from ex
