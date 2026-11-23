# REGISTRO DE RESULTADOS REALES

> **Archivo vivo.** Aquí se guardan **solo** los resultados que el usuario obtuvo ejecutando el código y pegó en el chat. Es la fuente única de cifras para el informe y la exposición. **La IA no debe escribir ninguna cifra que no esté aquí.**
>
> Reglas:
> 1. Cada fila lleva su **origen** (notebook y celda, o comando) y su **fecha**.
> 2. Mientras no haya dato real, la celda dice `[RESULTADO REAL PENDIENTE]`.
> 3. Si un resultado se repite con otra configuración, se **agrega una fila nueva**, no se sobrescribe la anterior (se conserva el historial de experimentos).
> 4. Marcar con ⭐ el modelo ganador de cada módulo y justificar la elección debajo de la tabla.

---

## 0. Datos usados (verificados por el usuario)

| Conjunto | Fuente (URL o entidad) | Fecha de descarga | Filas/imágenes | Licencia | Observaciones |
|---|---|---|---|---|---|
| DS1 What a Waste (países) | https://datacatalog.worldbank.org/search/dataset/0039597 | 2026-11-21 (día de ejecución) | 217 filas × 51 columnas | CC-BY-4.0 (según ficha; V8 pendiente) | V1 y V2 hechas (ver 0c) |
| DS2 DSNY Monthly Tonnage | https://data.cityofnewyork.us/d/ebb7-mvp5 | 2026-11-21 (día de ejecución) | 25 355 filas × 12 columnas (1990-01 a 2026-10) | `[PENDIENTE]` (sin licencia en la ficha) | V3 hecha; unidad por confirmar (ver 0c) |
| DS3 Garbage Classification V2 | https://www.kaggle.com/datasets/sumn2u/garbage-classification-v2 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | Verificar V5 |
| DS4 TrashNet | https://github.com/garythung/trashnet | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | Verificar V6 (duplicados con DS3) |
| DS5 XL-Sum (es) | https://huggingface.co/datasets/csebuetnlp/xlsum | `[PENDIENTE]` | `[PENDIENTE]` | CC BY-NC-SA 4.0 (según ficha) | Verificar V7 |
| DS6 MLSUM (es) | https://huggingface.co/datasets/GEM/mlsum | `[PENDIENTE]` | `[PENDIENTE]` | Solo investigación no comercial (según ficha) | Verificar V7 |
| DS7 What a Waste 2.0 (texto) | enlace en `C3` | `[PENDIENTE]` | — | `[PENDIENTE]` | Solo demostración |

*(Los enlaces y licencias provienen de las fichas; los conteos y fechas los registra el usuario tras descargar. Hasta entonces permanecen `[PENDIENTE]`.)*

## 0b. Entorno de ejecución del usuario (Fase 1)

| Elemento | Valor real | Origen | Fecha |
|---|---|---|---|
| Python | 3.13.6 | `python --version` | 2026-11-21 |
| Versiones instaladas (fijadas en `requirements.txt`) | streamlit 1.67.0, pandas 3.0.6, numpy 2.3.2, plotly 7.1.0, scikit-learn 1.9.1, xgboost 3.4.1, joblib 1.5.1, matplotlib 3.11.2, seaborn 0.13.2, pillow 12.3.0, pytest 9.0.1 | `python src/fijar_versiones.py` | 2026-11-21 |
| Arranque de la app | El servidor de Streamlit inició en `localhost:8501` sin errores en consola | `streamlit run app/main.py` | 2026-11-21 |
| Instalación de `notebook` y ejecución de `01_prediccion.ipynb` | `notebook==7.6.5` instalado y fijado; `jupyter nbconvert --to notebook --execute --inplace` terminó sin error y escribió `notebooks\01_prediccion.ipynb` (148 606 bytes, con salidas). Avisos sin consecuencia: bucle de eventos de Windows (zmq) y kernel local sin cifrado (TCP) | 2026-11-21 |
| Pestaña «Predicción» en la app real (Streamlit 1.67.0) | El usuario confirma que se ve bien (captura del 2026-11-22). Se leen: aviso con error típico ≈ 0.44 kg/hab/día y MAPE ≈ 37 % (coincide con el meta); una simulación con región SSF dio 0.59 kg/hab/día, banda 0.14 a 1.03 y 1 245 038 t/año, con comparación contra el promedio de la región SSF (n = 48); la barra lateral marca Predicción con ✅ |
| `streamlit skills` | El usuario lo ejecutó: instaló `.agents\skills\developing-with-streamlit` (enlace simbólico del entorno; no se versiona). Aviso de la consola sobre websockets 17.3 y uvicorn 0.34.0 (cabeceras no ASCII con proxy inverso): no afecta el uso local |
| Pestaña «Clustering» en la app real (Streamlit 1.67.0) | Captura del 2026-11-23: la pestaña carga, la barra lateral marca Predicción y Clustering con ✅, el aviso de Silhouette 0.219 aparece, y el selector «¿Qué quieres explorar?» se ve. **Error** en el modo «País del dataset»: «El módulo de clustering falló: '<' not supported between instances of 'float' and 'str'». El usuario indica que todo lo demás funcionaba |
| Pestaña «Clustering», modo «País del dataset», tras la corrección | Captura del 2026-11-23 con Albania seleccionada: Clúster con «Generación inter…» (el nombre aparecía cortado), 79 países en el grupo, ingreso y región UMC · ECS, descripción del grupo, y tabla de valores del país frente a la mediana del grupo y la global (generación 1.04, 0.99 global y 1.18 del grupo; orgánico 51.4 %; papel y cartón 9.9 %; plástico 9.6 %; vidrio 4.5 %; metal 4.8 %; otros 15.21 %) |
| País con nombre vacío en `clustering_paises.csv` | Un país: `TWN` (ingreso HIC, región EAS) |
| Aspecto de la interfaz en el navegador | El usuario confirma que ve las 5 pestañas | Navegador, `localhost:8501` | 2026-11-21 |
| TensorFlow instalable en Python 3.13 | Indicio favorable, no concluyente: la simulación resolvió las dependencias de tensorflow (keras>=3.12.0, requests, etc.) sin errores visibles; el usuario pegó solo las últimas líneas (sin la línea final "Would install"). Se confirmará con la instalación real en la Fase 5 | `pip install tensorflow --dry-run` | 2026-11-21 |

## 0c. Verificación y EDA de datos tabulares (Fase 2 Parte A; origen: `verificacion_ds1_ds2.txt`, `log_preparacion.txt` y salida de `eda_tabular.py`, 2026-11-21)

| Ítem | Resultado real |
|---|---|
| V1 DS1: forma | (217, 51); 10 columnas de texto y 41 numéricas; no existe columna de generación per cápita (se deriva) |
| V1 DS1: vacíos | cobertura por área geográfica (total, rural, urbana) 100 %; `waste_treatment_anaerobic_digestion_percent` 99 %; `..._waterways_marine_percent` 98 %; cobertura rural/urbana "de residuos" y "de hogares" 94–96 %; cobertura rural "de población" 89 %; `waste_treatment_other_percent` 88 % |
| V2 DS1: duplicados y años | 217 `iso3c` únicos, 0 duplicados, 0 vacíos. **No hay columna de año de referencia** (solo `where_where_is_this_data_measured`, texto): declarar la limitación |
| DS1 procesado | 41 columnas renombradas; `gpc_kg_hab_dia` calculable en 215 de 217 países; 217 × 52 columnas |
| `gpc_kg_hab_dia` (kg/hab/día) | n=215; media 1.034; desv. 0.714; mín 0.102; p25 0.465; mediana 0.875; p75 1.387; máx 3.794 |
| Mediana de gpc por grupo de ingreso | HIC 1.502; UMC 0.834; LMC 0.467; LIC 0.44 |
| Países por grupo de ingreso | HIC 81; UMC 56; LMC 47; LIC 33 |
| `gdp` (unidades del dataset) | n=216; media 22 645.9; desv. 22 663.6; mín 822.6; p25 4 799.8; mediana 13 465.9; p75 35 911.6; máx 117 335.6 |
| V3 DS2: forma y columnas | (25 355, 12): MONTH, BOROUGH, COMMUNITYDISTRICT, REFUSETONSCOLLECTED, PAPERTONSCOLLECTED, MGPTONSCOLLECTED, RESORGANICSTONS, SCHOOLORGANICTONS, LEAVESORGANICTONS, XMASTREETONS, OTHERORGANICSTONS, BOROUGH_ID |
| V3 DS2: fechas | formato crudo `AAAA / MM`; 100 % interpretables; rango 1990-01 a 2026-10; 4 meses sin ninguna fila (1990-02 a 1990-05) |
| V3 DS2: distritos | `COMMUNITYDISTRICT` toma 18 valores (numéricos, se repiten entre boroughs); filas por mes entre 3 y 59 |
| V3 DS2: unidades | `[VERIFICAR]`. Mediana de REFUSE por fila = 4 061.6 y máx = 10 413.9. La suma anual de refuse queda entre 2.71 millones (1995) y 3.41 millones (2004) en 1993–2025; es coherente con toneladas por mes, pero falta contrastar con un reporte mensual PDF de DSNY |
| DS2 procesado | 77 685 filas largas tras eliminar 23 735 de 101 420 por toneladas vacías; serie de ciudad 1990-01 a 2026-10 con 4 meses sin datos; `n_distritos` por mes entre 3 y 59 |
| DS2: columnas no usadas | `XMASTREETONS`, `BOROUGH_ID`, `COMMUNITYDISTRICT` (esta última sí se usa para el código de distrito) |
| EDA DS2: meses con vacío por material | refuse 4; paper 38; mgp 39; organics 185 (de 442 meses) |
| EDA DS2: toneladas por mes | refuse: n=438, media 245 446, mín 72, mediana 249 864, máx 318 839 · paper: n=404, media 25 399, mediana 25 595, máx 40 157 · mgp: n=403, media 20 502, mediana 20 823, máx 33 479 · organics: n=257, media 2 644, mediana 1 329, máx 15 587 |
| EDA DS2: 2019 → 2020 (suma anual) | refuse 2 984 431 → 3 122 079; mgp 302 842 → 352 541; organics 44 263 → 12 432 (2021: 4 854; 2022: 24 225) |
| EDA DS2: otras observaciones | 1990–1992 con refuse parcial y paper/mgp/organics sin datos; mgp cae a 41 180 en 2003 (204 887 en 2002; 190 171 en 2004); organics sube a 62 195 (2024) y 127 581 (2025) |
| DS2: cobertura de distritos (máx. 59) sostenida desde | ciudad y refuse: 1992-01 (18 meses incompletos antes o durante); paper: 2004-04 (134); mgp: 2004-04 (60); organics: 2024-10 (417) |
| DS1: 5 menores `gpc_kg_hab_dia` | Lesotho (LMC) 0.102; Timor-Leste (LMC) 0.138; Lao PDR (LMC) 0.145; Nepal (LIC) 0.167; Ethiopia (LIC) 0.179 |
| DS1: 5 mayores `gpc_kg_hab_dia` | Puerto Rico (HIC) 3.290; Monaco (HIC) 3.336; Faeroe Islands (HIC) 3.422; Bermuda (HIC) 3.467; Virgin Islands (U.S.) (HIC) 3.794 |
| DS1: completitud % de columnas | 100: `poblacion`, `gdp`, `iso3c`, `pais`, `region_id`, `income_id`; 99: `gpc_kg_hab_dia`, `residuos_total_ton_anio`; 79–81: las 6 de composición `comp_*` (paper_cardboard, food_organic_waste, plastic, other = 81; glass, metal = 79); 83: `especial_e_waste_tons_year`; 58: `trat_recycling_pct`; 54: `especial_hazardous_waste_tons_year`; 48: `especial_medical_waste_tons_year`; 43: `trat_unaccounted_for_pct`; 42: `cobertura_total_percent_of_population`; 34: `especial_construction_and_demolition_waste_tons_year` |
| Ejecución | `preparar` y `eda_tabular.py` corrieron sin errores con los datos reales; se generaron 8 figuras en `docs/figuras/` (2026-11-21) |

## 0d. Fase 2 Parte B: ejecución del usuario (2026-11-21)

| Ítem | Resultado real |
|---|---|
| Instalación de `datasets` | `datasets==5.2.0` se instaló sin errores en Python 3.13.6 (con `huggingface-hub` 2.4.0 como dependencia) y `fijar_versiones.py` lo fijó en `requirements.txt` |
| `preparar_textos.py` v1, XL-Sum | Falló. Con `csebuetnlp/xlsum` / `spanish`: «Dataset scripts are no longer supported, but found xlsum.py». Con la rama `refs/convert/parquet`: «BuilderConfig 'spanish' not found. Available: ['default']» |
| `preparar_textos.py` v1, MLSUM | Falló. Con `GEM/mlsum` / `es`: «Dataset scripts are no longer supported, but found mlsum.py». Con la rama `refs/convert/parquet`: «BuilderConfig 'es' not found. Available: ['default']» |
| `preparar_textos.py` v2, XL-Sum (test) | Cargó `spanish/test/0000.parquet` de la rama parquet: 4 763 filas, columnas `id, url, title, summary, text`. Con palabras de residuos: 192 (4.0 %). Palabras por texto (media) 765; por resumen de referencia (media) 27.4. Muestra de 500, de ellas 192 de residuos |
| `preparar_textos.py` v2, MLSUM (test) | Cargó **dos** archivos: `es/challenge_test_covid/0000.parquet` y `es/test/0000.parquet` (se mezclaron por error): 15 304 filas, columnas `gem_id, gem_parent_id, text, topic, url, title, date, target, references`. Con palabras de residuos: 789 (5.2 %). Palabras por texto (media) 828; por resumen (media) 22.3. Muestra de 500, **todas** de residuos. Esta salida queda invalidada por la mezcla y se corrige en la v3 |
| `textos_residuos.csv` (v2) | 1 000 filas (500 por fuente). Sustituible tras la reejecución de la v3 |
| `preparar_textos.py` v3, XL-Sum | Sin cambios respecto a la v2: 4 763 artículos de test, 192 con palabras de residuos (4.0 %); muestra de 500 con 192 de residuos |
| `preparar_textos.py` v3, MLSUM | Cargó solo `es/test/0000.parquet`: 13 366 filas (coherente con las ≈13 400 de `C3`). Con palabras de residuos: 699 (5.2 %). Palabras por texto (media) 798; por resumen (media) 22.0. Muestra de 500 con 250 de residuos |
| `textos_residuos.csv` (v3) | 1 000 filas (500 por fuente); sustituye al de la v2. `revision_filtro.csv` regenerado (50 artículos, sin rellenar todavía) |
| Aviso del Hub | «You are sending unauthenticated requests to the HF Hub» (se puede definir `HF_TOKEN`, opcional) |
| `verificar_imagenes.py`, DS3 y DS4 | 0 imágenes legibles y 0 dañadas en `data/raw/imagenes/ds3` y `ds4`: todavía no se habían descargado las imágenes |

## 0e. Revisión del filtro de residuos (PRELIMINAR; revisor: Claude, IA; 2026-11-21)

Criterio: `relevante_manual` = 1 si el **tema principal** del artículo son los residuos, la basura, el reciclaje o la contaminación por plástico. **Limitación:** la revisión usó solo el extracto de 300 caracteres de `revision_filtro.csv` (no el artículo completo ni la palabra clave que activó el filtro) y la hizo una sola persona/IA; el equipo no la ha validado.

| Ítem | Resultado |
|---|---|
| Artículos revisados | 50 (25 de XL-Sum y 25 de MLSUM), todos marcados `es_residuos = 1` por el filtro |
| Relevantes (tema principal) | 3 de 50 = **6 %** (XL-Sum 2 de 25; MLSUM 1 de 25); intervalo de Wilson al 95 %: 2.1 % a 16.2 % |
| Sensibilidad por confianza | 2 relevantes con confianza alta; 10 artículos dudosos (confianza baja). Si todos los dudosos fueran relevantes: 12 de 50 = 24 %; si ninguno: 2 de 50 = 4 % |
| Relevantes encontrados | «Islas de basura marina» (XL-Sum), «¿Qué tan malo es el plástico?» (XL-Sum), consumo responsable con granel y reutilización (MLSUM, dudoso) |
| Patrón observado | La mayoría de los artículos marcados trata de política, deporte, cultura u otros temas; las palabras clave aparecen como mención incidental (p. ej. cadáver hallado junto a contenedores de basura) |

## 1. Predicción (regresión) — Fase 3 (origen: `m1_resumen.txt`, ejecución del usuario, 2026-11-21)

Variable objetivo: `gpc_kg_hab_dia` (derivada) · Países usados: 215 de 217 (2 sin objetivo); entrenamiento 172 y prueba 43 (20 % estratificado por `income_id`, semilla 42) · Validación: cruzada repetida 5×3 sobre entrenamiento · Conjunto elegido por la regla fijada de antemano: **A0** (`gdp`, `poblacion`, `region_id`) · Métrica de decisión: RMSE (kg/hab/día) · Versiones: scikit-learn 1.9.1, XGBoost 3.4.1.

**RMSE de validación cruzada por modelo y conjunto** (mejor escala del objetivo por celda; baseline = promedio por grupo de ingreso, 0.496):

| Modelo | A0 | A | B |
|---|---|---|---|
| KNN | 0.507 | 0.494 | 0.513 |
| MLP | 0.468 | 0.467 | 0.489 |
| Polinómica g=2 (Ridge) | 0.469 | 0.459 | 0.475 |
| Random Forest | 0.501 | 0.506 | 0.510 |
| Ridge (lineal) | 0.472 | 0.459 | 0.466 |
| SVR | 0.460 | 0.463 | 0.474 |
| XGBoost | 0.525 | 0.528 | 0.525 |

Mejor global: conjunto A, Polinómica g=2 (Ridge), objetivo lineal, RMSE_cv 0.459 ± 0.093; umbral (mejor + 1 desv. est.) 0.553; mejor RMSE_cv por conjunto: A 0.459, A0 0.46, B 0.466.

**Modelos ajustados con `GridSearchCV` (conjunto A0, objetivo lineal)**

| Modelo | RMSE_cv sin ajustar | RMSE_cv ajustado | Desv. est. | Hiperparámetros elegidos |
|---|---|---|---|---|
| SVR ⭐ | 0.460 | 0.460 | 0.094 | C=1, epsilon=0.1 |
| MLP | 0.468 | 0.467 | 0.086 | alpha=0.01, capas (32, 16) |
| Polinómica g=2 (Ridge) | 0.469 | 0.469 | 0.088 | alpha=10 |

**Métricas en el conjunto de prueba (n = 43; kg/hab/día salvo MAPE en %, R² y r adimensionales)**

| Modelo | RMSE | MAE | MAPE % | R² | Pearson r | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|
| Baseline: promedio por grupo de ingreso | 0.501 | 0.319 | 43.789 | 0.398 | 0.661 | 2026-11-21 | |
| SVR (C=1, epsilon=0.1) | 0.443 | 0.268 | 36.729 | 0.529 | 0.736 | 2026-11-21 | ⭐ |
| MLP (alpha=0.01, (32, 16)) | 0.477 | 0.297 | 36.076 | 0.454 | 0.704 | 2026-11-21 | |
| Polinómica g=2 (Ridge, alpha=10) | 0.445 | 0.291 | 40.909 | 0.525 | 0.733 | 2026-11-21 | |
| Mejor global sin ajustar (Polinómica g=2, conjunto A) | 0.450 | 0.289 | 40.117 | 0.514 | 0.731 | 2026-11-21 | |

Ridge (lineal), KNN, Random Forest y XGBoost solo se evaluaron en validación cruzada (tabla anterior); no se midieron en prueba porque no llegaron al top 3 del conjunto elegido.

**Prueba sin los 5 extremos** (VIR, BMU, FRO, MCO, PRI; n de prueba no impreso):

| Modelo | RMSE | MAE | MAPE % | R² | Pearson r |
|---|---|---|---|---|---|
| Baseline | 0.442 | 0.288 | 43.682 | 0.333 | 0.679 |
| Ganador entrenado con todo | 0.420 | 0.250 | 36.871 | 0.397 | 0.689 |
| Ganador entrenado sin extremos | 0.401 | 0.241 | 36.580 | 0.449 | 0.705 |

**Errores por grupo de ingreso (prueba)**

| Grupo | n | RMSE ganador | RMSE baseline | MAE ganador |
|---|---|---|---|---|
| HIC | 16 | 0.459 | 0.582 | 0.323 |
| LIC | 7 | 0.165 | 0.158 | 0.133 |
| LMC | 9 | 0.700 | 0.724 | 0.391 |
| UMC | 11 | 0.210 | 0.208 | 0.171 |

**Importancia por permutación (prueba, aumento del RMSE):** `gdp` 0.277 ± 0.051; `poblacion` 0.069 ± 0.026; `region_id` 0.018 ± 0.023.

**Coeficientes del modelo lineal (A0; numéricas estandarizadas):** `region_id_NAC` 0.675; `gdp` 0.441; `region_id_EAS` −0.235; `poblacion` −0.180; `region_id_SAS` −0.159; `region_id_MEA` −0.102; `region_id_SSF` −0.077; `region_id_LCN` −0.063; `region_id_ECS` −0.040. Las 7 regiones observadas son EAS, ECS, LCN, MEA, NAC, SAS y SSF.

**Justificación del ganador:** SVR tuvo el menor RMSE de validación cruzada entre los 3 modelos ajustados del conjunto elegido (0.460 frente a 0.467 y 0.469), pero la diferencia es menor que la desviación entre pliegues (≈ 0.09): los tres son indistinguibles con estos datos. En prueba, SVR mejora al baseline en RMSE (0.443 frente a 0.501), MAE (0.268 frente a 0.319) y R² (0.529 frente a 0.398).

## 2. Series temporales — Fase 6

Serie (S1, S2, S3…): `[PENDIENTE]` · Frecuencia: `[PENDIENTE]` · Periodo: `[PENDIENTE]` · Partición cronológica: `[PENDIENTE]`

| Modelo | RMSE | MAE | MAPE % | Parámetros | Origen | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|
| Baseline ingenuo | [RESULTADO REAL PENDIENTE] | | | | | | |
| Ingenuo estacional | [RESULTADO REAL PENDIENTE] | | | | | | |
| SARIMAX (con indicadores) / Prophet / statsforecast | [RESULTADO REAL PENDIENTE] | | | | | | |
| LSTM (si hay datos suficientes) | [RESULTADO REAL PENDIENTE] | | | | | | |

**Justificación del ganador:** `[PENDIENTE]`

## 3. Clasificación de imágenes — Fase 5

Dataset: `[PENDIENTE]` · Clases: `[PENDIENTE]` · Particiones train/val/test: `[PENDIENTE]`

| Variante | Accuracy | Macro-F1 | Precision (macro) | Recall (macro) | Épocas | Origen | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Desde cero | [RESULTADO REAL PENDIENTE] | | | | | | | |
| Solo capa clasificadora (feature extraction) | [RESULTADO REAL PENDIENTE] | | | | | | | |
| Fine-tuning | [RESULTADO REAL PENDIENTE] | | | | | | | |

**Prueba externa (DS4 TrashNet en las 6 clases comunes; y fotos propias si las hay):**

| Variante | Conjunto externo | Nº de imágenes | Accuracy | Macro-F1 | Diferencia frente al test de DS3 (6 clases) | Fecha |
|---|---|---|---|---|---|---|
| [RESULTADO REAL PENDIENTE] | | | | | | |

**Métricas por clase (modelo ganador):** `[RESULTADO REAL PENDIENTE]` · **Matriz de confusión:** `[archivo/figura PENDIENTE]`

## 4. Clustering — Fase 4 (origen: `m4_resumen.txt`, ejecución del usuario, 2026-11-22)

Variante: **A (países, DS1)** · Unidades: 160 países con las 7 variables completas, de 217 (57 descartados por algún faltante) · Variables: `gpc_kg_hab_dia`, `comp_food_organic_waste_pct`, `comp_paper_cardboard_pct`, `comp_plastic_pct`, `comp_glass_pct`, `comp_metal_pct`, `comp_other_pct` · Preprocesamiento: `log1p` + estandarización en un `Pipeline` · scikit-learn 1.9.1 · Vacíos % de las variables: gpc 0.9; composición 18.9 a 21.2; cobertura total de población 57.6; reciclaje 42.4.

**Mejor configuración elegible por algoritmo** (regla: 3 a 8 clústeres, ruido ≤ 10 %, tamaño mínimo 5, mayor Silhouette):

| Algoritmo | Nº clústeres | Silhouette | Davies-Bouldin | Calinski-Harabasz | % ruido | Tamaño mínimo | Parámetros | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|---|---|
| K-Means | 4 | 0.219 | 1.548 | 34.312 | 0.0 | 16 | k = 4 | 2026-11-22 | ⭐ |
| Agglomerative (Ward) | 4 | 0.207 | 1.648 | 31.850 | 0.0 | 12 | k = 4 | 2026-11-22 | |
| GMM (diag) | 3 | 0.177 | 2.210 | 31.623 | 0.0 | 38 | k = 3 | 2026-11-22 | |
| DBSCAN | sin configuración elegible (ver abajo) | | | | | | | 2026-11-22 | |

Mejor Silhouette sin restricciones: DBSCAN (eps 0.8, min_samples 3), 7 clústeres, Silhouette 0.491, Davies-Bouldin 0.667, Calinski-Harabasz 28.635, **82.5 % de ruido** y tamaño mínimo 3: el Silhouette se calcula solo sobre el 17.5 % de los países (origen: `m4_resultados.csv`). DBSCAN tuvo 5 configuraciones con al menos 2 clústeres: las 4 de 3 a 8 clústeres tienen entre 48.1 % y 82.5 % de ruido; la única con ≤ 10 % de ruido (eps 2.2, min_samples 3) tiene 2 clústeres, Silhouette 0.209 y tamaño mínimo 3.

**K-Means por K** (inercia / Silhouette): 2: 855.795 / 0.219 · 3: 756.610 / 0.204 · 4: 674.758 / 0.219 · 5: 628.353 / 0.164 · 6: 563.574 / 0.175 · 7: 515.115 / 0.196 · 8: 483.727 / 0.171 · 9: 458.724 / 0.175 · 10: 434.414 / 0.173.

**Estabilidad** (30 submuestras del 80 %): ARI 0.662 ± 0.277, mínimo 0.250.

**Contraste externo** del ganador (referencia, no verdad absoluta):

| Etiqueta | ARI | NMI | Homogeneidad | Completitud | V-Measure |
|---|---|---|---|---|---|
| `income_id` | 0.180 | 0.254 | 0.245 | 0.264 | 0.254 |
| `region_id` | 0.075 | 0.151 | 0.128 | 0.185 | 0.151 |

**Sensibilidad:** CLR de la composición: ARI frente al principal 0.314 (4 clústeres) · semillas 0 a 9: ARI medio 0.963, mínimo 0.931 · conjunto ampliado con cobertura y reciclaje: solo 44 países, 4 clústeres, ARI frente al principal en esos países 0.231, Silhouette 0.231.

**Perfiles del ganador** (mediana de las variables originales):

| Clúster | n países | gpc (kg/hab/día) | Orgánico % | Papel y cartón % | Plástico % | Vidrio % | Metal % | Otros % |
|---|---|---|---|---|---|---|---|---|
| 0 | 17 | 2.22 | 24.00 | 28.50 | 5.40 | 4.60 | 6.29 | 13.13 |
| 1 | 79 | 1.18 | 41.47 | 15.00 | 13.50 | 5.50 | 3.80 | 12.10 |
| 2 | 48 | 0.59 | 59.79 | 8.00 | 10.00 | 2.32 | 2.00 | 11.05 |
| 3 | 16 | 0.83 | 16.80 | 8.35 | 10.29 | 3.10 | 3.50 | 41.07 |

**Clúster por grupo de ingreso** (HIC / LIC / LMC / UMC): 0: 16 / 0 / 1 / 0 · 1: 46 / 1 / 9 / 23 · 2: 0 / 11 / 20 / 17 · 3: 6 / 4 / 2 / 4.
**Clúster por región** (EAS / ECS / LCN / MEA / NAC / SAS / SSF): 0: 4 / 7 / 3 / 0 / 3 / 0 / 0 · 1: 16 / 32 / 18 / 9 / 0 / 1 / 3 · 2: 9 / 3 / 10 / 11 / 0 / 4 / 11 · 3: 4 / 5 / 1 / 0 / 0 / 0 / 6.
**Países más cercanos al centro:** 0: Norway, Liechtenstein, Guam, Canada, Cayman Islands, Denmark, United States, Puerto Rico · 1: Mexico, Netherlands, Dominican Republic, Italy, Brunei Darussalam, Antigua and Barbuda, Austria, Lebanon · 2: Morocco, Sri Lanka, China, Iran Islamic Rep., Ecuador, Colombia, West Bank and Gaza, Bolivia · 3: Hungary, Grenada, Senegal, Belgium, Marshall Islands, Togo, New Zealand, United Kingdom.
**Asignación por centroide más cercano:** coincide con las etiquetas en el 100.0 % de los países.

**Perfiles interpretados:** `[PENDIENTE]` (nombres y políticas en la Parte B; ver D54 de `ESTADO`).

## 5. Resumen de texto — Fase 7

Conjuntos de evaluación: E1 XL-Sum (es) y E2 MLSUM (es) — tamaño de cada muestra y semilla: `[PENDIENTE]` · Precisión del filtro por tema de residuos: `[PENDIENTE]` · Tokenizador de ROUGE: `[PENDIENTE]`

| Método | ROUGE-1 | ROUGE-2 | ROUGE-L | Ratio de compresión | Tiempo (s) | Origen | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Lead-3 (baseline) | [RESULTADO REAL PENDIENTE] | | | | | | | |
| TextRank (extractivo) | [RESULTADO REAL PENDIENTE] | | | | | | | |
| Modelo abstractivo HF: `[nombre verificado]` | [RESULTADO REAL PENDIENTE] | | | | | | | |

## 6. Pruebas de integración — Fase 8

| Prueba | Resultado | Fecha |
|---|---|---|
| Instalación desde cero siguiendo el manual | [RESULTADO REAL PENDIENTE] | |
| Los 5 módulos abren sin error | [RESULTADO REAL PENDIENTE] | |
| Entradas inválidas manejadas sin caída | [RESULTADO REAL PENDIENTE] | |
| Tiempo de arranque de la app | [RESULTADO REAL PENDIENTE] | |
