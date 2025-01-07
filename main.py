from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return 'FlashSale'

@app.get('/ping')
def ping():
    print("success")
    return 'pong'

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()