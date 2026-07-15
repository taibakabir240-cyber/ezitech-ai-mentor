import sys
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Force fresh path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Direct import without dynamic fallbacks to stop stale caching
from services.agent_service import process_smart_query

app = FastAPI(title="Ezitech AI Portal")