import os
import joblib
from pathlib import Path
from app.utils.logger import logger

# Base directory for models
MODEL_DIR = Path(__file__).parent / "models"
CARBON_MODEL_PATH = MODEL_DIR / "carbon_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# Cached models
_models = {
    "carbon_model": None,
    "scaler": None
}

def load_models():
    """
    Loads the machine learning models and scalers into memory if not already loaded.
    """
    global _models
    
    try:
        if _models["carbon_model"] is None:
            if not CARBON_MODEL_PATH.exists():
                logger.error(f"Carbon model file not found at {CARBON_MODEL_PATH}")
                # We won't raise here if we want the app to start even without models, 
                # but for ML module it's critical.
                raise FileNotFoundError(f"Carbon model file not found at {CARBON_MODEL_PATH}")
            
            logger.info(f"Loading carbon model from {CARBON_MODEL_PATH}...")
            _models["carbon_model"] = joblib.load(CARBON_MODEL_PATH)
            logger.info("Carbon model loaded successfully.")

        if _models["scaler"] is None:
            if not SCALER_PATH.exists():
                logger.error(f"Scaler file not found at {SCALER_PATH}")
                raise FileNotFoundError(f"Scaler file not found at {SCALER_PATH}")
            
            logger.info(f"Loading scaler from {SCALER_PATH}...")
            _models["scaler"] = joblib.load(SCALER_PATH)
            logger.info("Scaler loaded successfully.")
            
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise e

def get_model(name: str):
    """
    Returns a loaded model by name.
    """
    if _models.get(name) is None:
        load_models()
    return _models.get(name)

def get_carbon_model():
    return get_model("carbon_model")

def get_scaler():
    return get_model("scaler")
