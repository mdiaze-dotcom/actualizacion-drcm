# Actualización Consolidada de Expedientes - DRCM

Coloca esta carpeta en la máquina que ejecutará la aplicación (por ejemplo, un equipo en la red con acceso a la carpeta compartida).
La app trabaja directamente sobre el archivo maestro en red:
\\172.27.230.55\gu\Jefaturas Zonales\actualizacion_drcm\expedientes.xlsx

## Uso
1. Instala dependencias: `pip install -r requirements.txt`
2. Ejecuta: `streamlit run app.py`
3. Desde el navegador selecciona la dependencia, ingresa la clave (DEPENDENCIA + 2025) y actualiza las fechas.
4. El sistema actualizará el archivo maestro en la ruta de red y registrará el cambio en `log_actualizaciones.csv`.

## Notas
- Asegúrate de que la máquina que ejecuta la app tenga acceso de lectura/escritura a la ruta de red.
- Si múltiples usuarios actualizan simultáneamente, Windows maneja el bloqueo. El código hace una lectura fresca antes de escribir para minimizar conflictos.
