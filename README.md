# Aplicación Actualización Expedientes DRCM - Avanzada

Esta aplicación en Streamlit permite filtrar por **Dependencia** y actualizar la **Fecha Envío a DRCM** solo para expedientes con estado 'Pendiente'.
- Formato de visualización de fechas: `dd/mm/yyyy`
- Cálculo de 'Días restantes' = (Fecha Envío a DRCM o HOY) - Fecha de Expediente
- Si 'Días restantes' >= 6 se indica en rojo en la interfaz.
- Control de acceso simple: clave = DEPENDENCIA + '2025' (por ejemplo: LIMA2025).

Archivos incluidos:
- app.py (aplicación Streamlit)
- expedientes.xlsx (ejemplo)
- requirements.txt
- README.md

Pasos para desplegar:
1. Subir todos los archivos al repositorio GitHub.
2. Conectar el repositorio en Streamlit Cloud y desplegar seleccionando app.py.
3. Actualizar el archivo `expedientes.xlsx` directamente en el repositorio cuando haya nuevos expedientes.
