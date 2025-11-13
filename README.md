# 📑 Actualización de Fechas de Pase a DRCM

Aplicación desarrollada en Streamlit para que las sedes actualicen la fecha de pase de expedientes hacia la DRCM.

## 🚀 Cómo usar

1. Seleccione su sede.
2. Ingrese la clave correspondiente (ej. LIMA2025).
3. Actualice las fechas de pase y presione "Guardar".

Los cambios se guardan directamente en el archivo Excel.

## 🛠️ Requisitos
- pandas
- openpyxl
- streamlit

## 🔄 Actualización de datos
Para agregar nuevos expedientes, reemplace el archivo `expedientes.xlsx` en el repositorio y Streamlit actualizará automáticamente la app.

## 🌐 Despliegue
1. Suba esta carpeta a GitHub.
2. En Streamlit Cloud, seleccione “New app”.
3. Vincule su repositorio y elija el archivo `app.py`.
4. Listo: la aplicación estará disponible en línea.
