# Manual de instalación — EcoCiudad IA

> **Estado de verificación (honesto):** estos pasos se probaron en el PC del equipo con Windows y Python 3.13.6 (Git Bash), pero **sobre una carpeta de trabajo ya existente**. La instalación en una carpeta y un entorno virtual **nuevos** sigue pendiente (checklist en `docs/checklist_instalacion.md`). Otros sistemas operativos y otras versiones de Python **no se probaron**.

## 1. Requisitos

| Elemento | Detalle |
|---|---|
| Sistema operativo | Probado: Windows. Linux y macOS: no probados |
| Python | Probado: **3.13.6**. El diseño inicial sugería 3.11, que no se probó. Comprueba con `python --version` |
| Git | Para clonar el repositorio (o descarga el ZIP desde GitHub) |
| GPU | **No se necesita**: la app solo carga modelos ya entrenados |
| Internet | Para instalar paquetes y, solo si usas el resumen abstractivo, para descargarlo la primera vez |
| Espacio en disco | La carpeta `models/` pesa unos 60 MB. El modelo abstractivo (opcional) se descarga de Hugging Face y ocupa unos 2.33 GB. El espacio de TensorFlow y de las demás librerías **no se midió** |
| Memoria | Con el abstractivo se midió un pico de unos 2.5 GiB en un PC de 4 núcleos sin GPU. La memoria mínima para el resto **no se midió** |

## 2. Obtener el código

```bash
git clone <URL del repositorio> EcoCiudad
cd EcoCiudad
```
(O descarga el ZIP del repositorio, descomprímelo y entra a la carpeta que contiene `config.py`.) **Todos los comandos siguientes se ejecutan desde esa carpeta.**

## 3. Crear y activar el entorno virtual

```bash
python -m venv venv
```
| Terminal | Activar |
|---|---|
| Git Bash (Windows) | `source venv/Scripts/activate` |
| PowerShell | `venv\Scripts\Activate.ps1` |
| cmd | `venv\Scripts\activate.bat` |
| Linux / macOS | `source venv/bin/activate` |

El prompt debe mostrar `(venv)`.

## 4. Instalar las dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Puede tardar varios minutos (incluye TensorFlow). `requirements.txt` también trae `notebook` y `datasets`, que solo se usan para los notebooks y para `src/preparar_textos.py`; la app no los necesita.

**Opcional, resumen abstractivo** (si no lo instalas, la pestaña Resumen funciona con el método extractivo):
```bash
pip install -r requirements-abstractivo.txt
```
Si pip no encuentra `torch==2.14.1`, instala torch para CPU desde <https://pytorch.org/get-started/locally/> y luego `transformers` y `sentencepiece`.

## 5. Datos y modelos

Ya vienen en el repositorio y **no hay que descargar nada para ejecutar la app**:
- `models/`: modelos entrenados y sus `*_meta.json` (de ahí salen todas las métricas que muestra la app).
- `data/processed/`: tablas limpias que usan los módulos.

No se incluyen (y la app no los necesita): `data/raw/`, `data/imagenes/` y `data/processed/textos_residuos.csv` (licencia no comercial). Si quieres regenerar datos o reentrenar, mira los scripts de `src/` y los notebooks de `notebooks/`; el de imágenes se ejecuta en Google Colab y pide una cuenta de Kaggle. **Nunca subas `kaggle.json` al repositorio.**

## 6. Comprobar la instalación

```bash
python -c "from app.utils.diagnostico import revisar_todos; print([r for r in revisar_todos() if not r['listo']])"
python -m pytest -q
```
La primera línea debe imprimir `[]` (no falta ningún archivo). La segunda debe terminar con `passed`; en el PC del equipo salió `46 passed in 38.71s`.

## 7. Ejecutar la aplicación

```bash
streamlit run app/main.py
```
Se abre el navegador en `http://localhost:8501` con la pestaña **Inicio** y las cinco de los módulos. Para detenerla, pulsa `Ctrl+C` en la terminal. En el PC del equipo, el servidor respondió en unos 3 s y la primera ejecución de la página tardó unos 6 s medida sin navegador (después, unos 0.5 s por interacción); en otros equipos serán distintos.

## 8. Solución de problemas

| Síntoma | Qué hacer |
|---|---|
| `ModuleNotFoundError: No module named 'app'` o `'config'` | Ejecuta siempre desde la carpeta que contiene `config.py` y con `streamlit run app/main.py` |
| El puerto 8501 está ocupado | `streamlit run app/main.py --server.port 8502` |
| En PowerShell no activa el entorno («la ejecución de scripts está deshabilitada») | Usa cmd o Git Bash, o permite scripts para tu usuario con `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| La barra lateral muestra ⏳ y «Faltan: …» | Falta un archivo de `models/` o `data/processed/`; vuelve a descargar el repositorio completo |
| Un módulo muestra «Falta la librería …» | Activa el entorno y repite `pip install -r requirements.txt` |
| Series temporales muestra «No pude usar el modelo guardado…» | La versión de `statsmodels` es distinta de la del entrenamiento (`models/serie_meta.json`, campo `librerias`); la app muestra entonces la tabla del entrenamiento. Reinstala la versión de `requirements.txt` |
| Resumen abstractivo no aparece | Faltan `torch`, `transformers` o `sentencepiece`: instala `requirements-abstractivo.txt` |
| El abstractivo tarda mucho la primera vez | Descarga unos 2.33 GB y luego queda en memoria; sin GPU, un texto largo puede tardar minutos (la app muestra una estimación) |
| Poca memoria al usar el abstractivo | Cierra otros programas; usa el método extractivo |
| Fallo de instalación de TensorFlow | Se probó con Python 3.13.6 en Windows; con otra versión de Python puede no haber paquete. Anota el mensaje completo |
| Al ejecutar un script de `src/` aparece «No runtime found» de Streamlit | Es normal fuera de la app |
