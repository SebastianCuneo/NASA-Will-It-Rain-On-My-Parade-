#!/usr/bin/env python3
"""
NASA Weather Risk Navigator - Gemini AI Plan B Test Script
Test the enhanced Gemini AI integration for Plan B generation
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_plan_b():
    """
    Test the enhanced Gemini AI Plan B generation
    """
    print("🧪 Testing Enhanced Gemini AI Plan B Generation")
    print("=" * 60)
    
    try:
        from logic import generate_plan_b_with_gemini, generate_fallback_plan_b
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Beach Day - Rainy Weather",
                "activity": "beach",
                "weather_condition": "rainy",
                "risk_level": "HIGH",
                "temperature_risk": 15.2,
                "precipitation_risk": 45.8,
                "cold_risk": 8.3
            },
            {
                "name": "Picnic - Hot Weather",
                "activity": "picnic",
                "weather_condition": "hot",
                "risk_level": "MODERATE",
                "temperature_risk": 28.5,
                "precipitation_risk": 12.1,
                "cold_risk": 5.2
            },
            {
                "name": "Running - Cold Weather",
                "activity": "run",
                "weather_condition": "cold",
                "risk_level": "HIGH",
                "temperature_risk": 8.7,
                "precipitation_risk": 15.3,
                "cold_risk": 35.4
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Test {i}: {scenario['name']}")
            print("-" * 40)
            
            # Test Gemini AI
            print("🤖 Testing Gemini AI...")
            gemini_result = generate_plan_b_with_gemini(
                activity=scenario['activity'],
                weather_condition=scenario['weather_condition'],
                risk_level=scenario['risk_level'],
                location="Montevideo, Uruguay",
                season="Summer",
                temperature_risk=scenario['temperature_risk'],
                precipitation_risk=scenario['precipitation_risk'],
                cold_risk=scenario['cold_risk']
            )
            
            if gemini_result.get('success'):
                print("✅ Gemini AI successful!")
                alternatives = gemini_result.get('alternatives', [])
                print(f"Generated {len(alternatives)} alternatives")
                print(f"AI Model: {gemini_result.get('ai_model', 'Unknown')}")
                
                # Show first alternative
                if alternatives:
                    first_alt = alternatives[0]
                    print(f"\nFirst alternative:")
                    print(f"  Title: {first_alt.get('title', 'N/A')}")
                    print(f"  Type: {first_alt.get('type', 'N/A')}")
                    print(f"  Description: {first_alt.get('description', 'N/A')[:100]}...")
                    print(f"  Location: {first_alt.get('location', 'N/A')}")
                    print(f"  Duration: {first_alt.get('duration', 'N/A')}")
                    print(f"  Cost: {first_alt.get('cost', 'N/A')}")
            else:
                print("❌ Gemini AI failed")
                print(f"Error: {gemini_result.get('message', 'Unknown error')}")
                
                # Test fallback
                print("\n🔄 Testing fallback system...")
                fallback_result = generate_fallback_plan_b(
                    activity=scenario['activity'],
                    weather_condition=scenario['weather_condition'],
                    risk_level=scenario['risk_level'],
                    location="Montevideo, Uruguay",
                    season="Summer"
                )
                
                if fallback_result.get('success'):
                    print("✅ Fallback system working!")
                    alternatives = fallback_result.get('alternatives', [])
                    print(f"Generated {len(alternatives)} fallback alternatives")
                else:
                    print("❌ Fallback system also failed")
            
            print("\n" + "=" * 40)
        
        print("\n🎉 All tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_integration():
    """
    Test the API integration with Gemini AI
    """
    print("\n🌐 Testing API Integration")
    print("-" * 40)
    
    try:
        import requests
        import json
        
        # Test API endpoint
        api_url = "http://localhost:8000/api/risk"
        test_payload = {
            "latitude": -34.90,
            "longitude": -56.16,
            "event_date": "15/03/2024",
            "adverse_condition": "Very Rainy",
            "activity": "beach"
        }
        
        print("Sending test request to API...")
        response = requests.post(api_url, json=test_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API request successful!")
                
                plan_b = data.get('data', {}).get('plan_b', {})
                if plan_b.get('success'):
                    print("✅ Plan B generation successful!")
                    alternatives = plan_b.get('alternatives', [])
                    print(f"Generated {len(alternatives)} alternatives")
                    print(f"AI Model: {plan_b.get('ai_model', 'Unknown')}")
                else:
                    print("⚠️ Plan B generation failed")
                    print(f"Error: {plan_b.get('message', 'Unknown error')}")
            else:
                print("❌ API request failed")
                print(f"Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        print("Make sure the backend is running: python -m uvicorn backend.api:app --reload --port 8000")
    except Exception as e:
        print(f"❌ API test failed: {e}")

def main():
    """
    Main test function
    """
    print("🚀 NASA Weather Risk Navigator - Gemini AI Test Suite")
    print("=" * 60)
    
    # Test Gemini AI directly
    gemini_success = test_gemini_plan_b()
    
    # Test API integration
    test_api_integration()
    
    print("\n" + "=" * 60)
    if gemini_success:
        print("🎉 Gemini AI integration is working!")
        print("Plan B generation with AI is ready to use.")
    else:
        print("⚠️ Gemini AI integration has issues")
        print("Check your API key and configuration.")
    
    print("\nNext steps:")
    print("1. Start the backend: python -m uvicorn backend.api:app --reload --port 8000")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Test the application with weather conditions that trigger Plan B")

if __name__ == "__main__":
    main()
