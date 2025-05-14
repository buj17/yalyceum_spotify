from typing import Sequence

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
                url = s3_manager.get_file_url(
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
                url = s3_manager.get_file_url(
                    f'music_audio_{music_id}.jpg',
                    content_type='image/jpeg',
                    content_disposition='inline'
                )
                return url
            except ValueError:
                return None

    @staticmethod
    def search_music(query: str) -> Sequence[Music]:
        pass
