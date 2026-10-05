"""
preprocess.py — Prepare raw input data for the carbon footprint model.

The RandomForestRegressor was trained on a specific set of features.
This module converts the incoming feature dict into a 2-D numpy array
in exactly the same column order the model expects.
"""

from typing import Dict, List
import numpy as np

# Canonical feature order — must exactly match what the model was trained on.
# Obtained from model.feature_names_in_ after loading carbon_model.pkl.
#
# FIX #20 WARNING: This feature array dangerously mixes two entirely different schemas 
# (Schema 1: 'User_ID', 'Transport_Mode' vs Schema 2: 'Sex', 'Diet', survey questions).
# The current prepare_input logic simply defaults missing fields to 0.0, which produces
# silently incorrect predictions if the wrong schema is used.
# In a future iteration, this must be split or strict schema validation must be added.
FEATURE_ORDER: List[str] = [
    "User_ID",
    "Age",
    "Gender",
    "City",
    "Transport_Mode",
    "Daily_Travel_km",
    "Electricity_Usage_kWh_per_month",
    "Water_Usage_L_per_day",
    "Waste_kg_per_week",
    "Recycling_Habit",
    "Diet_Type",
    "Meat_Consumption_per_week",
    "Plastic_Usage_Level",
    "Uses_Renewable_Energy",
    "Carbon_Footprint_Score",
    "Eco_Awareness_Level",
    "Body Type",
    "Sex",
    "Diet",
    "How Often Shower",
    "Heating Energy Source",
    "Transport",
    "Vehicle Type",
    "Social Activity",
    "Monthly Grocery Bill",
    "Frequency of Traveling by Air",
    "Vehicle Monthly Distance Km",
    "Waste Bag Size",
    "Waste Bag Weekly Count",
    "How Long TV PC Daily Hour",
    "How Many New Clothes Monthly",
    "How Long Internet Daily Hour",
    "Energy efficiency",
    "Recycling",
    "Cooking_With",
    "Timestamp",
    "1. Age:",
    "2. Gender:",
    "3.  Occupation:",
    "4. How familiar are you with the concept of a carbon footprint?",
    "5. Do you currently take steps to reduce your carbon footprint (e.g., recycling, reducing energy use, sustainable travel)?  ",
    "6. How comfortable would you feel sharing lifestyle data (e.g., diet, transport habits, energy use) with a machine learning model to calculate your carbon footprint?",
    "7.  How accurate do you think such a model could be in predicting your carbon footprint?",
    "8. Would personalized recommendations (e.g., eco-friendly travel routes, diet changes, energy tips) make you more likely to adopt sustainable behaviors?",
    "9. What type of personalized recommendation would be most useful to you? ",
    "10. Do you think real-time data visualization (e.g., dashboards, mobile apps showing your impact) would increase your awareness of sustainability?",
    "11.  Which type of visualization would motivate you the most?",
    "12. In your opinion, what is the biggest challenge in adopting sustainable behaviors?  ",
    "13. Any suggestions for making sustainability apps or tools more engaging? ",
]


def prepare_input(features: Dict[str, float]) -> np.ndarray:
    """Convert a feature dict into a 2-D numpy array for model prediction.

    Missing features default to 0.0.  The resulting shape is (1, n_features).

    Args:
        features: Dict mapping feature names to numeric values.
                  Use the keys in FEATURE_ORDER.  Unknown keys are ignored;
                  missing keys default to 0.0.

    Returns:
        np.ndarray of shape (1, len(FEATURE_ORDER)) with dtype float64.

    Raises:
        ValueError: If `features` is empty or not a dict.
    """
    if not isinstance(features, dict):
        raise ValueError("features must be a dictionary of {str: float}")
    if not features:
        raise ValueError("features must not be empty")

    # FIX #20 Schema normalization: map comprehensible frontend features (Schema 1)
    # to the actual high-importance features the model was trained on (Schema 2).
    if "Vehicle Monthly Distance Km" not in features and "Daily_Travel_km" in features:
        features["Vehicle Monthly Distance Km"] = float(features["Daily_Travel_km"]) * 30.0

    if "Diet" not in features and "Meat_Consumption_per_week" in features:
        # Scale meat consumption 0-14 into Diet categorical integers (roughly 1 to 4)
        meat = float(features["Meat_Consumption_per_week"])
        if meat > 7:
            features["Diet"] = 1.0
        elif meat > 3:
            features["Diet"] = 2.0
        elif meat > 0:
            features["Diet"] = 3.0
        else:
            features["Diet"] = 4.0

    if "How Long TV PC Daily Hour" not in features and "Electricity_Usage_kWh_per_month" in features:
        # Rough translation of electric usage to the closest highly-weighted schema feature
        features["How Long TV PC Daily Hour"] = float(features["Electricity_Usage_kWh_per_month"]) / 60.0

    # Ensure other highly-weighted variables have non-zero baselines to avoid static prediction trees
    defaults = {
        "Frequency of Traveling by Air": 1.0,
        "Vehicle Type": 1.0,
        "How Many New Clothes Monthly": 2.0,
        "Waste Bag Weekly Count": 3.0,
        "Body Type": 1.0,
        "Sex": 1.0,
        "Waste Bag Size": 1.0,
        "Monthly Grocery Bill": 200.0,
        "Heating Energy Source": 1.0
    }
    
    for k, v in defaults.items():
        if k not in features:
            features[k] = v

    row = [float(features.get(name, 0.0)) for name in FEATURE_ORDER]
    return np.array([row], dtype=np.float64)
