# Sustainability Tracking Platform Backend

This is the FastAPI backend for the Sustainability Tracking Platform.

## Prerequisites

- Python 3.10+
- MongoDB (Local or Atlas)

## Getting Started

1. **Navigate to the Backend directory**:
   ```bash
   cd /home/abdul/projects4/final-year-project/Backend
   ```

2. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```
   *Note: I have already installed these for you in the `venv`.*

4. **Environment Variables**:
   Ensure the `.env` file exists with the following content:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=sustainability_db
   ```

5. **Run the Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access Documentation**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Machine Learning / Prediction Layer

This backend includes a lightweight ML layer that can be used for simple predictions without external ML dependencies.

- POST `/api/ml/predict`: Public endpoint that accepts a JSON body with `features` (object of numeric features) and returns a `prediction`.
- POST `/api/ml/train`: Protected endpoint (requires authentication) that accepts training data to fit a simple linear model. The model is persisted to `app/models/ml_model.json`.

The training implementation uses a small batch gradient descent in pure Python to avoid adding heavy dependencies; it is intended as a starting point and can be replaced with a more advanced model later.
