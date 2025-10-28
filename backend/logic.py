"""
The Parade Planner - Core Logic Module
NASA Space Apps Challenge MVP
Enhanced with NASA POWER API integration
"""

# =============================================================================
# IMPORTS Y CONFIGURACIÓN
# =============================================================================
# Importación de todas las librerías necesarias y configuración inicial
# del sistema de logging y variables globales.

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
import os
import logging

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

# =============================================================================
# CONEXIÓN NASA POWER API
# =============================================================================
# Esta sección maneja toda la integración con la NASA POWER API, incluyendo
# validación de coordenadas, fetch de datos climáticos, manejo de errores,
# reintentos automáticos y sistema de fallback con datos locales de Montevideo.

def load_fallback_data(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Carga datos de fallback desde el archivo CSV de Montevideo cuando la NASA API no está disponible.
    
    Args:
        start_year: Año inicial para el rango de datos
        end_year: Año final para el rango de datos
        
    Returns:
        pd.DataFrame: DataFrame con datos de fallback de Montevideo
    """
    # Validar años antes de intentar cargar
    if start_year > end_year:
        logger.error(f"Invalid year range: start_year ({start_year}) > end_year ({end_year})")
        return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])
    
    try:
        logger.info(f"Attempting to load fallback data for years {start_year}-{end_year}")
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

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Valida que las coordenadas estén dentro de rangos geográficos válidos globalmente.
    
    La NASA POWER API puede obtener datos de cualquier lugar del mundo, por lo que
    esta validación solo verifica que las coordenadas estén dentro de rangos
    geográficos válidos (no fuera de la Tierra).

    Args:
        lat: Latitud en grados decimales (-90 a 90)
        lon: Longitud en grados decimales (-180 a 180)
        
    Returns:
        bool: True si las coordenadas son válidas globalmente
        
    Raises:
        ValueError: Si las coordenadas están fuera de rangos geográficos válidos
    """
    # Rangos geográficos válidos globalmente
    LAT_MIN, LAT_MAX = -90.0, 90.0
    LON_MIN, LON_MAX = -180.0, 180.0
    
    if not (LAT_MIN <= lat <= LAT_MAX):
        raise ValueError(f"Latitud {lat} fuera del rango válido global [{LAT_MIN}, {LAT_MAX}]")
    
    if not (LON_MIN <= lon <= LON_MAX):
        raise ValueError(f"Longitud {lon} fuera del rango válido global [{LON_MIN}, {LON_MAX}]")
    
    logger.info(f"Coordenadas validadas globalmente: ({lat}, {lon})")
    return True

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
        # Validar coordenadas al inicio
        validate_coordinates(lat, lon)
        
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
            logger.error("No response received from NASA API after all retries")
            logger.info("Falling back to Montevideo data due to no response")
            return load_fallback_data(start_year, end_year)
            
        # Parse de la respuesta JSON de la NASA con manejo de errores específico
        logger.info("Parsing JSON response from NASA POWER API...")
        try:
            data = response.json()
            logger.info("JSON response parsed successfully")
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.info("Falling back to Montevideo data due to JSON parsing error")
            return load_fallback_data(start_year, end_year)
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            logger.info("Falling back to Montevideo data due to parsing error")
            return load_fallback_data(start_year, end_year)
        
        # Validación de la estructura de respuesta de la API
        logger.info("Validating API response structure...")
        
        # Verificar mensajes de error de la API
        if 'messages' in data and data['messages'] and len(data['messages']) > 0:
            logger.error(f"NASA API returned error messages: {data['messages']}")
            logger.info("Falling back to Montevideo data due to API error messages")
            return load_fallback_data(start_year, end_year)
            
        # Verificar estructura de datos requerida
        if 'properties' not in data:
            logger.error(f"Missing 'properties' key in API response. Available keys: {list(data.keys())}")
            logger.info("Falling back to Montevideo data due to missing properties")
            return load_fallback_data(start_year, end_year)
            
        if 'parameter' not in data['properties']:
            logger.error(f"Missing 'parameter' key in API properties. Available keys: {list(data['properties'].keys())}")
            logger.info("Falling back to Montevideo data due to missing parameter data")
            return load_fallback_data(start_year, end_year)
        
        parameters = data['properties']['parameter']
        logger.info(f"Available parameters in response: {list(parameters.keys())}")
        
        # Extracción de datos específicos: T2M_MAX, T2M_MIN, T2M (temperaturas) y PRECTOTCORR (precipitación)
        logger.info("Extracting climate data from API response...")
        temp_max_data = parameters.get('T2M_MAX', {})
        temp_min_data = parameters.get('T2M_MIN', {})
        temp_avg_data = parameters.get('T2M', {})
        precip_data = parameters.get('PRECTOTCORR', {})
        
        # Validar que todos los datos requeridos estén presentes
        missing_params = []
        if not temp_max_data:
            missing_params.append('T2M_MAX')
        if not temp_min_data:
            missing_params.append('T2M_MIN')
        if not temp_avg_data:
            missing_params.append('T2M')
        if not precip_data:
            missing_params.append('PRECTOTCORR')
            
        if missing_params:
            logger.error(f"Missing climate parameters in API response: {missing_params}")
            logger.info("Falling back to Montevideo data due to missing climate parameters")
            return load_fallback_data(start_year, end_year)
            
        logger.info("All required climate parameters found in API response")
            
        # Conversión de datos JSON a DataFrame de Pandas con logging detallado
        logger.info("Converting JSON data to DataFrame...")
        records = []
        total_dates = len(temp_max_data)
        processed_dates = 0
        skipped_dates = 0
        
        for date_str, temp_max_value in temp_max_data.items():
            if date_str in temp_min_data and date_str in temp_avg_data and date_str in precip_data:
                try:
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
                    processed_dates += 1
                    
                except ValueError as e:
                    logger.warning(f"Error parsing date {date_str}: {str(e)}")
                    skipped_dates += 1
            else:
                skipped_dates += 1
        
        logger.info(f"Data conversion completed: {processed_dates} dates processed, {skipped_dates} dates skipped")
        
        if not records:
            logger.error("No valid data records found in API response")
            logger.info("Falling back to Montevideo data due to empty data records")
            return load_fallback_data(start_year, end_year)
        
        # Creación del DataFrame final
        logger.info("Creating final DataFrame...")
        df = pd.DataFrame(records)
        
        # Limpieza de datos: eliminación de filas con valores nulos
        initial_count = len(df)
        df = df.dropna()
        final_count = len(df)
        removed_count = initial_count - final_count
        
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} records with missing values (from {initial_count} to {final_count})")
        
        # Ordenamiento por año y mes para análisis temporal
        df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        # Validación final de datos
        if len(df) == 0:
            logger.error("DataFrame is empty after processing")
            logger.info("Falling back to Montevideo data due to empty DataFrame")
            return load_fallback_data(start_year, end_year)
        
        # Logging de estadísticas finales
        logger.info(f"Successfully fetched {len(df)} records from NASA POWER API")
        logger.info(f"Date range: {df['Year'].min()}-{df['Month'].min():02d} to {df['Year'].max()}-{df['Month'].max():02d}")
        logger.info(f"Temperature range: {df['Max_Temperature_C'].min():.1f}C to {df['Max_Temperature_C'].max():.1f}C")
        logger.info(f"Precipitation range: {df['Precipitation_mm'].min():.1f}mm to {df['Precipitation_mm'].max():.1f}mm")
        
        return df
        
    except ValueError as e:
        # Error de validación de coordenadas
        logger.error(f"Coordinate validation error: {str(e)}")
        logger.info("Falling back to Montevideo data due to coordinate validation error")
        return load_fallback_data(start_year, end_year)
        
    except requests.exceptions.RequestException as e:
        # Errores específicos de requests
        logger.error(f"Request error: {str(e)}")
        logger.info("Falling back to Montevideo data due to request error")
        return load_fallback_data(start_year, end_year)
        
    except Exception as e:
        # Manejo de errores inesperados: retorna datos de fallback en lugar de DataFrame vacío
        logger.error(f"Unexpected error fetching or processing NASA POWER data: {str(e)}")
        logger.info("Falling back to Montevideo data due to unexpected error")
        return load_fallback_data(start_year, end_year)

# =============================================================================
# CÁLCULOS DE RIESGO CLIMÁTICO
# =============================================================================
# Esta sección implementa la metodología P90 (percentil 90) para calcular
# probabilidades de condiciones climáticas adversas. Incluye análisis de
# riesgo de calor extremo, precipitación y frío estacional.

def filter_data_by_month(historical_data: pd.DataFrame, target_month: int) -> pd.DataFrame:
    """
    Filter historical data to include only records from the target month
    
    Args:
        historical_data: DataFrame with historical climate data (20 years)
        target_month: Target month (1-12) to filter data for
        
    Returns:
        DataFrame filtered to the target month (monthly data for analysis)
    """
    if historical_data.empty:
        logger.warning("Empty historical data provided to filter_data_by_month")
        return historical_data
    
    if 'Month' not in historical_data.columns:
        logger.warning("No 'Month' column in historical data, returning original data")
        return historical_data
    
    # Filter data for the target month
    monthly_data = historical_data[historical_data['Month'] == target_month].copy()
    
    logger.info(f"Filtered data for month {target_month}: {len(monthly_data)} records")
    
    return monthly_data

def calculate_heat_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate heat risk using P90 methodology on Max_Temperature_C
    """
    # Validación inicial
    if monthly_data.empty or 'Max_Temperature_C' not in monthly_data.columns:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filtrar valores inválidos
    valid_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    if len(valid_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid temperature data",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Calcular threshold usando P90
    risk_threshold = np.percentile(valid_data['Max_Temperature_C'], 90)
    
    # Contar eventos adversos (días > threshold)
    adverse_events = valid_data[valid_data['Max_Temperature_C'] > risk_threshold]
    total_observations = len(valid_data)
    adverse_count = len(adverse_events)
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Determinar nivel de riesgo
    if probability >= 20:
        risk_level = "HIGH"
    elif probability >= 10:
        risk_level = "MODERATE"
    elif probability >= 5:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    # Mensaje personalizado
    if risk_threshold >= 30.0:
        status_message = f"🚨 HIGH RISK of extreme heat! P90 Threshold: {risk_threshold:.1f}°C."
    elif risk_threshold >= 25.0:
        status_message = f"⚠️ MODERATE RISK of warm weather. P90 Threshold: {risk_threshold:.1f}°C."
    else:
        status_message = f"☀️ LOW RISK of extreme heat. P90 Threshold: {risk_threshold:.1f}°C."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }

def calculate_precipitation_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate precipitation risk using P90 methodology on Precipitation_mm
    """
    # Validación inicial
    if monthly_data.empty or 'Precipitation_mm' not in monthly_data.columns:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filtrar valores inválidos (NASA usa >= 0 para precipitation)
    valid_data = monthly_data[monthly_data['Precipitation_mm'] >= 0]
    if len(valid_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid precipitation data",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Usar threshold fijo de 5mm (precipitación significativa)
    risk_threshold = 5.0
    
    # Contar eventos adversos (días con precipitation > threshold)
    adverse_events = valid_data[valid_data['Precipitation_mm'] > risk_threshold]
    total_observations = len(valid_data)
    adverse_count = len(adverse_events)
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Determinar nivel de riesgo
    if probability >= 20:
        risk_level = "HIGH"
    elif probability >= 10:
        risk_level = "MODERATE"
    elif probability >= 5:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    # Mensaje personalizado
    if probability >= 20:
        status_message = "🌧️ HIGH RISK of heavy precipitation. Consider indoor alternatives."
    elif probability >= 10:
        status_message = "🌦️ MODERATE RISK of rain. Bring umbrella."
    elif probability >= 5:
        status_message = "🌤️ LOW RISK of precipitation. Light rain possible."
    else:
        status_message = "☀️ MINIMAL RISK of rain. Dry conditions expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }

def calculate_cold_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate cold weather risk using P10 methodology on Max_Temperature_C
    """
    # Validación inicial
    if monthly_data.empty or 'Max_Temperature_C' not in monthly_data.columns:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filtrar valores inválidos
    valid_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    if len(valid_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid temperature data",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Calcular threshold usando P10
    risk_threshold = np.percentile(valid_data['Max_Temperature_C'], 10)
    
    # Contar eventos adversos (días < threshold)
    adverse_events = valid_data[valid_data['Max_Temperature_C'] < risk_threshold]
    total_observations = len(valid_data)
    adverse_count = len(adverse_events)
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Determinar nivel de riesgo
    if probability >= 20:
        risk_level = "HIGH"
    elif probability >= 10:
        risk_level = "MODERATE"
    elif probability >= 5:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    # Mensaje personalizado
    if probability >= 20:
        status_message = "🧊 HIGH RISK of cold weather. Consider warmer dates or indoor alternatives!"
    elif probability >= 10:
        status_message = "❄️ MODERATE RISK of cold weather. Dress warmly!"
    elif probability >= 5:
        status_message = "🌤️ LOW RISK of cold weather. Light jacket recommended."
    else:
        status_message = "☀️ MINIMAL RISK of cold weather. Comfortable temperatures expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }

def calculate_weather_risk(historical_data: pd.DataFrame, risk_type: str, target_month: int) -> Dict[str, Any]:
    """
    Unified weather risk calculation function that handles all three risk types.
    Filters data by target month before calculating risk.
    
    Args:
        historical_data: DataFrame with historical weather data (20 years)
        risk_type: Type of risk to calculate ("heat" | "cold" | "precipitation")
        target_month: Target month (1-12) for the event date
        
    Returns:
        Dict with risk analysis results
    """
    logger.info(f"Calculating {risk_type} risk for target month {target_month}")
    logger.info(f"Historical data: {len(historical_data)} total records")
    
    if risk_type not in ["heat", "cold", "precipitation"]:
        logger.error(f"Invalid risk_type: {risk_type}")
        raise ValueError(f"Invalid risk_type: {risk_type}. Must be 'heat', 'cold', or 'precipitation'")
    
    # Filter data by target month to get "monthly data"
    monthly_data = filter_data_by_month(historical_data, target_month)
    logger.info(f"Monthly data after filtering: {len(monthly_data)} records for month {target_month}")
    
    # Calculate the specific risk type
    if risk_type == "heat":
        logger.info("Calculating heat risk using P90 methodology")
        result = calculate_heat_risk(monthly_data)
        logger.info(f"Heat risk calculated: probability={result['probability']}%, level={result['risk_level']}")
        return result
    elif risk_type == "cold":
        logger.info("Calculating cold risk using P10 methodology")
        result = calculate_cold_risk(monthly_data)
        logger.info(f"Cold risk calculated: probability={result['probability']}%, level={result['risk_level']}")
        return result
    elif risk_type == "precipitation":
        logger.info("Calculating precipitation risk using threshold methodology")
        result = calculate_precipitation_risk(monthly_data)
        logger.info(f"Precipitation risk calculated: probability={result['probability']}%, level={result['risk_level']}")
        return result

# =============================================================================
# ANÁLISIS DE TENDENCIAS CLIMÁTICAS
# =============================================================================
# Esta sección analiza tendencias de cambio climático a largo plazo,
# comparando datos recientes con promedios históricos para detectar
# patrones de cambio en las condiciones climáticas.

def analyze_climate_change_trend(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Análisis de tendencias climáticas basado en metodología IPCC/WMO.
    
    Esta función implementa un análisis científico de tendencias climáticas que compara
    las temperaturas promedio de los primeros 5 años del dataset con los últimos 5 años.
    Esta metodología es estándar en climatología y está validada por IPCC y WMO.
    
    Metodología científica:
    1. Identifica los primeros 5 años del dataset (período inicial)
    2. Identifica los últimos 5 años del dataset (período reciente)
    3. Calcula el promedio de T2M (temperatura promedio diaria) para cada período
    4. Compara las diferencias usando umbrales científicos estándar
    
    Clasificación basada en umbrales IPCC/WMO:
    - SIGNIFICANT_WARMING: Diferencia >= 1.0°C (IPCC: calentamiento significativo)
    - WARMING_TREND: Diferencia >= 0.5°C (WMO: cambio estadísticamente detectable)
    - COOLING_TREND: Diferencia <= -0.5°C (WMO: cambio estadísticamente detectable)
    - STABLE: Diferencia < 0.5°C (variabilidad natural del clima)
    
    Args:
        monthly_data: DataFrame con datos históricos del mes específico (20 años)
        
    Returns:
        Dict con análisis de tendencia climática:
            - trend_status: Estado de la tendencia (SIGNIFICANT_WARMING, etc.)
            - early_period_mean: Temperatura promedio del período inicial en Celsius
            - recent_period_mean: Temperatura promedio del período reciente en Celsius
            - difference: Diferencia entre períodos reciente e inicial en Celsius
            - early_years: Lista de años del período inicial
            - recent_years: Lista de años del período reciente
            - message: Mensaje descriptivo de la tendencia
            - methodology: Metodología científica utilizada
            - data_period: Período total de datos analizados
    """
    if monthly_data.empty:
        return {
            'trend_status': 'UNKNOWN',
            'early_period_mean': 0.0,
            'recent_period_mean': 0.0,
            'difference': 0.0,
            'early_years': [],
            'recent_years': [],
            'message': "No data available for trend analysis.",
            'methodology': 'IPCC/WMO standard analysis',
            'data_period': 'No data'
        }

    # Obtener años únicos ordenados
    unique_years = sorted(monthly_data['Year'].unique())
    total_years = len(unique_years)
    
    # Validación científica: WMO requiere mínimo 10 años para análisis robusto
    if total_years < 10:
        return {
            'trend_status': 'INSUFFICIENT_DATA',
            'early_period_mean': 0.0,
            'recent_period_mean': 0.0,
            'difference': 0.0,
            'early_years': [],
            'recent_years': [],
            'message': f"Insufficient data: WMO requires minimum 10 years, got {total_years} years.",
            'methodology': 'IPCC/WMO standard analysis',
            'data_period': f"{total_years} years"
        }
    
    # Períodos científicos: primeros 5 años vs últimos 5 años (metodología IPCC/WMO fija)
    comparison_years = 5  # Metodología IPCC/WMO estándar: comparar primeros 5 vs últimos 5 años
    early_years = unique_years[:comparison_years]      # Primeros 5 años
    recent_years = unique_years[-comparison_years:]     # Últimos 5 años
    
    # Filtrar datos por períodos
    early_data = monthly_data[monthly_data['Year'].isin(early_years)]
    recent_data = monthly_data[monthly_data['Year'].isin(recent_years)]
    
    # Variable científica: T2M (temperatura promedio diaria) - estándar IPCC
    early_period_mean = early_data['Avg_Temperature_C'].mean()
    recent_period_mean = recent_data['Avg_Temperature_C'].mean()
    difference = recent_period_mean - early_period_mean
    
    # Clasificación basada en umbrales científicos IPCC/WMO
    if difference >= 1.0:  # IPCC: Calentamiento significativo
        trend_status = 'SIGNIFICANT_WARMING'
        message = f"🔴 SIGNIFICANT WARMING: +{difference:.2f}°C over {total_years} years. IPCC threshold exceeded - climate change is worsening heat risk."
    elif difference >= 0.5:  # WMO: Tendencia detectable
        trend_status = 'WARMING_TREND'
        message = f"🟠 WARMING TREND: +{difference:.2f}°C over {total_years} years. Statistically significant warming detected - heat risk is increasing."
    elif difference <= -0.5:  # WMO: Enfriamiento detectable
        trend_status = 'COOLING_TREND'
        message = f"🔵 COOLING TREND: {difference:.2f}°C over {total_years} years. Statistically significant cooling detected - heat risk is decreasing."
    else:  # Variabilidad natural del clima
        trend_status = 'STABLE'
        message = f"🟢 STABLE CLIMATE: {difference:+.2f}°C over {total_years} years. Within natural climate variability - heat risk remains stable."

    return {
        'trend_status': trend_status,
        'early_period_mean': round(early_period_mean, 2),
        'recent_period_mean': round(recent_period_mean, 2),
        'difference': round(difference, 2),
        'early_years': early_years,
        'recent_years': recent_years,
        'message': message,
        'methodology': 'IPCC/WMO standard analysis',
        'data_period': f"{total_years} years ({unique_years[0]}-{unique_years[-1]})"
    }

# =============================================================================
# INTEGRACIÓN GEMINI AI 
# =============================================================================
# Funciones auxiliares para el manejo de respuestas de Gemini AI

def calculate_season_from_month(month: int, latitude: float = None) -> str:
    """
    Calculate season from month (1-12) based on hemisphere from coordinates.
    Uses global climatological standard based on meteorological seasons.
    
    Args:
        month: Month number (1-12)
        latitude: Latitude coordinate to determine hemisphere (optional)
        
    Returns:
        Season name (Summer, Autumn, Winter, Spring)
    """
    # If no latitude provided, assume Southern Hemisphere by default
    is_northern_hemisphere = latitude is not None and latitude > 0
    
    if is_northern_hemisphere:
        # Northern Hemisphere seasons
        if month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Autumn"
        elif month in [12, 1, 2]:
            return "Winter"
        else:  # 3, 4, 5
            return "Spring"
    else:
        # Southern Hemisphere seasons (default)
        if month in [12, 1, 2]:
            return "Summer"
        elif month in [3, 4, 5]:
            return "Autumn"
        elif month in [6, 7, 8]:
            return "Winter"
        else:  # 9, 10, 11
            return "Spring"

def generate_plan_b_with_gemini(
    activity: str,
    adverse_condition: str,
    risk_analysis: Dict[str, Any],
    location: str = "Montevideo, Uruguay",
    target_month: int = 1,
    latitude: float = None
) -> Dict[str, Any]:
    """
    Generate intelligent Plan B suggestions using Gemini AI with context from risk_analysis.
    
    Args:
        activity: Type of activity (beach, picnic, running, etc.)
        adverse_condition: Weather condition causing the risk (cold, hot, rainy, etc.)
        risk_analysis: Complete risk analysis result from calculate_weather_risk()
        location: Location name for context
        target_month: Target month for the event (1-12)
        latitude: Latitude coordinate to calculate season correctly by hemisphere
        
    Returns:
        Dict with Plan B suggestions
    """
    if not GEMINI_AVAILABLE:
        # Raise exception to trigger fallback in api.py
        raise ValueError("Gemini AI not available. Fallback will be used.")
    
    try:
        # Calculate season from target month based on hemisphere
        season = calculate_season_from_month(target_month, latitude)
        
        # Extract data from risk_analysis
        risk_level = risk_analysis.get('risk_level', 'MODERATE')
        risk_probability = risk_analysis.get('probability', 0.0)
        risk_threshold = risk_analysis.get('risk_threshold', 0.0)
        risk_message = risk_analysis.get('status_message', '')
        
        # Configure Gemini API with better error handling
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # Raise exception to trigger fallback in api.py
            raise ValueError("Gemini API key not configured. Fallback will be used.")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Enhanced context-aware prompt with risk probabilities
        risk_context = f"- Risk Level: {risk_level}\n"
        risk_context += f"- Risk Probability: {risk_probability:.1f}%\n"
        if 'threshold' in risk_analysis:
            risk_context += f"- Risk Threshold: {risk_threshold:.1f}\n"
        risk_context += f"- Risk Message: {risk_message}\n"
        
        # Create enhanced prompt with better structure
        prompt = f"""You are an expert weather planning assistant for {location}. Generate intelligent alternatives compatible with weather conditions when they are unfavorable.

CONTEXT:
- Weather Condition: {adverse_condition}
- Location: {location}
- Season: {season}
- Target Month: {target_month}
- Current Date: {datetime.now().strftime('%B %d, %Y')}
{risk_context}

REQUIREMENTS:
1. Provide exactly 3-4 specific, actionable activities compatible with the weather conditions
2. Focus on activities that work well despite {adverse_condition} conditions
3. Consider the season, location, and weather context
4. Make suggestions practical, enjoyable, and realistic
5. Include both indoor and outdoor options when weather permits
6. Be creative but maintain feasibility
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
                    "adverse_condition": adverse_condition,
                    "risk_level": risk_level,
                    "location": location,
                    "season": season,
                    "target_month": target_month
                }
            }
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"⚠️ Gemini AI response parsing failed: {str(e)}")
            logger.info("🔄 Falling back to predefined alternatives due to parsing error")
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Error generating Plan B with Gemini: {str(e)}")
        logger.info("🔄 Falling back to predefined alternatives due to Gemini error")
        raise  # Re-lanzar para que api.py active el fallback


def generate_fallback_plan_b(
    activity: str,
    adverse_condition: str,
    risk_level: str,
    location: str = "Montevideo, Uruguay",
    target_month: int = 1,
    latitude: float = None
) -> Dict[str, Any]:
    """
    Generate fallback Plan B suggestions when Gemini is not available.
    
    This function is activated automatically when:
    - Gemini AI API is unavailable
    - Gemini response parsing fails
    - Any error occurs during Gemini processing
    
    Logs are automatically generated to track when fallback mode is used.
    
    Args:
        activity: Type of activity
        adverse_condition: Weather condition causing the risk
        risk_level: Risk level (HIGH, MODERATE, LOW, MINIMAL)
        location: Location name for context
        target_month: Target month for the event (1-12)
        latitude: Latitude coordinate to calculate season
        
    Returns:
        Dict with Plan B alternatives
    """
    # Calculate season from coordinates
    season = calculate_season_from_month(target_month, latitude)
    
    logger.warning("[FALLBACK MODE] Using predefined alternatives (Gemini AI unavailable)")
    logger.info(f"Activity: {activity}, Condition: {adverse_condition}, Risk: {risk_level}, Season: {season}")
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
    
    # Get alternatives for the specific condition (activity-independent)
    alternatives = []
    
    # For each activity type, get relevant alternatives for the adverse condition
    for activity_type, activity_data in fallback_alternatives.items():
        if adverse_condition in activity_data:
            alternatives.extend(activity_data[adverse_condition])
    
    # If no alternatives found, provide general ones based on condition
    if not alternatives:
        general_alternatives = {
            "very hot": [
                {
                    "title": "Museo Torres García",
                    "description": "Explore Uruguayan art in an air-conditioned museum",
                    "type": "indoor",
                    "reason": "Cultural experience in cool environment",
                    "tips": "Check current exhibitions and guided tour schedules",
                    "location": "Sarandí 683, Montevideo",
                    "duration": "2-3 hours",
                    "cost": "Low"
                },
                {
                    "title": "Shopping Center",
                    "description": "Visit Punta Carretas Shopping for shopping and dining",
                    "type": "indoor",
                    "reason": "Climate-controlled environment perfect for hot days",
                    "tips": "Check for special events or sales, bring comfortable shoes",
                    "location": "Punta Carretas, Montevideo",
                    "duration": "3-4 hours",
                    "cost": "Medium"
                }
            ],
            "very cold": [
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
                    "title": "Mercado del Puerto",
                    "description": "Visit food market and try Uruguayan barbecue",
                    "type": "indoor",
                    "reason": "Food experience in warm environment",
                    "tips": "Try traditional parrillada and local wines",
                    "location": "Mercado del Puerto, Montevideo",
                    "duration": "2-3 hours",
                    "cost": "Medium"
                }
            ],
            "very rainy": [
                {
                    "title": "Cinema Theater",
                    "description": "Watch latest movies in air-conditioned theaters",
                    "type": "indoor",
                    "reason": "Perfect rainy day entertainment",
                    "tips": "Book tickets in advance for popular shows",
                    "location": "Various locations, Montevideo",
                    "duration": "2-3 hours",
                    "cost": "Low"
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
            ]
        }
        
        alternatives = general_alternatives.get(adverse_condition, [
            {
                "title": "Museo Nacional de Artes Visuales",
                "description": "Explore Uruguayan art and culture",
                "type": "indoor",
                "reason": "Cultural experience regardless of weather",
                "tips": "Check current exhibitions and opening hours",
                "location": "Montevideo, Uruguay",
                "duration": "2-3 hours",
                "cost": "Low"
            }
        ])
    
    logger.info(f"Fallback Plan B generated {len(alternatives)} alternatives")
    
    return {
        "success": True,
        "message": f"Generated {len(alternatives)} Plan B alternatives (fallback mode)",
        "alternatives": alternatives,
        "ai_model": "Fallback System",
        "generated_at": datetime.now().isoformat()
    }


# =============================================================================
# UTILIDADES Y VALIDACIONES
# =============================================================================
# Esta sección contiene funciones auxiliares, validaciones de datos,
# funciones de prueba y el punto de entrada del script.

if __name__ == "__main__":
    # Run verification when script is executed directly
    pass