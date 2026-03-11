import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN ---
# https://docs.google.com/spreadsheets/d/e/2PACX-1vQsVvVAuJQrO2jZdLLtBfXhrmqX0KAlwQh9Fazxd8wZydlyraBS_FqWYsm0WAHVd9CyXkPNTLsSmxk0/pub?output=csv" (el que termina en .csv)
URL_CSV = "TU_LINK_DE_PUBLICAR_EN_LA_WEB_AQUÍ"

st.set_page_config(page_title="Mi Jardín Permanente", layout="wide")

def leer_datos():
    try:
        # Leemos el CSV directamente de la web
        return pd.read_csv(URL_CSV)
    except:
        return pd.DataFrame(columns=["id", "apodo", "categoria", "especie", "ubicacion", "riego", "sustrato", "notas"])

# --- CLIMA ---
try:
    url_clima = "https://wttr.in/Comodoro+Rivadavia?format=%c+%t+%w"
    res = requests.get(url_clima, timeout=5)
    if res.status_code == 200:
        st.info(f"📍 Clima en Comodoro: {res.text}")
except:
    pass

st.title("🌿 Gestión Botánica")

menu = ["Inicio", "Registrar Nueva", "Panel de Control"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Inicio":
    st.write("Bienvenido. Tus datos se sincronizan con Google Sheets.")

elif choice == "Registrar Nueva":
    st.header("📝 Alta de Planta")
    with st.form("form_alta"):
        apodo = st.text_input("Apodo")
        cat = st.selectbox("Categoría", ["Cactus", "Flores", "Interior", "Exterior", "Árboles", "Bonsái", "Carnívoras"])
        esp = st.text_input("Especie")
        ubi = st.selectbox("Ubicación", ["Interior", "Exterior", "Invernadero", "Balcón"])
        riego = st.text_input("Riego")
        sust = st.text_input("Sustrato")
        notas = st.text_area("Notas")
        
        if st.form_submit_button("Guardar"):
            st.info("Para guardar datos permanentes, usaremos el formulario de Google Forms.")
            st.write("⚠️ Para evitar errores técnicos, te recomiendo usar un Google Form conectado a tu planilla.")

elif choice == "Panel de Control":
    df = leer_datos()
    st.dataframe(df, use_container_width=True)

