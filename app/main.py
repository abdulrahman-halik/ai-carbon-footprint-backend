from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import auth, users
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

@app.get("/")
async def root():
    return {"message": "Welcome to the Sustainability Tracking Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
