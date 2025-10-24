"""
The Parade Planner - Core Logic Module
NASA Space Apps Challenge MVP
Enhanced with NASA POWER API integration
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
import os
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Plan B generation will be disabled.")


def load_fallback_data(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Carga datos de fallback desde el archivo CSV de Montevideo cuando la NASA API no está disponible.
    
    Args:
        start_year: Año inicial para el rango de datos
        end_year: Año final para el rango de datos
        
    Returns:
        pd.DataFrame: DataFrame con datos de fallback de Montevideo
    """
    try:
        # Ruta al archivo de fallback
        fallback_file = os.path.join(os.path.dirname(__file__), 'FALLBACK_MONTEVIDEO_DATA.csv')
        
        if not os.path.exists(fallback_file):
            logger.error(f"Fallback file not found: {fallback_file}")
            return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])
        
        logger.info(f"Loading fallback data from Montevideo CSV: {fallback_file}")
        
        # Leer el archivo CSV, saltando las líneas de header
        df = pd.read_csv(fallback_file, skiprows=12)  # Saltar hasta la línea de datos
        
        # Convertir DOY (Day of Year) a fecha
        df['Date'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['DOY'].astype(str), format='%Y-%j')
        
        # Filtrar por rango de años
        df = df[(df['YEAR'] >= start_year) & (df['YEAR'] <= end_year)]
        
        if df.empty:
            logger.warning(f"No fallback data available for years {start_year}-{end_year}")
            return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])
        
        # Renombrar columnas para coincidir con el formato esperado
        df_processed = pd.DataFrame({
            'Year': df['YEAR'],
            'Month': df['Date'].dt.month,
            'Max_Temperature_C': df['T2M_MAX'],
            'Min_Temperature_C': df['T2M_MIN'],
            'Avg_Temperature_C': df['T2M'],
            'Precipitation_mm': df['PRECTOTCORR']
        })
        
        # Limpiar datos: eliminar valores -999 (datos faltantes de la NASA)
        df_processed = df_processed.replace(-999, np.nan).dropna()
        
        # Ordenar por año y mes
        df_processed = df_processed.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        logger.info(f"Successfully loaded {len(df_processed)} fallback records from Montevideo data")
        return df_processed
        
    except Exception as e:
        logger.error(f"Error loading fallback data: {str(e)}")
        return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])


def fetch_nasa_power_data(lat: float, lon: float, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Obtiene datos climáticos históricos diarios de la NASA POWER API.
    
    La NASA POWER API proporciona datos meteorológicos globales con resolución espacial de 0.5°x0.625°
    y temporal diaria. Esta función solicita temperatura máxima (T2M_MAX), temperatura mínima (T2M_MIN),
    temperatura promedio (T2M) y precipitación total corregida (PRECTOTCORR) para análisis de riesgo climático.

    Args:
        lat: Latitud en grados decimales (-90 a 90)
        lon: Longitud en grados decimales (-180 a 180)
        start_year: Año inicial para el rango de datos históricos
        end_year: Año final para el rango de datos históricos
        
    Returns:
        pd.DataFrame: DataFrame con datos diarios procesados, columnas:
            - Year: Año del registro
            - Month: Mes del registro (1-12)
            - Max_Temperature_C: Temperatura máxima diaria en Celsius
            - Min_Temperature_C: Temperatura mínima diaria en Celsius
            - Avg_Temperature_C: Temperatura promedio diaria en Celsius
            - Precipitation_mm: Precipitación diaria en milímetros
    """
    # DataFrame vacío como fallback en caso de error
    empty_df = pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])
    
    try:
        # URL base de la NASA POWER API para datos temporales diarios por punto
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Formato de fechas requerido por la API: YYYYMMDD
        start_date = f"{start_year}0101"  # 1 de enero del año inicial
        end_date = f"{end_year}1231"      # 31 de diciembre del año final
        
        # Parámetros de la solicitud HTTP
        params = {
            'parameters': 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR',  # Variables climáticas solicitadas
            'community': 'AG',                      # Comunidad Agroclimatológica
            'longitude': lon,                      # Coordenada de longitud
            'latitude': lat,                       # Coordenada de latitud
            'start': start_date,                   # Fecha de inicio
            'end': end_date,                       # Fecha de fin
            'format': 'JSON'                       # Formato de respuesta
        }
        
        logger.info(f"Fetching NASA POWER data for coordinates ({lat}, {lon}) from {start_year} to {end_year}")
        
        # Implementación de reintentos para manejar fallos de red
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()  # Lanza excepción para códigos HTTP 4xx/5xx
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch NASA POWER data after {max_retries} attempts: {str(e)}")
                    logger.info("Falling back to Montevideo data due to NASA API failure")
                    return load_fallback_data(start_year, end_year)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in 2 seconds... Error: {str(e)}")
                time.sleep(2)
        
        if response is None:
            logger.error("No response received from NASA API")
            logger.info("Falling back to Montevideo data due to no response")
            return load_fallback_data(start_year, end_year)
            
        # Parse de la respuesta JSON de la NASA
        data = response.json()
        
        # Validación de la estructura de respuesta de la API
        if 'messages' in data and data['messages'] and len(data['messages']) > 0:
            logger.error(f"NASA API returned error messages: {data['messages']}")
            logger.info("Falling back to Montevideo data due to API error messages")
            return load_fallback_data(start_year, end_year)
            
        if 'properties' not in data or 'parameter' not in data['properties']:
            logger.error(f"Invalid response format from NASA POWER API. Keys: {data.keys()}")
            logger.info("Falling back to Montevideo data due to invalid response format")
            return load_fallback_data(start_year, end_year)
        
        parameters = data['properties']['parameter']
        
        # Extracción de datos específicos: T2M_MAX, T2M_MIN, T2M (temperaturas) y PRECTOTCORR (precipitación)
        temp_max_data = parameters.get('T2M_MAX', {})
        temp_min_data = parameters.get('T2M_MIN', {})
        temp_avg_data = parameters.get('T2M', {})
        precip_data = parameters.get('PRECTOTCORR', {})
        
        if not temp_max_data or not temp_min_data or not temp_avg_data or not precip_data:
            logger.error("Temperature or precipitation data not found in API response")
            logger.info("Falling back to Montevideo data due to missing climate data")
            return load_fallback_data(start_year, end_year)
            
        # Conversión de datos JSON a DataFrame de Pandas
        records = []
        for date_str, temp_max_value in temp_max_data.items():
            if date_str in temp_min_data and date_str in temp_avg_data and date_str in precip_data:
                # Parse de fecha en formato YYYYMMDD a objeto datetime
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                
                # Conversión de valores (la NASA usa None para datos faltantes)
                temp_max_celsius = temp_max_value if temp_max_value is not None else None
                temp_min_celsius = temp_min_data[date_str] if temp_min_data[date_str] is not None else None
                temp_avg_celsius = temp_avg_data[date_str] if temp_avg_data[date_str] is not None else None
                precip_mm = precip_data[date_str] if precip_data[date_str] is not None else None
                
                # Creación de registro estructurado
                records.append({
                    'Year': date_obj.year,
                    'Month': date_obj.month,
                    'Max_Temperature_C': temp_max_celsius,
                    'Min_Temperature_C': temp_min_celsius,
                    'Avg_Temperature_C': temp_avg_celsius,
                    'Precipitation_mm': precip_mm
                })
        
        if not records:
            logger.error("No valid data records found in API response")
            logger.info("Falling back to Montevideo data due to empty data records")
            return load_fallback_data(start_year, end_year)
        
        # Creación del DataFrame final
        df = pd.DataFrame(records)
        
        # Limpieza de datos: eliminación de filas con valores nulos
        df = df.dropna()
        
        # Ordenamiento por año y mes para análisis temporal
        df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        logger.info(f"Successfully fetched {len(df)} records from NASA POWER API")
        return df
        
    except Exception as e:
        # Manejo de errores: retorna datos de fallback en lugar de DataFrame vacío
        logger.error(f"Fatal Error fetching or processing NASA POWER data: {str(e)}")
        logger.info("Falling back to Montevideo data due to fatal error")
        return load_fallback_data(start_year, end_year)

def calculate_heat_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula la probabilidad de condiciones climáticas adversas usando metodología P90.
    
    Esta función implementa el análisis de percentil 90 (P90) para determinar el umbral de 
    temperatura extrema histórica. El P90 representa la temperatura que se supera solo en 
    el 10% de los días históricos, siendo un indicador robusto de condiciones extremas.
    
    Metodología:
    1. Filtra datos válidos (elimina valores -999 de la NASA)
    2. Calcula el percentil 90 de temperaturas máximas históricas
    3. Cuenta días que superan este umbral
    4. Calcula probabilidad como porcentaje de días extremos
    
    Args:
        monthly_data: DataFrame con datos históricos del mes específico
        
    Returns:
        Dict con análisis de riesgo:
            - probability: Porcentaje de días con condiciones adversas (0-100)
            - risk_threshold: Temperatura umbral P90 en Celsius
            - status_message: Mensaje descriptivo del nivel de riesgo
            - risk_level: Nivel de riesgo (HIGH/MODERATE/LOW/MINIMAL)
            - total_observations: Total de observaciones válidas
            - adverse_count: Número de días que superan el umbral
    """
    if monthly_data.empty:
        raise ValueError("No data provided")
    
    if 'Max_Temperature_C' not in monthly_data.columns:
        raise ValueError("Temperature data not found")
    
    # Filtrado de datos válidos: la NASA usa -999 para indicar datos faltantes
    valid_temp_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    
    if len(valid_temp_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid temperature data for P90 calculation.",
            'risk_level': "UNKNOWN",
            'total_observations': len(monthly_data),
            'adverse_count': 0
        }
    
    # Cálculo del percentil 90: temperatura que se supera en el 10% de los días
    risk_threshold = np.percentile(valid_temp_data['Max_Temperature_C'], 90)
    
    # Conteo de eventos adversos: días que superan el umbral P90
    adverse_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] > risk_threshold]
    total_observations = len(valid_temp_data)
    adverse_count = len(adverse_events)
    
    # Cálculo de probabilidad como porcentaje de días extremos
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Clasificación de niveles de riesgo basada en umbrales empíricos
    if risk_threshold >= 30.0:  # Umbral alto: temperaturas extremas
        risk_level = "HIGH"
        status_message = f"🚨 HIGH RISK of extreme heat! P90 Threshold: {risk_threshold:.1f}°C. Extreme heat days expected to exceed this."
    elif risk_threshold >= 25.0:  # Umbral moderado: temperaturas cálidas
        risk_level = "MODERATE"
        status_message = f"⚠️ MODERATE RISK of warm weather. P90 Threshold: {risk_threshold:.1f}°C. Warm weather expected on average."
    else:  # Umbral bajo: temperaturas cómodas
        risk_level = "LOW"
        status_message = f"☀️ LOW RISK of extreme heat. P90 Threshold: {risk_threshold:.1f}°C. Comfortable temperatures expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }


    """
    Prepares temperature data for Plotly visualization (Historical Avg, P90, Recent Year).
    """
    if monthly_data.empty or 'Max_Temperature_C' not in monthly_data.columns:
        return {
            'historic_avg_c': 0.0,
            'p90_threshold_c': 0.0,
            'recent_year_data': [],
            'recent_year': None,
            'historic_range': {'min': 0.0, 'max': 0.0},
            'historic_data_available': False
        }

    # 1. Calculate P90 Threshold
    valid_temp_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    p90_threshold = np.percentile(valid_temp_data['Max_Temperature_C'], 90)

    # 2. Calculate the Overall Historical Average and Range
    historic_avg = valid_temp_data['Max_Temperature_C'].mean()
    historic_min = valid_temp_data['Max_Temperature_C'].min()
    historic_max = valid_temp_data['Max_Temperature_C'].max()

    # 3. Get Recent Year Data for comparison
    recent_year = monthly_data['Year'].max()
    recent_data = monthly_data[monthly_data['Year'] == recent_year].copy()
    
    # Create a 'Day' column for plotting (Day 1, Day 2, etc. of the month)
    recent_data['Day'] = recent_data.index - recent_data.index[0] + 1
    
    # Structure the recent data for simple plotting (Day vs Temp)
    recent_plot_data = recent_data[['Day', 'Max_Temperature_C']].to_dict('records')
    
    return {
        'p90_threshold_c': round(p90_threshold, 1),
        'historic_avg_c': round(historic_avg, 1),
        'historic_range': {'min': round(historic_min, 1), 'max': round(historic_max, 1)},
        'recent_year_data': recent_plot_data,
        'recent_year': recent_year,
        'historic_data_available': True
    }

def calculate_precipitation_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate precipitation risk using 90th percentile methodology
    
    Args:
        monthly_data: DataFrame with precipitation data
        
    Returns:
        Dict with precipitation risk analysis
    """
    if monthly_data.empty:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filter out invalid values (NASA uses -999 for missing data)
    valid_precip_data = monthly_data[monthly_data['Precipitation_mm'] >= 0]
    
    if len(valid_precip_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Use a fixed threshold for significant precipitation (5mm is noticeable rain)
    precip_threshold = 5.0
    
    # Count days with precipitation above threshold
    adverse_count = len(valid_precip_data[valid_precip_data['Precipitation_mm'] > precip_threshold])
    total_observations = len(monthly_data)
    
    # Calculate probability as percentage of days with significant precipitation
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Determine risk level
    if probability >= 20:
        risk_level = "HIGH"
        status_message = "🌧️ HIGH RISK of heavy precipitation. Consider indoor alternatives."
    elif probability >= 10:
        risk_level = "MODERATE"
        status_message = "🌦️ MODERATE RISK of rain. Bring umbrella."
    elif probability >= 5:
        risk_level = "LOW"
        status_message = "🌤️ LOW RISK of precipitation. Light rain possible."
    else:
        risk_level = "MINIMAL"
        status_message = "☀️ MINIMAL RISK of rain. Dry conditions expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(precip_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }

def get_seasonal_cold_threshold(month: int, activity: str = "general") -> float:
    """
    Obtiene umbrales de temperatura fría basados en estacionalidad y tipo de actividad.
    
    Esta función implementa umbrales adaptativos que consideran tanto la época del año
    como el tipo de actividad planificada. Los umbrales están calibrados empíricamente
    para Uruguay, considerando las condiciones climáticas locales y la tolerancia
    específica de cada actividad a temperaturas bajas.
    
    Lógica de umbrales:
    - Verano (Dic-Feb): Umbrales más altos (20-23°C) - mayor sensibilidad al frío
    - Otoño/Invierno (Mar-Ago): Umbrales más bajos (10-18°C) - mayor tolerancia
    - Primavera (Sep-Nov): Umbrales intermedios (16-20°C)
    
    Actividades específicas:
    - Beach: Mayor sensibilidad (umbrales más altos)
    - Running: Mayor tolerancia (umbrales más bajos)
    - Picnic: Sensibilidad intermedia
    - General: Umbral estándar
    
    Args:
        month: Mes del año (1-12)
        activity: Tipo de actividad ('beach', 'picnic', 'running', 'general')
        
    Returns:
        float: Temperatura umbral en Celsius para considerar condiciones frías
    """
    # Matriz de ajustes estacionales por mes y actividad
    # Valores basados en análisis empírico de tolerancia al frío en Uruguay
    seasonal_adjustments = {
        12: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},  # Diciembre (Verano)
        1: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},   # Enero (Verano)
        2: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},   # Febrero (Verano)
        3: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0},   # Marzo (Otoño)
        4: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0},   # Abril (Otoño)
        5: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},   # Mayo (Otoño)
        6: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},   # Junio (Invierno)
        7: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},   # Julio (Invierno)
        8: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},   # Agosto (Invierno)
        9: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},  # Septiembre (Primavera)
        10: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0}, # Octubre (Primavera)
        11: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0}, # Noviembre (Primavera)
    }
    
    # Obtención del umbral específico para el mes y actividad
    month_data = seasonal_adjustments.get(month, seasonal_adjustments[1])  # Fallback a enero
    return month_data.get(activity, month_data["general"])  # Fallback a "general"

def calculate_cold_risk(monthly_data: pd.DataFrame, activity: str = "general") -> Dict[str, Any]:
    """
    Calcula el riesgo de condiciones frías usando metodología estacional y específica por actividad.
    
    Esta función implementa un análisis de riesgo de frío más sofisticado que considera:
    1. Estacionalidad: Umbrales adaptativos según la época del año
    2. Tipo de actividad: Sensibilidad específica de cada actividad al frío
    3. Datos históricos: Análisis basado en temperaturas históricas del mes
    
    A diferencia del análisis de calor (P90), el análisis de frío usa umbrales fijos
    calibrados empíricamente para Uruguay, ya que las condiciones frías son más
    predecibles y dependen menos de eventos extremos.
    
    Args:
        monthly_data: DataFrame con datos históricos del mes específico
        activity: Tipo de actividad ('beach', 'picnic', 'running', 'general')
        
    Returns:
        Dict con análisis de riesgo de frío:
            - probability: Porcentaje de días con condiciones frías (0-100)
            - risk_threshold: Temperatura umbral en Celsius
            - status_message: Mensaje descriptivo del nivel de riesgo
            - risk_level: Nivel de riesgo (HIGH/MODERATE/LOW/MINIMAL)
            - total_observations: Total de observaciones válidas
            - adverse_count: Número de días por debajo del umbral
            - season: Estación del año identificada
            - activity: Tipo de actividad analizada
    """
    if monthly_data.empty:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0,
            'season': 'Unknown'
        }
    
    # Filtrado de datos válidos: elimina valores -999 de la NASA
    valid_temp_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    
    if len(valid_temp_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0,
            'season': 'Unknown'
        }
    
    # Obtención del mes para determinar estacionalidad y umbral
    month = monthly_data['Month'].iloc[0] if not monthly_data.empty else 1
    
    # Obtención del umbral estacional específico para la actividad
    cold_threshold = get_seasonal_cold_threshold(month, activity)
    
    # Conteo de eventos fríos: días por debajo del umbral estacional
    cold_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] < cold_threshold]
    total_observations = len(monthly_data)
    cold_count = len(cold_events)
    
    # Cálculo de probabilidad como porcentaje de días fríos
    probability = (cold_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Mapeo de meses a estaciones para Uruguay (hemisferio sur)
    season_names = {
        12: "Summer", 1: "Summer", 2: "Summer",    # Verano
        3: "Autumn", 4: "Autumn", 5: "Autumn",     # Otoño
        6: "Winter", 7: "Winter", 8: "Winter",     # Invierno
        9: "Spring", 10: "Spring", 11: "Spring"    # Primavera
    }
    season = season_names.get(month, "Unknown")
    
    # Clasificación de niveles de riesgo basada en probabilidad empírica
    if probability >= 20:  # Alto riesgo: más del 20% de días fríos
        risk_level = "HIGH"
        status_message = f"🧊 HIGH RISK of cold weather in {season}. Consider warmer dates or indoor alternatives!"
    elif probability >= 10:  # Riesgo moderado: 10-20% de días fríos
        risk_level = "MODERATE"
        status_message = f"❄️ MODERATE RISK of cold weather in {season}. Dress warmly!"
    elif probability >= 5:   # Riesgo bajo: 5-10% de días fríos
        risk_level = "LOW"
        status_message = f"🌤️ LOW RISK of cold weather in {season}. Light jacket recommended."
    else:  # Riesgo mínimo: menos del 5% de días fríos
        risk_level = "MINIMAL"
        status_message = f"☀️ MINIMAL RISK of cold weather in {season}. Comfortable temperatures expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(cold_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': cold_count,
        'season': season,
        'activity': activity
    }

def analyze_climate_change_trend(monthly_data: pd.DataFrame, comparison_years: int = 30) -> Dict[str, Any]:
    """
    Analiza tendencias de cambio climático comparando el año más reciente con el promedio histórico.
    
    Esta función implementa un análisis de tendencias climáticas que compara las temperaturas
    del año más reciente disponible con el promedio histórico de largo plazo. El análisis
    proporciona información sobre si las condiciones climáticas están cambiando hacia
    temperaturas más cálidas o más frías en la ubicación específica.
    
    Metodología:
    1. Identifica el año más reciente en los datos
    2. Calcula el promedio histórico excluyendo el año reciente
    3. Calcula el promedio del año reciente
    4. Compara las diferencias y clasifica la tendencia
    
    Clasificación de tendencias:
    - SIGNIFICANT_WARMING: Diferencia >= 1.0°C (cambio significativo)
    - WARMING_TREND: Diferencia >= 0.5°C (tendencia de calentamiento)
    - COOLING_TREND: Diferencia <= -0.5°C (tendencia de enfriamiento)
    - STABLE: Diferencia < 0.5°C (condiciones estables)
    
    Args:
        monthly_data: DataFrame con datos históricos del mes específico
        comparison_years: Años de comparación (parámetro no utilizado actualmente)
        
    Returns:
        Dict con análisis de tendencia climática:
            - trend_status: Estado de la tendencia (SIGNIFICANT_WARMING, etc.)
            - historical_mean: Temperatura promedio histórica en Celsius
            - recent_mean: Temperatura promedio del año reciente en Celsius
            - difference: Diferencia entre reciente e histórico en Celsius
            - message: Mensaje descriptivo de la tendencia
    """
    if monthly_data.empty:
        return {
            'trend_status': 'UNKNOWN',
            'historical_mean': 0.0,
            'recent_mean': 0.0,
            'difference': 0.0,
            'message': "No data available for trend analysis."
        }

    # Identificación del año más reciente en los datos
    recent_year = monthly_data['Year'].max()
    recent_data = monthly_data[monthly_data['Year'] == recent_year]
    historical_data = monthly_data[monthly_data['Year'] < recent_year]
    
    # Validación de datos suficientes para análisis
    if historical_data.empty or recent_data.empty:
        return {
            'trend_status': 'INSUFFICIENT_DATA',
            'historical_mean': 0.0,
            'recent_mean': 0.0,
            'difference': 0.0,
            'message': "Insufficient data to compare recent year with historical average."
        }
    
    # Cálculo de promedios de temperatura máxima
    historical_mean = historical_data['Max_Temperature_C'].mean()
    recent_mean = recent_data['Max_Temperature_C'].mean()
    difference = recent_mean - historical_mean
    
    # Clasificación de la tendencia basada en diferencias de temperatura
    if difference >= 1.0:  # Calentamiento significativo
        trend_status = 'SIGNIFICANT_WARMING'
        message = f"🔴 The most recent year was significantly warmer (+{difference:.2f}°C) than the long-term average."
    elif difference >= 0.5:  # Tendencia de calentamiento
        trend_status = 'WARMING_TREND'
        message = f"🟠 The most recent year was warmer (+{difference:.2f}°C) than the long-term average."
    elif difference <= -0.5:  # Tendencia de enfriamiento
        trend_status = 'COOLING_TREND'
        message = f"🔵 The most recent year was cooler ({difference:.2f}°C) than the long-term average."
    else:  # Condiciones estables
        trend_status = 'STABLE'
        message = f"🟢 Temperatures in the most recent year were close to the long-term average (diff: {difference:.2f}°C)."

    return {
        'trend_status': trend_status,
        'historical_mean': round(historical_mean, 2),
        'recent_mean': round(recent_mean, 2),
        'difference': round(difference, 2),
        'message': message
    }

def parse_fallback_response(response_text: str) -> list:
    
    """
    Parse Gemini response when JSON parsing fails
    """
    alternatives = []
    lines = response_text.split('\n')
    current_alt = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('{') or line.startswith('}'):
            continue
            
        # Look for activity titles (various patterns)
        if any(keyword in line.lower() for keyword in ['visit', 'go to', 'try', 'enjoy', 'explore', 'discover']):
            if current_alt and current_alt.get('title'):
                alternatives.append(current_alt)
            current_alt = {
                "title": line,
                "description": "",
                "type": "mixed",
                "reason": "",
                "tips": "",
                "location": "Various locations",
                "duration": "1-3 hours",
                "cost": "Varies"
            }
        elif current_alt:
            if not current_alt.get("description"):
                current_alt["description"] = line
            elif not current_alt.get("reason"):
                current_alt["reason"] = line
            elif not current_alt.get("tips"):
                current_alt["tips"] = line
    
    if current_alt and current_alt.get('title'):
        alternatives.append(current_alt)
    
    return alternatives[:4]  # Limit to 4 alternatives
    fallback_alternatives = {
        "beach": {
            "cold": [
                {
                    "title": "Indoor Pool Complex",
                    "description": "Visit a heated indoor pool or water park",
                    "type": "indoor",
                    "reason": "Warm water activities without cold weather exposure",
                    "tips": "Bring swimwear and check opening hours"
                },
                {
                    "title": "Museo del Mar",
                    "description": "Explore marine life and ocean exhibits",
                    "type": "indoor",
                    "reason": "Ocean-themed experience in a warm environment",
                    "tips": "Great for families and educational"
                },
                {
                    "title": "Thermal Baths",
                    "description": "Relax in natural hot springs",
                    "type": "mixed",
                    "reason": "Warm water therapy in natural setting",
                    "tips": "Bring towels and check temperature requirements"
                }
            ],
            "rainy": [
                {
                    "title": "Shopping Mall",
                    "description": "Visit Punta Carretas or Montevideo Shopping",
                    "type": "indoor",
                    "reason": "Stay dry while enjoying shopping and dining",
                    "tips": "Check for special events or sales"
                },
                {
                    "title": "Cinema Complex",
                    "description": "Watch latest movies in comfortable theaters",
                    "type": "indoor",
                    "reason": "Perfect rainy day entertainment",
                    "tips": "Book tickets in advance for popular shows"
                }
            ]
        },
        "picnic": {
            "cold": [
                {
                    "title": "Indoor Food Market",
                    "description": "Visit Mercado del Puerto for local cuisine",
                    "type": "indoor",
                    "reason": "Food experience in warm environment",
                    "tips": "Try traditional Uruguayan barbecue"
                },
                {
                    "title": "Cooking Class",
                    "description": "Learn to cook local dishes",
                    "type": "indoor",
                    "reason": "Interactive food experience",
                    "tips": "Book in advance and bring appetite"
                }
            ],
            "rainy": [
                {
                    "title": "Restaurant Tour",
                    "description": "Visit multiple restaurants for different courses",
                    "type": "indoor",
                    "reason": "Food adventure without weather concerns",
                    "tips": "Plan route and make reservations"
                }
            ]
        },
        "running": {
            "cold": [
                {
                    "title": "Indoor Gym",
                    "description": "Use treadmill or indoor track",
                    "type": "indoor",
                    "reason": "Maintain fitness routine in warm environment",
                    "tips": "Bring gym clothes and water bottle"
                },
                {
                    "title": "Shopping Mall Walking",
                    "description": "Power walk through large shopping centers",
                    "type": "indoor",
                    "reason": "Exercise while staying warm",
                    "tips": "Wear comfortable shoes and track steps"
                }
            ],
            "rainy": [
                {
                    "title": "Indoor Sports Complex",
                    "description": "Use indoor courts or tracks",
                    "type": "indoor",
                    "reason": "Stay active without getting wet",
                    "tips": "Check availability and book time slots"
                }
            ]
        }
    }
    
    # Get alternatives for the specific activity and condition
    alternatives = fallback_alternatives.get(activity, {}).get(weather_condition, [])
    
    # If no specific alternatives, provide general ones
    if not alternatives:
        alternatives = [
            {
                "title": "Museo Nacional de Artes Visuales",
                "description": "Explore Uruguayan art and culture",
                "type": "indoor",
                "reason": "Cultural experience regardless of weather",
                "tips": "Check current exhibitions and opening hours"
            },
            {
                "title": "Teatro Solís",
                "description": "Attend a performance or take a guided tour",
                "type": "indoor",
                "reason": "Cultural entertainment in beautiful venue",
                "tips": "Book tickets in advance for performances"
            }
        ]
    
    return {
        "success": True,
        "message": f"Generated {len(alternatives)} Plan B alternatives (fallback mode)",
        "alternatives": alternatives,
        "ai_model": "Fallback System",
        "generated_at": datetime.now().isoformat()
    }


    """
    Test function to verify NASA POWER API integration
    """
    print("Testing NASA POWER API integration...")
    
    try:
        # Test with Montevideo coordinates
        test_lat = -34.90
        test_lon = -56.16
        test_start_year = 2020
        test_end_year = 2024
      
        print(f"Testing with coordinates: ({test_lat}, {test_lon}")
        print(f"Date range: {test_start_year} to {test_end_year}")

        #Fetch data 
        df = fetch_nasa_power_data(test_lat, test_lon, test_start_year, test_end_year)
        
        print(f"Successfully fetched {len(df)} records")

        # Test month filtering and trend analysis
        load_result = load_historical_data(3)   # March
        march_data = load_result['data']
        climate_trend = load_result['climate_trend']
        print(f"March data: {len(march_data)} records")
        
        # Test the trend analysis
        print(f"Climate Trend Status: {climate_trend['trend_status']}")
        print(f"Trend Message: {climate_trend['message']}")

        # Test Plotly data preparation
        plot_result = get_plot_data(march_data['data'])
        print(f"P90 Threshold for Plot: {plot_result['p90_threshold_c']}C")
        print(f"Recent Year Data Points for Plot: {len(plot_result['recent_year_data'])}")
        
        # Test risk calculation
        risk_analysis = calculate_heat_risk(march_data)
        print(f"Risk analysis: {risk_analysis['risk_level']} ({risk_analysis['probability']:.1f}%)")
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


    """
    Crea el tercer gráfico: Análisis de riesgo de calor con áreas y umbrales
    
    Args:
        plot_data: Lista de diccionarios con datos P90 por año
        
    Returns:
        Dict: Configuración del gráfico Plotly
    """
    if not plot_data:
        return {"error": "No data available for heat risk analysis chart"}
    
    df = pd.DataFrame(plot_data)
    
    # Definir umbrales de riesgo
    risk_thresholds = {
        'low_risk': 25,      # Bajo riesgo
        'moderate_risk': 30, # Riesgo moderado
        'high_risk': 35,     # Alto riesgo
        'extreme_risk': 40   # Riesgo extremo
    }
    
    fig = go.Figure()
    
    # Áreas de riesgo
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=[risk_thresholds['extreme_risk']] * len(df),
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=[risk_thresholds['high_risk']] * len(df),
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        fillcolor='rgba(255,0,0,0.3)',
        name='Riesgo Extremo (>40°C)',
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=[risk_thresholds['moderate_risk']] * len(df),
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        fillcolor='rgba(255,165,0,0.3)',
        name='Riesgo Alto (30-40°C)',
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=[risk_thresholds['low_risk']] * len(df),
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        fillcolor='rgba(255,255,0,0.3)',
        name='Riesgo Moderado (25-30°C)',
        hoverinfo='skip'
    ))
    
    # Líneas de datos principales
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['P90_Max_Temp'],
        mode='lines+markers',
        name='P90 Temperatura',
        line=dict(color='red', width=4),
        marker=dict(size=10, color='red'),
        hovertemplate='<b>Año:</b> %{x}<br><b>P90:</b> %{y:.1f}°C<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['Max_Temp'],
        mode='lines+markers',
        name='Temperatura Máxima',
        line=dict(color='darkred', width=3, dash='dash'),
        marker=dict(size=8, color='darkred'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Máxima:</b> %{y:.1f}°C<extra></extra>'
    ))
    
    # Líneas de umbral
    for threshold_name, threshold_value in risk_thresholds.items():
        fig.add_hline(
            y=threshold_value,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Umbral {threshold_name.replace('_', ' ').title()}: {threshold_value}°C",
            annotation_position="top right"
        )
    
    # Configurar layout
    fig.update_layout(
        title=None,  # Remover título interno
        xaxis_title='Año',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        template='plotly_white',
        height=320,
        width=400,
        margin=dict(l=40, r=40, t=20, b=40),  # Más espacio en los lados, menos arriba
        autosize=False,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=9)  # Fuente más pequeña
        )
    )
    
    return {
        "chart_type": "heat_risk_analysis",
        "figure": fig.to_dict(),
        "description": "Gráfico de análisis de riesgo que muestra P90 vs umbrales de riesgo de calor con áreas coloreadas"
    }

def generate_plan_b_with_gemini(
    activity: str,
    weather_condition: str,
    risk_level: str,
    location: str = "Montevideo, Uruguay",
    season: str = "Summer",
    temperature_risk: float = None,
    precipitation_risk: float = None,
    cold_risk: float = None
) -> Dict[str, Any]:
    """
    Generate intelligent Plan B suggestions using Gemini AI with enhanced context
    
    Args:
        activity: Type of activity (beach, picnic, running, etc.)
        weather_condition: Weather condition causing the risk (cold, hot, rainy, etc.)
        risk_level: Risk level (HIGH, MODERATE, LOW, MINIMAL)
        location: Location name for context
        season: Current season
        temperature_risk: Temperature risk probability (0-100)
        precipitation_risk: Precipitation risk probability (0-100)
        cold_risk: Cold weather risk probability (0-100)
        
    Returns:
        Dict with Plan B suggestions
    """
    if not GEMINI_AVAILABLE:
        return {
            "success": False,
            "message": "Gemini AI not available. Please install google-generativeai package.",
            "alternatives": []
        }
    
    try:
        # Configure Gemini API with better error handling
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {
                "success": False,
                "message": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable.",
                "alternatives": []
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Enhanced context-aware prompt with risk probabilities
        risk_context = ""
        if temperature_risk is not None:
            risk_context += f"- Temperature Risk: {temperature_risk:.1f}%\n"
        if precipitation_risk is not None:
            risk_context += f"- Precipitation Risk: {precipitation_risk:.1f}%\n"
        if cold_risk is not None:
            risk_context += f"- Cold Weather Risk: {cold_risk:.1f}%\n"
        
        # Create enhanced prompt with better structure
        prompt = f"""You are an expert weather planning assistant for {location}. Generate intelligent Plan B alternatives for outdoor activities when weather conditions are unfavorable.

CONTEXT:
- Original Activity: {activity}
- Primary Weather Risk: {weather_condition} ({risk_level} risk level)
- Location: {location}
- Season: {season}
- Current Date: {datetime.now().strftime('%B %d, %Y')}
{risk_context}

REQUIREMENTS:
1. Provide exactly 3-4 specific, actionable alternatives
2. Consider the season, location, and weather context
3. Make suggestions practical, enjoyable, and realistic
4. Include both indoor and outdoor options when weather permits
5. Be creative but maintain feasibility
6. Consider local attractions and activities specific to Uruguay
7. Provide specific locations or venues when possible
8. Consider cost, accessibility, and time requirements

RESPONSE FORMAT: Return ONLY a valid JSON response with this exact structure:
{{
    "alternatives": [
        {{
            "title": "Specific activity name",
            "description": "Brief but detailed description of the activity",
            "type": "indoor/outdoor/mixed",
            "reason": "Why this is a good alternative for the weather conditions",
            "tips": "Practical tips for this activity",
            "location": "Specific location or venue (if applicable)",
            "duration": "Estimated time needed",
            "cost": "Free/Low/Medium/High"
        }}
    ]
}}

Focus on making the day enjoyable despite the weather conditions. Be specific, helpful, and consider the local context of Uruguay."""
        
        # Generate response with timeout
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
        except Exception as api_error:
            print(f"Gemini API call failed: {str(api_error)}")
            return {
                "success": False,
                "message": f"Gemini API call failed: {str(api_error)}",
                "alternatives": []
            }
        
        # Enhanced JSON parsing with better error handling
        try:
            response_text = response.text.strip()
            print(f"Gemini raw response: {response_text[:200]}...")  # Debug log
            
            # Clean the response text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Find JSON boundaries more robustly
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON structure found in response")
            
            json_text = response_text[start_idx:end_idx]
            plan_b_data = json.loads(json_text)
            
            # Validate the response structure
            alternatives = plan_b_data.get('alternatives', [])
            if not isinstance(alternatives, list) or len(alternatives) == 0:
                raise ValueError("No alternatives found in response")
            
            # Ensure each alternative has required fields
            validated_alternatives = []
            for alt in alternatives:
                if isinstance(alt, dict) and alt.get('title'):
                    validated_alt = {
                        'title': alt.get('title', 'Activity'),
                        'description': alt.get('description', 'No description available'),
                        'type': alt.get('type', 'mixed'),
                        'reason': alt.get('reason', 'Good alternative for current conditions'),
                        'tips': alt.get('tips', 'Enjoy your activity!'),
                        'location': alt.get('location', 'Various locations available'),
                        'duration': alt.get('duration', '1-3 hours'),
                        'cost': alt.get('cost', 'Varies')
                    }
                    validated_alternatives.append(validated_alt)
            
            if len(validated_alternatives) == 0:
                raise ValueError("No valid alternatives found after validation")
            
            return {
            "success": True,
                "message": f"Generated {len(validated_alternatives)} Plan B alternatives using Gemini AI",
                "alternatives": validated_alternatives,
                "ai_model": "Gemini 2.0 Flash",
                "generated_at": datetime.now().isoformat(),
                "context": {
                    "activity": activity,
                    "weather_condition": weather_condition,
                    "risk_level": risk_level,
                    "location": location,
                    "season": season
                }
            }
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing failed: {str(e)}")
            # Enhanced fallback parsing
            alternatives = parse_fallback_response(response.text)
            
            if len(alternatives) > 0:
                return {
                    "success": True,
                    "message": f"Generated {len(alternatives)} Plan B alternatives using Gemini AI (fallback parsing)",
                    "alternatives": alternatives,
                    "ai_model": "Gemini 2.0 Flash (Fallback)",
                    "generated_at": datetime.now().isoformat(),
                    "warning": "Response parsing used fallback method"
                }
            else:
                raise ValueError("Failed to parse response and no alternatives found")
        
    except Exception as e:
        print(f"Error generating Plan B with Gemini: {str(e)}")
        return {
            "success": False,
            "message": f"Error generating Plan B: {str(e)}",
            "alternatives": [],
            "error_type": type(e).__name__
        }


if __name__ == "__main__":
    # Run verification when script is executed directly
    # verify_data_source()  # COMENTADO: función eliminada
    pass