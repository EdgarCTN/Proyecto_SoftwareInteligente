# Diccionario de datos — EcoCiudad IA

Fecha de acceso a las fuentes: **2026-11-21** (día de ejecución). Lo marcado **[VERIFICAR]** no está confirmado con la fuente.
Los números de este documento salen de las ejecuciones reales registradas en `estado/REGISTRO_RESULTADOS.md` (sección 0c).

## 1. `data/processed/paises_residuos.csv` (DS1, 217 filas × 52 columnas)
**Fuente:** Banco Mundial, *What a Waste* (datos por país), https://datacatalog.worldbank.org/search/dataset/0039597. Licencia indicada en la ficha: CC-BY-4.0 (verificación V8 pendiente).
**Unidad de análisis:** un país o territorio (`iso3c` único, 217, sin duplicados). **No existe columna de año de referencia**: los valores corresponden a años distintos según el país; es una limitación a declarar.

| Columna(s) | Tipo | Significado |
|---|---|---|
| `iso3c`, `pais` | texto | Código ISO de tres letras y nombre del país o territorio |
| `region_id` | texto | Región del Banco Mundial; 7 códigos observados: EAS, ECS, LCN, MEA, NAC, SAS, SSF (significados **[VERIFICAR]** con el codebook) |
| `income_id` | texto | Grupo de ingreso: HIC (alto), UMC (medio-alto), LMC (medio-bajo), LIC (bajo) |
| `gdp` | número | PIB en las unidades del dataset. Por su magnitud (Afganistán ≈ 2 057; Aruba ≈ 35 563) parece un valor per cápita y no un total **[VERIFICAR con el codebook]** |
| `poblacion` | número | Habitantes |
| `residuos_total_ton_anio` | número | Residuos sólidos urbanos generados, toneladas por año |
| `gpc_kg_hab_dia` | número (derivada) | `residuos_total_ton_anio` × 1000 ÷ 365 ÷ `poblacion`; vacía si no se puede calcular (215 de 217 países) |
| `comp_*_pct` (9) | % | Composición de los residuos: food_organic_waste, glass, metal, other, paper_cardboard, plastic, rubber_leather, wood, yard_garden_green_waste |
| `trat_*_pct` (11) | % | Destino de los residuos: anaerobic_digestion, compost, controlled_landfill, incineration, landfill_unspecified, open_dump, other, recycling, sanitary_landfill_landfill_gas_system, unaccounted_for, waterways_marine |
| `cobertura_{rural,total,urban}_percent_of_{geographic_area,households,population,waste}` (12) | % | Cobertura de recolección por ámbito y base de cálculo |
| `especial_*_tons_year` (6) | ton/año | Residuos especiales: agricultural, construction_and_demolition, e (e-waste), hazardous, industrial, medical |
| `other_information_*` (5), `where_where_is_this_data_measured` | texto | Información cualitativa sobre políticas, sistema de información y dónde se midió el dato |

**Nombre vacío:** `TWN` (grupo de ingreso HIC, región EAS) no trae nombre de país en DS1 (observado en `clustering_paises.csv`); las pestañas de la app lo muestran con su código `iso3c`.
**Calidad:** completos al 100 %: `iso3c`, `pais`, `region_id`, `income_id`, `gdp`, `poblacion`; 99 %: `gpc_kg_hab_dia`, `residuos_total_ton_anio`; composición 79–81 %; reciclaje 58 %; cobertura total de población 42 %; cobertura por área geográfica 100 % vacía. Los valores más altos de `gpc_kg_hab_dia` son territorios pequeños de ingreso alto (p. ej. Virgin Islands (U.S.) 3.794, Bermuda 3.467).
**Transformaciones:** renombrado de columnas (mapa en `estado/ESTRUCTURA_PROYECTO.md`), conversión numérica, derivación de `gpc_kg_hab_dia`. No se eliminó ninguna fila.

## 2. `data/processed/dsny_distritos_mensual.csv` (DS2, formato largo, 77 685 filas)
**Fuente:** NYC Department of Sanitation, *DSNY Monthly Tonnage Data*, NYC Open Data, https://data.cityofnewyork.us/d/ebb7-mvp5. Licencia **[VERIFICAR]** (la ficha no la indicó en nuestras notas).

| Columna | Tipo | Significado |
|---|---|---|
| `fecha` | fecha | Primer día del mes (el original usa `AAAA / MM`) |
| `distrito` | texto | Distrito comunitario: `borough-NN` (el número de distrito se repite entre boroughs) |
| `borough` | texto | Borough de Nueva York |
| `material` | texto | `refuse` (basura), `paper` (papel), `mgp` (metal, vidrio y plástico), `organics` (suma de RESORGANICS, SCHOOLORGANIC, LEAVESORGANIC y OTHERORGANICS; **no** incluye árboles de Navidad) |
| `toneladas` | número | Toneladas **por mes** (supuesto razonable; unidad **[VERIFICAR]**) |

**Transformaciones:** se descartaron 23 735 de 101 420 filas (por toneladas vacías); no se eliminaron fechas. Columnas originales no usadas: `XMASTREETONS`, `BOROUGH_ID`.

## 3. `data/processed/serie_ciudad_mensual.csv` (DS2, 442 meses: 1990-01 a 2026-10)
| Columna | Tipo | Significado |
|---|---|---|
| `fecha` | fecha | Primer día del mes |
| `refuse`, `paper`, `mgp`, `organics` | número | Toneladas del mes sumadas en todos los distritos con dato |
| `n_distritos` | entero | Distritos con algún dato ese mes (entre 3 y 59) |
| `cobertura_completa` | 0/1 | 1 si el mes tiene el máximo de distritos (59) |
| `dias_mes` | entero | Días del mes |
| `covid` | 0/1 | 1 de 2020-03 a 2021-12 (el **fin es provisional**) |
| `organicos_programa` | 0/1 | 1 = programa de orgánicos vigente; 0 de 2020-05 a 2021-09 (suspensión documentada) |

**Cobertura completa (59 distritos) sostenida desde:** refuse 1992-01; paper y mgp 2004-04; organics 2024-10. Antes de esas fechas los totales **no son comparables**. 4 meses (1990-02 a 1990-05) no tienen ninguna fila. `organics` tiene datos en 257 de 442 meses y cambia de régimen (suspensión 2020–2021; salto en 2024–2025 posiblemente por expansión del programa **[VERIFICAR]**).

## 4. `data/processed/textos_residuos.csv` (DS5 y DS6; **no va al repositorio**)
**Fuentes:** XL-Sum, español (partición *test*), artículo https://aclanthology.org/2021.findings-acl.413/ — licencia **CC BY-NC-SA 4.0** (no comercial). MLSUM, español (*test*), artículo https://aclanthology.org/2020.emnlp-main.647 — **investigación no comercial**.

| Columna | Tipo | Significado |
|---|---|---|
| `id` | texto | Identificador del artículo en su fuente |
| `fuente` | texto | `xlsum` o `mlsum` |
| `particion` | texto | `test` |
| `texto` | texto | Artículo completo |
| `resumen_ref` | texto | Resumen de referencia humano (muy corto) |
| `es_residuos` | 0/1 | 1 si el texto contiene alguna palabra clave de residuos (lista en `src/preparar_textos.py`); **no implica que el artículo trate de residuos**: es una heurística que detecta menciones. Precisión preliminar con criterio de tema principal: 6 % (3 de 50; revisión por IA con extractos, ver `estado/REGISTRO_RESULTADOS.md` 0e) |

Muestra de 500 artículos por fuente (semilla 42): hasta 250 de residuos y el resto de otros temas, para que las dos fuentes sean comparables y se pueda reportar ROUGE por subconjunto. Solo la partición *test* oficial (se excluyen conjuntos de desafío como `challenge_test_covid`). **Cifras reales (2026-11-21):** XL-Sum test 4 763 artículos (192 con palabras de residuos, 4.0 %); MLSUM test 13 366 (699, 5.2 %). Muestras: 500 por fuente, con 192 y 250 artículos de residuos respectivamente. Textos de unas 765 y 798 palabras de media; resúmenes de referencia de 27.4 y 22.0. Precisión del filtro: 6 % preliminar (3 de 50; intervalo 95 %: 2.1 %–16.2 %); falta validación humana.

## 5. Imágenes (DS3 y DS4; **no van al repositorio**)
Estructura, descarga y verificación en `docs/guia_imagenes.md`. Clases, conteos, licencias y duplicados: `[RESULTADO REAL PENDIENTE]`. Las clases de DS3 indicadas por la fuente son metal, vidrio, biológico, papel, batería, basura general, cartón, zapatos, ropa y plástico; los nombres exactos de carpeta se confirman en la verificación.

## 6. Limitaciones generales
- Datos globales (DS1) y de una sola ciudad (DS2); Lima solo aparece como caso de discusión, no como dato.
- DS1 mezcla años distintos y tiene muchos vacíos; DS2 cambia de cobertura y de programas con el tiempo.
- Las salidas de los modelos son orientativas: pueden contener errores y sesgos de los datos.
