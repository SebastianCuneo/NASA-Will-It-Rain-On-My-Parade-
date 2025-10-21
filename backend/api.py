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

# Import logic module from same directory
try:
    from logic import load_historical_data, calculate_adverse_probability, calculate_precipitation_risk, calculate_cold_risk, generate_plan_b_with_gemini, generate_fallback_plan_b
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
    activity: str = "general"  # Tipo de actividad: 'beach', 'picnic', 'running', 'general'
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -34.90,
                "longitude": -56.16,
                "event_date": "16/12/2026",
                "adverse_condition": "Very Cold",
                "activity": "beach"
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
            result = load_historical_data(
                month_filter=month_filter,
                lat=request.latitude,
                lon=request.longitude
            )
            
            # Extract DataFrame from result
            historical_data = result['data']
            climate_trend = result['climate_trend']
            
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
            cold_risk = calculate_cold_risk(historical_data, request.activity)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")
        
        # Paso D: Generar Plan B con IA si hay riesgo alto
        plan_b = None
        try:
            # Determine which risk is highest and generate Plan B accordingly
            risks = {
                'temperature': temperature_risk,
                'precipitation': precipitation_risk,
                'cold': cold_risk
            }
            
            # Find the highest risk
            highest_risk = max(risks.items(), key=lambda x: x[1]['probability'])
            risk_type, risk_data = highest_risk
            
            # Only generate Plan B if risk is MODERATE or HIGH
            if risk_data['risk_level'] in ['MODERATE', 'HIGH']:
                # Map risk types to weather conditions
                weather_condition_map = {
                    'temperature': 'hot',
                    'precipitation': 'rainy',
                    'cold': 'cold'
                }
                
                weather_condition = weather_condition_map.get(risk_type, 'adverse')
                
                # Get season from cold_risk data
                season = cold_risk.get('season', 'Unknown')
                
                # Try Gemini first with enhanced context, fallback to static alternatives
                plan_b = generate_plan_b_with_gemini(
                    activity=request.activity,
                    weather_condition=weather_condition,
                    risk_level=risk_data['risk_level'],
                    location="Montevideo, Uruguay",
                    season=season,
                    temperature_risk=temperature_risk['probability'],
                    precipitation_risk=precipitation_risk['probability'],
                    cold_risk=cold_risk['probability']
                )
                
                # If Gemini fails, use fallback
                if not plan_b.get('success', False):
                    plan_b = generate_fallback_plan_b(
                        activity=request.activity,
                        weather_condition=weather_condition,
                        risk_level=risk_data['risk_level'],
                        location="Montevideo, Uruguay",
                        season=season
                    )
                
                print(f"Generated Plan B with {len(plan_b.get('alternatives', []))} alternatives")
                
        except Exception as e:
            print(f"Error generating Plan B: {str(e)}")
            plan_b = {
                "success": False,
                "message": f"Error generating Plan B: {str(e)}",
                "alternatives": []
            }
        
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
                "activity": request.activity,
                "temperature_risk": temperature_risk,
                "precipitation_risk": precipitation_risk,
                "cold_risk": cold_risk,
                "plan_b": plan_b,
                "data_source": "NASA POWER API",
                "records_analyzed": len(historical_data)
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "NASA Weather Risk Navigator API",
        "timestamp": datetime.now().isoformat()
    }

# Endpoint adicional para testing
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API functionality"""
    try:
        # Test with March data using default Montevideo coordinates
        result = load_historical_data(3, -34.90, -56.16)
        monthly_data = result['data']
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

# Regenerate Plan B request model
class RegeneratePlanBRequest(BaseModel):
    activity: str = "general"
    weather_conditions: list = []
    location: str = "Montevideo, Uruguay"
    date: str = ""
    temperature_risk: float = 0.0
    precipitation_risk: float = 0.0
    cold_risk: float = 0.0

# Regenerate Plan B endpoint
@app.post("/api/regenerate-plan-b")
def regenerate_plan_b(request: RegeneratePlanBRequest):
    """
    Regenerate Plan B alternatives using Gemini AI
    """
    try:
        # Extract data from request
        activity = request.activity
        weather_conditions = request.weather_conditions
        location = request.location
        temperature_risk = request.temperature_risk
        precipitation_risk = request.precipitation_risk
        cold_risk = request.cold_risk
        
        # Determine primary weather condition
        primary_condition = 'adverse'
        if 'wet' in weather_conditions or 'rainy' in weather_conditions:
            primary_condition = 'rainy'
        elif 'hot' in weather_conditions:
            primary_condition = 'hot'
        elif 'cold' in weather_conditions:
            primary_condition = 'cold'
        
        # Determine risk level based on probabilities
        max_risk = max(temperature_risk, precipitation_risk, cold_risk)
        if max_risk >= 30:
            risk_level = "HIGH"
        elif max_risk >= 15:
            risk_level = "MODERATE"
        elif max_risk >= 5:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Generate Plan B with Gemini AI
        plan_b = generate_plan_b_with_gemini(
            activity=activity,
            weather_condition=primary_condition,
            risk_level=risk_level,
            location=location,
            season="Summer",
            temperature_risk=temperature_risk,
            precipitation_risk=precipitation_risk,
            cold_risk=cold_risk
        )
        
        # If Gemini fails, use fallback
        if not plan_b.get('success', False):
            plan_b = generate_fallback_plan_b(
                activity=activity,
                weather_condition=primary_condition,
                risk_level=risk_level,
                location=location,
                season="Summer"
            )
        
        return {
            "success": plan_b.get('success', False),
            "alternatives": plan_b.get('alternatives', []),
            "ai_model": plan_b.get('ai_model', 'Fallback System'),
            "message": plan_b.get('message', 'Plan B generated'),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "alternatives": [],
            "ai_model": "Error",
            "message": f"Error regenerating Plan B: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NASA Weather Risk Navigator API",
        "version": "1.0.0",
        "endpoints": {
            "risk_analysis": "POST /api/risk",
            "regenerate_plan_b": "POST /api/regenerate-plan-b",
            "test": "GET /api/test",
            "docs": "GET /docs"
        },
        "data_source": "NASA POWER API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)