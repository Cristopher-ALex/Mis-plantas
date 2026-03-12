import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE ENLACES ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5S2AYo5jWssqfdMA7tsLX7N2Ba6QdC-E2E_oHFYUnTBvzCEG6mryI1uVNLCDe-R44--dTvmrARqy/pub?output=csv"
LINK_DE_EDICION = https://docs.google.com/spreadsheets/d/13eofTb4yy_Mxzv6j_Sv949bpsUvIpb84cDiHqy-MYPw/edit?gid=0#gid=0"" 

st.set_page_config(page_title="Mi Jardín Botánico", page_icon="🌿", layout="centered")

# --- ESTILO VISUAL MEJORADO CON FOTOS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f1; }
    .planta-card {
        background-color: white;
        padding: 0px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    .card-content { padding: 20px; border-left: 6px solid #2e7d32; }
    .foto-planta {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .categoria-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Mi Inventario Botánico")

try:
    df = pd.read_csv(URL_CSV)
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    busqueda = st.text_input("🔍 Buscar en el jardín...", placeholder="Ej: Cactus, Interior, Jade...")

    if busqueda:
        mask = df.apply(lambda r: busqueda.lower() in r.astype(str).str.lower().values, axis=1)
        df_mostrar = df[mask]
    else:
        df_mostrar = df

    if not df_mostrar.empty:
        for i, row in df_mostrar.iterrows():
            foto_url = row.get('foto')
            # Si no hay foto, usamos una imagen por defecto de naturaleza
            img_html = f'<img src="{foto_url}" class="foto-planta">' if pd.notna(foto_url) and str(foto_url).startswith('http') else ''
            
            st.markdown(f"""
            <div class="planta-card">
                {img_html}
                <div class="card-content">
                    <span class="categoria-badge">{row.get('categoria', 'General')}</span>
                    <h3 style="margin: 10px 0 5px 0; color:#1b5e20;">🌵 {row.get('apodo', 'Sin nombre')}</h3>
                    <p style="color:#666; font-size: 14px; margin-bottom:15px;"><i>{row.get('especie', 'No especificada')}</i></p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 13px; color: #444;">
                        <div><b>📍 Ubicación</b><br>{row.get('ubicacion', '-')}</div>
                        <div><b>💧 Riego</b><br>{row.get('riego', '-')}</div>
                        <div><b>🪴 Sustrato</b><br>{row.get('sustrato', '-')}</div>
                    </div>
                    {f'<p style="margin-top:15px; padding-top:10px; border-top:1px solid #eee; font-size: 13px; color: #777;"><b>Notas:</b> {row.get("notas", "")}</p>' if pd.notna(row.get("notas")) else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay plantas para mostrar.")

except Exception as e:
    st.error("Error al cargar los datos.")

with st.sidebar:
    st.header("Opciones")
    st.link_button("📂 Editar mi Google Sheets", LINK_DE_EDICION)
    st.divider()
    try:
        clima = requests.get("https://wttr.in/Comodoro+Rivadavia?format=%c+%t", timeout=2).text
        st.metric("Clima actual", clima)
    except:
        pass
