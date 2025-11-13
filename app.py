# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="Actualización Expedientes DRCM", layout="wide")
st.title("📋 Actualización Consolidada de Expedientes - DRCM")

# Ruta del archivo maestro en red (ajustar si cambia la ubicación)
ARCHIVO = r"C:\Users\mdiaze\Desktop\actualizacion_drcm\expedientes.xlsx"

# ---------------- FUNCIONES AUXILIARES ----------------
@st.cache_data(ttl=60)
def cargar_datos(ruta):
    """Carga el archivo Excel y corrige formatos de fecha."""
    try:
        df = pd.read_excel(ruta, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"No se encontró el archivo en la ruta: {ruta}")
        return pd.DataFrame()

    # Limpieza de nombres de columnas
    df.columns = [c.strip() for c in df.columns]

    # Conversión de fechas
    for col in ["Fecha de Expediente", "Fecha Inicio de Etapa de Proceso",
                "Fecha Fin de Etapa de Proceso", "Fecha Envío a DRCM"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        else:
            df[col] = pd.NaT

    return df


def calcular_dias_restantes(fecha_expediente, fecha_envio=None):
    """Calcula días entre fecha de expediente y fecha de envío o fecha actual."""
    if pd.isna(fecha_expediente):
        return None
    fecha_ref = fecha_envio if pd.notna(fecha_envio) else datetime.now()
    return (fecha_ref - fecha_expediente).days


def guardar_actualizacion(expediente, nueva_fecha):
    """Guarda la fecha de envío actualizada en el Excel consolidado."""
    try:
        df = pd.read_excel(ARCHIVO, engine="openpyxl")
        df.columns = [c.strip() for c in df.columns]
        df["Fecha de Expediente"] = pd.to_datetime(df["Fecha de Expediente"], errors="coerce", dayfirst=True)

        mask = df["Número de Expediente"] == expediente
        if mask.any():
            df.loc[mask, "Fecha Envío a DRCM"] = pd.to_datetime(nueva_fecha, dayfirst=True)
            df.loc[mask, "Días restantes"] = (
                pd.to_datetime(date.today()) - df.loc[mask, "Fecha de Expediente"]
            ).dt.days

            # Guardar consolidado
            df.to_excel(ARCHIVO, index=False, engine="openpyxl")

            # Registro de actualización
            hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.success(f"✅ Expediente {expediente} actualizado correctamente en el consolidado.")
            st.info(f"📁 Guardado en: {ARCHIVO}\n🕒 Última actualización: {hora_actual}")
        else:
            st.warning(f"⚠️ No se encontró el expediente {expediente}.")
    except Exception as e:
        st.error(f"Error al guardar los cambios: {e}")


# ---------------- INTERFAZ PRINCIPAL ----------------
df = cargar_datos(ARCHIVO)
if df.empty:
    st.stop()

dependencias = sorted(df["Dependencia"].dropna().unique().tolist())
dependencia_sel = st.selectbox("Seleccione la Dependencia:", ["-- Seleccione --"] + dependencias)

clave = st.text_input("🔐 Clave de acceso (por dependencia):", type="password")
if dependencia_sel == "-- Seleccione --":
    st.info("Seleccione una dependencia para continuar.")
    st.stop()

clave_correcta = dependencia_sel.upper() + "2025"
if clave != clave_correcta:
    st.warning("Clave incorrecta o no ingresada.")
    st.stop()

st.success(f"✅ Acceso concedido a dependencia: {dependencia_sel}")

# Filtrar expedientes pendientes
df_dep = df[
    (df["Dependencia"] == dependencia_sel) &
    (df["Estado de Trámite"].str.lower() == "pendiente")
].copy()

if df_dep.empty:
    st.info("No hay expedientes pendientes para esta dependencia.")
    st.stop()

st.subheader(f"📄 Expedientes pendientes - {dependencia_sel} ({len(df_dep)})")

# Mostrar y actualizar expedientes
for idx, row in df_dep.iterrows():
    cols = st.columns([2, 1, 1, 1, 1])
    expediente = row.get("Número de Expediente")

    with cols[0]:
        st.markdown(f"**{expediente}**")
        st.caption(f"🗂️ {row.get('Tipo de Proceso', '')} | {row.get('Tipo de Calidad Migratoria', '')}")

    with cols[1]:
        fecha_exp = row.get("Fecha de Expediente")
        txt_fecha_exp = fecha_exp.strftime("%d/%m/%Y") if not pd.isna(fecha_exp) else "---"
        st.write(f"📅 Expediente: **{txt_fecha_exp}**")

    with cols[2]:
        fecha_envio_actual = row.get("Fecha Envío a DRCM")
        default_date = fecha_envio_actual.date() if not pd.isna(fecha_envio_actual) else date.today()
        nueva_fecha = st.date_input("Fecha Envío DRCM", value=default_date, key=f"fecha_{idx}")

    with cols[3]:
        dias = calcular_dias_restantes(fecha_exp, fecha_envio_actual)
        color = "red" if dias and dias >= 6 else "black"
        st.markdown(f"<span style='color:{color}'><b>{dias if dias else '--'} días</b></span>", unsafe_allow_html=True)

    with cols[4]:
        if st.button("💾 Guardar", key=f"guardar_{idx}"):
            guardar_actualizacion(expediente, nueva_fecha)
            st.cache_data.clear()
