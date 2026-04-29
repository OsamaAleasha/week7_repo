# sync_embeddings.py
from database.main import engine, courses, course_vectors # Import your DB setup
from ai_service import AIService
from sqlalchemy import select, insert
import json

ai = AIService()

def fill_course_vectors():
    with engine.begin() as conn:
        # 1. Get all courses that don't have a vector yet
        # (For now, let's just get all courses)
        all_courses = conn.execute(select(courses)).mappings().all()
        
        print(f"Found {len(all_courses)} courses. Generating embeddings...")

        for course in all_courses:
            # 2. Prepare the text for the AI
            # We combine title and description so the AI understands both
            combined_text = f"{course['title']} {course['description']}"
            
            # 3. Generate the vector (the list of numbers)
            vector = ai.generate_embedding(combined_text)
            
            # 4. Save to course_vectors table
            # Note: We convert the list to a JSON string or use the DB's array type
            query = insert(course_vectors).values(
                course_id=course['id'],
                embedding_vector=json.dumps(vector) 
            )
            conn.execute(query)
            
            print(f"✅ Generated vector for: {course['title']}")

if __name__ == "__main__":
    fill_course_vectors()