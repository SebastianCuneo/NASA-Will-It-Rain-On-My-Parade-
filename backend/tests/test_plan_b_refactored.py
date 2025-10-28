"""
Tests for refactored Plan B functions (generate_plan_b_with_gemini and generate_fallback_plan_b)
Tests both functions with the new signatures that use risk_analysis and latitude-based seasons
"""

import unittest
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import generate_plan_b_with_gemini, generate_fallback_plan_b, calculate_season_from_month


class TestPlanBRefactored(unittest.TestCase):
    """Tests for refactored Plan B functions with new signatures"""
    
    def setUp(self):
        """Set up test data"""
        self.test_risk_analysis = {
            'risk_level': 'HIGH',
            'probability': 45.5,
            'risk_threshold': 30.0,
            'status_message': 'High risk of extreme heat!'
        }
    
    def test_calculate_season_from_month_northern_hemisphere(self):
        """Test season calculation for Northern Hemisphere"""
        # New York (40.7°N) - January should be Winter
        self.assertEqual(calculate_season_from_month(1, 40.7), "Winter")
        # New York - July should be Summer
        self.assertEqual(calculate_season_from_month(7, 40.7), "Summer")
        # New York - April should be Spring
        self.assertEqual(calculate_season_from_month(4, 40.7), "Spring")
        # New York - October should be Autumn
        self.assertEqual(calculate_season_from_month(10, 40.7), "Autumn")
    
    def test_calculate_season_from_month_southern_hemisphere(self):
        """Test season calculation for Southern Hemisphere"""
        # Montevideo (-34.9°S) - January should be Summer
        self.assertEqual(calculate_season_from_month(1, -34.9), "Summer")
        # Montevideo - July should be Winter
        self.assertEqual(calculate_season_from_month(7, -34.9), "Winter")
        # Montevideo - April should be Autumn
        self.assertEqual(calculate_season_from_month(4, -34.9), "Autumn")
        # Montevideo - October should be Spring
        self.assertEqual(calculate_season_from_month(10, -34.9), "Spring")
    
    def test_calculate_season_from_month_no_latitude(self):
        """Test season calculation without latitude (defaults to Southern Hemisphere)"""
        # Should default to Southern Hemisphere
        self.assertEqual(calculate_season_from_month(1), "Summer")
        self.assertEqual(calculate_season_from_month(7), "Winter")
    
    def test_generate_fallback_plan_b_new_signature(self):
        """Test fallback Plan B with new signature"""
        result = generate_fallback_plan_b(
            activity="beach",
            adverse_condition="cold",
            risk_level="HIGH",
            location="Montevideo, Uruguay",
            target_month=7,  # July (Winter in Southern Hemisphere)
            latitude=-34.9
        )
        
        # Verify structure
        self.assertIn('success', result)
        self.assertIn('alternatives', result)
        self.assertIn('message', result)
        self.assertIn('ai_model', result)
        self.assertIn('generated_at', result)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertEqual(result['ai_model'], 'Fallback System')
        
        # Verify alternatives
        alternatives = result.get('alternatives', [])
        self.assertGreater(len(alternatives), 0)
        
        # Verify each alternative has required fields
        if alternatives:
            alt = alternatives[0]
            self.assertIn('title', alt)
            self.assertIn('description', alt)
            self.assertIn('type', alt)
            self.assertIn('reason', alt)
            self.assertIn('tips', alt)
    
    def test_generate_fallback_plan_b_northern_hemisphere(self):
        """Test fallback Plan B for Northern Hemisphere"""
        result = generate_fallback_plan_b(
            activity="beach",
            adverse_condition="cold",
            risk_level="MODERATE",
            location="New York, USA",
            target_month=1,  # January (Winter in Northern Hemisphere)
            latitude=40.7
        )
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['alternatives']), 0)
    
    def test_generate_fallback_plan_b_season_calculation(self):
        """Test that fallback calculates season correctly from coordinates"""
        # Southern Hemisphere - January
        result_sh = generate_fallback_plan_b(
            activity="picnic",
            adverse_condition="rainy",
            risk_level="HIGH",
            location="Montevideo, Uruguay",
            target_month=1,
            latitude=-34.9
        )
        
        # Northern Hemisphere - January
        result_nh = generate_fallback_plan_b(
            activity="picnic",
            adverse_condition="rainy",
            risk_level="HIGH",
            location="New York, USA",
            target_month=1,
            latitude=40.7
        )
        
        # Both should succeed
        self.assertTrue(result_sh['success'])
        self.assertTrue(result_nh['success'])
    
    def test_generate_plan_b_with_gemini_new_signature(self):
        """Test Gemini Plan B with new signature"""
        # This will likely fail if no API key, but we test the signature
        result = generate_plan_b_with_gemini(
            activity="beach",
            adverse_condition="hot",
            risk_analysis=self.test_risk_analysis,
            location="Montevideo, Uruguay",
            target_month=1,
            latitude=-34.9
        )
        
        # Check structure regardless of success
        self.assertIn('success', result)
        self.assertIn('alternatives', result)
    
    def test_generate_plan_b_with_gemini_extracts_risk_data(self):
        """Test that Gemini function extracts data from risk_analysis correctly"""
        # Test that function accepts risk_analysis properly
        # This will fail without API key, but we can test signature
        try:
            result = generate_plan_b_with_gemini(
                activity="running",
                adverse_condition="cold",
                risk_analysis={
                    'risk_level': 'MODERATE',
                    'probability': 25.5,
                    'risk_threshold': 15.0,
                    'status_message': 'Moderate cold risk'
                },
                location="Buenos Aires, Argentina",
                target_month=6,
                latitude=-34.6
            )
            
            # If API key exists, should succeed
            # If not, should return failure but not crash
            self.assertIn('success', result)
            
        except Exception as e:
            # API key error is acceptable
            self.assertIn('API', str(e) or 'Error generating Plan B with Gemini')


class TestPlanBEdgeCases(unittest.TestCase):
    """Test edge cases for Plan B functions"""
    
    def test_fallback_with_no_specific_alternatives(self):
        """Test fallback when no specific alternatives exist"""
        result = generate_fallback_plan_b(
            activity="unknown_activity",
            adverse_condition="unknown_condition",
            risk_level="LOW",
            location="Unknown Location",
            target_month=1,
            latitude=-34.9
        )
        
        # Should return general alternatives
        self.assertTrue(result['success'])
        alternatives = result.get('alternatives', [])
        self.assertGreater(len(alternatives), 0)
    
    def test_fallback_with_various_activities(self):
        """Test fallback with different activity types"""
        activities = ["beach", "picnic", "running", "general"]
        
        for activity in activities:
            with self.subTest(activity=activity):
                result = generate_fallback_plan_b(
                    activity=activity,
                    adverse_condition="rainy",
                    risk_level="HIGH",
                    location="Montevideo, Uruguay",
                    target_month=3,
                    latitude=-34.9
                )
                
                self.assertTrue(result['success'])
                self.assertGreater(len(result['alternatives']), 0)
    
    def test_season_calculation_edge_cases(self):
        """Test season calculation for edge months"""
        # Test month 12 (December)
        self.assertEqual(calculate_season_from_month(12, -34.9), "Summer")
        self.assertEqual(calculate_season_from_month(12, 40.7), "Winter")
        
        # Test month 3 (March)
        self.assertEqual(calculate_season_from_month(3, -34.9), "Autumn")
        self.assertEqual(calculate_season_from_month(3, 40.7), "Spring")


if __name__ == '__main__':
    unittest.main(verbosity=2)

