from app.models.community_model import CommunityPostModel
from app.models.user_model import UserModel
from app.schemas.community_schema import PostCreate, PostOut
from app.services.dashboard_service import get_dashboard_summary
from typing import List

async def create_post(user_id: str, user_name: str, post_in: PostCreate):
    post_dict = post_in.model_dump()
    post_dict["user_id"] = user_id
    post_dict["user_name"] = user_name
    
    post = await CommunityPostModel.create(post_dict)
    return PostOut.from_mongo(post)

async def get_community_feed(limit: int = 20) -> List[PostOut]:
    posts = await CommunityPostModel.get_all(limit=limit)
    return [PostOut.from_mongo(post) for post in posts]

async def get_leaderboard(limit: int = 10):
    users = await UserModel.get_collection().find({}).to_list(length=100)
    leaderboard = []
    for u in users:
        stats = await get_dashboard_summary(str(u["_id"]))
        # score is calculated as remaining budget (assuming 1000 is default budget)
        co2 = stats.get("total_emissions", 0)
        score = max(0, int(1000 - co2))
        
        name = u.get("full_name", "Anonymous")
        leaderboard.append({
            "id": str(u["_id"]),
            "name": name,
            "avatar": name[0].upper() if name else "U",
            "score": score
        })
    
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard[:limit]

async def get_peer_comparison(user_id: str):
    # Get current user stats
    user_stats = await get_dashboard_summary(user_id)
    user_emissions = user_stats.get("emissions_by_category", [])
    
    user_data = {"transport": 0, "energy": 0, "diet": 0}
    for stat in user_emissions:
        cat = stat.get("_id", "").lower()
        val = stat.get("total_value", 0)
        if cat in ["transport", "transportation"]:
            user_data["transport"] += val
        elif cat in ["energy", "home energy", "electricity"]:
            user_data["energy"] += val
        elif cat in ["diet", "food", "diet & food"]:
            user_data["diet"] += val

    # Get average from all OTHER users
    from bson import ObjectId
    try:
        user_obj_id = ObjectId(user_id)
        query = {"_id": {"$ne": user_obj_id}}
    except:
        query = {"_id": {"$ne": user_id}}
        
    users = await UserModel.get_collection().find(query).to_list(length=100)
    total_transport = 0
    total_energy = 0
    total_diet = 0
    valid_users = 0

    for u in users:
        stats = await get_dashboard_summary(str(u["_id"]))
        emissions = stats.get("emissions_by_category", [])
        if not emissions:
            continue
            
        valid_users += 1
        for stat in emissions:
            cat = stat.get("_id", "").lower()
            val = stat.get("total_value", 0)
            if cat in ["transport", "transportation"]:
                total_transport += val
            elif cat in ["energy", "home energy", "electricity"]:
                total_energy += val
            elif cat in ["diet", "food", "diet & food"]:
                total_diet += val

    actual_valid_users = valid_users
    if valid_users == 0:
        valid_users = 1 # Avoid division by zero

    peer_data = {
        "transport": round(total_transport / valid_users, 1),
        "energy": round(total_energy / valid_users, 1),
        "diet": round(total_diet / valid_users, 1)
    }

    return {
        "userStats": user_data,
        "peerStats": peer_data,
        "totalUsers": actual_valid_users
    }
