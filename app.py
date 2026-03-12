import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE ENLACES ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5S2AYo5jWssqfdMA7tsLX7N2Ba6QdC-E2E_oHFYUnTBvzCEG6mryI1uVNLCDe-R44--dTvmrARqy/pub?output=csv"
# PEGA AQUÍ EL LINK QUE USAS PARA EDITAR TU EXCEL:
LINK_DE_EDICION = "https://docs.google.com/spreadsheets/d/13eofTb4yy_Mxzv6j_Sv949bpsUvIpb84cDiHqy-MYPw/edit?gid=0#gid=0" 

st.set_page_config(page_title="Mi Jardín Botánico", page_icon="🌿", layout="centered")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f1; }
    .planta-card {
        background-color: white;
        padding: 22px;
        border-radius: 15px;
        border-left: 6px solid #2e7d32;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .categoria-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🌿 Mi Inventario Botánico")
st.caption("Base de datos personalizada de mi colección")

# --- CARGA Y PROCESAMIENTO ---
try:
    df = pd.read_csv(URL_CSV)
    # Normalizar nombres de columnas
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Limpiar columnas automáticas de Google si existen
    columnas_a_quitar = ['marca temporal', 'timestamp']
    for col in columnas_a_quitar:
        if col in df.columns:
            df = df.drop(columns=[col])

    # --- BUSCADOR ---
    busqueda = st.text_input("🔍 Buscar en el jardín...", placeholder="Ej: Cactus, Interior, Jade...")

    if busqueda:
        mask = df.apply(lambda r: busqueda.lower() in r.astype(str).str.lower().values, axis=1)
        df_mostrar = df[mask]
    else:
        df_mostrar = df

    # --- VISTA DE FICHAS ---
    if not df_mostrar.empty:
        for i, row in df_mostrar.iterrows():
            with st.container():
                # Obtenemos datos con valores por defecto por si falta alguno
                nombre = row.get('apodo', 'Sin nombre')
                especie = row.get('especie', 'No especificada')
                cat = row.get('categoria', 'General')
                ubi = row.get('ubicacion', '-')
                riego = row.get('riego', '-')
                sust = row.get('sustrato', '-')
                notas = row.get('notas', '')

                st.markdown(f"""
                <div class="planta-card">
                    <span class="categoria-badge">{cat}</span>
                    <h3 style="margin: 10px 0 5px 0; color:#1b5e20;">🌵 {nombre}</h3>
                    <p style="color:#666; font-size: 14px; margin-bottom:15px;"><i>{especie}</i></p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 13px; color: #444;">
                        <div><b>📍 Ubicación</b><br>{ubi}</div>
                        <div><b>💧 Riego</b><br>{riego}</div>
                        <div><b>🪴 Sustrato</b><br>{sust}</div>
                    </div>
                    {f'<p style="margin-top:15px; padding-top:10px; border-top:1px solid #eee; font-size: 13px; color: #777;"><b>Notas:</b> {notas}</p>' if notas else ''}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron resultados en la búsqueda.")

except Exception as e:
    st.error("Conectando con la base de datos...")
    st.caption("Asegúrate de que la primera fila del Excel tenga los títulos correctos.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Opciones")
    st.write("Gestiona tus plantas directamente en la planilla original.")
    
    # Botón para abrir el Excel real
    st.link_button("📂 Editar mi Google Sheets", LINK_DE_EDICION)
    
    st.divider()
    
    # Clima local (Comodoro Rivadavia)
    try:
        clima = requests.get("https://wttr.in/Comodoro+Rivadavia?format=%c+%t", timeout=2).text
        st.metric("Clima actual", clima)
    except:
        pass
    
    st.caption("v2.0 - Interfaz Mejorada")
