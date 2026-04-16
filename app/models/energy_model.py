from app.db import mongodb
from bson import ObjectId
from datetime import datetime

class EnergyModel:
    collection = "energy_logs"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def create(cls, data: dict):
        data["created_at"] = datetime.utcnow()
        result = cls.get_collection().insert_one(data)
        return cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def find_by_user_id(cls, user_id: str):
        return list(cls.get_collection().find({"user_id": user_id}).sort("date", -1))

    @classmethod
    async def update(cls, record_id: str, update_data: dict):
        if not ObjectId.is_valid(record_id):
            return None
        update_data["updated_at"] = datetime.utcnow()
        cls.get_collection().update_one(
            {"_id": ObjectId(record_id)}, {"$set": update_data}
        )
        return cls.get_collection().find_one({"_id": ObjectId(record_id)})

    @classmethod
    async def delete(cls, record_id: str):
        if not ObjectId.is_valid(record_id):
            return False
        result = cls.get_collection().delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count > 0
