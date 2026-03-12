import streamlit as st
import pandas as pd

# PEGA TU LINK DE PUBLICAR EN LA WEB AQUÍ
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5S2AYo5jWssqfdMA7tsLX7N2Ba6QdC-E2E_oHFYUnTBvzCEG6mryI1uVNLCDe-R44--dTvmrARqy/pub?output=csv"

st.set_page_config(page_title="Mi Jardín", page_icon="🌵")

st.title("🌵 Mi Colección de Plantas")

try:
    # Leemos los datos
    df = pd.read_csv(URL_CSV)
    
    # Buscador
    buscar = st.text_input("🔍 Buscar planta...")
    if buscar:
        df = df[df.apply(lambda r: buscar.lower() in r.astype(str).str.lower().values, axis=1)]

    # Mostramos la tabla
    st.dataframe(df, use_container_width=True)
    
    st.success(f"Se encontraron {len(df)} plantas.")

except Exception as e:
    st.error("Conectando con la base de datos...")
    st.info("Asegurate de haber pegado el link de 'Publicar en la web' en el código.")

st.divider()
st.write("📢 **Para agregar plantas:** Editá directamente tu archivo de Google Sheets y los cambios aparecerán aquí al refrescar.")
