import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ELITE (CSS AVANZADO)
st.set_page_config(page_title="GPS STEWARD Elite Analytics", layout="wide")

st.markdown("""
    <style>
    /* Fondo total de la aplicación (Negro profundo mate) */
    .stApp {
        background-color: #0D1527 !important;
        color: #0D1527 !important;
    }
    
    /* Títulos principales estilo deportivo (Verde Neón) */
    h1, h2, h3 {
        color: #00FF87 !important;
        font-family: 'Impact', 'Arial Black', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Contenedor del cargador de archivos con borde brillante */
    .stFileUploader {
        background-color: #0D0D0D !important;
        border: 2px dashed #00FF87 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Personalización total de las tarjetas de métricas (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #0D0D0D !important;
        border: 1px solid #1A3A2A !important;
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0px 4px 15px rgba(0, 255, 135, 0.05) !important;
    }
    
    /* Números de los KPIs en Dorado de Campeonato */
    div[data-testid="stMetricValue"] > div {
        color: #FFD700 !important;
        font-family: 'Arial Black', sans-serif !important;
        font-size: 32px !important;
    }
    
    /* Etiquetas de los KPIs en Blanco Limpio */
    div[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Ajuste de la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0D1527 !important;
        border-right: 1px solid #111111 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ GPS Performance - Steward PF")
st.write("Panel de control optimizado para la monitorización de cargas y altas intensidades.")
st.markdown("---")

# 2. CARGADOR DE ARCHIVOS AUTOMATIZADO
archivo_subido = st.file_uploader("📂 Arrastra aquí el reporte de la sesión (Excel/CSV)", type=["xlsx", "xls", "csv"])

if archivo_subido is not None:
    try:
        if archivo_subido.name.endswith('.csv'):
            datos = pd.read_csv(archivo_subido, encoding='latin1', sep=None, engine='python')
        else:
            datos = pd.read_excel(archivo_subido)
            
        st.success("🔥 Datos de plantel sincronizados correctamente.")
        
        # 3. LIMPIEZA MASIVA DE MÉTRICAS
        metricas_clave = [
            'PLAYER LOAD (UA)', 'DISTANCIA (m)', 'M/MIN', 
            'ACELERACIONES', 'DESACELERACIONES', 'Max Vel (km/h)', 'HSR'
        ]
        
        for metrica in metricas_clave:
            if metrica in datos.columns:
                datos[metrica] = pd.to_numeric(datos[metrica], errors='coerce')
        
        # 4. FILTROS EN LA BARRA LATERAL (STYLISH SIDEBAR)
        st.sidebar.markdown("### 🕹️ Centro de Mando")
        metricas_disponibles = [m for m in metricas_clave if m in datos.columns]
        metrica_seleccionada = st.sidebar.selectbox("Métrica Activa:", metricas_disponibles)
        
        if 'POSICIÓN' in datos.columns:
            posiciones = ["TODAS LAS POSICIONES"] + list(datos['POSICIÓN'].dropna().unique())
            posicion_elegida = st.sidebar.selectbox("Filtrar Plantel:", posiciones)
            if posicion_elegida != "TODAS LAS POSICIONES":
                datos = datos[datos['POSICIÓN'] == posicion_elegida]

        # 5. PROCESAMIENTO DE RENDIMIENTO
        reporte_equipo = datos.groupby('JUGADOR')[metricas_disponibles].mean().reset_index()
        
        if 'Max Vel (km/h)' in datos.columns:
            max_vel = datos.groupby('JUGADOR')['Max Vel (km/h)'].max().reset_index()
            reporte_equipo['Max Vel (km/h)'] = max_vel['Max Vel (km/h)']
            
        reporte_equipo = reporte_equipo.round(1).sort_values(by=metrica_seleccionada, ascending=False)

        # 6. GRÁFICA DE ALTO IMPACTO VISUAL
        fig = go.Figure(go.Bar(
            x=reporte_equipo['JUGADOR'],
            y=reporte_equipo[metrica_seleccionada],
            marker=dict(
                color='#00FF87',  # Verde Neón brillante
                line=dict(color='#00AA5B', width=1.5)  # Borde sutil para dar volumen
            ),
            text=reporte_equipo[metrica_seleccionada],
            textposition='outside',
            textfont=dict(color='#FFD700', size=13, family='Arial Black'),
            hovertemplate="<b>%{x}</b><br>Valor: %{y}<extra></extra>"
        ))
        
        fig.update_layout(
            title=f"RANKING ACTUAL: {metrica_seleccionada}",
            title_font=dict(color='#00FF87', size=18, family='Arial Black'),
            plot_bgcolor='#0D0D0D',  # Fondo interno gris oscuro deportivo
            paper_bgcolor='#050505', # Fondo exterior negro puro
            font=dict(color='#FFFFFF'),
            xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=12, color='#FFFFFF')),
            yaxis=dict(showgrid=True, gridcolor='#1A1A1A', tickfont=dict(color='#A0A0A0')),
            margin=dict(t=60, b=80),
            hoverlabel=dict(bgcolor='#0D0D0D', font_size=13, font_family='Arial')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        
        # 7. SECCIÓN DE DESTACADOS (MEDALLERO DE LA SESIÓN)
        st.subheader("🏆 Cuadro de Honor de la Jornada")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_load = reporte_equipo.sort_values(by='PLAYER LOAD (UA)', ascending=False).iloc[0] if 'PLAYER LOAD (UA)' in reporte_equipo.columns else None
            if top_load is not None:
                st.metric(label="🔥 Máximo Desgaste (Player Load)", value=f"{top_load['PLAYER LOAD (UA)']} UA", delta=f"🏃‍♂️ {top_load['JUGADOR']}", delta_color="normal")
        
        with col2:
            top_dist = reporte_equipo.sort_values(by='DISTANCIA (m)', ascending=False).iloc[0] if 'DISTANCIA (m)' in reporte_equipo.columns else None
            if top_dist is not None:
                st.metric(label="🏃‍♂️ Kilometraje Mayor", value=f"{top_dist['DISTANCIA (m)']} m", delta=f"🏃‍♂️ {top_dist['JUGADOR']}", delta_color="normal")
                
        with col3:
            top_vel_player = reporte_equipo.sort_values(by='Max Vel (km/h)', ascending=False).iloc[0] if 'Max Vel (km/h)' in reporte_equipo.columns else None
            if top_vel_player is not None:
                st.metric(label="⚡ Velocidad Pico (Récord)", value=f"{top_vel_player['Max Vel (km/h)']} km/h", delta=f"🏃‍♂️ {top_vel_player['JUGADOR']}", delta_color="normal")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("💡 Esperando que subas el archivo de Excel para desplegar el centro de mando...")
