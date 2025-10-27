#!/usr/bin/env python3
"""
Test script for the /planb endpoint
Tests the AI-powered Plan B generation functionality
"""

import requests
import json
from datetime import datetime

def test_planb_endpoint():
    """Test the /planb endpoint with different scenarios"""
    
    # Base URL for the API
    base_url = "http://localhost:8000"
    planb_url = f"{base_url}/planb"
    
    print("Testing /planb endpoint...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "High Risk Beach Activity",
            "data": {
                "risk_level": "HIGH",
                "activity": "beach",
                "location": "Montevideo, Uruguay",
                "date": "2024-12-16"
            }
        },
        {
            "name": "Moderate Risk Picnic",
            "data": {
                "risk_level": "MODERATE",
                "activity": "picnic",
                "location": "Punta del Este, Uruguay",
                "date": "2024-12-20"
            }
        },
        {
            "name": "Low Risk (Should return no Plan B needed)",
            "data": {
                "risk_level": "LOW",
                "activity": "running",
                "location": "Montevideo, Uruguay",
                "date": "2024-12-25"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Make POST request to /planb endpoint
            response = requests.post(
                planb_url,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS: {result.get('message', 'No message')}")
                
                # Check if we have Plan B suggestions
                suggestions = result.get('plan_b_suggestions', [])
                if suggestions:
                    print(f"Generated {len(suggestions)} Plan B suggestions:")
                    for j, suggestion in enumerate(suggestions, 1):
                        print(f"   {j}. {suggestion.get('name', 'Unknown')}")
                        print(f"      {suggestion.get('description', 'No description')}")
                else:
                    print("No Plan B suggestions (as expected for low risk)")
                
                # Show AI model used
                ai_model = result.get('ai_model', 'Unknown')
                print(f"AI Model: {ai_model}")
                
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("CONNECTION ERROR: Make sure the FastAPI server is running on localhost:8000")
            print("   Start the server with: python api.py")
            break
        except requests.exceptions.Timeout:
            print("TIMEOUT: Request took too long")
        except Exception as e:
            print(f"UNEXPECTED ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

def test_endpoint_availability():
    """Test if the endpoint is available"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            if 'plan_b' in endpoints:
                print("SUCCESS: /planb endpoint is available in the API")
                return True
            else:
                print("ERROR: /planb endpoint not found in API endpoints")
                return False
        else:
            print(f"ERROR: API not responding: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"ERROR: Error checking endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    print("Plan B Endpoint Test Suite")
    print("=" * 50)
    
    # First check if endpoint is available
    if test_endpoint_availability():
        test_planb_endpoint()
    else:
        print("\nTo start the server, run:")
        print("   cd backend")
        print("   python api.py")
        print("\n   Then run this test again.")
