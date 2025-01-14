import base64
import hashlib
import re
import time
from datetime import datetime
from multiprocessing import Process

from flask import Flask
from flask_cors import CORS
from peewee import MySQLDatabase

from conf.conf import conf
from controller.product_controller import ProductController
from controller.user_controller import UserController
from util.email_verify_util import EmailVerifyUtil

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return 'FlashSale'

@app.get('/ping')
def ping():
    print("success")
    return 'pong'

def init_controller():
    app.register_blueprint(UserController().user_bp, url_prefix='/user')
    app.register_blueprint(ProductController().product_bp, url_prefix='/product')

def flask_app():
    init_controller()
    app.run(
        host=conf.flask.host,
        port=conf.flask.port,
        debug=conf.flask.debug
    )

def email_verify_consumer():
    process = Process(target=EmailVerifyUtil().email_consumer)
    process.start()

if __name__ == '__main__':
    # email_verify_consumer()
    # flask_app()
    order_str = "order:2:1:3"
    hash_obj = hashlib.sha256(order_str.encode())
    hash_hex = hash_obj.hexdigest()
    hash_base64 = (base64.urlsafe_b64encode(hash_obj.digest())
                   .decode()
                   .rstrip('='))
    order_pre = re.sub(r'[^a-zA-Z0-9]', '', hash_base64)
    now = datetime.now()
    timestamp_str = now.strftime('%Y%m%d%H%M%S') + f"{now.microsecond // 1000:03d}"
    print(f"FS{order_pre[2:10]}-{timestamp_str}")
    print(hash_base64)


