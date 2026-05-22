from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.logger import logger
from app.core.config import settings

client: AsyncIOMotorClient = None
db = None


def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        logger.info("Connected to MongoDB (motor async)!")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")


def close_mongo_connection():
    global client
    if client:
        client.close()
        logger.info("Closed MongoDB connection.")
