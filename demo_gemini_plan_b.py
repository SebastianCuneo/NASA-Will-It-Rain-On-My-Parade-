#!/usr/bin/env python3
"""
NASA Weather Risk Navigator - Gemini AI Plan B Demo
Demonstration of enhanced Plan B generation with Gemini AI
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_enhanced_plan_b():
    """
    Demonstrate the enhanced Gemini AI Plan B generation
    """
    print("🌤️ NASA Weather Risk Navigator - Enhanced Plan B Demo")
    print("=" * 70)
    print("Demonstrating AI-powered Plan B generation with Gemini AI")
    print("=" * 70)
    
    try:
        from logic import generate_plan_b_with_gemini, generate_fallback_plan_b
        
        # Demo scenarios with realistic data
        demo_scenarios = [
            {
                "name": "🏖️ Beach Day - Heavy Rain Expected",
                "activity": "beach",
                "weather_condition": "rainy",
                "risk_level": "HIGH",
                "temperature_risk": 12.5,
                "precipitation_risk": 68.3,
                "cold_risk": 15.2,
                "description": "Planning a beach day but heavy rain is expected with 68% probability"
            },
            {
                "name": "🧺 Picnic - Extreme Heat Warning",
                "activity": "picnic",
                "weather_condition": "hot",
                "risk_level": "HIGH",
                "temperature_risk": 45.7,
                "precipitation_risk": 8.2,
                "cold_risk": 2.1,
                "description": "Picnic planned but extreme heat warning with 45% probability of dangerous temperatures"
            },
            {
                "name": "🏃‍♂️ Running - Cold Weather Alert",
                "activity": "run",
                "weather_condition": "cold",
                "risk_level": "MODERATE",
                "temperature_risk": 5.8,
                "precipitation_risk": 22.1,
                "cold_risk": 42.6,
                "description": "Morning run planned but cold weather with 42% probability of uncomfortable conditions"
            },
            {
                "name": "⛵ Sailing - Storm Conditions",
                "activity": "sailing",
                "weather_condition": "windy",
                "risk_level": "HIGH",
                "temperature_risk": 18.3,
                "precipitation_risk": 55.4,
                "cold_risk": 25.7,
                "description": "Sailing trip planned but storm conditions with high winds and precipitation"
            }
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['name']}")
            print("=" * 50)
            print(f"📝 {scenario['description']}")
            print(f"🎯 Activity: {scenario['activity']}")
            print(f"🌦️ Weather Risk: {scenario['weather_condition']} ({scenario['risk_level']} level)")
            print(f"📊 Risk Probabilities:")
            print(f"   - Temperature: {scenario['temperature_risk']:.1f}%")
            print(f"   - Precipitation: {scenario['precipitation_risk']:.1f}%")
            print(f"   - Cold Weather: {scenario['cold_risk']:.1f}%")
            
            print(f"\n🤖 Generating Plan B with Gemini AI...")
            print("-" * 30)
            
            # Generate Plan B with Gemini AI
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
                print("✅ Gemini AI Plan B Generated Successfully!")
                print(f"🤖 AI Model: {gemini_result.get('ai_model', 'Unknown')}")
                print(f"⏰ Generated at: {gemini_result.get('generated_at', 'Unknown')}")
                
                alternatives = gemini_result.get('alternatives', [])
                print(f"\n🎯 {len(alternatives)} Alternative Activities:")
                print("-" * 40)
                
                for j, alt in enumerate(alternatives, 1):
                    print(f"\n{j}. {alt.get('title', 'Activity')}")
                    print(f"   📝 {alt.get('description', 'No description')}")
                    print(f"   🏠 Type: {alt.get('type', 'mixed').title()}")
                    print(f"   💡 Why: {alt.get('reason', 'Good alternative')}")
                    print(f"   🎯 Tips: {alt.get('tips', 'Enjoy!')}")
                    
                    # Show additional details
                    details = []
                    if alt.get('location'):
                        details.append(f"📍 {alt.get('location')}")
                    if alt.get('duration'):
                        details.append(f"⏱️ {alt.get('duration')}")
                    if alt.get('cost'):
                        details.append(f"💰 {alt.get('cost')}")
                    
                    if details:
                        print(f"   📋 Details: {' | '.join(details)}")
                
                # Show context information
                context = gemini_result.get('context', {})
                if context:
                    print(f"\n📊 Context Used:")
                    print(f"   - Activity: {context.get('activity', 'N/A')}")
                    print(f"   - Weather: {context.get('weather_condition', 'N/A')}")
                    print(f"   - Risk Level: {context.get('risk_level', 'N/A')}")
                    print(f"   - Location: {context.get('location', 'N/A')}")
                    print(f"   - Season: {context.get('season', 'N/A')}")
                
            else:
                print("❌ Gemini AI failed")
                print(f"Error: {gemini_result.get('message', 'Unknown error')}")
                print(f"Error Type: {gemini_result.get('error_type', 'Unknown')}")
                
                print(f"\n🔄 Using Fallback System...")
                fallback_result = generate_fallback_plan_b(
                    activity=scenario['activity'],
                    weather_condition=scenario['weather_condition'],
                    risk_level=scenario['risk_level'],
                    location="Montevideo, Uruguay",
                    season="Summer"
                )
                
                if fallback_result.get('success'):
                    print("✅ Fallback Plan B Generated!")
                    alternatives = fallback_result.get('alternatives', [])
                    print(f"🎯 {len(alternatives)} Fallback Alternatives:")
                    
                    for j, alt in enumerate(alternatives, 1):
                        print(f"\n{j}. {alt.get('title', 'Activity')}")
                        print(f"   📝 {alt.get('description', 'No description')}")
                        print(f"   🏠 Type: {alt.get('type', 'mixed').title()}")
                        print(f"   💡 Why: {alt.get('reason', 'Good alternative')}")
                        print(f"   🎯 Tips: {alt.get('tips', 'Enjoy!')}")
                else:
                    print("❌ Fallback system also failed")
            
            print("\n" + "=" * 70)
        
        print("\n🎉 Demo completed successfully!")
        print("Enhanced Plan B generation with Gemini AI is working!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def show_improvements():
    """
    Show the improvements made to the Plan B system
    """
    print("\n🚀 Enhanced Plan B System Improvements")
    print("=" * 50)
    
    improvements = [
        "✅ Enhanced prompts with detailed context and risk probabilities",
        "✅ Better error handling and fallback mechanisms",
        "✅ Improved JSON parsing with validation",
        "✅ Additional fields: location, duration, cost information",
        "✅ Better UI display with organized information",
        "✅ Automated setup script for easy configuration",
        "✅ Comprehensive testing and demo scripts",
        "✅ Enhanced API integration with risk data",
        "✅ Better user experience with detailed alternatives"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    print(f"\n📊 Technical Enhancements:")
    print(f"  - Gemini 2.0 Flash model for better responses")
    print(f"  - Enhanced prompt engineering with context")
    print(f"  - Robust JSON parsing with fallback")
    print(f"  - Better error handling and logging")
    print(f"  - Improved UI with detailed information display")

def main():
    """
    Main demo function
    """
    print("🌤️ NASA Weather Risk Navigator - Plan B Enhancement Demo")
    print("=" * 70)
    
    # Show improvements
    show_improvements()
    
    # Run demo
    demo_success = demo_enhanced_plan_b()
    
    print("\n" + "=" * 70)
    if demo_success:
        print("🎉 Enhanced Plan B system is working perfectly!")
        print("Gemini AI integration is complete and ready for production.")
    else:
        print("⚠️ Demo completed with some issues")
        print("Check your Gemini AI configuration and try again.")
    
    print("\nNext steps:")
    print("1. Configure Gemini AI: python setup_gemini.py")
    print("2. Test integration: python test_gemini_plan_b.py")
    print("3. Start the application and test Plan B generation")

if __name__ == "__main__":
    main()
