from sqlalchemy.orm import Session

from ..models import Music
from ..s3manager import S3Manager


class MusicManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @staticmethod
    def get_music_audio_url(music_id: int) -> str | None:
        """Возвращает url на файл с музыкой по id

        :param music_id: id музыки
        :type music_id: int
        :return: url, содержащий трек или None, если файл не найден
        :rtype: str | None
        """
        with S3Manager() as s3_manager:
            try:
                url = s3_manager.get_file_url_safe(
                    f'music_audio_{music_id}.mp4',
                    content_type='audio/mp3',
                    content_disposition='inline'
                )
                return url
            except ValueError:
                return None

    @staticmethod
    def get_music_image_url(music_id: int) -> str | None:
        """Возвращает url на файл с изображением к треку по id

        :param music_id: id музыки
        :type music_id: int
        :return: url, содержащий JPEG изображение или None, если файл не найден
        :rtype: str | None
        """
        with S3Manager() as s3_manager:
            try:
                url = s3_manager.get_file_url_safe(
                    f'music_image_{music_id}.jpg',
                    content_type='image/jpeg',
                    content_disposition='inline'
                )
                return url
            except ValueError:
                return None

    @staticmethod
    def get_music_url_pair(music_id: int) -> tuple[str, str] | None:
        with S3Manager() as s3_manager:
            try:
                url_pair = (
                    s3_manager.get_file_url_safe(
                        f'music_audio_{music_id}.mp4',
                        content_type='audio/mp3',
                        content_disposition='inline'
                    ),
                    s3_manager.get_file_url_safe(
                        f'music_image_{music_id}.jpg',
                        content_type='image/jpeg',
                        content_disposition='inline'
                    )
                )
                return url_pair
            except ValueError:
                return None

    @staticmethod
    def get_music_url_pairs(*music_ids: int) -> list[tuple[str, str]]:
        """Возвращает список, каждый элемент которого - кортеж с первым элементом - url на аудио музыки
        и вторым элементом - url на изображение к музыке.\n
        Внимание! Данный метод не проверяет существование записей в базе данных и файлов в s3.
        Используйте данный метод, если уверены, что в базе данных и s3 хранилище существует необходимая информация.

        :param music_ids: id треков
        :return: Список, каждый элемент которого - кортеж с первым элементом - url на аудио музыки
        и вторым элементом - url на изображение к музыке.
        :rtype: list[tuple[str, str]]
        """
        with S3Manager() as s3_manager:
            url_lists = s3_manager.get_file_group_urls(
                *zip(
                    map(
                        lambda music_id: f'music_audio_{music_id}.mp4',
                        music_ids
                    ),
                    map(
                        lambda music_id: f'music_image_{music_id}.jpg',
                        music_ids
                    )
                ),
                content_types=('audio/mp3', 'image/jpeg'),
                content_disposition='inline'
            )
        res: list[tuple[str, str]] = list(map(tuple, url_lists))
        return res

    def search_music(self, pattern: str) -> list[type[Music]]:
        """Возвращает список объектов модели Music, в название которых входит паттерн query

        :param pattern: Паттерн для поиска
        :type pattern: str
        :return: Список объектов модели Music, в название которых соответствует '%pattern%'
        :rtype: list[type[Music]]
        """
        return self.db_session.query(Music).filter(Music.name.ilike(f'%{pattern}%')).all()
