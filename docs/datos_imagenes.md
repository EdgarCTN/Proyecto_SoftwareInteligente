# Datos de imágenes

Las imágenes no se incluyen en el repositorio por su peso y sus licencias. El entrenamiento se realizó en Google Colab con `notebooks/03_imagenes_colab.ipynb`, que descarga los datos con la API de Kaggle, elimina duplicados, genera la partición y entrena y compara tres variantes de modelo.

## Conjuntos utilizados

| Conjunto | Uso | Fuente | Contenido |
|---|---|---|---|
| DS3, Garbage Classification V2 | Entrenamiento, validación y prueba | Kaggle: `sumn2u/garbage-classification-v2` | 10 clases; se usó la carpeta `original` |
| DS4, TrashNet | Prueba externa en 6 clases comunes | Kaggle: `feyzazkefe/trashnet` | Carpeta `dataset-resized`; 277 imágenes quedan tras excluir las que coinciden con DS3 |

La licencia de cada conjunto debe consultarse en su página de origen antes de reutilizar los datos; en este proyecto se usan solo con fines académicos y no se redistribuyen.

## Obtención

1. En Kaggle, la opción *Settings > API > Create New Token* descarga el archivo `kaggle.json`. Es una credencial personal: no se sube a Git ni se comparte.
2. Colócalo en `%USERPROFILE%\.kaggle\kaggle.json` (Windows) o en `~/.kaggle/kaggle.json` (Linux y macOS).
3. Instala la herramienta y descarga los conjuntos:

```bash
pip install kaggle
kaggle datasets download -d sumn2u/garbage-classification-v2 -p data/raw/imagenes/ds3 --unzip
kaggle datasets download -d feyzazkefe/trashnet -p data/raw/imagenes/ds4 --unzip
```

Si no tienes cuenta de Kaggle, descarga los archivos ZIP desde el navegador y descomprímelos en esas carpetas.

## Verificación

El script cuenta las clases, detecta archivos dañados y duplicados dentro de cada conjunto y entre DS3 y DS4. Debe apuntar a una sola versión de DS3 (por ejemplo, la carpeta `original`):

```bash
python src/verificar_imagenes.py --ds3 data/raw/imagenes/ds3 --ds4 data/raw/imagenes/ds4
```

Escribe `data/processed/verificacion_imagenes.txt` y `data/processed/duplicados_ds3_ds4.csv`.

## Limitaciones

- Los dos conjuntos tienen fondos controlados o proceden de la web, así que el modelo puede fallar con fotos tomadas en la calle. La brecha entre la prueba de DS3 y la externa en DS4 mide ese efecto.
- La prueba externa tiene pocas imágenes y las clases están desbalanceadas; sus resultados deben leerse con cautela.
- El modelo no tiene una clase para objetos que no son residuos y puede responder con alta confianza ante ellos.

## Uso responsable

La aplicación advierte al usuario que no suba fotos con personas. Los esquemas de contenedores son orientativos y no sustituyen las indicaciones de la municipalidad.
