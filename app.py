import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Actualización de Pase a DRCM", layout="wide")
st.title("📑 Actualización de Fechas de Pase a DRCM")

st.markdown("""
Este sistema permite que cada sede actualice las fechas de pase de expedientes a la DRCM.  
Seleccione su sede, ingrese su clave y actualice las fechas según corresponda.
""")

archivo = "expedientes.xlsx"

@st.cache_data(ttl=60)
def cargar_datos():
    df = pd.read_excel(archivo)
    df["Fecha Trámite"] = pd.to_datetime(df["Fecha Trámite"], errors="coerce")
    if "Fecha Pase DRCM" in df.columns:
        df["Fecha Pase DRCM"] = pd.to_datetime(df["Fecha Pase DRCM"], errors="coerce")
    return df

df = cargar_datos()

sedes = sorted(df["Sede"].dropna().unique())
sede_sel = st.selectbox("Seleccione su sede:", sedes)

clave = st.text_input("🔒 Ingrese la clave de acceso de su sede:", type="password")
clave_correcta = sede_sel.upper() + "2025"

if clave != clave_correcta:
    st.warning("⚠️ Ingrese la clave correcta para continuar.")
    st.stop()

st.success(f"✅ Acceso concedido a la sede: {sede_sel}")

df_sede = df[df["Sede"] == sede_sel].copy()

st.subheader(f"📍 Expedientes de la sede: {sede_sel}")
st.info("Ingrese o actualice la fecha de pase a DRCM según corresponda.")

for i, row in df_sede.iterrows():
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        st.write(f"📂 {row['N° Expediente']}")
    with col2:
        st.write(f"🗓️ {row['Fecha Trámite'].strftime('%d/%m/%Y') if pd.notna(row['Fecha Trámite']) else '---'}")
    with col3:
        nueva_fecha = st.date_input(
            "Fecha Pase DRCM",
            value=row["Fecha Pase DRCM"] if pd.notna(row["Fecha Pase DRCM"]) else datetime.today(),
            key=f"fecha_{i}"
        )
    with col4:
       if st.button("Guardar", key=f"save_{i}"):
    # Convertir correctamente a datetime
    fecha_guardar = pd.to_datetime(nueva_fecha)
    df.loc[i, "Fecha Pase DRCM"] = fecha_guardar

    # Asegurar que todas las fechas tengan formato válido antes de guardar
    df["Fecha Trámite"] = pd.to_datetime(df["Fecha Trámite"], errors="coerce")
    df["Fecha Pase DRCM"] = pd.to_datetime(df["Fecha Pase DRCM"], errors="coerce")

    # Guardar sin conflictos de tipo
    df.to_excel(archivo, index=False, engine="openpyxl")

    st.success(f"✅ Expediente {row['N° Expediente']} actualizado correctamente.")

st.caption("💾 Los cambios se guardan directamente en el archivo Excel del servidor.")
