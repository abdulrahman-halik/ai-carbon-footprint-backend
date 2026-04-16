from app.db import mongodb
from bson import ObjectId

class UserModel:
    collection = "users"

    @classmethod
    def get_collection(cls):
        return mongodb.db[cls.collection]

    @classmethod
    async def find_by_email(cls, email: str):
        return cls.get_collection().find_one({"email": email})

    @classmethod
    async def create(cls, user_data: dict):
        result = cls.get_collection().insert_one(user_data)
        return cls.get_collection().find_one({"_id": result.inserted_id})

    @classmethod
    async def find_by_id(cls, user_id: str):
        if not ObjectId.is_valid(user_id):
            return None
        return cls.get_collection().find_one({"_id": ObjectId(user_id)})
