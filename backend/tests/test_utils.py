"""
Configuración y utilidades para pruebas de NASA POWER API
"""

import os
import sys
import logging
from datetime import datetime

def setup_test_logging():
    """Configura logging para las pruebas"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'nasa_api_tests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def get_test_coordinates():
    """Retorna coordenadas de prueba para diferentes ubicaciones"""
    return {
        'montevideo': (-34.90, -56.16),
        'buenos_aires': (-34.61, -58.38),
        'sao_paulo': (-23.55, -46.63),
        'santiago': (-33.45, -70.67),
        'lima': (-12.05, -77.03),
        'bogota': (4.71, -74.07),
        'mexico_city': (19.43, -99.13),
        'miami': (25.76, -80.19),
        'madrid': (40.42, -3.70),
        'london': (51.51, -0.13)
    }

def get_test_year_ranges():
    """Retorna rangos de años para pruebas"""
    return {
        'recent': (2023, 2023),      # Un año reciente
        'short': (2020, 2022),        # Rango corto
        'medium': (2015, 2020),       # Rango medio
        'long': (2005, 2024),         # Rango largo (20 años)
        'edge_case': (2024, 2024)     # Solo año actual
    }

def create_mock_nasa_response(start_year=2020, end_year=2024, include_none=False):
    """Crea una respuesta mock de la NASA POWER API para pruebas"""
    import random
    
    temp_data = {}
    precip_data = {}
    
    # Generar datos para cada año
    for year in range(start_year, end_year + 1):
        # Generar datos para cada día del año (simplificado: solo algunos días)
        for month in range(1, 13):
            days_in_month = 30 if month in [4, 6, 9, 11] else 31
            if month == 2:
                days_in_month = 29 if year % 4 == 0 else 28
            
            for day in range(1, min(days_in_month + 1, 6)):  # Solo primeros 5 días por mes
                date_str = f"{year:04d}{month:02d}{day:02d}"
                
                # Generar datos realistas
                base_temp = 20 + (month - 6) * 2  # Variación estacional
                temp_variation = random.uniform(-5, 5)
                temp_value = base_temp + temp_variation
                
                precip_value = random.uniform(0, 10) if random.random() < 0.3 else 0
                
                # Agregar valores None si se solicita
                if include_none and random.random() < 0.1:  # 10% de valores None
                    temp_value = None
                    precip_value = None
                
                temp_data[date_str] = temp_value
                precip_data[date_str] = precip_value
    
    return {
        "properties": {
            "parameter": {
                "T2M_MAX": temp_data,
                "PRECTOTCORR": precip_data
            }
        }
    }

def validate_dataframe_structure(df, expected_columns=None):
    """Valida la estructura de un DataFrame"""
    import pandas as pd
    
    if expected_columns is None:
        expected_columns = ['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm']
    
    # Verificar que es un DataFrame
    assert isinstance(df, pd.DataFrame), "Result should be a pandas DataFrame"
    
    # Verificar columnas
    for col in expected_columns:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verificar tipos de datos
    assert pd.api.types.is_numeric_dtype(df['Year']), "Year should be numeric"
    assert pd.api.types.is_numeric_dtype(df['Month']), "Month should be numeric"
    assert pd.api.types.is_numeric_dtype(df['Max_Temperature_C']), "Max_Temperature_C should be numeric"
    assert pd.api.types.is_numeric_dtype(df['Min_Temperature_C']), "Min_Temperature_C should be numeric"
    assert pd.api.types.is_numeric_dtype(df['Avg_Temperature_C']), "Avg_Temperature_C should be numeric"
    assert pd.api.types.is_numeric_dtype(df['Precipitation_mm']), "Precipitation_mm should be numeric"
    
    # Verificar rangos de valores
    if not df.empty:
        assert all(1 <= month <= 12 for month in df['Month']), "Month should be between 1 and 12"
        assert all(year >= 1900 for year in df['Year']), "Year should be reasonable"
        assert all(temp >= -50 and temp <= 60 for temp in df['Max_Temperature_C']), "Max temperature should be reasonable"
        assert all(temp >= -50 and temp <= 60 for temp in df['Min_Temperature_C']), "Min temperature should be reasonable"
        assert all(temp >= -50 and temp <= 60 for temp in df['Avg_Temperature_C']), "Avg temperature should be reasonable"
        assert all(precip >= 0 for precip in df['Precipitation_mm']), "Precipitation should be non-negative"
    
    return True

def print_test_summary(results):
    """Imprime un resumen de los resultados de las pruebas"""
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result['status'] == 'PASSED')
    failed_tests = total_tests - passed_tests
    
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS DE NASA POWER API")
    print("="*60)
    print(f"Total de pruebas: {total_tests}")
    print(f"Pruebas exitosas: {passed_tests}")
    print(f"Pruebas fallidas: {failed_tests}")
    print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\nPruebas fallidas:")
        for result in results:
            if result['status'] == 'FAILED':
                print(f"  ❌ {result['test_name']}: {result['error']}")
    
    print("="*60)
