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

from logic import calculate_weather_risk, calculate_heat_risk, calculate_cold_risk, calculate_precipitation_risk, filter_data_by_month


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
        result = calculate_weather_risk(self.summer_data, "heat", target_month=1)
        
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
        result = calculate_weather_risk(self.winter_data, "cold", target_month=7)
        
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
    
    def test_precipitation_risk_calculation(self):
        """Test precipitation risk calculation through unified function"""
        result = calculate_weather_risk(self.rainy_data, "precipitation", target_month=4)
        
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
            calculate_weather_risk(self.summer_data, "invalid_type", target_month=1)
        
        self.assertIn("Invalid risk_type", str(context.exception))
        self.assertIn("Must be 'heat', 'cold', or 'precipitation'", str(context.exception))
    
    def test_empty_data_handling(self):
        """Test that empty data is handled gracefully for all risk types"""
        # Test all risk types with empty data (should return default values)
        result_heat = calculate_weather_risk(self.empty_data, "heat", target_month=1)
        result_cold = calculate_weather_risk(self.empty_data, "cold", target_month=1)
        result_precip = calculate_weather_risk(self.empty_data, "precipitation", target_month=1)
        
        # All should return UNKNOWN with 0.0 probability
        self.assertEqual(result_heat['probability'], 0.0)
        self.assertEqual(result_heat['risk_level'], 'UNKNOWN')
        self.assertEqual(result_cold['probability'], 0.0)
        self.assertEqual(result_cold['risk_level'], 'UNKNOWN')
        self.assertEqual(result_precip['probability'], 0.0)
        self.assertEqual(result_precip['risk_level'], 'UNKNOWN')
    
    def test_consistency_with_original_functions(self):
        """Test that unified function returns same results as original functions"""
        # Test heat risk consistency
        unified_heat = calculate_weather_risk(self.summer_data, "heat", target_month=1)
        original_heat = calculate_heat_risk(self.summer_data)
        
        self.assertEqual(unified_heat['probability'], original_heat['probability'])
        self.assertEqual(unified_heat['risk_threshold'], original_heat['risk_threshold'])
        self.assertEqual(unified_heat['risk_level'], original_heat['risk_level'])
        
        # Test cold risk consistency
        unified_cold = calculate_weather_risk(self.winter_data, "cold", target_month=7)
        original_cold = calculate_cold_risk(self.winter_data)
        
        self.assertEqual(unified_cold['probability'], original_cold['probability'])
        self.assertEqual(unified_cold['risk_threshold'], original_cold['risk_threshold'])
        self.assertEqual(unified_cold['risk_level'], original_cold['risk_level'])
        
        # Test precipitation risk consistency
        unified_precip = calculate_weather_risk(self.rainy_data, "precipitation", target_month=4)
        original_precip = calculate_precipitation_risk(self.rainy_data)
        
        self.assertEqual(unified_precip['probability'], original_precip['probability'])
        self.assertEqual(unified_precip['risk_threshold'], original_precip['risk_threshold'])
        self.assertEqual(unified_precip['risk_level'], original_precip['risk_level'])
    

class TestFilterDataByMonth(unittest.TestCase):
    """Test cases for the filter_data_by_month function"""
    
    def setUp(self):
        """Set up test data with multiple months"""
        # Create historical data for 5 years with 3 different months
        self.historical_data = pd.DataFrame({
            'Year': [2020] * 36 + [2021] * 36 + [2022] * 36 + [2023] * 36 + [2024] * 36,
            'Month': ([1] * 12 + [6] * 12 + [12] * 12) * 5,
            'Max_Temperature_C': list(range(20, 32)) * 15,
            'Precipitation_mm': list(range(0, 12)) * 15
        })
        
        self.empty_data = pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C'])
        
        self.no_month_column = pd.DataFrame({
            'Year': [2020, 2021, 2022],
            'Max_Temperature_C': [25.0, 26.0, 27.0]
        })
    
    def test_filter_by_month_january(self):
        """Test filtering data for January (month 1)"""
        result = filter_data_by_month(self.historical_data, 1)
        
        # Should have 5 years * 12 days = 60 records for January
        self.assertEqual(len(result), 60)
        
        # All records should be from month 1
        self.assertTrue(all(result['Month'] == 1))
        
        # Should have all required columns
        self.assertIn('Year', result.columns)
        self.assertIn('Month', result.columns)
        self.assertIn('Max_Temperature_C', result.columns)
    
    def test_filter_by_month_june(self):
        """Test filtering data for June (month 6)"""
        result = filter_data_by_month(self.historical_data, 6)
        
        # Should have 5 years * 12 days = 60 records for June
        self.assertEqual(len(result), 60)
        
        # All records should be from month 6
        self.assertTrue(all(result['Month'] == 6))
    
    def test_filter_by_month_december(self):
        """Test filtering data for December (month 12)"""
        result = filter_data_by_month(self.historical_data, 12)
        
        # Should have 5 years * 12 days = 60 records for December
        self.assertEqual(len(result), 60)
        
        # All records should be from month 12
        self.assertTrue(all(result['Month'] == 12))
    
    def test_filter_by_month_no_matches(self):
        """Test filtering for a month that doesn't exist in data"""
        result = filter_data_by_month(self.historical_data, 13)  # Invalid month
        
        # Should return empty DataFrame
        self.assertEqual(len(result), 0)
        self.assertTrue(result.empty)
    
    def test_filter_by_month_empty_data(self):
        """Test filtering with empty historical data"""
        result = filter_data_by_month(self.empty_data, 1)
        
        # Should return empty DataFrame
        self.assertEqual(len(result), 0)
        self.assertTrue(result.empty)
    
    def test_filter_by_month_no_month_column(self):
        """Test filtering when Month column doesn't exist"""
        result = filter_data_by_month(self.no_month_column, 1)
        
        # Should return original data (with warning)
        self.assertEqual(len(result), 3)
        self.assertEqual(list(result['Year']), [2020, 2021, 2022])


class TestCalculateWeatherRiskWithTargetMonth(unittest.TestCase):
    """Test cases for calculate_weather_risk with target_month parameter"""
    
    def setUp(self):
        """Set up test data with historical data across multiple months"""
        # Create data for 2 years with 3 different months
        self.historical_data = pd.DataFrame({
            'Year': [2020] * 36 + [2021] * 36,
            'Month': ([1] * 12 + [6] * 12 + [12] * 12) * 2,
            'Max_Temperature_C': ([35.0] * 12 + [20.0] * 12 + [32.0] * 12) * 2,
            'Min_Temperature_C': ([15.0] * 12 + [5.0] * 12 + [12.0] * 12) * 2,
            'Avg_Temperature_C': ([25.0] * 12 + [12.5] * 12 + [22.0] * 12) * 2,
            'Precipitation_mm': ([0.0] * 12 + [8.0] * 12 + [2.0] * 12) * 2
        })
    
    def test_heat_risk_with_target_month_january(self):
        """Test heat risk calculation for January (summer)"""
        result = calculate_weather_risk(self.historical_data, "heat", target_month=1)
        
        # Should have correct structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        
        # Should have 24 observations (2 years * 12 days for January)
        self.assertEqual(result['total_observations'], 24)
        
        # Probability should be reasonable for summer heat
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
    
    def test_cold_risk_with_target_month_june(self):
        """Test cold risk calculation for June (winter)"""
        result = calculate_weather_risk(self.historical_data, "cold", target_month=6)
        
        # Should have correct structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        
        # Should have 24 observations (2 years * 12 days for June)
        self.assertEqual(result['total_observations'], 24)
        
        # Probability should be reasonable for winter cold
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
    
    def test_precipitation_risk_with_target_month_december(self):
        """Test precipitation risk calculation for December"""
        result = calculate_weather_risk(self.historical_data, "precipitation", target_month=12)
        
        # Should have correct structure
        self.assertIn('probability', result)
        self.assertIn('risk_threshold', result)
        self.assertIn('risk_level', result)
        self.assertIn('total_observations', result)
        
        # Should have 24 observations (2 years * 12 days for December)
        self.assertEqual(result['total_observations'], 24)
        
        # Probability should be reasonable
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 100.0)
    
    def test_different_months_different_results(self):
        """Test that different months produce different risk calculations"""
        result_january = calculate_weather_risk(self.historical_data, "heat", target_month=1)
        result_june = calculate_weather_risk(self.historical_data, "heat", target_month=6)
        
        # January has higher temperatures (35°C) than June (20°C)
        # So January should have a higher risk threshold
        self.assertGreater(result_january['risk_threshold'], result_june['risk_threshold'])
    
    def test_invalid_target_month(self):
        """Test with invalid target month (should filter to empty data)"""
        result = calculate_weather_risk(self.historical_data, "heat", target_month=13)
        
        # Should return default values for empty data
        self.assertEqual(result['probability'], 0.0)
        self.assertEqual(result['risk_level'], "UNKNOWN")
        self.assertEqual(result['total_observations'], 0)
    
    def test_monthly_data_filtering_integration(self):
        """Test that monthly filtering works correctly with risk calculation"""
        # Create data with clear differences between months
        test_data = pd.DataFrame({
            'Year': [2020] * 36 + [2021] * 36,
            'Month': ([1] * 12 + [6] * 12 + [12] * 12) * 2,
            'Max_Temperature_C': [40.0] * 12 + [10.0] * 12 + [38.0] * 12 + [40.0] * 12 + [10.0] * 12 + [38.0] * 12,
            'Min_Temperature_C': [20.0] * 72,
            'Avg_Temperature_C': [30.0] * 72,
            'Precipitation_mm': [0.0] * 72
        })
        
        # January should have very high temperatures (40°C)
        result_jan = calculate_weather_risk(test_data, "heat", target_month=1)
        self.assertGreater(result_jan['risk_threshold'], 35.0)
        
        # June should have much lower temperatures (10°C)
        result_jun = calculate_weather_risk(test_data, "cold", target_month=6)
        self.assertLess(result_jun['risk_threshold'], 15.0)
    
    def test_consistency_with_filter_then_calculate(self):
        """Test that calculate_weather_risk is equivalent to filter then calculate"""
        # Use unified function
        unified_result = calculate_weather_risk(self.historical_data, "heat", target_month=1)
        
        # Use filter then calculate directly
        filtered_data = filter_data_by_month(self.historical_data, 1)
        direct_result = calculate_heat_risk(filtered_data)
        
        # Results should be identical
        self.assertEqual(unified_result['probability'], direct_result['probability'])
        self.assertEqual(unified_result['risk_threshold'], direct_result['risk_threshold'])
        self.assertEqual(unified_result['risk_level'], direct_result['risk_level'])
        self.assertEqual(unified_result['total_observations'], direct_result['total_observations'])


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
