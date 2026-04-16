from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import auth, users, onboarding, goals, emissions, energy, water, dashboard
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()

app = FastAPI(
    title="Sustainability Tracking Platform API",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(emissions.router, prefix="/api/emissions", tags=["emissions"])
app.include_router(energy.router, prefix="/api/energy", tags=["energy"])
app.include_router(water.router, prefix="/api/water", tags=["water"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Sustainability Tracking Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
