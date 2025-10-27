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
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Plan B generation will be disabled.")

def get_climate_trend_data(historical_data: pd.DataFrame) -> Dict[str, Any]:
# =============================================================================
# CONEXIÓN NASA POWER API
# =============================================================================
# Esta sección maneja toda la integración con la NASA POWER API, incluyendo
# validación de coordenadas, fetch de datos climáticos, manejo de errores,
# reintentos automáticos y sistema de fallback con datos locales de Montevideo.

def load_fallback_data(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Calcula el Percentil 90 (P90) de la temperatura máxima para cada año y genera los datos necesarios para los gráficos de Plotly.
    Implementa granularidad correcta para datos de la NASA API.
    
    Args:
        historical_data: DataFrame con datos históricos de temperatura.
        
    Returns:
        Dict: Contiene 'plot_data' (P90 por año) y 'climate_trend' (resumen).
    """
    if historical_data.empty:
        return {
            "plot_data": [],
            "climate_trend": "No se encontraron datos históricos suficientes para realizar el análisis de tendencia climática (P90 anual)."
        }
    
    # Filtrar datos válidos (NASA usa -999 para datos faltantes)
    valid_data = historical_data[historical_data['Max_Temperature_C'] > -100].copy()
    
    if valid_data.empty:
        return {
            "plot_data": [],
            "climate_trend": "No se encontraron datos de temperatura válidos para el análisis P90."
        }
    
    # Calcular P90 por año con granularidad correcta
    # Agrupar por año y calcular el percentil 90 de las temperaturas máximas diarias
    p90_by_year = valid_data.groupby('Year')['Max_Temperature_C'].quantile(0.90).reset_index()
    p90_by_year.rename(columns={'Max_Temperature_C': 'P90_Max_Temp'}, inplace=True)
    
    # Calcular también estadísticas adicionales para mejor visualización
    stats_by_year = valid_data.groupby('Year')['Max_Temperature_C'].agg([
        'mean', 'max', 'min', 'std'
    ]).reset_index()
    stats_by_year.columns = ['Year', 'Mean_Temp', 'Max_Temp', 'Min_Temp', 'Std_Temp']
    
    # Combinar datos P90 con estadísticas
    plot_data = p90_by_year.merge(stats_by_year, on='Year', how='left')
    plot_data = plot_data.to_dict('records')
    
    # Análisis de tendencias climáticas
    if len(p90_by_year) >= 2:
        # Calcular la diferencia entre el P90 del último año y el primer año
        start_p90 = p90_by_year.iloc[0]['P90_Max_Temp']
        end_p90 = p90_by_year.iloc[-1]['P90_Max_Temp']
        trend_diff = end_p90 - start_p90
        
        start_year = p90_by_year.iloc[0]['Year']
        end_year = p90_by_year.iloc[-1]['Year']
        
        # Calcular tendencia de la media también
        start_mean = stats_by_year.iloc[0]['Mean_Temp']
        end_mean = stats_by_year.iloc[-1]['Mean_Temp']
        mean_trend_diff = end_mean - start_mean
        
        if trend_diff > 1.0:
            trend_summary = f"ALARMA: El umbral de calor extremo (P90) ha aumentado en {trend_diff:.2f}°C entre {start_year} y {end_year}. La temperatura media también aumentó {mean_trend_diff:.2f}°C. Esto sugiere una clara tendencia al aumento de temperaturas extremas."
        elif trend_diff > 0.3:
            trend_summary = f"Advertencia: El umbral de calor extremo (P90) ha aumentado ligeramente en {trend_diff:.2f}°C entre {start_year} y {end_year}. La temperatura media cambió {mean_trend_diff:.2f}°C. Se recomienda monitoreo continuo."
        else:
            trend_summary = f"Estable: El umbral de calor extremo (P90) se ha mantenido relativamente estable, con una variación de {trend_diff:.2f}°C entre {start_year} y {end_year}. La temperatura media cambió {mean_trend_diff:.2f}°C."
    else:
        trend_summary = "Datos insuficientes (menos de 2 años) para calcular una tendencia climática anual significativa."

    return {
        "plot_data": plot_data,
        "climate_trend": trend_summary
    }


def load_historical_data_by_date(lat: float, lon: float, date_str: str) -> pd.DataFrame:
    """
    Carga los datos históricos del mes de interés.

    Args:
        lat: Latitud.
        lon: Longitud.
        date_str: Fecha en formato YYYY-MM-DD.
        
    Returns:
        pd.DataFrame: DataFrame de Pandas con datos históricos del mes.
    """
    try:
        # Extraer el mes
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month = date_obj.month
        
        print(f"FastAPI Processing: Month={month}")
        
        # 1. Llamar a la función de obtención de datos (asumiendo 20 años de historia)
        start_year = 2005
        end_year = date_obj.year # Hasta el año actual
        print(f"Fetching NASA POWER data for coordinates ({lat}, {lon}) from {start_year} to {end_year}")

        # La función fetch_nasa_power_data debe retornar un DF en caso de éxito
        historical_data_full = fetch_nasa_power_data(lat, lon, start_year, end_year)
        
        if historical_data_full.empty:
             print("NASA POWER API returned empty DataFrame.")
             return pd.DataFrame() # Devuelve un DF vacío si no hay datos

        # 2. Filtrar los datos solo para el mes de interés
        monthly_data = historical_data_full[historical_data_full['Month'] == month]

        if monthly_data.empty:
            print(f"Error in load_historical_data: No data found for month {month}")
            return pd.DataFrame() # Devuelve un DF vacío si no hay datos para ese mes
        
        return monthly_data
        
    except Exception as e:
        print(f"FastAPI Error in Load: {str(e)}")
        # Define las columnas para que api.py sepa que es un DataFrame
        return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'])
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
    Fetch historical weather data from NASA POWER API
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate  
        start_year: Start year for data (e.g., 2004)
        end_year: End year for data (e.g., 2024)
        
    Returns:
        pd.DataFrame: DataFrame with columns 'Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'
    """
    # Define el DataFrame vacío de fallback
    empty_df = pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'])
    
    try:
        # Construct the NASA POWER API URL
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Format dates as YYYYMMDD
        start_date = f"{start_year}0101" 
        end_date = f"{end_year}1231" 
        
        # API parameters
        params = {
            'parameters': 'T2M_MAX,PRECTOTCORR',
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        print(f"Fetching NASA POWER data for coordinates ({lat}, {lon}) from {start_year} to {end_year}")
        
        # Make API request with timeout and retry logic
        max_retries = 3
        response = None # Inicializar response
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch NASA POWER data after {max_retries} attempts: {str(e)}")
                    return empty_df # Retorna vacío después de fallar todos los reintentos
                print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
        
        if response is None:
            return empty_df # Asegura que si no hubo respuesta, se devuelve vacío
            
        # Parse JSON response
        data = response.json()
        
        # 🚨 CAMBIO CLAVE 1: Verificar si la respuesta JSON es un mensaje de error 🚨
        # Solo considerar error si hay mensajes de error específicos, no mensajes informativos
        if 'message' in data and 'error' in str(data['message']).lower():
            print(f"NASA API returned an error message: {data['message']}")
            return empty_df
            
        # Extract time series data - NASA POWER API structure
        if 'properties' not in data or 'parameter' not in data['properties']:
            # Esto atrapa el caso que ya tenías
            print("Invalid response format from NASA POWER API - no 'properties.parameter' key found")
            return empty_df
        
        parameters = data['properties']['parameter']
        
        # Extract T2M_MAX (Temperature Max) and PRECTOTCORR (Precipitation Total Corrected)
        temp_data = parameters.get('T2M_MAX', {})
        precip_data = parameters.get('PRECTOTCORR', {})
        
        if not temp_data or not precip_data:
            print("Temperature or precipitation data not found in API response")
            return empty_df
            
        # Convert to DataFrame
        records = []
        for date_str, temp_value in temp_data.items():
            if date_str in precip_data:
                # Parse date (format: YYYYMMDD)
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                
                temp_celsius = temp_value if temp_value is not None else None
                precip_mm = precip_data[date_str] if precip_data[date_str] is not None else None
                
                records.append({
                    'Year': date_obj.year,
                    'Month': date_obj.month,
                    'Max_Temperature_C': temp_celsius,
                    'Precipitation_mm': precip_mm
                })
        
        if not records:
            print("No valid data records found in API response")
            return empty_df
        
        df = pd.DataFrame(records)
        
        # Remove any rows with null values
        df = df.dropna()
        
        # Sort by year and month
        df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        print(f"Successfully fetched {len(df)} records from NASA POWER API")
        return df
        
    except Exception as e:
        # 🚨 CAMBIO CLAVE 2: En caso de cualquier error de procesamiento, retorna un DF vacío 🚨
        print(f"Fatal Error fetching or processing NASA POWER data: {str(e)}")
        # Ya no lanzamos 'raise Exception', devolvemos el DF vacío para que el código que llama no falle.
        return empty_df
def load_historical_data(lat: float, lon: float, date_str: str) -> Dict[str, Any]:
    """
    Load and filter historical data by month using NASA POWER API
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Dict: Dictionary containing the filtered DataFrame and the climate trend analysis.
    """
    try:
        # Extract month from date string
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month_filter = date_obj.month
        
        # Validate coordinates
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        # Fetch 20 years of data (2004-2024)
        current_year = datetime.now().year
        start_year = current_year - 20  # 20 years back
        end_year = current_year
        
        # Fetch data from NASA POWER API
        df = fetch_nasa_power_data(
            lat=lat,
            lon=lon,
            start_year=start_year,
            end_year=end_year
        )
        
        # Filter by the specified month
        monthly_data = df[df['Month'] == month_filter].copy()
        
        if monthly_data.empty:
            raise ValueError(f"No data found for month {month_filter}")
        
        print(f"Loaded {len(monthly_data)} records for month {month_filter} from NASA POWER API")
        climate_trend = analyze_climate_change_trend(monthly_data)
        return {
            'data': monthly_data,
            'climate_trend': climate_trend
        }
        
    except Exception as e:
        print(f"Error in load_historical_data: {str(e)}")
        # Return empty DataFrame instead of raising exception
        print("NASA POWER API failed - returning empty DataFrame")
        return {
            'data': pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm']),
            'climate_trend': analyze_climate_change_trend(pd.DataFrame())
        }


def calculate_adverse_probability(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate adverse weather probability based on temperature data"""
    if monthly_data.empty:
        raise ValueError("No data provided")
    
    if 'Max_Temperature_C' not in monthly_data.columns:
        raise ValueError("Temperature data not found")
    
    # Filter out invalid values (NASA uses -999 for missing data)
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
    risk_threshold = np.percentile(valid_temp_data['Max_Temperature_C'], 90) ###MAAAL
    
    
    # Count adverse events (days above the hot weather threshold)
    adverse_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] > risk_threshold]
    total_observations = len(valid_temp_data)
    adverse_count = len(adverse_events)
    
    # Calculate probability as percentage of days above threshold
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Generate status message
    if risk_threshold >= 30.0: # If the extreme temperature (P90) is 30C or more
        risk_level = "HIGH"
        status_message = f"🚨 HIGH RISK of extreme heat! P90 Threshold: {risk_threshold:.1f}°C. Extreme heat days expected to exceed this."
    elif risk_threshold >= 25.0: # If the extreme temperature (P90) is between 25C and 30C
        risk_level = "MODERATE"
        status_message = f"⚠️ MODERATE RISK of warm weather. P90 Threshold: {risk_threshold:.1f}°C. Warm weather expected on average."
    else:
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

def get_plot_data(monthly_data: pd.DataFrame) -> Dict[str, Any]:
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
    Get appropriate cold threshold based on season and activity type
    """
    seasonal_adjustments = {
        12: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        1: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        2: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        3: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        4: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0},
        5: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},
        6: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        7: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        8: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        9: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},
        10: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0},
        11: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
    }
    month_data = seasonal_adjustments.get(month, seasonal_adjustments[1])
    return month_data.get(activity, month_data["general"])


def calculate_weather_risk(monthly_data: pd.DataFrame, risk_type: str, activity: str = "general") -> Dict[str, Any]:
    """
    Unified weather risk calculation function that handles all three risk types
    
    Args:
        monthly_data: DataFrame with weather data
        risk_type: Type of risk to calculate ("heat" | "cold" | "precipitation")
        activity: Activity type (optional, used only for cold risk)
        
    Returns:
        Dict with risk analysis results
    """
    if risk_type not in ["heat", "cold", "precipitation"]:
        raise ValueError(f"Invalid risk_type: {risk_type}. Must be 'heat', 'cold', or 'precipitation'")
    
    if risk_type == "heat":
        return calculate_adverse_probability(monthly_data)
    elif risk_type == "cold":
        return calculate_cold_risk(monthly_data, activity)
    elif risk_type == "precipitation":
        return calculate_precipitation_risk(monthly_data)


def calculate_cold_risk(monthly_data: pd.DataFrame, activity: str = "general") -> Dict[str, Any]:
    """
    Calculate cold weather risk using seasonal and activity-aware methodology (10th Percentile)
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
    
    month = monthly_data['Month'].iloc[0] if not monthly_data.empty else 1
    cold_threshold = get_seasonal_cold_threshold(month, activity)
    cold_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] < cold_threshold]
    total_observations = len(monthly_data)
    cold_count = len(cold_events)
    probability = (cold_count / total_observations) * 100 if total_observations > 0 else 0
    
    season_names = {
        12: "Summer", 1: "Summer", 2: "Summer",
        3: "Autumn", 4: "Autumn", 5: "Autumn", 
        6: "Winter", 7: "Winter", 8: "Winter",
        9: "Spring", 10: "Spring", 11: "Spring"
    }
    season = season_names.get(month, "Unknown")
    
    if probability >= 20:
        risk_level = "HIGH"
        status_message = f"🧊 HIGH RISK of cold weather in {season}. Consider warmer dates or indoor alternatives!"
    elif probability >= 10:
        risk_level = "MODERATE"
        status_message = f"❄️ MODERATE RISK of cold weather in {season}. Dress warmly!"
    elif probability >= 5:
        risk_level = "LOW"
        status_message = f"🌤️ LOW RISK of cold weather in {season}. Light jacket recommended."
    else:
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

# =============================================================================
# ANÁLISIS DE TENDENCIAS CLIMÁTICAS
# =============================================================================
# Esta sección analiza tendencias de cambio climático a largo plazo,
# comparando datos recientes con promedios históricos para detectar
# patrones de cambio en las condiciones climáticas.

def analyze_climate_change_trend(monthly_data: pd.DataFrame, comparison_years: int = 5) -> Dict[str, Any]:
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
        comparison_years: Años a comparar por período (por defecto 5 años)
        
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
    
    # Períodos científicos: primeros 5 años vs últimos 5 años
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


def generate_fallback_plan_b(
    activity: str,
    weather_condition: str,
    risk_level: str,
    location: str = "Montevideo, Uruguay",
    season: str = "Summer"
) -> Dict[str, Any]:
    """
    Generate fallback Plan B suggestions when Gemini is not available
    """
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


def test_nasa_power_integration():
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
        risk_analysis = calculate_adverse_probability(march_data)
        print(f"Risk analysis: {risk_analysis['risk_level']} ({risk_analysis['probability']:.1f}%)")
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


def verify_data_source(month: int = 3):
    """
    Function to verify which data source is being used (NASA vs Mock)
    """
    print("=" * 60)
    print("VERIFICACION DE FUENTE DE DATOS")
    print("=" * 60)
    
    try:
        # Test NASA POWER API directly
        print("\n1. Probando NASA POWER API directamente...")
        test_lat = -34.90
        test_lon = -56.16
        current_year = datetime.now().year
        start_year = current_year - 20
        
        nasa_data = fetch_nasa_power_data(test_lat, test_lon, start_year, current_year)
        print(f"   NASA POWER API: {len(nasa_data)} registros")
        print(f"   Rango de anos: {nasa_data['Year'].min()}-{nasa_data['Year'].max()}")
        print(f"   Temperatura: {nasa_data['Max_Temperature_C'].min():.1f}C - {nasa_data['Max_Temperature_C'].max():.1f}C")
        
        # Test load_historical_data function
        print(f"\n2. Probando load_historical_data(month={month})...")
        monthly_data = load_historical_data(month)
        print(f"   Registros para mes {month}: {len(monthly_data)}")
        
        # Compare with mock data
        print(f"\n3. Comparando con datos mock...")
        try:
            mock_df = pd.read_csv('mock_data.csv')
            mock_monthly = mock_df[mock_df['Month'] == month]
            print(f"   Mock data para mes {month}: {len(mock_monthly)} registros")
            
            if len(monthly_data) > len(mock_monthly) * 10:
                print("   CONFIRMADO: Usando datos reales de NASA (mucho mas registros)")
            else:
                print("   ADVERTENCIA: Podria estar usando datos mock")
                
        except FileNotFoundError:
            print("   Mock data no encontrado")
        
        # Show sample of real data
        print(f"\n4. Muestra de datos reales (mes {month}):")
        print(monthly_data.head())
        
        # Calculate risk with real data
        print(f"\n5. Analisis de riesgo con datos reales:")
        risk_analysis = calculate_adverse_probability(monthly_data, {'Temp': 30.0, 'Condition': 'wet'})
        print(f"   Nivel de riesgo: {risk_analysis['risk_level']}")
        print(f"   Probabilidad: {risk_analysis['probability']:.1f}%")
        print(f"   Umbral: {risk_analysis['risk_threshold']:.1f}C")
        
        print("\n" + "=" * 60)
        print("VERIFICACION COMPLETADA")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Error en verificacion: {str(e)}")
        return False


def create_p90_trend_chart(plot_data: list) -> Dict[str, Any]:
    """
    Crea el primer gráfico: Línea de tendencia del P90 a lo largo de los años
    
    Args:
        plot_data: Lista de diccionarios con datos P90 por año
        
    Returns:
        Dict: Configuración del gráfico Plotly
    """
    if not plot_data:
        return {"error": "No data available for P90 trend chart"}
    
    df = pd.DataFrame(plot_data)
    
    # Crear gráfico de línea con P90
    fig = go.Figure()
    
    # Línea principal del P90
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['P90_Max_Temp'],
        mode='lines+markers',
        name='P90 Temperatura Máxima',
        line=dict(color='red', width=3),
        marker=dict(size=8, color='red'),
        hovertemplate='<b>Año:</b> %{x}<br><b>P90:</b> %{y:.1f}°C<extra></extra>'
    ))
    
    # Línea de la media para comparación
    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['Mean_Temp'],
        mode='lines+markers',
        name='Temperatura Media',
        line=dict(color='blue', width=2, dash='dash'),
        marker=dict(size=6, color='blue'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Media:</b> %{y:.1f}°C<extra></extra>'
    ))
    
    # Calcular línea de tendencia
    if len(df) > 1:
        z = np.polyfit(df['Year'], df['P90_Max_Temp'], 1)
        p = np.poly1d(z)
        trend_line = p(df['Year'])
        
        fig.add_trace(go.Scatter(
            x=df['Year'],
            y=trend_line,
            mode='lines',
            name='Tendencia P90',
            line=dict(color='orange', width=2, dash='dot'),
            hovertemplate='<b>Año:</b> %{x}<br><b>Tendencia:</b> %{y:.1f}°C<extra></extra>'
        ))
    
    # Configurar layout
    fig.update_layout(
        title=None,  # Remover título interno
        xaxis_title='Año',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)  # Fuente más pequeña
        ),
        template='plotly_white',
        height=300,
        width=400,
        margin=dict(l=40, r=40, t=20, b=40),  # Más espacio en los lados, menos arriba
        autosize=False
    )
    
    return {
        "chart_type": "p90_trend",
        "figure": fig.to_dict(),
        "description": "Gráfico de línea que muestra la evolución del P90 de temperatura máxima a lo largo de los años"
    }


def create_climate_comparison_chart(plot_data: list) -> Dict[str, Any]:
    """
    Crea el segundo gráfico: Comparación histórica vs actual con barras y líneas
    
    Args:
        plot_data: Lista de diccionarios con datos P90 por año
        
    Returns:
        Dict: Configuración del gráfico Plotly
    """
    if not plot_data:
        return {"error": "No data available for climate comparison chart"}
    
    df = pd.DataFrame(plot_data)
    
    # Crear subplot con ejes secundarios
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('P90 vs Temperatura Máxima por Año', 'Rango de Temperaturas'),
        vertical_spacing=0.15,  # Más espacio entre subplots
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Gráfico 1: P90 vs Max Temp
    fig.add_trace(
        go.Bar(
            x=df['Year'],
            y=df['P90_Max_Temp'],
            name='P90 Temperatura',
            marker_color='lightcoral',
            hovertemplate='<b>Año:</b> %{x}<br><b>P90:</b> %{y:.1f}°C<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Max_Temp'],
            mode='lines+markers',
            name='Temperatura Máxima',
            line=dict(color='darkred', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Año:</b> %{x}<br><b>Máxima:</b> %{y:.1f}°C<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Rango de temperaturas (Min, Mean, Max)
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Min_Temp'],
            mode='lines+markers',
            name='Temperatura Mínima',
            line=dict(color='lightblue', width=2),
            marker=dict(size=6),
            hovertemplate='<b>Año:</b> %{x}<br><b>Mínima:</b> %{y:.1f}°C<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Mean_Temp'],
            mode='lines+markers',
            name='Temperatura Media',
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Año:</b> %{x}<br><b>Media:</b> %{y:.1f}°C<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Max_Temp'],
            mode='lines+markers',
            name='Temperatura Máxima',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Año:</b> %{x}<br><b>Máxima:</b> %{y:.1f}°C<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Configurar layout
    fig.update_layout(
        title=None,  # Remover título interno
        height=280,  # Achicar más para que se vea completa
        width=400,
        template='plotly_white',
        hovermode='x unified',
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
    
    # Configurar ejes
    fig.update_xaxes(title_text="Año", row=2, col=1)
    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Temperatura (°C)", row=2, col=1)
    
    return {
        "chart_type": "climate_comparison",
        "figure": fig.to_dict(),
        "description": "Gráfico comparativo que muestra P90 vs temperaturas históricas y rangos de temperatura"
    }


def create_heat_risk_analysis_chart(plot_data: list) -> Dict[str, Any]:
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


def generate_plotly_visualizations(historical_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera los 3 gráficos interactivos Plotly para visualización P90 y comparación histórica
    
    Args:
        historical_data: DataFrame con datos históricos
        
    Returns:
        Dict: Diccionario con los 3 gráficos generados
    """
    try:
        # Obtener datos para los gráficos
        climate_data = get_climate_trend_data(historical_data)
        plot_data = climate_data.get('plot_data', [])
        
        if not plot_data:
            return {
                "error": "No data available for visualization",
                "charts": []
            }
        
        # Generar los 3 gráficos
        charts = []
        
        # Gráfico 1: Tendencia P90
        chart1 = create_p90_trend_chart(plot_data)
        if "error" not in chart1:
            charts.append(chart1)
        
        # Gráfico 2: Comparación climática
        chart2 = create_climate_comparison_chart(plot_data)
        if "error" not in chart2:
            charts.append(chart2)
        
        # Gráfico 3: Análisis de riesgo
        chart3 = create_heat_risk_analysis_chart(plot_data)
        if "error" not in chart3:
            charts.append(chart3)
        
        return {
            "success": True,
            "charts": charts,
            "climate_trend": climate_data.get('climate_trend', ''),
            "data_points": len(plot_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating visualizations: {str(e)}",
            "charts": []
        }


# =============================================================================
# UTILIDADES Y VALIDACIONES
# =============================================================================
# Esta sección contiene funciones auxiliares, validaciones de datos,
# funciones de prueba y el punto de entrada del script.

if __name__ == "__main__":
    # Run verification when script is executed directly
    verify_data_source()