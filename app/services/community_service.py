from app.models.community_model import CommunityPostModel
from app.schemas.community_schema import PostCreate, PostOut
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
