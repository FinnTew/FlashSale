from itertools import product

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
        self.product_bp.add_url_rule('/update', 'product_update', self.update_product, methods=['POST'])
        self.product_bp.add_url_rule('/delete', 'product_delete', self.delete_product, methods=['POST'])
        self.product_bp.add_url_rule('/list', 'product_list', self.list_product, methods=['GET'])
        self.product_bp.add_url_rule('/incr_stock', 'product_incr_stock', self.incr_stock, methods=['POST'])
        self.product_bp.add_url_rule('/decr_stock', 'product_decr_stock', self.decr_stock, methods=['POST'])

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

    def update_product(self):
        json_data = request.get_json()

        v = Validator({
            'id': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
            'name': {'type': 'string', 'minlength': 1, 'required': False},
            'description': {'type': 'string', 'minlength': 0, 'required': False},
            'price': {'type': 'float', 'min': 0.0, 'required': True, 'empty': False, 'coerce': float},
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        product = self.product_service.get_product_by_id(json_data['id'])
        if product is None:
            return ResponseUtil.error(message=f'Product {json_data["id"]} does not exist')

        update_success = self.product_service.update_product(
            product_id=product.product_id,
            name=json_data['name'] if 'name' in json_data else product.name,
            description=json_data['description'] if 'description' in json_data else product.description,
            price=json_data['price'] if 'price' in json_data else product.price,
        )
        if not update_success:
            return ResponseUtil.error(message=f'Update product {json_data["id"]} failed')

        return ResponseUtil.success(message='Update product success')

    def delete_product(self):
        json_data = request.get_json()

        v = Validator({
            'id': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        product = self.product_service.get_product_by_id(json_data['id'])
        if product is None:
            return ResponseUtil.error(message=f'Product {json_data["id"]} does not exist')

        del_success = self.product_service.delete_product(product_id=product.product_id)
        if not del_success:
            return ResponseUtil.error(message=f'Delete product {json_data["id"]} failed')

        return ResponseUtil.success(message='Delete product success')

    def list_product(self):
        product_list = self.product_service.get_all_products()
        if not product_list:
            return ResponseUtil.error(message='No products found')

        products = [
            {
                'id': product.product_id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'stock': product.stock,
                'created_at': product.created_at
            } for product in product_list
        ]
        return ResponseUtil.success(
            message='List product success',
            data={
                'products': products
            }
        )

    def incr_stock(self):
        json_data = request.get_json()

        v = Validator({
            'id': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
            'amount': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        product = self.product_service.get_product_by_id(json_data['id'])
        if product is None:
            return ResponseUtil.error(message=f'Product {json_data["id"]} does not exist')

        incr_success = self.product_service.increase_stock(
            product_id=product.product_id,
            amount=json_data['amount']
        )
        if not incr_success:
            return ResponseUtil.error(message=f'Increment stock failed')

        return ResponseUtil.success(message='Increment stock success')

    def decr_stock(self):
        json_data = request.get_json()

        v = Validator({
            'id': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
            'amount': {'type': 'integer', 'min': 1, 'required': True, 'empty': False},
        })
        if not v.validate(json_data):
            return ResponseUtil.error(message=v.errors)

        product = self.product_service.get_product_by_id(json_data['id'])
        if product is None:
            return ResponseUtil.error(message=f'Product {json_data["id"]} does not exist')

        decr_success = self.product_service.decrease_stock(
            product_id=product.product_id,
            amount=json_data['amount']
        )
        if not decr_success:
            return ResponseUtil.error(message=f'Decrement stock failed')

        return ResponseUtil.success(message='Decrement stock success')
