from app.db import mongodb
from bson import ObjectId
from datetime import datetime, timezone


class EmissionModel:
    collection = "emissions"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def create(cls, data: dict):
        data["created_at"] = datetime.now(timezone.utc)
        result = await cls.get_collection().insert_one(data)
        return await cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def find_by_user_id(cls, user_id: str):
        cursor = cls.get_collection().find({"user_id": user_id}).sort("date", -1)
        return await cursor.to_list(length=None)

    @classmethod
    async def update(cls, record_id: str, update_data: dict, user_id: str = None):
        if not ObjectId.is_valid(record_id):
            return None
        update_data["updated_at"] = datetime.now(timezone.utc)
        # If user_id is provided, scope the update to that user (ownership check)
        query = {"_id": ObjectId(record_id)}
        if user_id:
            query["user_id"] = user_id
        result = await cls.get_collection().update_one(query, {"$set": update_data})
        if result.matched_count == 0:
            return None
        return await cls.get_collection().find_one({"_id": ObjectId(record_id)})

    @classmethod
    async def delete(cls, record_id: str, user_id: str = None) -> bool:
        if not ObjectId.is_valid(record_id):
            return False
        query = {"_id": ObjectId(record_id)}
        if user_id:
            query["user_id"] = user_id
        result = await cls.get_collection().delete_one(query)
        return result.deleted_count > 0

    @classmethod
    async def get_aggregated_stats(cls, user_id: str):
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$category",
                "total_value": {"$sum": "$value"}
            }}
        ]
        return await cls.get_collection().aggregate(pipeline).to_list(length=None)

    @classmethod
    async def delete_by_user_id(cls, user_id: str):
        await cls.get_collection().delete_many({"user_id": user_id})
