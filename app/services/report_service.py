import csv
import io
from datetime import datetime, timedelta
from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.water_model import WaterModel

async def generate_user_report_csv(user_id: str, period: str):
    # Determine date range
    now = datetime.utcnow()
    if period == "monthly":
        start_date = now - timedelta(days=30)
    elif period == "yearly":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30) # Default to monthly

    # Fetch data
    emissions = await EmissionModel.find_by_user_id(user_id)
    energy = await EnergyModel.find_by_user_id(user_id)
    water = await WaterModel.find_by_user_id(user_id)

    # Filter by date and combine (simple approach)
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Type", "Date", "Category", "Value", "Unit", "Comment"])
    
    for e in emissions:
        if isinstance(e.get("date"), datetime) and e["date"] >= start_date:
             writer.writerow(["Emission", e.get("date"), e.get("category"), e.get("value"), "kgCO2", e.get("comment", "")])
    
    for en in energy:
        if isinstance(en.get("date"), datetime) and en["date"] >= start_date:
            writer.writerow(["Energy", en.get("date"), en.get("type"), en.get("consumption"), "kWh", en.get("notes", "")])
            
    for w in water:
        if isinstance(w.get("date"), datetime) and w["date"] >= start_date:
            writer.writerow(["Water", w.get("date"), "Usage", w.get("liters"), "Liters", w.get("notes", "")])

    return output.getvalue()
