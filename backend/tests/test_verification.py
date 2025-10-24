"""
🧪 VERIFICACIÓN END-TO-END: COHERENCIA LÓGICA Y DATOS NASA
NASA Weather Risk Navigator - Test Suite
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path to import logic module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic import load_historical_data, calculate_heat_risk, calculate_precipitation_risk, calculate_cold_risk

def create_mock_data_for_testing():
    """
    Crear datos mock controlados para pruebas de coherencia lógica
    """
    print("🔧 Creando datos mock controlados para pruebas...")
    
    # Crear datos con probabilidades conocidas
    np.random.seed(42)  # Para resultados reproducibles
    
    # Caso 1: Diciembre (Verano) - Alta probabilidad de calor
    december_data = []
    for year in range(2004, 2024):
        for day in range(1, 32):  # Diciembre tiene 31 días
            # 30% de los días con temperatura > 30°C (calor extremo)
            if np.random.random() < 0.30:
                temp = np.random.normal(32, 2)  # Calor extremo
            else:
                temp = np.random.normal(25, 3)  # Temperatura normal
            
            december_data.append({
                'Year': year,
                'Month': 12,
                'Max_Temperature_C': max(temp, 15),  # Mínimo 15°C
                'Precipitation_mm': np.random.exponential(2)  # Lluvia ocasional
            })
    
    # Caso 2: Junio (Invierno) - Alta probabilidad de frío
    june_data = []
    for year in range(2004, 2024):
        for day in range(1, 31):  # Junio tiene 30 días
            # 35% de los días con temperatura < 25°C (frío para playa)
            if np.random.random() < 0.35:
                temp = np.random.normal(20, 3)  # Frío
            else:
                temp = np.random.normal(28, 2)  # Temperatura normal
            
            june_data.append({
                'Year': year,
                'Month': 6,
                'Max_Temperature_C': max(temp, 10),  # Mínimo 10°C
                'Precipitation_mm': np.random.exponential(3)  # Más lluvia en invierno
            })
    
    # Caso 3: Abril (Otoño) - Baja probabilidad de condiciones extremas
    april_data = []
    for year in range(2004, 2024):
        for day in range(1, 31):  # Abril tiene 30 días
            # Solo 5% de los días con condiciones extremas
            if np.random.random() < 0.05:
                temp = np.random.normal(35, 2)  # Calor extremo ocasional
            else:
                temp = np.random.normal(22, 2)  # Temperatura templada
            
            april_data.append({
                'Year': year,
                'Month': 4,
                'Max_Temperature_C': max(temp, 15),
                'Precipitation_mm': np.random.exponential(1.5)  # Poca lluvia
            })
    
    return {
        'december': pd.DataFrame(december_data),
        'june': pd.DataFrame(june_data),
        'april': pd.DataFrame(april_data)
    }

def test_percentile_calculation():
    """
    Verificar que el cálculo del percentil 90 funciona correctamente
    """
    print("\n📊 AUDITORÍA DEL BACKEND - Validación del Umbral de Riesgo")
    print("=" * 60)
    
    # Crear datos de prueba con distribución conocida
    test_data = pd.DataFrame({
        'Max_Temperature_C': [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58]
    })
    
    # Calcular percentil 90 manualmente
    manual_percentile = np.percentile(test_data['Max_Temperature_C'], 90)
    print(f"Percentil 90 manual: {manual_percentile:.1f}°C")
    
    # Verificar que la función usa umbral fijo (30°C según el código actual)
    risk_analysis = calculate_heat_risk(test_data)
    print(f"Umbral usado en función: {risk_analysis['risk_threshold']:.1f}°C")
    print(f"Probabilidad calculada: {risk_analysis['probability']:.1f}%")
    print(f"Nivel de riesgo: {risk_analysis['risk_level']}")
    
    return risk_analysis

def test_risk_level_mapping():
    """
    Verificar el mapeo correcto de niveles de riesgo
    """
    print("\n🎯 AUDITORÍA DEL BACKEND - Mapeo de Nivel de Riesgo")
    print("=" * 60)
    
    test_cases = [
        (25.0, "HIGH"),      # ≥20%
        (15.0, "MODERATE"),  # 10-19%
        (7.5, "LOW"),        # 5-9%
        (3.0, "MINIMAL")     # <5%
    ]
    
    for expected_prob, expected_level in test_cases:
        # Crear datos que produzcan la probabilidad esperada
        total_days = 100
        adverse_days = int((expected_prob / 100) * total_days)
        
        # Crear DataFrame con la distribución deseada
        temps = [35.0] * adverse_days + [25.0] * (total_days - adverse_days)
        test_data = pd.DataFrame({'Max_Temperature_C': temps})
        
        result = calculate_heat_risk(test_data)
        actual_level = result['risk_level']
        actual_prob = result['probability']
        
        status = "✅" if actual_level == expected_level else "❌"
        print(f"{status} Probabilidad: {actual_prob:.1f}% → Nivel: {actual_level} (esperado: {expected_level})")

def test_critical_cases_e2e():
    """
    Prueba de casos críticos E2E para Montevideo
    """
    print("\n🧪 PRUEBA DE CASO CRÍTICO E2E")
    print("=" * 60)
    
    # Crear datos mock controlados
    mock_data = create_mock_data_for_testing()
    
    test_cases = [
        {
            'name': 'Caso 1: Montevideo, Diciembre, "Very Hot"',
            'data': mock_data['december'],
            'condition': 'Very Hot',
            'expected_risk': ['HIGH', 'MODERATE'],
            'expected_recommendation': 'Stay Hydrated',
            'reason': 'Diciembre es verano, alta probabilidad histórica de calor extremo en Montevideo'
        },
        {
            'name': 'Caso 2: Montevideo, Junio, "Very Cold"',
            'data': mock_data['june'],
            'condition': 'Very Cold',
            'expected_risk': ['HIGH', 'MODERATE'],
            'expected_recommendation': 'Dress Warmly / Consider Indoor Plan',
            'reason': 'Junio es invierno, alta probabilidad histórica de frío extremo'
        },
        {
            'name': 'Caso 3: Montevideo, Abril, "Very Rainy"',
            'data': mock_data['april'],
            'condition': 'Very Rainy',
            'expected_risk': ['LOW', 'MINIMAL'],
            'expected_recommendation': 'Conditions are generally favorable',
            'reason': 'Abril es una estación intermedia, la probabilidad de lluvia extrema debería ser menor'
        }
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n🔍 {case['name']}")
        print("-" * 50)
        
        # Calcular riesgos
        temp_risk = calculate_heat_risk(case['data'])
        precip_risk = calculate_precipitation_risk(case['data'])
        cold_risk = calculate_cold_risk(case['data'])
        
        print(f"📊 Datos: {len(case['data'])} registros")
        print(f"🌡️  Temperatura - Riesgo: {temp_risk['risk_level']} ({temp_risk['probability']:.1f}%)")
        print(f"🌧️  Precipitación - Riesgo: {precip_risk['risk_level']} ({precip_risk['probability']:.1f}%)")
        print(f"❄️  Frío - Riesgo: {cold_risk['risk_level']} ({cold_risk['probability']:.1f}%)")
        
        # Determinar el riesgo principal según la condición
        if case['condition'] == 'Very Hot':
            main_risk = temp_risk
        elif case['condition'] == 'Very Cold':
            main_risk = cold_risk
        elif case['condition'] == 'Very Rainy':
            main_risk = precip_risk
        else:
            main_risk = temp_risk
        
        # Verificar si el resultado está en el rango esperado
        risk_match = main_risk['risk_level'] in case['expected_risk']
        status = "✅" if risk_match else "❌"
        
        print(f"{status} Resultado: {main_risk['risk_level']} (esperado: {case['expected_risk']})")
        print(f"💡 Recomendación: {main_risk['status_message']}")
        print(f"📝 Razón: {case['reason']}")
        
        results.append({
            'case': case['name'],
            'risk_level': main_risk['risk_level'],
            'probability': main_risk['probability'],
            'expected_risk': case['expected_risk'],
            'match': risk_match,
            'recommendation': main_risk['status_message']
        })
    
    return results

def test_nasa_data_integration():
    """
    Verificar la integración con datos reales de NASA
    """
    print("\n🌍 VERIFICACIÓN DE INTEGRACIÓN NASA POWER")
    print("=" * 60)
    
    try:
        # Probar con datos reales de Montevideo
        print("🔄 Cargando datos reales de NASA POWER para Montevideo...")
        real_data = load_historical_data(month_filter=12, lat=-34.90, lon=-56.16)
        
        if not real_data.empty:
            print(f"✅ Datos cargados: {len(real_data)} registros")
            print(f"📅 Rango de años: {real_data['Year'].min()}-{real_data['Year'].max()}")
            print(f"🌡️  Temperatura: {real_data['Max_Temperature_C'].min():.1f}°C - {real_data['Max_Temperature_C'].max():.1f}°C")
            print(f"🌧️  Precipitación: {real_data['Precipitation_mm'].min():.1f}mm - {real_data['Precipitation_mm'].max():.1f}mm")
            
            # Calcular riesgos con datos reales
            temp_risk = calculate_heat_risk(real_data)
            precip_risk = calculate_precipitation_risk(real_data)
            cold_risk = calculate_cold_risk(real_data)
            
            print(f"\n📊 Análisis de Riesgo (Datos Reales - Diciembre):")
            print(f"🌡️  Temperatura: {temp_risk['risk_level']} ({temp_risk['probability']:.1f}%)")
            print(f"🌧️  Precipitación: {precip_risk['risk_level']} ({precip_risk['probability']:.1f}%)")
            print(f"❄️  Frío: {cold_risk['risk_level']} ({cold_risk['probability']:.1f}%)")
            
            return True
        else:
            print("❌ No se pudieron cargar datos reales de NASA")
            return False
            
    except Exception as e:
        print(f"❌ Error en integración NASA: {str(e)}")
        return False

def generate_test_report(results):
    """
    Generar reporte de pruebas
    """
    print("\n📋 REPORTE DE PRUEBAS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['match'])
    
    print(f"Total de pruebas: {total_tests}")
    print(f"Pruebas exitosas: {passed_tests}")
    print(f"Pruebas fallidas: {total_tests - passed_tests}")
    print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📊 RESUMEN DE CASOS:")
    for result in results:
        status = "✅" if result['match'] else "❌"
        print(f"{status} {result['case']}")
        print(f"   Resultado: {result['risk_level']} ({result['probability']:.1f}%)")
        print(f"   Esperado: {result['expected_risk']}")
        print()

def main():
    """
    Función principal de verificación
    """
    print("🧪 VERIFICACIÓN END-TO-END: COHERENCIA LÓGICA Y DATOS NASA")
    print("=" * 80)
    print("NASA Weather Risk Navigator - Test Suite")
    print("=" * 80)
    
    # 1. Auditoría del Backend
    test_percentile_calculation()
    test_risk_level_mapping()
    
    # 2. Pruebas E2E
    results = test_critical_cases_e2e()
    
    # 3. Verificación NASA
    nasa_success = test_nasa_data_integration()
    
    # 4. Reporte final
    generate_test_report(results)
    
    # 5. Conclusión
    print("\n🎯 CONCLUSIÓN")
    print("=" * 60)
    
    if nasa_success:
        print("✅ Integración con NASA POWER: FUNCIONAL")
    else:
        print("❌ Integración con NASA POWER: REQUIERE ATENCIÓN")
    
    total_passed = sum(1 for r in results if r['match'])
    if total_passed == len(results):
        print("✅ Lógica de negocio: COHERENTE")
        print("✅ Sistema listo para implementación de PostgreSQL")
    else:
        print("❌ Lógica de negocio: REQUIERE CORRECCIONES")
        print("❌ Revisar mapeo de niveles de riesgo antes de continuar")

if __name__ == "__main__":
    main()

