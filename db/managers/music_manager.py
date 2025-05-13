from typing import Sequence

from sqlalchemy.orm import Session

from ..models import Music


class MusicManager:
    def __init__(self, db_session: Session):
        pass

    @staticmethod
    def get_music_audio_url(music_id: int) -> str | None:
        pass

    @staticmethod
    def get_music_image_url(music_id: int) -> str | None:
        pass

    @staticmethod
    def search_music(query: str) -> Sequence[Music]:
        pass




