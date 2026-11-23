# EcoResiduos IA

Aplicación web para el análisis y el apoyo a la decisión en la gestión de residuos sólidos municipales. Integra modelos de aprendizaje automático entrenados con datos abiertos y los presenta en una interfaz con una pestaña por módulo. Trabajo final de Software Inteligente (UNMSM, 2026-2).

## Alcance de esta versión

Esta versión incluye tres de los cinco módulos previstos. Los módulos de series temporales y de resumen de texto se incorporarán en la entrega final; los datos de la serie mensual de Nueva York ya están preparados en `data/processed/`.

| Módulo | Qué hace | Datos | Modelo seleccionado |
|---|---|---|---|
| Predicción | Estima la generación de residuos per cápita (kg por habitante y día) de un país a partir de su PIB, población y región, con un simulador de escenarios | What a Waste (Banco Mundial), 172 países con dato | SVR; RMSE de prueba 0,443 frente a 0,501 del baseline (promedio por grupo de ingreso) |
| Clustering | Agrupa países según su generación y composición de residuos y permite asignar un perfil nuevo a un grupo | What a Waste (Banco Mundial) | K-Means con k = 4; Silhouette 0,219 (estructura débil, se presenta como tipología orientativa) |
| Imágenes | Clasifica la foto de un residuo en 10 categorías y sugiere el contenedor según el esquema elegido | Garbage Classification V2 (entrenamiento) y TrashNet (prueba externa) | MobileNetV2 con ajuste fino; exactitud de 0,915 y macro-F1 de 0,910 en la prueba de 10 clases, y exactitud de 0,610 en la prueba externa |

Las métricas completas, las limitaciones de cada modelo y la fecha de entrenamiento se muestran en la pestaña «Modelo y métricas» de cada módulo y se guardan en `models/*_meta.json`.

## Requisitos

- Python 3.11 o superior. El desarrollo y las pruebas se hicieron con Python 3.13.
- No se necesita GPU. El entrenamiento del clasificador de imágenes se realizó en Google Colab; la aplicación solo carga modelos ya entrenados.

## Instalación

```bash
python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# Windows (cmd):         venv\Scripts\activate.bat
# Linux y macOS:         source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto (la carpeta que contiene `config.py`):

```bash
streamlit run app/main.py
```

La aplicación se abre en `http://localhost:8501`.

## Pruebas

```bash
python -m pytest tests
```

Las pruebas del módulo de imágenes se omiten si faltan TensorFlow o los archivos de `models/`.

## Reproducir el entrenamiento

Los modelos incluidos en `models/` ya están entrenados. Para regenerarlos:

```bash
python src/preparar_datos.py todo      # descarga y limpia What a Waste y DSNY
python src/eda_tabular.py              # figuras del análisis exploratorio en docs/figuras/
python src/entrenar_prediccion.py      # módulo de predicción
python src/entrenar_clustering.py      # módulo de clustering
```

El clasificador de imágenes se entrena en Google Colab con `notebooks/03_imagenes_colab.ipynb`. Allí se descargan los datos con la API de Kaggle, que requiere un archivo `kaggle.json` propio; ese archivo no debe subirse al repositorio. Los notebooks `01_prediccion.ipynb` y `04_clustering.ipynb` contienen el mismo análisis que los scripts, con sus resultados.

## Estructura

```
app/            interfaz (main.py), módulos por pestaña (modules/) y utilidades (utils/)
config.py       rutas, semilla, registro de módulos y esquemas de contenedores
data/           raw/ (descargas, no versionadas), processed/ (datos limpios y resultados), imagenes/
docs/           diccionario de datos, descripción de los datos de imágenes y figuras
models/         modelos entrenados y sus metadatos (*_meta.json)
notebooks/      entrenamiento y comparación de modelos
src/            preparación de datos, análisis exploratorio y entrenamiento
tests/          pruebas automáticas
```

## Datos, licencias y uso responsable

Los datos provienen de fuentes públicas: *What a Waste* (Banco Mundial, licencia CC-BY-4.0 según su ficha), *DSNY Monthly Tonnage* (NYC Open Data), Garbage Classification V2 y TrashNet (ambos en Kaggle). Las fuentes, columnas y transformaciones están en `docs/diccionario_datos.md` y `docs/datos_imagenes.md`. Antes de reutilizar los datos, consulta la licencia de cada conjunto en su página de origen; aquí se usan con fines académicos y las imágenes no se incluyen en el repositorio.

Las estimaciones y clasificaciones son orientativas y pueden contener errores y sesgos de los datos; no sustituyen la evaluación de un especialista. No subas imágenes con personas ni datos personales.
