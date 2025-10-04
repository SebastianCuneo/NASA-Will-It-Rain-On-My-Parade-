"""
The Parade Planner - Core Logic Module
NASA Space Apps Challenge MVP
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def load_historical_data(month_filter: int) -> pd.DataFrame:
    """Load and filter historical data by month"""
    try:
        df = pd.read_csv('mock_data.csv')
        
        if not isinstance(month_filter, int) or month_filter < 1 or month_filter > 12:
            raise ValueError("Month must be between 1 and 12")
        
        monthly_data = df[df['Month'] == month_filter].copy()
        
        if monthly_data.empty:
            raise ValueError(f"No data found for month {month_filter}")
            
        return monthly_data
        
    except FileNotFoundError:
        raise FileNotFoundError("mock_data.csv not found")
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")


def calculate_adverse_probability(monthly_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate adverse weather probability based on temperature data"""
    if monthly_data.empty:
        raise ValueError("No data provided")
    
    if 'Max_Temperature_C' not in monthly_data.columns:
        raise ValueError("Temperature data not found")
    
    # Calculate 90th percentile threshold
    risk_threshold = np.percentile(monthly_data['Max_Temperature_C'], 90)
    
    # Count adverse events
    adverse_events = monthly_data[monthly_data['Max_Temperature_C'] >= risk_threshold]
    total_observations = len(monthly_data)
    adverse_count = len(adverse_events)
    
    # Calculate probability
    probability = (adverse_count / total_observations) * 100
    
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