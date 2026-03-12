import streamlit as st
import pandas as pd
import requests

# Tu link seguro
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5S2AYo5jWssqfdMA7tsLX7N2Ba6QdC-E2E_oHFYUnTBvzCEG6mryI1uVNLCDe-R44--dTvmrARqy/pub?output=csv"

st.set_page_config(page_title="Mi Jardín Botánico", page_icon="🌿", layout="centered")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f1; }
    .planta-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .categoria-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🌿 Mi Inventario Botánico")
st.caption("Gestión personalizada para mi colección en Comodoro")

try:
    df = pd.read_csv(URL_CSV)
    df.columns = df.columns.str.strip().str.lower()

    # --- BUSCADOR ---
    busqueda = st.text_input("🔍 Buscar en mi jardín...", placeholder="Ej: Cactus, Jade, Interior...")

    if busqueda:
        df = df[df.apply(lambda r: busqueda.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- VISTA DE FICHAS (No tabla) ---
    if not df.empty:
        for i, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="planta-card">
                    <span class="categoria-badge">{row.get('categoria', 'Sin Categoría').upper()}</span>
                    <h3 style="margin-top:10px; color:#1b5e20;">🌵 {row.get('apodo', 'Sin nombre')}</h3>
                    <p style="color:#555;"><b>Especie:</b> {row.get('especie', '-')}</p>
                    <hr style="margin:10px 0; border:0.5px solid #eee;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>📍 {row.get('ubicacion', '-')}</span>
                        <span>💧 {row.get('riego', '-')}</span>
                        <span>🪴 {row.get('sustrato', '-')}</span>
                    </div>
                    <p style="margin-top:10px; font-size: 13px; font-style: italic; color: #777;">
                        <b>Notas:</b> {row.get('notas', 'Sin anotaciones.')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron plantas. Agregá datos en tu Google Sheets para verlos aquí.")

except:
    st.error("Esperando conexión con Google Sheets...")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    st.write("Para agregar plantas, editá tu planilla de Google.")
    st.link_button("📂 Abrir mi Excel", "https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F") # Cambia por tu link real de edición
    
    st.divider()
    # Clima rápido
    try:
        res = requests.get("https://wttr.in/Comodoro+Rivadavia?format=%c+%t", timeout=2)
        st.metric("Clima Comodoro", res.text)
    except:
        pass
