from multiprocessing import Process

from flask import Flask
from flask_cors import CORS

from conf.conf import conf
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
    email_verify_consumer()
    flask_app()