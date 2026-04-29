# ai_service.py
import numpy as np

class AIService:
    def __init__(self, model_name="simple-local"):
        self.model_name = model_name
        # This is where we will eventually load a real model
        print(f"AI Service initialized with model: {self.model_name}")

    def generate_embedding(self, text):
        """
        Converts text into a list of numbers.
        For now, we will generate a 'dummy' vector so you can build your table.
        """
        if not text:
            return None
        
        # In the future, this will use a real AI model.
        # For learning, we'll generate 128 random numbers to represent the 'meaning'.
        # Real models usually produce 384, 768, or 1536 numbers.
        dummy_vector = np.random.uniform(-1, 1, 128).tolist()
        
        return dummy_vector

    def calculate_similarity(self, vector_a, vector_b):
        """
        Calculates how close two vectors are (Cosine Similarity).
        1.0 means identical, 0.0 means completely different.
        """
        a = np.array(vector_a)
        b = np.array(vector_b)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        return dot_product / (norm_a * norm_b)
    
    # ai_service.py (Add this method)
    def generate_user_vector(self, skills):
        """
        Skills is a list of dicts like: [{'name': 'Python', 'proficiency_level': 'beginner'}]
        We turn this list into one combined string and then into a vector.
        """
        if not skills:
            return None
    
        # Combine skills into a single string to represent the user's "knowledge profile"
        skill_text = " ".join([f"{s['name']} {s['proficiency_level']}" for s in skills])
    
        # Use the same logic as course embeddings
        return self.generate_embedding(skill_text)