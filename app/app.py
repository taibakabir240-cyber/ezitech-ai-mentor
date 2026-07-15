import sys
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Setup directories for reliable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for d in [current_dir, parent_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

# Try to import agent service safely
import_error = ""
try:
    from services.agent_service import process_smart_query
except Exception as e:
    try:
        from app.services.agent_service import process_smart_query
    except Exception as e2:
        import_error = f"Primary: {str(e)} | Fallback: {str(e2)}"
        def process_smart_query(query, user_type):
            return {"response": f"[Fallback Error]: {import_error}", "metrics": None}

app = FastAPI(title="Ezitech AI Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correct path pointing directly to templates/index.html
TEMPLATE_PATH = os.path.join(current_dir, "templates", "index.html")

@app.get("/", response_class=HTMLResponse)
def render_dashboard():
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    return HTMLResponse(content=f"<h3>index.html not found at {TEMPLATE_PATH}</h3>", status_code=404)

@app.post("/api/v1/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        user_type = data.get("user_type", "student")
        
        # Get raw response from our service
        ai_output = process_smart_query(query, user_type)
        
        # 100% CLEAN FORMAT GUARANTEE:
        # Hamesha frontend ko "response" key mein direct string text bhejenge
        text_reply = ""
        metrics_reply = None
        
        if isinstance(ai_output, dict):
            text_reply = ai_output.get("response", "")
            metrics_reply = ai_output.get("metrics", None)
            
            # Agar kisi wajah se 'response' key ke andar bhi dictionary phansi hui hai
            if isinstance(text_reply, dict):
                text_reply = text_reply.get("response", str(text_reply))
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