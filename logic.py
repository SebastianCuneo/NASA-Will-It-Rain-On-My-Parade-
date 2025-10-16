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
    try:
        # Construct the NASA POWER API URL
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Format dates as YYYYMMDD
        start_date = f"{start_year}0101"  # January 1st
        end_date = f"{end_year}1231"      # December 31st
        
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
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to fetch NASA POWER data after {max_retries} attempts: {str(e)}")
                print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
        
        # Parse JSON response
        data = response.json()
        
        # Extract time series data - NASA POWER API structure
        if 'properties' not in data or 'parameter' not in data['properties']:
            raise Exception("Invalid response format from NASA POWER API - no 'properties.parameter' key found")
        
        parameters = data['properties']['parameter']
        
        # Extract T2M_MAX (Temperature Max) and PRECTOTCORR (Precipitation Total Corrected)
        temp_data = parameters.get('T2M_MAX', {})
        precip_data = parameters.get('PRECTOTCORR', {})
        
        if not temp_data or not precip_data:
            raise Exception("Temperature or precipitation data not found in API response")
        
        # Convert to DataFrame
        records = []
        for date_str, temp_value in temp_data.items():
            if date_str in precip_data:
                # Parse date (format: YYYYMMDD)
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                
                # Temperature is already in Celsius from NASA POWER API
                temp_celsius = temp_value if temp_value is not None else None
                
                # Precipitation is already in mm/day
                precip_mm = precip_data[date_str] if precip_data[date_str] is not None else None
                
                records.append({
                    'Year': date_obj.year,
                    'Month': date_obj.month,
                    'Max_Temperature_C': temp_celsius,
                    'Precipitation_mm': precip_mm
                })
        
        if not records:
            raise Exception("No valid data records found in API response")
        
        df = pd.DataFrame(records)
        
        # Remove any rows with null values
        df = df.dropna()
        
        # Sort by year and month
        df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        print(f"Successfully fetched {len(df)} records from NASA POWER API")
        return df
        
    except Exception as e:
        print(f"Error fetching NASA POWER data: {str(e)}")
        # Fallback to mock data if API fails
        print("Falling back to mock data...")
        try:
            df = pd.read_csv('mock_data.csv')
            return df
        except FileNotFoundError:
            raise Exception(f"NASA POWER API failed and mock data not found: {str(e)}")


def load_historical_data(month_filter: int, lat: float = -34.90, lon: float = -56.16) -> pd.DataFrame:
    """
    Load and filter historical data by month using NASA POWER API
    
    Args:
        month_filter: Month to filter (1-12)
        lat: Latitude coordinate (default: Montevideo)
        lon: Longitude coordinate (default: Montevideo)
        
    Returns:
        pd.DataFrame: Filtered data for the specified month
    """
    try:
        if not isinstance(month_filter, int) or month_filter < 1 or month_filter > 12:
            raise ValueError("Month must be between 1 and 12")
        
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
        return monthly_data
        
    except Exception as e:
        print(f"Error in load_historical_data: {str(e)}")
        # Final fallback to mock data
        try:
            print("Attempting fallback to mock data...")
            df = pd.read_csv('mock_data.csv')
            monthly_data = df[df['Month'] == month_filter].copy()
            if monthly_data.empty:
                raise ValueError(f"No data found for month {month_filter}")
            print(f"Using mock data: {len(monthly_data)} records for month {month_filter}")
            return monthly_data
        except FileNotFoundError:
            raise FileNotFoundError("mock_data.csv not found and NASA POWER API unavailable")
        except Exception as fallback_error:
            raise Exception(f"Both NASA POWER API and mock data failed: {str(e)} | {str(fallback_error)}")


def calculate_adverse_probability(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate adverse weather probability based on temperature data"""
    if monthly_data.empty:
        raise ValueError("No data provided")
    
    if 'Max_Temperature_C' not in monthly_data.columns:
        raise ValueError("Temperature data not found")
    
    # Calculate 90th percentile threshold
    risk_threshold = np.percentile(monthly_data['Max_Temperature_C'], 90)
    
    # Count adverse events
    adverse_events = monthly_data[monthly_data['Max_Temperature_C'] >= risk_threshold]
    total_observations = len(monthly_data)
    adverse_count = len(adverse_events)
    
    # Calculate probability
    probability = (adverse_count / total_observations) * 100
    
    # Generate status message
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
        
        print(f"Testing with coordinates: ({test_lat}, {test_lon})")
        print(f"Date range: {test_start_year} to {test_end_year}")
        
        # Fetch data
        df = fetch_nasa_power_data(test_lat, test_lon, test_start_year, test_end_year)
        
        print(f"Successfully fetched {len(df)} records")
        print(f"Data shape: {df.shape}")
        print(f"Date range: {df['Year'].min()}-{df['Year'].max()}")
        print(f"Temperature range: {df['Max_Temperature_C'].min():.1f}C to {df['Max_Temperature_C'].max():.1f}C")
        print(f"Precipitation range: {df['Precipitation_mm'].min():.1f}mm to {df['Precipitation_mm'].max():.1f}mm")
        
        # Test month filtering
        march_data = load_historical_data(3)  # March
        print(f"March data: {len(march_data)} records")
        
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
        risk_analysis = calculate_adverse_probability(monthly_data)
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


if __name__ == "__main__":
    # Run verification when script is executed directly
    verify_data_source()