"""
Tests para análisis de tendencias climáticas
NASA Weather Risk Navigator - Test Suite
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Agregar el directorio padre al path para importar logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import analyze_climate_change_trend, get_climate_trend_data


class TestClimateTrendAnalysis(unittest.TestCase):
    """Tests para análisis científico de tendencias climáticas"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Datos de prueba con 20 años (2004-2023) con tendencia de calentamiento
        self.years = list(range(2004, 2024))  # 20 años
        # Simular calentamiento gradual: +1.5°C en 20 años (0.075°C por año)
        base_temp = 18.0  # Temperatura base de Montevideo
        temperatures = [base_temp + (i * 0.075) for i in range(20)]
        
        self.test_data = pd.DataFrame({
            'Year': self.years,
            'Month': [3] * 20,  # Marzo
            'Max_Temperature_C': [t + 8 for t in temperatures],  # Max = avg + 8°C
            'Min_Temperature_C': [t - 8 for t in temperatures],  # Min = avg - 8°C
            'Avg_Temperature_C': temperatures,  # T2M - temperatura promedio diaria
            'Precipitation_mm': [5.0] * 20
        })
        
        # Datos de prueba con tendencia de enfriamiento
        cooling_temps = [base_temp - (i * 0.05) for i in range(20)]  # -1.0°C en 20 años
        self.cooling_data = pd.DataFrame({
            'Year': self.years,
            'Month': [3] * 20,
            'Max_Temperature_C': [t + 8 for t in cooling_temps],
            'Min_Temperature_C': [t - 8 for t in cooling_temps],
            'Avg_Temperature_C': cooling_temps,
            'Precipitation_mm': [5.0] * 20
        })
        
        # Datos de prueba estables (sin tendencia)
        stable_temps = [base_temp + np.random.normal(0, 0.2) for _ in range(20)]
        self.stable_data = pd.DataFrame({
            'Year': self.years,
            'Month': [3] * 20,
            'Max_Temperature_C': [t + 8 for t in stable_temps],
            'Min_Temperature_C': [t - 8 for t in stable_temps],
            'Avg_Temperature_C': stable_temps,
            'Precipitation_mm': [5.0] * 20
        })
    
    def test_significant_warming_trend(self):
        """Test: Detección de calentamiento significativo (≥1.0°C)"""
        result = analyze_climate_change_trend(self.test_data)
        
        # Verificar clasificación
        self.assertEqual(result['trend_status'], 'SIGNIFICANT_WARMING')
        
        # Verificar períodos
        self.assertEqual(result['early_years'], [2004, 2005, 2006, 2007, 2008])
        self.assertEqual(result['recent_years'], [2019, 2020, 2021, 2022, 2023])
        
        # Verificar diferencias
        self.assertGreaterEqual(result['difference'], 1.0)
        self.assertGreater(result['recent_period_mean'], result['early_period_mean'])
        
        # Verificar metodología científica
        self.assertEqual(result['methodology'], 'IPCC/WMO standard analysis')
        self.assertEqual(result['data_period'], '20 years (2004-2023)')
        
        # Verificar mensaje
        self.assertIn('SIGNIFICANT WARMING', result['message'])
        self.assertIn('IPCC threshold exceeded', result['message'])
    
    def test_insufficient_data(self):
        """Test: Manejo de datos insuficientes"""
        # Datos con menos de 10 años
        short_data = self.test_data.head(5)  # Solo 5 años
        result = analyze_climate_change_trend(short_data)
        
        self.assertEqual(result['trend_status'], 'INSUFFICIENT_DATA')
        self.assertIn('WMO requires minimum 10 years', result['message'])
    
    def test_empty_data(self):
        """Test: Manejo de datos vacíos"""
        empty_data = pd.DataFrame()
        result = analyze_climate_change_trend(empty_data)
        
        self.assertEqual(result['trend_status'], 'UNKNOWN')
        self.assertEqual(result['message'], "No data available for trend analysis.")
    
    def test_cooling_trend(self):
        """Test: Detección de tendencia de enfriamiento"""
        result = analyze_climate_change_trend(self.cooling_data)
        
        # Verificar clasificación
        self.assertEqual(result['trend_status'], 'COOLING_TREND')
        
        # Verificar diferencias
        self.assertLessEqual(result['difference'], -0.5)
        self.assertLess(result['recent_period_mean'], result['early_period_mean'])
        
        # Verificar mensaje
        self.assertIn('COOLING TREND', result['message'])
        self.assertIn('heat risk is decreasing', result['message'])
    
    def test_stable_climate(self):
        """Test: Detección de clima estable"""
        result = analyze_climate_change_trend(self.stable_data)
        
        # Verificar clasificación
        self.assertEqual(result['trend_status'], 'STABLE')
        
        # Verificar diferencias (debe ser < 0.5°C)
        self.assertLess(abs(result['difference']), 0.5)
        
        # Verificar mensaje
        self.assertIn('STABLE CLIMATE', result['message'])
        self.assertIn('natural climate variability', result['message'])
    
    def test_t2m_variable_usage(self):
        """Test: Verificación de uso de variable T2M (Avg_Temperature_C)"""
        result = analyze_climate_change_trend(self.test_data)
        
        # Verificar que se usan temperaturas promedio (T2M)
        early_mean = self.test_data[self.test_data['Year'].isin([2004, 2005, 2006, 2007, 2008])]['Avg_Temperature_C'].mean()
        recent_mean = self.test_data[self.test_data['Year'].isin([2019, 2020, 2021, 2022, 2023])]['Avg_Temperature_C'].mean()
        
        self.assertAlmostEqual(result['early_period_mean'], early_mean, places=2)
        self.assertAlmostEqual(result['recent_period_mean'], recent_mean, places=2)
    
    def test_period_calculation(self):
        """Test: Verificación de cálculo de períodos (primeros 5 vs últimos 5 años)"""
        result = analyze_climate_change_trend(self.test_data)
        
        # Verificar años del período inicial
        expected_early_years = sorted(self.test_data['Year'].unique())[:5]
        self.assertEqual(result['early_years'], expected_early_years)
        
        # Verificar años del período reciente
        expected_recent_years = sorted(self.test_data['Year'].unique())[-5:]
        self.assertEqual(result['recent_years'], expected_recent_years)
    
    def test_scientific_thresholds(self):
        """Test: Verificación de umbrales científicos IPCC/WMO"""
        # Crear datos con diferencias específicas para probar umbrales
        test_cases = [
            (1.2, 'SIGNIFICANT_WARMING'),  # ≥ 1.0°C
            (0.7, 'WARMING_TREND'),        # ≥ 0.5°C
            (-0.6, 'COOLING_TREND'),       # ≤ -0.5°C
            (0.3, 'STABLE')                # < 0.5°C
        ]
        
        for difference, expected_status in test_cases:
            with self.subTest(difference=difference):
                # Crear datos con diferencia específica
                early_temp = 18.0
                recent_temp = early_temp + difference
                
                test_data = pd.DataFrame({
                    'Year': self.years,
                    'Month': [3] * 20,
                    'Avg_Temperature_C': [early_temp] * 10 + [recent_temp] * 10,
                    'Max_Temperature_C': [25.0] * 20,
                    'Min_Temperature_C': [15.0] * 20,
                    'Precipitation_mm': [5.0] * 20
                })
                
                result = analyze_climate_change_trend(test_data)
                self.assertEqual(result['trend_status'], expected_status)


class TestGetClimateTrendData(unittest.TestCase):
    """Tests para función de integración con API"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Datos de prueba con tendencia de calentamiento
        years = list(range(2004, 2024))
        temperatures = [18.0 + (i * 0.075) for i in range(20)]
        
        self.test_data = pd.DataFrame({
            'Year': years,
            'Month': [3] * 20,
            'Max_Temperature_C': [t + 8 for t in temperatures],
            'Min_Temperature_C': [t - 8 for t in temperatures],
            'Avg_Temperature_C': temperatures,
            'Precipitation_mm': [5.0] * 20
        })
    
    def test_successful_analysis(self):
        """Test: Análisis exitoso con datos válidos"""
        result = get_climate_trend_data(self.test_data)
        
        # Verificar estructura de respuesta
        self.assertIn('plot_data', result)
        self.assertIn('climate_trend', result)
        
        # Verificar que plot_data está vacío (sin visualizaciones)
        self.assertEqual(result['plot_data'], [])
        
        # Verificar contenido del análisis
        climate_text = result['climate_trend']
        self.assertIn('Climate Trend Analysis Results', climate_text)
        self.assertIn('IPCC/WMO Methodology', climate_text)
        self.assertIn('SIGNIFICANT_WARMING', climate_text)
        self.assertIn('T2M', climate_text)  # Variable científica
    
    def test_empty_data_handling(self):
        """Test: Manejo de datos vacíos"""
        empty_data = pd.DataFrame()
        result = get_climate_trend_data(empty_data)
        
        self.assertEqual(result['plot_data'], [])
        self.assertEqual(result['climate_trend'], "No sufficient historical data found to perform climate trend analysis.")
    
    def test_error_handling(self):
        """Test: Manejo de errores en el análisis"""
        # Crear datos con estructura incorrecta para provocar error
        invalid_data = pd.DataFrame({
            'Year': [2004, 2005],
            'Invalid_Column': [1, 2]  # Sin Avg_Temperature_C
        })
        
        result = get_climate_trend_data(invalid_data)
        
        # Debe manejar el error graciosamente
        self.assertIn('plot_data', result)
        self.assertIn('climate_trend', result)
        # Verificar que maneja datos insuficientes correctamente
        self.assertIn('Insufficient data', result['climate_trend'])
    
    def test_api_format(self):
        """Test: Formato correcto para API"""
        result = get_climate_trend_data(self.test_data)
        
        # Verificar que el formato es apropiado para la API
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['plot_data'], list)
        self.assertIsInstance(result['climate_trend'], str)
        
        # Verificar que el texto contiene información científica
        climate_text = result['climate_trend']
        self.assertIn('Status:', climate_text)
        self.assertIn('Methodology:', climate_text)
        self.assertIn('Data Period:', climate_text)
        self.assertIn('Temperature Change:', climate_text)
        self.assertIn('Scientific Assessment:', climate_text)


class TestClimateTrendIntegration(unittest.TestCase):
    """Tests de integración completa"""
    
    def test_end_to_end_analysis(self):
        """Test: Análisis completo de extremo a extremo"""
        # Simular datos reales de Montevideo con tendencia de calentamiento
        years = list(range(2004, 2024))
        # Tendencia realista: +1.2°C en 20 años
        base_temp = 17.5
        temperatures = [base_temp + (i * 0.06) for i in range(20)]
        
        real_data = pd.DataFrame({
            'Year': years,
            'Month': [3] * 20,  # Marzo
            'Max_Temperature_C': [t + 7.5 for t in temperatures],
            'Min_Temperature_C': [t - 7.5 for t in temperatures],
            'Avg_Temperature_C': temperatures,
            'Precipitation_mm': [4.5] * 20
        })
        
        # Análisis científico
        trend_result = analyze_climate_change_trend(real_data)
        
        # Verificar resultados científicos (ajustar expectativa según datos reales)
        self.assertIn(trend_result['trend_status'], ['SIGNIFICANT_WARMING', 'WARMING_TREND'])
        self.assertGreater(trend_result['difference'], 0.5)  # Al menos tendencia de calentamiento
        
        # Integración con API
        api_result = get_climate_trend_data(real_data)
        
        # Verificar integración
        self.assertIn(trend_result['trend_status'], api_result['climate_trend'])
        self.assertIn('IPCC/WMO', api_result['climate_trend'])
        
        print(f"\n✅ Análisis completo exitoso:")
        print(f"   Status: {trend_result['trend_status']}")
        print(f"   Cambio: {trend_result['difference']:+.2f}°C")
        print(f"   Metodología: {trend_result['methodology']}")
    
    def test_different_months(self):
        """Test: Análisis con diferentes meses"""
        months_to_test = [1, 6, 12]  # Enero, Junio, Diciembre
        
        for month in months_to_test:
            with self.subTest(month=month):
                # Crear datos para el mes específico
                years = list(range(2004, 2024))
                temperatures = [18.0 + (i * 0.075) for i in range(20)]
                
                month_data = pd.DataFrame({
                    'Year': years,
                    'Month': [month] * 20,
                    'Max_Temperature_C': [t + 8 for t in temperatures],
                    'Min_Temperature_C': [t - 8 for t in temperatures],
                    'Avg_Temperature_C': temperatures,
                    'Precipitation_mm': [5.0] * 20
                })
                
                result = analyze_climate_change_trend(month_data)
                
                # Verificar que el análisis funciona para cualquier mes
                self.assertIn(result['trend_status'], 
                            ['SIGNIFICANT_WARMING', 'WARMING_TREND', 'COOLING_TREND', 'STABLE'])
                self.assertEqual(result['methodology'], 'IPCC/WMO standard analysis')


if __name__ == '__main__':
    # Configurar logging para las pruebas
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar pruebas
    unittest.main(verbosity=2)
