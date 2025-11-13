import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Actualización DRCM", page_icon="📁", layout="wide")

archivo = "expedientes.xlsx"

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        df = pd.read_excel(archivo, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"No se encontró {archivo}")
        return pd.DataFrame(columns=["N° Expediente", "Fecha Trámite", "Sede", "Fecha Pase DRCM"])
    df["Fecha Trámite"] = pd.to_datetime(df.get("Fecha Trámite"), errors="coerce")
    df["Fecha Pase DRCM"] = pd.to_datetime(df.get("Fecha Pase DRCM"), errors="coerce")
    return df

df = cargar_datos()
if df.empty:
    st.stop()

sedes = sorted(df["Sede"].dropna().unique())
sede_sel = st.selectbox("Seleccione su sede:", sedes)
if not sede_sel:
    st.stop()

df_sede = df[df["Sede"] == sede_sel].copy()

def safe_strftime(val):
    if pd.isna(val): return "---"
    return pd.to_datetime(val).strftime("%d/%m/%Y")

st.subheader(f"Expedientes - {sede_sel}")
for i, row in df_sede.iterrows():
    c1, c2, c3, c4 = st.columns([2,2,2,1])
    with c1: st.write(f"📂 {row['N° Expediente']}")
    with c2: st.write(f"🗓️ {safe_strftime(row['Fecha Trámite'])}")
    fecha = row["Fecha Pase DRCM"]
    default_date = date.today() if pd.isna(fecha) else pd.to_datetime(fecha).date()
    with c3:
        nueva_fecha = st.date_input("Fecha Pase DRCM", value=default_date, key=f"f{i}")
    with c4:
        if st.button("Guardar", key=f"s{i}"):
            try:
                df.loc[i, "Fecha Pase DRCM"] = pd.to_datetime(nueva_fecha)
                df.to_excel(archivo, index=False, engine="openpyxl")
                st.success(f"Actualizado {row['N° Expediente']}")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
