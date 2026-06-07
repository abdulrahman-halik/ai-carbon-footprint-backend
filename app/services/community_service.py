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
