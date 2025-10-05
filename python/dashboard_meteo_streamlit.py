import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Predicción Climática - Montevideo", layout="wide")
st.title("🌎 Predicción Climática Interactiva - Montevideo")

# -------------------------------
# 1️⃣ Cargar datos históricos
# -------------------------------
df = pd.read_csv("inumet_temp_prec.csv")
df['datetime'] = pd.to_datetime(df['fecha_simple'] + ' ' + df['hora'])

# -------------------------------
# 2️⃣ Mapear estación -> ciudad principal
# -------------------------------
estacion_a_ciudad = {
    "Aeropuerto Melilla G3": "Montevideo",
    "Artigas G3": "Artigas",
    "Colonia G3": "Colonia del Sacramento",
    "Mercedes G3": "Mercedes",
    "Paso de los Toros G3": "Paso de los Toros",
    "Rocha G3": "Rocha",
    "Salto G3": "Salto"
}
df['ciudad'] = df['estacion'].map(estacion_a_ciudad)

# -------------------------------
# 3️⃣ Filtrar solo Montevideo
# -------------------------------
if 'Montevideo' not in df['ciudad'].unique():
    st.error("⚠️ No hay datos suficientes para Montevideo.")
    st.stop()

ciudad_seleccionada = "Montevideo"
df_ciudad = df[df['ciudad'] == ciudad_seleccionada]

# Verificar si hay suficientes datos
if len(df_ciudad) < 30:
    st.warning("⚠️ No hay suficientes datos históricos para entrenar el modelo en esta ciudad.")
    st.stop()

# -------------------------------
# 4️⃣ Seleccionar estación con más datos
# -------------------------------
estacion_mejor = df_ciudad['estacion'].value_counts().idxmax()
df_estacion = df_ciudad[df_ciudad['estacion'] == estacion_mejor][['datetime','temperatura','precipitacion']].dropna()

# -------------------------------
# 5️⃣ Resample diario para Prophet
# -------------------------------
df_daily = df_estacion.set_index('datetime').resample('D').mean().reset_index()

# -------------------------------
# 6️⃣ Selección rango de predicción
# -------------------------------
max_days = 90
hoy = datetime.today().date()
rango_inicial = 7

start_date = st.date_input("Fecha inicio predicción", hoy)
default_end = start_date + timedelta(days=rango_inicial-1)
end_date = st.date_input("Fecha fin predicción", default_end)

if (end_date - start_date).days >= max_days:
    st.warning(f"El rango máximo es de {max_days} días. Se ajustará automáticamente.")
    end_date = start_date + timedelta(days=max_days-1)

# -------------------------------
# 7️⃣ Ajustar modelo con caché
# -------------------------------
@st.cache_data
def fit_model(df_prophet):
    modelo = Prophet(daily_seasonality=True)
    modelo.fit(df_prophet)
    return modelo

pronosticos = {}
with st.spinner('Generando predicción, por favor espera...'):
    for variable in ['temperatura','precipitacion']:
        df_prophet = pd.DataFrame({'ds': df_daily['datetime'], 'y': df_daily[variable]})
        modelo = fit_model(df_prophet)

        fechas_futuras = pd.date_range(start=start_date, end=end_date, freq='D')
        df_futuro = pd.DataFrame({'ds': fechas_futuras})
        pronostico = modelo.predict(df_futuro)
        pronosticos[variable] = pronostico[['ds','yhat']]

# -------------------------------
# 8️⃣ Resumen diario y rangos plausibles
# -------------------------------
df_temp = pronosticos['temperatura'].copy()
df_prec = pronosticos['precipitacion'].copy()
df_daily_pred = pd.merge(df_temp, df_prec, on='ds')
df_daily_pred.rename(columns={'ds':'fecha','yhat_x':'temp','yhat_y':'precip'}, inplace=True)
df_daily_pred['fecha'] = pd.to_datetime(df_daily_pred['fecha'])

df_daily_pred['temp_min'] = (df_daily_pred['temp'] - 2).clip(0, 45)
df_daily_pred['temp_max'] = (df_daily_pred['temp'] + 3).clip(0, 45)
df_daily_pred['temp'] = df_daily_pred['temp'].clip(0, 45)
df_daily_pred['precip'] = df_daily_pred['precip'].apply(lambda x: max(0, x))

# -------------------------------
# 🔹 Gráfico con iconos
# -------------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=pd.concat([df_daily_pred['fecha'], df_daily_pred['fecha'][::-1]]),
    y=pd.concat([df_daily_pred['temp_max'], df_daily_pred['temp_min'][::-1]]),
    fill='toself',
    fillcolor='rgba(255,140,0,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo='skip',
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=df_daily_pred['fecha'],
    y=df_daily_pred['temp_max'],
    mode='lines+markers',
    name='Temp. Máx',
    line=dict(color='orange', width=3),
    marker=dict(size=8)
))
fig.add_trace(go.Scatter(
    x=df_daily_pred['fecha'],
    y=df_daily_pred['temp_min'],
    mode='lines+markers',
    name='Temp. Mín',
    line=dict(color='red', width=3),
    marker=dict(size=8)
))

fig.add_trace(go.Bar(
    x=df_daily_pred['fecha'],
    y=df_daily_pred['precip'],
    name='Precipitación (mm)',
    marker_color='royalblue',
    yaxis='y2',
    opacity=0.6
))

for i, row in df_daily_pred.iterrows():
    if row['precip'] > 5:
        icon = "🌧️"
    elif row['temp'] > 28:
        icon = "☀️"
    elif row['temp'] > 20:
        icon = "⛅"
    else:
        icon = "❄️"
    fig.add_annotation(
        x=row['fecha'],
        y=row['temp_max'] + 1,
        text=icon,
        showarrow=False,
        font=dict(size=20)
    )

fig.update_layout(
    title=f"Pronóstico Diario — {ciudad_seleccionada} (Estación: {estacion_mejor})",
    xaxis_title="Fecha",
    yaxis=dict(title="Temperatura (°C)"),
    yaxis2=dict(title="Precipitación (mm)", overlaying='y', side='right'),
    barmode='overlay',
    template='plotly_dark',
    hovermode='x unified',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 🔹 Recomendaciones
# -------------------------------
temp_prom = df_daily_pred['temp'].mean()
lluvia_tot = df_daily_pred['precip'].sum()

st.subheader("🏖️ Recomendaciones según clima")
if temp_prom >= 25 and lluvia_tot < 100:
    st.write("Clima ideal para **playa y deportes acuáticos**.")
elif 20 <= temp_prom < 25 and lluvia_tot < 150:
    st.write("Buen clima para **turismo cultural y gastronómico**.")
elif temp_prom < 20 and lluvia_tot >= 50:
    st.write("Clima fresco/lluvioso, ideal para **excursiones de montaña, trekking y museos**.")
else:
    st.write("Clima mixto, se recomienda **actividades indoor y al aire libre**.")
