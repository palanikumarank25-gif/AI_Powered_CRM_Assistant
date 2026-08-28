from pathlib import Path
from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # pyright: ignore[reportMissingImports]
from fastapi.responses import FileResponse  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel  # pyright: ignore[reportMissingImports]

from agent import run_agent


app = FastAPI(
    title="AI-Powered CRM Assistant",
    description=(
        "Small AI CRM assistant for "
        "sales and support teams."
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    message: str


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI CRM Assistant"
    }


# =========================================================
# CHAT API
# =========================================================

@app.post("/api/chat")
def chat(
    request: ChatRequest
):

    try:

        result = run_agent(
            request.message
        )

        return {
            "success": True,
            "response": result["response"]
        }

    except Exception as error:

        return {
            "success": False,
            "response": (
                "I encountered an error "
                "while processing your request."
            ),
            "error": str(error)
        }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    frontend_path = (
        Path(__file__).resolve().parent
        / "frontend"
        / "index.html"
    )

    if frontend_path.exists():

        return FileResponse(
            frontend_path
        )

    return {
        "message": (
            "AI CRM Assistant backend "
            "is running."
        )
    }