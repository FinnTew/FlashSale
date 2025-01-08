from service.user_service import UserService
from flask import Blueprint, request, jsonify
from cerberus import Validator

from util.response_util import ResponseUtil


class UserController:
    def __init__(self):
        self.user_service = UserService()
        self.user_bp = Blueprint('user_controller', __name__)
        self.setup_routes()


    def setup_routes(self):
        self.user_bp.add_url_rule('/register', 'register', self.register, methods=['POST'])
        self.user_bp.add_url_rule('/login', 'login', self.login, methods=['POST'])

    def register(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 8, 'required': True},
            'password': {'type': 'string', 'minlength': 8, 'required': True},
            'email': {'type': 'string', 'minlength': 4, 'required': True}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.user_service.get_user_by_user_id(json_data['username']):
            return ResponseUtil.error(message='Username already exists')
        if self.user_service.get_user_by_email(json_data['email']):
            return ResponseUtil.error(message='Email already exists')

        if self.user_service.register(json_data['username'], json_data['password'], json_data['email']):
            return ResponseUtil.success(message='User reg success')

        return ResponseUtil.error(message='User reg failed: unknown error')

    def login(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 8, 'required': True},
            'password': {'type': 'string', 'minlength': 8, 'required': True}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.user_service.get_user_by_username(json_data['username']):
            return ResponseUtil.error(message='Username does not exist')

        if self.user_service.login(json_data['username'], json_data['password']):
            # TODO: generate jwt token.
            return ResponseUtil.success(
                message='Login success',
                data=None
            )

        return ResponseUtil.error(message='Login failed: invalid password')

    def reset_password(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 8, 'required': True},
            'old_password': {'type': 'string', 'minlength': 8, 'required': True},
            'new_password': {'type': 'string', 'minlength': 8, 'required': True}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.user_service.get_user_by_username(json_data['username']):
            return ResponseUtil.error(message='Username does not exist')

        if self.user_service.update_password(json_data['username'], json_data['old_password'], json_data['new_password']):
            return ResponseUtil.success(message='Password updated')

        return ResponseUtil.error(message='Password update failed: unknown error')

    def reset_email(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 8, 'required': True},
            'old_email': {'type': 'string', 'minlength': 4, 'required': True},
            'new_email': {'type': 'string', 'minlength': 4, 'required': True}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.user_service.get_user_by_username(json_data['username']):
            return ResponseUtil.error(message='Username does not exist')

        # TODO: check old email.

        if self.user_service.update_email(json_data['username'], json_data['new_email']):
            return ResponseUtil.success(message='Email updated')

        return ResponseUtil.error(message='Email update failed: unknown error')