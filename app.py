import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Jardín Digital", page_icon="🌿", layout="wide")

# --- BASE DE DATOS (SQLite) ---
conn = sqlite3.connect('mi_jardin.db', check_same_thread=False)
c = conn.cursor()

# Crear tablas si no existen
c.execute('''CREATE TABLE IF NOT EXISTS especies 
             (id INTEGER PRIMARY KEY, nombre TEXT, agua TEXT, frecuencia INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS plantas 
             (id INTEGER PRIMARY KEY, apodo TEXT, especie_id INTEGER, salud INTEGER, ubicacion TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS historial 
             (id INTEGER PRIMARY KEY, planta_id INTEGER, fecha TEXT, accion TEXT)''')
conn.commit()

# --- FUNCIONES DE APOYO ---
def obtener_clima():
    # --- PEGA TU CLAVE AQUÍ ABAJO ---
    API_KEY_PERSONAL = "dd01e978a1371798766bc0ff1f0fa1b0" 
        # Coordenadas de Comodoro Rivadavia
    lat, lon = -45.8641, -67.4808 
    
    # URL configurada para Celsius, Km/h y Español
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY_PERSONAL}&units=metric&lang=es"
        try:
        res = requests.get(url, timeout=3).json()
        if res.get("cod") == 200:
            return {
                "temp": res['main']['temp'], 
                "viento": res['wind']['speed'] * 3.6, # Convertimos m/s a km/h
                "hum": res['main']['humidity'],
                "desc": res['weather'][0]['description'].capitalize()
            }
        else:
            return None
    except:
        return None
# --- BARRA LATERAL (CLIMA Y NAVEGACIÓN) ---
st.sidebar.title("🌿 Gestión Botánica")
clima = obtener_clima()
if clima:
    st.sidebar.metric("Temp en Comodoro", f"{clima['temp']}°C")
    viento = clima['viento']
    if viento > 50:
        st.sidebar.error(f"⚠️ VIENTO FUERTE: {viento:.1f} km/h")
    else:
        st.sidebar.info(f"🌬️ Viento: {viento:.1f} km/h")
menu = ["Panel de Control", "Registrar Planta/Especie", "Cámara de Seguimiento", "Biblioteca PDF"]
choice = st.sidebar.selectbox("Ir a:", menu)
# --- SECCIÓN 1: PANEL DE CONTROL (CON ELIMINACIÓN) ---
elif choice == "Panel de Control":
    st.header("📋 Mi Colección de Plantas")
    
    # Consultamos la base de datos
    query = '''
        SELECT p.id, p.apodo, e.nombre as especie, p.ubicacion 
        FROM plantas p 
        JOIN especies e ON p.especie_id = e.id
    '''
        try:
        df = pd.read_sql(query, conn)
               if not df.empty:
            # Mostramos una tabla linda
            st.dataframe(df, use_container_width=True)
                     # Un buscador rápido por si tienes muchas
            busqueda = st.text_input("🔍 Buscar planta por apodo")
            if busqueda:
                df = df[df['apodo'].str.contains(busqueda, case=False)]
                st.write(df)
        else:
            st.info("Aún no tienes plantas registradas. ¡Ve a 'Registrar Planta' para empezar!")
                except Exception as e:
        st.error(f"Hubo un problema al cargar los datos: {e}")
st.divider()
    st.subheader("pulse 📖 Ver historial de una planta")
        if not df.empty:
        planta_sel = st.selectbox("Selecciona para ver historial:", df['apodo'].unique())
        
        # Buscamos el ID de esa planta
        p_id_query = f"SELECT id FROM plantas WHERE apodo = '{planta_sel}'"
        p_id = pd.read_sql(p_id_query, conn).iloc[0]['id']
                # Traemos su historial
        historial_df = pd.read_sql(f"SELECT fecha, accion FROM historial WHERE planta_id = {p_id} ORDER BY fecha DESC", conn)
        
        if not historial_df.empty:
            for index, row in historial_df.iterrows():
                st.write(f"**{row['fecha']}**: {row['accion']}")
        else:
            st.write("No hay eventos registrados para esta planta.")

# --- SECCIÓN 2: REGISTRO ---
elif choice == "Registrar Planta":
        st.header("🌱 Nueva Planta en la Colección")
        with st.form("form_planta"):
            apodo = st.text_input("Apodo de la planta (Ej: Mi Bonsái)")
            ubicacion = st.selectbox("Ubicación", ["Interior", "Exterior", "Invernadero"])
            # Traemos las especies para el selector
            esp_df = pd.read_sql("SELECT id, nombre FROM especies", conn)
            esp_id = st.selectbox("Especie", esp_df['id'], format_func=lambda x: esp_df[esp_df['id']==x]['nombre'].values[0])
            
            if st.form_submit_button("Añadir a Colección"):
                c.execute("INSERT INTO plantas (apodo, especie_id, ubicacion) VALUES (?, ?, ?)", 
                          (apodo, esp_id, ubicacion))
                conn.commit()
                st.success(f"¡{apodo} registrada con éxito!")

    elif choice == "Panel de Control":
        st.header("📋 Mi Colección")
        try:
            query = "SELECT p.id, p.apodo, e.nombre as especie, p.ubicacion FROM plantas p JOIN especies e ON p.especie_id = e.id"
            df = pd.read_sql(query, conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay plantas aún.")
        except Exception as e:
            st.error(f"Error de base de datos: {e}")
# --- SECCIÓN 4: BIBLIOTECA PDF ---
elif choice == "Biblioteca PDF":
    st.header("📚 Mis Manuales Técnicos")
    if not os.path.exists("biblioteca"):
        os.makedirs("biblioteca")
    
    archivo = st.file_uploader("Subir PDF de Bonsái/Carnívoras/Conservas", type="pdf")
    if archivo:
        with open(os.path.join("biblioteca", archivo.name), "wb") as f:
            f.write(archivo.getbuffer())
        st.success("Libro guardado.")

    libros = [f for f in os.listdir("biblioteca") if f.endswith(".pdf")]
    if libros:
        sel_pdf = st.selectbox("Leer manual:", libros)
        with open(os.path.join("biblioteca", sel_pdf), "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_viewer = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf">'

        st.markdown(pdf_viewer, unsafe_allow_html=True)






