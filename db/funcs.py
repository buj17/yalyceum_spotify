import os
from datetime import datetime
from io import BytesIO

from api.music_getter import ApiUtil
from . import connect, models, s3manager


def download_music_cover_and_push_into_s3_and_db(category: str, limit=1):
    db = connect.SessionLocal()
    try:
        api_util = ApiUtil()
        album_ids = api_util.get_album_ids_by_category(category, limit=limit)  # забираем все альбомы этой категории
        if album_ids:
            for album_id in album_ids:
                album_info = api_util.get_album_info(album_id)  # инфа об альбоме
                res_of_download = api_util.download_song_data(album_info)  # загружаем треки
                img_path_lst = res_of_download["img_path_lst"]  # список со ссылками на картинки
                audio_path_lst = res_of_download["audio_path_lst"]  # список со ссылками на треки

                # print(img_path_lst)
                # print(audio_path_lst)
                # pprint.pprint(album_info)

                manager = s3manager.S3Manager()

                album = db.query(models.Album).filter(
                    models.Album.name == album_info.get('name', 'Unknown Album')
                ).first()
                if album is None:
                    # Создаем альбом в БД
                    album = models.Album(
                        name=album_info.get('name', 'Unknown Album'),
                        description=album_info.get('description', ''),
                        year=album_info.get('year', datetime.now().year)
                    )
                    db.add(album)
                    db.flush()
                    db.refresh(album)

                for img_path, audio_path in zip(img_path_lst, audio_path_lst):
                    img_name = os.path.basename(img_path)
                    audio_name = os.path.basename(audio_path)

                    # Получаем информацию о песне
                    song_info = next((s for s in album_info['songs']
                                      if s['name'] in audio_name), None)
                    if not song_info:
                        continue

                    # Создаем артистов
                    artists = []
                    for artist_data in song_info.get('artists', []):
                        artist = db.query(models.Artist).filter(
                            models.Artist.name == artist_data['name']
                        ).first()
                        if not artist:
                            artist = models.Artist(
                                name=artist_data['name'],
                                bio='',
                                country=''
                            )
                            db.add(artist)
                            db.flush()
                        artists.append(artist)

                    # Создаем музыку
                    music = models.Music(
                        name=song_info['name'],
                        release_year=song_info.get('year',
                                                   datetime.now().year),
                        duration=song_info.get('duration', 0),
                        language=song_info.get('language', 'Unknown'),
                        album_id=album.id
                    )
                    db.add(music)
                    db.flush()
                    db.refresh(music)

                    # Создаем связи между музыкой и артистами
                    for artist in artists:
                        association = db.get(models.MusicArtistAssociation, (music.id, artist.id))

                        if association is None:
                            association = models.MusicArtistAssociation(
                                music_id=music.id,
                                artist_id=artist.id
                            )
                            db.add(association)
                            db.flush()

                    # Загружаем изображение в S3
                    print(img_name)
                    with open(img_path, 'rb') as file:
                        img_bytes = file.read()
                        img_bytes_io = BytesIO(img_bytes)
                    img_root, img_extension = os.path.splitext(img_name)
                    manager.upload_file(f'music_image_{music.id}{img_extension}', img_bytes_io, force=True)

                    # Загружаем аудио в S3
                    with open(audio_path, 'rb') as file:
                        audio_bytes = file.read()
                        audio_bytes_io = BytesIO(audio_bytes)
                    audio_root, audio_extension = os.path.splitext(audio_name)
                    manager.upload_file(f'music_audio_{music.id}{audio_extension}', audio_bytes_io, force=True)

                    print(f'music_image_{music.id}{img_extension}')
                    print(f'music_audio_{music.id}{audio_extension}')

                db.commit()
                print(f"Успешно сохранен альбом: {album.name}")

    except Exception as e:
        db.rollback()
        print(f"Ошибка в download_music_cover_and_push_into_s3_and_db, {e}")
    finally:
        db.close()
