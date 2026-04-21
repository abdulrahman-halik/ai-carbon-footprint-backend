from typing import Dict, Any
from app.ml.model_loader import get_carbon_model
from app.ml.preprocess import preprocess_input
from app.utils.logger import logger

class CarbonPredictor:
    """
    Main class for running predictions using the carbon footprint model.
    """
    
    def __init__(self):
        self.model = None
        
    def _initialize(self):
        if self.model is None:
            self.model = get_carbon_model()
            
    def predict(self, raw_data: Dict[str, Any]) -> float:
        """
        Takes raw data, preprocesses it, and returns the predicted carbon footprint.
        """
        try:
            self._initialize()
            
            if self.model is None:
                logger.error("Failed to initialize carbon model.")
                raise RuntimeError("Model not loaded.")
                
            # Preprocess the data
            processed_data = preprocess_input(raw_data)
            
            # Run prediction
            logger.info("Running prediction...")
            prediction = self.model.predict(processed_data)
            
            # Return the predicted value (usually the first element of the array)
            # Depending on the model, it might be an array or a single value
            if hasattr(prediction, "__getitem__"):
                result = float(prediction[0])
            else:
                result = float(prediction)
                
            logger.info(f"Prediction result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise e

# Singleton instance for easy access
predictor = CarbonPredictor()
