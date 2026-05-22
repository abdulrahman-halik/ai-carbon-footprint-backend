from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.core.config import settings

client: AsyncIOMotorClient = None
db = None


def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        logging.info("Connected to MongoDB (motor async)!")
    except Exception as e:
        logging.error(f"Could not connect to MongoDB: {e}")


def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("Closed MongoDB connection.")
