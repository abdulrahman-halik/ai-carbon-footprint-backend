from app.db import mongodb
from bson import ObjectId


class UserModel:
    collection = "users"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def find_by_email(cls, email: str):
        return await cls.get_collection().find_one({"email": email})

    @classmethod
    async def create(cls, user_data: dict):
        result = await cls.get_collection().insert_one(user_data)
        return await cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def find_by_id(cls, user_id: str):
        if not ObjectId.is_valid(user_id):
            return None
        return await cls.get_collection().find_one({"_id": ObjectId(user_id)})

    @classmethod
    async def update(cls, user_id: str, update_data: dict):
        if not ObjectId.is_valid(user_id):
            return None
        await cls.get_collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return await cls.get_collection().find_one({"_id": ObjectId(user_id)})

    @classmethod
    async def find_all_by_role(cls, role: str = "user"):
        cursor = cls.get_collection().find({"role": role}).sort("created_at", -1)
        return await cursor.to_list(length=None)

    @classmethod
    async def find_regular_users(cls):
        cursor = cls.get_collection().find({"role": {"$ne": "admin"}}).sort("created_at", -1)
        return await cursor.to_list(length=None)

    @classmethod
    async def set_active_status(cls, user_id: str, is_active: bool):
        if not ObjectId.is_valid(user_id):
            return None
        await cls.get_collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"is_active": is_active}}
        )
        return await cls.get_collection().find_one({"_id": ObjectId(user_id)})

    @classmethod
    async def delete(cls, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = await cls.get_collection().delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
