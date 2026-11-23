# ESTADO DEL PROYECTO

> **Archivo vivo** (memoria del proyecto entre chats). Se edita con cambios puntuales al cerrar cada fase/parte. Solo se marca completado lo que el usuario validó; nunca se escriben resultados que no vengan de una ejecución real.

**Leyenda de estados:** ⬜ pendiente · 🟡 entregada, pendiente de validar · ✅ completada y validada · ⚠️ con problemas abiertos

---

## 0. Metadatos

| Campo | Valor |
|---|---|
| Versión del estado | 31 (Fase 5 Parte B: script de comprobación OK y TensorFlow fijado) |
| Última actualización | 2026-11-21 |
| Última fase completada | Fase 4 (con P20 parcial; Fase 2 con pendientes: revisión humana del filtro de textos e imágenes DS3 y DS4) |
| Fase actual | Fase 5 Parte B — 🟡 entregada; falta que el usuario la pruebe y escriba "Continuar" |
| Semana del cronograma | 13 (próxima entrega: semana 14, avance 50 %) |
| Nº de conversación (chat) | 1 |

## 1. Datos del proyecto

| Campo | Valor |
|---|---|
| Curso | Software Inteligente (UNMSM, 2026-2), docente David Calderón Vilca |
| Tema | Gestión inteligente de residuos urbanos (decidido por el usuario; datasets globales, Lima solo como caso local opcional) |
| Nombre del proyecto | **EcoCiudad IA** (elegido por el usuario) |
| Integrantes y roles | No se registran nombres por decisión del usuario; nº de integrantes y roles `[PENDIENTE]` (no bloquea) |
| Repositorio (GitHub u otro) | `[PENDIENTE]` |
| Fuente de la serie temporal mensual | **DS2 DSNY Monthly Tonnage (NYC)** — propuesta, sin verificar (ver `C3`, V3/V4) |
| Dataset de imágenes elegido | **DS3 Garbage Classification V2** (entrenamiento) + **DS4 TrashNet** (prueba externa) — propuesta, sin verificar (ver `C3`, V5/V6) |
| Dataset(s) tabulares elegidos | **DS1 What a Waste (países)** para módulos 1 y 4-A; DS2 para 4-B (opcional) — propuesta, sin verificar (ver `C3`, V1) |
| Datasets de texto | **DS5 XL-Sum (es)** y **DS6 MLSUM (es)** para el módulo 5; DS7 para la demostración — propuesta, sin verificar (ver `C3`, V7) |

## 2. Progreso por fases

| Fase | Nombre | Estado | Entregables principales | Validado | Notas |
|---|---|---|---|---|---|
| 0 | Arranque y decisiones | ✅ | Resumen, preguntas resueltas, nombre, stack confirmado | Sí (Continuar) | Semana 13, informe en Markdown, nombre EcoCiudad IA, sin nombres de integrantes |
| 1 | Estructura del repositorio y entorno | ✅ | Árbol, `requirements.txt`, `main.py` esqueleto, `config.py`, utils | Sí (Continuar) | App abre con 5 pestañas (confirmado por el usuario) |
| 2 | Datos: descarga, verificación, limpieza y EDA | ✅ | `src/preparar_datos.py`, CSV limpio, diccionario de datos, EDA | Sí (Continuar, con pendientes) | Parte A validada (REGISTRO 0c). Parte B entregada; textos listos y verificados (XL-Sum 4 763 y MLSUM 13 366 artículos de test; muestras de 500); revisión preliminar del filtro hecha por la IA (precisión 6 % con criterio de tema principal; REGISTRO 0e); imágenes aún no descargadas |
| 3 | Módulo 1: Predicción | ✅ | Notebook 01, `prediccion.py`, modelo + meta | Sí (Continuar) | Parte A ejecutada con datos reales (REGISTRO 1): ganador SVR con A0; mejora modesta sobre el baseline. Parte B entregada: `app/modules/prediccion.py` (simulador, países, métricas); abierta por el usuario en la app real y confirmada (REGISTRO 0b) |
| 4 | Módulo 4: Clustering | ✅ | Notebook 04, `clustering.py`, modelo + meta | Sí (Continuar) | Parte A con datos reales (REGISTRO 4): K-Means k=4, estructura débil. Parte B: `app/modules/clustering.py`; modo país confirmado tras corregir TWN sin nombre (D57, D58); perfil nuevo, mapa y métricas sin reporte de fallas (P20 parcial) |
| 5 | Módulo 3: Imágenes | 🟡 | Notebook 03 (Colab), `imagenes.py`, `.keras` + meta | Parte A: sí (Continuar) | Parte A ejecutada con datos reales (REGISTRO 3). Parte B entregada: `app/modules/imagenes.py`, `CONTENEDORES` en `config.py`, `src/comprobar_modelo_imagenes.py`, `tests/test_imagenes.py`. Probada por la IA con el modelo real, 5 pruebas pytest y Streamlit AppTest con una foto sintética; en el PC del usuario: 5 pruebas pasan, la app y la pestaña funcionan (interfaz aprobada por el usuario); el script de comprobación se corrigió (codificación) y terminó en OK; 1 foto real probada (REGISTRO 3) |
| 6 | Módulo 2: Series temporales | ⬜ | Notebook 02, `series_tiempo.py`, modelo + meta | — | |
| 7 | Módulo 5: Resumen de texto | ⬜ | Notebook 05, `resumen.py` | — | |
| 8 | Integración y pruebas | ⬜ | `main.py` completo, pruebas, caché, errores | — | |
| 9 | Manuales | ⬜ | `docs/manual_instalacion.md`, `docs/manual_usuario.md` | — | |
| 10 | Informe técnico, Parte A | ⬜ | Secciones 1–5 | — | |
| 11 | Informe técnico, Parte B | ⬜ | Secciones 6–12 | — | |
| 12 | Exposición y revisión final | ⬜ | Guion, diapositivas, preguntas probables, checklist | — | |

## 3. Decisiones tomadas

Detalle y motivos en los archivos indicados. Todas las decisiones de datos son **propuestas** hasta que la Fase 2 las verifique (`C3`, lista V1 a V8).

| Nº | Decisión | Detalle en | Fase |
|---|---|---|---|
| D1 | Tema: gestión inteligente de residuos urbanos (reemplaza "residuos en Lima"; Lima = caso local opcional) | `C1` | v2 |
| D2 | Arquitectura en 3 capas (Streamlit, módulos, modelos/datos); notebooks fuera de la app | `C2` 3 | previa |
| D3 | Stack moderno y gratuito, sin GPU en la app | `C2` 2 | previa |
| D4 | No inventar datos, métricas, modelos ni versiones | prompt | previa |
| D5 | Cada modelo guardado lleva `*_meta.json` con sus métricas reales | `ESTRUCTURA` 3 | previa |
| D6 | Predicción de generación **per cápita**, no toneladas triviales | `M1` 4 | previa |
| D7 | M1: países (DS1), sin total ni composición como variables, baseline = media por grupo de ingreso | `M1` 4 | v2 (confirmar F3) |
| D8 | M2: serie mensual DSNY (S1 obligatoria; S2 y S3 recomendadas), indicadores COVID/orgánicos, ventana móvil | `M2` 2 | v2 (confirmar F6) |
| D9 | M3: entrenar con DS3, probar en DS4 (6 clases comunes), revisar duplicados | `M3` 6 | v2 (confirmar F5) |
| D10 | M4: variante A (países) obligatoria; B (distritos NYC) opcional; C (texto) descartada por defecto: el PDF del enunciado no exige texto (decisión del usuario) | `M4` 1.6 y 2 | v2.2 |
| D11 | M5: ROUGE con XL-Sum y MLSUM (longitud comparable, Lead-3, tokenizador propio); DS7 solo demostración | `M5` 2 | v2 (confirmar F7) |
| D12 | Un solo `src/preparar_datos.py`; datos crudos y de licencia no comercial no van al repositorio | `C3` 4 | v2 |
| D13 | Modo ahorro (cuenta gratuita): fases pesadas en Parte A/B; módulos mínimos al avance = 3 | `PLAN_DE_FASES`, `INDICE` 5 | v2.1 |

| D15 | Nombre del proyecto: EcoCiudad IA | `C1` | 0 |
| D16 | Informe y manuales en Markdown por ahora (sin Word/PDF) | `C2` 4 | 0 |
| D17 | Semana 13, entrega del avance 50 % en la semana 14: prioridad a 3 módulos funcionando (Fases 1 a 5) y borrador del informe; Fases 6 y 7 después si el tiempo no alcanza | `PLAN_DE_FASES` | 0 |
| D18 | `requirements.txt` sin versiones inventadas: el usuario ejecuta `src/fijar_versiones.py` tras instalar | `ESTRUCTURA` 2 | 1 |
| D19 | `main.py` carga módulos con `importlib` (módulo ausente = "en construcción", fallo = `st.error` sin tumbar la app) | `ESTRUCTURA` 2 | 1 |
| D20 | `models/` no se ignora en Git (la app necesita los modelos); `data/raw/`, `data/imagenes/` y `textos_residuos.csv` sí | `.gitignore` | 1 |
| D21 | DS1 se renombra con prefijos `comp_`, `trat_`, `cobertura_`, `especial_` (mapa en `ESTRUCTURA`) y `gpc_kg_hab_dia` se deriva con la fórmula de `C3` | `ESTRUCTURA` 4 | 2A |
| D22 | DS2: `organics` = suma de todas las columnas cuyo nombre contenga «organic» (`[VERIFICAR]` con la salida real); unidad asumida ton/mes hasta que V3 diga lo contrario | `src/preparar_datos.py` | 2A |
| D23 | `covid` = 1 de 2020-03 a 2021-12 (fin **provisional**, se define con el EDA); `organicos_programa` = 0 de 2020-05 a 2021-09 | `M2` 2.2 | 2A |
| D24 | La variante 4-B (`distritos_nyc_perfil.csv`) no se genera en la Parte A; se hará solo si sobra tiempo | `C3` 4 | 2A |
| D25 | DS2: `organics` suma las 4 columnas `*ORGANIC*`; `XMASTREETONS` queda fuera (pico estacional, no es un programa continuo). Revisar si se quiere alinear con la definición oficial | `src/preparar_datos.py` | 2A |
| D26 | DS2: unidad ton/mes se mantiene como supuesto razonable (suma anual de refuse ≈ 2.7–3.4 millones de 1993 a 2025); queda `[VERIFICAR]` con un PDF mensual de DSNY | `REGISTRO` 0c | 2A |
| D27 | DS2: no se sumarán distritos sin comprobar cobertura (hay meses con 3 a 59 distritos); la ventana de modelado se decide en la Fase 6 con `cobertura_completa`. Hay quiebres a documentar (mgp 2003; organics 2020–2021 y 2024–2025) | `M2` 2.2 | 2A |
| D28 | DS2: ventanas con cobertura completa de 59 distritos: refuse desde 1992-01; paper y mgp desde 2004-04. Organics solo la tiene desde 2024-10 (25 meses): no se modela con esa ventana; su tratamiento (suma de ciudad con indicador de expansión, o descartarla) se decide en la Fase 6 | `REGISTRO` 0c | 2A |
| D29 | M1: los extremos de gpc son territorios pequeños de ingreso alto (p. ej. Virgin Islands (U.S.), Bermuda, Monaco); se conservan y se evalúa con y sin ellos, reportando MAE y RMSE (confirmar en F3) | `REGISTRO` 0c | 2A |
| D30 | M1: solo `gdp`, `poblacion`, `income_id` y `region_id` están completas (100 %); cobertura y tratamiento tienen 42–58 % de datos. Comparar un conjunto base con otro ampliado imputando dentro del `Pipeline` (confirmar en F3) | `REGISTRO` 0c | 2A |
| D31 | La partición train/val/test de imágenes y el mapeo de clases DS3→TrashNet se hacen en la Fase 5 (al leer `M3` y ver los nombres reales); la Fase 2 deja verificación y lista de duplicados | `C3` 4 | 2B |
| D32 | Textos: solo partición *test* de XL-Sum y MLSUM (no se entrena nada); muestra de hasta 500 por fuente (semilla 42) con prioridad a artículos de residuos; filtro por palabras clave con revisión manual de 50 | `M5` 2.1 | 2B |
| D33 | `datasets` se agrega manualmente a `requirements.txt` del usuario (no se envía el archivo para no perder las versiones fijadas); si no instala en Python 3.13, `preparar_textos.py` se ejecuta en Colab | `ESTRUCTURA` 2 | 2B |
| D34 | Textos: carga mediante archivos parquet de la rama `refs/convert/parquet` con `huggingface_hub` (los scripts de dataset ya no se soportan), o archivo local de test con `--xlsum_archivo` / `--mlsum_archivo` | `REGISTRO` 0d | 2B |
| D35 | Textos: se excluyen del test los archivos de conjuntos aparte («challenge_test_covid» en MLSUM) y solo se usa la carpeta `test` oficial | `REGISTRO` 0d | 2B |
| D36 | Textos: tope de 250 artículos de residuos por fuente (500 en total) para que E1 y E2 sean comparables y se pueda reportar ROUGE en subconjuntos «residuos» y «otros»; relaja la prioridad absoluta a residuos de `M5` 2.1 (editable con `--max_residuos`) | `M5` 2.1 | 2B |
| D37 | **Propuesta (pendiente de confirmar):** `es_residuos` significa «menciona residuos», no «trata de residuos» (precisión preliminar 6 %). En la Fase 7 reportar ROUGE sobre la muestra completa de cada fuente; el subconjunto «residuos» solo se usará con un filtro más estricto (palabra clave en el título o ≥ 3 apariciones) y si queda con suficientes artículos; la temática de residuos se demuestra con DS7 | `REGISTRO` 0e | 2B |
| D38 | M1: reglas fijadas antes de ver resultados: prueba 20 % estratificada por `income_id` (semilla 42) usada una sola vez; validación cruzada 5×3; objetivo en escala lineal y logarítmica; selección por RMSE; ganador entre los 3 mejores modelos ajustados con `GridSearchCV` por RMSE de validación cruzada | `notebooks/01_prediccion.ipynb` | 3A |
| D39 | M1: tres conjuntos de variables: A0 (`gdp`, `poblacion`, `region_id`), A (A0 + `income_id`) y B (A + `cobertura_total_percent_of_population`, 42 % de datos). Para la app se elige el más simple cuyo mejor RMSE_cv no supere el mejor global + 1 desviación estándar entre pliegues (A0 < A < B); así el simulador de PIB es coherente y las variables son conocibles | `M1` 4 | 3A |
| D40 | M1: los 5 países de mayor gpc (territorios pequeños de ingreso alto) se conservan; se reporta el desempeño con y sin ellos (cierra la propuesta D29). El baseline es el promedio por grupo de ingreso y se compara con la misma validación cruzada | `M1` 4 | 3A |
| D41 | M1: el entrenamiento está en `notebooks/01_prediccion.ipynb` y en `src/entrenar_prediccion.py` (mismo código, sin Jupyter, generado del notebook). XGBoost es opcional: si no está instalado se omite. El modelo final se reentrena con todos los países con objetivo después de reportar las métricas | `ESTRUCTURA` | 3A |
| D42 | M1, ganador: SVR (C=1, epsilon=0.1), conjunto A0, objetivo lineal; RMSE de prueba 0.443 frente a 0.501 del baseline (n = 43). Es una mejora modesta: los 3 mejores modelos no se distinguen dentro de la desviación entre pliegues (≈ 0.09), y Random Forest, XGBoost y KNN quedan peor que el baseline en validación cruzada con 172 países | `REGISTRO` 1 | 3A |
| D43 | M1: la mejora sobre el baseline se concentra en el grupo HIC (RMSE 0.459 frente a 0.582); en LIC, LMC y UMC es nula o mínima. La app y el informe deben decirlo y mostrar el error típico (RMSE ≈ 0.44 kg/hab/día; MAPE ≈ 37 %) | `REGISTRO` 1 | 3A |
| D44 | El notebook `notebooks/01_prediccion.ipynb` ejecutado por el usuario (con salidas) es el válido: las próximas entregas no lo incluyen para no sobrescribirlo | `ESTRUCTURA` | 3A |
| D45 | **Aceptada por el usuario e implementada en `app/modules/prediccion.py`:** simulador con `gdp`, `poblacion` y `region_id`; compara con el promedio de la región y de un grupo de ingreso elegido a mano; muestra siempre el error típico; los países del dataset se muestran como «ajuste dentro de la muestra, no validación»; aviso si los valores caen fuera de `rangos_variables` o si es un territorio pequeño de ingreso alto | `M1` 6 | 3A |
| D46 | Predicción en la app: tres pestañas (Simulador, Países del dataset, Modelo y métricas). Todas las cifras de error salen de `prediccion_meta.json`, nunca fijas en el código; el texto «frente al baseline» se calcula (si el modelo no mejora, lo dice). Banda orientativa = estimación ± RMSE de prueba (no es un intervalo formal). Equivalente nacional en t/año = estimación × población × 365 ÷ 1000 | `app/modules/prediccion.py` | 3B |
| D47 | Streamlit 1.67.0: no se usan los parámetros `use_container_width` ni `width` en `st.plotly_chart`, `st.dataframe` ni `st.image` (no se pudo verificar su API vigente); si el diseño sale angosto, se ajusta con `Error:` | `REGISTRO` 0b | 3B |
| D48 | `.agents/` (habilidades de agentes de Streamlit, enlaces simbólicos locales) se agrega a `.gitignore` | `.gitignore` | 3B |
| D49 | M4 variante A: se agrupa con 7 variables (`gpc_kg_hab_dia` y los 6 porcentajes de composición con más datos); se excluyen total de toneladas, `gdp`, `income_id` y `region_id`, y los países con algún faltante en esas 7 variables (sin imputar la composición) | `M4` 2 | 4A |
| D50 | M4: cobertura de recolección (42 % de datos) y reciclaje (58 %) quedan fuera del conjunto principal por completitud (REGISTRO 0c); solo se usan como sensibilidad con los países que los tienen | `REGISTRO` 0c | 4A |
| D51 | M4: 4 algoritmos (K-Means, Agglomerative Ward, GMM diagonal, DBSCAN) y regla fijada de antemano: mayor Silhouette con 3 a 8 clústeres, ruido ≤ 10 %, tamaño mínimo 5, desempate por Davies-Bouldin; preprocesamiento principal log1p + estandarización, CLR como sensibilidad comparada por ARI (las métricas internas no son comparables entre espacios) | `M4` 1.6 | 4A |
| D52 | M4: los nombres de los clústeres se escriben después de ver los perfiles reales, en `models/clustering_nombres.json`; la variante B (distritos de NYC) no se hace por ahora y la de texto no se hace | `M4` 2 | 4A |
| D53 | M4, lectura de los resultados: la estructura de grupos es **débil y poco estable**: Silhouette 0.219 (igual que K = 2), estabilidad ARI 0.662 ± 0.277 (mín 0.250), cambia mucho con el preprocesamiento (CLR: ARI 0.314) y con el conjunto de variables (ampliado, n = 44: ARI 0.231); en cambio es estable frente a la semilla (ARI 0.963). Los 4 grupos se presentan como **tipología orientativa**, no como categorías naturales | `REGISTRO` 4 | 4A |
| D54 | M4, **nombres escritos en `models/clustering_nombres.json`** (la app los usa solo si los tamaños de clúster coinciden con los del meta; las políticas son sugerencias, no derivadas de los datos): 0 «Alta generación, mucho papel y cartón» (16 de 17 son HIC); 1 «Generación intermedia, composición mixta» (79 países, mayoría HIC y UMC); 2 «Baja generación, predominio orgánico» (ningún HIC); 3 «Alta fracción de “otros”» (heterogéneo en ingreso; la categoría «otros» puede reflejar cómo se clasificó cada país) | `REGISTRO` 4 | 4A |
| D55 | M4: DBSCAN no produjo ninguna configuración que cumpliera la regla; su mejor Silhouette sin restricciones (0.491) se informa pero no se usa: tiene 82.5 % de ruido, así que solo cubre el 17.5 % de los países | `REGISTRO` 4 | 4A |
| D56 | App de clustering: tres pestañas (Explorar, Mapa y grupos, Modelo y métricas). «Explorar» permite elegir un país del dataset o introducir un perfil nuevo (se asigna al centroide más cercano; avisa si la composición suma más de 100 % o si el perfil está casi a igual distancia de dos grupos, con margen (d2 − d1)/d2 < 0.15, umbral heurístico). Los avisos sobre estructura débil, estabilidad y sensibilidad se calculan con el meta; no hay cifras fijas en el código. No se muestra selector de variante: solo existe la A | `app/modules/clustering.py` | 4B |
| D57 | Clustering, corrección del error: `sorted()` fallaba con un nombre de país vacío (reproducido en pruebas con un nombre vacío; el error es idéntico). Ahora `_leer_paises()` rellena `pais` con `iso3c` cuando falta, la lista de descartados tolera valores vacíos y el módulo muestra un «Detalle técnico del error» con el traceback. La causa en los datos reales (qué país tiene el nombre vacío) está sin confirmar | `app/modules/clustering.py` | 4B |
| D58 | Causa confirmada del error de clustering: `TWN` no trae nombre de país en DS1. Las pestañas de clustering y de predicción muestran el código `iso3c` cuando falta el nombre; no se inventa un nombre en los datos. El nombre del grupo se muestra con `st.subheader` porque no cabía en un `st.metric` | `REGISTRO` 0c | 4B |
| D59 | M3: un solo notebook de Colab (`03_imagenes_colab.ipynb`) hace descarga (API de Kaggle), inventario, duplicados, partición, 3 variantes, prueba externa, meta y zip de salida. Las subcarpetas de DS3 y DS4 y el emparejamiento de clases **no se suponen**: el usuario las elige tras ver la lista real (`SUB_DS3`, `SUB_DS4`, `MAPEO_MANUAL`) | `notebooks/03_imagenes_colab.ipynb` | 5A |
| D60 | M3: duplicados = mismo MD5 o mismo hash perceptual (igual que `verificar_imagenes.py`); en DS3 se conserva una copia (si hay etiquetas distintas se descartan todas), y las imágenes de DS4 que coinciden con DS3 se excluyen de la prueba externa | `notebooks/03_imagenes_colab.ipynb` | 5A |
| D61 | M3: partición estratificada 70/15/15 (semilla 42) hecha antes del aumento; pesos de clase `balanced`; se guarda `data/processed/m3_particiones.csv` | idem | 5A |
| D62 | M3, regla fijada antes de entrenar: gana la variante con mayor macro-F1 de **validación**; empate (≤ 0.005) → menos parámetros entrenables; test no se usa para elegir. V1 CNN propia; V2 MobileNetV2 solo clasificador; V3 fine-tuning de las últimas 30 capas (BatchNorm congelada, lr 1e-5) desde V2 | idem | 5A |
| D63 | M3: preprocesamiento y aumento dentro del modelo; `Rescaling(1/127.5, offset=-1)` reemplaza a `preprocess_input` (mismo escalado a [-1, 1]); no se verificó contra la función oficial | idem | 5A |
| D64 | M3: prueba externa con decisión restringida a 6 clases comunes (probabilidades renormalizadas); se reporta DS3 test 6 clases, DS4 y la brecha; «trash» de TrashNet y la basura general de DS3 pueden no equivaler | idem | 5A |
| D65 | M3, datos: 2 238 de las 2 527 imágenes de DS4 coinciden con DS3 (MD5 o hash perceptual idéntico), así que la prueba externa solo tiene 277 imágenes, desbalanceadas (glass 111, trash 86, metal 10). Se reporta tal cual, con esa limitación; no se presenta como prueba de TrashNet completa | `REGISTRO` 3 | 5A |
| D66 | M3, lectura: V3 es el ganador (macro-F1 val 0.9127 frente a 0.8832 de V2), con una sola ejecución por variante; V1 (CNN propia) queda en 0.4194 de macro-F1 en test. La brecha de dominio (0.266 en accuracy, 0.296 en macro-F1) debe leerse con la cautela de D65 y se discute en el informe | `REGISTRO` 3 | 5A |
| D67 | **Rechazada por el usuario (2026-11-23):** no se usarán fotos propias. La prueba externa queda solo con las 277 imágenes de DS4 no coincidentes (D65); el informe lo declara como limitación | `REGISTRO` 3 | 5A |
| D68 | M3 se entrenó con la versión `original` de DS3 (tamaños variados), no con la de 256 px que proponía `M3` 6.1. `image_dataset_from_directory` redimensiona a 224×224 sin recortar (la imagen se estira); la app debe aplicar el mismo redimensionado a la foto subida, y se comprueba en la Parte B (PIL vs. TensorFlow pueden diferir un poco) | `REGISTRO` 3 | 5A |
| D69 | M3, contenedores: tres esquemas en `config.CONTENEDORES` — `proyecto` (convención propia, no es estándar), `peru_municipal` y `peru_no_municipal` (resumen de Inacal publicado por Andina sobre la NTP 900.058:2019, 2.ª ed.; el PDF oficial no se pudo abrir). Cada sugerencia indica si su origen es `norma` o `proyecto` (p. ej. calzado y basura general son criterio del proyecto). **[VERIFICAR] los colores contra el texto oficial antes de citarlos** | `config.py` | 5B |
| D70 | M3, app: la foto se redimensiona con `tf.image.resize` bilinear sin recorte (la misma llamada que `image_dataset_from_directory` en el código fuente de Keras 3.15.1; el entrenamiento usó 3.13.2, no se comparó su código); se corrige la rotación EXIF y las transparencias PNG se pasan a fondo blanco; límite 10 MB | `app/modules/imagenes.py` | 5B |
| D71 | M3, umbrales heurísticos (no derivados de datos ni calibrados): confianza < 0.60 → no se sugiere contenedor y se pide otra foto; si una clase peligrosa (batería) es la 2.ª o 3.ª con ≥ 0.20, se avisa igual | `config.py` | 5B |
| D72 | M3: el modelo no tiene clase «ninguno» y responde con alta confianza a imágenes que no son residuos (ruido → `paper` 0.876; REGISTRO 3); la app lo declara en «¿Qué tan fiable es este resultado?» y el informe lo incluirá como limitación | `REGISTRO` 3 | 5B |
| D74 | M3: `comprobar_modelo_imagenes.py` fuerza UTF-8 en la salida (la consola de Windows usa cp1252 y fallaba con «≈»); el aviso «No runtime found» de Streamlit al ejecutarlo fuera de la app es normal | `src/comprobar_modelo_imagenes.py` | 5B |
| D73 | M3: TensorFlow se agrega **a mano** a `requirements.txt` (no se reenvía el archivo, D33); `src/comprobar_modelo_imagenes.py` verifica la carga local (P12) | `src/comprobar_modelo_imagenes.py` | 5B |
| D14 | Stack de `C2` sec. 2 propuesto sin cambios (Python 3.11, Streamlit, scikit-learn, Keras/Colab, etc.); confirmar al validar F0 | `C2` 2 | 0 (propuesta) |

*(La IA agrega aquí cada decisión nueva con su fase.)*

## 4. Modelos y datasets ganadores por módulo

| Módulo | Dataset usado | Modelo ganador | Métrica clave (real) | Artefacto | Estado |
|---|---|---|---|---|---|
| 1 Predicción | DS1, 172 países con objetivo (prueba n = 43) | SVR (C=1, epsilon=0.1), conjunto A0 | RMSE prueba 0.443 (baseline 0.501), MAE 0.268, R² 0.529 (REGISTRO 1) | `models/prediccion_mejor.pkl` | ✅ |
| 2 Series temporales | — | — | — | `models/serie_mejor.*` | ⬜ |
| 3 Imágenes | DS3 limpio (12 220 imágenes, 10 clases); prueba externa DS4 (277) | V3 MobileNetV2 con fine-tuning | Test DS3: accuracy 0.915, macro-F1 0.910; DS4 (6 clases): accuracy 0.610, macro-F1 0.574 (REGISTRO 3) | `models/clasificador_imagenes.keras` | 🟡 (falta Parte B) |
| 4 Clustering | DS1, 7 variables de composición y generación | K-Means k=4 | Silhouette 0.219, DB 1.548; estabilidad ARI 0.662 ± 0.277 (estructura débil) (REGISTRO 4) | `models/clustering_mejor.pkl` | ✅ |
| 5 Resumen | — | — | — | (modelo HF / TextRank) | ⬜ |

*(Detalle completo de métricas en `REGISTRO_RESULTADOS.md`.)*

## 5. Pendientes y bloqueos

| Nº | Pendiente | Resp. | Estado |
|---|---|---|---|
| P1 | Verificar DS2 (DSNY): descarga, fechas, unidades, columnas (`C3` V3, V4) | Usuario | abierto |
| P2 | Nº de integrantes (4 o 5) y roles; sin nombres por ahora | Usuario | abierto (no bloquea) |
| P3 | Nombre del proyecto | Usuario | cerrado: EcoCiudad IA |
| P4 | Verificar DS1, DS3 a DS6 (columnas, clases, licencias, carga) con `C3` V1 a V8 | Usuario | abierto |
| P5 | (Opcional) Fotos propias de residuos, sin personas | Equipo | descartado por el usuario (D67) |
| P6 | Crear repositorio Git | Usuario | abierto |
| P9 | Semana actual del cronograma | Usuario | cerrado: semana 13 |
| P10 | Formato del informe | Usuario | cerrado: Markdown |
| P11 | Confirmar que el navegador muestra las 5 pestañas | Usuario | cerrado: confirmado 2026-11-21 |
| P13 | Ejecutar `preparar` y `eda_tabular.py` con el ajuste y pegar las líneas nuevas | Usuario | cerrado: 2026-11-21 |
| P14 | Contrastar la unidad ton/mes con un reporte mensual PDF de DSNY (opcional, V3). Hipótesis a verificar: la caída de mgp en 2003 coincide con cobertura incompleta (antes de 2004-04) y el salto de organics en 2025 con que los 59 distritos reportan desde 2024-10 | Equipo | abierto |
| P1 | Verificar DS2 (columnas, fechas, rango): hecho; falta unidad y cobertura | Usuario | parcial |
| P12 | TensorFlow en el PC del usuario (Python 3.13) | Usuario | cerrado: 2026-11-22 (TensorFlow 2.21.0 y Keras 3.15.1 cargan el modelo; 5 pruebas pasan) |
| P18 | Ejecutar el clustering y pegar `m4_resumen.txt` | Usuario | cerrado: 2026-11-22 |
| P20 | Reprobar la pestaña Clustering: país del dataset, perfil nuevo, mapa y métricas | Usuario | parcial: país del dataset confirmado (captura); perfil nuevo, mapa y métricas sin reporte de fallas |
| P21 | Identificar qué país tiene el nombre vacío | Usuario | cerrado: 2026-11-23 (TWN) |
| P19 | Registrar el % de ruido de DBSCAN | Usuario | cerrado: 2026-11-22 (82.5 %, desde `m4_resultados.csv`) |
| P17 | Abrir la pestaña Predicción y confirmar que se ve bien | Usuario | cerrado: 2026-11-22 (simulador confirmado con captura; las sub-pestañas de países y métricas no se mencionaron) |
| P16 | Ejecutar el entrenamiento y pegar `m1_resumen.txt` | Usuario | cerrado: 2026-11-21 |
| P15 | Textos: reejecución hecha y revisión preliminar hecha por la IA con extractos (REGISTRO 0e). Falta que una persona del equipo revise por lo menos 10 de los 50 con el artículo completo, y decidir D37, antes de la Fase 7. Imágenes: descargar DS3 y DS4 y ejecutar `verificar_imagenes.py`, o hacerlo en Colab al inicio de la Fase 5 | Usuario | abierto (parcial) |
| P8 | Cuenta de Kaggle y `kaggle.json` (el notebook lo pide al ejecutarse; o descargar a mano los ZIP) | Usuario | abierto (se usa en Fase 5A) |
| P22 | Ejecutar `notebooks/03_imagenes_colab.ipynb` en Colab y pegar resultados | Usuario | cerrado: 2026-11-23 (`m3_resumen.txt` y celdas 4 y 5; REGISTRO 3) |
| P23 | Anotar la licencia de DS3 y DS4 (V5, V8). El emparejamiento TrashNet→DS3 se recibió (nombres idénticos); que `trash` sea equivalente es un supuesto | Usuario | parcial: falta la licencia |
| P24 | `SUB_DS3` = `original`, `SUB_DS4` = `dataset-resized`; artefactos `clasificador_imagenes.keras` (21.9 MB), `clases_imagenes.json` e `imagenes_meta.json` recibidos y comprobados | Usuario | cerrado: 2026-11-23 |
| P25 | Decidir D67 (fotos propias) | Usuario | cerrado: no (2026-11-23) |
| P26 | `tensorflow==2.21.0` agregado y fijado en `requirements.txt`; `python src/comprobar_modelo_imagenes.py` termina en OK en el PC del usuario | Usuario | cerrado: 2026-11-22 |
| P27 | Probar la pestaña con 3 a 5 fotos reales de residuos (clase, confianza, si acertó) y guardar capturas para el manual | Usuario | parcial: 1 foto (madera → Cartón 94.5 %, REGISTRO 3) |
| P28 | Contrastar los colores de `peru_municipal` y `peru_no_municipal` con el texto oficial de la NTP 900.058:2019 (INACAL) | Usuario | abierto |

## 6. Próximo paso exacto

> Con **Continuar** la Fase 5 pasa a ✅ y empieza la **Fase 6** (Módulo 5: resumen de texto); antes se lee su guía `M5` y la sección de textos de `C3`. Siguen abiertos, sin bloquear: P23 (licencias de DS3 y DS4), P27 (más fotos reales y capturas para el manual) y P28 (colores de la NTP 900.058:2019).

## 7. Historial

| Versión | Fecha | Fase | Cambio |
|---|---|---|---|
| 0 | — | — | Estado inicial creado junto con el paquete |
| 31 | 2026-11-23 | 5B | Script de comprobación OK en el PC del usuario; `tensorflow==2.21.0` fijado en `requirements.txt` (`fijar_versiones.py` dejó `pytest==8.3.4`, la versión instalada, en lugar de 9.0.1); P26 cerrado; quedan P23, P27 (parcial) y P28 |
| 30 | 2026-11-23 | 5B | Pruebas en el PC del usuario: 5 pruebas OK, app y pestaña funcionando; script corregido por codificación (D74); P12 cerrado, P26 y P27 parciales; observación con foto real en REGISTRO 3 |
| 29 | 2026-11-23 | 5B | Fase 5 Parte B entregada: `imagenes.py`, `CONTENEDORES` y umbrales en `config.py`, script de comprobación y pruebas; D69 a D73; pendientes P26 a P28 |
| 28 | 2026-11-23 | 5A | Artefactos del módulo 3 recibidos y comprobados (carga y coherencia con el meta); D67 rechazada; P24 y P25 cerrados; confusiones principales en REGISTRO 3 |
| 27 | 2026-11-23 | 5A | Confirmados `SUB_DS3` = `original` y `SUB_DS4` = `dataset-resized` (P24 parcial); D68 |
| 26 | 2026-11-23 | 5A | Resultados reales del módulo 3 registrados (REGISTRO 3); decisiones D65 a D67; pendientes P22 cerrado, P23 parcial, P24 y P25; tabla de ganadores actualizada |
| 25 | 2026-11-23 | 5A | Fase 4 validada (✅). Fase 5 Parte A entregada: notebook 03 de Colab (D59 a D64); probado solo con datos de juguete. Tabla de ganadores (sec. 4) completada para M1 y M4 desde REGISTRO |
| 24 | 2026-11-23 | 4B | Modo país confirmado; causa del error: TWN sin nombre (D58); mismo ajuste en predicción y nombre del grupo en `st.subheader` |
| 23 | 2026-11-23 | 4B | Error reportado en clustering (modo país); corregido con D57 |
| 22 | 2026-11-22 | 4B | Fase 4 Parte B entregada: `app/modules/clustering.py` y `models/clustering_nombres.json` (D54 aplicada, D56) |
| 21 | 2026-11-22 | 4A | Registrado el 82.5 % de ruido de DBSCAN desde `m4_resultados.csv` (P19 cerrado) |
| 20 | 2026-11-22 | 4A | Registrados los resultados reales del clustering (REGISTRO 4); decisiones D53 a D55 |
| 19 | 2026-11-22 | 4A | Fase 3 validada (✅). Fase 4 Parte A entregada: notebook 04 y `src/entrenar_clustering.py` (D49 a D52) |
| 18 | 2026-11-22 | 3B | Pestaña Predicción confirmada en la app real; `.agents/` ignorado (D48) |
| 17 | 2026-11-22 | 3B | Fase 3 Parte B entregada: `app/modules/prediccion.py` (D45 implementada, D46, D47) |
| 16 | 2026-11-21 | 3A | Registrados los resultados reales del módulo 1 (REGISTRO 1); decisiones D42 a D45 |
| 15 | 2026-11-21 | 3A | Fase 2 pasa a ✅ (con pendientes). Fase 3 Parte A entregada: notebook 01 y `src/entrenar_prediccion.py` (D38 a D41) |
| 14 | 2026-11-21 | 2B | Revisión preliminar del filtro de residuos por la IA (REGISTRO 0e); propuesta D37 |
| 13 | 2026-11-21 | 2B | Registrada la reejecución de textos: MLSUM 13 366 filas de test, muestras de 500 con 250 y 192 de residuos |
| 12 | 2026-11-21 | 2B | Registrada la carga real de XL-Sum y MLSUM; detectada mezcla de `challenge_test_covid`; corregido y limitado el tope de residuos (D35, D36) |
| 11 | 2026-11-21 | 2B | Registrados resultados reales de la Parte B (REGISTRO 0d); carga de textos corregida (D34) |
| 10 | 2026-11-21 | 2B | Fase 2 Parte A validada. Parte B entregada: textos, verificación de imágenes, guías y diccionario (D31 a D33) |
| 9 | 2026-11-21 | 2A | Registrados cobertura de distritos, extremos de gpc y completitud (REGISTRO 0c); decisiones D28 a D30; P13 cerrado |
| 8 | 2026-11-21 | 2A | Resultados reales de DS1 y DS2 registrados (REGISTRO 0c); ajuste de cobertura y de EDA (D25 a D27) |
| 7 | 2026-11-21 | 2A | Fase 1 validada (✅). Fase 2 Parte A entregada: `preparar_datos.py`, `eda_tabular.py` (D21 a D24). Probada con datos de juguete |
| 6 | 2026-11-21 | 1 | Interfaz confirmada por el usuario; dry-run de TensorFlow registrado como indicio. Falta "Continuar" para pasar la Fase 1 a ✅ |
| 5 | 2026-11-21 | 1 | Registrados Python 3.13.6, versiones fijadas y arranque del servidor (REGISTRO 0b). Fase 1 sigue 🟡; abierto P11, P12 |
| 4 | 2026-11-21 | 1 | Fase 0 validada (✅). Fase 1 entregada: config, utils, main esqueleto, README, requirements, .gitignore, `fijar_versiones.py` (D18 a D20) |
| 3 | 2026-11-21 | 0 | Registradas respuestas: semana 13, Markdown, nombre EcoCiudad IA, sin nombres de integrantes (D15 a D17) |
| 2 | 2026-11-21 | 0 | Fase 0 entregada (resumen, 3 preguntas, 3 nombres propuestos, stack propuesto). Sin validar |
| 1 | 2026-11-20 | — | Paquete v2: tema a "residuos urbanos", catálogo `C3`, módulos y plan actualizados. v2.1: avance = 3 módulos, modo ahorro, Parte A/B, archivos más compactos |
