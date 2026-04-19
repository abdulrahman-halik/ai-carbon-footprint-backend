from datetime import datetime

from bson import ObjectId

from app.db import mongodb


class CommunityModel:
    collection = "community_posts"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def create(cls, post_data: dict):
        post_data["created_at"] = datetime.utcnow()
        result = cls.get_collection().insert_one(post_data)
        return cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def get_feed(cls, limit: int = 20):
        return list(cls.get_collection().find({}).sort("created_at", -1).limit(limit))

    @classmethod
    async def find_by_user_id(cls, user_id: str, limit: int = 20):
        return list(cls.get_collection().find({"user_id": user_id}).sort("created_at", -1).limit(limit))

    @classmethod
    async def delete(cls, post_id: str):
        if not ObjectId.is_valid(post_id):
            return False
        result = cls.get_collection().delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count > 0