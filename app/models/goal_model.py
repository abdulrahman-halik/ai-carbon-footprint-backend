from app.db import mongodb
from bson import ObjectId
from datetime import datetime

class GoalModel:
    collection = "goals"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def create(cls, goal_data: dict):
        goal_data["created_at"] = datetime.utcnow()
        result = cls.get_collection().insert_one(goal_data)
        return cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def find_by_user_id(cls, user_id: str):
        return list(cls.get_collection().find({"user_id": user_id}))

    @classmethod
    async def update(cls, goal_id: str, update_data: dict):
        if not ObjectId.is_valid(goal_id):
            return None
        update_data["updated_at"] = datetime.utcnow()
        result = cls.get_collection().update_one(
            {"_id": ObjectId(goal_id)}, {"$set": update_data}
        )
        return cls.get_collection().find_one({"_id": ObjectId(goal_id)})

    @classmethod
    async def find_active_by_user_id(cls, user_id: str):
        return cls.get_collection().find_one({"user_id": user_id, "is_active": True})
