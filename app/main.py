from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, onboarding, goals, emissions, energy, water, dashboard, ml, insights, community, reports, education
from app.core.exceptions import validation_exception_handler
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import app.db.mongodb as mongo_db
from app.core.config import settings
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Sustainability Tracking Platform API...")
    connect_to_mongo()
    import pymongo
    if mongo_db.db is not None:
        # Fix #17: Create critical indexes on startup
        await mongo_db.db["users"].create_index([("email", pymongo.ASCENDING)], unique=True)
        await mongo_db.db["emissions"].create_index([("user_id", pymongo.ASCENDING)])
        await mongo_db.db["energy_logs"].create_index([("user_id", pymongo.ASCENDING)])
        await mongo_db.db["water_logs"].create_index([("user_id", pymongo.ASCENDING)])
        await mongo_db.db["goals"].create_index([("user_id", pymongo.ASCENDING)])
    yield
    # Shutdown
    close_mongo_connection()

app = FastAPI(
    title="Sustainability Tracking Platform API",
    lifespan=lifespan
)

# CORS configuration is now dynamically loaded from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(emissions.router, prefix="/api/emissions", tags=["emissions"])
app.include_router(energy.router, prefix="/api/energy", tags=["energy"])
app.include_router(water.router, prefix="/api/water", tags=["water"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(community.router, prefix="/api/community", tags=["community"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(education.router, prefix="/api/education", tags=["education"])

app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def root():
    return {"message": "Welcome to the Sustainability Tracking Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")
