from sqlalchemy import MetaData, Table, Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime

metadata = MetaData()

users = Table (
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100), unique=True, nullable=False),
    Column("email", String(120), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("phone", String(20)),
    Column("age", Integer),
    Column("major", String(100)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

skills = Table (
    "skills",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), unique=True, nullable=False),
    Column("description", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

user_skills = Table (
    "user_skills",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE")),
    Column("proficiency_level", String(50)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

courses = Table (
    "courses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200)),
    Column("description", Text),
    Column("instructor", String(100)),
    Column("skill_requirements", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

course_vectors = Table(
    "course_vectors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE")),
    Column("embedding_vector", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
)