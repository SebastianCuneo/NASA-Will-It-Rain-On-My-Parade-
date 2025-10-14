# 🚀 NASA Weather Risk Navigator - Backlog Simplificado (Post-Hackathon)

## 📋 Executive Summary

**Contexto:** Reto Post-Hackatón NASA Space Apps Challenge - Validación Técnica y Conceptual

**Objetivo Estratégico Único:**  
Reemplazar *mock data* por **datos reales de INUMET** (Montevideo) para **validar la metodología del 90th Percentil** y preparar el prototipo para defensa e informe técnico.

**Coherencia con el Proyecto Actual:** ✅
- Se mantiene el análisis de riesgo basado en **percentil 90**
- Se mantiene el sistema de **4 niveles de riesgo** (MINIMAL, LOW, MODERATE, HIGH)
- Se mantiene la **compatibilidad de actividades** y Plan B
- Se mantiene la **arquitectura FastAPI + React**
- **SE SIMPLIFICA**: Solo Montevideo, sin ML, sin optimizaciones complejas

**Alcance Simplificado:**
- ✅ **SÍ**: Datos reales INUMET (Montevideo, 60K+ registros)
- ✅ **SÍ**: **Solo 3 variables**: Temperatura, Precipitación, Humedad
- ✅ **SÍ**: Visualizaciones Plotly con línea P90
- ✅ **SÍ**: Plan B con Gemini AI (sugerencias inteligentes basadas en riesgo)
- ✅ **SÍ**: Docker y documentación para defensa
- ❌ **NO**: Machine Learning con Prophet (Visión futura)
- ❌ **NO**: Multi-ciudad (Visión futura)
- ❌ **NO**: Redis/Caching avanzado (Visión futura)
- ❌ **NO**: Viento, UV, sensación térmica (Visión futura)

**Enfoque:** Validación técnica con prototipo funcional mínimo

---

## 🎯 Objetivo Estratégico Simplificado

### Objetivo Único: Validar Metodología P90 con Datos Reales

**Meta Principal:**  
Demostrar que la metodología del 90th Percentil funciona con datos reales de complejidad significativa (60K+ registros INUMET) para **3 variables climáticas clave**: Temperatura, Precipitación y Humedad.

**Criterios de Éxito:**
1. ✅ Sistema procesa datos reales INUMET (Montevideo)
2. ✅ Cálculo P90 funciona para **Temperatura, Precipitación y Humedad**
3. ✅ Visualización Plotly muestra línea P90 para las 3 variables
4. ✅ Análisis de riesgo mantiene coherencia (4 niveles por variable)
5. ✅ Plan B con Gemini AI genera sugerencias inteligentes
6. ✅ Prototipo Dockerizado y documentado para defensa

### Validación Técnica y Conceptual
- ✅ **Validación Técnica**: Sistema funciona con datasets grandes
- ✅ **Validación Conceptual**: P90 detecta extremos climáticos reales
- ✅ **Validación Arquitectónica**: FastAPI + React escalable
- ✅ **Artefactos para Informe**: Screenshots, métricas, documentación

---

## 📋 BACKLOG SIMPLIFICADO - Tareas Priorizadas

### 🔥 **SECCIÓN 1: Validar el Núcleo Científico** (PRIORIDAD CRÍTICA)

**Objetivo:** Migrar a datos reales y asegurar que el cálculo del 90th Percentil funciona con complejidad real.

| **ID** | **Tarea** | **Descripción** | **Entregable** | **Complejidad** |
|--------|-----------|-----------------|----------------|-----------------|
| **T1.1** | Integrar datos INUMET | Migrar `logic.py` para leer `python/inumet_temp_prec.csv` (temperatura, precipitación, humedad) | Función `load_inumet_data()` funcionando | Media |
| **T1.2** | Filtrar estación Montevideo | Implementar filtrado por estación: `"Aeropuerto Melilla G3"` | Datos de Montevideo aislados | Baja |
| **T1.3** | Agregación horaria → diaria | Convertir 60K+ registros a diarios: **max temp, sum precipitación, avg humedad** | Función `aggregate_daily()` con 3 variables | Media |
| **T1.4** | Validar cálculo P90 | Verificar P90 para **temperatura, precipitación y humedad** | 3 umbrales P90 calculados | Alta |
| **T1.5** | Actualizar endpoint `/api/risk` | Modificar API para devolver riesgo de las 3 variables | API responde con 3 análisis P90 | Media |
| **T1.6** | Tests de integración | Crear tests para carga de datos y cálculo P90 (3 variables) | `test_inumet_integration.py` | Media |

**Criterio de Completitud:** Sistema calcula P90 correctamente sobre 60,000+ registros reales de Montevideo.

---

### 🟡 **SECCIÓN 2: Prototipo Funcional y Visualización** (PRIORIDAD IMPORTANTE)

**Objetivo:** Integrar Plotly y mostrar visualmente la línea del 90th Percentil, demostrando viabilidad conceptual.

| **ID** | **Tarea** | **Descripción** | **Entregable** | **Complejidad** |
|--------|-----------|-----------------|----------------|-----------------|
| **T2.1** | Instalar Plotly | Añadir `plotly` y `react-plotly.js` a dependencias | `requirements.txt` y `package.json` actualizados | Baja |
| **T2.2** | Endpoint `/api/visualizations` | Crear endpoint que devuelve datos históricos + P90 para **3 variables** | API JSON con datos Temp/Precip/Humedad | Media |
| **T2.3** | Componente `PlotlyChart.jsx` | Crear componente React para gráficos interactivos | Componente React funcional | Alta |
| **T2.4** | Gráfico de temperatura | Histograma de temperatura con línea roja P90 | Gráfico interactivo temperatura | Alta |
| **T2.5** | Gráfico de precipitación | Histograma de precipitación con línea roja P90 | Gráfico interactivo precipitación | Media |
| **T2.6** | Gráfico de humedad | Histograma de humedad con línea roja P90 | Gráfico interactivo humedad | Media |
| **T2.7** | Configurar Gemini API | Obtener API key de Google AI Studio y crear archivo `.env` | Variables de entorno configuradas | Baja |
| **T2.8** | Plan B con Gemini AI | Implementar función `generateGeminiPlanB()` con prompt optimizado | Sugerencias IA funcionando | Media |
| **T2.9** | Integrar visualizaciones | Añadir 3 gráficos Plotly en sección de resultados | UI muestra 3 visualizaciones P90 | Media |
| **T2.10** | Screenshots para informe | Capturar screenshots de visualizaciones y Plan B | Imágenes para documentación | Baja |

**Criterio de Completitud:** Usuario ve gráficos interactivos que muestran claramente la línea P90 y su significado.

---

### 🟡 **SECCIÓN 3: Documentación y Defensa** (PRIORIDAD IMPORTANTE)

**Objetivo:** Dockerizar, preparar deployment y obtener artefactos para el Informe Técnico.

| **ID** | **Tarea** | **Descripción** | **Entregable** | **Complejidad** |
|--------|-----------|-----------------|----------------|-----------------|
| **T3.1** | Dockerfile backend | Crear `Dockerfile` para backend FastAPI | `backend/Dockerfile` | Media |
| **T3.2** | Dockerfile frontend | Crear `Dockerfile` para frontend React | `frontend/Dockerfile` | Media |
| **T3.3** | Docker Compose | Crear `docker-compose.yml` para orquestar frontend + backend | Aplicación completa con `docker-compose up` | Media |
| **T3.4** | Actualizar README | Documentar instalación con Docker, arquitectura de datos reales | `README.md` actualizado | Baja |
| **T3.5** | Crear `TECHNICAL_REPORT.md` | Documentar metodología P90, análisis de datos INUMET, resultados | Documento técnico para defensa | Alta |
| **T3.6** | Métricas de performance | Medir tiempos de procesamiento (60K registros → P90) | Tabla de métricas en informe | Media |
| **T3.7** | Validación científica | Comparar P90 calculado con literatura climatológica Uruguay | Validación en informe técnico | Alta |

**Criterio de Completitud:** Proyecto Dockerizado, documentado y con métricas/validaciones para defensa técnica.

---

### 🔮 **SECCIÓN 4: Próximos Pasos (Visión Futura para el Informe)** (PRIORIDAD BAJA)

**Justificación:** Estas tareas demuestran escalabilidad y visión del proyecto, pero NO son críticas para validar la metodología P90.

| **ID** | **Tarea (Futuro)** | **Justificación** | **Valor para Informe** |
|--------|--------------------|-------------------|------------------------|
| **F1** | Machine Learning con Prophet | Predicción temporal (7-90 días) aplicando P90 | Demuestra potencial de expansión |
| **F2** | Expansión Multi-Ciudad | Soporte para 7 ciudades de Uruguay | Escalabilidad geográfica |
| **F3** | Optimización con Redis | Caching de modelos ML y cálculos P90 | Performance en producción |
| **F4** | PWA y Service Workers | Aplicación offline-first | Accesibilidad sin conexión |
| **F5** | Integración NASA APIs | MERRA-2 y GPM en tiempo real | Conexión directa con datos NASA |
| **F6** | Testing exhaustivo | >80% code coverage con pytest | Calidad de código profesional |
| **F7** | CI/CD Pipeline | GitHub Actions para deploy automático | DevOps moderno |

**Nota para Informe:** Estas tareas se incluyen en la sección "Trabajo Futuro" del informe técnico, demostrando que el proyecto tiene una hoja de ruta clara y escalable.

---

## 📊 Resumen de Entregables Clave

### **Entregables Mínimos para Validación:**

1. **Sistema Funcional con Datos Reales (3 Variables)**
   - Backend procesa `inumet_temp_prec.csv` (60K+ registros)
   - Cálculo P90 para: **Temperatura, Precipitación, Humedad**
   - Frontend muestra análisis de riesgo P90 con datos reales
   
2. **Visualizaciones P90 (3 Gráficos)**
   - Gráfico Plotly de **Temperatura** con línea P90
   - Gráfico Plotly de **Precipitación** con línea P90
   - Gráfico Plotly de **Humedad** con línea P90
   
3. **Plan B con Gemini AI**
   - Sistema de sugerencias inteligentes con Gemini API
   - Respuestas personalizadas basadas en riesgo detectado
   - Integración simple (~2-3 segundos de respuesta)
   
4. **Documentación Técnica**
   - `TECHNICAL_REPORT.md` con metodología y resultados
   - Screenshots de visualizaciones (3 variables)
   - Métricas de performance

5. **Despliegue**
   - Proyecto Dockerizado (`docker-compose up`)
   - README actualizado con instrucciones

---

## 🎯 Criterios de Éxito para el Reto

| **Criterio** | **Métrica** | **Validación** |
|--------------|-------------|----------------|
| **Viabilidad Técnica** | Sistema procesa 60K+ registros | ✅ P90 calculado correctamente |
| **Viabilidad Conceptual** | P90 detecta extremos reales | ✅ Visualización muestra patrones |
| **Arquitectura Escalable** | FastAPI + React modular | ✅ Código organizado y testeado |
| **Documentación** | Informe técnico completo | ✅ Metodología + Resultados + Futuro |

---

## ⚠️ Tareas ELIMINADAS (Fuera del Alcance)

Las siguientes tareas se eliminan del alcance actual pero se documentan como "Visión Futura":

### ❌ **Eliminado: Prophet Machine Learning**
- **Razón:** Demasiado complejo para validación inicial
- **Valor:** Predicción temporal no es crítica para validar P90 histórico
- **Futuro:** Sección F1 del backlog

### ❌ **Eliminado: Expansión Multi-Ciudad**  
- **Razón:** Montevideo es suficiente para validar metodología
- **Valor:** Escalabilidad geográfica no es crítica inicialmente
- **Futuro:** Sección F2 del backlog

### ❌ **Eliminado: Optimización Redis/Caching**
- **Razón:** Performance es aceptable sin optimización
- **Valor:** No crítico para prototipo de validación
- **Futuro:** Sección F3 del backlog

---

## 📐 Comparación: Plan Original vs. Simplificado

| **Aspecto** | **Plan Original (2 semanas)** | **Plan Simplificado (Reto)** |
|-------------|-------------------------------|------------------------------|
| **Alcance** | Full product con ML | Validación metodología P90 |
| **Tareas** | 50+ tareas complejas | **23 tareas enfocadas** |
| **Variables Climáticas** | Múltiples (Temp, Precip, Viento, UV, etc.) | **Solo 3: Temp, Precip, Humedad** |
| **Ciudades** | 7 ciudades Uruguay | Solo Montevideo |
| **ML/Prophet** | Predicción 7-90 días | ❌ Eliminado (Visión futura) |
| **Plan B** | IA generativa (Gemini API) | **IA con Gemini (simplificado)** |
| **Optimización** | Redis + PWA + CI/CD | ❌ Eliminado (Visión futura) |
| **Visualizaciones** | Múltiples gráficos avanzados | **3 gráficos Plotly** (Temp/Precip/Humedad) |
| **Deploy** | Producción cloud | Docker local + documentación |
| **Timeline** | 10 días hábiles | Flexible (enfoque en validación) |

---

## 🚀 Orden de Ejecución Recomendado

### **Fase 1: Núcleo Científico (Crítico)**
```
T1.1 → T1.2 → T1.3 → T1.4 → T1.5 → T1.6
(Integrar INUMET → Filtrar Montevideo → Agregar → Validar P90 → API → Tests)
```

### **Fase 2: Visualización y Plan B con IA (Importante)**
```
T2.1 → T2.2 → T2.3 → T2.4 → T2.5 → T2.6 → T2.7 → T2.8 → T2.9 → T2.10
(Instalar Plotly → Endpoint → Componente → Gráfico Temp → Gráfico Precip → 
 Gráfico Humedad → Config Gemini → Plan B IA → Integrar → Screenshots)
```

### **Fase 3: Documentación (Importante)**
```
T3.1 → T3.2 → T3.3 → T3.4 → T3.5 → T3.6 → T3.7
(Docker Backend → Frontend → Compose → README → Informe → Métricas → Validación)
```

---

## 📝 Dependencias Actualizadas (Simplificadas)

### **Backend** (`requirements.txt`)
```txt
# Core (Ya existentes)
fastapi
uvicorn
pandas
numpy
python-multipart

# Nuevas (Solo esenciales)
plotly  # Para visualizaciones
pytest  # Para tests
```

### **Frontend** (`package.json`)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "react-plotly.js": "^2.6.0",  // NUEVO - Visualizaciones
    "plotly.js": "^2.27.0"        // NUEVO - Visualizaciones
  }
}
```

**Variables de Entorno** (`.env`):
```env
# Gemini API Key (obtener en https://aistudio.google.com/apikey)
REACT_APP_GEMINI_API_KEY=tu_api_key_aqui
```

**❌ NO incluir:** `prophet`, `redis`, o dependencias complejas de ML.  
✅ **SÍ incluir**: Gemini API (solo configuración, sin dependencias)

---

## 🎓 Artefactos para Informe Técnico

### **1. Screenshots Requeridos**
- [ ] Dashboard mostrando análisis P90 con datos reales
- [ ] Gráfico Plotly con línea roja P90
- [ ] Comparación mock data vs. datos reales
- [ ] Ejemplo de análisis de riesgo HIGH/MODERATE/LOW

### **2. Métricas Técnicas**
- [ ] Tiempo de procesamiento: 60K registros → P90
- [ ] Tamaño del dataset: MB procesados
- [ ] Precisión: P90 calculado vs. literatura
- [ ] Performance: Requests/segundo del API

### **3. Validación Científica**
- [ ] Comparar P90 calculado con datos climatológicos Uruguay
- [ ] Validar que P90 detecta eventos extremos históricos conocidos
- [ ] Justificar elección de P90 vs. otros percentiles

---

## ✅ Checklist Final para Defensa

### **Técnico**
- [ ] Sistema funciona con `docker-compose up`
- [ ] P90 se calcula correctamente sobre datos INUMET
- [ ] Visualizaciones Plotly muestran línea P90
- [ ] Tests básicos pasan (`pytest`)

### **Documentación**
- [ ] `README.md` actualizado con Docker
- [ ] `TECHNICAL_REPORT.md` completo
- [ ] Screenshots de calidad en documentación
- [ ] Métricas de performance documentadas

### **Conceptual**
- [ ] Justificación científica de metodología P90
- [ ] Comparación con literatura climatológica
- [ ] Demostración de viabilidad técnica y conceptual
- [ ] Roadmap claro de "Trabajo Futuro"

---

## 🎯 Resumen Ejecutivo para el Reto

**Objetivo Alcanzado:**  
✅ Validar que la metodología del 90th Percentil funciona con datos reales de complejidad significativa (60K+ registros INUMET).

**Entregables Clave:**
1. Sistema funcional procesando datos reales
2. Visualizaciones P90 interactivas
3. Documentación técnica completa
4. Prototipo Dockerizado

**Diferenciación:**
- ✅ Datos reales vs. mock data
- ✅ Visualización científica del P90
- ✅ Arquitectura escalable (FastAPI + React)
- ✅ Roadmap claro hacia producto completo

**Valor para Defensa:**
- Demuestra viabilidad técnica (funciona con datasets grandes)
- Demuestra viabilidad conceptual (P90 detecta extremos)
- Arquitectura lista para escalar (ML, multi-ciudad en roadmap)
- Metodología científicamente rigurosa (P90 estándar NASA)

---

---

## 🔄 Plan B con Gemini AI - Especificación Simplificada

### **Objetivo del Plan B**
Proporcionar sugerencias **inteligentes y personalizadas** de actividades alternativas basadas en el nivel de riesgo detectado, usando Gemini API de forma simple y eficiente.

### **¿Por Qué Gemini AI es Simple?**

✅ **Solo 1 endpoint**: Gemini API REST simple  
✅ **Sin configuración compleja**: API Key + URL  
✅ **Sin entrenamiento**: Modelo pre-entrenado  
✅ **Respuesta rápida**: 2-3 segundos  
✅ **Código mínimo**: ~30 líneas

### **Implementación Simplificada (Frontend)**

```javascript
// frontend/src/components/WeatherResults.jsx

async function generateGeminiPlanB(riskLevels, originalActivity, location, date) {
  /*
   * Input:
   * - riskLevels = { temperature: "HIGH", precipitation: "LOW", humidity: "MODERATE" }
   * - originalActivity = "beach" | "picnic" | "hiking" | etc.
   * - location = "Montevideo"
   * - date = "2024-03-15"
   * 
   * Output:
   * - Array de 2-3 sugerencias generadas por Gemini
   */
  
  // 1. Construir prompt contextual
  const riskSummary = Object.entries(riskLevels)
    .filter(([_, level]) => level === "HIGH" || level === "MODERATE")
    .map(([variable, level]) => `${variable}: ${level}`)
    .join(", ");
  
  const prompt = `
You are a weather-aware activity planner. 

CONTEXT:
- Location: ${location}
- Date: ${date}
- Planned activity: ${originalActivity}
- Weather risks detected: ${riskSummary}

TASK:
Suggest 2-3 alternative activities that are safe and enjoyable given these weather conditions.

FORMAT (JSON):
[
  {
    "activity": "Activity name",
    "icon": "🏛️",
    "reason": "Why this is better"
  }
]

Be concise, practical, and consider local Montevideo activities.
`;

  // 2. Llamar a Gemini API (simple fetch)
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            responseMimeType: "application/json",
            responseSchema: {
              type: "ARRAY",
              items: {
                type: "OBJECT",
                properties: {
                  activity: { type: "STRING" },
                  icon: { type: "STRING" },
                  reason: { type: "STRING" }
                }
              }
            }
          }
        })
      }
    );
    
    const data = await response.json();
    const suggestions = JSON.parse(data.candidates[0].content.parts[0].text);
    
    return suggestions.slice(0, 3); // Limitar a 3
    
  } catch (error) {
    console.error("Gemini API Error:", error);
    // Fallback a sugerencia genérica
    return [
      { activity: "Indoor activity", icon: "🏠", reason: "Weather conditions not ideal" }
    ];
  }
}
```

### **Implementación en Frontend**

```jsx
// En WeatherResults.jsx

function WeatherResults({ data }) {
  const [planB, setPlanB] = useState(null);
  
  useEffect(() => {
    const riskLevels = {
      temperature: data.temperature_risk.risk_level,
      precipitation: data.precipitation_risk.risk_level,
      humidity: data.humidity_risk.risk_level
    };
    
    // Solo generar Plan B si hay riesgo MODERATE o HIGH
    const hasHighRisk = Object.values(riskLevels).some(
      level => level === "HIGH" || level === "MODERATE"
    );
    
    if (hasHighRisk) {
      const suggestions = generateSimplePlanB(riskLevels, data.activity);
      setPlanB(suggestions);
    }
  }, [data]);
  
  return (
    <div>
      {/* Mostrar análisis de riesgo */}
      {/* ... */}
      
      {/* Mostrar Plan B si existe */}
      {planB && (
        <div className="plan-b-section">
          <h3>🔄 Plan B - Alternative Suggestions</h3>
          <p>Based on detected weather risks, consider these alternatives:</p>
          {planB.map((suggestion, index) => (
            <div key={index} className="plan-b-card">
              <span className="icon">{suggestion.icon}</span>
              <h4>{suggestion.activity}</h4>
              <p>{suggestion.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### **Ventajas del Plan B con Gemini AI**

| Aspecto | Ventaja |
|---------|---------|
| **Inteligencia** | Sugerencias personalizadas y contextuales |
| **Adaptabilidad** | Se ajusta a cualquier combinación de riesgos |
| **Simplicidad Técnica** | Solo 1 API call, ~30 líneas de código |
| **Velocidad** | Respuesta en 2-3 segundos (aceptable para UX) |
| **Costo** | ~$0.001 por request (muy económico) |
| **Fallback** | Sugerencia genérica si falla API |
| **Valor Educativo** | Demuestra integración de IA en el proyecto |

### **Complejidad de Implementación**

| Componente | Complejidad | Esfuerzo |
|------------|-------------|----------|
| **API Key Setup** | Baja | 5 minutos (obtener key en Google AI Studio) |
| **Frontend Code** | Baja | ~30 líneas JavaScript |
| **Error Handling** | Baja | Try-catch con fallback |
| **Testing** | Media | Validar respuestas JSON |
| **Total** | **BAJA** | **1-2 horas** |

### **¿Por Qué NO es Complejo?**

✅ **No requiere backend**: Llamada directa desde frontend  
✅ **No requiere entrenamiento**: Modelo pre-entrenado  
✅ **No requiere infraestructura**: Solo una API key  
✅ **JSON Schema**: Gemini devuelve JSON estructurado automáticamente  
✅ **Fallback simple**: Si falla, muestra sugerencia genérica

---

## 📊 Estructura de Datos - 3 Variables

### **Datos INUMET (Entrada)**
```csv
datetime,fecha_simple,hora,estacion,temperatura,precipitacion,humedad
2020-01-01 00:00:00,2020-01-01,00:00,Aeropuerto Melilla G3,21.3,0.2,75
2020-01-01 01:00:00,2020-01-01,01:00,Aeropuerto Melilla G3,21.1,0.0,76
...
```

### **Agregación Diaria (Procesamiento)**
```python
# logic.py

def aggregate_daily(hourly_data):
    daily = hourly_data.groupby(hourly_data['datetime'].dt.date).agg({
        'temperatura': 'max',      # Temperatura máxima del día
        'precipitacion': 'sum',     # Precipitación acumulada
        'humedad': 'mean'           # Humedad promedio
    }).reset_index()
    return daily
```

### **Cálculo P90 (3 Variables)**
```python
# logic.py

def calculate_p90_multi_variable(monthly_data):
    p90_temp = np.percentile(monthly_data['temperatura'], 90)
    p90_precip = np.percentile(monthly_data['precipitacion'], 90)
    p90_humidity = np.percentile(monthly_data['humedad'], 90)
    
    return {
        'temperature': {
            'p90_threshold': p90_temp,
            'probability': calculate_probability(monthly_data['temperatura'], p90_temp),
            'risk_level': assign_risk_level(probability)
        },
        'precipitation': {
            'p90_threshold': p90_precip,
            'probability': calculate_probability(monthly_data['precipitacion'], p90_precip),
            'risk_level': assign_risk_level(probability)
        },
        'humidity': {
            'p90_threshold': p90_humidity,
            'probability': calculate_probability(monthly_data['humedad'], p90_humidity),
            'risk_level': assign_risk_level(probability)
        }
    }
```

### **Respuesta API (Output)**
```json
{
  "temperature_risk": {
    "probability": 25.5,
    "risk_threshold": 31.2,
    "status_message": "🚨 HIGH RISK of extreme heat",
    "risk_level": "HIGH"
  },
  "precipitation_risk": {
    "probability": 8.3,
    "risk_threshold": 45.1,
    "status_message": "☁️ LOW RISK of significant rain",
    "risk_level": "LOW"
  },
  "humidity_risk": {
    "probability": 15.7,
    "risk_threshold": 82.5,
    "status_message": "⚠️ MODERATE RISK of high humidity",
    "risk_level": "MODERATE"
  }
}
```

---

---

## 🔑 Guía Rápida: Configuración Gemini API (5 minutos)

### **Paso 1: Obtener API Key**
1. Ir a: https://aistudio.google.com/apikey
2. Iniciar sesión con cuenta Google
3. Hacer clic en "Create API Key"
4. Copiar la key generada

### **Paso 2: Configurar en el Proyecto**
```bash
# En la carpeta frontend/
touch .env

# Añadir al archivo .env:
REACT_APP_GEMINI_API_KEY=tu_api_key_aqui
```

### **Paso 3: Usar en el Código**
```javascript
// frontend/src/components/WeatherResults.jsx
const GEMINI_API_KEY = process.env.REACT_APP_GEMINI_API_KEY;

// Ya puedes usar la API
const response = await fetch(
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_API_KEY}`,
  { /* ... */ }
);
```

### **Paso 4: Gitignore**
```bash
# Añadir al .gitignore
frontend/.env
*.env
```

### **¡Listo!** ✅
Total: 5 minutos de configuración, ~30 líneas de código.

---

## 📊 Resumen Final del Backlog

### **Total de Tareas: 23**

| Sección | Tareas | Prioridad | Complejidad |
|---------|--------|-----------|-------------|
| **1. Núcleo Científico** | 6 | 🔥 Crítica | Media-Alta |
| **2. Visualización + IA** | 10 | 🟡 Importante | Media-Alta |
| **3. Documentación** | 7 | 🟡 Importante | Media-Alta |
| **4. Visión Futura** | 7+ | 🔮 Baja | - |

### **Enfoque del Reto:**
✅ **3 Variables Climáticas**: Temp, Precip, Humedad  
✅ **P90 con Datos Reales**: 60K+ registros INUMET  
✅ **3 Visualizaciones Plotly**: Interactivas con línea P90  
✅ **Plan B con Gemini AI**: Sugerencias inteligentes (~30 líneas)  
✅ **Docker + Documentación**: Listo para defensa  

---

**¡Backlog actualizado con 3 variables, 3 gráficos Plotly y Plan B con Gemini AI!** ✅🚀🤖
