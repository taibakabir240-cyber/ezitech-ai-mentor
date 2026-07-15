import sys
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Path management: Taake Vercel and Local dono paths automatic set ho jayein
current_dir = os.path.dirname(os.path.abspath(__file__)) # app folder
parent_dir = os.path.dirname(current_dir) # project root folder

for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 100% Safe and Crash-proof Imports
try:
    from app.services.agent_service import process_smart_query
except ImportError:
    try:
        from services.agent_service import process_smart_query
    except ImportError as e:
        # Agar dono imports fail ho jayein (taake server crash na ho)
        print(f"CRITICAL IMPORT ERROR: {e}")
        def process_smart_query(query, user_type="student"):
            return {
                "response": f"Backend Import Error: Please check directory structure. {str(e)}",
                "metrics": {"confidence": 0, "source": "System Fallback"}
            }

app = FastAPI(title="Ezitech AI Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correct template resolution
TEMPLATE_PATH = os.path.join(current_dir, "templates", "index.html")

@app.get("/", response_class=HTMLResponse)
def render_dashboard():
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    return HTMLResponse(content=f"<h3>index.html not found</h3>", status_code=404)

@app.post("/api/v1/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        user_type = data.get("user_type", "student")
        
        ai_output = process_smart_query(query, user_type)
        
        text_reply = ""
        metrics_reply = None
        
        if isinstance(ai_output, dict):
            text_reply = ai_output.get("response", "")
            metrics_reply = ai_output.get("metrics", None)
        else:
            text_reply = str(ai_output)
            
        return JSONResponse(content={
            "success": True,
            "response": text_reply,
            "metrics": metrics_reply
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "response": f"Backend Exception: {str(e)}",
            "metrics": None
        })