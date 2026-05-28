import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="GPS Performance Dashboard", layout="wide")

# Inyección de CSS para mantener la estética (Fondo negro y textos dorados)
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFD700; }
    h1, h2, h3 { color: #2ecc71 !important; font-family: 'Arial Black'; }
    .stDataFrame { background-color: #111111; }
    .css-10trblm { color: #FFD700 !important; }
    /* Estilo para el cargador de archivos */
    .stFileUploader { background-color: #111111; border: 1px solid #2ecc71; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ Centro de Mando GPS - Temporada 2026")
st.write("Sube el archivo de la sesión para actualizar automáticamente todo el análisis del plantel.")

# 2. CARGADOR DE ARCHIVOS AUTOMATIZADO
archivo_subido = st.file_uploader("📂 Arrastra aquí tu archivo de Excel de los GPS", type=["xlsx", "xls", "csv"])

if archivo_subido is not None:
    try:
        # Detectar automáticamente si es Excel o CSV
        if archivo_subido.name.endswith('.csv'):
            datos = pd.read_csv(archivo_subido, encoding='latin1', sep=None, engine='python')
        else:
            datos = pd.read_excel(archivo_subido)
            
        st.success("¡Archivo procesado con éxito!")
        
        # 3. LIMPIEZA MASIVA DE MÉTRICAS
        metricas_clave = [
            'PLAYER LOAD (UA)', 'DISTANCIA (m)', 'M/MIN', 
            'ACELERACIONES', 'DESACELERACIONES', 'Max Vel (km/h)', 'HSR'
        ]
        
        for metrica in metricas_clave:
            if metrica in datos.columns:
                datos[metrica] = pd.to_numeric(datos[metrica], errors='coerce')
        
        # 4. FILTROS INTERACTIVOS EN LA BARRA LATERAL
        st.sidebar.header("🕹️ Panel de Control")
        
        # Filtro 1: Elegir la Métrica Principal
        metricas_disponibles = [m for m in metricas_clave if m in datos.columns]
        metrica_seleccionada = st.sidebar.selectbox("Selecciona la métrica a visualizar:", metricas_disponibles)
        
        # Filtro 2: Seleccionar posiciones si existen en tu tabla
        if 'POSICIÓN' in datos.columns:
            posiciones = ["TODAS"] + list(datos['POSICIÓN'].dropna().unique())
            posicion_elegida = st.sidebar.selectbox("Filtrar por Posición:", posiciones)
            if posicion_elegida != "TODAS":
                datos = datos[datos['POSICIÓN'] == posicion_elegida]

        # 5. PROCESAMIENTO DE REPORTES
        reporte_equipo = datos.groupby('JUGADOR')[metricas_disponibles].mean().reset_index()
        
        # Si la métrica es velocidad, usamos el máximo en vez del promedio
        if 'Max Vel (km/h)' in datos.columns:
            max_vel = datos.groupby('JUGADOR')['Max Vel (km/h)'].max().reset_index()
            reporte_equipo['Max Vel (km/h)'] = max_vel['Max Vel (km/h)']
            
        reporte_equipo = reporte_equipo.round(1).sort_values(by=metrica_seleccionada, ascending=False)

        # 6. DISEÑO DE LA GRÁFICA PRINCIPAL
        fig = go.Figure(go.Bar(
            x=reporte_equipo['JUGADOR'],
            y=reporte_equipo[metrica_seleccionada],
            marker_color='#2ecc71',
            text=reporte_equipo[metrica_seleccionada],
            textposition='outside',
            textfont=dict(color='#FFD700', size=12, family='Arial Black')
        ))
        
        fig.update_layout(
            title=f"Ranking del Equipo: {metrica_seleccionada}",
            title_font=dict(color='#2ecc71', size=20, family='Arial Black'),
            plot_bgcolor='#111111',
            paper_bgcolor='#000000',
            font=dict(color='#FFD700'),
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor='#222222'),
            margin=dict(t=50, b=50)
        )
        
        # Mostrar gráfica en la App
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. SECCIÓN DE DESTACADOS (KPIs)
        st.subheader("🏆 Destacados de la Sesión")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_load = reporte_equipo.sort_values(by='PLAYER LOAD (UA)', ascending=False).iloc[0] if 'PLAYER LOAD (UA)' in reporte_equipo.columns else None
            if top_load is not None:
                st.metric(label="🔥 Mayor Desgaste (Player Load)", value=f"{top_load['PLAYER LOAD (UA)']} UA", delta=top_load['JUGADOR'], delta_color="inverse")
        
        with col2:
            top_dist = reporte_equipo.sort_values(by='DISTANCIA (m)', ascending=False).iloc[0] if 'DISTANCIA (m)' in reporte_equipo.columns else None
            if top_dist is not None:
                st.metric(label="🏃‍♂️ Mayor Distancia Recorrida", value=f"{top_dist['DISTANCIA (m)']} m", delta=top_dist['JUGADOR'], delta_color="inverse")
                
        with col3:
            top_vel_player = reporte_equipo.sort_values(by='Max Vel (km/h)', ascending=False).iloc[0] if 'Max Vel (km/h)' in reporte_equipo.columns else None
            if top_vel_player is not None:
                st.metric(label="⚡ Velocidad Pico", value=f"{top_vel_player['Max Vel (km/h)']} km/h", delta=top_vel_player['JUGADOR'], delta_color="inverse")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("💡 Esperando que subas el archivo de Excel para desplegar el centro de mando...")