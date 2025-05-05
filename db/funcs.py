import os
from datetime import datetime
from io import BytesIO

from . import connect, models, s3manager
from api.music_getter import ApiUtil


def get_user_by_username(username):
    db = connect.SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.username == username).first()  # Убрал .data
        return user
    except Exception as e:
        print(f"Ошибка в get_user_by_username, {e}")
        return None
    finally:
        db.close()

def get_user_by_email(email):
    db = connect.SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.email == email).first()  # Убрал .data
        return user
    except Exception as e:
        print(f"Ошибка в get_user_by_email, {e}")
        return None
    finally:
        db.close()

def get_user_by_id(id):
    db = connect.SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.id == id).first()
        return user
    except Exception as e:
        print(f"Ошибка в get_user_by_id, {e}")
    finally:
        db.close()

def create_user(email, username, password):
    db = connect.SessionLocal()
    try:
        user = models.User(
            email=email, username=username)
        user.set_password(password)
        db.add(user)
        db.commit()
    except Exception as e:
        print(f"Ошибка в create_user, {e}")
    finally:
        db.close()


def download_music_cover_and_push_into_s3_and_db(category, limit=1):
    db = connect.SessionLocal()
    try:
        api_util = ApiUtil()
        album_ids = api_util.get_album_ids_by_category(category, limit=limit)
        if album_ids:
            for album_id in album_ids:
                album_info = api_util.get_album_info(album_id)
                res_of_download = api_util.download_song_data(album_info)
                img_path_lst = res_of_download["img_path_lst"]
                audio_path_lst = res_of_download["audio_path_lst"]

                manager = s3manager.S3Manager()

                # Создаем альбом в БД
                album = models.Album(
                    id=album_id,
                    name=album_info.get('name', 'Unknown Album'),
                    description=album_info.get('description', ''),
                    year=album_info.get('year', datetime.now().year)
                )
                db.add(album)

                for img_path, audio_path in zip(img_path_lst, audio_path_lst):
                    # Загружаем изображение в S3
                    img_name = os.path.basename(img_path)
                    try:
                        manager.get_file(img_name)
                    except ValueError:
                        continue
                    with open(img_path, 'rb') as file:
                        img_bytes = file.read()
                        img_bytes_io = BytesIO(img_bytes)
                    manager.upload_file(img_name, img_bytes_io)

                    # Загружаем аудио в S3
                    audio_name = os.path.basename(audio_path)
                    try:
                        manager.get_file(audio_name)
                    except ValueError:
                        continue
                    with open(audio_path, 'rb') as file:
                        audio_bytes = file.read()
                        audio_bytes_io = BytesIO(audio_bytes)
                    manager.upload_file(audio_name, audio_bytes_io)

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
                        album_id=album_id
                    )
                    db.add(music)
                    db.flush()

                    # Создаем связи между музыкой и артистами
                    for artist in artists:
                        association = models.MusicArtistAssociation(
                            music_id=music.id,
                            artist_id=artist.id
                        )
                        db.add(association)

                db.commit()
                print(f"Успешно сохранен альбом: {album.name}")

    except Exception as e:
        db.rollback()
        print(f"Ошибка в download_music_cover_and_push_into_s3_and_db, {e}")
    finally:
        db.close()