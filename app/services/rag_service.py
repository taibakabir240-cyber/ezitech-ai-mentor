import os
import sys

# Crucial import: Hamari updated rag_service se function lekar aana
try:
    from services.rag_service import process_rag_query
except Exception:
    try:
        from app.services.rag_service import process_rag_query
    except Exception:
        # Fallback agar import bilkul hi na ho sake
        def process_rag_query(query):
            return {
                "response": "RAG Service import failed in Agent Service.",
                "match_source": "Error Fallback",
                "confidence_score": 0
            }

def process_smart_query(query: str, user_type: str = "student"):
    """
    Main Agent Router:
    User ki query leta hai, use RAG service se process karwata hai,
    aur response ko proper clean format aur metrics ke sath return karta hai.
    """
    if not query.strip():
        return {
            "response": "Please enter a valid query.",
            "metrics": {
                "confidence": 100,
                "source": "Local Input Validator"
            }
        }
    
    # RAG service se response generate karwana
    rag_result = process_rag_query(query)
    
    # Frontend/API format ke mutabiq metadata structure karna
    response_text = rag_result.get("response", "No response generated.")
    match_source = rag_result.get("match_source", "Unknown Source")
    confidence_score = rag_result.get("confidence_score", 50)
    
    return {
        "response": response_text,
        "metrics": {
            "confidence": confidence_score,
            "source": match_source
        }
    }