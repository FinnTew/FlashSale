from flask import jsonify

class ResponseUtil:
    @staticmethod
    def success(message="Success", data=None, status_code=200):
        response = {
            "status": "success",
            "message": message,
            "data": data
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message="Error", data=None, status_code=400):
        response = {
            "status": "error",
            "message": message,
            "data": data
        }
        return jsonify(response), status_code