import os

from flask import Flask, jsonify, request

from .models import UserModel

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = {"user_id": data["user_id"], "name": data["name"], "email": data["email"]}

    try:
        UserModel.create(user)
        return jsonify({"message": "User created", "user_id": data["user_id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = UserModel.get(user_id)
        return jsonify(user)
    except Exception as e:
        if str(e) == "DoesNotExist":
            return jsonify({"error": "User not found"}), 404
        return jsonify({"error": str(e)}), 500


@app.route("/users", methods=["GET"])
def list_users():
    try:
        users = UserModel.scan()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        UserModel.delete(user_id)
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
