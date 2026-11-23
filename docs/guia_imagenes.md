# Guía de datos de imágenes (DS3 y DS4)

Las imágenes **no se suben al repositorio** (peso y licencias). Esta guía deja listo el material para la Fase 5 (clasificación de imágenes). Todo lo marcado **[VERIFICAR]** se confirma con la salida del script de verificación.

## 1. Qué descargar
| Dataset | Uso | Dónde | Notas |
|---|---|---|---|
| **DS3** Garbage Classification V2 | entrenamiento y validación | Kaggle: `sumn2u/garbage-classification-v2` | 10 clases; trae 3 versiones (original, 256 px, 384 px). **Elige una sola versión** para el entrenamiento. Licencia y particiones **[VERIFICAR]** |
| **DS4** TrashNet | prueba externa (6 clases comunes) | Kaggle: `feyzazkefe/trashnet` o GitHub `garythung/trashnet` | 2 527 imágenes según la bibliografía **[VERIFICAR]** |
| Alternativa sin Kaggle | solo si DS3 no se puede descargar | Hugging Face: `TrashBusters/combined` | 6 clases; licencia y particiones **[VERIFICAR]** |

## 2. Dónde guardarlas
```
data/raw/imagenes/ds3/   <- la versión elegida, con una carpeta por clase
data/raw/imagenes/ds4/   <- TrashNet, con una carpeta por clase
```
(`data/raw/` ya está ignorada por Git.)

## 3. Descarga con la API de Kaggle (opcional)
1. En Kaggle: *Settings → API → Create New Token* descarga `kaggle.json`. **No lo subas a Git ni lo compartas.**
2. Colócalo en `%USERPROFILE%\.kaggle\kaggle.json` (Windows) o `~/.kaggle/kaggle.json` (Linux/macOS).
3. `pip install kaggle` y luego:
```bash
kaggle datasets download -d sumn2u/garbage-classification-v2 -p data/raw/imagenes/ds3 --unzip
kaggle datasets download -d feyzazkefe/trashnet -p data/raw/imagenes/ds4 --unzip
```
Si no tienes cuenta o falla, descarga el ZIP desde el navegador y descomprímelo en esas carpetas.

## 4. Verificar (V5 y V6)
Primero mira qué carpetas quedaron (puede haber un nivel extra o las 3 versiones) y apunta `--ds3` a **la carpeta de la versión elegida**:
```bash
python src/verificar_imagenes.py --ds3 data/raw/imagenes/ds3 --ds4 data/raw/imagenes/ds4
```
Si aparecen varias versiones mezcladas, vuelve a ejecutarlo apuntando a una sola. El script informa: clases y conteos, imágenes dañadas, tamaños, duplicados dentro de cada conjunto y **cuántas imágenes de DS4 también están en DS3** (V6). Las coincidencias quedan en `data/processed/duplicados_ds3_ds4.csv` para excluirlas de la prueba externa.

## 5. Qué pasa después
- La **partición train/val/test estratificada** (semilla 42, sin duplicados entre particiones) y el mapeo de clases DS3→TrashNet se hacen en la **Fase 5**, con los nombres de carpeta reales.
- El entrenamiento se hace en **Google Colab** (GPU gratuita). Puedes ejecutar este mismo script allí si prefieres no descargar nada a tu PC.

## 6. Ética y uso responsable
- Citar la fuente y la licencia de cada dataset en el informe; **no redistribuir** las imágenes.
- Los datasets tienen fondos controlados y fotos de objetos: el modelo puede fallar con fotos reales de la calle (cambio de dominio); se mide con DS4.
- La app mostrará un aviso de que no se suban fotos con personas.
