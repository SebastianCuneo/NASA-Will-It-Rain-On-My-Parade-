"""
NASA Weather Risk Navigator - Backend API
NASA Space Apps Challenge - FastAPI Backend

Este API utiliza un enfoque de endpoint único que devuelve todos los análisis
necesarios en una sola respuesta consolidada.

Endpoint Principal: POST /api/risk

Respuesta Incluye:
- risk_analysis: Análisis de riesgo climático (calor, frío, precipitación)
- plan_b: Alternativas generadas por IA (Gemini) o sistema fallback
- climate_trend: Análisis de tendencias climáticas (IPCC/WMO)
- visualizations: Datos para visualizaciones Plotly

"""
# ========================================
# IMPORTS
# ========================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

# Import funciones de análisis climático desde logic.py
try:
    # ========================================
    # FUNCIONES DE DATOS HISTÓRICOS
    # ========================================
    # fetch_nasa_power_data: Obtiene datos reales de NASA POWER API
    
    # ========================================
    # FUNCIONES DE ANÁLISIS DE RIESGO
    # ========================================
    # calculate_heat_risk: Análisis de riesgo de calor (P90)
    # calculate_cold_risk: Análisis de riesgo de frío (estacional)
    # calculate_precipitation_risk: Análisis de riesgo de precipitación (P90)
    
    # ========================================
    # FUNCIONES DE TENDENCIAS CLIMÁTICAS
    # ========================================
    # get_climate_trend_data: Análisis IPCC/WMO de tendencias
    
    # ========================================
    # FUNCIONES DE PLAN B (AI)
    # ========================================
    # generate_plan_b_with_gemini: Generación de alternativas con Gemini AI
    # generate_fallback_plan_b: Sistema fallback sin IA
    
    from logic import (
        fetch_nasa_power_data,
        calculate_heat_risk,
        calculate_cold_risk, 
        calculate_precipitation_risk,
        generate_plan_b_with_gemini,
        generate_fallback_plan_b,
        get_climate_trend_data
    )
except ImportError as e:
    print(f"Error importing logic module: {e}")

# ========================================
# CONFIGURACIÓN DE FASTAPI
# ========================================

app = FastAPI(
    title="NASA Weather Risk Navigator API",
    description="API for weather risk analysis using NASA POWER data",
    version="1.0.0"
)

# CORS: Permitir conexión desde frontend React en localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ========================================
# MODELO DE PETICIÓN (Pydantic)
# ========================================

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

# ========================================
# ENDPOINT PRINCIPAL: POST /api/risk
# ========================================
# Este endpoint único devuelve TODOS los análisis necesarios:
# - Análisis de riesgo (calor, frío, precipitación) 
# - Plan B con alternativas generadas por IA
# - Tendencias climáticas a largo plazo
# - Visualizaciones para el frontend

@app.post("/api/risk")
async def get_risk_analysis(request: RiskRequest):
    """
    Endpoint único que calcula todo el análisis climático y genera Plan B.
    
    Parámetros de entrada:
    - latitude: Latitud del lugar (ej: -34.90)
    - longitude: Longitud del lugar (ej: -56.16)
    - event_date: Fecha del evento (formato: "DD/MM/YYYY" o "YYYY-MM-DD")
    - adverse_condition: Condición adversa a analizar ('Very Hot', 'Very Cold', etc.)
    - activity: Tipo de actividad ('beach', 'picnic', 'running', 'general')
    
    Retorna:
    - risk_analysis: Análisis de riesgo P90 (probabilidad, umbral, nivel)
    - plan_b: Alternativas generadas por IA o sistema fallback
    - climate_trend: Análisis de tendencias climáticas (IPCC/WMO)
    - plot_data: Datos para visualizaciones
    """
    print(f'📥 Solicitud recibida: Lat={request.latitude}, Lon={request.longitude}, '
          f'Fecha={request.event_date}, Condición={request.adverse_condition}')
    
    try:
        # ========================================
        # PASO 1: OBTENER DATOS HISTÓRICOS
        # ========================================
        print("📊 Obteniendo datos históricos de NASA POWER API...")
        
        # TODO: Obtener datos reales de NASA usando fetch_nasa_power_data
        # Por ahora usar datos de prueba para desarrollo
        years = list(range(2020, 2025))
        historical_data = pd.DataFrame({
            'Year': years,
            'Month': [3] * len(years),
            'Max_Temperature_C': [25.5, 26.2, 27.1, 28.3, 29.0],
            'Precipitation_mm': [5.2, 3.8, 4.1, 6.7, 2.3]
        })

        # ========================================
        # PASO 2: ANÁLISIS DE RIESGO P90
        # ========================================
        print("🔬 Calculando análisis de riesgo P90...")
        risk_analysis = calculate_heat_risk(historical_data)  # Usar calculate_heat_risk
        print(f"✅ Análisis completado: {risk_analysis.get('risk_level', 'N/A')}")

        # ========================================
        # PASO 3: ANÁLISIS DE TENDENCIAS CLIMÁTICAS
        # ========================================
        print("📈 Calculando tendencias climáticas (IPCC/WMO)...")
        climate_data = get_climate_trend_data(historical_data)
        print(f"✅ Tendencias completadas: {climate_data.get('climate_trend', 'N/A')[:50]}...")
        
        # ========================================
        # PASO 4: GENERACIÓN DE PLAN B
        # ========================================
        print("🤖 Generando Plan B con Gemini AI...")
        
        # Intentar con Gemini AI, si falla usar fallback
        try:
            plan_b = generate_plan_b_with_gemini(
                activity=request.activity,
                weather_condition=request.adverse_condition.lower(),
                risk_level=risk_analysis.get('risk_level', 'MODERATE'),
                location=f"{request.latitude}, {request.longitude}",
                season="Summer",  # TODO: Calcular estación automáticamente
                temperature_risk=risk_analysis.get('probability', 0.0),
                precipitation_risk=0.0,
                cold_risk=0.0
            )
        except Exception as gemini_error:
            print(f"⚠️ Gemini AI falló, usando sistema fallback: {gemini_error}")
            plan_b = generate_fallback_plan_b(
                activity=request.activity,
                weather_condition=request.adverse_condition.lower(),
                risk_level=risk_analysis.get('risk_level', 'MODERATE'),
                location=f"{request.latitude}, {request.longitude}",
                season="Summer"
            )
        
        print(f"✅ Plan B generado: {len(plan_b.get('alternatives', []))} alternativas")
        
        # ========================================
        # PASO 5: RESPUESTA CONSOLIDADA
        # ========================================
        return {
            "success": True,
            "risk_analysis": risk_analysis,
            "plan_b": plan_b,
            "climate_trend": climate_data.get('climate_trend', 'No climate trend data available'),
            "plot_data": climate_data.get('plot_data', [])
        }
        
    except Exception as e:
        print(f"❌ Error en el servidor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )
# ========================================
# SERVER STARTUP
# ========================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando NASA Weather Risk Navigator API...")
    print("📡 Endpoint disponible: POST http://localhost:8000/api/risk")
    print("📚 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)