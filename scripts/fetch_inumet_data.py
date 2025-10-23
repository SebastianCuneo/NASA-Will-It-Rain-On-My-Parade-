#!/usr/bin/env python3
"""
INUMET Real Data Fetcher for Montevideo
This script fetches real data from INUMET and creates a fallback CSV file
"""

import pandas as pd
import requests
from datetime import datetime
import numpy as np

def fetch_inumet_data():
    """
    Fetch real data from INUMET for Montevideo (only temperature and precipitation)
    """
    print("🌍 Fetching real INUMET data for Montevideo...")
    print("📊 Only downloading temperature and precipitation data")
    
    # URLs from the notebook - only what we need
    url_temp = 'https://catalogodatos.gub.uy/dataset/accd0e24-76be-4101-904b-81bb7d41ee88/resource/f800fc53-556b-4d1c-8bd6-28b41f9cf146/download/inumet_temperatura_del_aire.csv'
    url_prec = 'https://catalogodatos.gub.uy/dataset/fd896b11-4c04-4807-bae4-5373d65beea2/resource/ca987721-6052-4bb8-8596-2a5ad9630639/download/inumet_precipitacion_acumulada_horaria.csv'
    
    try:
        # Fetch temperature data
        print("📊 Fetching temperature data...")
        temp = pd.read_csv(url_temp, encoding='ISO-8859-1', delimiter=';')
        
        # Fetch precipitation data
        print("🌧️ Fetching precipitation data...")
        prec = pd.read_csv(url_prec, encoding='ISO-8859-1', delimiter=';')
        
        # Clean column names
        temp.columns = temp.columns.str.strip().str.lower()
        prec.columns = prec.columns.str.strip().str.lower()
        
        # Rename columns
        temp.rename(columns={'temp_aire': 'temperatura', 'estacion_id': 'estacion'}, inplace=True)
        prec.rename(columns={'precip_horario': 'precipitacion', 'estacion_id': 'estacion'}, inplace=True)
        
        # Convert dates
        temp['fecha'] = pd.to_datetime(temp['fecha'], errors='coerce')
        prec['fecha'] = pd.to_datetime(prec['fecha'], errors='coerce')
        
        # Extract date and hour
        temp['fecha_simple'] = temp['fecha'].dt.date
        prec['fecha_simple'] = prec['fecha'].dt.date
        temp['hour'] = temp['fecha'].dt.strftime('%H:%M')
        prec['hour'] = prec['fecha'].dt.strftime('%H:%M')
        
        # Handle missing values
        temp['temperatura'] = temp['temperatura'].interpolate()
        prec['precipitacion'] = prec['precipitacion'].fillna(0)
        
        # Merge datasets
        df_merged = pd.merge(temp, prec, on=['fecha_simple', 'hour', 'estacion'], how='inner')
        df_merged = df_merged[['fecha_x', 'fecha_simple', 'hour', 'estacion', 'temperatura', 'precipitacion']]
        df_merged = df_merged.dropna()
        
        print(f"✅ Successfully loaded {len(df_merged)} records")
        print(f"📅 Date range: {df_merged['fecha_simple'].min()} to {df_merged['fecha_simple'].max()}")
        print(f"🏢 Stations: {df_merged['estacion'].unique()}")
        
        return df_merged
        
    except Exception as e:
        print(f"❌ Error fetching INUMET data: {e}")
        return None

def process_inumet_data_to_monthly(df):
    """
    Process INUMET data to monthly format for our application
    """
    if df is None:
        return None
    
    try:
        # Convert fecha_simple to datetime
        df['fecha_simple'] = pd.to_datetime(df['fecha_simple'])
        
        # Extract year and month
        df['Year'] = df['fecha_simple'].dt.year
        df['Month'] = df['fecha_simple'].dt.month
        
        # Group by year and month, calculate only what we need
        monthly_stats = df.groupby(['Year', 'Month']).agg({
            'temperatura': ['max', 'mean'],  # Only max and mean temperature
            'precipitacion': 'sum'           # Only precipitation sum
        }).round(2)
        
        # Flatten column names
        monthly_stats.columns = ['Max_Temperature_C', 'Mean_Temperature_C', 'Precipitation_mm']
        
        # Reset index
        monthly_stats = monthly_stats.reset_index()
        
        # Filter for recent years (2020-2024)
        monthly_stats = monthly_stats[monthly_stats['Year'].between(2020, 2024)]
        
        print(f"✅ Processed {len(monthly_stats)} monthly records")
        print(f"📊 Years: {sorted(monthly_stats['Year'].unique())}")
        print(f"📅 Months: {sorted(monthly_stats['Month'].unique())}")
        
        return monthly_stats
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def save_inumet_fallback_data(monthly_data):
    """
    Save processed INUMET data as fallback CSV
    """
    if monthly_data is None:
        return None
    
    try:
        # Save to CSV
        csv_filename = '../backend/inumet_montevideo_data.csv'
        monthly_data.to_csv(csv_filename, index=False)
        
        print(f"✅ Saved INUMET data to {csv_filename}")
        print(f"📊 Records: {len(monthly_data)}")
        
        # Show sample data
        print("\n📋 Sample data:")
        print(monthly_data.head(10))
        
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return None

def main():
    """
    Main function to fetch and process INUMET data
    """
    print("🌍 INUMET Real Data Fetcher for Montevideo")
    print("=" * 50)
    
    # Step 1: Fetch data from INUMET
    df = fetch_inumet_data()
    
    if df is not None:
        # Step 2: Process to monthly format
        monthly_data = process_inumet_data_to_monthly(df)
        
        if monthly_data is not None:
            # Step 3: Save as fallback data
            csv_file = save_inumet_fallback_data(monthly_data)
            
            if csv_file:
                print("\n🎉 Process completed successfully!")
                print(f"📁 Real INUMET data saved: {csv_file}")
                print("\n💡 This data can now be used as fallback when NASA POWER API fails")
            else:
                print("❌ Failed to save data")
        else:
            print("❌ Failed to process data")
    else:
        print("❌ Failed to fetch data from INUMET")

if __name__ == "__main__":
    main()
