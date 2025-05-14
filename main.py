from db import create_session
from db.managers import MusicManager, UserManager

if __name__ == '__main__':
    user_manager = UserManager()
    print(MusicManager(create_session()).search_music('a'))
