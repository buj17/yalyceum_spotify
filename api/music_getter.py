import os
from pathlib import Path
from typing import List, Dict, Optional, Any

import requests


class ApiUtil:
    def __init__(self):
        self.URL_FOR_ALBUMS = "https://saavn.dev/api/search/albums"
        self.URL_FOR_DETAIL_ALBUM = "https://saavn.dev/api/albums"
        self.session = requests.Session()

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Общий метод для выполнения HTTP-запросов."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Request failed: {e}")
            return None

    def get_album_ids_by_category(self, category: str, limit: int = 1) -> Optional[List[str]]:
        """Получает список ID альбомов по категории."""
        params = {"query": category, "limit": limit}
        data = self._make_request(self.URL_FOR_ALBUMS, params)
        return [album["id"] for album in data.get("data", {}).get("results", [])] if data else None

    @staticmethod
    def _extract_image_url(images: List[Dict]) -> Optional[str]:
        """Извлекает URL последнего изображения из списка."""
        return images[-1]["url"] if images else None

    def _process_song(self, song: Dict) -> Dict:
        """Обрабатывает данные песни."""
        return {
            "id": song.get("id"),
            "name": song.get("name"),
            "year": song.get("year"),
            "duration": song.get("duration"),
            "language": song.get("language"),
            "image_url": self._extract_image_url(song.get("image", [])),
            "music_url": song.get("downloadUrl", [{}])[-1].get("url"),
            "artists": [self._process_artist(a) for a in song.get("artists", {}).get("all", [])]
        }

    def _process_artist(self, artist: Dict) -> Dict:
        """Обрабатывает данные артиста."""
        return {
            "id": artist.get("id"),
            "name": artist.get("name"),
            "image_url": self._extract_image_url(artist.get("image", []))
        }

    def get_album_info(self, album_id: str) -> Optional[Dict]:
        """Получает полную информацию об альбоме."""
        data = self._make_request(self.URL_FOR_DETAIL_ALBUM, {"id": album_id})
        if not data:
            return None

        album = data.get("data", {})
        return {
            "id": album_id,
            "name": album.get("name"),
            "description": album.get("description"),
            "image_url": self._extract_image_url(album.get("image", [])),
            "songs": [self._process_song(s) for s in album.get("songs", [])]
        }

    def download_song_data(self, album_data: dict) -> dict[str, list[str]]:
        path_to_download = Path(__file__).parent.parent / "media"
        os.makedirs(path_to_download, exist_ok=True)
        img_path_lst = []
        audio_path_lst = []

        for song in album_data.get("songs", []):
            song_name = song["name"]
            song_key = song_name.strip()

            # Скачиваем изображение
            img_url = song.get("image_url")
            if img_url:
                img_ext = os.path.splitext(img_url)[-1].split("?")[0]
                img_path = os.path.join(path_to_download, f"{song_key}_cover{img_ext}")
                try:
                    with requests.get(img_url, stream=True) as r:
                        r.raise_for_status()
                        with open(img_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    img_path_lst.append(img_path)
                except Exception as e:
                    print(f"Ошибка при скачивании изображения для {song_name}: {e}")

            # Скачиваем аудиофайл
            music_url = song.get("music_url")
            if music_url:
                audio_ext = os.path.splitext(music_url)[-1].split("?")[0]
                audio_path = os.path.join(path_to_download, f"{song_key}_audio{audio_ext}")
                try:
                    with requests.get(music_url, stream=True) as r:
                        r.raise_for_status()
                        with open(audio_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    audio_path_lst.append(audio_path)
                except Exception as e:
                    print(f"Ошибка при скачивании аудио для {song_name}: {e}")

        return {"img_path_lst": img_path_lst, "audio_path_lst": audio_path_lst}
