"""
Pruebas para fetch_nasa_power_data - NASA POWER API Integration Tests
NASA Space Apps Challenge - Test Suite
"""

import unittest
import pandas as pd
import requests
from unittest.mock import patch, Mock
import json
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path para importar logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import fetch_nasa_power_data


class TestNasaPowerAPI(unittest.TestCase):
    """Pruebas comprehensivas para fetch_nasa_power_data"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.test_lat = -34.90  # Montevideo
        self.test_lon = -56.16  # Montevideo
        self.start_year = 2020
        self.end_year = 2024
        
        # Respuesta JSON de ejemplo de la NASA POWER API
        self.mock_nasa_response = {
            "properties": {
                "parameter": {
                    "T2M_MAX": {
                        "20200101": 33.9,
                        "20200102": 32.1,
                        "20200103": 31.5,
                        "20200104": 29.8,
                        "20200105": 30.2,
                        "20210101": 34.1,
                        "20210102": 33.2,
                        "20210103": 32.8,
                        "20210104": 30.5,
                        "20210105": 31.1
                    },
                    "T2M_MIN": {
                        "20200101": 18.5,
                        "20200102": 17.2,
                        "20200103": 16.8,
                        "20200104": 15.1,
                        "20200105": 16.3,
                        "20210101": 19.2,
                        "20210102": 18.1,
                        "20210103": 17.5,
                        "20210104": 15.8,
                        "20210105": 16.9
                    },
                    "T2M": {
                        "20200101": 26.2,
                        "20200102": 24.7,
                        "20200103": 24.2,
                        "20200104": 22.5,
                        "20200105": 23.3,
                        "20210101": 26.7,
                        "20210102": 25.7,
                        "20210103": 25.2,
                        "20210104": 23.2,
                        "20210105": 24.0
                    },
                    "PRECTOTCORR": {
                        "20200101": 0.0,
                        "20200102": 5.2,
                        "20200103": 0.0,
                        "20200104": 2.1,
                        "20200105": 0.0,
                        "20210101": 1.5,
                        "20210102": 0.0,
                        "20210103": 3.8,
                        "20210104": 0.0,
                        "20210105": 2.3
                    }
                }
            }
        }
        
        # Respuesta de error de ejemplo
        self.mock_error_response = {
            "messages": ["Invalid coordinates provided"],
            "message": "The requested location is outside the valid range"
        }

    def test_successful_data_fetch(self):
        """Prueba: Obtención exitosa de datos de la NASA POWER API"""
        with patch('requests.get') as mock_get:
            # Configurar mock response
            mock_response = Mock()
            mock_response.json.return_value = self.mock_nasa_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Ejecutar función
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificaciones
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)
            self.assertIn('Year', result.columns)
            self.assertIn('Month', result.columns)
            self.assertIn('Max_Temperature_C', result.columns)
            self.assertIn('Min_Temperature_C', result.columns)
            self.assertIn('Avg_Temperature_C', result.columns)
            self.assertIn('Precipitation_mm', result.columns)
            
            # Verificar que se llamó la API correctamente
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            self.assertEqual(call_args[1]['params']['latitude'], self.test_lat)
            self.assertEqual(call_args[1]['params']['longitude'], self.test_lon)
            self.assertEqual(call_args[1]['params']['parameters'], 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR')

    def test_data_structure_validation(self):
        """Prueba: Validación de estructura de datos devueltos"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.mock_nasa_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificar estructura de datos
            self.assertEqual(len(result), 10)  # 10 registros en el mock
            
            # Verificar tipos de datos
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Year']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Month']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Max_Temperature_C']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Min_Temperature_C']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Avg_Temperature_C']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['Precipitation_mm']))
            
            # Verificar rangos de valores
            self.assertTrue(all(1 <= month <= 12 for month in result['Month']))
            self.assertTrue(all(year >= self.start_year for year in result['Year']))
            self.assertTrue(all(temp >= -50 and temp <= 60 for temp in result['Max_Temperature_C']))
            self.assertTrue(all(temp >= -50 and temp <= 60 for temp in result['Min_Temperature_C']))
            self.assertTrue(all(temp >= -50 and temp <= 60 for temp in result['Avg_Temperature_C']))
            self.assertTrue(all(precip >= 0 for precip in result['Precipitation_mm']))

    def test_api_error_response(self):
        """Prueba: Manejo de respuesta de error de la API"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.mock_error_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback (no DataFrame vacío)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback
            self.assertEqual(list(result.columns), ['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])

    def test_invalid_json_structure(self):
        """Prueba: Manejo de estructura JSON inválida"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"invalid": "structure"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback (no DataFrame vacío)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback

    def test_missing_parameters(self):
        """Prueba: Manejo de parámetros faltantes en respuesta"""
        incomplete_response = {
            "properties": {
                "parameter": {
                    "T2M_MAX": {"20200101": 33.9},
                    "T2M_MIN": {"20200101": 18.5},
                    # T2M y PRECTOTCORR faltantes
                }
            }
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = incomplete_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback (no DataFrame vacío)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback

    def test_network_timeout(self):
        """Prueba: Manejo de timeout de red"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback después de reintentos
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback
            # Verificar que se hicieron múltiples intentos
            self.assertEqual(mock_get.call_count, 3)

    def test_connection_error(self):
        """Prueba: Manejo de error de conexión"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback después de reintentos
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback
            self.assertEqual(mock_get.call_count, 3)

    def test_http_error(self):
        """Prueba: Manejo de error HTTP"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback después de reintentos
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback
            self.assertEqual(mock_get.call_count, 3)

    def test_json_decode_error(self):
        """Prueba: Manejo de error de decodificación JSON"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback (no DataFrame vacío)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback

    def test_data_with_none_values(self):
        """Prueba: Manejo de valores None en datos"""
        response_with_none = {
            "properties": {
                "parameter": {
                    "T2M_MAX": {
                        "20200101": 33.9,
                        "20200102": None,  # Valor faltante
                        "20200103": 31.5
                    },
                    "T2M_MIN": {
                        "20200101": 18.5,
                        "20200102": 17.2,
                        "20200103": None  # Valor faltante
                    },
                    "T2M": {
                        "20200101": 26.2,
                        "20200102": 24.7,
                        "20200103": 24.2
                    },
                    "PRECTOTCORR": {
                        "20200101": 0.0,
                        "20200102": 5.2,
                        "20200103": None  # Valor faltante
                    }
                }
            }
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = response_with_none
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar DataFrame con datos válidos (sin None)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)
            # Verificar que no hay valores None
            self.assertFalse(result.isnull().any().any())

    def test_date_parsing(self):
        """Prueba: Parsing correcto de fechas"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.mock_nasa_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificar parsing de fechas
            self.assertIn(2020, result['Year'].values)
            self.assertIn(2021, result['Year'].values)
            self.assertIn(1, result['Month'].values)  # Enero

    def test_empty_data_response(self):
        """Prueba: Manejo de respuesta con datos vacíos"""
        empty_response = {
            "properties": {
                "parameter": {
                    "T2M_MAX": {},
                    "T2M_MIN": {},
                    "T2M": {},
                    "PRECTOTCORR": {}
                }
            }
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = empty_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Debe retornar datos de fallback (no DataFrame vacío)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)  # Ahora esperamos datos de fallback

    def test_coordinate_edge_cases(self):
        """Prueba: Coordenadas en casos límite"""
        edge_cases = [
            (-90.0, -180.0),  # Esquina sudoeste
            (90.0, 180.0),    # Esquina noreste
            (0.0, 0.0),       # Centro
        ]
        
        for lat, lon in edge_cases:
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self.mock_nasa_response
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                result = fetch_nasa_power_data(lat, lon, self.start_year, self.end_year)
                
                # Debe funcionar con coordenadas válidas
                self.assertIsInstance(result, pd.DataFrame)

    def test_year_range_edge_cases(self):
        """Prueba: Rangos de años en casos límite"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.mock_nasa_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Mismo año (rango de 1 año)
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                2020, 
                2020
            )
            
            self.assertIsInstance(result, pd.DataFrame)

    def test_fallback_system(self):
        """Prueba: Sistema de fallback con datos de Montevideo"""
        with patch('requests.get') as mock_get:
            # Simular error de conexión para activar fallback
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificar que se retornan datos de fallback
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)
            self.assertEqual(list(result.columns), ['Year', 'Month', 'Max_Temperature_C', 'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'])
            
            # Verificar que los datos tienen sentido (datos de Montevideo)
            self.assertTrue(len(result) > 100)  # Debe tener muchos registros históricos
            self.assertTrue(all(year >= self.start_year for year in result['Year']))
            self.assertTrue(all(year <= self.end_year for year in result['Year']))
            
            # Verificar que las temperaturas tienen sentido para Montevideo
            self.assertTrue(all(temp >= -10 and temp <= 40 for temp in result['Max_Temperature_C']))
            self.assertTrue(all(temp >= -10 and temp <= 40 for temp in result['Min_Temperature_C']))
            self.assertTrue(all(temp >= -10 and temp <= 40 for temp in result['Avg_Temperature_C']))
            self.assertTrue(all(precip >= 0 for precip in result['Precipitation_mm']))

    def test_api_url_construction(self):
        """Prueba: Construcción correcta de URL de API"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.mock_nasa_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificar URL y parámetros
            call_args = mock_get.call_args
            self.assertEqual(call_args[0][0], "https://power.larc.nasa.gov/api/temporal/daily/point")
            
            params = call_args[1]['params']
            self.assertEqual(params['parameters'], 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR')
            self.assertEqual(params['community'], 'AG')
            self.assertEqual(params['format'], 'JSON')
            self.assertEqual(params['latitude'], self.test_lat)
            self.assertEqual(params['longitude'], self.test_lon)
            self.assertEqual(params['start'], '20200101')
            self.assertEqual(params['end'], '20241231')


class TestNasaPowerAPIIntegration(unittest.TestCase):
    """Pruebas de integración real con la NASA POWER API (opcional)"""
    
    def setUp(self):
        """Configuración para pruebas de integración"""
        self.test_lat = -34.90  # Montevideo
        self.test_lon = -56.16  # Montevideo
        self.start_year = 2023  # Año reciente para pruebas
        self.end_year = 2023    # Solo un año para pruebas rápidas

    @unittest.skip("Skip integration test by default - uncomment to run")
    def test_real_api_call(self):
        """Prueba: Llamada real a la NASA POWER API (requiere internet)"""
        try:
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificaciones básicas
            self.assertIsInstance(result, pd.DataFrame)
            
            if not result.empty:
                # Verificar estructura
                self.assertIn('Year', result.columns)
                self.assertIn('Month', result.columns)
                self.assertIn('Max_Temperature_C', result.columns)
                self.assertIn('Precipitation_mm', result.columns)
                
                # Verificar datos
                self.assertTrue(len(result) > 0)
                self.assertTrue(all(year == self.start_year for year in result['Year']))
                
                print(f"✅ Real API test successful: {len(result)} records fetched")
            else:
                print("⚠️ Real API test returned empty data")
                
        except Exception as e:
            self.fail(f"Real API test failed: {str(e)}")


if __name__ == '__main__':
    # Configurar logging para las pruebas
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar pruebas
    unittest.main(verbosity=2)
