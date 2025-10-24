# Pruebas de NASA POWER API

Este directorio contiene pruebas comprehensivas para la función `fetch_nasa_power_data` que integra con la NASA POWER API.

## 📁 Estructura de Archivos

```
tests/
├── __init__.py                    # Inicializador del paquete
├── test_nasa_power_api.py         # Pruebas principales de la API
├── test_utils.py                  # Utilidades y helpers para pruebas
├── run_tests.py                   # Script de ejecución de pruebas
└── README.md                      # Este archivo
```

## 🧪 Tipos de Pruebas

### **Pruebas Unitarias** (`TestNasaPowerAPI`)
- ✅ Obtención exitosa de datos
- ✅ Validación de estructura de datos
- ✅ Manejo de respuestas de error de la API
- ✅ Manejo de estructura JSON inválida
- ✅ Manejo de parámetros faltantes
- ✅ Manejo de timeout de red
- ✅ Manejo de errores de conexión
- ✅ Manejo de errores HTTP
- ✅ Manejo de errores de decodificación JSON
- ✅ Manejo de valores None en datos
- ✅ Parsing correcto de fechas
- ✅ Respuestas con datos vacíos
- ✅ Coordenadas en casos límite
- ✅ Rangos de años en casos límite
- ✅ Construcción correcta de URL de API

### **Pruebas de Integración** (`TestNasaPowerAPIIntegration`)
- 🌐 Llamada real a la NASA POWER API (opcional)

## 🚀 Ejecución de Pruebas

### **Método 1: Script de Ejecución (Recomendado)**
```bash
# Desde el directorio raíz del proyecto
cd backend/tests
python run_tests.py

# Opciones disponibles:
python run_tests.py --type unit        # Solo pruebas unitarias
python run_tests.py --type integration # Solo pruebas de integración
python run_tests.py --real-api         # Incluir pruebas reales de API
python run_tests.py --verbose          # Salida detallada
```

### **Método 2: unittest Directo**
```bash
# Desde el directorio backend
python -m unittest tests.test_nasa_power_api -v
python -m unittest tests.test_nasa_power_api.TestNasaPowerAPI -v
python -m unittest tests.test_nasa_power_api.TestNasaPowerAPIIntegration -v
```

### **Método 3: pytest (si está instalado)**
```bash
# Desde el directorio backend
pytest tests/test_nasa_power_api.py -v
```

## 📊 Ejemplo de Salida

```
🚀 INICIANDO PRUEBAS DE NASA POWER API
============================================================
Tipo de pruebas: all
Verbose: False
Pruebas reales de API: False
Timestamp: 2024-01-15 14:30:25
============================================================

📋 Agregando pruebas unitarias...
🌐 Agregando pruebas de integración...

🧪 Ejecutando 16 pruebas...
------------------------------------------------------------

test_api_error_response (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_api_url_construction (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_connection_error (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_coordinate_edge_cases (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_data_structure_validation (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_data_with_none_values (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_date_parsing (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_empty_data_response (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_http_error (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_invalid_json_structure (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_json_decode_error (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_missing_parameters (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_network_timeout (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_successful_data_fetch (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_year_range_edge_cases (tests.test_nasa_power_api.TestNasaPowerAPI) ... ok
test_real_api_call (tests.test_nasa_power_api.TestNasaPowerAPIIntegration) ... SKIP

============================================================
RESUMEN DE EJECUCIÓN
============================================================
Pruebas ejecutadas: 16
Fallos: 0
Errores: 0
Saltadas: 1

Tasa de éxito: 100.0%
✅ Todas las pruebas pasaron exitosamente!
```

## 🔧 Configuración

### **Pruebas de Integración Real**
Las pruebas de integración real están deshabilitadas por defecto para evitar:
- Llamadas innecesarias a la API de la NASA
- Dependencia de conexión a internet
- Posibles límites de rate limiting

Para habilitarlas:
```bash
python run_tests.py --real-api
```

### **Logging**
Las pruebas generan logs detallados en:
```
backend/logs/nasa_api_tests_YYYYMMDD_HHMMSS.log
```

## 📋 Casos de Prueba Cubiertos

### **✅ Casos Exitosos**
- Coordenadas válidas de Montevideo
- Rangos de años válidos (1-20 años)
- Respuestas JSON válidas de la NASA
- Datos con valores realistas

### **❌ Casos de Error**
- Respuestas de error de la API
- Estructura JSON inválida
- Parámetros faltantes
- Timeouts de red
- Errores de conexión
- Errores HTTP (404, 500, etc.)
- Errores de decodificación JSON
- Datos vacíos o con valores None

### **🔍 Casos Límite**
- Coordenadas en los extremos del planeta
- Rangos de años mínimos (1 año)
- Datos con valores None
- Respuestas con estructura parcial

## 🛠️ Utilidades de Prueba

### **`test_utils.py`**
- `setup_test_logging()`: Configuración de logging
- `get_test_coordinates()`: Coordenadas de prueba para diferentes ciudades
- `get_test_year_ranges()`: Rangos de años para pruebas
- `create_mock_nasa_response()`: Generador de respuestas mock
- `validate_dataframe_structure()`: Validador de estructura de DataFrame
- `print_test_summary()`: Impresor de resumen de resultados

## 📈 Métricas de Prueba

- **Cobertura**: 100% de la función `fetch_nasa_power_data`
- **Casos de prueba**: 15+ casos diferentes
- **Tiempo de ejecución**: ~30 segundos (pruebas unitarias)
- **Dependencias**: unittest (estándar), requests, pandas

## 🔍 Debugging

### **Problemas Comunes**

1. **ImportError**: Asegúrate de ejecutar desde el directorio correcto
2. **Mock failures**: Verifica que los mocks estén configurados correctamente
3. **Timeout errors**: Aumenta el timeout en las pruebas si es necesario

### **Logs Detallados**
```bash
python run_tests.py --verbose
```

## 📚 Referencias

- [NASA POWER API Documentation](https://power.larc.nasa.gov/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pandas Testing](https://pandas.pydata.org/docs/reference/testing.html)
