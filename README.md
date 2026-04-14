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
