from db.managers import UserManager

if __name__ == '__main__':
    user_manager = UserManager()
    # user_manager.upload_avatar(1, open('static/audio/Bangu Aaku Thechi_cover.jpg', 'rb').read())
    # print(open('static/audio/Bangu Aaku Thechi_cover.jpg', 'rb').read())
    print(user_manager.get_avatar_url(1))
