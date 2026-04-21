import pandas as pd
import numpy as np
from typing import Dict, Any
from app.ml.model_loader import get_scaler
from app.utils.logger import logger

def preprocess_input(data: Dict[str, Any]):
    """
    Prepares raw input data for the model.
    The features must match exactly what the scaler and model were trained on.
    """
    try:
        # These features were extracted from the scaler object
        features = [
            'Timestamp', 
            '1. Age:', 
            '2. Gender:', 
            '3.  Occupation:',
            '4. How familiar are you with the concept of a carbon footprint?',
            '5. Do you currently take steps to reduce your carbon footprint (e.g., recycling, reducing energy use, sustainable travel)?  ',
            '6. How comfortable would you feel sharing lifestyle data (e.g., diet, transport habits, energy use) with a machine learning model to calculate your carbon footprint?',
            '7.  How accurate do you think such a model could be in predicting your carbon footprint?',
            '8. Would personalized recommendations (e.g., eco-friendly travel routes, diet changes, energy tips) make you more likely to adopt sustainable behaviors?',
            '9. What type of personalized recommendation would be most useful to you? ',
            '10. Do you think real-time data visualization (e.g., dashboards, mobile apps showing your impact) would increase your awareness of sustainability?',
            '11.  Which type of visualization would motivate you the most?',
            '12. In your opinion, what is the biggest challenge in adopting sustainable behaviors?  '
        ]
        
        # Create a list matching the feature order
        input_list = []
        for feature in features:
            # We assume the input data has these keys or we use a default value (0.0)
            # In a real scenario, we might need mapping for categorical values.
            val = data.get(feature, 0.0)
            if val is None:
                val = 0.0
            input_list.append(float(val))
            
        # Convert to numpy array and reshape for a single sample (1, n_features)
        input_array = np.array(input_list).reshape(1, -1)
        
        # Apply scaling
        scaler = get_scaler()
        if scaler:
            logger.info("Applying scaling to input data")
            scaled_input = scaler.transform(input_array)
            return scaled_input
        else:
            logger.warning("Scaler not found, returning raw input")
            return input_array
            
    except Exception as e:
        logger.error(f"Error during preprocessing: {str(e)}")
        raise e
