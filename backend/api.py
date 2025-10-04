"""
NASA Weather Risk Navigator - Backend API
NASA Space Apps Challenge - FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import logic module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from logic import load_historical_data, calculate_adverse_probability
except ImportError:
    # Fallback if logic module is not found
    def load_historical_data(month_filter: int) -> pd.DataFrame:
        try:
            df = pd.read_csv('../mock_data.csv')
            if not isinstance(month_filter, int) or month_filter < 1 or month_filter > 12:
                raise ValueError("Month must be between 1 and 12")
            monthly_data = df[df['Month'] == month_filter].copy()
            if monthly_data.empty:
                raise ValueError(f"No data found for month {month_filter}")
            return monthly_data
        except FileNotFoundError:
            raise FileNotFoundError("mock_data.csv not found")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def calculate_adverse_probability(monthly_data: pd.DataFrame) -> Dict[str, Any]:
        if monthly_data.empty:
            raise ValueError("No data provided")
        if 'Max_Temperature_C' not in monthly_data.columns:
            raise ValueError("Temperature data not found")
        
        risk_threshold = np.percentile(monthly_data['Max_Temperature_C'], 90)
        adverse_events = monthly_data[monthly_data['Max_Temperature_C'] >= risk_threshold]
        total_observations = len(monthly_data)
        adverse_count = len(adverse_events)
        probability = (adverse_count / total_observations) * 100
        
        if probability >= 20:
            risk_level = "HIGH"
            status_message = "🚨 HIGH RISK of extreme heat! Consider alternative dates."
        elif probability >= 10:
            risk_level = "MODERATE"
            status_message = "⚠️ MODERATE RISK of warm weather. Monitor conditions."
        elif probability >= 5:
            risk_level = "LOW"
            status_message = "🌤️ LOW RISK of adverse conditions. Favorable weather."
        else:
            risk_level = "MINIMAL"
            status_message = "☀️ MINIMAL RISK of extreme heat. Excellent conditions."
        
        return {
            'probability': round(probability, 1),
            'risk_threshold': round(risk_threshold, 1),
            'status_message': status_message,
            'risk_level': risk_level,
            'total_observations': total_observations,
            'adverse_count': adverse_count
        }

# Initialize FastAPI app
app = FastAPI(
    title="NASA Weather Risk Navigator API",
    description="NASA Space Apps Challenge - Weather Risk Assessment API",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class RiskRequest(BaseModel):
    lat: float
    lon: float
    month: int

class TemperatureRisk(BaseModel):
    probability: float
    risk_threshold: float
    status_message: str
    risk_level: str
    total_observations: int
    adverse_count: int

class PrecipitationRisk(BaseModel):
    probability: float
    risk_threshold: float
    status_message: str
    risk_level: str
    total_observations: int
    adverse_count: int

class RiskResponse(BaseModel):
    temperature_risk: TemperatureRisk
    precipitation_risk: PrecipitationRisk
    location: Dict[str, float]
    month: int

# Helper function to calculate precipitation risk
def calculate_precipitation_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate precipitation risk using similar methodology as temperature"""
    if 'Precipitation_mm' not in monthly_data.columns:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "📊 No precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Calculate 90th percentile for precipitation (high precipitation is adverse)
    risk_threshold = np.percentile(monthly_data['Precipitation_mm'], 90)
    
    # Count high precipitation events
    adverse_events = monthly_data[monthly_data['Precipitation_mm'] >= risk_threshold]
    total_observations = len(monthly_data)
    adverse_count = len(adverse_events)
    probability = (adverse_count / total_observations) * 100
    
    # Generate status message for precipitation
    if probability >= 20:
        risk_level = "HIGH"
        status_message = "🌧️ HIGH RISK of heavy rainfall! Consider indoor alternatives."
    elif probability >= 10:
        risk_level = "MODERATE"
        status_message = "🌦️ MODERATE RISK of rainfall. Have backup plans ready."
    elif probability >= 5:
        risk_level = "LOW"
        status_message = "🌤️ LOW RISK of heavy rain. Generally clear conditions."
    else:
        risk_level = "MINIMAL"
        status_message = "☀️ MINIMAL RISK of rainfall. Dry conditions expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NASA Weather Risk Navigator API",
        "version": "1.0.0",
        "description": "NASA Space Apps Challenge - Weather Risk Assessment",
        "endpoints": {
            "risk_assessment": "/api/risk",
            "health_check": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NASA Weather Risk Navigator API"}

@app.post("/api/risk", response_model=RiskResponse)
async def calculate_weather_risk(request: RiskRequest):
    """
    Calculate weather risk for a specific location and month
    
    Args:
        request: RiskRequest containing lat, lon, and month
        
    Returns:
        RiskResponse with temperature and precipitation risk assessments
    """
    try:
        # Validate coordinates
        if not (-90 <= request.lat <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= request.lon <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        if not (1 <= request.month <= 12):
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        # Load historical data for the specified month
        monthly_data = load_historical_data(request.month)
        
        # Calculate temperature risk
        temperature_risk_data = calculate_adverse_probability(monthly_data)
        temperature_risk = TemperatureRisk(**temperature_risk_data)
        
        # Calculate precipitation risk
        precipitation_risk_data = calculate_precipitation_risk(monthly_data)
        precipitation_risk = PrecipitationRisk(**precipitation_risk_data)
        
        # Prepare response
        response = RiskResponse(
            temperature_risk=temperature_risk,
            precipitation_risk=precipitation_risk,
            location={"lat": request.lat, "lon": request.lon},
            month=request.month
        )
        
        return response
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Historical data file not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Additional endpoint for testing
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API functionality"""
    try:
        # Test with March data
        monthly_data = load_historical_data(3)
        temp_risk = calculate_adverse_probability(monthly_data)
        precip_risk = calculate_precipitation_risk(monthly_data)
        
        return {
            "status": "success",
            "message": "API is working correctly",
            "test_data": {
                "month": 3,
                "temperature_risk": temp_risk,
                "precipitation_risk": precip_risk
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
