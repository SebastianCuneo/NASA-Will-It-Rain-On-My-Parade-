"""
The Parade Planner - NASA Space Apps Challenge MVP
Will It Rain On My Parade?
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from logic import load_historical_data, calculate_adverse_probability

# Page configuration
st.set_page_config(
    page_title="The Parade Planner",
    page_icon="🌤️",
    layout="wide"
)

# Title
st.title("🌤️ The Parade Planner")
st.markdown("### *Will It Rain On My Parade?*")
st.markdown("**NASA Space Apps Challenge** - Weather risk assessment for outdoor events.")

# Sidebar inputs
st.sidebar.header("📍 Event Location & Timing")

# Location inputs - MONTEVIDEO, URUGUAY
latitude = st.sidebar.number_input(
    "Latitude",
    min_value=-90.0,
    max_value=90.0,
    value=-34.90,  # Montevideo, Uruguay
    step=0.0001,
    help="Enter the latitude of your event location"
)

longitude = st.sidebar.number_input(
    "Longitude", 
    min_value=-180.0,
    max_value=180.0,
    value=-56.16,  # Montevideo, Uruguay
    step=0.0001,
    help="Enter the longitude of your event location"
)

# Month selection
month = st.sidebar.selectbox(
    "Event Month",
    options=list(range(1, 13)),
    format_func=lambda x: ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"][x-1],
    index=2,  # Default to March
    help="Select the month when your event will take place"
)

# Simple methodology section
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Methodology")
st.sidebar.markdown("""
**Risk Assessment:**
- 90th Percentile Threshold
- Historical temperature analysis
- NASA MERRA-2 simulation data
""")

# Main content
if st.button("🔍 Analyze Weather Risk", type="primary"):
    
    try:
        # Load and process data
        monthly_data = load_historical_data(month)
        risk_analysis = calculate_adverse_probability(monthly_data)
        
        # Display results
        st.markdown("---")
        
        # Simple metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌡️ Risk Threshold", f"{risk_analysis['risk_threshold']}°C")
        
        with col2:
            st.metric("⚠️ Adverse Probability", f"{risk_analysis['probability']}%")
        
        with col3:
            st.metric("📊 Historical Data", f"{risk_analysis['total_observations']} years")
        
        # Status message
        st.markdown("### 🎯 Risk Assessment")
        st.info(risk_analysis['status_message'])
        
        # Educational visualization
        st.markdown("### 📈 Historical Temperature Distribution")
        
        # Create histogram
        histogram = alt.Chart(monthly_data).mark_bar(
            color='lightblue',
            opacity=0.7
        ).encode(
            x=alt.X('Max_Temperature_C:Q', 
                   bin=alt.Bin(maxbins=10),
                   title='Maximum Temperature (°C)'),
            y=alt.Y('count():Q', title='Number of Years')
        ).properties(
            width=600,
            height=400,
            title=f"Temperature Distribution for {['January', 'February', 'March', 'April', 'May', 'June',
                                                   'July', 'August', 'September', 'October', 'November', 'December'][month-1]}"
        )
        
        # Add threshold line
        threshold_line = alt.Chart(
            pd.DataFrame({'threshold': [risk_analysis['risk_threshold']]})
        ).mark_rule(
            color='red',
            strokeWidth=3,
            strokeDash=[5, 5]
        ).encode(x='threshold:Q')
        
        # Combine charts
        final_chart = histogram + threshold_line
        st.altair_chart(final_chart, use_container_width=True)
        
        # Simple interpretation
        st.markdown("### 📖 Chart Interpretation")
        st.markdown(f"""
        - **Blue bars**: Temperature distribution over {risk_analysis['total_observations']} years
        - **Red line**: 90th percentile threshold ({risk_analysis['risk_threshold']}°C)
        - **Risk area**: Temperatures above the red line
        """)
        
        # Basic recommendations
        st.markdown("### 💡 Recommendations")
        if risk_analysis['risk_level'] == "HIGH":
            st.warning("Consider alternative dates or indoor backup plans.")
        elif risk_analysis['risk_level'] == "MODERATE":
            st.warning("Monitor weather conditions and have backup plans ready.")
        else:
            st.success("Weather conditions are historically favorable for your event.")
    
    except FileNotFoundError:
        st.error("❌ Historical data file not found.")
    except ValueError as e:
        st.error(f"❌ Data error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Simple footer
st.markdown("---")
st.markdown("**NASA Space Apps Challenge 2024** | Will It Rain On My Parade?")