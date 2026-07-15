import os

DATA_PATH = "C:/ezitech_project/data/ezitech_data.txt"

def fetch_knowledge_base():
    """Ezitech rules aur FAQ data read karne ke liye"""
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as file:
                return file.read()
        return "No knowledge base data available."
    except Exception as e:
        return f"Error reading knowledge base: {str(e)}"

def get_rag_retriever():
    """Fallback function taake agar purani dependencies kahin call ho rahi hon to code crash na ho"""
    return None