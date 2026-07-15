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
    print("WARNING: Gemini API Key not found! Please check your .env file.")

DATA_PATH = "C:/ezitech_project/data/ezitech_data.txt"

def fetch_knowledge_base():
    """Ezitech rules aur FAQ data read karne ke liye"""
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as file:
                return file.read()
        return ""
    except Exception as e:
        print(f"Error reading knowledge base: {str(e)}")
        return ""

def process_rag_query(query: str):
    """
    Real RAG Logic:
    1. Knowledge Base se relevant context search karega.
    2. Context aur Query ko Gemini AI ke paas bhej kar intelligent response generate karega.
    """
    knowledge_base_content = fetch_knowledge_base()
    
    # 1. Simple Keyword Search (RAG Retrieval Step)
    # Hum knowledge base ki lines mein se query ke keywords match karte hain
    relevant_context = []
    if knowledge_base_content:
        lines = knowledge_base_content.split('\n')
        keywords = query.lower().split()
        for line in lines:
            # Agar query ka koi bhi ahem word line mein match ho jaye
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

    # 3. Gemini AI se response generate karwana
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
        # API fail hone par aakhri fallback
        response_text = f"I parsed your query '{query}' but encountered an issue connecting to the AI brain. Please check database/API settings."
        match_source = "Offline Parser Fallback"
        confidence_score = 50

    return {
        "response": response_text,
        "match_source": match_source,
        "confidence_score": confidence_score
    }

def get_rag_retriever():
    """Fallback function taake crash na ho"""
    return None