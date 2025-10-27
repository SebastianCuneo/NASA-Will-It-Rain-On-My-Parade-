"""
Unit tests for the unified calculate_weather_risk function
Tests all three risk types: heat, cold, and precipitation
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic import calculate_weather_risk, calculate_adverse_probability, calculate_cold_risk, calculate_precipitation_risk


class TestCalculateWeatherRisk(unittest.TestCase):
    """Test cases for the unified calculate_weather_risk function"""
    
    def setUp(self):
        """Set up test data for all risk types"""
        # Create sample monthly data for testing
        np.random.seed(42)  # For reproducible tests
        
        # Sample data for heat risk testing (summer month)
        self.summer_data = pd.DataFrame({
            'Year': [2020, 2020, 2020, 2021, 2021, 2021, 2022, 2022, 2022],
            'Month': [1, 1, 1, 1, 1, 1, 1, 1, 1],  # January (summer in Uruguay)
            'Max_Temperature_C': [32.0, 35.0, 38.0, 30.0, 33.0, 36.0, 29.0, 34.0, 37.0],
            'Precipitation_mm': [0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        })
        
        # Sample data for cold risk testing (winter month)
        self.winter_data = pd.DataFrame({
            'Year': [2020, 2020, 2020, 2021, 2021, 2021, 2022, 2022, 2022],
            'Month': [7, 7, 7, 7, 7, 7, 7, 7, 7],  # July (winter in Uruguay)
            'Max_Temperature_C': [12.0, 15.0, 18.0, 14.0, 16.0, 19.0, 13.0, 17.0, 20.0],
            'Precipitation_mm': [5.0, 0.0, 0.0, 8.0, 0.0, 0.0, 3.0, 0.0, 0.0]
        })
        
        # Sample data for precipitation risk testing
        self.rainy_data = pd.DataFrame({
            'Year': [2020, 2020, 2020, 2021, 2021, 2021, 2022, 2022, 2022],
            'Month': [4, 4, 4, 4, 4, 4, 4, 4, 4],  # April
            'Max_Temperature_C': [22.0, 24.0, 26.0, 23.0, 25.0, 27.0, 21.0, 24.0, 26.0],
            'Precipitation_mm': [15.0, 0.0, 8.0, 12.0, 0.0, 6.0, 20.0, 0.0, 4.0]
        })
        
        # Empty data for edge case testing
        self.empty_data = pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'])
    
    def test_heat_risk_calculation(self):
        """Test heat risk calculation through unified function"""
        result = calculate_weather_risk(self.summer_data, "heat")
        
        # Verify return structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('status_message', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        self.assertIn('adverse_count', result)
        
        # Verify data types
        self.assertIsInstance(result['probability'], (int, float))
        self.assertIsInstance(result['risk_threshold'], (int, float))
        self.assertIsInstance(result['status_message'], str)
        self.assertIsInstance(result['risk_level'], str)
        self.assertIsInstance(result['total_observations'], int)
        self.assertIsInstance(result['adverse_count'], int)
        
        # Verify values are reasonable
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
        self.assertGreater(result['risk_threshold'], 0.0)
        self.assertIn(result['risk_level'], ['HIGH', 'MODERATE', 'LOW', 'MINIMAL', 'UNKNOWN'])
    
    def test_cold_risk_calculation(self):
        """Test cold risk calculation through unified function"""
        result = calculate_weather_risk(self.winter_data, "cold", "beach")
        
        # Verify return structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('status_message', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        self.assertIn('adverse_count', result)
        self.assertIn('season', result)
        self.assertIn('activity', result)
        
        # Verify data types
        self.assertIsInstance(result['probability'], (int, float))
        self.assertIsInstance(result['risk_threshold'], (int, float))
        self.assertIsInstance(result['status_message'], str)
        self.assertIsInstance(result['risk_level'], str)
        self.assertIsInstance(result['total_observations'], int)
        self.assertIsInstance(result['adverse_count'], int)
        self.assertIsInstance(result['season'], str)
        self.assertEqual(result['activity'], 'beach')
        
        # Verify values are reasonable
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
        self.assertGreater(result['risk_threshold'], 0.0)
        self.assertIn(result['risk_level'], ['HIGH', 'MODERATE', 'LOW', 'MINIMAL', 'UNKNOWN'])
        self.assertEqual(result['season'], 'Winter')
    
    def test_precipitation_risk_calculation(self):
        """Test precipitation risk calculation through unified function"""
        result = calculate_weather_risk(self.rainy_data, "precipitation")
        
        # Verify return structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('status_message', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        self.assertIn('adverse_count', result)
        
        # Verify data types
        self.assertIsInstance(result['probability'], (int, float))
        self.assertIsInstance(result['risk_threshold'], (int, float))
        self.assertIsInstance(result['status_message'], str)
        self.assertIsInstance(result['risk_level'], str)
        self.assertIsInstance(result['total_observations'], int)
        self.assertIsInstance(result['adverse_count'], int)
        
        # Verify values are reasonable
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
        self.assertGreaterEqual(result['risk_threshold'], 0.0)
        self.assertIn(result['risk_level'], ['HIGH', 'MODERATE', 'LOW', 'MINIMAL', 'UNKNOWN'])
    
    def test_invalid_risk_type(self):
        """Test that invalid risk type raises ValueError"""
        with self.assertRaises(ValueError) as context:
            calculate_weather_risk(self.summer_data, "invalid_type")
        
        self.assertIn("Invalid risk_type", str(context.exception))
        self.assertIn("Must be 'heat', 'cold', or 'precipitation'", str(context.exception))
    
    def test_empty_data_handling(self):
        """Test that empty data is handled gracefully for all risk types"""
        # Test heat risk with empty data (should raise ValueError)
        with self.assertRaises(ValueError):
            calculate_weather_risk(self.empty_data, "heat")
        
        # Test cold risk with empty data (should return default values)
        result_cold = calculate_weather_risk(self.empty_data, "cold")
        self.assertEqual(result_cold['probability'], 0.0)
        self.assertEqual(result_cold['risk_level'], 'UNKNOWN')
        
        # Test precipitation risk with empty data (should return default values)
        result_precip = calculate_weather_risk(self.empty_data, "precipitation")
        self.assertEqual(result_precip['probability'], 0.0)
        self.assertEqual(result_precip['risk_level'], 'UNKNOWN')
    
    def test_consistency_with_original_functions(self):
        """Test that unified function returns same results as original functions"""
        # Test heat risk consistency
        unified_heat = calculate_weather_risk(self.summer_data, "heat")
        original_heat = calculate_adverse_probability(self.summer_data)
        
        self.assertEqual(unified_heat['probability'], original_heat['probability'])
        self.assertEqual(unified_heat['risk_threshold'], original_heat['risk_threshold'])
        self.assertEqual(unified_heat['risk_level'], original_heat['risk_level'])
        
        # Test cold risk consistency
        unified_cold = calculate_weather_risk(self.winter_data, "cold", "picnic")
        original_cold = calculate_cold_risk(self.winter_data, "picnic")
        
        self.assertEqual(unified_cold['probability'], original_cold['probability'])
        self.assertEqual(unified_cold['risk_threshold'], original_cold['risk_threshold'])
        self.assertEqual(unified_cold['risk_level'], original_cold['risk_level'])
        self.assertEqual(unified_cold['activity'], original_cold['activity'])
        
        # Test precipitation risk consistency
        unified_precip = calculate_weather_risk(self.rainy_data, "precipitation")
        original_precip = calculate_precipitation_risk(self.rainy_data)
        
        self.assertEqual(unified_precip['probability'], original_precip['probability'])
        self.assertEqual(unified_precip['risk_threshold'], original_precip['risk_threshold'])
        self.assertEqual(unified_precip['risk_level'], original_precip['risk_level'])
    
    def test_activity_parameter_handling(self):
        """Test that activity parameter is properly handled for different risk types"""
        # Activity should only affect cold risk
        result_heat = calculate_weather_risk(self.summer_data, "heat", "beach")
        result_cold = calculate_weather_risk(self.winter_data, "cold", "beach")
        result_precip = calculate_weather_risk(self.rainy_data, "precipitation", "beach")
        
        # Heat and precipitation should not have activity field
        self.assertNotIn('activity', result_heat)
        self.assertNotIn('activity', result_precip)
        
        # Cold should have activity field
        self.assertIn('activity', result_cold)
        self.assertEqual(result_cold['activity'], 'beach')
    
    def test_different_activities_for_cold_risk(self):
        """Test that different activities produce different cold risk thresholds"""
        result_beach = calculate_weather_risk(self.winter_data, "cold", "beach")
        result_picnic = calculate_weather_risk(self.winter_data, "cold", "picnic")
        result_running = calculate_weather_risk(self.winter_data, "cold", "running")
        result_general = calculate_weather_risk(self.winter_data, "cold", "general")
        
        # Different activities should have different thresholds
        # (This tests the underlying get_seasonal_cold_threshold function)
        self.assertNotEqual(result_beach['risk_threshold'], result_picnic['risk_threshold'])
        self.assertNotEqual(result_beach['risk_threshold'], result_running['risk_threshold'])
        
        # All should have activity field set correctly
        self.assertEqual(result_beach['activity'], 'beach')
        self.assertEqual(result_picnic['activity'], 'picnic')
        self.assertEqual(result_running['activity'], 'running')
        self.assertEqual(result_general['activity'], 'general')


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
