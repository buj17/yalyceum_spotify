from db.managers.user_manager import UserManager
from db.models import User

manager = UserManager()
user = manager.get_user_by_username('user')
manager.delete_user(user)


