# ESTRUCTURA DEL PROYECTO

> **Archivo vivo.** Describe cómo está organizado el repositorio y **qué debe cumplir cada archivo** (su "contrato"), para que cualquier fase escrita en una conversación distinta sea **compatible** con las demás sin necesidad de ver todo el código. La IA lo actualiza cuando se crean o cambian archivos y entrega el archivo completo.

**Leyenda (árbol de la sección 1):** ⬜ planificado · 🟡 entregado, sin validar · ✅ validado · ⚠️ con problemas

---

## 1. Árbol del proyecto (= contenido del zip)

La raíz `software_inteligente/` es a la vez la carpeta de trabajo, el repositorio Git y lo que se comprime para llevar al siguiente chat.

```
software_inteligente/
├── INDICE_PARA_IA.md · PROMPT_INICIO.md · LEEME_PRIMERO.md   (existen desde el inicio)
├── contexto/   PLAN_DE_FASES, C0, C1_tema_residuos_urbanos, C2, C3_datasets_del_proyecto,
│               modulos/ (M1, M2, M3, M3b, M4, M4b, M5)           (solo lectura)
├── estado/     ESTADO_PROYECTO, ESTRUCTURA_PROYECTO (este archivo), REGISTRO_RESULTADOS
│
│   ── A partir de aquí, lo crea la IA en las fases ──
├── app/
│   ├── __init__.py                   ✅ Fase 1 (también en modules/ y utils/)
│   ├── main.py                       🟡 Fase 1 (esqueleto, ya carga módulos dinámicamente) · Fase 8 (completo)
│   ├── modules/
│   │   ├── prediccion.py             🟡 Fase 3 B
│   │   ├── series_tiempo.py          🟡 Fase 6 B
│   │   ├── imagenes.py               🟡 Fase 5 B
│   │   ├── clustering.py             🟡 Fase 4 B
│   │   └── resumen.py                ⬜ Fase 7
│   └── utils/
│       ├── datos.py                  🟡 Fase 1
│       ├── graficos.py               🟡 Fase 1
│       └── modelos.py                🟡 Fase 1 (carga de artefactos + lectura de *_meta.json)
├── src/
│   ├── fijar_versiones.py            ✅ Fase 1 (fija en requirements.txt las versiones instaladas)
│   ├── preparar_datos.py             🟡 Fase 2 A (DS1 y DS2: descargar|verificar|preparar|todo) · Parte B: textos
│   ├── eda_tabular.py                🟡 Fase 2 A (EDA; figuras en docs/figuras/)
│   ├── entrenar_prediccion.py        🟡 Fase 3 A (mismo código del notebook 01, sin Jupyter)
│   ├── entrenar_clustering.py        🟡 Fase 4 A (mismo código del notebook 04, sin Jupyter)
│   ├── entrenar_series.py            🟡 Fase 6 A (mismo código del notebook 02, sin Jupyter)
│   ├── preparar_textos.py            🟡 Fase 2 B (DS5 y DS6 → textos_residuos.csv, log_textos.txt, revision_filtro.csv)
│   ├── verificar_imagenes.py         🟡 Fase 2 B (V5 y V6 de DS3 y DS4; duplicados_ds3_ds4.csv)
│   └── comprobar_modelo_imagenes.py  🟡 Fase 5 B (comprueba la carga del modelo en el entorno local)
├── notebooks/
│   ├── 01_prediccion.ipynb           🟡 Fase 3 A (entrena y compara; escribe models/prediccion_*, data/processed/m1_*, docs/figuras/m1_*.png)
│   ├── 02_series_tiempo.ipynb        🟡 Fase 6 A (local; mismo código que `src/entrenar_series.py`)
│   ├── 03_imagenes_colab.ipynb       🟡 Fase 5 A (Colab; sin ejecutar con datos reales)
│   ├── 04_clustering.ipynb           🟡 Fase 4 A (agrupa países; escribe models/clustering_*, data/processed/clustering_paises.csv, m4_*, docs/figuras/m4_*.png)
│   └── 05_resumen.ipynb              ⬜ Fase 7
├── models/                           (artefactos entrenados + *_meta.json)
├── data/
│   ├── raw/                          (descargas sin modificar: wab/, dsny/, texto/; no van al repo)
│   ├── processed/                    (paises_residuos.csv, dsny_distritos_mensual.csv, serie_ciudad_mensual.csv,
│   │                                  distritos_nyc_perfil.csv [opcional], textos_residuos.csv [no va al repo])
│   └── imagenes/
│       ├── train/ val/ test/         (DS3, por clase)
│       ├── externo_trashnet/         (DS4, solo las 6 clases comunes)
│       └── externo_propio/           (fotos propias, opcional)
├── tests/
│   ├── test_series_tiempo.py         🟡 Fase 6 B (5 pruebas; la de artefactos reales compara cada modelo guardado con su CSV y se omite si faltan los archivos)
│   ├── test_imagenes.py              🟡 Fase 5 B (5 pruebas; las del modelo se omiten si faltan TensorFlow o models/)
│   └── test_humo.py                  ⬜ Fase 8
├── docs/
│   ├── diccionario_datos.md          🟡 Fase 2 B (DS1 y DS2 con datos reales; textos e imágenes pendientes de ejecución)
│   ├── guia_imagenes.md              🟡 Fase 2 B
│   ├── figuras/                      🟡 Fase 2 A (PNG del EDA)
│   ├── manual_instalacion.md         ⬜ Fase 9
│   ├── manual_usuario.md             ⬜ Fase 9
│   ├── informe_tecnico.md            ⬜ Fases 10–11
│   └── exposicion.md                 ⬜ Fase 12
├── config.py                         🟡 Fase 1
├── requirements.txt                  🟡 Fase 1 (sin versiones hasta ejecutar src/fijar_versiones.py)
├── .gitignore                        🟡 Fase 1 (models/ NO se ignora)
└── README.md                         🟡 Fase 1
```

**Qué NO va en el zip que se lleva al siguiente chat:** ver `INDICE_PARA_IA.md`, sección 7 (la Fase 1 lo replica en `.gitignore`).

## 2. Convenciones (obligatorias en todas las fases)

1. **Rutas** siempre relativas a la raíz y centralizadas en `config.py` (`BASE_DIR`, `DATA_RAW`, `DATA_PROCESSED`, `MODELS_DIR`, `IMG_DIR`). Nada de rutas absolutas ni de usuario.
2. **Semilla** `RANDOM_STATE = 42` definida en `config.py`.
3. **Nombres** de archivos, funciones y variables en español, sin tildes ni ñ (`prediccion`, no `predicción`).
4. **La app nunca entrena**: solo carga artefactos de `models/` con `@st.cache_resource` y datos con `@st.cache_data`.
5. **Cada módulo** `app/modules/<nombre>.py` expone `render() -> None`, maneja sus errores con `st.error(...)` y no debe romper el resto de la app si falla.
6. **Artefactos con metadatos:** cada modelo guardado en `models/` tiene un archivo hermano `<nombre>_meta.json`. Es la **única fuente** de las métricas que muestra la app y el informe.
7. **Notebooks:** fijan la semilla, documentan cada paso y terminan guardando el artefacto y su `_meta.json`. Para Colab, las celdas se entregan separadas.
8. **Git:** un commit por fase con el mensaje `fase-N: descripción`.
9. **Idioma:** interfaz, comentarios, manuales e informe en español.
10. **Dependencias:** todo paquete nuevo se agrega a `requirements.txt`; las versiones se fijan con `python src/fijar_versiones.py` tras instalar (así no se inventan versiones).
11. **Carga de módulos:** `app/main.py` importa `app.modules.<modulo>` con `importlib` según `config.MODULOS`; si el archivo no existe muestra "en construcción". Ejecutar siempre desde la raíz: `streamlit run app/main.py`.

## 3. Formato de `*_meta.json`

```json
{
  "modulo": "prediccion",
  "modelo": "nombre legible del modelo ganador",
  "fecha": "AAAA-MM-DD",
  "dataset": "descripción y archivo de origen",
  "n_entrenamiento": 0,
  "n_prueba": 0,
  "parametros": {},
  "metricas": {"RMSE": null, "MAE": null, "MAPE": null, "R2": null},
  "features": [],
  "clases": [],
  "librerias": {"scikit-learn": "x.y.z"},
  "notas": "limitaciones relevantes"
}
```

**Campos adicionales de `prediccion_meta.json`** (Fase 3): `conjunto_variables` (A0, A o B), `objetivo_log` (bool), `metricas_cv`, `baseline` (métricas en prueba y de validación cruzada), `metricas_sin_extremos`, `extremos` (iso3c), `importancia_permutacion`, `referencias_app` (`por_ingreso` y `por_region`, cada una con media, mediana y n de `gpc_kg_hab_dia`), `rangos_variables` (min, p05, mediana, p95, max de las numéricas), `categorias` (valores de las categóricas), `gdp_por_ingreso` (min y max de `gdp` por grupo). `features` lista las columnas, en el orden y con los nombres que el Pipeline espera como `DataFrame`. Los valores de `metricas` salen del modelo entrenado solo con el 80 %; `prediccion_mejor.pkl` está reentrenado con todos los países.

**Salidas del módulo 1:** `data/processed/m1_resultados_cv.csv`, `m1_resultados_test.csv`, `m1_resumen.txt` y las figuras `docs/figuras/m1_comparacion_cv.png`, `m1_real_vs_predicho.png`, `m1_importancia.png`.

**Artefactos del módulo 4 (variante A, países):** `models/clustering_mejor.pkl` es un dict de joblib con `prep` (Pipeline log1p + StandardScaler ya ajustado), `centroides` (k × 7, en el espacio estandarizado), `ids_cluster` (lista de enteros en el mismo orden que los centroides), `variables` (las 7 columnas, en orden), `pca` (2 componentes ajustado sobre el espacio estandarizado), `algoritmo` y `parametros`. Un país nuevo se asigna al centroide más cercano de `prep.transform(df[variables])`. `models/clustering_meta.json` agrega: `variante`, `preprocesamiento`, `regla_seleccion`, `mejor_sin_restricciones`, `comparacion_algoritmos`, `estabilidad`, `contraste_externo`, `sensibilidad`, `paises_usados`, `paises_descartados`, `vacios_pct` y `perfiles` (por clúster: `n_paises`, `mediana` de las 7 variables, `ingreso`, `representativos`); `clases` lista los ids de clúster. `data/processed/clustering_paises.csv` tiene `iso3c, pais, income_id, region_id`, las 7 variables, `cluster`, `pc1`, `pc2`. `models/clustering_nombres.json` (lo escribe la IA tras ver los perfiles) mapea id de clúster a `{nombre, descripcion, politica}`. Salidas: `data/processed/m4_resultados.csv`, `m4_resumen.txt` y figuras `docs/figuras/m4_codo_silhouette.png`, `m4_dendrograma.png`, `m4_pca_clusters.png`, `m4_perfiles.png`.

**Artefactos del módulo 2 (Fase 6 Parte A; los genera `src/entrenar_series.py` o el notebook 02):** un modelo por serie (S1 `refuse`, S2 `paper`, S3 `mgp`; S4 no se modela). `models/serie_<id>.joblib` = diccionario con `id`, `tipo` (`ingenuo`, `media_movil`, `ingenuo_estacional`, `ets`, `sarimax` o `lstm`), `config`, `ultima_fecha` (`YYYY-MM`), `horizonte_max` (12), `exog_futuro` (`covid` = 0, `organicos_programa` = último valor), `unidad_modelo` (los modelos trabajan en **toneladas por día**: multiplicar por los días del mes) y, según el tipo: `modelo` + `escala` (ets, sarimax: se pronostica sobre la serie dividida por `escala` y se multiplica de vuelta), `ultimos_12_ton_dia` (baselines), o `keras` (nombres de `models/serie_<id>_lstm_<k>.keras`) + `escalador_min` + `escalador_max` + `look_back` + `ultimos_escalados` (lstm). `models/serie_meta.json`: campos comunes del contrato más `frecuencia` (`MS`), `horizonte_max`, `unidades` y `series` (por id: `nombre`, `columna`, `inicio`, `fin`, `n_meses`, `ganador`, `archivo_modelo`, `archivo_pronostico`, `metricas_test`, `metricas_validacion`, `mejora_rmse_test_vs_ingenuo_estacional_pct`, `tabla_modelos`, `config_sarimax`, `config_ets`, `adf_p_valor`, `intervalo`, `convergio`). `data/processed/m2_pronostico_<id>.csv` (`fecha`, `pronostico_ton_mes`, `inferior_ton_mes`, `superior_ton_mes`; los límites quedan vacíos si el ganador no da intervalo), `m2_resultados.csv` (todas las métricas por serie, modelo y ventana), `m2_resumen.txt`. Figuras: `docs/figuras/m2_eda_<id>.png`, `m2_pronostico_<id>.png`, `m2_comparacion.png`. Los objetos de statsmodels se guardan con joblib: la app debe usar la misma versión de statsmodels (`serie_meta.json` → `librerias`).

**Artefactos del módulo 3 (Fase 5 Parte A; los genera el notebook de Colab y se entregan en `salida_fase5.zip`):** `models/clasificador_imagenes.keras` (modelo completo con aumento y escalado dentro; entrada 224×224×3 en píxeles 0–255), `models/clases_imagenes.json` (lista de nombres; el índice = salida del modelo), `models/imagenes_meta.json`. Campos del meta: `ganador`, `metricas` (accuracy y macro_f1 en test de DS3; `*_val`; `*_test_6clases`; `*_ds4`; `brecha_accuracy`, `brecha_macro_f1`), `comparacion_variantes`, `por_clase_test`, `matriz_confusion_test`, `prueba_externa` (`clases_comunes`, `mapeo_trashnet_a_ds3`, `n_ds4`, `ds4_por_clase`, `matriz_ds4`, `fotos_propias`), `limpieza` (duplicados y conteo por clase y partición), `librerias`, `notas`. Salidas: `data/processed/m3_resultados.csv`, `m3_resumen.txt`, `m3_particiones.csv` y figuras `docs/figuras/m3_conteo_clases.png`, `m3_curvas.png`, `m3_comparacion.png`, `m3_matriz_confusion.png`, `m3_matriz_ds4.png`. El mapeo clase→contenedor está en `config.CONTENEDORES` (Parte B).

Las claves de `metricas` varían por módulo (clasificación: accuracy, macro_f1, etc.; clustering: silhouette, davies_bouldin, calinski_harabasz; resumen: rouge1, rouge2, rougeL, ratio_compresion). Los valores **solo** se llenan con ejecución real.

## 4. Contratos de los artefactos y módulos

| Módulo | Artefactos en `models/` | Entrada que recibe `render()` | Salida que muestra |
|---|---|---|---|
| Predicción | `prediccion_mejor.pkl` (Pipeline completo de sklearn/XGBoost con su preprocesamiento), `prediccion_meta.json` (campo `features` obligatorio) | Elección de un país o formulario con las variables de `features` (+ simulador) | Generación per cápita estimada (kg/hab/día), comparación con su grupo de ingreso/región, métricas desde el `_meta.json` |
| Series temporales | `serie_mejor.*` o un modelo por serie (`serie_<id>.*`), `serie_meta.json` (campos `series` con sus ids y métricas, `frecuencia`, `horizonte_max`, unidades) | Serie elegida (S1, S2, S3…) y horizonte de pronóstico | Gráfico histórico + pronóstico (+ intervalo si aplica), comparación con el baseline, métricas |
| Imágenes | `clasificador_imagenes.keras`, `clases_imagenes.json` (orden de clases del entrenamiento), `imagenes_meta.json` (incluye métricas en test de DS3 y en DS4) | Imagen subida (jpg/png) y esquema de colores | Clase predicha, probabilidades (top 3), contenedor sugerido (mapeo en `config.py`), aviso para residuos peligrosos |
| Clustering | `clustering_mejor.pkl` (variante A, países), `clustering_meta.json` (etiquetas de perfil por clúster); si hay otras variantes: `clustering_<variante>_mejor.pkl` y `_meta.json` (`nyc`, `texto`) | Variante, y país/distrito elegido o tabla subida | Clúster asignado, descripción del perfil, gráfico 2D, vecinos más cercanos |
| Resumen | `resumen_meta.json` (modelos usados, ROUGE reales en E1 y E2, tokenizador usado); el modelo abstractivo se descarga de Hugging Face en la primera ejecución | Texto pegado o archivo `.txt` | Resumen extractivo y abstractivo, ratio de compresión, aviso de uso responsable |

**Datos procesados** (la Fase 2 los genera; descripción en `contexto/C3_datasets_del_proyecto.md`, sección 4):

| Archivo | Lo usan | Notas |
|---|---|---|
| `data/processed/paises_residuos.csv` | Predicción, Clustering A | incluye `gpc_kg_hab_dia` derivada |
| `data/processed/dsny_distritos_mensual.csv` | Series (modelo global), Clustering B | formato largo por distrito y material |
| `data/processed/serie_ciudad_mensual.csv` | Series temporales | una columna por material + indicadores exógenos |
| `data/processed/distritos_nyc_perfil.csv` | Clustering B (opcional) | periodo reciente y estable |
| `data/processed/textos_residuos.csv` | Resumen (ROUGE), Clustering C | **no va al repositorio** (licencia no comercial) |

### Columnas del dataset procesado (nombres estandarizados que genera la Fase 2 Parte A; las columnas **reales** se confirman con la salida del usuario)

**`paises_residuos.csv`** (orden: `iso3c`, `pais`, `region_id`, `income_id`, `gdp`, `poblacion`, `residuos_total_ton_anio`, `gpc_kg_hab_dia`, y el resto). Mapeo de DS1: `country_name`→`pais`; `population_population_number_of_people`→`poblacion`; `total_msw_total_msw_generated_tons_year`→`residuos_total_ton_anio`; `composition_X_percent`→`comp_X_pct`; `waste_treatment_X`→`trat_X` (`_percent`→`_pct`); `waste_collection_coverage_X`→`cobertura_X`; `special_waste_X`→`especial_X`; `gpc_kg_hab_dia` = `residuos_total_ton_anio`×1000÷365÷`poblacion` (NaN si no se puede calcular).

**`dsny_distritos_mensual.csv`**: `fecha` (primer día del mes), `distrito`, `borough`, `material` (refuse/paper/mgp/organics), `toneladas`.

**`serie_ciudad_mensual.csv`**: `fecha`, una columna por material, `n_distritos`, `dias_mes`, `covid`, `organicos_programa` (1 = programa vigente).

Con `cobertura_completa` (1 = mes con el máximo de distritos con dato) añadida en el ajuste de la Parte A. `distritos_nyc_perfil.csv` (variante 4-B, opcional): **no se genera en la Parte A**.

### Columnas reales de `paises_residuos.csv` (52; derivadas de la salida real del usuario, 2026-11-21)
- **Texto (10):** `iso3c`, `region_id`, `pais`, `income_id`, `where_where_is_this_data_measured` y 5 columnas `other_information_*` (sistema de información, agencia, ley nacional, reglas APP, resumen público).
- **Principales:** `gdp`, `poblacion`, `residuos_total_ton_anio`, `gpc_kg_hab_dia` (derivada).
- **Composición (9, %):** `comp_food_organic_waste_pct`, `comp_glass_pct`, `comp_metal_pct`, `comp_other_pct`, `comp_paper_cardboard_pct`, `comp_plastic_pct`, `comp_rubber_leather_pct`, `comp_wood_pct`, `comp_yard_garden_green_waste_pct`.
- **Tratamiento (11, %):** `trat_anaerobic_digestion_pct`, `trat_compost_pct`, `trat_controlled_landfill_pct`, `trat_incineration_pct`, `trat_landfill_unspecified_pct`, `trat_open_dump_pct`, `trat_other_pct`, `trat_recycling_pct`, `trat_sanitary_landfill_landfill_gas_system_pct`, `trat_unaccounted_for_pct`, `trat_waterways_marine_pct`.
- **Cobertura de recolección (12, %):** `cobertura_{rural|total|urban}_percent_of_{geographic_area|households|population|waste}` (el sufijo `_percent_of_...` NO se abrevia).
- **Residuos especiales (6, ton/año):** `especial_{agricultural|construction_and_demolition|e|hazardous|industrial|medical}_waste_tons_year` (el de e-waste se llama `especial_e_waste_tons_year`).

### Columnas reales de DS2 crudo
`MONTH` (`AAAA / MM`), `BOROUGH`, `COMMUNITYDISTRICT`, `REFUSETONSCOLLECTED`, `PAPERTONSCOLLECTED`, `MGPTONSCOLLECTED`, `RESORGANICSTONS`, `SCHOOLORGANICTONS`, `LEAVESORGANICTONS`, `XMASTREETONS`, `OTHERORGANICSTONS`, `BOROUGH_ID`. `organics` = suma de las 4 columnas `*ORGANIC*`; `XMASTREETONS` no se incluye.

### Columnas (plantilla anterior, ya cubierta arriba)

| Columna | Tipo | Descripción | Fuente |
|---|---|---|---|
| `[PENDIENTE]` | | | |

*(Una tabla por archivo de la lista anterior; los nombres provisionales están en `C3`, sección 4. Los nombres originales de DS1 que ya se vieron en documentación, p. ej. `total_msw_total_msw_generated_tons_year`, `population_population_number_of_people`, `income_id`, `region_id`, `gdp`, se renombran en la Fase 2 y el mapeo se registra aquí.)*

## 5. Funciones públicas registradas

Los estados de los archivos se llevan en el árbol de la sección 1 (cambiar ⬜ por 🟡 / ✅ / ⚠️). Cuando una fase crea una función que otras fases usarán, **anota aquí su firma exacta**:

| Archivo | Firma | Qué hace |
|---|---|---|
| `config.py` | constantes `NOMBRE_PROYECTO`, `RANDOM_STATE`, `BASE_DIR`, `DATA_RAW`, `DATA_PROCESSED`, `IMG_DIR`, `MODELS_DIR`, `DOCS_DIR`, `ARCHIVOS_PROCESADOS` (dict clave→CSV: paises, dsny_distritos, serie_ciudad, distritos_nyc, textos), `MODULOS` (lista de dict: id, titulo, modulo, meta), `CONTENEDORES` (dict esquema_id → {nombre, fuente, clases: {clase: {color, hex, contenedor, origen ('norma'|'proyecto'), nota}}}; esquemas `proyecto`, `peru_municipal`, `peru_no_municipal`), `NOMBRES_CLASES`, `RESIDUOS_PELIGROSOS`, `UMBRAL_CONFIANZA` (0.60), `UMBRAL_PELIGROSO_POSIBLE` (0.20), `ESQUEMA_PREDETERMINADO`, `AVISO_USO` | Rutas, semilla y registro de módulos |
| `app/utils/modelos.py` | `ruta_modelo(nombre)`, `meta_existe(nombre_meta)`, `leer_meta(nombre_meta) -> dict`, `cargar_joblib(nombre)`, `cargar_keras(nombre)`, `estado_modulo(modulo) -> bool` | Carga de artefactos (cacheada con `st.cache_resource` si hay Streamlit) y lectura de metadatos |
| `app/utils/datos.py` | `ruta_procesado(clave)`, `procesado_existe(clave)`, `cargar_procesado(clave) -> DataFrame` | Lectura de CSV procesados (cacheada con `st.cache_data`) |
| `app/utils/graficos.py` | `tabla_metricas(meta)`, `mostrar_metricas(meta)`, `grafico_barras(df,x,y,titulo,color)`, `grafico_dispersion_2d(df,x,y,color,hover,titulo)`, `grafico_pronostico(historico,pronostico,inferior,superior,titulo,unidad)` | Gráficos plotly y métricas desde el `_meta.json` |
| `app/modules/prediccion.py` | `render()`; puras: `fmt(x, decimales)`, `construir_tabla(valores, features, n)`, `estimar(modelo, tabla) -> (array, hubo_negativos)`, `avisos_rango(gdp, poblacion, meta) -> [(nivel, texto)]`, `referencia(meta, tipo, clave)`, `comparacion_con_baseline(meta)`, `curva_pib(modelo, meta, poblacion, region, puntos)`. Constantes `ARCHIVO_MODELO`, `ARCHIVO_META`, `ORDEN_INGRESO`, `NOMBRE_INGRESO` | Pestaña de predicción. Entrada: `gdp`, `poblacion`, `region_id` (las `features` del meta); lee `prediccion_mejor.pkl` y `prediccion_meta.json`. Si el meta pide otras variables, avisa y no estima |
| `app/modules/clustering.py` | `render()`; puras: `etiqueta(variable)`, `cargar_nombres(meta) -> (nombres, avisos)`, `asignar_perfil(art, valores) -> (cluster, distancias, vector)`, `vecinos_de_vector(art, paises, x, n, excluir)`, `margen_frontera(distancias)`, `z_perfiles(paises, variables)`, `avisos_estructura(meta)`, `ruido_configuracion(algoritmo, parametros)`, `validar_perfil(valores, comp_vars)`. Constantes `ARCHIVO_MODELO`, `ARCHIVO_META`, `ARCHIVO_NOMBRES`, `ARCHIVO_PAISES`, `ETIQUETAS` | Pestaña de clustering. Lee `clustering_mejor.pkl`, `clustering_meta.json`, `clustering_nombres.json` (opcional) y `data/processed/clustering_paises.csv` (más `m4_resultados.csv` y las figuras `m4_*.png` si existen). Los nombres solo se aplican si `tamanos_de_la_ejecucion` coincide con `perfiles[c].n_paises` del meta |
| `app/modules/imagenes.py` | `render()`; puras: `nombre_clase(clase)`, `leer_clases(meta)`, `tam_entrada(meta)`, `abrir_imagen(bytes) -> PIL RGB`, `a_entrada(img, tam) -> array (1,alto,ancho,3) 0-255`, `predecir(modelo, img, tam) -> probs`, `top_k(probs, clases, k)`, `clase_peligrosa(top)`, `contenedor_de(clase, esquema_id)`, `precision_recall(meta, clase)`, `confundidas_con(meta, clase, k)`. Constantes `ARCHIVO_MODELO`, `ARCHIVO_CLASES`, `ARCHIVO_META`, `MAX_MB` | Pestaña de imágenes. Entrada: foto jpg/png (≤ 10 MB) y esquema de contenedores. Lee `clasificador_imagenes.keras`, `clases_imagenes.json` e `imagenes_meta.json`. Redimensiona con `tf.image.resize` bilinear sin recorte (igual que el entrenamiento); si la confianza es menor que `UMBRAL_CONFIANZA` no sugiere contenedor |
| `app/modules/series_tiempo.py` | `render()`; puras: `nombre_modelo(m)`, `fmt(x, dec)`, `fechas_futuras(ultima_fecha, h)`, `pronosticar(art, h=None) -> DataFrame (índice fecha; pronostico, inferior, superior en t/mes)`, `leer_pronostico_csv(meta_serie)`, `texto_comparacion(tabla_modelos, ganador) -> list[str]`, `tabla_modelos_df(meta_serie)`, `serie_historica(clave, columna, inicio)`. Constantes `ARCHIVO_META`, `NOMBRES`, `SIMPLES` | Pestaña de series. Entrada: serie (ids de `serie_meta.json`), horizonte 1 a `horizonte_max` y años de histórico. Calcula siempre el pronóstico de 12 meses con el modelo guardado (para que los intervalos no cambien con el horizonte) y recorta; si el `.joblib` no carga (p. ej. otra versión de statsmodels) usa `m2_pronostico_<id>.csv` y avisa. Muestra métricas desde el meta, comparación calculada contra el ingenuo estacional, avisos por modelo simple sin intervalo o `convergio` = False, y descarga del pronóstico en CSV |
| `src/entrenar_series.py` | CLI: `python src/entrenar_series.py` (sin argumentos) | Entrena y evalúa los 7 modelos por serie, elige el ganador, guarda los artefactos del módulo 2 y escribe `data/processed/m2_resumen.txt`. Puede tardar decenas de minutos por el LSTM |
| `src/comprobar_modelo_imagenes.py` | CLI: `python src/comprobar_modelo_imagenes.py [--imagen ruta]` | Comprueba que el modelo carga y predice en el entorno local; devuelve 0 si todo bien |
| `src/fijar_versiones.py` | script (sin funciones públicas) | Reescribe `requirements.txt` con las versiones instaladas |
| `src/preparar_datos.py` | CLI: `python src/preparar_datos.py <descargar\|verificar\|preparar\|todo> [--forzar]`. Funciones: `renombrar_ds1(df)`, `preparar_ds1(log)`, `detectar_ds2(df)`, `parsear_fecha(serie)`, `ds2_largo(df, det, log)`, `serie_ciudad(largo, log)`, `preparar_ds2(log)`. Parámetros editables al inicio: `UNIDAD_DS2`, `SUBCADENAS_MATERIAL`, `COVID_INICIO/FIN`, `ORG_SUSPENDE/REANUDA`, `MAPA_DS1` | Descarga a `data/raw/wab/` y `data/raw/dsny/`; escribe `verificacion_ds1_ds2.txt`, `log_preparacion.txt` y los CSV de `data/processed/` |
| `src/eda_tabular.py` | CLI: `python src/eda_tabular.py` (sin funciones públicas) | Imprime resumen y guarda 8 figuras en `docs/figuras/` |
| `src/preparar_textos.py` | CLI: `python src/preparar_textos.py [--n 500] [--fuente xlsum\|mlsum\|ambas]`. Funciones: `sin_tildes(t)`, `marcar_residuos(serie)`, `estandarizar(df, fuente)`, `muestrear(df, n, semilla)`, `cargar(fuente)`, `procesar(fuente, n, log)`. Constantes editables: `PALABRAS_RESIDUOS`, `CANDIDATOS` (formas de carga) | Salidas: `data/processed/textos_residuos.csv` (columnas `id, fuente, particion, texto, resumen_ref, es_residuos`; solo test, hasta `n` por fuente), `log_textos.txt`, `revision_filtro.csv` (25 por fuente para revisión manual). Requiere `datasets` |
| `src/verificar_imagenes.py` | CLI: `python src/verificar_imagenes.py --ds3 RUTA [--ds4 RUTA]`. Funciones: `dhash(img)`, `analizar(raiz)`, `informe(...)`, `cruzar(df3, df4, L)` | Salidas: `data/processed/verificacion_imagenes.txt` y `duplicados_ds3_ds4.csv` (`ruta_ds3, ruta_ds4, tipo`). La partición train/val/test se hace en la Fase 5 |
