"""
NASA Weather Risk Navigator - Backend API
FastAPI Backend Server

Este API implementa una arquitectura de endpoint único que consolida
todos los análisis necesarios en una sola respuesta completa.

Endpoint Principal:
-------------------
POST /api/risk

Recibe:
- latitude, longitude: Coordenadas globales del evento
- event_date: Fecha del evento (formato YYYY-MM-DD)
- adverse_condition: Condición climática a evaluar (hot, cold, wet)

Devuelve:
- risk_analysis: Análisis de riesgo con umbrales fijos (30°C, 10°C, 5mm) y P90/P10 como referencia
- plan_b: Alternativas generadas por IA (Google Gemini) o éxito=false si no está disponible
- climate_trend: Análisis de tendencias climáticas usando metodología IPCC/WMO
- is_fallback: Indicador de si se usaron datos de respaldo

Arquitectura:
- Single endpoint design para simplificar el frontend
- Integración con NASA POWER API para datos globales
- Gemini AI para generación de Plan B contextual
- Fallback automático a datos Montevideo si NASA API falla
- Conversión automática de tipos NumPy a Python nativo para JSON

Características:
- CORS habilitado para desarrollo local
- Logging completo de todas las operaciones
- Manejo robusto de errores
- Documentación automática en /docs
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
import os
from pathlib import Path

# Load environment variables from .env file (in project root)
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración de logging para la API
logger = logging.getLogger(__name__)

# Import funciones de análisis climático desde logic.py
try:
    from logic import (
        fetch_nasa_power_data,
        calculate_weather_risk,
        generate_plan_b_with_gemini,
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://nasa-will-it-rain-on-my-parade.onrender.com"],
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
    # Note: activity removed - Plan B will generate compatible activities based on weather
    
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

# ========================================
# ENDPOINT PRINCIPAL: POST /api/risk
# ========================================
# Este endpoint único devuelve TODOS los análisis necesarios:
# - Análisis de riesgo (calor, frío, precipitación) 
# - Plan B con alternativas generadas por IA
# - Tendencias climáticas a largo plazo

@app.post("/api/risk")
async def get_risk_analysis(request: RiskRequest):
    """
    Endpoint único que calcula todo el análisis climático y genera Plan B.
    
    Parámetros de entrada:
    - latitude: Latitud del lugar (ej: -34.90)
    - longitude: Longitud del lugar (ej: -56.16)
    - event_date: Fecha del evento (formato: "DD/MM/YYYY" o "YYYY-MM-DD")
    - adverse_condition: Condición adversa a analizar ('Very Hot', 'Very Cold', etc.)
    
    Retorna:
    - risk_analysis: Análisis de riesgo P90 (probabilidad, umbral, nivel)
    - plan_b: Alternativas generadas por IA o sistema fallback
    - climate_trend: Análisis de tendencias climáticas (IPCC/WMO)
    """
    
    try:
        # ========================================
        # PASO 0: EXTRAER MES DE LA FECHA DEL EVENTO
        # ========================================
        logger.info(f"Extrayendo mes de la fecha: {request.event_date}")
        
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
        logger.info(f"Fecha parseada: año={target_year}, mes={target_month}")
        
        # ========================================
        # PASO 1: OBTENER DATOS HISTÓRICOS DE NASA POWER API
        # ========================================
        logger.info("Starting data fetch from NASA POWER API")
        
        # Calcular años para la búsqueda (20 años de historia desde el año del evento)
        start_year = target_year - 20
        end_year = target_year - 1  # Hasta el año anterior al evento
        
        logger.info(f"Fetching data for years {start_year}-{end_year} at coordinates ({request.latitude}, {request.longitude})")
        
        # fetch_nasa_power_data maneja internamente el fallback a Montevideo si NASA falla
        historical_data = fetch_nasa_power_data(
            lat=request.latitude,
            lon=request.longitude,
            start_year=start_year,
            end_year=end_year
        )
        
        logger.info(f"Data fetch completed: {len(historical_data)} records received")

        # ========================================
        # PASO 2: ANÁLISIS DE RIESGO P90
        # ========================================
        logger.info(f"Starting risk calculation for month {target_month} with condition: {request.adverse_condition}")
        
        # Map condition ID directly to risk type (cold, hot, wet)
        # Frontend sends: "cold", "hot", "wet"
        adverse_condition_lower = request.adverse_condition.lower()
        
        if adverse_condition_lower == 'hot':
            risk_type = "heat"
        elif adverse_condition_lower == 'cold':
            risk_type = "cold"
        elif adverse_condition_lower == 'wet':
            risk_type = "precipitation"
        else:
            risk_type = "heat"
            
        logger.info(f"Risk type determined: {risk_type} from condition: {request.adverse_condition}")
        
        # Calcular riesgo usando calculate_weather_risk con el mes objetivo
        risk_analysis = calculate_weather_risk(historical_data, risk_type, target_month)
        
        logger.info(f"Risk analysis completed: Level={risk_analysis.get('risk_level')}, "
                    f"Probability={risk_analysis.get('probability')}%, "
                    f"Threshold={risk_analysis.get('risk_threshold')}")

        # ========================================
        # PASO 3: ANÁLISIS DE TENDENCIAS CLIMÁTICAS (IPCC/WMO)
        # ========================================
        logger.info(f"Starting climate trend analysis for month {target_month}")
        
        # Filtrar datos históricos para el mes objetivo (comparar primeros vs últimos 5 años)
        monthly_data_for_trend = filter_data_by_month(historical_data, target_month)
        
        logger.info(f"Monthly data filtered: {len(monthly_data_for_trend)} records from month {target_month}")
        
        # Analizar tendencias climáticas en el mes objetivo usando metodología IPCC/WMO
        # Compara temperatura promedio de primeros 5 años vs últimos 5 años
        climate_trend_result = analyze_climate_change_trend(monthly_data_for_trend)
        
        # Formatear mensaje de tendencia para el frontend
        climate_message = f"Climate Trend: {climate_trend_result.get('trend_status', 'UNKNOWN')} - {climate_trend_result.get('message', 'No trend data')}"
        
        logger.info(f"Climate trend analysis completed: Status={climate_trend_result.get('trend_status')}, "
                    f"Difference={climate_trend_result.get('difference', 0):.2f}°C")
        
        # ========================================
        # PASO 4: GENERACIÓN DE PLAN B (AI-POWERED ALTERNATIVES)
        # ========================================
        logger.info("Starting Plan B generation with Gemini AI")
        
        # Intentar con Gemini AI
        # Gemini genera actividades compatibles con el clima y ubicación
        plan_b = {"success": False, "alternatives": [], "message": "Plan B generation unavailable"}
        
        try:
            plan_b = generate_plan_b_with_gemini(
                adverse_condition=request.adverse_condition,  # Direct: cold, hot, wet
                risk_analysis=risk_analysis,
                location=f"{request.latitude}, {request.longitude}",
                target_month=target_month,
                latitude=request.latitude
            )
            logger.info(f"Gemini AI successful: Generated {len(plan_b.get('alternatives', []))} alternatives")
            
        except Exception as gemini_error:
            logger.warning(f"Gemini AI unavailable: {gemini_error}")
                
        # ========================================
        # PASO 5: RESPUESTA CONSOLIDADA
        # ========================================
        logger.info("Consolidating final response with all analyses")
        
        # Convert all numpy types to native Python types for JSON serialization
        def convert_to_python_types(obj):
            """Convert numpy types to native Python types for JSON serialization"""
            if isinstance(obj, (int, float, bool, str, type(None))):
                return obj
            elif isinstance(obj, dict):
                return {k: convert_to_python_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_python_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar types
                return obj.item()
            elif hasattr(obj, '__dict__'):
                return convert_to_python_types(obj.__dict__)
            else:
                return str(obj)
        
        # Convert risk_analysis to native Python types
        risk_analysis_converted = convert_to_python_types(risk_analysis)
        plan_b_converted = convert_to_python_types(plan_b)
        climate_trend_details_converted = convert_to_python_types(climate_trend_result)
        
        # Check if we used fallback data
        is_fallback = historical_data.get('is_fallback', [False]).iloc[0] if isinstance(historical_data, pd.DataFrame) and len(historical_data) > 0 else False
        
        response = {
            "success": True,
            "is_fallback": bool(is_fallback),
            "risk_analysis": risk_analysis_converted,
            "plan_b": plan_b_converted,
            "climate_trend": climate_message,
            "climate_trend_details": climate_trend_details_converted
        }
        
        logger.info("Endpoint /api/risk completed successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in /api/risk endpoint: {str(e)}", exc_info=True)
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


# =============================================================================
# EJEMPLO DE RESPUESTA COMPLETA DEL ENDPOINT /api/risk
# =============================================================================
"""
EJEMPLO DE REQUEST (desde frontend):
POST http://localhost:8000/api/risk
{
    "latitude": -34.90,
    "longitude": -56.16,
    "event_date": "2026-12-16",
    "adverse_condition": "Very Cold"  // Frontend envía: "Very Cold", "Very Hot", "Very Rainy"
}


EJEMPLO DE RESPONSE:
{
    "success": true,
    "risk_analysis": {
        "probability": 25.5,
        "risk_threshold": 15.2,
        "status_message": "❄️ MODERATE RISK of cold weather. Dress warmly!",
        "risk_level": "MODERATE",
        "total_observations": 620,
        "adverse_count": 158
    },
    "plan_b": {
        "success": true,
        "message": "Generated 4 Plan B alternatives using Gemini AI",
        "alternatives": [
            {
                "title": "Museo Torres García",
                "description": "Explore Uruguayan art in a climate-controlled museum",
                "type": "indoor",
                "reason": "Warm cultural experience perfect for cold weather",
                "tips": "Check current exhibitions and guided tour schedules",
                "location": "Sarandí 683, Montevideo",
                "duration": "2-3 hours",
                "cost": "Low"
            },
            {
                "title": "Termas de Daymán",
                "description": "Relax in natural hot springs",
                "type": "outdoor",
                "reason": "Hot water therapy is ideal for cold weather",
                "tips": "Bring towels, wear flip-flops, check pool temperatures",
                "location": "Salto, Uruguay",
                "duration": "Half day",
                "cost": "Medium"
            },
            {
                "title": "Indoor Markets Tour",
                "description": "Visit Mercado del Puerto and try Uruguayan barbecue",
                "type": "indoor",
                "reason": "Food experience in warm environment",
                "tips": "Try traditional parrillada and local wines",
                "location": "Mercado del Puerto, Montevideo",
                "duration": "2-3 hours",
                "cost": "Medium"
            },
            {
                "title": "Teatro Solís",
                "description": "Attend a performance in Uruguay's historic theater",
                "type": "indoor",
                "reason": "Cultural entertainment in beautiful warm venue",
                "tips": "Book tickets in advance, dress code varies",
                "location": "Buenos Aires, Montevideo",
                "duration": "2-4 hours",
                "cost": "Medium"
            }
        ],
        "ai_model": "Gemini 2.0 Flash",
        "generated_at": "2025-01-15T18:30:00",
        "context": {
            "adverse_condition": "very cold",
            "risk_level": "MODERATE",
            "location": "-34.90, -56.16",
            "season": "Summer",
            "target_month": 12
        }
    },
    "climate_trend": "Climate Trend: WARMING_TREND - 🟠 WARMING TREND: +0.85°C over 20 years. Statistically significant warming detected - heat risk is increasing.",
    "climate_trend_details": {
        "trend_status": "WARMING_TREND",
        "early_period_mean": 23.45,
        "recent_period_mean": 24.30,
        "difference": 0.85,
        "early_years": [2006, 2007, 2008, 2009, 2010],
        "recent_years": [2021, 2022, 2023, 2024, 2025],
        "message": "🟠 WARMING TREND: +0.85°C over 20 years. Statistically significant warming detected - heat risk is increasing.",
        "methodology": "IPCC/WMO standard analysis",
        "data_period": "20 years (2006-2025)"
    }
}

NOTAS:
- risk_analysis: Análisis de riesgo para el mes objetivo (diciembre)
- plan_b: Actividades compatibles generadas por IA según clima
- climate_trend: Mensaje resumido de tendencia climática
- climate_trend_details: Detalles científicos completos del análisis IPCC/WMO

FLUJO:
1. Extrae mes (12) de event_date
2. Obtiene 20 años de datos de NASA POWER API
3. Filtra datos para diciembre (target_month=12)
4. Calcula riesgo de cold usando P10 en Max_Temperature_C
5. Analiza tendencias climáticas (primeros 5 vs últimos 5 años)
6. Genera Plan B con Gemini AI usando contexto completo
7. Retorna todo en una sola respuesta consolidada
"""