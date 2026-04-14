from pymongo import MongoClient
import logging

from app.core.config import settings

client = None
db = None

def connect_to_mongo():
    global client, db
    try:
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        logging.info("Connected to MongoDB!")
    except Exception as e:
        logging.error(f"Could not connect to MongoDB: {e}")

def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("Closed MongoDB connection.")
