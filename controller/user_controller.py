from service.user_service import UserService
from flask import Blueprint, request, jsonify
from cerberus import Validator
from util.jwt_redis import JWTRedis

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
            'username': {'type': 'string', 'minlength': 6, 'required': True},
            'password': {'type': 'string', 'minlength': 8, 'required': True},
            'email': {
                'type': 'string',
                'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'required': True
            }
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.user_service.get_user_by_username(json_data['username']):
            return ResponseUtil.error(message='Username already exists')
        if self.user_service.get_user_by_email(json_data['email']):
            return ResponseUtil.error(message='Email already exists')

        if self.user_service.register(json_data['username'], json_data['password'], json_data['email']):
            user_id = self.user_service.get_user_by_username(json_data['username']).user_id
            if user_id is None:
                return ResponseUtil.error(message='User reg failed: unknown error')

            jwt_redis = JWTRedis()
            uid = f"{user_id}_{json_data['username']}"
            token_dict = jwt_redis.generate_token(uid)
            token: str = token_dict['token']

            return ResponseUtil.success(
                message='User register success',
                data={
                    'id': user_id,
                    'token': token,
                    'username': json_data['username'],
                    'email': json_data['email']
                }
            )

        return ResponseUtil.error(message='User reg failed: unknown error')

    def login(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 6, 'required': True},
            'password': {'type': 'string', 'minlength': 8, 'required': True}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        user = self.user_service.get_user_by_username(json_data['username'])
        if user is None:
            return ResponseUtil.error(message='Username does not exist')

        if self.user_service.login(json_data['username'], json_data['password']):
            jwt_redis = JWTRedis()
            uid = f"{user.user_id}_{user.username}"
            token_dict = jwt_redis.generate_token(uid)
            token: str = token_dict['token']

            return ResponseUtil.success(
                message='Login success',
                data={
                    'id': user.user_id,
                    'token': token,
                    'username': user.username,
                    'email': user.email
                }
            )

        return ResponseUtil.error(message='Login failed: invalid password')

    def reset_password(self):
        json_data = request.get_json()

        v = Validator({
            'username': {'type': 'string', 'minlength': 6, 'required': True},
            'new_password': {'type': 'string', 'minlength': 8, 'required': True},
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        user = self.user_service.get_user_by_username(json_data['username'])
        if user is None:
            return ResponseUtil.error(message='Username does not exist')
        user_email = user.email

        # TODO: use the rabbitmq to implement email sending and verification,
        #       if verify success, then update the password

        return ResponseUtil.success(message='Password reset success')