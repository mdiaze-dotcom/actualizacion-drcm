import streamlit as st
import pandas as pd
from datetime import date
import os
import csv
from datetime import datetime as dt

st.set_page_config(page_title="Actualización Expedientes DRCM (Consolidado)", layout="wide")
st.title("📋 Actualización Consolidada de Expedientes - DRCM")

# RUTA en red (modifícala si la carpeta difiere)
archivo = r"\\172.27.230.55\gu\Jefaturas Zonales\actualizacion_drcm\expedientes.xlsx"

# Archivo de log (local)
log_file = "log_actualizaciones.csv"

def init_log():
    if not os.path.exists(log_file):
        with open(log_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp","usuario_dependencia","numero_expediente","fecha_envio_drcm"])

@st.cache_data(ttl=60)
def cargar_datos(path):
    try:
        df = pd.read_excel(path, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"No se encontró el archivo maestro en la ruta: {path}\nAsegúrese de que la ruta sea accesible desde el equipo que ejecuta la app.")
        return pd.DataFrame(columns=[
            "Número de Expediente","Dependencia","Fecha de Expediente","Días restantes",
            "Tipo de Proceso","Tipo de Calidad Migratoria","Fecha Inicio de Etapa de Proceso",
            "Fecha Fin de Etapa de Proceso","Estado de Trámite","Fecha Envío a DRCM"
        ])
    except Exception as e:
        st.error(f"Error al leer el archivo maestro: {e}")
        return pd.DataFrame()

    df.columns = [c.strip() for c in df.columns]

    # Forzar dayfirst para interpretar dd/mm/YYYY hh:mm:ss correctamente
    for col in ["Fecha de Expediente","Fecha Inicio de Etapa de Proceso","Fecha Fin de Etapa de Proceso","Fecha Envío a DRCM"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        else:
            df[col] = pd.NaT

    if "Estado de Trámite" not in df.columns:
        df["Estado de Trámite"] = ""

    return df

def compute_days_remaining(fecha_expediente, fecha_envio):
    if pd.isna(fecha_expediente):
        return None
    ref = fecha_envio if not pd.isna(fecha_envio) else pd.to_datetime(date.today())
    delta = (pd.to_datetime(ref).normalize() - pd.to_datetime(fecha_expediente).normalize()).days
    return int(delta)

def guardar_actualizacion_consolidada(expediente, dependencia_usuario, nueva_fecha_envio):
    # Leer el maestro actual (última versión en la red)
    try:
        df_actual = pd.read_excel(archivo, engine="openpyxl")
    except Exception as e:
        st.error(f"No se puede acceder al archivo maestro para guardar: {e}")
        return False, str(e)

    df_actual.columns = [c.strip() for c in df_actual.columns]

    # Asegurar parsing
    if "Fecha de Expediente" in df_actual.columns:
        df_actual["Fecha de Expediente"] = pd.to_datetime(df_actual["Fecha de Expediente"], errors="coerce", dayfirst=True)
    if "Fecha Envío a DRCM" in df_actual.columns:
        df_actual["Fecha Envío a DRCM"] = pd.to_datetime(df_actual["Fecha Envío a DRCM"], errors="coerce", dayfirst=True)
    else:
        df_actual["Fecha Envío a DRCM"] = pd.NaT

    mask = df_actual["Número de Expediente"] == expediente
    if not mask.any():
        return False, "Expediente no encontrado en el maestro."

    # Actualizar solo la(s) columnas necesarias
    df_actual.loc[mask, "Fecha Envío a DRCM"] = pd.to_datetime(nueva_fecha_envio, dayfirst=True)
    df_actual.loc[mask, "Días restantes"] = compute_days_remaining(df_actual.loc[mask, "Fecha de Expediente"].iloc[0], df_actual.loc[mask, "Fecha Envío a DRCM"].iloc[0])

    # Guardar el maestro (sobrescribe consolidado en red)
    try:
        df_actual.to_excel(archivo, index=False, engine="openpyxl")
    except Exception as e:
        return False, f"Error al escribir en archivo maestro: {e}"

    # Registrar en log local
    try:
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([dt.now().strftime('%Y-%m-%d %H:%M:%S'), dependencia_usuario, expediente, pd.to_datetime(nueva_fecha_envio).strftime('%Y-%m-%d %H:%M:%S')])
    except Exception as e:
        # no fatal: log fallido pero actualización hecha
        st.warning(f"Advertencia: no se pudo escribir el log local: {e}")

    return True, "OK"

# Inicializar log
init_log()

# Cargar datos maestro
df = cargar_datos(archivo)
if df.empty:
    st.stop()

# Selección de dependencia y control sencillo por clave
dependencias = sorted(df['Dependencia'].dropna().unique().tolist())
dependencia_sel = st.selectbox("Seleccione la Dependencia:", ["-- Seleccione --"] + dependencias)

clave = st.text_input("Clave de acceso (por dependencia):", type='password')
if dependencia_sel == "-- Seleccione --":
    st.info("Seleccione una dependencia para continuar.")
    st.stop()

clave_correcta = dependencia_sel.upper() + "2025"
if clave != clave_correcta:
    st.warning("Clave incorrecta o no ingresada.")
    st.stop()

st.success(f"Acceso concedido a dependencia: {dependencia_sel}")

# Filtrar pendientes
df_dep = df[(df['Dependencia'] == dependencia_sel) & (df['Estado de Trámite'].str.lower() == 'pendiente')].copy()

st.subheader(f"Expedientes pendientes - {dependencia_sel} ({len(df_dep)})")
st.write("Formato de fecha mostrado: dd/mm/yyyy hh:mm:ss. Actualice 'Fecha Envío a DRCM' y presione Guardar.")

if df_dep.empty:
    st.info("No hay expedientes pendientes para esta dependencia.")
else:
    st.markdown('**Leyenda:** si \"Días restantes\" >= 6 se muestra en rojo.')
    for idx, row in df_dep.iterrows():
        cols = st.columns([2,1,1,1,1])
        with cols[0]:
            st.markdown(f"**{row.get('Número de Expediente','---')}**")
            st.write(f"Tipo: {row.get('Tipo de Proceso','---')} | Calidad: {row.get('Tipo de Calidad Migratoria','---')}")
        with cols[1]:
            fecha_exp = row.get('Fecha de Expediente')
            txt_fecha_exp = fecha_exp.strftime('%d/%m/%Y %H:%M:%S') if not pd.isna(fecha_exp) else '---'
            st.write(f"📅 Fecha Expediente: **{txt_fecha_exp}**")
        with cols[2]:
            fecha_envio_actual = row.get('Fecha Envío a DRCM')
            default_date = fecha_envio_actual.date() if not pd.isna(fecha_envio_actual) else date.today()
            nueva_fecha = st.date_input('Fecha Envío a DRCM', value=default_date, key=f'envio_{idx}')
        with cols[3]:
            dias = compute_days_remaining(row.get('Fecha de Expediente'), nueva_fecha)
            if dias is None:
                st.write('Días: ---')
            else:
                color = 'red' if dias >= 6 else 'black'
                st.markdown(f"<span style='color:{color}; font-weight:bold'>{dias} días</span>", unsafe_allow_html=True)
        with cols[4]:
            if st.button('Guardar', key=f'guardar_{idx}'):
                ok, msg = guardar_actualizacion_consolidada(row.get('Número de Expediente'), dependencia_sel, nueva_fecha)
                if ok:
                    st.success(f'Expediente {row.get(\"Número de Expediente\")} actualizado en el consolidado.')
                    st.cache_data.clear()
                else:
                    st.error(f'Error: {msg}')

# Descargar log si se desea
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        st.download_button('📥 Descargar registro de actualizaciones', data=f, file_name='log_actualizaciones.csv', mime='text/csv')
