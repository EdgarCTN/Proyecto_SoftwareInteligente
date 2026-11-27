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

## 2. Series temporales — Fase 6 Parte A (origen: `m2_resumen.txt`, ejecución real del usuario con `python src/entrenar_series.py`; Windows, Python 3.13.6, statsmodels 0.15.0, TensorFlow 2.21.0; 2026-11-23)

Frecuencia: mensual (`MS`). Se modela **toneladas por día** y todas las métricas están en **toneladas por mes**. Partición cronológica: prueba = últimos 12 meses; 4 ventanas móviles de validación de 12 meses antes de ella (RMSE val = media de las 4 ventanas; desv. = desviación estándar entre ventanas). Regla del ganador fijada antes de ver resultados (D77). Tiempos de ejecución de la reejecución del usuario en la rama correcta: S1 384 s, S2 121 s, S3 128 s (la ejecución anterior tardó S1 288 s, S2 179 s, S3 186 s; en total unos 10 minutos). S4 (orgánicos) no se modela (D76). La prueba ADF se reporta por serie; SARIMAX usa una diferencia simple y una estacional (d = 1, D = 1).

### S1 Basura (refuse): 1992-01 a 2026-10 (418 meses)

ADF (p-valor): {'serie': 0.22118522652020806, 'dif_1': 6.632479056455282e-06, 'dif_1_y_12': 1.8487901637764702e-13}

Configuración elegida por AIC/AICc con datos anteriores a la primera validación: SARIMAX {'orden': (2, 1, 1), 'estacional': (0, 1, 1, 12), 'exog': ['covid', 'organicos_programa']} (AIC -1158.3) | ETS elegido: {'error': 'add', 'trend': None, 'damped': False, 'seasonal': 'mul'} (AICc -1273.5). La de ETS está en `m2_resumen.txt`.

| Modelo | RMSE val | desv. RMSE val | MAE val | MAPE val % | RMSE prueba | MAE prueba | MAPE prueba % | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Ingenuo (último valor) | 14469.92 | 6734.82 | 11705.12 | 4.88 | 13172.48 | 10188.81 | 4.31 |  |
| Media móvil 12 m | 12726.95 | 3911.32 | 10215.18 | 4.26 | 13458.58 | 10946.58 | 4.58 |  |
| Ingenuo estacional | 12478.89 | 4943.95 | 10291.42 | 4.21 | 9101.32 | 7425.80 | 3.04 |  |
| ETS | 10304.55 | 5803.87 | 8319.82 | 3.37 | 8785.38 | 7505.56 | 3.08 | ⭐ |
| SARIMAX | 11441.88 | 8206.26 | 9819.97 | 3.97 | 9258.68 | 7950.00 | 3.26 |  |
| SARIMAX sin COVID en el entrenamiento (solo análisis) | 8331.34 | 2239.28 | 6700.06 | 2.73 | 9168.40 | 7923.69 | 3.24 |  |
| LSTM | 10747.49 | 3556.96 | 8581.84 | 3.56 | 12797.77 | 9581.63 | 4.08 |  |

**Ganador:** ETS. Mejora del RMSE de prueba del ganador frente al ingenuo estacional: 3.5 %. Convergencia del modelo final: None (`None` = no aplica). Pronóstico de 12 meses (2026-11 a 2027-10): primer mes 247923.6 ton (intervalo: 228988.5 a 265775.4); último mes 251041.2 ton (intervalo: 226710.4 a 275330.2) — valores de `m2_pronostico_S1.csv` tras reejecutar con el script corregido (D83); sustituyen a los intervalos de las dos ejecuciones anteriores; tabla completa en `data/processed/m2_pronostico_S1.csv`.

### S2 Papel: 2004-04 a 2026-10 (271 meses)

ADF (p-valor): {'serie': 0.039124877145881275, 'dif_1': 0.000759457747672763, 'dif_1_y_12': 6.437103470126484e-08}

Configuración elegida por AIC/AICc con datos anteriores a la primera validación: SARIMAX {'orden': (1, 1, 1), 'estacional': (0, 1, 1, 12), 'exog': ['covid', 'organicos_programa']} (AIC -509.1) | ETS elegido: {'error': 'add', 'trend': 'add', 'damped': True, 'seasonal': 'mul'} (AICc -588.4). La de ETS está en `m2_resumen.txt`.

| Modelo | RMSE val | desv. RMSE val | MAE val | MAPE val % | RMSE prueba | MAE prueba | MAPE prueba % | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Ingenuo (último valor) | 1882.75 | 409.50 | 1484.01 | 5.80 | 2452.06 | 1950.72 | 7.94 |  |
| Media móvil 12 m | 2085.84 | 714.69 | 1749.66 | 6.99 | 2481.16 | 1954.66 | 7.79 |  |
| Ingenuo estacional | 1732.55 | 689.00 | 1422.75 | 5.78 | 2362.15 | 1596.97 | 6.36 |  |
| ETS | 1690.90 | 642.83 | 1449.20 | 5.83 | 2116.50 | 1578.55 | 6.33 |  |
| SARIMAX | 1384.27 | 318.74 | 1132.13 | 4.55 | 2224.96 | 1622.17 | 6.48 | ⭐ |
| SARIMAX sin COVID en el entrenamiento (solo análisis) | 1264.65 | 178.54 | 1000.58 | 4.03 | 2265.33 | 1652.54 | 6.61 |  |
| LSTM | 2082.85 | 774.37 | 1729.55 | 6.93 | 2440.25 | 1936.10 | 7.78 |  |

**Ganador:** SARIMAX. Mejora del RMSE de prueba del ganador frente al ingenuo estacional: 5.8 %. Convergencia del modelo final: False (`None` = no aplica). Pronóstico de 12 meses (2026-11 a 2027-10): primer mes 24771.0 ton (intervalo: 21723.0 a 27819.0); último mes 25892.0 ton (intervalo: 22348.0 a 29436.0); tabla completa en `data/processed/m2_pronostico_S2.csv`.

### S3 Metal, vidrio y plástico (MGP): 2004-04 a 2026-10 (271 meses)

ADF (p-valor): {'serie': 0.6121090304254807, 'dif_1': 0.007889248069544377, 'dif_1_y_12': 5.623798953439335e-08}

Configuración elegida por AIC/AICc con datos anteriores a la primera validación: SARIMAX {'orden': (2, 1, 1), 'estacional': (1, 1, 1, 12), 'exog': ['covid', 'organicos_programa']} (AIC -511.6) | ETS elegido: {'error': 'mul', 'trend': None, 'damped': False, 'seasonal': 'mul'} (AICc -582.0). La de ETS está en `m2_resumen.txt`.

| Modelo | RMSE val | desv. RMSE val | MAE val | MAPE val % | RMSE prueba | MAE prueba | MAPE prueba % | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Ingenuo (último valor) | 1174.90 | 173.55 | 986.37 | 4.01 | 2227.23 | 1731.44 | 7.49 | ⭐ |
| Media móvil 12 m | 1551.23 | 947.75 | 1345.08 | 5.62 | 2240.65 | 1783.38 | 7.65 |  |
| Ingenuo estacional | 1580.84 | 953.69 | 1350.18 | 5.57 | 2344.53 | 1512.05 | 6.35 |  |
| ETS | 1342.38 | 701.68 | 1122.50 | 4.63 | 2146.27 | 1454.77 | 6.26 |  |
| SARIMAX | 1444.53 | 877.58 | 1251.32 | 5.12 | 2157.75 | 1333.44 | 5.82 |  |
| SARIMAX sin COVID en el entrenamiento (solo análisis) | 1235.64 | 596.31 | 1045.19 | 4.33 | 2193.53 | 1396.06 | 6.08 |  |
| LSTM | 1425.22 | 860.51 | 1245.78 | 5.15 | 2211.92 | 1718.03 | 7.42 |  |

**Ganador:** Ingenuo (último valor). Mejora del RMSE de prueba del ganador frente al ingenuo estacional: 5.0 %. Convergencia del modelo final: None (`None` = no aplica). Pronóstico de 12 meses (2026-11 a 2027-10): primer mes 23967.0 ton (intervalo: NaN a NaN); último mes 24766.0 ton (intervalo: NaN a NaN); tabla completa en `data/processed/m2_pronostico_S3.csv`.

**Efecto de quitar el periodo COVID del entrenamiento (SARIMAX; RMSE en ton/mes, salida del script):** S1 validación 11 442 → 8 331 (−27.2 %), prueba 9 259 → 9 168 (−1.0 %); S2 validación 1 384 → 1 265 (−8.6 %), prueba 2 225 → 2 265 (+1.8 %); S3 validación 1 445 → 1 236 (−14.5 %), prueba 2 158 → 2 194 (+1.7 %). Porcentajes calculados por la IA sobre las cifras pegadas. Este modelo no compite (D78).

**Lectura (calculada sobre las cifras de arriba; una sola ventana de prueba de 12 meses y 4 ventanas de validación con mucha dispersión):**
1. **S1:** ETS gana por la regla (RMSE de validación 10 305, un 4.1 % menor que el del siguiente, LSTM). Su ventaja de prueba sobre el ingenuo estacional es de 3.5 %, menor que la dispersión entre ventanas (desv. 5 804).
2. **S2:** SARIMAX gana en validación (18.1 % menos RMSE que ETS) pero en prueba ETS tiene menor RMSE (2 116 frente a 2 225); SARIMAX supera al ingenuo estacional en 5.8 %. **El SARIMAX final de S2 no convergió** (`convergio` = False): su pronóstico e intervalo van con esa reserva.
3. **S3:** gana el ingenuo (último valor), 12.5 % menos RMSE de validación que ETS; en prueba ETS (2 146) y SARIMAX (2 158) quedan por debajo del ingenuo (2 227). Los siete modelos quedan entre 2 146 y 2 345 en prueba y la dispersión entre ventanas es grande (174 a 954): **ningún modelo supera con claridad al baseline**. El pronóstico de S3 no tiene intervalo.
4. **LSTM:** no gana en ninguna serie; en prueba queda peor que el ingenuo estacional en S1 (12 798 frente a 9 101) y S2 (2 440 frente a 2 362) y algo mejor en S3 (2 212 frente a 2 345).
5. **MAPE de prueba del ganador:** S1 3.08 %, S2 6.48 %, S3 7.49 %.
6. La unidad ton/mes sigue sin contrastar con un reporte de DSNY (P14). El modelo supone `covid` = 0 y `organicos_programa` = último valor en el futuro.

7. **Validación frente a prueba (calculado de las tablas):** en las 4 ventanas de validación cada ganador mejora al ingenuo estacional en RMSE, MAE y MAPE (S1: RMSE 10 305 frente a 12 479; S2: 1 384 frente a 1 733; S3, con el ingenuo: 1 175 frente a 1 581). En la ventana de prueba la mejora solo aparece en el RMSE (3.5 %, 5.8 % y 5.0 %); en MAE y MAPE los tres ganadores quedan peor que el ingenuo estacional (S1: MAE 7 506 frente a 7 426, MAPE 3.08 frente a 3.04; S2: 1 622 frente a 1 597 y 6.48 frente a 6.36; S3: 1 731 frente a 1 512 y 7.49 frente a 6.35). La prueba es una sola ventana de 12 meses.
8. **Quiebre COVID (análisis, no candidato):** SARIMAX sin el periodo COVID en el entrenamiento tiene menor RMSE de validación que SARIMAX con él en las tres series (S1 8 331 frente a 11 442; S2 1 265 frente a 1 384; S3 1 236 frente a 1 445), pero en prueba la diferencia es pequeña y de signo mixto (S1 9 168 frente a 9 259; S2 2 265 frente a 2 225; S3 2 194 frente a 2 158). Por la regla fijada de antemano no compite; incluirlo como candidato después de ver la validación sería una decisión posterior a los resultados.
9. **Reproducibilidad:** la reejecución en la rama correcta dio exactamente las mismas métricas, configuraciones y pronósticos puntuales que la ejecución registrada antes, pero **distintos intervalos de S1** (primer mes 228 550 a 268 303 frente a 229 020 a 267 013), porque los intervalos de ETS con componentes multiplicativos se simulan sin semilla. Corregido en la Fase 6 A (D83). Tras reejecutar con el script nuevo, `m2_pronostico_S1.csv` trae los intervalos de la línea anterior, y el pronóstico recalculado por la IA desde `serie_S1.joblib` (ETS, 418 observaciones, última fecha 2026-10, escala 8 238.38) coincide con ese CSV con diferencia máxima de 0.00 ton/mes en pronóstico, límite inferior y límite superior.

**Reproducibilidad:** `m2_resumen.txt` y `data/processed/m2_resultados.csv` (todas las métricas por serie, modelo y ventana) están en el proyecto del usuario. Las figuras `docs/figuras/m2_*.png` las generó el script; la IA no las ha visto.

## 3. Clasificación de imágenes — Fase 5 Parte A (origen: `m3_resumen.txt` y salida de las celdas 4 y 5 de `03_imagenes_colab.ipynb`, ejecución del usuario en Colab, 2026-11-23)

Dataset de entrenamiento: **DS3 Garbage Classification V2**, 12 259 imágenes legibles (0 dañadas) en 10 clases: `battery, biological, cardboard, clothes, glass, metal, paper, plastic, shoes, trash`. Existen tres versiones con las mismas 12 259 imágenes (`original`, `standardized_256`, `standardized_384`); **subcarpeta usada: `original`** (`SUB_DS3 = "original"`, confirmada por el usuario con su celda 2; DS4: `SUB_DS4 = "dataset-resized"`). Tamaños más frecuentes en el inventario: 512×384 (2 218), 225×225 (1 336) y 400×533 (1 024): coherente con la versión `original` (no estandarizada). Licencia de DS3 y DS4: `[PENDIENTE]` (P23).

**Limpieza (V6):** DS3: 12 duplicados eliminados y 27 imágenes con etiquetas en conflicto descartadas → **12 220** imágenes. Particiones estratificadas (semilla 42): **train 8 554 · val 1 833 · test 1 833**. Conteo por clase (train/val/test): battery 526/113/112 · biological 489/105/105 · cardboard 983/211/210 · clothes 1 324/284/284 · glass 1 206/258/259 · metal 651/139/140 · paper 932/199/200 · plastic 1 113/239/238 · shoes 1 014/217/217 · trash 316/68/68. DS4 (TrashNet, carpeta `dataset-resized`): 2 527 imágenes legibles, 6 clases (paper 594, glass 501, plastic 482, metal 410, cardboard 403, trash 137); 2 duplicados y 10 con etiqueta en conflicto eliminados, y **2 238 coinciden con DS3 (MD5 o hash perceptual idéntico) y se excluyen** → **277** imágenes quedan como prueba externa.

| Variante | Accuracy (val) | Macro-F1 (val) | Accuracy (test) | Macro-F1 (test) | Épocas ejecutadas | Parámetros entrenables | Segundos | Origen | Fecha | ⭐ |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 desde cero (CNN propia) | 0.4283 | 0.4160 | 0.4239 | 0.4194 | 9 | 242 474 | 339 | `m3_resumen.txt` | 2026-11-23 | |
| V2 MobileNetV2, solo clasificador | 0.8931 | 0.8832 | 0.9013 | 0.8938 | 11 | 12 810 | 287 | `m3_resumen.txt` | 2026-11-23 | |
| V3 MobileNetV2, fine-tuning (últimas 30 capas) | 0.9225 | 0.9127 | 0.9149 | 0.9099 | 12 | 1 523 530 | 341 | `m3_resumen.txt` | 2026-11-23 | ⭐ |

**Justificación del ganador:** regla fijada antes de entrenar (macro-F1 de validación; empate ≤ 0.005 → menos parámetros entrenables). V3 supera a V2 por 0.0295 en macro-F1 de validación (> 0.005), así que no hubo empate. Una sola ejecución por variante (una semilla): no se midió la variabilidad entre ejecuciones. V1 se detuvo en la época 9 con EarlyStopping (patience 4 sobre `val_loss`) y su macro-F1 de validación es 0.4160.

**Métricas por clase del ganador (test DS3, n = 1 833; macro avg: precision 0.908, recall 0.916, F1 0.910; accuracy 0.915):**

| Clase | Precision | Recall | F1 | Soporte |
|---|---|---|---|---|
| battery | 0.981 | 0.946 | 0.964 | 112 |
| biological | 0.990 | 0.962 | 0.976 | 105 |
| cardboard | 0.873 | 0.919 | 0.896 | 210 |
| clothes | 0.993 | 0.996 | 0.995 | 284 |
| glass | 0.942 | 0.819 | 0.876 | 259 |
| metal | 0.762 | 0.936 | 0.840 | 140 |
| paper | 0.899 | 0.845 | 0.871 | 200 |
| plastic | 0.871 | 0.878 | 0.874 | 238 |
| shoes | 0.991 | 0.986 | 0.988 | 217 |
| trash | 0.776 | 0.868 | 0.819 | 68 |

**Prueba externa (ganador V3; decisión restringida a las 6 clases comunes; emparejamiento TrashNet→DS3 por nombre idéntico: glass, paper, cardboard, plastic, metal, trash):**

| Conjunto | Nº de imágenes | Accuracy | Macro-F1 | Fecha |
|---|---|---|---|---|
| Test de DS3 restringido a las 6 clases | 1 115 | 0.8762 | 0.8694 | 2026-11-23 |
| DS4 (solo las 277 no coincidentes con DS3) | 277 | 0.6101 | 0.5739 | 2026-11-23 |
| **Brecha (DS3 − DS4)** | | 0.2661 | 0.2955 | 2026-11-23 |

DS4 por clase (precision / recall / F1 / soporte): glass 0.986 / 0.622 / 0.762 / 111 · paper 0.487 / 0.826 / 0.613 / 23 · cardboard 0.625 / 0.938 / 0.750 / 16 · plastic 0.289 / 0.419 / 0.342 / 31 · metal 0.217 / 1.000 / 0.357 / 10 · trash 0.811 / 0.500 / 0.619 / 86 (macro avg: precision 0.569, recall 0.717, F1 0.574; weighted F1 0.643). Fotos propias: no se usaron.

**Lectura (no son cifras nuevas):** (1) DS3 ya contiene gran parte de TrashNet: 2 238 de 2 527 imágenes de DS4 coinciden con DS3. Por eso la prueba externa es **pequeña (277) y desbalanceada** (glass y trash suman 197; metal solo 10), y sus métricas por clase con pocas imágenes (metal, cardboard, paper) son poco fiables. (2) Si quedaran imágenes casi duplicadas con hash distinto (el criterio es hash idéntico), la exactitud en DS4 estaría inflada y la brecha real sería mayor `[no verificado]`. (3) El test de DS3 con 6 clases (0.8762) es menor que el de 10 clases (0.9149) porque se quitan clases con F1 alto (clothes, shoes, battery, biological). (4) «trash» de TrashNet y `trash` de DS3 se emparejaron por nombre; que signifiquen lo mismo es un supuesto.

**Confusiones principales** (leídas de `matriz_confusion_test` y `matriz_ds4` de `imagenes_meta.json`, filas = real): en test de DS3, glass→plastic 21, glass→metal 21, paper→cardboard 18, cardboard→paper 11, plastic→glass 8. En DS4: glass→plastic 20, glass→metal 20, trash→paper 15, trash→metal 14, trash→plastic 10.

**Comprobación de los artefactos (2026-11-23, entorno de la IA con Keras 3.15.1):** `clasificador_imagenes.keras` carga (entrada 224×224×3, salida 10, 2 270 794 parámetros), `clases_imagenes.json` coincide con `clases` del meta, y accuracy recalculada desde las matrices de confusión coincide con el meta (test DS3 n = 1 833: 0.9149; DS4 n = 277: 0.6101). La carga en el entorno local del usuario (Python 3.13, P12) está sin verificar.

**Observación informal de la Fase 5 Parte B (no es una métrica; 3 imágenes sintéticas en el entorno de la IA, 2026-11-23):** el modelo siempre reparte probabilidad entre las 10 clases. Con ruido aleatorio a color respondió `paper` 0.876 (luego `trash` 0.065, `metal` 0.033); con gris uniforme, `plastic` 0.279, `metal` 0.203, `trash` 0.176; con blanco, `trash` 0.451, `cardboard` 0.258, `paper` 0.102. Una imagen que no es un residuo puede recibir confianza alta; la app lo avisa y no hay clase «ninguno».

**Verificación en el PC del usuario (Windows, Python 3.13.6, TensorFlow 2.21.0, Keras 3.15.1, 2026-11-22 noche, hora de Lima):** `tests/test_imagenes.py`: 5 pruebas pasan (incluye cargar el `.keras` y predecir). `src/comprobar_modelo_imagenes.py` cargó el modelo (entrada `(None, 224, 224, 3)`, salida `(None, 10)`, 10 clases) pero falló al imprimir por la codificación de la consola (cp1252); corregido en la Fase 5 B. Repetido después en el PC del usuario (2026-11-22, 23:27, hora de Lima): imprime la suma de probabilidades con una imagen de prueba (gris uniforme) = 1.0000 y termina con «OK: el modelo carga y predice en este entorno». `requirements.txt` quedó con `tensorflow==2.21.0` tras `fijar_versiones.py`. La app abrió y la pestaña de imágenes respondió.

**Primera foto real en la app (captura del usuario; no es una métrica):** una foto de trozos de madera apilados (el archivo se llama `Como-se…irarla.jpg`, 188.4 KB) se clasificó como **Cartón con 94.5 %** (Papel 2.2 %, Plástico 0.8 %) y sugirió el contenedor azul «Papel y cartón» (esquema del proyecto). La madera no es ninguna de las 10 clases: confirma D72 (sin clase «ninguno», con confianza alta).

**Reproducibilidad:** Colab con TensorFlow 2.21.0, Keras 3.13.2, NumPy 2.4.6, scikit-learn 1.6.1, Pillow 11.3.0. Recarga del `.keras`: diferencia máxima de probabilidades 0.0; tamaño del `.keras`: 21.9 MB. **Matriz de confusión:** `docs/figuras/m3_matriz_confusion.png` y `m3_matriz_ds4.png` (generadas por el notebook; confirmar que están en el proyecto).

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

## 5. Resumen de texto — Fase 7 Parte A (origen: `m5_resumen.txt` y celdas 4, 6 y 11 de `notebooks/05_resumen.ipynb`, ejecución real del usuario en Colab; Tesla T4; 2026-11-24)

**Condiciones.** Ejecución completa (no es la prueba rápida): E1 XL-Sum (es, test) n = 500 y E2 MLSUM (es, test) n = 500, muestras de `textos_residuos.csv` (250 de residuos y 250 de otros en MLSUM; 192 y 308 en XL-Sum), semilla 42. Tokenizador de ROUGE: propio. Librerías reportadas: numpy 2.4.6, pandas 2.2.3, torch 2.14.1+cu130, transformers 5.22.1, sentencepiece 0.2.2, rouge-score 0.1.2, huggingface_hub 1.33.0. Modelo abstractivo: `csebuetnlp/mT5_multilingual_XLSum`, revisión `2437a524effdbadc327ced84595508f1e32025b3` (última modificación 2022-08-13), float32. Longitud media de las referencias en estas muestras: XL-Sum 27.0 y MLSUM 22.3 palabras (calculado por la IA sobre el CSV subido).

### Verificaciones (celdas 4 y 6)

| Verificación | Resultado real |
|---|---|
| El modelo existe en el Hub | Sí; `licencia_ficha` y `etiquetas_licencia` salieron vacías (la API no las expone; ver la fila siguiente) |
| Licencia y uso del modelo (origen distinto: ficha del modelo leída por la IA con búsqueda web, 2026-11-24) | La ficha declara `cc-by-nc-sa-4.0` en el campo `licenses`, indica que se entrenó con `csebuetnlp/xlsum` y recomienda entrada de 512 tokens, `max_length=84` y `no_repeat_ngram_size=2`; el fragmento leído se cortó antes de `num_beams`, así que **`num_beams=4` sigue sin confirmarse**. Los pesos pesan 2.33 GB |
| Tokenizador por defecto de `rouge-score` | `pequeña` frente a `pequeño`: ROUGE-1 = 0.500 con el tokenizador por defecto y 0.000 con el propio (el por defecto parte las palabras con tilde o ñ). Con textos idénticos ambos dan 1.000 |
| ROUGE propio frente a `rouge-score` (mismo tokenizador, 50 pares Lead-2 de XL-Sum) | Diferencia máxima 0.0 en ROUGE-1 y en ROUGE-L (ROUGE-2 no se contrastó) |

### E1 — XL-Sum (en dominio para el abstractivo) · n = 500

| Método | ROUGE-1 | ROUGE-2 | ROUGE-L | desv. ROUGE-L | Palabras del resumen | Ratio de compresión | s/doc | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Lead-1 (sensibilidad) | 0.1905 | 0.0457 | 0.1494 | 0.0961 | 17.3 | 0.0328 | 0.0023 | |
| **Lead-2 (baseline principal)** | 0.2144 | 0.0402 | 0.1484 | 0.0690 | 43.4 | 0.0818 | 0.0012 | |
| Lead-3 (sensibilidad) | 0.2044 | 0.0378 | 0.1364 | 0.0546 | 68.1 | 0.1247 | 0.0012 | |
| TextRank-1 (sensibilidad) | 0.2108 | 0.0364 | 0.1483 | 0.0705 | 33.2 | 0.0557 | 0.0031 | |
| **TextRank-2 (principal)** | 0.2021 | 0.0379 | 0.1408 | 0.0578 | 63.7 | 0.1079 | 0.0031 | |
| TextRank-3 (sensibilidad) | 0.1832 | 0.0372 | 0.1265 | 0.0482 | 93.2 | 0.1582 | 0.0030 | |
| **Abstractivo (mT5 XL-Sum)** | 0.2902 | 0.1064 | 0.2232 | 0.1448 | 16.7 | 0.0321 | 0.3998 | ⭐ |

### E2 — MLSUM (fuera de dominio) · n = 500

| Método | ROUGE-1 | ROUGE-2 | ROUGE-L | desv. ROUGE-L | Palabras del resumen | Ratio de compresión | s/doc | ⭐ |
|---|---|---|---|---|---|---|---|---|
| Lead-1 (sensibilidad) | 0.1907 | 0.0470 | 0.1492 | 0.1037 | 24.1 | 0.0390 | 0.0015 | |
| **Lead-2 (baseline principal)** | 0.2049 | 0.0530 | 0.1504 | 0.0907 | 51.4 | 0.0842 | 0.0035 | |
| Lead-3 (sensibilidad) | 0.1978 | 0.0569 | 0.1435 | 0.0771 | 77.3 | 0.1239 | 0.0015 | |
| TextRank-1 (sensibilidad) | 0.2140 | 0.0511 | 0.1556 | 0.1029 | 44.3 | 0.0623 | 0.0038 | |
| **TextRank-2 (principal)** | 0.1904 | 0.0502 | 0.1383 | 0.0751 | 83.6 | 0.1193 | 0.0065 | |
| TextRank-3 (sensibilidad) | 0.1642 | 0.0467 | 0.1201 | 0.0606 | 120.1 | 0.1729 | 0.0039 | |
| **Abstractivo (mT5 XL-Sum)** | 0.1999 | 0.0440 | 0.1582 | 0.1003 | 18.4 | 0.0304 | 0.4189 | ⭐ |

Tiempos: el abstractivo se midió en la GPU Tesla T4 de Colab (≈ 0.40 y 0.42 s por documento); los extractivos, en la CPU de Colab. **No se midió el abstractivo en CPU ni en el PC del usuario.**

### Ganador y comparación con Lead-2

ROUGE-L medio entre E1 y E2: Lead-2 0.1494 · TextRank-2 0.1395 · **Abstractivo 0.1907** → ganador por la regla fijada (D88): **Abstractivo**.

| Fuente | Método | Δ ROUGE-L frente a Lead-2 | IC 95 % (bootstrap pareado, 1000, semilla 42) | ¿Excluye 0? |
|---|---|---|---|---|
| XL-Sum | TextRank-2 | −0.0076 | [−0.0132, −0.0018] | sí |
| XL-Sum | Abstractivo | +0.0748 | [+0.0627, +0.0873] | sí |
| MLSUM | TextRank-2 | −0.0121 | [−0.0216, −0.0034] | sí |
| MLSUM | Abstractivo | +0.0077 | [−0.0019, +0.0176] | **no** |

### Subconjuntos «residuos» (ROUGE-L; informativos, sin intervalos)

| Subconjunto | n | Lead-2 | TextRank-2 | Abstractivo |
|---|---|---|---|---|
| XL-Sum, con palabra clave | 192 | 0.1430 | 0.1332 | 0.1978 |
| MLSUM, con palabra clave | 250 | 0.1434 | 0.1367 | 0.1570 |
| XL-Sum, estricto (≥ 3 apariciones) | 39 | 0.1299 | 0.1306 | 0.1878 |
| MLSUM, estricto (≥ 3 apariciones) | 53 | 0.1524 | 0.1297 | 0.1588 |

### Lecturas (escritas por la IA a partir de las cifras anteriores; D94)

1. El abstractivo gana por la regla, pero **la ventaja viene de E1**, donde el modelo se entrenó con XL-Sum (Δ +0.0748, IC que excluye 0). En E2, fuera de dominio, su diferencia con Lead-2 (+0.0077) tiene un IC que incluye 0: no se distingue de un baseline que copia las primeras oraciones.
2. TextRank-2 queda algo por debajo de Lead-2 en las dos fuentes (diferencias de 0.008 y 0.012, con IC que excluyen 0). Son diferencias pequeñas.
3. Hay mucha dispersión entre documentos (desviación de ROUGE-L de 0.06 a 0.14), y los ROUGE absolutos son bajos para todos los métodos porque las referencias son de una sola frase: se comparan entre métodos, no con otros trabajos.
4. **Las longitudes difieren mucho:** el abstractivo produce 17–18 palabras; Lead-2 y TextRank-2, de 43 a 84. Como la F1 depende de la longitud, la comparación principal está en parte condicionada por ella. Observación **exploratoria, no fijada de antemano y sin IC**: Lead-1, de longitud parecida al abstractivo, obtiene 0.1494 (E1) y 0.1492 (E2) frente a 0.2232 y 0.1582.
5. La sensibilidad no cambia la regla (no se usa para elegir), pero muestra que en E2 todos los métodos quedan en una banda estrecha de ROUGE-L (0.1201 a 0.1582) y que en ROUGE-1 TextRank-1 (0.2140) supera al abstractivo (0.1999).
6. Los subconjuntos siguen el mismo patrón, pero los estrictos tienen 39 y 53 artículos y no se calcularon intervalos: no sacar conclusiones propias sobre residuos.

### Revisión cualitativa (celda 11; 6 ejemplos, 3 por fuente, semilla 42)

Revisor: Claude (IA), a partir de los extractos impresos (≈ 200–300 caracteres del artículo) y de la referencia, no de los artículos completos; el usuario los encontró «coherentes» sin detallar casos. **Limitación:** 6 ejemplos no permiten estimar una tasa de errores.

| Fuente · ejemplo | Observación |
|---|---|
| XL-Sum · meteorito en Managua | Frase poco coherente («un cráter de roca espacial de 12 metros de profundidad se desintegró»); el dato de 12 m no se puede comprobar con lo impreso |
| XL-Sum · niños de Irak | Atribuye el informe a «Save the Children»; la referencia lo atribuye a **War Child** → contradice la referencia |
| XL-Sum · jubilación en Alemania | No menciona la edad de jubilación (el tema del inicio del artículo) y afirma que Merkel «llegó a la presidencia… el pasado septiembre», algo que no aparece en lo impreso |
| MLSUM · Márquez Cabrera | Casi copia la primera oración; aparece un carácter extraño («destino à Chicago») |
| MLSUM · Preysler | Copia exacta de la primera oración; omite lo que resume la referencia (vacaciones en Grecia con Vargas Llosa) |
| MLSUM · propuestas del PSOE | **Invierte los papeles** («atraer al PSOE» en lugar de «atraer a Podemos», como dice el texto impreso) y añade «presidente de la oposición española, Pedro Sánchez», que no aparece en lo impreso. La referencia de este ejemplo (Aguirre imputada) no corresponde al inicio del artículo |

Resumen: en 2 de 6 hay contradicciones comprobables con lo impreso, en otros 2 hay afirmaciones que lo impreso no respalda, y en 2 el abstractivo copia la primera oración. Es evidencia para el aviso de «puede inventar datos» de la interfaz y del informe.

### Pruebas en el PC del usuario — Fase 7 Parte B (capturas y salida de pip pegadas por el usuario; 2026-11-24)

- **Instalación** de `requirements-abstractivo.txt` en Windows con Python 3.13: correcta. Instalados: torch 2.14.1 (el archivo descargado pesó 124.1 MB), transformers 5.22.1, sentencepiece 0.2.2, tokenizers 0.23.3, safetensors 0.8.0, regex 2026.11.25, networkx 3.7, sympy 1.14.0, mpmath 1.3.0, typer 0.29.3 y shellingham 1.5.4. Ya estaban: numpy 2.3.2 y huggingface-hub 2.4.0.
- **Interfaz (capturas):** las cinco pestañas con ✅; «Resumen» con el texto de ejemplo y TextRank de 3 oraciones (264 palabras → 83; tiempo 0.0 s); «Evaluación y límites» con la tabla y las cuatro frases de bootstrap leídas de `resumen_meta.json`. En las capturas el método abstractivo figura como no disponible; no consta si se tomaron antes de instalar las librerías.
- **Defectos vistos en las capturas (corregidos, D101):** el gráfico de ROUGE-L salía **apilado** (sumaba las dos fuentes y el eje llegaba a ≈ 0.38, lo que engaña) y el selector de archivos mostraba «200 MB per file» aunque el módulo acepta 1 MB.
- **`resumen_meta.json` recibido:** sus 14 filas de evaluación coinciden con la tabla de `m5_resumen.txt` a 4 decimales y trae las claves que usa la app (comprobado por la IA).
- **`python -m pytest tests/test_texto.py tests/test_resumen.py` en el PC (2026-11-27; Windows, Python 3.13.6, pytest 8.3.4): 17 passed in 14.55 s** (8 de `test_texto.py` y 9 de `test_resumen.py`; la novena, la de las barras agrupadas, exige plotly, así que se ejecutó con plotly real). tiempo y memoria del abstractivo en CPU: ver las dos viñetas finales de esta subsección.
- **Método abstractivo en la app (2026-11-27, CPU, Windows; captura y consola pegadas por el usuario):** con el texto de ejemplo (264 palabras, 4 párrafos) produjo una sola oración de 18 palabras: «La gestión de los residuos sólidos urbanos es una de las etapas más complejas de la vida moderna.». La interfaz mostró **1289.4 s**, pero ese cronómetro arrancaba **antes** de cargar el modelo, así que incluye la descarga (≈ 2.33 GB) y la carga: **no es el tiempo de generación** (defecto corregido, D102). En la consola la barra «Loading weights» llegó a 284/284 en menos de un segundo, lo que sugiere que la descarga ya había terminado (inferencia de la IA, no verificada).
- **Lectura (IA) de ese resumen:** es fluido, pero la afirmación «una de las etapas más complejas de la vida moderna» **no aparece en el texto original** y solo recoge el tema general, no los pasos que describe el texto (separación, recolección, compost, relleno sanitario y comunicación). La pista de datos no respaldados dijo que todas las cifras y nombres aparecen en el original, porque solo revisa cifras y palabras con mayúscula: confirma el límite que ya anuncia la interfaz.
- **Avisos de la consola** (ninguno impidió el resultado; su efecto sobre la calidad no se comprobó): `transformers` indica que no ata `shared.weight` con `lm_head.weight` porque el checkpoint trae valores distintos; avisa de que `max_new_tokens` (84) prevalece sobre `max_length` (84) de la configuración del modelo; el Hub avisa de peticiones sin autenticar (`HF_TOKEN` es opcional y acelera descargas); y `uvicorn` avisa de un problema con `websockets 17.3` que solo afecta detrás de un proxy inverso.
- **Medición del abstractivo en el PC (`src/medir_abstractivo.py` corregido, 2026-11-27; salida pegada por el usuario):** equipo Windows 10 (10.0.19045), Python 3.13.6, 4 núcleos lógicos, 2 hilos de torch, sin GPU, `psutil` 7.2.2.

| Medida | Valor |
|---|---|
| Carga del modelo ya descargado | 13.5 s (14.8 s en la medición anterior) |
| Memoria residente tras cargarlo | 1398 MiB |
| Primera generación (calentamiento, no se promedia) | 31.8 s (38.6 s en la medición anterior) |
| Texto de ejemplo (264 palabras, 1 bloque), régimen estable | 14.84 s y 16.15 s |
| Ejemplo repetido 5 veces (1320 palabras, 5 bloques), 1 repetición | 77.28 s |
| Memoria al final: actual / pico | 2191 MiB / 2486 MiB |

Lecturas (IA): en este PC sin GPU el abstractivo tarda ≈ 15 s por bloque de unas 260 palabras (frente a ≈ 0.4 s por artículo en la T4 de Colab) y necesita ≈ 2.5 GiB de memoria como pico. Las 77.28 s del texto largo corresponden, por el código del procedimiento por bloques, a 5 llamadas por bloque más una final (≈ 13 s por llamada): es una inferencia, no se midió llamada por llamada. El pico se midió en el proceso del script, que también carga Streamlit y los módulos de la app.

- **Calidad del resumen por bloques (1 caso, texto repetido y por tanto artificial):** el resumen del texto de 5 bloques fue «La mayoría de los residuos sólidos de las grandes ciudades del mundo están en el riesgo de descomposición de basura.»: **no corresponde a lo que dice el texto** (no habla de «la mayoría» ni de «grandes ciudades del mundo») y la frase final es poco coherente. Con el texto de un bloque repitió la oración de la ejecución anterior (la afirmación sobre «las etapas más complejas de la vida moderna» que el texto no respalda). Un solo caso no permite estimar una tasa, pero coincide con la advertencia de la interfaz: resumir los resúmenes puede alejarse del texto.

## 6. Pruebas de integración — Fase 8

| Prueba | Resultado | Fecha |
|---|---|---|
| Instalación desde cero siguiendo el manual | [RESULTADO REAL PENDIENTE] | |
| Los 5 módulos abren sin error | Sí: las 6 pestañas (Inicio + 5 módulos) abren sin errores en el PC del usuario (Fase 8 A; captura) | 2026-11-27 |
| Entradas inválidas manejadas sin caída | Cubiertas por las pruebas automáticas de `tests/test_integracion.py` (texto vacío, corto o largo; archivo que no es imagen; composición > 100 %; extrapolación; metadatos inexistentes): pasan dentro de `46 passed` en el PC del usuario. No se probó la subida de archivos por interfaz | 2026-11-27 |
| Tiempo de arranque de la app | Medido con `src/medir_arranque.py` (3 repeticiones; ver la tabla de abajo) | 2026-11-27 |
| Seguridad y dependencias (paso 4 y 9 del checklist) | `git ls-files \| findstr kaggle` sale vacío tras `git rm --cached notebooks/kaggle.json` (aún sin commit confirmado); `grep -n statsmodels requirements.txt` → 1 comentario (línea 14) y 1 pin (línea 18) | 2026-11-27 |
| Todas las pruebas `pytest` en el PC del usuario | `python -m pytest -q` → 46 passed in 38.71s (Windows, Git Bash) | 2026-11-27 |

### Tiempo de ejecución de la página por pestaña — Fase 8 Parte A (captura del «Diagnóstico técnico» en el PC del usuario, 2026-11-27)

Estado de la captura: pestaña Predicción > «Países del dataset» con Perú elegido (es decir, tras interactuar con un control), sin foto subida en Imágenes y sin texto en Resumen. Cada cifra es **una sola lectura**, sin repeticiones.

| Pestaña | Segundos |
|---|---|
| Inicio | 0.01 |
| Predicción | 0.16 |
| Series temporales | 0.23 |
| Imágenes | 0.04 (sin foto cargada) |
| Clustering | 0.25 |
| Resumen | 0.11 |
| Suma | 0.80 (calculada a partir de las seis lecturas) |

Lectura (IA): con esos controles, una interacción vuelve a ejecutar las seis pestañas en unos 0.8 s en total, lo que respalda conservar `st.tabs` (D106). **No está medido** el caso con una foto cargada en Imágenes ni con un texto grande en Resumen, que son los que podrían encarecer cada interacción. Tampoco es el tiempo de arranque en frío (queda pendiente).

### Arranque de la app — Fase 8 Parte B (salida de `python src/medir_arranque.py` en el PC del usuario, 2026-11-27)

Tres repeticiones. «Proceso nuevo» usa `AppTest` (sin navegador); «servidor listo» es el tiempo hasta que `/_stcore/health` responde (no incluye abrir el navegador ni cargar TensorFlow). Todas: 0 excepciones y 0 errores.

| Repetición | Importar Streamlit (s) | 1.ª ejecución (s) | 2.ª ejecución (s) | Servidor listo (s) |
|---|---|---|---|---|
| 1 | 1.40 | 6.33 | 0.52 | 3.64 |
| 2 | 1.42 | 5.48 | 0.51 | 3.15 |
| 3 | 1.53 | 5.53 | 0.52 | 3.06 |
| Promedio (calculado a partir de las tres lecturas) | 1.45 | 5.78 | 0.52 | 3.28 |

Lectura (IA): la primera ejecución de la página tarda unos 5.5 a 6.3 s y las siguientes unos 0.5 s, coherente con los ≈ 0.8 s de la sección anterior. **No se midió por separado** qué parte de la primera ejecución corresponde a importar librerías y qué parte a la primera carga de modelos y datos; es probable que sean ambas, pero es una suposición. Solo tres repeticiones en un equipo, con caché de disco ya caliente tras la primera.

