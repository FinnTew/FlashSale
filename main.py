import os

from flask import Flask
from flask_cors import CORS
from conf.conf import conf

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return 'FlashSale'

@app.get('/ping')
def ping():
    print("success")
    return 'pong'

def flask_app():
    app.run(
        host=conf.flask.host,
        port=conf.flask.port,
        debug=conf.flask.debug
    )

if __name__ == '__main__':
    flask_app()
