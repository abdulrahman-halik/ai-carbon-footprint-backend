#!/usr/bin/env python3
"""
Seed or promote an Administrator account in EcoTracker.
Usage:
    python seed_admin.py [--email admin@ecotracker.com] [--password Admin@123] [--name "System Admin"]
"""

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.security import get_password_hash


async def seed_admin(email: str, password: str, full_name: str):
    print(f"Connecting to MongoDB database '{settings.DATABASE_NAME}'...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_col = db["users"]

    existing_user = await users_col.find_one({"email": email})

    if existing_user:
        print(f"Found existing user with email '{email}'. Promoting to admin role...")
        update_data = {
            "role": "admin",
            "is_active": True,
            "onboarding_completed": True,
        }
        if password:
            update_data["password"] = get_password_hash(password)
        await users_col.update_one({"_id": existing_user["_id"]}, {"$set": update_data})
        print(f"✅ User '{email}' successfully updated to ADMIN!")
    else:
        print(f"Creating new admin user '{email}'...")
        admin_doc = {
            "full_name": full_name,
            "email": email,
            "password": get_password_hash(password),
            "role": "admin",
            "is_active": True,
            "onboarding_completed": True,
            "profile": {},
            "created_at": datetime.now(timezone.utc),
        }
        result = await users_col.insert_one(admin_doc)
        print(f"✅ New ADMIN user created successfully! (ID: {result.inserted_id})")

    client.close()


def main():
    parser = argparse.ArgumentParser(description="Seed or promote an EcoTracker Admin user")
    parser.add_argument("--email", default="admin@ecotracker.com", help="Admin email address")
    parser.add_argument("--password", default="Admin@123", help="Admin password")
    parser.add_argument("--name", default="System Administrator", help="Admin full name")
    args = parser.parse_args()

    asyncio.run(seed_admin(args.email, args.password, args.name))


if __name__ == "__main__":
    main()
