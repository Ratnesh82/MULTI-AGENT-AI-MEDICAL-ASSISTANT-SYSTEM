"""
FCMAS-W FastAPI Application Entry Point — Phase 3.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db
from routers import auth, scheduling, wellness, admin, profile

app = FastAPI(
    title="FCMAS-W API",
    description="Fairness-Constrained Multilingual Agent for Scheduling & Wellness",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scheduling.router)
app.include_router(wellness.router)
app.include_router(admin.router)
app.include_router(profile.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "FCMAS-W",
        "version": "3.0.0",
        "status": "running",
        "modules": ["Scheduling Engine", "Wellness Engine", "NLP Module",
                    "Admin Panel", "Patient Profile", "Health Score AI",
                    "Email Notifications", "Full Health Report PDF"],
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}
