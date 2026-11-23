# Diccionario de datos

Fecha de acceso a las fuentes: **2026-11-21**. Los datos señalados como «pendiente de contrastar» no se han confirmado con la fuente original.
Las cifras de este documento provienen de la ejecución de los scripts de `src/`.

## 1. `data/processed/paises_residuos.csv` (DS1, 217 filas × 52 columnas)
**Fuente:** Banco Mundial, *What a Waste* (datos por país), https://datacatalog.worldbank.org/search/dataset/0039597. Licencia indicada en la ficha: CC-BY-4.0 (pendiente de contrastar con la fuente).
**Unidad de análisis:** un país o territorio (`iso3c` único, 217, sin duplicados). **No existe columna de año de referencia**: los valores corresponden a años distintos según el país; es una limitación a declarar.

| Columna(s) | Tipo | Significado |
|---|---|---|
| `iso3c`, `pais` | texto | Código ISO de tres letras y nombre del país o territorio |
| `region_id` | texto | Región del Banco Mundial; 7 códigos observados: EAS, ECS, LCN, MEA, NAC, SAS, SSF (significados pendientes de contrastar con el diccionario oficial) |
| `income_id` | texto | Grupo de ingreso: HIC (alto), UMC (medio-alto), LMC (medio-bajo), LIC (bajo) |
| `gdp` | número | PIB en las unidades del dataset. Por su magnitud (Afganistán ≈ 2 057; Aruba ≈ 35 563) parece un valor per cápita y no un total (pendiente de contrastar con el diccionario oficial) |
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
**Transformaciones:** renombrado de columnas con los prefijos `comp_`, `trat_`, `cobertura_` y `especial_` (ver `src/preparar_datos.py`), conversión numérica, derivación de `gpc_kg_hab_dia`. No se eliminó ninguna fila.

## 2. `data/processed/dsny_distritos_mensual.csv` (DS2, formato largo, 77 685 filas)
**Fuente:** NYC Department of Sanitation, *DSNY Monthly Tonnage Data*, NYC Open Data, https://data.cityofnewyork.us/d/ebb7-mvp5. Licencia pendiente de confirmar en la ficha de NYC Open Data.

| Columna | Tipo | Significado |
|---|---|---|
| `fecha` | fecha | Primer día del mes (el original usa `AAAA / MM`) |
| `distrito` | texto | Distrito comunitario: `borough-NN` (el número de distrito se repite entre boroughs) |
| `borough` | texto | Borough de Nueva York |
| `material` | texto | `refuse` (basura), `paper` (papel), `mgp` (metal, vidrio y plástico), `organics` (suma de RESORGANICS, SCHOOLORGANIC, LEAVESORGANIC y OTHERORGANICS; **no** incluye árboles de Navidad) |
| `toneladas` | número | Toneladas **por mes** (supuesto; unidad pendiente de contrastar con un reporte mensual de DSNY) |

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

**Cobertura completa (59 distritos) sostenida desde:** refuse 1992-01; paper y mgp 2004-04; organics 2024-10. Antes de esas fechas los totales **no son comparables**. 4 meses (1990-02 a 1990-05) no tienen ninguna fila. `organics` tiene datos en 257 de 442 meses y cambia de régimen (suspensión 2020–2021; salto en 2024–2025 posiblemente por expansión del programa, sin confirmar).

## 4. Imágenes (DS3 y DS4; no se incluyen en el repositorio)
Fuentes, descarga y verificación en `docs/datos_imagenes.md`. Clases de DS3 usadas por el modelo: battery, biological, cardboard, clothes, glass, metal, paper, plastic, shoes, trash. DS3 aporta 12 259 imágenes originales (12 duplicados y 27 con etiquetas en conflicto eliminadas) y DS4 aporta 2 527 (2 238 coinciden con DS3 y se excluyen de la prueba externa, que queda con 277 imágenes).

## 5. Limitaciones generales
- Datos globales (DS1) y de una sola ciudad (DS2); Lima solo aparece como caso de discusión, no como dato.
- DS1 mezcla años distintos y tiene muchos vacíos; DS2 cambia de cobertura y de programas con el tiempo.
- Las salidas de los modelos son orientativas: pueden contener errores y sesgos de los datos.
