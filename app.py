import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN DE BASE DE DATOS ---
conn = sqlite3.connect('mi_jardin.db', check_same_thread=False)
c = conn.cursor()

# Crear tablas si no existen
c.execute('''CREATE TABLE IF NOT EXISTS especies (id INTEGER PRIMARY KEY, nombre TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS plantas (id INTEGER PRIMARY KEY, apodo TEXT, especie_id INTEGER, ubicacion TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS historial (id INTEGER PRIMARY KEY, planta_id INTEGER, fecha TEXT, accion TEXT)''')
conn.commit()

# --- INTERFAZ ---
st.title("🌿 Mi Jardín en la Nube")

menu = ["Inicio", "Registrar Planta", "Panel de Control", "Cámara de Seguimiento"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

if choice == "Inicio":
    st.subheader("Bienvenido a tu bitácora de cultivo")
    st.write("Gestiona tus ejemplares y haz un seguimiento visual de su crecimiento.")

elif choice == "Registrar Planta":
    st.header("🌱 Nueva Planta")
    
    # Primero: Crear especies (si la tabla está vacía)
    with st.expander("Añadir Nueva Especie (Ej: Bonsái, Carnívora)"):
        nueva_esp = st.text_input("Nombre de la Especie")
        if st.button("Guardar Especie"):
            c.execute("INSERT INTO especies (nombre) VALUES (?)", (nueva_esp,))
            conn.commit()
            st.success("Especie guardada")

    # Segundo: Registrar la planta
    st.subheader("Datos de la planta")
    esp_df = pd.read_sql("SELECT * FROM especies", conn)
    
    if not esp_df.empty:
        with st.form("form_nueva_planta"):
            apodo = st.text_input("Apodo (Ej: El Olmo del patio)")
            ubi = st.selectbox("Ubicación", ["Interior", "Exterior", "Invernadero"])
            esp_id = st.selectbox("Especie", esp_df['id'], format_func=lambda x: esp_df[esp_df['id']==x]['nombre'].values[0])
            
            if st.form_submit_button("Añadir a Colección"):
                c.execute("INSERT INTO plantas (apodo, especie_id, ubicacion) VALUES (?, ?, ?)", (apodo, esp_id, ubi))
                conn.commit()
                st.success(f"¡{apodo} registrada!")
                st.rerun()
    else:
        st.warning("Primero registra una especie arriba.")

elif choice == "Panel de Control":
    st.header("📋 Mi Colección")
    try:
        query = "SELECT p.id, p.apodo, e.nombre as especie, p.ubicacion FROM plantas p JOIN especies e ON p.especie_id = e.id"
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Opción para borrar
            st.divider()
            id_borrar = st.number_input("ID de planta a eliminar", step=1, min_value=1)
            if st.button("Borrar Registro"):
                c.execute("DELETE FROM plantas WHERE id = ?", (id_borrar,))
                conn.commit()
                st.warning("Planta eliminada")
                st.rerun()
        else:
            st.info("No hay plantas aún.")
    except:
        st.error("Error al cargar datos. Asegúrate de haber registrado una especie primero.")

elif choice == "Cámara de Seguimiento":
    st.header("📸 Registro Visual")
    plantas_df = pd.read_sql("SELECT id, apodo FROM plantas", conn)
    
    if not plantas_df.empty:
        p_id = st.selectbox("¿A qué planta pertenece la foto?", plantas_df['id'], 
                            format_func=lambda x: plantas_df[plantas_df['id']==x]['apodo'].values[0])
        
        # Subidor de archivos (funciona con cámara o galería en el celu)
        foto = st.file_uploader("Elegir foto o sacar con la cámara", type=['png', 'jpg', 'jpeg'])
        
        if foto:
            st.image(foto, caption="Vista previa")
            if st.button("Guardar en Historial"):
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute("INSERT INTO historial (planta_id, fecha, accion) VALUES (?, ?, ?)", (p_id, fecha, "Foto registrada"))
                conn.commit()
                st.success("¡Foto vinculada al historial!")
    else:
        st.warning("Primero registra una planta.")
