# ♻️ EcoCiudad IA

Aplicación de **gestión inteligente de residuos urbanos** con 5 módulos de IA (predicción, series temporales, clasificación de imágenes, clustering y resumen de texto). Trabajo Final de *Software Inteligente* (UNMSM, 2026-2).

> **Estado:** en desarrollo por fases. Los módulos aparecen como «en construcción» hasta que se entrenen y se agreguen sus modelos. Consulta `estado/ESTADO_PROYECTO.md`.

## Requisitos
- Python 3.11 (recomendado en el stack del proyecto). Verifica con `python --version`.
- Sin GPU: el entrenamiento pesado (imágenes) se hace en Google Colab; la app solo carga modelos ya entrenados.

## Instalación (primera vez)
```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
# Windows (PowerShell):   venv\Scripts\Activate.ps1
# Windows (cmd):          venv\Scripts\activate.bat
# Linux / macOS:          source venv/bin/activate

# 2. Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Fijar las versiones realmente instaladas en requirements.txt
python src/fijar_versiones.py
```

## Ejecutar la aplicación
Desde la raíz del proyecto (la carpeta que contiene `config.py`):
```bash
streamlit run app/main.py
```
Se abre en `http://localhost:8501`.

## Estructura
- `app/`: interfaz (`main.py`), módulos (`modules/`) y utilidades (`utils/`).
- `src/`: scripts de datos y utilidades de entorno.
- `notebooks/`: entrenamiento y comparación de modelos por módulo.
- `models/`: modelos entrenados y sus `*_meta.json` (única fuente de las métricas).
- `data/`: `raw/` (descargas, no versionadas), `processed/` (CSV limpios), `imagenes/`.
- `docs/`: manuales e informe técnico (Markdown).
- `estado/`, `contexto/`: memoria y material de apoyo del proyecto.

## Datos y ética
Se usan datasets públicos con sus licencias y citas (ver `contexto/C3_datasets_del_proyecto.md`; se verifican en la Fase 2). Los datos crudos y los de licencia no comercial no se incluyen en el repositorio. Las salidas son orientativas y pueden contener sesgos y errores. No subas imágenes con personas ni datos personales.
