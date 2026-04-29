from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jwt import JWT, jwk_from_dict
from functools import wraps
import os
import bcrypt
import database.main as db


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# JWT setup
jwt_instance = JWT()
key = jwk_from_dict({
    "k": SECRET_KEY,
    "kty": "oct"
})

# --- JWT HELPERS ---

def create_token(user_id, token_type="access"):
    now = datetime.now(timezone.utc)
    
    # Set expiration based on type
    if token_type == "access":
        expiry = now + timedelta(minutes=15)
    else:
        expiry = now + timedelta(days=7)

    payload = {
        "user_id": user_id,
        "type": token_type, # This prevents using a refresh token as an access token
        "exp": int(expiry.timestamp()),
        "iat": int(now.timestamp())
    }
    return jwt_instance.encode(payload, key, alg="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            data = jwt_instance.decode(token, key, do_time_check=True)

            if data.get("type") != "access":
                return jsonify({"error": "Invalid token type for this route"}), 401

            current_user_id = data["user_id"]
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Pass the user_id to the route function
        return f(current_user_id, *args, **kwargs)
    
    return decorated


# --- PAGE ROUTES ---

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/courses_page")
def courses_page():
    return render_template("courses.html")

@app.route("/course-details_page")
def course_details_page():
    return render_template("course-details.html")

@app.route("/recommendations_page")
def recommendations_page():
    return render_template("recommendations.html")

@app.route("/profile_page")
def profile_page():
    return render_template("profile.html")


# --- API ROUTES ---

@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"error": "No refresh token provided"}), 400

    try:
        # 1. Decode and verify signature/expiration
        decoded = jwt_instance.decode(refresh_token, key, do_time_check=True)
        
        # 2. Critical Safety Check: Ensure this is actually a REFRESH token
        if decoded.get("type") != "refresh":
            return jsonify({"error": "Invalid token type"}), 401
            
        # 3. If valid, issue a NEW Access Token
        user_id = decoded["user_id"]
        new_access_token = create_token(user_id, token_type="access")
        
        return jsonify({
            "access_token": new_access_token
        })

    except Exception:
        return jsonify({"error": "Refresh token expired or invalid. Please login again."}), 401

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = db.get_user_by_email(email)

    if not user:
        return jsonify({"error": "User not found"}), 401

    if not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({
        "user": {"id": user['id'], "username": user['username'], "email": user['email']},
        "access_token": create_token(user['id'], "access"),
        "refresh_token": create_token(user['id'], "refresh")
    })

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json()

    try:
        hashed_password = bcrypt.hashpw(data.get("password").encode(), bcrypt.gensalt()).decode()

        user_id = db.register_user_transaction(
            data.get("username"), data.get("email"), hashed_password,
            data.get("phone"), data.get("age"), data.get("major"),
            data.get("skills", [])
        )

        token = create_token(user_id)

        return jsonify({
        "user": {"id": user_id, "username": data.get("username"), "email": data.get("email")},
        "access_token": create_token(user_id, "access"),
        "refresh_token": create_token(user_id, "refresh")
        }), 201
    
    except Exception as e:
        error_msg = str(e).lower()
        if "unique" in error_msg or "already exists" in error_msg:
            return jsonify({"error": "Email or Username already registered"}), 409
        return jsonify({"error": "Registration failed"}), 400

@app.route("/api/skills", methods=["GET"])
def get_skills():
    return jsonify({"skills": db.get_all_skills()})

@app.route("/api/courses", methods=["GET"])
def get_courses():
    q = request.args.get("q")
    skill = request.args.get("skill")
    instructor = request.args.get("instructor")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "relevance")

    offset = (page - 1) * limit

    course_list = db.get_filtered_courses(q, skill, instructor, sort, limit, offset)

    return jsonify({
        "page": page,
        "limit": limit,
        "courses": course_list
    })

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    course = db.get_course_by_id(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    return jsonify({"course": course})

@app.route("/api/users/me", methods=["GET"])
@token_required
def get_my_profile(user_id):
    user_data, user_skills = db.get_user_profile_data(user_id)

    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # Protect the hashed password
    user_data.pop("password", None)

    return jsonify({"user": user_data,"skills": user_skills})

@app.route("/api/recommend", methods=["POST"])
@token_required
def api_recommend(user_id):
    try:
        user_data, user_skills = db.get_user_profile_data(user_id)
        
        if not user_skills:
            return jsonify({
                "message": "No skills found in your profile. Add skills to get better recommendations.",
                "recommendations": []
            }), 200

        recommendations = db.get_course_recommendations(user_id, user_skills)

        return jsonify({
            "status": "success",
            "user_major": user_data.get("major"),
            "recommendations": recommendations
        })

    except Exception as e:
        print(f"Recommendation Error: {str(e)}")
        return jsonify({"error": "Failed to generate recommendations"}), 500