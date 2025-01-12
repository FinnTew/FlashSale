from model.user_model import Users
from util.password_util import PasswordUtil
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.user = Users()

    def register(self, username: str, password: str, email: str) -> bool:
        password_hash = PasswordUtil.hash_password(password)
        try:
            self.user.create(
                username=username,
                password_hash=password_hash,
                email=email
            )
            return True
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return False

    def login(self, username: str, password: str) -> bool:
        user = self.user.get_or_none(Users.username == username)
        if user is None:
            return False
        return PasswordUtil.check_password(password, user.password_hash)

    def get_user_by_username(self, username: str) -> Users:
        return self.user.select().where(Users.username == username).first()

    def get_user_by_user_id(self, user_id: int) -> Users:
        return self.user.select().where(Users.user_id == user_id).first()

    def get_user_by_email(self, email: str) -> Users:
        return self.user.select().where(Users.email == email).first()

    def update_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = self.get_user_by_user_id(user_id)
        if user is None:
            return False
        if not PasswordUtil.check_password(old_password, user.password_hash):
            return False

        new_password_hash = PasswordUtil.hash_password(new_password)
        try:
            self.user.update(
                password_hash=new_password_hash
            ).where(Users.user_id == user_id).execute()
            return True
        except Exception as e:
            logger.error(f"更新密码失败: {str(e)}")
            return False

    def update_email(self, user_id: int, new_email: str) -> bool:
        try:
            self.user.update(
                email=new_email
            ).where(Users.user_id == user_id).execute()
            return True
        except Exception as e:
            logger.error(f"更新邮箱失败: {str(e)}")
            return False