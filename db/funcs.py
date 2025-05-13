import os
from datetime import datetime
from io import BytesIO
from typing import Optional

from api.music_getter import ApiUtil
from . import connect, models, s3manager


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


def get_music_by_id(id):
    db = connect.SessionLocal()
    try:
        music = db.query(models.Music).filter(
            models.Music.id == id).first()
        return music
    except Exception as e:
        print(f"get_music_by_id в create_user, {e}")
    finally:
        db.close()


def add_to_favorite_music(user, music):
    db = connect.SessionLocal()
    try:
        favorite = models.Favorite(
            user_id=user, music_id=music)
        db.add(favorite)
        db.commit()
    except Exception as e:
        print(f"Ошибка в add_to_favorite_music, {e}")
    finally:
        db.close()


def get_avatar_from_user(user: models.User) -> None:
    db = connect.SessionLocal()
    try:
        if user.is_avatar:
            avatar_path: str = f"user_avatar_{user.id}.jpg"
            manager = s3manager.S3Manager()
            streaming_body = manager.get_file(avatar_path)

            # Сохраняем содержимое в файл
            with open(f"avatars/{avatar_path}", 'wb') as f:
                f.write(streaming_body.read())
    except Exception as e:
        print(f"Ошибка в get_avatar_from_user, {e}")
    finally:
        db.close()


def upload_user_avatar(user: models.User, avatar_file) -> Optional[bool]:
    db = connect.SessionLocal()
    try:
        avatar_filename = f"user_avatar_{user.id}.jpg"

        manager = s3manager.S3Manager()

        try:
            manager.get_file(avatar_filename)
        except ValueError:
            manager.delete_file(avatar_filename)

        # Загружаем файл в S3
        if isinstance(avatar_file, str):
            # Если это путь к файлу
            with open(avatar_file, 'rb') as file:
                avatar_bytes = file.read()
        else:
            avatar_bytes = avatar_file.read()

        # Загружаем в S3
        avatar_bytes_io = BytesIO(avatar_bytes)
        manager.upload_file(avatar_filename, avatar_bytes_io)

        # Обновляем информацию о пользователе в БД
        user.is_avatar = True  # Добавьте это поле в модель User, если его нет

        db.add(user)
        db.commit()

        return True

    except Exception as e:
        print(f"Ошибка в upload_user_avatar: {e}")
        return False
    finally:
        db.close()


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
