# SIGERH v9 — Paso 25: integración de la cartera completa

Esta versión conserva los módulos del MPRH de la versión 8 y añade la pestaña **Cartera completa**, que permite consultar y filtrar los 100,000 créditos originales de forma independiente de las clasificaciones experimentales.

## Instalación en Windows
1. Descomprime el ZIP dentro de `PPt8`.
2. Copia la carpeta `datos` de `SIGERH_web_v8` dentro de `SIGERH_web_v9`.
3. Comprueba que en `datos` estén `BD_hipotecarios_SIGERH_limpia.csv` y los cuatro archivos `clasificacion_{variable,persistente}_{validacion,prueba}.csv`.
4. Abre `SIGERH_web_v9` en VS Code.
5. Ejecuta `python -m pip install -r requirements.txt` y `python -m streamlit run app.py`.

## Alcance metodológico
- La pestaña **Cartera completa** muestra el dataset original de 100,000 créditos, sin asignar puntuaciones del MPRH a registros sin evaluación.
- Las pestañas predictivas conservan sus 16,875 créditos de validación y prueba, con filtros propios en la barra lateral.
- Las 56,449 observaciones elegibles incluyen entrenamiento, validación y prueba. No se muestran las predicciones de entrenamiento como evaluación independiente.
- El módulo nuevo no requiere reentrenamiento ni altera las bases de datos.
- Los datos son simulados; las puntuaciones no representan probabilidades reales validadas.
