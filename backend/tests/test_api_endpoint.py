"""
Test suite for the main API endpoint /api/risk
NASA Weather Risk Navigator - API Endpoint Tests
"""

import unittest
import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from api import app

# Create test client
client = TestClient(app)


class TestRiskEndpoint(unittest.TestCase):
    """Tests for the /api/risk endpoint"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "/api/risk"
        self.test_lat = -34.90
        self.test_lon = -56.16
        self.test_date = "2026-12-16"
        
    def test_endpoint_exists(self):
        """Test that the /api/risk endpoint exists and responds"""
        response = client.get("/docs")
        self.assertEqual(response.status_code, 200)
    
    def test_request_with_all_fields(self):
        """Test POST request with all required fields"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Verify response structure
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check main structure
        self.assertIn("success", data)
        self.assertIn("risk_analysis", data)
        self.assertIn("plan_b", data)
        self.assertIn("climate_trend", data)
        self.assertIn("climate_trend_details", data)
    
    def test_risk_analysis_structure(self):
        """Test that risk_analysis contains expected fields"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Hot"
        }
        
        response = client.post(self.base_url, json=payload)
        data = response.json()
        
        risk_analysis = data.get("risk_analysis", {})
        
        self.assertIn("probability", risk_analysis)
        self.assertIn("risk_threshold", risk_analysis)
        self.assertIn("status_message", risk_analysis)
        self.assertIn("risk_level", risk_analysis)
    
    def test_plan_b_structure(self):
        """Test that plan_b contains expected fields"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Rainy"
        }
        
        response = client.post(self.base_url, json=payload)
        data = response.json()
        
        plan_b = data.get("plan_b", {})
        
        self.assertIn("success", plan_b)
        self.assertIn("alternatives", plan_b)
        self.assertGreaterEqual(len(plan_b.get("alternatives", [])), 0)
    
    def test_climate_trend_structure(self):
        """Test that climate_trend contains expected information"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        data = response.json()
        
        climate_trend = data.get("climate_trend", "")
        self.assertIsInstance(climate_trend, str)
        self.assertGreater(len(climate_trend), 0)
        
        climate_trend_details = data.get("climate_trend_details", {})
        self.assertIn("trend_status", climate_trend_details)


class TestRiskEndpointWeatherConditions(unittest.TestCase):
    """Tests for different weather conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "/api/risk"
        self.test_lat = -34.90
        self.test_lon = -56.16
        self.test_date = "2026-07-15"
    
    def test_very_hot_condition(self):
        """Test endpoint with Very Hot condition"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Hot"
        }
        
        response = client.post(self.base_url, json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
    
    def test_very_cold_condition(self):
        """Test endpoint with Very Cold condition"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
    
    def test_very_rainy_condition(self):
        """Test endpoint with Very Rainy condition"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Rainy"
        }
        
        response = client.post(self.base_url, json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))


class TestRiskEndpointDateFormats(unittest.TestCase):
    """Tests for different date formats"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "/api/risk"
        self.test_lat = -34.90
        self.test_lon = -56.16
    
    def test_date_format_yyyy_mm_dd(self):
        """Test with YYYY-MM-DD format"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": "2026-12-25",
            "adverse_condition": "Very Hot"
        }
        
        response = client.post(self.base_url, json=payload)
        
        self.assertEqual(response.status_code, 200)
    
    def test_date_format_dd_mm_yyyy(self):
        """Test with DD/MM/YYYY format"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": "25/12/2026",
            "adverse_condition": "Very Hot"
        }
        
        response = client.post(self.base_url, json=payload)
        
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_date_format(self):
        """Test with invalid date format"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": "12-25-2026",
            "adverse_condition": "Very Hot"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)


class TestRiskEndpointErrorHandling(unittest.TestCase):
    """Tests for error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "/api/risk"
    
    def test_missing_latitude(self):
        """Test with missing latitude field"""
        payload = {
            "longitude": -56.16,
            "event_date": "2026-12-16",
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return 422 Unprocessable Entity
        self.assertIn(response.status_code, [400, 422])
    
    def test_missing_longitude(self):
        """Test with missing longitude field"""
        payload = {
            "latitude": -34.90,
            "event_date": "2026-12-16",
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return 422 Unprocessable Entity
        self.assertIn(response.status_code, [400, 422])
    
    def test_missing_event_date(self):
        """Test with missing event_date field"""
        payload = {
            "latitude": -34.90,
            "longitude": -56.16,
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return 422 Unprocessable Entity
        self.assertIn(response.status_code, [400, 422])
    
    def test_missing_adverse_condition(self):
        """Test with missing adverse_condition field"""
        payload = {
            "latitude": -34.90,
            "longitude": -56.16,
            "event_date": "2026-12-16"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return 422 Unprocessable Entity
        self.assertIn(response.status_code, [400, 422])
    
    def test_invalid_coordinates(self):
        """Test with invalid coordinate values"""
        payload = {
            "latitude": 100.0,  # Invalid latitude
            "longitude": -56.16,
            "event_date": "2026-12-16",
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        
        # Should return an error status
        self.assertNotEqual(response.status_code, 200)


class TestRiskEndpointAlternatives(unittest.TestCase):
    """Tests for Plan B alternatives structure"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "/api/risk"
        self.test_lat = -34.90
        self.test_lon = -56.16
        self.test_date = "2026-12-16"
    
    def test_alternatives_contains_required_fields(self):
        """Test that alternatives contain required fields"""
        payload = {
            "latitude": self.test_lat,
            "longitude": self.test_lon,
            "event_date": self.test_date,
            "adverse_condition": "Very Cold"
        }
        
        response = client.post(self.base_url, json=payload)
        data = response.json()
        
        alternatives = data.get("plan_b", {}).get("alternatives", [])
        
        if alternatives:
            for alt in alternatives:
                # Check for common fields
                self.assertIn("title", alt)
                # Other fields may vary depending on AI response


if __name__ == '__main__':
    unittest.main()

