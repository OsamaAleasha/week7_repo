from sqlalchemy import insert
from database.db import engine
from database.models import courses
import json

course_data = [
    {
        "title": "Python Basics for Beginners",
        "description": "Learn Python fundamentals, variables, loops, functions, and basic problem solving.",
        "instructor": "John Smith",
        "skills": ["Python"]
    },
    {
        "title": "Advanced Python & OOP",
        "description": "Deep dive into object-oriented programming, modules, error handling, and best practices.",
        "instructor": "Sarah Johnson",
        "skills": ["Python"]
    },
    {
        "title": "Web Development with Flask",
        "description": "Build backend web applications using Flask, routing, templates, and database integration.",
        "instructor": "Ali Hassan",
        "skills": ["Python", "Flask", "SQL"]
    },
    {
        "title": "Frontend Development with React",
        "description": "Build modern UI applications using React components, hooks, and state management.",
        "instructor": "Emma Wilson",
        "skills": ["JavaScript", "React", "HTML/CSS"]
    },
    {
        "title": "Full Stack Web Development",
        "description": "End-to-end development covering frontend and backend integration with databases.",
        "instructor": "Michael Brown",
        "skills": ["Python", "Flask", "JavaScript", "React", "SQL", "HTML/CSS"]
    },
    {
        "title": "Data Analysis with Python",
        "description": "Learn data cleaning, manipulation, and analysis using Python and SQL.",
        "instructor": "David Lee",
        "skills": ["Python", "Data Analysis", "SQL"]
    },
    {
        "title": "Machine Learning Foundations",
        "description": "Introduction to ML concepts, supervised learning, and model training.",
        "instructor": "Dr. Alan Turing",
        "skills": ["Python", "Machine Learning", "Data Analysis"]
    },
    {
        "title": "Data Visualization Mastery",
        "description": "Create charts, dashboards, and insights using visualization tools.",
        "instructor": "Nora Adams",
        "skills": ["Data Visualization", "Python", "Data Analysis"]
    },
    {
        "title": "SQL for Data Engineering",
        "description": "Advanced SQL queries, joins, aggregations, and optimization.",
        "instructor": "Chris Evans",
        "skills": ["SQL", "Data Analysis"]
    },
    {
        "title": "Git & Version Control Essentials",
        "description": "Learn Git workflows, branching, commits, and collaboration.",
        "instructor": "Tony Stark",
        "skills": ["Git"]
    },
    {
        "title": "Frontend Fundamentals (HTML/CSS)",
        "description": "Build static websites with structure, styling, and responsiveness.",
        "instructor": "Lisa Ray",
        "skills": ["HTML/CSS"]
    }
]

def seed_courses():
    with engine.begin() as conn:
        for course in course_data:
            stmt = insert(courses).values(
                title=course["title"],
                description=course["description"],
                instructor=course["instructor"],
                skill_requirements=json.dumps(course["skills"])
            )
            conn.execute(stmt)

    print("✅ Courses seeded successfully!")

if __name__ == "__main__":
    seed_courses()