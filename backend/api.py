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
import logging

# Configuración de logging para la API
logger = logging.getLogger(__name__)

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
        calculate_weather_risk,
        generate_plan_b_with_gemini,
        generate_fallback_plan_b,
        analyze_climate_change_trend,
        filter_data_by_month
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
    """
    print(f'📥 Solicitud recibida: Lat={request.latitude}, Lon={request.longitude}, '
          f'Fecha={request.event_date}, Condición={request.adverse_condition}')
    
    try:
        # ========================================
        # PASO 0: EXTRAER MES DE LA FECHA DEL EVENTO
        # ========================================
        print(f"📅 Extrayendo mes de la fecha: {request.event_date}")
        
        # Intentar parsear fecha en formato DD/MM/YYYY o YYYY-MM-DD
        try:
            if '/' in request.event_date:
                # Formato DD/MM/YYYY
                event_date_obj = datetime.strptime(request.event_date, "%d/%m/%Y")
            else:
                # Formato YYYY-MM-DD
                event_date_obj = datetime.strptime(request.event_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {request.event_date}. Use 'DD/MM/YYYY' o 'YYYY-MM-DD'")
        
        target_month = event_date_obj.month
        target_year = event_date_obj.year
        print(f"✅ Fecha parseada: año={target_year}, mes={target_month}")
        
        # ========================================
        # PASO 1: OBTENER DATOS HISTÓRICOS
        # ========================================
        print("📊 Obteniendo datos históricos de NASA POWER API...")
        
        # Calcular años para la búsqueda (20 años de historia desde el año del evento)
        start_year = target_year - 20
        end_year = target_year - 1  # Hasta el año anterior al evento
        
        print(f"📊 Buscando datos de {start_year} a {end_year}")
        
        # TODO: Usar fetch_nasa_power_data para datos reales
        # Por ahora usar datos de prueba con datos para múltiples meses
        years = []
        months = []
        temps = []
        precip = []
        
        # Crear datos de prueba para 20 años con todos los meses
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                years.append(year)
                months.append(month)
                # Simular temperatura máxima con variación por mes
                temps.append(20 + month * 1.5 + (year - start_year) * 0.1)
                precip.append(5.0 + (month - 6) * 0.5)
        
        historical_data = pd.DataFrame({
            'Year': years,
            'Month': months,
            'Max_Temperature_C': temps,
            'Precipitation_mm': precip
        })
        
        print(f"✅ Datos históricos preparados: {len(historical_data)} registros")

        # ========================================
        # PASO 2: ANÁLISIS DE RIESGO P90
        # ========================================
        print(f"🔬 Calculando análisis de riesgo para el mes {target_month}...")
        
        # Determinar tipo de riesgo según la condición adversa
        adverse_condition_lower = request.adverse_condition.lower()
        if 'hot' in adverse_condition_lower or 'heat' in adverse_condition_lower:
            risk_type = "heat"
        elif 'cold' in adverse_condition_lower or 'frio' in adverse_condition_lower:
            risk_type = "cold"
        elif 'rain' in adverse_condition_lower or 'precip' in adverse_condition_lower:
            risk_type = "precipitation"
        else:
            # Default a heat
            risk_type = "heat"
        
        # Calcular riesgo usando calculate_weather_risk con el mes objetivo
        risk_analysis = calculate_weather_risk(historical_data, risk_type, target_month)
        print(f"✅ Análisis completado: {risk_analysis.get('risk_level', 'N/A')}")

        # ========================================
        # PASO 3: ANÁLISIS DE TENDENCIAS CLIMÁTICAS
        # ========================================
        print("📈 Calculando tendencias climáticas (IPCC/WMO)...")
        
        # Filtrar datos históricos para el mes objetivo
        monthly_data_for_trend = filter_data_by_month(historical_data, target_month)
        
        # Analizar tendencias climáticas en el mes objetivo
        climate_trend_result = analyze_climate_change_trend(monthly_data_for_trend)
        
        # Formatear mensaje de tendencia para el frontend
        climate_message = f"Climate Trend: {climate_trend_result.get('trend_status', 'UNKNOWN')} - {climate_trend_result.get('message', 'No trend data')}"
        
        print(f"✅ Tendencias completadas: {climate_trend_result.get('trend_status', 'N/A')}")
        
        # ========================================
        # PASO 4: GENERACIÓN DE PLAN B
        # ========================================
        print("🤖 Generando Plan B con Gemini AI...")
        
        # Intentar con Gemini AI, si falla usar fallback
        try:
            plan_b = generate_plan_b_with_gemini(
                activity=request.activity,
                adverse_condition=request.adverse_condition.lower(),
                risk_analysis=risk_analysis,
                location=f"{request.latitude}, {request.longitude}",
                target_month=target_month,
                latitude=request.latitude
            )
        except Exception as gemini_error:
            logger.warning(f"⚠️ Gemini AI falló, activando sistema fallback: {gemini_error}")
            print(f"⚠️ Gemini AI falló, usando sistema fallback: {gemini_error}")
            
            plan_b = generate_fallback_plan_b(
                activity=request.activity,
                adverse_condition=request.adverse_condition.lower(),
                risk_level=risk_analysis.get('risk_level', 'MODERATE'),
                location=f"{request.latitude}, {request.longitude}",
                target_month=target_month,
                latitude=request.latitude
            )
            logger.info("✅ Sistema fallback activado correctamente")
        
        print(f"✅ Plan B generado: {len(plan_b.get('alternatives', []))} alternativas")
        
        # ========================================
        # PASO 5: RESPUESTA CONSOLIDADA
        # ========================================
        return {
            "success": True,
            "risk_analysis": risk_analysis,
            "plan_b": plan_b,
            "climate_trend": climate_message,
            "climate_trend_details": climate_trend_result
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