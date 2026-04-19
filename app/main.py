from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, onboarding, goals, emissions, energy, water, dashboard, ml, insights, community, reports
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.logger import configure_logging, get_logger

# Initialise logging as early as possible so every module inherits the config
configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s …", settings.PROJECT_NAME)
    connect_to_mongo()
    yield
    logger.info("Shutting down %s …", settings.PROJECT_NAME)
    close_mongo_connection()

app = FastAPI(
    title="Sustainability Tracking Platform API",
    lifespan=lifespan
)

# CORS – origins loaded from settings so they can be overridden via environment variable
_allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,   # Required for HTTP-only refresh-token cookie
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

@app.get("/")
async def root():
    return {"message": "Welcome to the Sustainability Tracking Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
