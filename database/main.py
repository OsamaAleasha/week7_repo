from database.db import engine
from database.models import metadata, users, skills, user_skills, courses, course_vectors
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import datetime

metadata.create_all(engine)

def create_user(conn, username, email, password, phone, age, major):
    now = datetime.datetime.utcnow()

    query = insert(users).values(
        username=username,
        email=email,
        password=password,
        phone=phone,
        age=age,
        major=major,
        created_at=now,
        updated_at=now
    )

    result = conn.execute(query)
    return result.inserted_primary_key[0]

def add_user_skills(conn, user_id, skills_list):
    now = datetime.datetime.utcnow()

    for skill in skills_list:
        conn.execute(
            insert(user_skills).values(
                user_id=user_id,
                skill_id=skill.get("id"),
                proficiency_level=skill.get("level", 1),  # default = beginner
                created_at=now,
                updated_at=now
            )
        )

def get_user_by_email(conn, email):
    query = select(users).where(users.c.email == email)
    result = conn.execute(query).fetchone()
    return result

def get_user_by_id(conn, user_id):
    query = select(users).where(users.c.id == user_id)
    return conn.execute(query).fetchone()

def get_user_skills(conn, user_id):
    query = (
        select(
            skills.c.id,
            skills.c.name,
            user_skills.c.proficiency_level
        )
        .join(user_skills, skills.c.id == user_skills.c.skill_id)
        .where(user_skills.c.user_id == user_id)
    )

    results = conn.execute(query).fetchall()

    return [
        {
            "id": r.id,
            "name": r.name,
            "level": r.proficiency_level
        }
        for r in results
    ]