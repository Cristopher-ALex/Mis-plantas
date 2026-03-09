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
if choice == "Panel de Control":
    st.header("📋 Estado de mi Colección")
    
    # Traemos los datos actuales
    query = '''
        SELECT p.id, p.apodo, e.nombre as especie, p.ubicacion 
        FROM plantas p JOIN especies e ON p.especie_id = e.id
    '''
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        st.subheader("🗑️ Eliminar o Editar")
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector para elegir qué planta borrar
            id_a_borrar = st.selectbox("Selecciona la planta que quieres eliminar:", 
                                        df['id'], 
                                        format_func=lambda x: df[df['id']==x]['apodo'].values[0])
        
        with col2:
            st.write("---") # Espacio visual
            # Botón de confirmación para evitar borrados por error
            if st.button("Confirmar: Eliminar Planta"):
                try:
                    c.execute("DELETE FROM plantas WHERE id = ?", (id_a_borrar,))
                    conn.commit()
                    st.warning(f"Registro {id_a_borrar} eliminado. La página se recargará.")
                    st.rerun() # Esto refresca la app para que ya no aparezca
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
    else:
        st.info("No hay registros para mostrar.")

# --- SECCIÓN 2: REGISTRO ---
elif choice == "Registrar Planta/Especie":
    st.header("📝 Alta de Ejemplares")
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("1. Nueva Especie")
        nom_e = st.text_input("Nombre (ej: Venus Atrapamoscas)")
        agua_e = st.selectbox("Tipo de Agua", ["Destilada", "Lluvia", "Grifo"])
        freq_e = st.number_input("Riego cada (días)", min_value=1, value=3)
        if st.button("Guardar Especie"):
            c.execute("INSERT INTO especies (nombre, agua, frecuencia) VALUES (?,?,?)", (nom_e, agua_e, freq_e))
            conn.commit()
            st.success("Especie creada.")

    with colB:
        st.subheader("2. Nueva Planta")
        esp_df = pd.read_sql("SELECT id, nombre FROM especies", conn)
        if not esp_df.empty:
            apodo_p = st.text_input("Apodo (ej: La Cazadora)")
            esp_p = st.selectbox("Especie", esp_df['id'], format_func=lambda x: esp_df[esp_df['id']==x]['nombre'].values[0])
            salud_p = st.slider("Salud inicial", 1, 5, 5)
            ubic_p = st.text_input("Ubicación (ej: Invernadero)")
            if st.button("Añadir a Colección"):
                c.execute("INSERT INTO plantas (apodo, especie_id, salud, ubicacion) VALUES (?,?,?,?)", 
                          (apodo_p, esp_p, salud_p, ubic_p))
                conn.commit()
                st.balloons()
        else:
            st.warning("Primero debes crear una Especie.")

# --- SECCIÓN 3: CÁMARA ---
elif choice == "Cámara de Seguimiento":
    st.header("📸 Registro Visual")
    plantas_df = pd.read_sql("SELECT id, apodo FROM plantas", conn)
    if not plantas_df.empty:
        p_id = st.selectbox("¿A qué planta le tomas la foto?", plantas_df['id'], format_func=lambda x: plantas_df[plantas_df['id']==x]['apodo'].values[0])
        foto = st.camera_input("Capturar progreso de mi planta")
        if foto:
            st.image(foto)
            st.success("Foto capturada. (Para guardarla permanentemente en disco requiere configuración de archivos adicional).")
    else:
        st.warning("No hay plantas registradas.")

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

