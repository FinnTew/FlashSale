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
        self.product_bp.add_url_rule('/create', 'product_create', self.create_product, methods=['POST'])

    def create_product(self):
        json_data = request.get_json()

        v = Validator({
            'name': {'type': 'string', 'minlength': 1, 'required': True},
            'description': {'type': 'string', 'minlength': 0, 'required': False},
            'price': {'type': 'float', 'min': 0.0, 'required': True, 'empty': False, 'coerce': float},
            'stock': {'type': 'integer', 'min': 0, 'required': True, 'empty': False}
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        if self.product_service.get_product_by_name(json_data['name']) is not None:
            return ResponseUtil.error(message=f'Product {json_data["name"]} already exists')

        create_success = self.product_service.create_product(
            name=json_data['name'],
            description=json_data.get('description', ''),
            price=json_data['price'],
            stock=json_data['stock']
        )
        if not create_success:
            return ResponseUtil.error(message='Create product failed')

        return ResponseUtil.success(message='Create product success')


