from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.db import mongodb
from app.models.user_model import UserModel
from app.models.emission_model import EmissionModel
from app.models.water_model import WaterModel
from app.models.energy_model import EnergyModel
from app.models.goal_model import GoalModel


def _serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc_copy = dict(doc)
    if "_id" in doc_copy:
        doc_copy["id"] = str(doc_copy["_id"])
        doc_copy["_id"] = str(doc_copy["_id"])
    if "password" in doc_copy:
        del doc_copy["password"]
    if "otp_code" in doc_copy:
        del doc_copy["otp_code"]
    if "reset_token" in doc_copy:
        del doc_copy["reset_token"]
    return doc_copy


async def get_all_regular_users() -> List[Dict[str, Any]]:
    """Fetch all users whose role is 'user' (excluding admins) with quick emission summaries."""
    db = mongodb.db
    users = await UserModel.find_regular_users()
    serialized_users = []

    for u in users:
        u_dict = _serialize_doc(u)
        user_id_str = u_dict["id"]

        # Fetch records count
        records_count = await db["emissions"].count_documents({"user_id": user_id_str})
        u_dict["records_count"] = records_count

        # Fetch total emissions from the latest 'emissions_dashboard' record (source of truth)
        latest_dashboard = await db["emissions"].find_one(
            {"user_id": user_id_str, "sub_category": "emissions_dashboard"},
            sort=[("date", -1)]
        )
        u_dict["total_emissions"] = round(latest_dashboard.get("value", 0.0), 2) if latest_dashboard else 0.0

        serialized_users.append(u_dict)

    return serialized_users


async def get_user_summary(user_id: str) -> Dict[str, Any]:
    """Retrieve an individual user's carbon emission usage summary and activity."""
    if not ObjectId.is_valid(user_id):
        return None

    db = mongodb.db
    user = await UserModel.find_by_id(user_id)
    if not user:
        return None

    user_info = _serialize_doc(user)

    # 1. Total and categorical emissions
    cat_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$category", "total": {"$sum": "$value"}, "count": {"$sum": 1}}},
        {"$sort": {"total": -1}},
    ]
    cat_results = await db["emissions"].aggregate(cat_pipeline).to_list(length=None)

    # Fetch total emissions from the latest 'emissions_dashboard' record
    latest_dashboard = await db["emissions"].find_one(
        {"user_id": user_id, "sub_category": "emissions_dashboard"},
        sort=[("date", -1)]
    )
    total_emissions = latest_dashboard.get("value", 0.0) if latest_dashboard else 0.0

    category_breakdown = {
        item["_id"] or "Uncategorized": round(item["total"], 2) for item in cat_results
    }

    # 2. Recent emission logs
    recent_cursor = db["emissions"].find({"user_id": user_id}).sort("date", -1).limit(10)
    recent_logs = []
    async for doc in recent_cursor:
        recent_logs.append(_serialize_doc(doc))

    # 3. Water and Energy totals
    water_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$value"}}},
    ]
    water_res = await db["water_logs"].aggregate(water_pipeline).to_list(length=1)
    total_water = round(water_res[0]["total"], 2) if water_res else 0.0

    energy_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$value"}}},
    ]
    energy_res = await db["energy_logs"].aggregate(energy_pipeline).to_list(length=1)
    total_energy = round(energy_res[0]["total"], 2) if energy_res else 0.0

    # 4. User goals
    goals_cursor = db["goals"].find({"user_id": user_id}).limit(5)
    goals = []
    async for g in goals_cursor:
        goals.append(_serialize_doc(g))

    return {
        "user": user_info,
        "total_emissions": round(total_emissions, 2),
        "total_records": len(recent_logs),
        "category_breakdown": category_breakdown,
        "recent_logs": recent_logs,
        "total_water": total_water,
        "total_energy": total_energy,
        "goals": goals,
    }


async def set_user_status(user_id: str, is_active: bool) -> Dict[str, Any]:
    """Toggle a user's active/deactivated status."""
    if not ObjectId.is_valid(user_id):
        return None
    updated = await UserModel.set_active_status(user_id, is_active)
    if not updated:
        return None
    return _serialize_doc(updated)


async def get_emissions_analytics() -> Dict[str, Any]:
    """Aggregate carbon footprint metrics across all users for comparison charts."""
    db = mongodb.db

    # Resolve user details first
    user_map = {}
    users = await UserModel.find_regular_users()
    for u in users:
        u_id = str(u["_id"])
        user_map[u_id] = {
            "name": u.get("full_name", "Unknown User"),
            "email": u.get("email", ""),
            "is_active": u.get("is_active", True),
        }
        
    valid_user_ids = list(user_map.keys())

    # Fetch all latest dashboard emissions for valid users
    pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}, "sub_category": "emissions_dashboard"}},
        {"$sort": {"date": -1}},
        {"$group": {
            "_id": "$user_id",
            "latest_emission": {"$first": "$value"}
        }}
    ]
    user_footprints = await db["emissions"].aggregate(pipeline).to_list(length=None)
    footprint_map = {item["_id"]: item["latest_emission"] for item in user_footprints}
    
    # Fetch records count
    count_pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}}},
        {"$group": {"_id": "$user_id", "records_count": {"$sum": 1}}}
    ]
    user_counts = await db["emissions"].aggregate(count_pipeline).to_list(length=None)
    count_map = {item["_id"]: item["records_count"] for item in user_counts}

    user_comparison = []
    total_platform_emissions = 0.0

    for u_id in valid_user_ids:
        total_val = round(footprint_map.get(u_id, 0.0), 2)
        records_count = count_map.get(u_id, 0)
        total_platform_emissions += total_val
        details = user_map[u_id]
        
        user_comparison.append(
            {
                "user_id": u_id,
                "name": details["name"],
                "email": details["email"],
                "is_active": details["is_active"],
                "total_emissions": total_val,
                "records_count": records_count,
            }
        )
    user_comparison.sort(key=lambda x: x["total_emissions"], reverse=True)

    # Categories breakdown
    cat_pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}}},
        {"$group": {"_id": "$category", "total": {"$sum": "$value"}}},
        {"$sort": {"total": -1}},
    ]
    categories = await db["emissions"].aggregate(cat_pipeline).to_list(length=None)
    category_data = [
        {"category": c["_id"] or "Uncategorized", "total": round(c["total"], 2)}
        for c in categories
    ]

    return {
        "platform_total_emissions": round(total_platform_emissions, 2),
        "total_users_tracked": len(user_comparison),
        "highest_emitters": user_comparison[:5],
        "lowest_emitters": sorted(user_comparison, key=lambda x: x["total_emissions"])[:5],
        "all_users_comparison": user_comparison,
        "category_distribution": category_data,
    }


async def get_water_analytics() -> Dict[str, Any]:
    """Aggregate water usage metrics across all users for charts."""
    db = mongodb.db
    
    users = await UserModel.find_regular_users()
    user_map = {str(u["_id"]): u.get("full_name", "Unknown User") for u in users}
    valid_user_ids = list(user_map.keys())

    pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}}},
        {
            "$group": {
                "_id": "$user_id",
                "total_water": {"$sum": "$value"},
                "logs_count": {"$sum": 1},
            }
        },
        {"$sort": {"total_water": -1}},
    ]
    water_agg = await db["water_logs"].aggregate(pipeline).to_list(length=None)

    comparison = []
    platform_total = 0.0
    for item in water_agg:
        u_id = item["_id"]
        tot = round(item.get("total_water", 0.0), 2)
        platform_total += tot
        comparison.append(
            {
                "user_id": u_id,
                "name": user_map[u_id],
                "total_water": tot,
                "unit": "L",
                "logs_count": item.get("logs_count", 0),
            }
        )

    return {
        "platform_total_water": round(platform_total, 2),
        "unit": "L",
        "highest_consumers": comparison[:5],
        "all_users_comparison": comparison,
    }


async def get_energy_analytics() -> Dict[str, Any]:
    """Aggregate energy / electricity metrics across all users for charts."""
    db = mongodb.db
    
    users = await UserModel.find_regular_users()
    user_map = {str(u["_id"]): u.get("full_name", "Unknown User") for u in users}
    valid_user_ids = list(user_map.keys())

    pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}}},
        {
            "$group": {
                "_id": "$user_id",
                "total_energy": {"$sum": "$value"},
                "logs_count": {"$sum": 1},
            }
        },
        {"$sort": {"total_energy": -1}},
    ]
    energy_agg = await db["energy_logs"].aggregate(pipeline).to_list(length=None)

    comparison = []
    platform_total = 0.0
    for item in energy_agg:
        u_id = item["_id"]
        tot = round(item.get("total_energy", 0.0), 2)
        platform_total += tot
        comparison.append(
            {
                "user_id": u_id,
                "name": user_map[u_id],
                "total_energy": tot,
                "unit": "kWh",
                "logs_count": item.get("logs_count", 0),
            }
        )

    # Energy by type breakdown
    type_pipeline = [
        {"$match": {"user_id": {"$in": valid_user_ids}}},
        {"$group": {"_id": "$energy_type", "total": {"$sum": "$value"}}},
        {"$sort": {"total": -1}},
    ]
    by_type = await db["energy_logs"].aggregate(type_pipeline).to_list(length=None)
    type_distribution = [
        {"type": t["_id"] or "Electricity", "total": round(t["total"], 2)} for t in by_type
    ]

    return {
        "platform_total_energy": round(platform_total, 2),
        "unit": "kWh",
        "highest_consumers": comparison[:5],
        "all_users_comparison": comparison,
        "energy_type_distribution": type_distribution,
    }


async def get_goals_analytics() -> Dict[str, Any]:
    """Aggregate active goals and reducing goals performance across users."""
    db = mongodb.db
    users = await UserModel.find_regular_users()
    valid_user_ids = [str(u["_id"]) for u in users]
    user_map = {str(u["_id"]): u.get("full_name", "User") for u in users}

    goals_cursor = db["goals"].find({"user_id": {"$in": valid_user_ids}})
    all_goals = []
    async for g in goals_cursor:
        all_goals.append(_serialize_doc(g))

    active_goals = []
    reducing_goals = []
    user_scores = {}

    for g in all_goals:
        u_id = g.get("user_id")
        user_name = user_map.get(u_id, "User")
        g["user_name"] = user_name

        target = float(g.get("target_value", 0.0))
        current = float(g.get("current_value", 0.0))
        pct = 0.0
        if target > 0:
            pct = min(round((current / target) * 100, 1), 100.0)
        g["percentage"] = pct

        if g.get("is_active", True):
            active_goals.append(g)

        # Reducing goals: targeted emission reduction or category reduction
        reduction_achieved = max(0.0, target - current) if current <= target else 0.0
        g["reduction_achieved"] = round(reduction_achieved, 2)
        reducing_goals.append(g)

        # Score per user
        if u_id not in user_scores:
            user_scores[u_id] = {
                "user_id": u_id,
                "name": user_name,
                "goals_count": 0,
                "avg_completion": 0.0,
                "total_pct": 0.0,
            }
        user_scores[u_id]["goals_count"] += 1
        user_scores[u_id]["total_pct"] += pct

    # Calculate average completion score for leaderboard
    leaderboard = []
    for u_id, data in user_scores.items():
        if data["goals_count"] > 0:
            avg = round(data["total_pct"] / data["goals_count"], 1)
            leaderboard.append({
                "user_id": u_id,
                "name": data["name"],
                "goals_count": data["goals_count"],
                "score": avg,
            })
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    return {
        "total_goals": len(all_goals),
        "total_active_goals": len(active_goals),
        "active_goals": active_goals,
        "reducing_goals": reducing_goals,
        "top_scorers": leaderboard,
    }
