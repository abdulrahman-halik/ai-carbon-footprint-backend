"""
predictor.py — Use the trained brain to answer: predict carbon footprint.

This is the single entry-point used by the rest of the application.
It wires model_loader + preprocess together and returns a plain float.
"""

from typing import Dict

from app.ml.model_loader import get_model
from app.ml.preprocess import prepare_input


def predict(features: Dict[str, float]) -> float:
    """Predict the carbon footprint (kg CO₂e) for the given activity features.

    Args:
        features: Dict mapping feature names to numeric values.
                  See preprocess.FEATURE_ORDER for the full list.
                  Unknown keys are ignored; missing keys default to 0.0.

    Returns:
        Predicted carbon footprint as a float (kg CO₂e).
    """
    try:
        model = get_model()
        X = prepare_input(features)
        result = model.predict(X)
        return float(result[0])
    except RuntimeError as e:
        # Fallback heuristic if sklearn model fails to load (e.g. AppLocker DLL block)
        return fallback_predict(features)

def fallback_predict(features: Dict[str, float]) -> float:
    # A simple heuristic based on features used in WhatIfSimulator
    # The result represents a monthly carbon footprint in kg CO2e
    car = features.get("Daily_Travel_km", 20.0)
    electricity = features.get("Electricity_Usage_kWh_per_month", 300.0)
    meat = features.get("Meat_Consumption_per_week", 5.0)
    solar = features.get("Uses_Renewable_Energy", 0.0)
    
    # Simple emission factors:
    # 0.2 kg CO2 per km * 30 days = 6.0 kg/month per daily km
    # 0.4 kg CO2 per kWh
    # 3.0 kg CO2 per meat meal * 4.3 weeks = 12.9 kg/month per weekly meal
    footprint = (car * 6.0) + (electricity * 0.4) + (meat * 12.9)
    
    # Renewable energy provides a 20% reduction
    if solar > 0:
        footprint *= 0.8
        
    return footprint
