
import streamlit as st
import pandas as pd
from datetime import date, datetime
from dateutil import parser

st.set_page_config(page_title="Actualización Expedientes DRCM - Avanzado", layout="wide")
st.title("📋 Actualización y Validación de Expedientes - DRCM")

archivo = "expedientes.xlsx"  # nombre del archivo en el repo

# Cargar con manejo de errores y parseo de fechas
@st.cache_data(ttl=60)
def cargar_datos(path):
    try:
        df = pd.read_excel(path, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {path}. Suba el archivo 'expedientes.xlsx' al repositorio.")
        return pd.DataFrame(columns=[
            "Número de Expediente","Dependencia","Fecha de Expediente","Días restantes",
            "Tipo de Proceso","Tipo de Calidad Migratoria","Fecha Inicio de Etapa de Proceso",
            "Fecha Fin de Etapa de Proceso","Estado de Trámite","Fecha Envío a DRCM"
        ])
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()
    # Normalize column names (strip)
    df.columns = [c.strip() for c in df.columns]
    # Parse date columns
    for col in ["Fecha de Expediente","Fecha Inicio de Etapa de Proceso","Fecha Fin de Etapa de Proceso","Fecha Envío a DRCM"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT
    # Ensure Estado de Trámite exists
    if "Estado de Trámite" not in df.columns:
        df["Estado de Trámite"] = ""
    return df

df = cargar_datos(archivo)
if df.empty:
    st.stop()

# Dependencias disponibles
dependencias = sorted(df["Dependencia"].dropna().unique().tolist())
dependencia_sel = st.selectbox("Seleccione la Dependencia:", ["-- Seleccione --"] + dependencias)

# Control de acceso básico por dependencia
clave = st.text_input("Clave de acceso (por dependencia):", type="password")
if dependencia_sel == "-- Seleccione --":
    st.info("Seleccione una dependencia para continuar.")
    st.stop()

clave_correcta = dependencia_sel.upper() + "2025"
if clave != clave_correcta:
    st.warning("Clave incorrecta o no ingresada. Ingrese la clave proporcionada para su dependencia.")
    st.stop()

st.success(f"Acceso concedido a dependencia: {dependencia_sel}")

# Filtrar por dependencia y solo pendientes
df_dep = df[(df["Dependencia"] == dependencia_sel) & (df["Estado de Trámite"].str.lower() == "pendiente")].copy()

st.subheader(f"Expedientes pendientes - {dependencia_sel} ({len(df_dep)})")
st.write("Formato de fecha mostrado: dd/mm/yyyy. Edite 'Fecha Envío a DRCM' para actualizar el pase.")

# Function to compute days remaining
def compute_days_remaining(fecha_expediente, fecha_envio):
    # If fecha_expediente is NaT return None
    if pd.isna(fecha_expediente):
        return None
    ref = fecha_envio if not pd.isna(fecha_envio) else pd.to_datetime(date.today())
    delta = (pd.to_datetime(ref).normalize() - pd.to_datetime(fecha_expediente).normalize()).days
    return delta

# Display table with editable rows
if df_dep.empty:
    st.info("No hay expedientes pendientes para esta dependencia.")
else:
    # Show a small legend
    st.markdown("**Leyenda:** si 'Días restantes' >= 6 se marcará en rojo (riesgo).")
    # Iterate rows and allow updating Fecha Envío a DRCM
    for idx, row in df_dep.iterrows():
        cols = st.columns([2,1,1,1,1])
        with cols[0]:
            st.markdown(f"**{row.get('Número de Expediente','---')}**")
            st.write(f"Tipo Proceso: {row.get('Tipo de Proceso','---')} | Calidad: {row.get('Tipo de Calidad Migratoria','---')}")
        with cols[1]:
            fecha_exp = row.get("Fecha de Expediente")
            txt_fecha_exp = fecha_exp.strftime('%d/%m/%Y') if not pd.isna(fecha_exp) else '---'
            st.write(f"📅 Fecha Expediente: **{txt_fecha_exp}**")
        with cols[2]:
            fecha_envio_current = row.get("Fecha Envío a DRCM")
            default_date = fecha_envio_current.date() if not pd.isna(fecha_envio_current) else date.today()
            nueva_fecha = st.date_input("Fecha Envío a DRCM", value=default_date, key=f"envio_{idx}")
        with cols[3]:
            dias = compute_days_remaining(row.get("Fecha de Expediente"), nueva_fecha)
            if dias is None:
                st.write("Días: ---")
            else:
                if dias >= 6:
                    st.markdown(f"<span style='color:red; font-weight:bold'>{dias} días</span>", unsafe_allow_html=True)
                else:
                    st.write(f"{dias} días")
        with cols[4]:
            if st.button("Guardar", key=f"guardar_{idx}"):
                try:
                    # Only update if Estado de Trámite == Pendiente (we already filtered)
                    fecha_guardar = pd.to_datetime(nueva_fecha)
                    df.loc[idx, "Fecha Envío a DRCM"] = fecha_guardar
                    # Recalculate Días restantes column in the master df
                    df.loc[idx, "Días restantes"] = compute_days_remaining(df.loc[idx, "Fecha de Expediente"], df.loc[idx, "Fecha Envío a DRCM"])
                    # Save with correct types
                    df["Fecha de Expediente"] = pd.to_datetime(df["Fecha de Expediente"], errors="coerce")
                    df["Fecha Envío a DRCM"] = pd.to_datetime(df["Fecha Envío a DRCM"], errors="coerce")
                    df.to_excel(archivo, index=False, engine="openpyxl")
                    st.success(f"Expediente {row.get('Número de Expediente')} actualizado correctamente.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# Option to download current filtered view as CSV
if not df_dep.empty:
    csv = df_dep.to_csv(index=False, date_format='%d/%m/%Y')
    st.download_button("📥 Descargar vista filtrada (CSV)", data=csv, file_name=f"expedientes_{dependencia_sel}.csv", mime="text/csv")
