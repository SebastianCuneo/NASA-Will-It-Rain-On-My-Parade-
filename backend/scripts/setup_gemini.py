#!/usr/bin/env python3
"""
NASA Weather Risk Navigator - Gemini AI Setup Script
This script helps configure Gemini AI for Plan B generation
"""

import os
import sys
from pathlib import Path

def setup_gemini_config():
    """
    Setup Gemini AI configuration for the NASA Weather Risk Navigator
    """
    print("🌤️ NASA Weather Risk Navigator - Gemini AI Setup")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content and 'your_gemini_api_key_here' not in content:
                print("✅ GEMINI_API_KEY already configured")
                return True
    else:
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("""# NASA Weather Risk Navigator - Environment Configuration
# Copy this file to .env and add your API keys

# Gemini AI API Key (for Plan B generation)
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: NASA API configuration (if needed in future)
# NASA_API_KEY=your_nasa_api_key_here

# Development settings
DEBUG=true
LOG_LEVEL=INFO
""")
    
    print("\n🔑 Gemini AI API Key Setup")
    print("-" * 40)
    print("To use Gemini AI for Plan B generation, you need an API key.")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated API key")
    print("5. Replace 'your_gemini_api_key_here' in the .env file")
    
    api_key = input("\nEnter your Gemini API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file with the API key
        with open(env_file, 'r') as f:
            content = f.read()
        
        content = content.replace('GEMINI_API_KEY=your_gemini_api_key_here', f'GEMINI_API_KEY={api_key}')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ API key saved to .env file")
        return True
    else:
        print("⚠️ Skipping API key configuration")
        print("You can configure it later by editing the .env file")
        return False

def test_gemini_integration():
    """
    Test Gemini AI integration
    """
    print("\n🧪 Testing Gemini AI Integration")
    print("-" * 40)
    
    try:
        # Import required modules
        from logic import generate_plan_b_with_gemini
        
        # Test with sample data
        print("Testing Plan B generation...")
        result = generate_plan_b_with_gemini(
            activity="beach",
            weather_condition="rainy",
            risk_level="HIGH",
            location="Montevideo, Uruguay",
            season="Summer",
            temperature_risk=25.5,
            precipitation_risk=45.2,
            cold_risk=8.3
        )
        
        if result.get('success'):
            print("✅ Gemini AI integration working!")
            print(f"Generated {len(result.get('alternatives', []))} alternatives")
            print(f"AI Model: {result.get('ai_model', 'Unknown')}")
            
            # Show first alternative as example
            alternatives = result.get('alternatives', [])
            if alternatives:
                first_alt = alternatives[0]
                print(f"\nExample alternative: {first_alt.get('title', 'N/A')}")
                print(f"Description: {first_alt.get('description', 'N/A')}")
                print(f"Type: {first_alt.get('type', 'N/A')}")
        else:
            print("❌ Gemini AI integration failed")
            print(f"Error: {result.get('message', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """
    Main setup function
    """
    print("🚀 Setting up Gemini AI for NASA Weather Risk Navigator")
    print("=" * 60)
    
    # Setup configuration
    config_success = setup_gemini_config()
    
    if config_success:
        # Test integration
        test_success = test_gemini_integration()
        
        if test_success:
            print("\n🎉 Setup completed successfully!")
            print("Gemini AI is now configured for Plan B generation.")
            print("\nNext steps:")
            print("1. Start the backend: python -m uvicorn backend.api:app --reload --port 8000")
            print("2. Start the frontend: cd frontend && npm start")
            print("3. Test the application with weather conditions that trigger Plan B")
        else:
            print("\n⚠️ Setup completed with warnings")
            print("Gemini AI configuration saved, but testing failed.")
            print("Check your API key and internet connection.")
    else:
        print("\n⚠️ Setup incomplete")
        print("Gemini AI not configured. Plan B will use fallback suggestions.")
    
    print("\n" + "=" * 60)
    print("Setup complete! 🌤️")

if __name__ == "__main__":
    main()
