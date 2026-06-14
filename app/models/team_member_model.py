from app.db import mongodb
from bson import ObjectId
from datetime import datetime, timezone


class TeamMemberModel:
    collection = "team_members"

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
        cursor = cls.get_collection().find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=None)

    @classmethod
    async def find_by_id(cls, member_id: str, user_id: str):
        if not ObjectId.is_valid(member_id):
            return None
        return await cls.get_collection().find_one(
            {"_id": ObjectId(member_id), "user_id": user_id}
        )

    @classmethod
    async def update(cls, member_id: str, user_id: str, update_data: dict):
        if not ObjectId.is_valid(member_id):
            return None
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await cls.get_collection().update_one(
            {"_id": ObjectId(member_id), "user_id": user_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return None
        return await cls.get_collection().find_one({"_id": ObjectId(member_id)})

    @classmethod
    async def delete(cls, member_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(member_id):
            return False
        result = await cls.get_collection().delete_one(
            {"_id": ObjectId(member_id), "user_id": user_id}
        )
        return result.deleted_count > 0
