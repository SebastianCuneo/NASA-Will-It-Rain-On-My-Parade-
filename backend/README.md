# The Parade Planner - Backend API

## NASA Space Apps Challenge - FastAPI Backend

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API server:**
   ```bash
   uvicorn api:app --reload
   ```

3. **API will be available at:**
   - Local: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### API Endpoints

- `POST /api/risk` - Calculate weather risk assessment
- `GET /health` - Health check endpoint
- `GET /api/test` - Test endpoint with sample data

### Request Format

```json
{
  "lat": -34.90,
  "lon": -56.16,
  "month": 3
}
```

### Response Format

```json
{
  "temperature_risk": {
    "probability": 20.0,
    "risk_threshold": 29.3,
    "status_message": "🚨 HIGH RISK of extreme heat!",
    "risk_level": "HIGH",
    "total_observations": 5,
    "adverse_count": 1
  },
  "precipitation_risk": {
    "probability": 20.0,
    "risk_threshold": 48.9,
    "status_message": "🌧️ HIGH RISK of heavy rainfall!",
    "risk_level": "HIGH",
    "total_observations": 5,
    "adverse_count": 1
  },
  "location": {
    "lat": -34.90,
    "lon": -56.16
  },
  "month": 3
}
```
