import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Jardín Permanente", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Esta conexión buscará tus credenciales en los "Secrets" de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE LECTURA MEJORADA ---
def leer_datos():
    try:
        # Forzamos la lectura de la hoja "plantas"
        return conn.read(worksheet="plantas", ttl=0)
    except Exception as e:
        # Si la planilla está vacía o no se encuentra, creamos un DF básico
        return pd.DataFrame(columns=["id", "apodo", "categoria", "especie", "ubicacion", "riego", "sustrato", "notas"])

# --- SECCIÓN REGISTRAR NUEVA ---
elif choice == "Registrar Nueva":
    st.header("📝 Alta de Planta")
    
    # Movimos la lectura de datos adentro de un try para que no bloquee la app
    try:
        df_existente = leer_datos()
    except:
        df_existente = pd.DataFrame(columns=["id", "apodo", "categoria", "especie", "ubicacion", "riego", "sustrato", "notas"])

    with st.form("form_alta", clear_on_submit=True):
        apodo = st.text_input("Apodo de la planta")
        cat = st.selectbox("Categoría", ["Cactus", "Flores", "Plantas de Interior", "Plantas de Exterior", "Árboles", "Bonsái", "Carnívoras"])
        esp = st.text_input("Especie")
        ubi = st.selectbox("Ubicación", ["Interior", "Exterior", "Invernadero", "Balcón"])
        riego = st.text_input("Frecuencia de Riego")
        sust = st.text_input("Sustrato")
        notas = st.text_area("Notas")
        
        if st.form_submit_button("Guardar en Google Sheets"):
            if apodo and esp:
                try:
                    # Crear nueva fila con datos limpios
                    nueva_fila = {
                        "id": int(len(df_existente) + 1),
                        "apodo": str(apodo),
                        "categoria": str(cat),
                        "especie": str(esp),
                        "ubicacion": str(ubi),
                        "riego": str(riego),
                        "sustrato": str(sust),
                        "notas": str(notas)
                    }
                    
                    # Agregar a los datos actuales
                    df_actualizado = pd.concat([df_existente, pd.DataFrame([nueva_fila])], ignore_index=True)
                    
                    # Subir a Google
                    conn.update(worksheet="plantas", data=df_actualizado)
                    st.success(f"¡{apodo} guardada con éxito!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error técnico al guardar: {e}")
            else:
                st.error("Por favor, completá Apodo y Especie.")

# --- INTERFAZ Y CLIMA ---
st.title("🌿 Gestión Botánica Permanente")

try:
    url_clima = "https://wttr.in/Comodoro+Rivadavia?format=%c+%t+%w"
    res = requests.get(url_clima, timeout=5)
    if res.status_code == 200:
        st.info(f"📍 Clima en Comodoro: {res.text}")
except:
    st.write("🌤️ Clima no disponible")

# --- MENÚ ---
menu = ["Inicio", "Registrar Nueva", "Panel de Control", "Fichas Detalladas"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Inicio":
    st.subheader("Bienvenido a tu base de datos en Google Sheets")
    st.write("Todos los cambios que hagas aquí se reflejarán en tu planilla de Drive automáticamente.")

elif choice == "Registrar Nueva":
    st.header("📝 Alta de Planta")
    df_existente = leer_datos()
    
    with st.form("form_alta"):
        apodo = st.text_input("Apodo de la planta")
        cat = st.selectbox("Categoría", ["Cactus", "Flores", "Plantas de Interior", "Plantas de Exterior", "Árboles", "Bonsái", "Carnívoras"])
        esp = st.text_input("Especie")
        ubi = st.selectbox("Ubicación", ["Interior", "Exterior", "Invernadero", "Balcón"])
        riego = st.text_input("Frecuencia de Riego")
        sust = st.text_input("Sustrato")
        notas = st.text_area("Notas")
        
        if st.form_submit_button("Guardar en Google Sheets"):
            if apodo and esp:
                # Crear nueva fila
                nueva_fila = pd.DataFrame([{
                    "id": len(df_existente) + 1,
                    "apodo": apodo,
                    "categoria": cat,
                    "especie": esp,
                    "ubicacion": ubi,
                    "riego": riego,
                    "sustrato": sust,
                    "notas": notas
                }])
                # Combinar con datos existentes
                df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
                # Actualizar la planilla
                conn.update(worksheet="plantas", data=df_final)
                st.success(f"¡{apodo} guardada correctamente en Drive!")
                st.balloons()
            else:
                st.error("Por favor, completa al menos el Apodo y la Especie.")

elif choice == "Panel de Control":
    st.header("📋 Inventario en Tiempo Real")
    df = leer_datos()
    st.dataframe(df, use_container_width=True)

elif choice == "Fichas Detalladas":
    df = leer_datos()
    if not df.empty:
        sel_apodo = st.selectbox("Elegir Planta", df['apodo'].tolist())
        info = df[df['apodo'] == sel_apodo].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Categoría", info['categoria'])
            st.write(f"**Especie:** {info['especie']}")
            st.write(f"**Ubicación:** {info['ubicacion']}")
        with col2:
            st.write(f"**Riego:** {info['riego']}")
            st.write(f"**Sustrato:** {info['sustrato']}")
            st.write(f"**Notas:** {info['notas']}")
    else:
        st.info("No hay plantas registradas en la planilla.")

