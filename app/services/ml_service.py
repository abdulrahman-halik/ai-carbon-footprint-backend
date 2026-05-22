# Re-export the .pkl-based model functions from the ml package
from app.ml.model_loader import get_model
from app.ml.predictor import predict

# Removed the redundant/unconnected JSON-based train_model from this service.
# The endpoint /api/ml/predict uses the carbon_model.pkl pipeline.
