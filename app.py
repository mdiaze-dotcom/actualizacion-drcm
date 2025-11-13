import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Actualización de Expedientes DRCM", page_icon="📁", layout="wide")
st.title("📋 Sistema de Actualización de Expedientes - DRCM")
st.write("Aplicativo para que las sedes actualicen la **fecha de pase a la DRCM** de cada expediente.")

# --- RUTA DEL ARCHIVO EXCEL ---
archivo = "expedientes.xlsx"

# --- CARGA SEGURA DEL ARCHIVO ---
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        df = pd.read_excel(archivo, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo `{archivo}` en el repositorio.")
        return pd.DataFrame(columns=["N° Expediente", "Fecha Trámite", "Sede", "Fecha Pase DRCM"])
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame(columns=["N° Expediente", "Fecha Trámite", "Sede", "Fecha Pase DRCM"])

    # Asegurar tipos de datos correctos
    if "Fecha Trámite" in df.columns:
        df["Fecha Trámite"] = pd.to_datetime(df["Fecha Trámite"], errors="coerce")
    if "Fecha Pase DRCM" in df.columns:
        df["Fecha Pase DRCM"] = pd.to_datetime(df["Fecha Pase DRCM"], errors="coerce")
    else:
        df["Fecha Pase DRCM"] = pd.NaT

    return df


# --- CARGAR LOS DATOS ---
df = cargar_datos()

if df.empty:
    st.stop()

# --- SELECCIÓN DE SEDE ---
sedes = sorted(df["Sede"].dropna().unique())
sede_sel = st.selectbox("🏢 Seleccione su sede:", sedes)

if not sede_sel:
    st.info("Seleccione una sede para continuar.")
    st.stop()

df_sede = df[df["Sede"] == sede_sel].copy()

st.subheader(f"📍 Expedientes de la sede: {sede_sel}")
st.caption("Ingrese o actualice la fecha de pase a DRCM según corresponda.")

# --- FUNCIÓN AUXILIAR PARA MOSTRAR FECHAS ---
def safe_strftime(val):
    """Convierte fecha a texto o muestra '---' si no hay valor."""
    try:
        if pd.isna(val):
            return '---'
        return pd.to_datetime(val).strftime('%d/%m/%Y')
    except Exception:
        return '---'

# --- INTERFAZ DE ACTUALIZACIÓN ---
if df_sede.empty:
    st.warning("No hay expedientes registrados para esta sede.")
else:
    for i, row in df_sede.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            st.write(f"📂 **Expediente:** {row.get('N° Expediente', '---')}")

        with col2:
            st.write(f"🗓️ Fecha Trámite: {safe_strftime(row.get('Fecha Trámite'))}")

        # Fecha actual (si existe)
        fecha_actual = row.get("Fecha Pase DRCM")
        if pd.isna(fecha_actual):
            default_date = date.today()
        else:
            try:
                default_date = pd.to_datetime(fecha_actual).date()
            except Exception:
                default_date = date.today()

        with col3:
            nueva_fecha = st.date_input(
                "Fecha Pase DRCM",
                value=default_date,
                key=f"fecha_{i}"
            )

        with col4:
            if st.button("Guardar", key=f"save_{i}"):
                # --- BLOQUE TRY COMPLETO ---
                try:
                    # Convertir la fecha seleccionada a datetime
                    fecha_guardar = pd.to_datetime(nueva_fecha)

                    # Actualizar el registro en el DataFrame original
                    df.loc[i, "Fecha Pase DRCM"] = fecha_guardar

                    # Forzar tipos correctos antes de guardar
                    df["Fecha Trámite"] = pd.to_datetime(df["Fecha Trámite"], errors="coerce")
                    df["Fecha Pase DRCM"] = pd.to_datetime(df["Fecha Pase DRCM"], errors="coerce")

                    # Guardar cambios en el archivo Excel
                    df.to_excel(archivo, index=False, engine="openpyxl")

                    # Mostrar confirmación
                    st.success(f"✅ Expediente {row.get('N° Expediente', '')} actualizado correctamente.")

                    # Limpiar caché para que se vean los cambios
                    st.cache_data.clear()

                except Exception as e:
                    st.error(f"❌ Error al guardar los datos: {e}")

# --- PIE DE PÁGINA ---
st.divider()
st.caption("Desarrollado por el equipo de análisis de datos · Dirección de Gestión de Información")
