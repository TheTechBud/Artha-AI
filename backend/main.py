import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from db.crud import get_or_create_demo_user
from db.database import SessionLocal

from api.routes import transactions, analytics, drs, interventions, narrative, ai
from api.middleware.logging import log_requests
from api.middleware.error_handler import global_error_handler
from observability.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="Artha AI",
    description="Behavioral Finance Copilot API",
    version="0.1.0",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.middleware("http")(log_requests)

# Global error handler
app.add_exception_handler(Exception, global_error_handler)

# Routers
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(drs.router)
app.include_router(interventions.router)
app.include_router(narrative.router)
app.include_router(ai.router)


@app.on_event("startup")
def startup():
    logger.info("Starting Artha AI backend…")
    init_db()
    # Ensure demo user exists
    db = SessionLocal()
    try:
        user = get_or_create_demo_user(db)
        logger.info(f"Demo user ready: {user.name} (id={user.id})")
    finally:
        db.close()
    logger.info("Backend ready.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "artha-ai"}


@app.get("/")
def root():
    return {"message": "Artha AI API — visit /docs for API explorer"}
