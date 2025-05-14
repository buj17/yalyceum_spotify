from db import create_session
from db.managers import MusicManager, UserManager

if __name__ == '__main__':
    user_manager = UserManager()
    musics = MusicManager(create_session()).search_music('dhooma')
    print(MusicManager(create_session()).get_music_image_url(musics[0].id))
