from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.water_model import WaterModel
from datetime import datetime, timezone


async def get_dashboard_summary(user_id: str):
    """
    Get aggregated data for dashboard visualizations.
    Total emissions, energy, and water usage.
    """
    # Fix #11: use .get() with defaults to avoid KeyError on malformed docs
    emission_stats = await EmissionModel.get_aggregated_stats(user_id)
    total_co2 = sum(stat.get("total_value", 0) for stat in emission_stats)

    energy_logs = await EnergyModel.find_by_user_id(user_id)
    total_energy = sum(log.get("value", 0) for log in energy_logs)

    water_logs = await WaterModel.find_by_user_id(user_id)
    total_water = sum(log.get("value", 0) for log in water_logs)

    return {
        "total_emissions": total_co2,
        "emissions_by_category": emission_stats,
        "total_energy_usage": total_energy,
        "total_water_usage": total_water,
        "period": "All Time"
    }
