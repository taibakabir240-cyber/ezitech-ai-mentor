import os
import google.generativeai as genai
from dotenv import load_dotenv

# Environment variables load karein (.env file se API key lene ke liye)
load_dotenv()

# Gemini API Key configure karein
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: Gemini API Key not found! Please check your .env file or Vercel dashboard.")

# --- DYNAMIC AND SAFE PATH RESOLUTION ---
# Dynamic path extraction taake local machine aur Vercel dono par path automatic build ho
current_file_path = os.path.abspath(__file__) # app/services/agent_service.py
services_dir = os.path.dirname(current_file_path) # app/services
app_dir = os.path.dirname(services_dir) # app
BASE_DIR = os.path.dirname(app_dir) # Project Root (C:/ezitech_project)

# Dono potential locations ko check karega
DATA_PATH_1 = os.path.join(app_dir, "data", "ezitech_data.txt")
DATA_PATH_2 = os.path.join(BASE_DIR, "data", "ezitech_data.txt")

def fetch_knowledge_base():
    """Ezitech rules aur FAQ data read karne ke liye safe file reader"""
    try:
        if os.path.exists(DATA_PATH_1):
            with open(DATA_PATH_1, "r", encoding="utf-8") as file:
                return file.read()
        elif os.path.exists(DATA_PATH_2):
            with open(DATA_PATH_2, "r", encoding="utf-8") as file:
                return file.read()
        print("WARNING: ezitech_data.txt not found in configured data directories.")
        return ""
    except Exception as e:
        print(f"Error reading knowledge base: {str(e)}")
        return ""

def process_smart_query(query: str, user_type: str = "student"):
    """
    Real RAG Logic compatible with App Dashboard schema.
    """
    query_lower = query.lower().strip().replace("'", "").replace('"', "")
    
    if not query_lower:
        return {
            "response": "System Context Exception: Empty token string passed.",
            "metrics": {"confidence": 0, "source": "Parser Exception"}
        }

    # 1. Simple Keyword Search (RAG Retrieval Step)
    knowledge_base_content = fetch_knowledge_base()
    relevant_context = []
    
    if knowledge_base_content:
        lines = knowledge_base_content.split('\n')
        keywords = query_lower.split()
        for line in lines:
            if any(kw in line.lower() for kw in keywords if len(kw) > 3):
                relevant_context.append(line)
    
    context_str = "\n".join(relevant_context[:10]) # Top 10 matching lines as context
    
    # 2. Match Source aur Confidence determine karein
    if context_str:
        match_source = "Local FAQ RAG Index"
        confidence_score = 95
        prompt_context = f"You are an AI Mentor Assistant for Ezitech. Use the following official context to answer the student's query accurately:\n\n{context_str}"
    else:
        match_source = "Fallback Generative Logic"
        confidence_score = 80
        prompt_context = "You are an AI Mentor Assistant for Ezitech. Since this query is outside local documentation, provide a professional, helpful guidance answer."

    # 3. Gemini AI Response Generation
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = f"""
        {prompt_context}
        
        User Query: {query}
        
        Instructions:
        - If answering a technical question (like Docker, FastAPI), explain clearly with basic steps.
        - If answering internship policies, be precise.
        - Keep the tone highly professional, encouraging, and clear.
        - Write the response in the same language as the query (English or Roman Urdu).
        
        Answer:
        """
        
        response = model.generate_content(full_prompt)
        response_text = response.text
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        response_text = f"I parsed your query '{query}' but encountered an issue connecting to the AI. Error: {str(e)}"
        match_source = "Offline Parser Fallback"
        confidence_score = 50

    # Frontend expectations ke mutabiq split dictionary structure return karein
    return {
        "response": response_text,
        "metrics": {
            "confidence": confidence_score,
            "source": match_source
        }
    }

def get_rag_retriever():
    return None