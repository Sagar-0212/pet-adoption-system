"""
Main Application Entrypoint.
FastAPI application mounting routers, static portal, CORS, health probes,
and persistent database initialization.
Author: Harshwardhan (S4_Harshwardhan)
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import pets, adoptions, admin

# Initialize persistent database tables on startup
init_db()

app = FastAPI(
    title="Pet Adoption & Management System",
    version="1.0.0",
    description="Persistent REST API for managing pet adoptions and inventory."
)

# Enable CORS for browser frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(pets.router)
app.include_router(adoptions.router)
app.include_router(admin.router)

# Mount static frontend directory safely if present
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    static_dir = "static"

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/")
def root():
    """API Root Health Check returning JSON status."""
    return {
        "status": "ok",
        "message": "Pet Adoption & Management System API is running"
    }


@app.get("/health")
def health_check():
    """Kubernetes Liveness and Readiness probe endpoint."""
    return {"status": "ok"}
from fastapi.responses import FileResponse, RedirectResponse

@app.get("/adopt", tags=["Frontend"])
def serve_adopt():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/care", tags=["Frontend"])
def serve_care():
    return FileResponse(os.path.join(static_dir, "care.html"))

@app.get("/services", tags=["Frontend"])
def serve_services():
    return FileResponse(os.path.join(static_dir, "services.html"))

@app.get("/admin-dashboard", tags=["Frontend"])
def serve_admin():
    return FileResponse(os.path.join(static_dir, "admin.html"))
