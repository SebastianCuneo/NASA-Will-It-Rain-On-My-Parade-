#!/usr/bin/env python3
"""
Script de ejecución de pruebas para NASA POWER API
NASA Space Apps Challenge - Test Runner
"""

import sys
import os
import unittest
import argparse
from datetime import datetime

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_tests(test_type='all', verbose=False, real_api=False):
    """
    Ejecuta las pruebas de NASA POWER API
    
    Args:
        test_type: Tipo de pruebas a ejecutar ('unit', 'integration', 'all')
        verbose: Si mostrar salida detallada
        real_api: Si ejecutar pruebas de integración real
    """
    
    print("🚀 INICIANDO PRUEBAS DE NASA POWER API")
    print("="*60)
    print(f"Tipo de pruebas: {test_type}")
    print(f"Verbose: {verbose}")
    print(f"Pruebas reales de API: {real_api}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Configurar el loader de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Importar las pruebas
    try:
        from tests.test_nasa_power_api import TestNasaPowerAPI, TestNasaPowerAPIIntegration
        from tests.test_climate_trend import TestClimateTrendAnalysis, TestGetClimateTrendData, TestClimateTrendIntegration
        from tests.test_api_endpoint import (
            TestRiskEndpoint,
            TestRiskEndpointWeatherConditions,
            TestRiskEndpointDateFormats,
            TestRiskEndpointErrorHandling,
            TestRiskEndpointAlternatives
        )
    except ImportError as e:
        print(f"❌ Error importando pruebas: {e}")
        return False
    
    # Agregar pruebas según el tipo
    if test_type in ['unit', 'all']:
        print("📋 Agregando pruebas unitarias...")
        suite.addTests(loader.loadTestsFromTestCase(TestNasaPowerAPI))
        suite.addTests(loader.loadTestsFromTestCase(TestClimateTrendAnalysis))
        suite.addTests(loader.loadTestsFromTestCase(TestGetClimateTrendData))
        suite.addTests(loader.loadTestsFromTestCase(TestRiskEndpoint))
        suite.addTests(loader.loadTestsFromTestCase(TestRiskEndpointWeatherConditions))
        suite.addTests(loader.loadTestsFromTestCase(TestRiskEndpointDateFormats))
        suite.addTests(loader.loadTestsFromTestCase(TestRiskEndpointErrorHandling))
        suite.addTests(loader.loadTestsFromTestCase(TestRiskEndpointAlternatives))
    
    if test_type in ['integration', 'all']:
        print("🌐 Agregando pruebas de integración...")
        if real_api:
            # Habilitar pruebas de integración real
            for test in loader.loadTestsFromTestCase(TestNasaPowerAPIIntegration):
                for subtest in test:
                    if hasattr(subtest, '_testMethodName'):
                        if subtest._testMethodName == 'test_real_api_call':
                            # Remover el skip decorator
                            subtest.__class__.test_real_api_call = unittest.case.skipIf(
                                False, "Integration test enabled"
                            )(subtest.__class__.test_real_api_call)
        suite.addTests(loader.loadTestsFromTestCase(TestNasaPowerAPIIntegration))
        suite.addTests(loader.loadTestsFromTestCase(TestClimateTrendIntegration))
    
    # Ejecutar las pruebas
    print(f"\n🧪 Ejecutando {suite.countTestCases()} pruebas...")
    print("-"*60)
    
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE EJECUCIÓN")
    print("="*60)
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Saltadas: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ PRUEBAS FALLIDAS:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERRORES:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("✅ Todas las pruebas pasaron exitosamente!")
        return True
    else:
        print("❌ Algunas pruebas fallaron")
        return False

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Ejecutor de pruebas para NASA POWER API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py                    # Ejecutar todas las pruebas unitarias
  python run_tests.py --type unit        # Solo pruebas unitarias
  python run_tests.py --type integration # Solo pruebas de integración
  python run_tests.py --real-api         # Incluir pruebas reales de API
  python run_tests.py --verbose          # Salida detallada
        """
    )
    
    parser.add_argument(
        '--type', 
        choices=['unit', 'integration', 'all'],
        default='all',
        help='Tipo de pruebas a ejecutar (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar salida detallada'
    )
    
    parser.add_argument(
        '--real-api',
        action='store_true',
        help='Ejecutar pruebas reales de integración con NASA API'
    )
    
    args = parser.parse_args()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('backend/logic.py'):
        print("❌ Error: Ejecutar desde el directorio raíz del proyecto")
        print("   El archivo backend/logic.py no se encontró")
        return 1
    
    # Ejecutar las pruebas
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        real_api=args.real_api
    )
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
