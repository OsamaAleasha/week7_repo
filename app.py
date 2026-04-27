from flask import Flask, render_template, request, redirect, url_for, jsonify
from database.main import *
from dotenv import load_dotenv
from sqlalchemy import select, asc, desc, or_
import os
import bcrypt
import datetime
from jwt import JWT, jwk_from_dict
from functools import wraps

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

# JWT HELPER FUNCTIONS
def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp())
    }
    return jwt_instance.encode(payload, key, alg="HS256")

def decode_token(token):
    try:
        data = jwt_instance.decode(token, key, do_time_check=True)
        return data["user_id"]
    except Exception:
        return None

def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return decode_token(token)




# PAGE ROUTES (Serve HTML)
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




# API ROUTES (Handle Data & Auth)
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    with engine.begin() as conn:
        user = get_user_by_email(conn, email)

    if not user:
        return jsonify({"error": "User not found"}), 401

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({"error": "Invalid password"}), 401

    token = create_token(user.id)

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "token": token
    })

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    age = data.get("age")
    major = data.get("major")
    # Change 1: Ensure we use this name consistently
    skills_input = data.get("skills", []) 

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    try:
        with engine.begin() as conn:
            user_id = create_user(
                conn,
                username,
                email,
                hashed_password,
                phone,
                age,
                major
            )

            # Change 2: Loop over 'skills_input' instead of 'skills'
            skills_formatted = [
                {
                    "id": int(s["id"]), 
                    "level": s["level"]
                }
                for s in skills_input 
            ]

            # Change 3: Move this inside the 'with' block so 'conn' is still active
            add_user_skills(conn, user_id, skills_formatted)

    except IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 409
    except Exception as e:
        # This will now catch the specific error if add_user_skills fails
        return jsonify({"error": str(e)}), 500

    token = create_token(user_id)
    return jsonify({
        "user": {"id": user_id, "username": username, "email": email},
        "token": token
    })

@app.route("/api/skills", methods=["GET"])
def get_skills():
    with engine.begin() as conn:
        result = conn.execute(select(skills)).mappings().all()

        return jsonify({
            "skills": [dict(row) for row in result]
        })

@app.route("/api/courses", methods=["GET"])
def get_courses():
    q = request.args.get("q")
    skill = request.args.get("skill")
    instructor = request.args.get("instructor")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "relevance")

    offset = (page - 1) * limit

    with engine.begin() as conn:
        query = select(courses)

        # Search by keyword (Title or Description)
        if q:
            query = query.where(
                or_(
                    courses.c.title.ilike(f"%{q}%"),
                    courses.c.description.ilike(f"%{q}%")
                )
            )

        # NEW: Filter by skill (checks the skill_requirements column)
        if skill and skill != "All Skills":
            query = query.where(
                courses.c.skill_requirements.ilike(f"%{skill}%")
            )

        # Filter by instructor
        if instructor:
            query = query.where(
                courses.c.instructor.ilike(f"%{instructor}%")
            )

        # Sorting
        if sort == "title":
            query = query.order_by(asc(courses.c.title))
        else:
            query = query.order_by(desc(courses.c.id))  # default "relevance-like"

        # Pagination
        query = query.limit(limit).offset(offset)

        result = conn.execute(query).mappings().all()

        return jsonify({
        "page": page,
        "limit": limit,
        "courses": [dict(row) for row in result]
    })

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    with engine.begin() as conn:
        query = select(courses).where(courses.c.id == course_id)

        result = conn.execute(query).mappings().first()

        if not result:
            return jsonify({"error": "Course not found"}), 404

        return jsonify({
            "course": dict(result)
        })
    
@app.route("/api/users/me", methods=["GET"])
def get_my_profile():
    user_id = get_current_user()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    with engine.begin() as conn:

        # Get user
        user_query = select(users).where(users.c.id == user_id)
        user = conn.execute(user_query).mappings().first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get user skills (JOIN table)
        skills_query = (
            select(skills.c.id, skills.c.name, user_skills.c.proficiency_level)
            .select_from(user_skills.join(skills))
            .where(user_skills.c.user_id == user_id)
        )

        skills_result = conn.execute(skills_query).mappings().all()

        return jsonify({
            "user": dict(user),
            "skills": [dict(s) for s in skills_result]
        })