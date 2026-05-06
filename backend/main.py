"""
Concordia Simulation Builder - FastAPI Backend

Main application entry point.
"""
import os
import signal
import subprocess

# Load environment variables from .env file FIRST
# This must happen before any other imports that depend on debug_print
from dotenv import load_dotenv
load_dotenv()

# Fix tokenizers parallelism warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Install stdout tee for log broadcasting to frontend
from backend.utils.stdout_tee import install_tee
install_tee()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api import simulations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting Concordia Simulation Builder API...")
    yield
    # Shutdown
    print("Shutting down Concordia Simulation Builder API...")


# Create FastAPI app
app = FastAPI(
    title="Concordia Simulation Builder",
    description="API for building and running Concordia agent-based simulations",
    version="2.4.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulations.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Concordia Simulation Builder API",
        "version": "2.4.0",
        "docs": "/docs",
        "endpoints": {
            "prefabs": "/api/simulations/prefabs",
            "providers": "/api/simulations/providers",
            "validate": "/api/simulations/validate",
            "execute": "/api/simulations/execute",
            "templates": "/api/simulations/templates/peace-negotiation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/server/shutdown")
async def shutdown_server():
    """Kill all processes on our port, then exit."""
    subprocess.Popen(
        ['sh', '-c', 'sleep 0.3 && kill -9 $(lsof -ti :8000) 2>/dev/null'],
        start_new_session=True,
    )
    return {"status": "shutting_down"}


# Serve frontend static files in production
# This will be enabled when frontend is built
# app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


# @app.get("/{catchall:path}")
# async def serve_frontend(catchall: str):
#     """Serve the frontend application."""
#     return FileResponse("frontend/dist/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
