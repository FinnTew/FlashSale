from service.product_service import ProductService
from flask import Blueprint, request, jsonify
from cerberus import Validator
from util.jwt_redis import JWTRedis

from util.response_util import ResponseUtil

class ProductController:
    def __init__(self):
        self.product_service = ProductService()
        self.product_bp = Blueprint('product_controller', __name__)
        self.setup_routes()

    def setup_routes(self):
        pass

