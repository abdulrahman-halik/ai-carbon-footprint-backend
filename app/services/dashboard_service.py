from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.water_model import WaterModel
from datetime import datetime, timedelta

async def get_dashboard_summary(user_id: str):
    """
    Get aggregated data for dashboard visualizations.
    Total emissions, energy, and water usage.
    """
    # Get aggregated emissions by category
    emission_stats = await EmissionModel.get_aggregated_stats(user_id)
    
    # Calculate total CO2
    total_co2 = sum(stat["total_value"] for stat in emission_stats)
    
    # Simple totals for energy and water (could be aggregated by type/date too)
    energy_logs = await EnergyModel.find_by_user_id(user_id)
    total_energy = sum(log["value"] for log in energy_logs)
    
    water_logs = await WaterModel.find_by_user_id(user_id)
    total_water = sum(log["value"] for log in water_logs)
    
    return {
        "total_emissions": total_co2,
        "emissions_by_category": emission_stats,
        "total_energy_usage": total_energy,
        "total_water_usage": total_water,
        "period": "All Time" # Can be extended to filtering by date
    }
