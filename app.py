import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DE BASE DE DATOS ---
conn = sqlite3.connect('mi_jardin_v2.db', check_same_thread=False)
c = conn.cursor()

# Tablas actualizadas con nuevos campos para riego, sustrato y notas
c.execute('''CREATE TABLE IF NOT EXISTS especies 
             (id INTEGER PRIMARY KEY, nombre TEXT, categoria TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS plantas 
             (id INTEGER PRIMARY KEY, apodo TEXT, especie_id INTEGER, 
              ubicacion TEXT, riego TEXT, sustrato TEXT, notas TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS historial 
             (id INTEGER PRIMARY KEY, planta_id INTEGER, fecha TEXT, accion TEXT)''')
conn.commit()

# Insertar categorías base si la tabla está vacía
categorias_base = ["Flores", "Plantas de Interior", "Plantas de Exterior", "Árboles", "Bonsái", "Carnívoras"]

# --- INTERFAZ ---
st.set_page_config(page_title="Mi Jardín Pro", layout="wide")
st.title("🌿 Gestión Botánica Personalizada")

# --- SECCIÓN DE CLIMA ---
try:
    url_clima = "https://wttr.in/Comodoro+Rivadavia?format=%c+%t+%w"
    res = requests.get(url_clima, timeout=5)
    if res.status_code == 200:
        st.info(f"📍 Clima en Comodoro: {res.text}")
except:
    st.write("🌤️ Clima no disponible temporalmente")

# --- MENÚ LATERAL ---
menu = ["Inicio", "Registrar Nueva", "Panel de Control", "Fichas Detalladas", "Cámara/Fotos"]
choice = st.sidebar.selectbox("Seleccionar Sección", menu)

if choice == "Inicio":
    st.subheader("Bienvenido a tu Bitácora")
    st.write("Organiza tus especies por categorías y lleva un registro técnico de cada una.")
    st.image("https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?q=80&w=1000", caption="Jardinería Digital")

elif choice == "Registrar Nueva":
    st.header("📝 Alta de Planta")
    
    # 1. Gestión de Especies y Categorías
    with st.expander("1. Configurar Categoría y Especie"):
        cat_sel = st.selectbox("Elegir Grupo", categorias_base)
        nombre_especie = st.text_input("Nombre específico (Ej: Rosa, Potus, Pino)")
        if st.button("Registrar Categoría/Especie"):
            c.execute("INSERT INTO especies (nombre, categoria) VALUES (?, ?)", (nombre_especie, cat_sel))
            conn.commit()
            st.success(f"Registrada: {nombre_especie} en {cat_sel}")

    # 2. Registro de la Planta individual
    st.divider()
    esp_df = pd.read_sql("SELECT id, nombre, categoria FROM especies", conn)
    if not esp_df.empty:
        with st.form("form_alta"):
            st.subheader("2. Datos de la Planta")
            apodo = st.text_input("Apodo (Ej: La del living)")
            esp_id = st.selectbox("Especie/Grupo", esp_df['id'], 
                                  format_func=lambda x: f"{esp_df[esp_df['id']==x]['categoria'].values[0]} - {esp_df[esp_df['id']==x]['nombre'].values[0]}")
            ubi = st.selectbox("Ubicación Real", ["Interior", "Exterior", "Invernadero", "Balcón"])
            riego = st.text_input("Frecuencia de Riego")
            sustrato = st.text_input("Tipo de Sustrato")
            notas = st.text_area("Notas adicionales")
            
            if st.form_submit_button("Guardar en mi Jardín"):
                c.execute("INSERT INTO plantas (apodo, especie_id, ubicacion, riego, sustrato, notas) VALUES (?,?,?,?,?,?)",
                          (apodo, esp_id, ubi, riego, sustrato, notas))
                conn.commit()
                st.success(f"¡{apodo} añadida con éxito!")
    else:
        st.warning("Primero debes configurar una categoría y especie arriba.")

elif choice == "Panel de Control":
    st.header("📋 Inventario General")
    query = '''SELECT p.id, p.apodo, e.categoria, e.nombre as especie, p.ubicacion 
               FROM plantas p JOIN especies e ON p.especie_id = e.id'''
    df = pd.read_sql(query, conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Eliminar Registro")
        id_del = st.number_input("ID a borrar", step=1, min_value=1)
        if st.button("Eliminar Planta"):
            c.execute("DELETE FROM plantas WHERE id = ?", (id_del,))
            conn.commit()
            st.rerun()
    else:
        st.info("No hay plantas registradas.")

elif choice == "Fichas Detalladas":
    st.header("📇 Ficha Técnica Individual")
    p_df = pd.read_sql("SELECT id, apodo FROM plantas", conn)
    if not p_df.empty:
        sel = st.selectbox("Elegir Planta", p_df['id'], format_func=lambda x: p_df[p_df['id']==x]['apodo'].values[0])
        
        info = pd.read_sql(f'''SELECT p.*, e.nombre as esp, e.categoria as cat 
                               FROM plantas p JOIN especies e ON p.especie_id = e.id 
                               WHERE p.id = {sel}''', conn).iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Categoría", info['cat'])
            st.write(f"**Especie:** {info['esp']}")
            st.write(f"**Ubicación:** {info['ubicacion']}")
            st.write(f"**Riego:** {info['riego']}")
        with col2:
            st.write(f"**Sustrato:** {info['sustrato']}")
            st.write(f"**Notas:** {info['notas']}")
            
        # Historial de fotos
        st.divider()
        st.subheader("🕒 Historial y Fotos")
        hist = pd.read_sql(f"SELECT fecha, accion FROM historial WHERE planta_id = {sel} ORDER BY fecha DESC", conn)
        if not hist.empty:
            st.table(hist)
        else:
            st.write("Sin fotos o eventos registrados aún.")
    else:
        st.warning("Registra una planta primero.")

elif choice == "Cámara/Fotos":
    st.header("📸 Subir Seguimiento")
    p_df = pd.read_sql("SELECT id, apodo FROM plantas", conn)
    if not p_df.empty:
        sel_id = st.selectbox("¿A qué planta le sacaste foto?", p_df['id'], format_func=lambda x: p_df[p_df['id']==x]['apodo'].values[0])
        archivo = st.file_uploader("Capturar o elegir archivo", type=['jpg', 'png', 'jpeg'])
        if archivo:
            st.image(archivo)
            if st.button("Vincular Foto al Historial"):
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute("INSERT INTO historial (planta_id, fecha, accion) VALUES (?, ?, ?)", (sel_id, fecha, "Foto subida"))
                conn.commit()
                st.success("Foto registrada en la bitácora.")

