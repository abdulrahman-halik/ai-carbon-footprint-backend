from app.db import mongodb
from bson import ObjectId
from datetime import datetime

class CommunityPostModel:
    collection = "community_posts"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def create(cls, post_data: dict):
        post_data["timestamp"] = datetime.utcnow()
        result = cls.get_collection().insert_one(post_data)
        return cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def get_all(cls, limit: int = 20):
        posts = list(cls.get_collection().find().sort("timestamp", -1).limit(limit))
        return posts
