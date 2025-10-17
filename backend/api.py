"""
NASA Weather Risk Navigator - Backend API
NASA Space Apps Challenge - FastAPI Backend
Refactored for React Frontend Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add parent directory to path to import logic module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from logic import load_historical_data, calculate_adverse_probability, calculate_precipitation_risk, calculate_cold_risk
except ImportError as e:
    print(f"Error importing logic module: {e}")
    # Fallback functions if logic module is not found
    def load_historical_data(month_filter: int, lat: float = -34.90, lon: float = -56.16) -> pd.DataFrame:
        try:
            df = pd.read_csv('mock_data.csv')
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
            status_message = "HIGH RISK of extreme heat! Consider alternative dates."
        elif probability >= 10:
            risk_level = "MODERATE"
            status_message = "MODERATE RISK of warm weather. Monitor conditions."
        elif probability >= 5:
            risk_level = "LOW"
            status_message = "LOW RISK of adverse conditions. Favorable weather."
        else:
            risk_level = "MINIMAL"
            status_message = "MINIMAL RISK of extreme heat. Excellent conditions."
        
        return {
            'probability': round(probability, 1),
            'risk_threshold': round(risk_threshold, 1),
            'status_message': status_message,
            'risk_level': risk_level,
            'total_observations': total_observations,
            'adverse_count': adverse_count
        }

# Tarea 1: Configuración de la Aplicación FastAPI
app = FastAPI(
    title="NASA Weather Risk Navigator API",
    description="API for weather risk analysis using NASA POWER data",
    version="1.0.0"
)

# Configuración CORS para permitir conexión desde React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Tarea 2: Definición del Modelo de Petición (Pydantic)
class RiskRequest(BaseModel):
    latitude: float
    longitude: float
    event_date: str  # Formato: "DD/MM/YYYY" o "YYYY-MM-DD"
    adverse_condition: str  # Ej: 'Very Hot', 'Very Rainy', 'Very Cold', etc.
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -34.90,
                "longitude": -56.16,
                "event_date": "16/12/2026",
                "adverse_condition": "Very Cold"
            }
        }
    }

# Tarea 3: Creación del Endpoint POST /api/risk
@app.post("/api/risk")
def get_risk_analysis(request: RiskRequest):
    """
    Analiza el riesgo climático para una ubicación y fecha específica
    usando datos reales de NASA POWER API
    """
    try:
        # 1. Logging de datos recibidos para debugging
        print(f"FastAPI Received: Lat={request.latitude}, Lon={request.longitude}, Date={request.event_date}, Condition={request.adverse_condition}")
        
        # Validación de coordenadas
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        
        # Paso A: Extraer mes de event_date
        try:
            # Intentar diferentes formatos de fecha
            if '/' in request.event_date:
                # Formato DD/MM/YYYY
                day, month, year = request.event_date.split('/')
                month_filter = int(month)
            elif '-' in request.event_date:
                # Formato YYYY-MM-DD
                year, month, day = request.event_date.split('-')
                month_filter = int(month)
            else:
                raise ValueError("Invalid date format")
            
            if not (1 <= month_filter <= 12):
                raise ValueError("Month must be between 1 and 12")
                
        except (ValueError, IndexError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
        
        print(f"FastAPI Processing: Month={month_filter}")
        
        # Paso B: Cargar datos de NASA POWER
        try:
            historical_data = load_historical_data(
                month_filter=month_filter,
                lat=request.latitude,
                lon=request.longitude
            )
            
            # 2. Verificar si el DataFrame está vacío (datos de NASA fallaron)
            if historical_data.empty:
                print(f"FastAPI Warning: Empty DataFrame returned for coordinates ({request.latitude}, {request.longitude})")
                return {
                    "success": False,
                    "error": "Failed to fetch NASA data for this location/date.",
                    "data": {
                        "location": {"latitude": request.latitude, "longitude": request.longitude},
                        "date": request.event_date,
                        "month": month_filter,
                        "adverse_condition": request.adverse_condition,
                        "risk_analysis": {
                            "risk_level": "ERROR",
                            "probability": 0.0,
                            "message": "Failed to fetch NASA data for this location/date."
                        },
                        "data_source": "NASA POWER API (FAILED)",
                        "records_analyzed": 0
                    }
                }
            
            print(f"FastAPI Success: Loaded {len(historical_data)} records from NASA POWER API")
            
        except Exception as e:
            print(f"FastAPI Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading historical data: {str(e)}")
        
        # Paso C: Calcular el riesgo del percentil 90
        try:
            temperature_risk = calculate_adverse_probability(historical_data)
            precipitation_risk = calculate_precipitation_risk(historical_data)
            cold_risk = calculate_cold_risk(historical_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")
        
        # Agregar información adicional a la respuesta
        response = {
            "success": True,
            "data": {
                "location": {
                    "latitude": request.latitude,
                    "longitude": request.longitude
                },
                "date": request.event_date,
                "month": month_filter,
                "adverse_condition": request.adverse_condition,
                "temperature_risk": temperature_risk,
                "precipitation_risk": precipitation_risk,
                "cold_risk": cold_risk,
                "data_source": "NASA POWER API",
                "records_analyzed": len(historical_data)
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint adicional para testing
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API functionality"""
    try:
        # Test with March data using default Montevideo coordinates
        monthly_data = load_historical_data(3, -34.90, -56.16)
        risk_results = calculate_adverse_probability(monthly_data)
        
        return {
            "status": "success",
            "message": "API is working correctly",
            "test_data": {
                "month": 3,
                "coordinates": {"lat": -34.90, "lon": -56.16},
                "risk_analysis": risk_results,
                "records": len(monthly_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NASA Weather Risk Navigator API",
        "version": "1.0.0",
        "endpoints": {
            "risk_analysis": "POST /api/risk",
            "test": "GET /api/test",
            "docs": "GET /docs"
        },
        "data_source": "NASA POWER API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)