import os

from flask import Flask
from flask_cors import CORS
from conf.conf import conf
from controller.user_controller import UserController
from model.user_model import Users
from service.user_service import UserService

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

def flask_app():
    init_controller()
    app.run(
        host=conf.flask.host,
        port=conf.flask.port,
        debug=conf.flask.debug
    )

if __name__ == '__main__':
    flask_app()