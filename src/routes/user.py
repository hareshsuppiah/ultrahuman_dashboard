from flask import Blueprint, request, jsonify
from src.models.user import User, db

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("api_key") or not data.get("access_code"):
        return jsonify({"error": "Missing required fields (email, api_key, access_code)"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User with this email already exists"}), 409

    new_user = User(
        email=data["email"],
        api_key=data["api_key"],
        access_code=data["access_code"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize())

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    # Check for email uniqueness if email is being updated
    new_email = data.get("email")
    if new_email and new_email != user.email and User.query.filter_by(email=new_email).first():
        return jsonify({"error": "Another user with this email already exists"}), 409

    user.email = data.get("email", user.email)
    user.api_key = data.get("api_key", user.api_key)
    user.access_code = data.get("access_code", user.access_code)

    db.session.commit()
    return jsonify(user.serialize())

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})

