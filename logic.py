"""
The Parade Planner - Core Logic Module
NASA Space Apps Challenge MVP
Enhanced with NASA POWER API integration
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
import os

# Import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Plan B generation will be disabled.")


def fetch_nasa_power_data(lat: float, lon: float, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Fetch historical weather data from NASA POWER API
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate  
        start_year: Start year for data (e.g., 2004)
        end_year: End year for data (e.g., 2024)
        
    Returns:
        pd.DataFrame: DataFrame with columns 'Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'
    """
    try:
        # Construct the NASA POWER API URL
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Format dates as YYYYMMDD
        start_date = f"{start_year}0101"  # January 1st
        end_date = f"{end_year}1231"      # December 31st
        
        # API parameters
        params = {
            'parameters': 'T2M_MAX,PRECTOTCORR',
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        print(f"Fetching NASA POWER data for coordinates ({lat}, {lon}) from {start_year} to {end_year}")
        
        # Make API request with timeout and retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to fetch NASA POWER data after {max_retries} attempts: {str(e)}")
                print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
        
        # Parse JSON response
        data = response.json()
        
        # Extract time series data - NASA POWER API structure
        if 'properties' not in data or 'parameter' not in data['properties']:
            raise Exception("Invalid response format from NASA POWER API - no 'properties.parameter' key found")
        
        parameters = data['properties']['parameter']
        
        # Extract T2M_MAX (Temperature Max) and PRECTOTCORR (Precipitation Total Corrected)
        temp_data = parameters.get('T2M_MAX', {})
        precip_data = parameters.get('PRECTOTCORR', {})
        
        if not temp_data or not precip_data:
            raise Exception("Temperature or precipitation data not found in API response")
        
        # Convert to DataFrame
        records = []
        for date_str, temp_value in temp_data.items():
            if date_str in precip_data:
                # Parse date (format: YYYYMMDD)
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                
                # Temperature is already in Celsius from NASA POWER API
                temp_celsius = temp_value if temp_value is not None else None
                
                # Precipitation is already in mm/day
                precip_mm = precip_data[date_str] if precip_data[date_str] is not None else None
                
                records.append({
                    'Year': date_obj.year,
                    'Month': date_obj.month,
                    'Max_Temperature_C': temp_celsius,
                    'Precipitation_mm': precip_mm
                })
        
        if not records:
            raise Exception("No valid data records found in API response")
        
        df = pd.DataFrame(records)
        
        # Remove any rows with null values
        df = df.dropna()
        
        # Sort by year and month
        df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
        
        print(f"Successfully fetched {len(df)} records from NASA POWER API")
        return df
        
    except Exception as e:
        print(f"Error fetching NASA POWER data: {str(e)}")
        # Fallback to mock data if API fails
        print("Falling back to mock data...")
        try:
            df = pd.read_csv('mock_data.csv')
            return df
        except FileNotFoundError:
            raise Exception(f"NASA POWER API failed and mock data not found: {str(e)}")


def load_historical_data(month_filter: int, lat: float = -34.90, lon: float = -56.16) -> pd.DataFrame:
    """
    Load and filter historical data by month using NASA POWER API
    
    Args:
        month_filter: Month to filter (1-12)
        lat: Latitude coordinate (default: Montevideo)
        lon: Longitude coordinate (default: Montevideo)
        
    Returns:
        pd.DataFrame: Filtered data for the specified month
    """
    try:
        if not isinstance(month_filter, int) or month_filter < 1 or month_filter > 12:
            raise ValueError("Month must be between 1 and 12")
        
        # Validate coordinates
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        # Fetch 20 years of data (2004-2024)
        current_year = datetime.now().year
        start_year = current_year - 20  # 20 years back
        end_year = current_year
        
        # Fetch data from NASA POWER API
        df = fetch_nasa_power_data(
            lat=lat,
            lon=lon,
            start_year=start_year,
            end_year=end_year
        )
        
        # Filter by the specified month
        monthly_data = df[df['Month'] == month_filter].copy()
        
        if monthly_data.empty:
            raise ValueError(f"No data found for month {month_filter}")
        
        print(f"Loaded {len(monthly_data)} records for month {month_filter} from NASA POWER API")
        return monthly_data
        
    except Exception as e:
        print(f"Error in load_historical_data: {str(e)}")
        # Return empty DataFrame instead of raising exception
        print("NASA POWER API failed - returning empty DataFrame")
        return pd.DataFrame(columns=['Year', 'Month', 'Max_Temperature_C', 'Precipitation_mm'])


def calculate_adverse_probability(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate adverse weather probability based on temperature data"""
    if monthly_data.empty:
        raise ValueError("No data provided")
    
    if 'Max_Temperature_C' not in monthly_data.columns:
        raise ValueError("Temperature data not found")
    
    # Filter out invalid values (NASA uses -999 for missing data)
    valid_temp_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    
    if len(valid_temp_data) == 0:
        raise ValueError("No valid temperature data found")
    
    # Use a fixed threshold for hot weather (30°C is considered hot for outdoor activities)
    risk_threshold = 30.0
    
    # Count adverse events (days above the hot weather threshold)
    adverse_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] > risk_threshold]
    total_observations = len(monthly_data)
    adverse_count = len(adverse_events)
    
    # Calculate probability as percentage of days above threshold
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Generate status message
    if probability >= 20:
        risk_level = "HIGH"
        status_message = "🚨 HIGH RISK of extreme heat! Consider alternative dates."
    elif probability >= 10:
        risk_level = "MODERATE"
        status_message = "⚠️ MODERATE RISK of warm weather. Monitor conditions."
    elif probability >= 5:
        risk_level = "LOW"
        status_message = "🌤️ LOW RISK of adverse conditions. Favorable weather."
    else:
        risk_level = "MINIMAL"
        status_message = "☀️ MINIMAL RISK of extreme heat. Excellent conditions."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(risk_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }


def calculate_precipitation_risk(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate precipitation risk using 90th percentile methodology
    
    Args:
        monthly_data: DataFrame with precipitation data
        
    Returns:
        Dict with precipitation risk analysis
    """
    if monthly_data.empty:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filter out invalid values (NASA uses -999 for missing data)
    valid_precip_data = monthly_data[monthly_data['Precipitation_mm'] >= 0]
    
    if len(valid_precip_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid precipitation data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Use a fixed threshold for significant precipitation (5mm is noticeable rain)
    precip_threshold = 5.0
    
    # Count days with precipitation above threshold
    adverse_count = len(valid_precip_data[valid_precip_data['Precipitation_mm'] > precip_threshold])
    total_observations = len(monthly_data)
    
    # Calculate probability as percentage of days with significant precipitation
    probability = (adverse_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Determine risk level
    if probability >= 20:
        risk_level = "HIGH"
        status_message = "🌧️ HIGH RISK of heavy precipitation. Consider indoor alternatives."
    elif probability >= 10:
        risk_level = "MODERATE"
        status_message = "🌦️ MODERATE RISK of rain. Bring umbrella."
    elif probability >= 5:
        risk_level = "LOW"
        status_message = "🌤️ LOW RISK of precipitation. Light rain possible."
    else:
        risk_level = "MINIMAL"
        status_message = "☀️ MINIMAL RISK of rain. Dry conditions expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(precip_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': adverse_count
    }


def get_seasonal_cold_threshold(month: int, activity: str = "general") -> float:
    """
    Get appropriate cold threshold based on season and activity type
    
    Args:
        month: Month (1-12)
        activity: Type of activity (beach, picnic, running, general)
        
    Returns:
        float: Temperature threshold in Celsius
    """
    # Define seasonal adjustments for Southern Hemisphere
    seasonal_adjustments = {
        # Summer months (Dec, Jan, Feb) - More realistic thresholds
        12: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        1: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        2: {"base": 20.0, "beach": 22.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        
        # Autumn months (Mar, Apr, May)
        3: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
        4: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0},
        5: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},
        
        # Winter months (Jun, Jul, Aug)
        6: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        7: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        8: {"base": 14.0, "beach": 17.0, "picnic": 12.0, "running": 10.0, "general": 14.0},
        
        # Spring months (Sep, Oct, Nov)
        9: {"base": 16.0, "beach": 19.0, "picnic": 14.0, "running": 12.0, "general": 16.0},
        10: {"base": 18.0, "beach": 21.0, "picnic": 16.0, "running": 14.0, "general": 18.0},
        11: {"base": 20.0, "beach": 23.0, "picnic": 18.0, "running": 16.0, "general": 20.0},
    }
    
    # Get threshold for the month and activity
    month_data = seasonal_adjustments.get(month, seasonal_adjustments[1])  # Default to January
    return month_data.get(activity, month_data["general"])


def calculate_cold_risk(monthly_data: pd.DataFrame, activity: str = "general") -> Dict[str, Any]:
    """
    Calculate cold weather risk using seasonal and activity-aware methodology
    
    Args:
        monthly_data: DataFrame with temperature data
        activity: Type of activity (beach, picnic, running, general)
        
    Returns:
        Dict with cold weather risk analysis
    """
    if monthly_data.empty:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Filter out invalid values (NASA uses -999 for missing data)
    valid_temp_data = monthly_data[monthly_data['Max_Temperature_C'] > -100]
    
    if len(valid_temp_data) == 0:
        return {
            'probability': 0.0,
            'risk_threshold': 0.0,
            'status_message': "No valid temperature data available",
            'risk_level': "UNKNOWN",
            'total_observations': 0,
            'adverse_count': 0
        }
    
    # Get the month from the data to determine season
    month = monthly_data['Month'].iloc[0] if not monthly_data.empty else 1
    
    # Get appropriate cold threshold based on season and activity
    cold_threshold = get_seasonal_cold_threshold(month, activity)
    
    # Count days with temperature below the cold threshold
    cold_events = valid_temp_data[valid_temp_data['Max_Temperature_C'] < cold_threshold]
    total_observations = len(monthly_data)
    cold_count = len(cold_events)
    
    # Calculate probability of cold weather
    probability = (cold_count / total_observations) * 100 if total_observations > 0 else 0
    
    # Get season name for context
    season_names = {
        12: "Summer", 1: "Summer", 2: "Summer",
        3: "Autumn", 4: "Autumn", 5: "Autumn", 
        6: "Winter", 7: "Winter", 8: "Winter",
        9: "Spring", 10: "Spring", 11: "Spring"
    }
    season = season_names.get(month, "Unknown")
    
    # Determine risk level with activity-specific messages
    if probability >= 20:
        risk_level = "HIGH"
        if activity == "beach":
            status_message = f"🧊 HIGH RISK of cold weather for beach activities in {season}. Consider indoor alternatives!"
        elif activity == "picnic":
            status_message = f"🧊 HIGH RISK of cold weather for picnics in {season}. Bundle up or choose a warmer day!"
        elif activity == "running":
            status_message = f"🧊 HIGH RISK of cold weather for running in {season}. Dress in layers!"
        else:
            status_message = f"🧊 HIGH RISK of cold weather in {season}. Bundle up!"
    elif probability >= 10:
        risk_level = "MODERATE"
        if activity == "beach":
            status_message = f"❄️ MODERATE RISK of cold weather for beach activities in {season}. Bring warm clothes!"
        elif activity == "picnic":
            status_message = f"❄️ MODERATE RISK of cold weather for picnics in {season}. Dress warmly!"
        elif activity == "running":
            status_message = f"❄️ MODERATE RISK of cold weather for running in {season}. Wear appropriate gear!"
        else:
            status_message = f"❄️ MODERATE RISK of cold weather in {season}. Dress warmly."
    elif probability >= 5:
        risk_level = "LOW"
        if activity == "beach":
            status_message = f"🌤️ LOW RISK of cold weather for beach activities in {season}. Light jacket recommended."
        elif activity == "picnic":
            status_message = f"🌤️ LOW RISK of cold weather for picnics in {season}. Light layers should be fine."
        elif activity == "running":
            status_message = f"🌤️ LOW RISK of cold weather for running in {season}. Comfortable conditions expected."
        else:
            status_message = f"🌤️ LOW RISK of cold weather in {season}. Light jacket recommended."
    else:
        risk_level = "MINIMAL"
        if activity == "beach":
            status_message = f"☀️ MINIMAL RISK of cold weather for beach activities in {season}. Perfect beach weather!"
        elif activity == "picnic":
            status_message = f"☀️ MINIMAL RISK of cold weather for picnics in {season}. Ideal outdoor conditions!"
        elif activity == "running":
            status_message = f"☀️ MINIMAL RISK of cold weather for running in {season}. Excellent running weather!"
        else:
            status_message = f"☀️ MINIMAL RISK of cold weather in {season}. Comfortable temperatures expected."
    
    return {
        'probability': round(probability, 1),
        'risk_threshold': round(cold_threshold, 1),
        'status_message': status_message,
        'risk_level': risk_level,
        'total_observations': total_observations,
        'adverse_count': cold_count,
        'season': season,
        'activity': activity
    }


def generate_plan_b_with_gemini(
    activity: str,
    weather_condition: str,
    risk_level: str,
    location: str = "Montevideo, Uruguay",
    season: str = "Summer",
    temperature_risk: float = None,
    precipitation_risk: float = None,
    cold_risk: float = None
) -> Dict[str, Any]:
    """
    Generate intelligent Plan B suggestions using Gemini AI with enhanced context
    
    Args:
        activity: Type of activity (beach, picnic, running, etc.)
        weather_condition: Weather condition causing the risk (cold, hot, rainy, etc.)
        risk_level: Risk level (HIGH, MODERATE, LOW, MINIMAL)
        location: Location name for context
        season: Current season
        temperature_risk: Temperature risk probability (0-100)
        precipitation_risk: Precipitation risk probability (0-100)
        cold_risk: Cold weather risk probability (0-100)
        
    Returns:
        Dict with Plan B suggestions
    """
    if not GEMINI_AVAILABLE:
        return {
            "success": False,
            "message": "Gemini AI not available. Please install google-generativeai package.",
            "alternatives": []
        }
    
    try:
        # Configure Gemini API with better error handling
        api_key = os.getenv('GEMINI_API_KEY') or "AIzaSyCp0Jvb1FVFIUOo1NHRCyFFf_G09lzU5G0"
        if not api_key or api_key == "your_gemini_api_key_here":
            return {
                "success": False,
                "message": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable.",
                "alternatives": []
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Enhanced context-aware prompt with risk probabilities
        risk_context = ""
        if temperature_risk is not None:
            risk_context += f"- Temperature Risk: {temperature_risk:.1f}%\n"
        if precipitation_risk is not None:
            risk_context += f"- Precipitation Risk: {precipitation_risk:.1f}%\n"
        if cold_risk is not None:
            risk_context += f"- Cold Weather Risk: {cold_risk:.1f}%\n"
        
        # Create enhanced prompt with better structure
        prompt = f"""You are an expert weather planning assistant for {location}. Generate intelligent Plan B alternatives for outdoor activities when weather conditions are unfavorable.

CONTEXT:
- Original Activity: {activity}
- Primary Weather Risk: {weather_condition} ({risk_level} risk level)
- Location: {location}
- Season: {season}
- Current Date: {datetime.now().strftime('%B %d, %Y')}
{risk_context}

REQUIREMENTS:
1. Provide exactly 3-4 specific, actionable alternatives
2. Consider the season, location, and weather context
3. Make suggestions practical, enjoyable, and realistic
4. Include both indoor and outdoor options when weather permits
5. Be creative but maintain feasibility
6. Consider local attractions and activities specific to Uruguay
7. Provide specific locations or venues when possible
8. Consider cost, accessibility, and time requirements

RESPONSE FORMAT: Return ONLY a valid JSON response with this exact structure:
{{
    "alternatives": [
        {{
            "title": "Specific activity name",
            "description": "Brief but detailed description of the activity",
            "type": "indoor/outdoor/mixed",
            "reason": "Why this is a good alternative for the weather conditions",
            "tips": "Practical tips for this activity",
            "location": "Specific location or venue (if applicable)",
            "duration": "Estimated time needed",
            "cost": "Free/Low/Medium/High"
        }}
    ]
}}

Focus on making the day enjoyable despite the weather conditions. Be specific, helpful, and consider the local context of Uruguay."""
        
        # Generate response with timeout
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
        except Exception as api_error:
            print(f"Gemini API call failed: {str(api_error)}")
            return {
                "success": False,
                "message": f"Gemini API call failed: {str(api_error)}",
                "alternatives": []
            }
        
        # Enhanced JSON parsing with better error handling
        try:
            response_text = response.text.strip()
            print(f"Gemini raw response: {response_text[:200]}...")  # Debug log
            
            # Clean the response text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Find JSON boundaries more robustly
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON structure found in response")
            
            json_text = response_text[start_idx:end_idx]
            plan_b_data = json.loads(json_text)
            
            # Validate the response structure
            alternatives = plan_b_data.get('alternatives', [])
            if not isinstance(alternatives, list) or len(alternatives) == 0:
                raise ValueError("No alternatives found in response")
            
            # Ensure each alternative has required fields
            validated_alternatives = []
            for alt in alternatives:
                if isinstance(alt, dict) and alt.get('title'):
                    validated_alt = {
                        'title': alt.get('title', 'Activity'),
                        'description': alt.get('description', 'No description available'),
                        'type': alt.get('type', 'mixed'),
                        'reason': alt.get('reason', 'Good alternative for current conditions'),
                        'tips': alt.get('tips', 'Enjoy your activity!'),
                        'location': alt.get('location', 'Various locations available'),
                        'duration': alt.get('duration', '1-3 hours'),
                        'cost': alt.get('cost', 'Varies')
                    }
                    validated_alternatives.append(validated_alt)
            
            if len(validated_alternatives) == 0:
                raise ValueError("No valid alternatives found after validation")
            
            return {
                "success": True,
                "message": f"Generated {len(validated_alternatives)} Plan B alternatives using Gemini AI",
                "alternatives": validated_alternatives,
                "ai_model": "Gemini 2.0 Flash",
                "generated_at": datetime.now().isoformat(),
                "context": {
                    "activity": activity,
                    "weather_condition": weather_condition,
                    "risk_level": risk_level,
                    "location": location,
                    "season": season
                }
            }
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing failed: {str(e)}")
            # Enhanced fallback parsing
            alternatives = parse_fallback_response(response.text)
            
            if len(alternatives) > 0:
                return {
                    "success": True,
                    "message": f"Generated {len(alternatives)} Plan B alternatives using Gemini AI (fallback parsing)",
                    "alternatives": alternatives,
                    "ai_model": "Gemini 2.0 Flash (Fallback)",
                    "generated_at": datetime.now().isoformat(),
                    "warning": "Response parsing used fallback method"
                }
            else:
                raise ValueError("Failed to parse response and no alternatives found")
    
    except Exception as e:
        print(f"Error generating Plan B with Gemini: {str(e)}")
        return {
            "success": False,
            "message": f"Error generating Plan B: {str(e)}",
            "alternatives": [],
            "error_type": type(e).__name__
        }


def parse_fallback_response(response_text: str) -> list:
    """
    Parse Gemini response when JSON parsing fails
    """
    alternatives = []
    lines = response_text.split('\n')
    current_alt = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('{') or line.startswith('}'):
            continue
            
        # Look for activity titles (various patterns)
        if any(keyword in line.lower() for keyword in ['visit', 'go to', 'try', 'enjoy', 'explore', 'discover']):
            if current_alt and current_alt.get('title'):
                alternatives.append(current_alt)
            current_alt = {
                "title": line,
                "description": "",
                "type": "mixed",
                "reason": "",
                "tips": "",
                "location": "Various locations",
                "duration": "1-3 hours",
                "cost": "Varies"
            }
        elif current_alt:
            if not current_alt.get("description"):
                current_alt["description"] = line
            elif not current_alt.get("reason"):
                current_alt["reason"] = line
            elif not current_alt.get("tips"):
                current_alt["tips"] = line
    
    if current_alt and current_alt.get('title'):
        alternatives.append(current_alt)
    
    return alternatives[:4]  # Limit to 4 alternatives


def generate_fallback_plan_b(
    activity: str,
    weather_condition: str,
    risk_level: str,
    location: str = "Montevideo, Uruguay",
    season: str = "Summer"
) -> Dict[str, Any]:
    """
    Generate fallback Plan B suggestions when Gemini is not available
    """
    fallback_alternatives = {
        "beach": {
            "cold": [
                {
                    "title": "Indoor Pool Complex",
                    "description": "Visit a heated indoor pool or water park",
                    "type": "indoor",
                    "reason": "Warm water activities without cold weather exposure",
                    "tips": "Bring swimwear and check opening hours"
                },
                {
                    "title": "Museo del Mar",
                    "description": "Explore marine life and ocean exhibits",
                    "type": "indoor",
                    "reason": "Ocean-themed experience in a warm environment",
                    "tips": "Great for families and educational"
                },
                {
                    "title": "Thermal Baths",
                    "description": "Relax in natural hot springs",
                    "type": "mixed",
                    "reason": "Warm water therapy in natural setting",
                    "tips": "Bring towels and check temperature requirements"
                }
            ],
            "rainy": [
                {
                    "title": "Shopping Mall",
                    "description": "Visit Punta Carretas or Montevideo Shopping",
                    "type": "indoor",
                    "reason": "Stay dry while enjoying shopping and dining",
                    "tips": "Check for special events or sales"
                },
                {
                    "title": "Cinema Complex",
                    "description": "Watch latest movies in comfortable theaters",
                    "type": "indoor",
                    "reason": "Perfect rainy day entertainment",
                    "tips": "Book tickets in advance for popular shows"
                }
            ]
        },
        "picnic": {
            "cold": [
                {
                    "title": "Indoor Food Market",
                    "description": "Visit Mercado del Puerto for local cuisine",
                    "type": "indoor",
                    "reason": "Food experience in warm environment",
                    "tips": "Try traditional Uruguayan barbecue"
                },
                {
                    "title": "Cooking Class",
                    "description": "Learn to cook local dishes",
                    "type": "indoor",
                    "reason": "Interactive food experience",
                    "tips": "Book in advance and bring appetite"
                }
            ],
            "rainy": [
                {
                    "title": "Restaurant Tour",
                    "description": "Visit multiple restaurants for different courses",
                    "type": "indoor",
                    "reason": "Food adventure without weather concerns",
                    "tips": "Plan route and make reservations"
                }
            ]
        },
        "running": {
            "cold": [
                {
                    "title": "Indoor Gym",
                    "description": "Use treadmill or indoor track",
                    "type": "indoor",
                    "reason": "Maintain fitness routine in warm environment",
                    "tips": "Bring gym clothes and water bottle"
                },
                {
                    "title": "Shopping Mall Walking",
                    "description": "Power walk through large shopping centers",
                    "type": "indoor",
                    "reason": "Exercise while staying warm",
                    "tips": "Wear comfortable shoes and track steps"
                }
            ],
            "rainy": [
                {
                    "title": "Indoor Sports Complex",
                    "description": "Use indoor courts or tracks",
                    "type": "indoor",
                    "reason": "Stay active without getting wet",
                    "tips": "Check availability and book time slots"
                }
            ]
        }
    }
    
    # Get alternatives for the specific activity and condition
    alternatives = fallback_alternatives.get(activity, {}).get(weather_condition, [])
    
    # If no specific alternatives, provide general ones
    if not alternatives:
        alternatives = [
            {
                "title": "Museo Nacional de Artes Visuales",
                "description": "Explore Uruguayan art and culture",
                "type": "indoor",
                "reason": "Cultural experience regardless of weather",
                "tips": "Check current exhibitions and opening hours"
            },
            {
                "title": "Teatro Solís",
                "description": "Attend a performance or take a guided tour",
                "type": "indoor",
                "reason": "Cultural entertainment in beautiful venue",
                "tips": "Book tickets in advance for performances"
            }
        ]
    
    return {
        "success": True,
        "message": f"Generated {len(alternatives)} Plan B alternatives (fallback mode)",
        "alternatives": alternatives,
        "ai_model": "Fallback System",
        "generated_at": datetime.now().isoformat()
    }


def test_nasa_power_integration():
    """
    Test function to verify NASA POWER API integration
    """
    print("Testing NASA POWER API integration...")
    
    try:
        # Test with Montevideo coordinates
        test_lat = -34.90
        test_lon = -56.16
        test_start_year = 2020
        test_end_year = 2024
        
        print(f"Testing with coordinates: ({test_lat}, {test_lon})")
        print(f"Date range: {test_start_year} to {test_end_year}")
        
        # Fetch data
        df = fetch_nasa_power_data(test_lat, test_lon, test_start_year, test_end_year)
        
        print(f"Successfully fetched {len(df)} records")
        print(f"Data shape: {df.shape}")
        print(f"Date range: {df['Year'].min()}-{df['Year'].max()}")
        print(f"Temperature range: {df['Max_Temperature_C'].min():.1f}C to {df['Max_Temperature_C'].max():.1f}C")
        print(f"Precipitation range: {df['Precipitation_mm'].min():.1f}mm to {df['Precipitation_mm'].max():.1f}mm")
        
        # Test month filtering
        march_data = load_historical_data(3)  # March
        print(f"March data: {len(march_data)} records")
        
        # Test risk calculation
        risk_analysis = calculate_adverse_probability(march_data)
        print(f"Risk analysis: {risk_analysis['risk_level']} ({risk_analysis['probability']:.1f}%)")
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


def verify_data_source(month: int = 3):
    """
    Function to verify which data source is being used (NASA vs Mock)
    """
    print("=" * 60)
    print("VERIFICACION DE FUENTE DE DATOS")
    print("=" * 60)
    
    try:
        # Test NASA POWER API directly
        print("\n1. Probando NASA POWER API directamente...")
        test_lat = -34.90
        test_lon = -56.16
        current_year = datetime.now().year
        start_year = current_year - 20
        
        nasa_data = fetch_nasa_power_data(test_lat, test_lon, start_year, current_year)
        print(f"   NASA POWER API: {len(nasa_data)} registros")
        print(f"   Rango de anos: {nasa_data['Year'].min()}-{nasa_data['Year'].max()}")
        print(f"   Temperatura: {nasa_data['Max_Temperature_C'].min():.1f}C - {nasa_data['Max_Temperature_C'].max():.1f}C")
        
        # Test load_historical_data function
        print(f"\n2. Probando load_historical_data(month={month})...")
        monthly_data = load_historical_data(month)
        print(f"   Registros para mes {month}: {len(monthly_data)}")
        
        # Compare with mock data
        print(f"\n3. Comparando con datos mock...")
        try:
            mock_df = pd.read_csv('mock_data.csv')
            mock_monthly = mock_df[mock_df['Month'] == month]
            print(f"   Mock data para mes {month}: {len(mock_monthly)} registros")
            
            if len(monthly_data) > len(mock_monthly) * 10:
                print("   CONFIRMADO: Usando datos reales de NASA (mucho mas registros)")
            else:
                print("   ADVERTENCIA: Podria estar usando datos mock")
                
        except FileNotFoundError:
            print("   Mock data no encontrado")
        
        # Show sample of real data
        print(f"\n4. Muestra de datos reales (mes {month}):")
        print(monthly_data.head())
        
        # Calculate risk with real data
        print(f"\n5. Analisis de riesgo con datos reales:")
        risk_analysis = calculate_adverse_probability(monthly_data)
        print(f"   Nivel de riesgo: {risk_analysis['risk_level']}")
        print(f"   Probabilidad: {risk_analysis['probability']:.1f}%")
        print(f"   Umbral: {risk_analysis['risk_threshold']:.1f}C")
        
        print("\n" + "=" * 60)
        print("VERIFICACION COMPLETADA")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Error en verificacion: {str(e)}")
        return False


if __name__ == "__main__":
    # Run verification when script is executed directly
    verify_data_source()