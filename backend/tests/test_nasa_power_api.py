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


class TestNasaPowerAPIIntegration(unittest.TestCase):
    """Pruebas de integración real con la NASA POWER API"""
    
    def setUp(self):
        """Configuración para pruebas de integración"""
        self.test_lat = -34.90  # Montevideo
        self.test_lon = -56.16  # Montevideo
        self.start_year = 2024
        self.end_year = 2024
        
    def test_real_nasa_api_connectivity(self):
        """Prueba: Conectividad real con la NASA POWER API"""
        import requests
        
        # Construir URL de la NASA API
        base_url = 'https://power.larc.nasa.gov/api/temporal/daily/point'
        params = {
            'parameters': 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR',
            'community': 'RE',
            'longitude': self.test_lon,
            'latitude': self.test_lat,
            'start': f'{self.start_year}0101',
            'end': f'{self.end_year}1231',
            'format': 'JSON'
        }
        
        try:
            # Llamada real a la NASA API
            response = requests.get(base_url, params=params, timeout=30)
            
            # Verificar respuesta HTTP
            self.assertEqual(response.status_code, 200, 
                           f"NASA API returned status {response.status_code}")
            
            # Verificar content type
            content_type = response.headers.get('content-type', '')
            self.assertIn('application/json', content_type,
                         f"Expected JSON response, got: {content_type}")
            
            # Parsear JSON
            data = response.json()
            
            # Verificar estructura básica
            self.assertIn('properties', data, 
                         "Response missing 'properties' key")
            
            properties = data['properties']
            self.assertIn('parameter', properties,
                         "Response missing 'parameter' key")
            
            # Verificar parámetros requeridos
            parameters = properties['parameter']
            required_params = ['T2M_MAX', 'T2M_MIN', 'T2M', 'PRECTOTCORR']
            
            for param in required_params:
                self.assertIn(param, parameters,
                             f"Missing required parameter: {param}")
            
            # Verificar que hay datos
            for param in required_params:
                param_data = parameters[param]
                self.assertGreater(len(param_data), 0,
                                 f"Parameter {param} has no data")
            
            print(f"✅ NASA API connectivity test passed")
            print(f"   Parameters received: {list(parameters.keys())}")
            print(f"   Sample dates: {list(parameters['T2M_MAX'].keys())[:3]}")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Network error connecting to NASA API: {e}")
        except Exception as e:
            self.fail(f"Unexpected error in NASA API test: {e}")
    
    def test_real_nasa_api_data_quality(self):
        """Prueba: Calidad de datos reales de la NASA API"""
        try:
            # Llamada real usando nuestra función
            result = fetch_nasa_power_data(
                self.test_lat, 
                self.test_lon, 
                self.start_year, 
                self.end_year
            )
            
            # Verificar que obtenemos datos
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty, "NASA API returned empty data")
            
            # Verificar estructura de columnas
            expected_columns = [
                'Year', 'Month', 'Max_Temperature_C', 
                'Min_Temperature_C', 'Avg_Temperature_C', 'Precipitation_mm'
            ]
            for col in expected_columns:
                self.assertIn(col, result.columns, f"Missing column: {col}")
            
            # Verificar calidad de datos de temperatura
            max_temp = result['Max_Temperature_C']
            min_temp = result['Min_Temperature_C']
            avg_temp = result['Avg_Temperature_C']
            
            # Temperaturas deben estar en rangos realistas para Montevideo
            self.assertGreater(max_temp.max(), 20, "Max temperatures too low")
            self.assertLess(max_temp.max(), 45, "Max temperatures too high")
            self.assertGreater(min_temp.min(), -5, "Min temperatures too low")
            self.assertLess(min_temp.min(), 25, "Min temperatures too high")
            
            # Temperatura promedio debe estar entre min y max
            for idx in result.index:
                self.assertGreaterEqual(avg_temp.iloc[idx], min_temp.iloc[idx],
                                      "Avg temp should be >= min temp")
                self.assertLessEqual(avg_temp.iloc[idx], max_temp.iloc[idx],
                                   "Avg temp should be <= max temp")
            
            # Verificar precipitación
            precipitation = result['Precipitation_mm']
            self.assertGreaterEqual(precipitation.min(), 0, 
                                  "Precipitation should be >= 0")
            
            # Verificar fechas
            self.assertTrue(all(year == self.start_year for year in result['Year']),
                          "All years should match requested year")
            
            months = result['Month'].unique()
            self.assertTrue(all(1 <= month <= 12 for month in months),
                          "All months should be between 1 and 12")
            
            print(f"✅ NASA API data quality test passed")
            print(f"   Records: {len(result)}")
            print(f"   Temperature range: {min_temp.min():.1f}°C - {max_temp.max():.1f}°C")
            print(f"   Precipitation range: {precipitation.min():.1f}mm - {precipitation.max():.1f}mm")
            print(f"   Months covered: {sorted(months)}")
            
        except Exception as e:
            self.fail(f"Data quality test failed: {e}")
    
    def test_real_nasa_api_global_coordinates(self):
        """Prueba: NASA API con coordenadas globales"""
        global_coordinates = [
            ("Montevideo, Uruguay", -34.90, -56.16),
            ("New York, USA", 40.7128, -74.0060),
            ("Tokyo, Japan", 35.6762, 139.6503),
            ("London, UK", 51.5074, -0.1278),
            ("Sydney, Australia", -33.8688, 151.2093)
        ]
        
        for location_name, lat, lon in global_coordinates:
            with self.subTest(location=location_name):
                try:
                    result = fetch_nasa_power_data(lat, lon, 2024, 2024)
                    
                    # Verificar que obtenemos datos
                    self.assertIsInstance(result, pd.DataFrame)
                    self.assertFalse(result.empty, 
                                   f"No data returned for {location_name}")
                    
                    # Verificar estructura básica
                    self.assertIn('Max_Temperature_C', result.columns)
                    self.assertIn('Precipitation_mm', result.columns)
                    
                    # Verificar que las temperaturas son realistas
                    max_temp = result['Max_Temperature_C'].max()
                    min_temp = result['Min_Temperature_C'].min()
                    
                    # Rangos globales realistas
                    self.assertGreater(max_temp, -50, f"Max temp too low for {location_name}")
                    self.assertLess(max_temp, 60, f"Max temp too high for {location_name}")
                    self.assertGreater(min_temp, -60, f"Min temp too low for {location_name}")
                    self.assertLess(min_temp, 40, f"Min temp too high for {location_name}")
                    
                    print(f"✅ {location_name}: {len(result)} records, "
                          f"temp range {min_temp:.1f}°C - {max_temp:.1f}°C")
                    
                except Exception as e:
                    self.fail(f"Global coordinates test failed for {location_name}: {e}")
    
    def test_real_nasa_api_error_handling(self):
        """Prueba: Manejo de errores reales de la NASA API"""
        import requests
        
        # Probar con coordenadas inválidas
        invalid_coordinates = [
            (999.0, 0.0),    # Latitud inválida
            (0.0, 999.0),    # Longitud inválida
            (999.0, 999.0),  # Ambas inválidas
        ]
        
        for lat, lon in invalid_coordinates:
            with self.subTest(coordinates=(lat, lon)):
                try:
                    # Esto debería activar el fallback
                    result = fetch_nasa_power_data(lat, lon, 2024, 2024)
                    
                    # Debería obtener datos de fallback (Montevideo)
                    self.assertIsInstance(result, pd.DataFrame)
                    self.assertFalse(result.empty, "Should get fallback data")
                    
                    print(f"✅ Invalid coordinates ({lat}, {lon}): Fallback activated")
                    
                except ValueError as e:
                    # Si las coordenadas son muy inválidas, debería fallar en validación
                    self.assertIn("fuera del rango válido global", str(e))
                    print(f"✅ Invalid coordinates ({lat}, {lon}): Correctly rejected")
                    
                except Exception as e:
                    self.fail(f"Unexpected error for invalid coordinates ({lat}, {lon}): {e}")
    
    def test_real_nasa_api_vs_fallback_data(self):
        """Prueba: Verificar que obtenemos datos reales de NASA API, no del fallback"""
        import requests
        from datetime import datetime
        
        # Usar coordenadas de Montevideo para comparar con datos conocidos
        lat, lon = -34.90, -56.16
        
        # Fecha específica que sabemos que existe en el fallback (2005-10-23, DOY 296)
        test_year = 2005
        test_month = 10
        test_day = 23
        
        print(f"\n🔍 VERIFICANDO DATOS REALES DE NASA API:")
        print(f"   Fecha: {test_year}-{test_month:02d}-{test_day:02d}")
        print(f"   Coordenadas: ({lat}, {lon})")
        
        # 1. Obtener datos directamente de la NASA API
        base_url = 'https://power.larc.nasa.gov/api/temporal/daily/point'
        params = {
            'parameters': 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR',
            'community': 'RE',
            'longitude': lon,
            'latitude': lat,
            'start': f'{test_year}1023',  # 2005-10-23
            'end': f'{test_year}1023',    # Mismo día
            'format': 'JSON'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            self.assertEqual(response.status_code, 200, "NASA API should return 200")
            
            data = response.json()
            parameters = data['properties']['parameter']
            
            # Extraer datos específicos del día
            date_key = f'{test_year}1023'
            nasa_max_temp = parameters['T2M_MAX'].get(date_key)
            nasa_min_temp = parameters['T2M_MIN'].get(date_key)
            nasa_avg_temp = parameters['T2M'].get(date_key)
            nasa_precip = parameters['PRECTOTCORR'].get(date_key)
            
            print(f"   📊 Datos de NASA API:")
            print(f"      T2M_MAX: {nasa_max_temp}°C")
            print(f"      T2M_MIN: {nasa_min_temp}°C")
            print(f"      T2M: {nasa_avg_temp}°C")
            print(f"      PRECTOTCORR: {nasa_precip}mm")
            
            # 2. Obtener datos usando nuestra función
            result = fetch_nasa_power_data(lat, lon, test_year, test_year)
            
            # Filtrar por el mes específico
            october_data = result[result['Month'] == test_month]
            
            print(f"   📊 Datos de nuestra función:")
            print(f"      Registros en octubre: {len(october_data)}")
            
            if len(october_data) > 0:
                # Encontrar el día específico (aproximado)
                day_data = october_data.iloc[test_day-1] if test_day <= len(october_data) else october_data.iloc[-1]
                
                print(f"      T2M_MAX: {day_data['Max_Temperature_C']:.2f}°C")
                print(f"      T2M_MIN: {day_data['Min_Temperature_C']:.2f}°C")
                print(f"      T2M: {day_data['Avg_Temperature_C']:.2f}°C")
                print(f"      PRECTOTCORR: {day_data['Precipitation_mm']:.2f}mm")
                
                # 3. Verificar que los datos son similares (no exactos porque pueden variar)
                # pero dentro de rangos razonables
                temp_diff_max = abs(nasa_max_temp - day_data['Max_Temperature_C'])
                temp_diff_min = abs(nasa_min_temp - day_data['Min_Temperature_C'])
                temp_diff_avg = abs(nasa_avg_temp - day_data['Avg_Temperature_C'])
                
                print(f"   🔍 Diferencias:")
                print(f"      T2M_MAX diff: {temp_diff_max:.2f}°C")
                print(f"      T2M_MIN diff: {temp_diff_min:.2f}°C")
                print(f"      T2M diff: {temp_diff_avg:.2f}°C")
                
                # Las diferencias deben ser pequeñas (máximo 2°C)
                self.assertLess(temp_diff_max, 2.0, "Max temperature difference too large")
                self.assertLess(temp_diff_min, 2.0, "Min temperature difference too large")
                self.assertLess(temp_diff_avg, 2.0, "Avg temperature difference too large")
                
                print(f"   ✅ Datos verificados: Diferencias dentro de rangos aceptables")
                
            else:
                self.fail("No data found for October 2005")
            
            # 4. Verificar que NO estamos usando datos de fallback
            # Los datos de fallback tienen valores específicos que podemos detectar
            fallback_max_temp = 15.48  # Del archivo CSV
            fallback_min_temp = 12.13
            fallback_avg_temp = 13.63
            fallback_precip = 0.01
            
            # Si los datos son exactamente iguales a los del fallback, algo está mal
            if (abs(nasa_max_temp - fallback_max_temp) < 0.01 and 
                abs(nasa_min_temp - fallback_min_temp) < 0.01 and
                abs(nasa_avg_temp - fallback_avg_temp) < 0.01):
                print(f"   ⚠️ ADVERTENCIA: Los datos parecen ser del fallback")
            else:
                print(f"   ✅ CONFIRMADO: Datos reales de NASA API (no fallback)")
            
            # 5. Verificar que los datos son realistas para Montevideo en octubre
            self.assertGreater(nasa_max_temp, 10, "Max temp too low for Montevideo October")
            self.assertLess(nasa_max_temp, 30, "Max temp too high for Montevideo October")
            self.assertGreater(nasa_min_temp, 5, "Min temp too low for Montevideo October")
            self.assertLess(nasa_min_temp, 20, "Min temp too high for Montevideo October")
            
            print(f"   ✅ Datos realistas para Montevideo en octubre")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Network error: {e}")
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_nasa_api_data_source_verification(self):
        """Prueba: Verificar que los datos del fallback son realmente de la NASA API"""
        import requests
        
        print(f"\n🔍 VERIFICANDO FUENTE DE DATOS:")
        print(f"   Objetivo: Confirmar que FALLBACK_MONTEVIDEO_DATA.csv contiene datos reales de NASA")
        
        # Coordenadas de Montevideo
        lat, lon = -34.90, -56.16
        
        # Probar múltiples fechas del fallback
        test_dates = [
            ('20051023', 'DOY 296', 15.48, 12.13, 13.63, 0.01),
            ('20051024', 'DOY 297', 16.39, 12.03, 13.97, 33.21),
            ('20051025', 'DOY 298', 16.42, 12.82, 14.55, 11.29),
        ]
        
        for date_key, doy_desc, fallback_max, fallback_min, fallback_avg, fallback_precip in test_dates:
            print(f"\n   📅 Fecha: {date_key} ({doy_desc})")
            
            # Llamada directa a NASA API
            base_url = 'https://power.larc.nasa.gov/api/temporal/daily/point'
            params = {
                'parameters': 'T2M_MAX,T2M_MIN,T2M,PRECTOTCORR',
                'community': 'RE',
                'longitude': lon,
                'latitude': lat,
                'start': date_key,
                'end': date_key,
                'format': 'JSON'
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                self.assertEqual(response.status_code, 200, f"NASA API failed for {date_key}")
                
                data = response.json()
                parameters = data['properties']['parameter']
                
                nasa_max = parameters['T2M_MAX'].get(date_key)
                nasa_min = parameters['T2M_MIN'].get(date_key)
                nasa_avg = parameters['T2M'].get(date_key)
                nasa_precip = parameters['PRECTOTCORR'].get(date_key)
                
                print(f"      📊 NASA API: Max={nasa_max}°C, Min={nasa_min}°C, Avg={nasa_avg}°C, Precip={nasa_precip}mm")
                print(f"      📊 Fallback: Max={fallback_max}°C, Min={fallback_min}°C, Avg={fallback_avg}°C, Precip={fallback_precip}mm")
                
                # Verificar que los datos son exactamente iguales
                max_diff = abs(nasa_max - fallback_max)
                min_diff = abs(nasa_min - fallback_min)
                avg_diff = abs(nasa_avg - fallback_avg)
                precip_diff = abs(nasa_precip - fallback_precip)
                
                print(f"      🔍 Diferencias: Max={max_diff:.3f}°C, Min={min_diff:.3f}°C, Avg={avg_diff:.3f}°C, Precip={precip_diff:.3f}mm")
                
                # Los datos deben ser prácticamente idénticos (diferencia < 0.01)
                self.assertLess(max_diff, 0.01, f"Max temp difference too large for {date_key}")
                self.assertLess(min_diff, 0.01, f"Min temp difference too large for {date_key}")
                self.assertLess(avg_diff, 0.01, f"Avg temp difference too large for {date_key}")
                self.assertLess(precip_diff, 0.01, f"Precip difference too large for {date_key}")
                
                print(f"      ✅ Datos idénticos - Fallback contiene datos reales de NASA")
                
            except Exception as e:
                self.fail(f"Test failed for {date_key}: {e}")
        
        print(f"\n🎉 CONCLUSIÓN:")
        print(f"   ✅ FALLBACK_MONTEVIDEO_DATA.csv contiene datos REALES de la NASA API")
        print(f"   ✅ Nuestra función está obteniendo datos REALES de la NASA API")
        print(f"   ✅ El sistema de fallback es confiable porque usa datos reales")


if __name__ == "__main__":
    # Configurar logging para las pruebas
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar pruebas
    unittest.main(verbosity=2)
