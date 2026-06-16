from flask import Blueprint, request, jsonify
from flask_jwt_extended import ( create_access_token, jwt_required, get_jwt_identity)
from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

#Register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    
    if not all([name, email, password]):
        return jsonify({ "message" : "Name, email and password are required"}), 400
    
    has_user = User.query.filter_by(email=email).first()

    if has_user:
        return jsonify({"message": "Email already exists"}), 400
    
    user = User(
        name=name,
        email=email,
        password=password,
        role=role
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    
    
    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401
    
    if user.is_active == False:
        return jsonify({
            "message":"User is not active"
        }), 400
    
    if user.password != password:
        return jsonify({
            "message": "Your password is incorrect"
        })
    
    access_token = create_access_token(
    identity=str(user.id),
    additional_claims={
        "name": user.name,
        "role": user.role
    }
)

    return jsonify({
        "message": "Login Successful",
        "token" : access_token,
        "user": {
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        
        
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_current_user():

    current_user = get_jwt_identity()

    return jsonify({
        "user" : current_user
    }), 200