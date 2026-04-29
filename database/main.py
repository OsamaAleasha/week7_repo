from database.db import engine
from database.models import metadata, users, skills, user_skills, courses, course_vectors
from sqlalchemy import insert, select, or_, asc, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import datetime

metadata.create_all(engine)


# User Functions

def create_user(conn, username, email, password, phone, age, major):
    now = datetime.datetime.now(datetime.timezone.utc)

    query = insert(users).values(
        username=username, email=email, password=password,
        phone=phone, age=age, major=major,
        created_at=now, updated_at=now
    )

    result = conn.execute(query)
    return result.inserted_primary_key[0]

def register_user_transaction(username, email, password, phone, age, major, skills_list):
    try:
        with engine.begin() as conn:
            user_id = create_user(conn, username, email, password, phone, age, major)

            # Format skills for the add_user_skills function
            skills_formatted = [
                {"id": int(s["id"]), "level": s["level"]}
                for s in skills_list
            ]

            add_user_skills(conn, user_id, skills_formatted)
            return user_id
        
    except Exception as e:
        raise e

def get_user_by_email(email):
    with engine.begin() as conn:
        query = select(users).where(users.c.email == email)
        result = conn.execute(query).mappings().first()
        return dict(result) if result else None

def get_user_profile_data(user_id):
    with engine.begin() as conn:
        user = conn.execute(select(users).where(users.c.id == user_id)).mappings().first()

        if not user:
            return None, None
        
        skills_query = (
            select(skills.c.id, skills.c.name, user_skills.c.proficiency_level)
            .select_from(user_skills.join(skills))
            .where(user_skills.c.user_id == user_id)
        )

        user_skills_list = conn.execute(skills_query).mappings().all()
        return dict(user), [dict(s) for s in user_skills_list]


# Skill Functions

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

def get_all_skills():
    with engine.begin() as conn:
        result = conn.execute(select(skills)).mappings().all()
        return [dict(row) for row in result]


# Course Functions

def get_course_by_id(course_id):
    with engine.begin() as conn:
        query = select(courses).where(courses.c.id == course_id)
        result = conn.execute(query).mappings().first()
        return dict(result) if result else None
    
def get_filtered_courses(q=None, skill=None, instructor=None, sort="relevance", limit=10, offset=0):
    with engine.begin() as conn:
        query = select(courses)

        if q:
            query = query.where(or_(courses.c.title.ilike(f"%{q}%"), courses.c.description.ilike(f"%{q}%")))

        if skill and skill != "All Skills":
            query = query.where(courses.c.skill_requirements.ilike(f"%{skill}%"))

        if instructor:
            query = query.where(courses.c.instructor.ilike(f"%{instructor}%"))

        # Sorting logic
        if sort == "title":
            query = query.order_by(asc(courses.c.title))
        else:
            query = query.order_by(desc(courses.c.id))

        result = conn.execute(query.limit(limit).offset(offset)).mappings().all()
        return [dict(row) for row in result]