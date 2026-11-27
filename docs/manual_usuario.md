# Manual de usuario — EcoCiudad IA

EcoCiudad IA es una aplicación **académica** de apoyo a la decisión sobre gestión de residuos urbanos, con cinco módulos de inteligencia artificial. Sus resultados son **orientativos**: pueden tener errores y sesgos y no sustituyen la evaluación de un especialista.

> **Capturas:** las imágenes enlazadas viven en `docs/capturas/`. Cada una está **pendiente** hasta que alguien la tome con la app abierta y la guarde con el nombre indicado (lista al final). Mientras tanto, el enlace aparecerá roto en los visores de Markdown.

**Antes de usarla**
- No subas fotos con personas, rostros ni documentos, ni textos con datos personales.
- Los modelos aprenden de datos públicos con vacíos y sesgos. La predicción y el clustering son por **país**; las series temporales son de **una sola ciudad (Nueva York)**; las fotos provienen de conjuntos públicos.
- Cada módulo tiene una sección «Modelo y métricas» (o similar) con los errores reales medidos y sus limitaciones. Léela antes de confiar en un resultado.

## 0. Pantalla general

Se abre con `streamlit run app/main.py` (ver el manual de instalación). Arriba hay seis pestañas: **Inicio** y los cinco módulos. A la izquierda, la barra lateral muestra:
- **Estado de los módulos:** ✅ significa que los archivos del módulo están presentes (no prueba que funcione); ⏳ y «Faltan: …» indican qué archivo falta.
- **Aviso de uso responsable.**
- **Diagnóstico técnico:** tiempo que tardó cada pestaña en la última interacción. Si un módulo falla, aquí aparece ❌ y la pestaña muestra el error con un «Detalle técnico»; el resto de la app sigue funcionando.

![Inicio y barra lateral](capturas/01_inicio.png)

## 1. 📈 Predicción

**Propósito:** estimar cuántos kg de residuos genera por día una persona en un país, a partir de su PIB, población y región.

**Simulador — pasos**
1. Abre la subpestaña **Simulador**.
2. Completa **PIB** (en las unidades del dataset), **Población (habitantes)** (mínimo 1 000) y **Región (código del Banco Mundial)**.
3. Opcional: elige un **Grupo de ingreso para comparar**.
4. Lee la **Estimación** en kg/hab/día, junto con el error típico y la comparación con el promedio de la región y del grupo elegido.

**Cómo interpretarlo**
- El **error típico** es el error medido en países de prueba; no es un intervalo de confianza formal.
- Si el PIB o la población salen del rango de entrenamiento, la app avisa: es una extrapolación y la estimación es poco fiable.
- El modelo mejora de forma modesta a un promedio simple por grupo de ingreso, y esa mejora no es igual en todos los grupos; los detalles están en **Modelo y métricas**.
- Estima un promedio nacional, no una ciudad.

![Predicción: simulador](capturas/02_prediccion_simulador.png)

**Países del dataset:** elige un **País o territorio** para ver su valor real (derivado) y el ajuste del modelo. Es un ajuste **dentro de la muestra** (el modelo final se reentrenó con todos los países): no es una validación.

![Predicción: países del dataset](capturas/03_prediccion_paises.png)

## 2. 🕒 Series temporales

**Propósito:** pronosticar las toneladas mensuales de residuos de la ciudad de Nueva York para planificar recursos.

**Pasos** (subpestaña **Pronóstico**)
1. Elige la **Serie** (basura; papel; metal, vidrio y plástico).
2. Mueve **Meses a pronosticar** (1 hasta el máximo del modelo).
3. Elige el **Histórico a mostrar** (últimos 3, 5 o 10 años, o todo).
4. Mira el gráfico y los indicadores: **Modelo elegido**, **RMSE, MAE y MAPE en prueba**.
5. Opcional: abre «Ver tabla del pronóstico y descargarla» y pulsa **Descargar CSV**.

**Cómo interpretarlo**
- Las unidades son **toneladas por mes**.
- El intervalo del 95 % existe solo si el modelo elegido es ETS o SARIMAX; con modelos simples no hay intervalo y la app lo avisa.
- Las mejoras sobre un pronóstico ingenuo estacional son pequeñas; abre «¿Qué tan fiable es este pronóstico?» y la subpestaña **Modelos y datos**.
- Supuestos: no hay otra pandemia y el programa de residuos orgánicos sigue como en el último dato. Una sola ciudad: no generalizar.

![Series: pronóstico](capturas/04_series_pronostico.png)

## 3. 🖼️ Imágenes

**Propósito:** reconocer el tipo de residuo en una foto y sugerir el contenedor.

**Pasos** (subpestaña **Clasificar una foto**)
1. Elige el **Esquema de colores de contenedores** (esquema del proyecto o los dos esquemas de la norma peruana NTP 900.058:2019, municipal y no municipal).
2. Pulsa **Sube una foto (jpg o png)** (máximo 10 MB). Una sola foto de **un** residuo, con buena luz y sin personas.
3. Lee el tipo de residuo, la **Confianza del modelo** y el **Contenedor sugerido**.

**Tipos que reconoce:** batería o pila, residuo orgánico, cartón, ropa, vidrio, metal, papel, plástico, zapatos y basura general.

**Cómo interpretarlo**
- Si la confianza es baja, la app **no sugiere contenedor** y pide otra foto.
- Si detecta una posible pila o batería, avisa que es un residuo peligroso: no va a la basura común.
- La app indica si cada sugerencia sale de la norma o de un criterio del proyecto. Los colores de la norma peruana están **pendientes de contrastar con el texto oficial**.
- El modelo **no tiene una clase «ninguno»**: ante algo que no es un residuo puede responder con mucha confianza.
- En **Modelo y métricas** están el desempeño medido y la matriz de confusión, y el desempeño baja en la prueba externa.

![Imágenes: clasificar](capturas/05_imagenes_clasificar.png)

## 4. 🧩 Clustering

**Propósito:** ver a qué grupo de países se parece un país (o un perfil que tú introduces) según su generación y composición de residuos.

**Pasos** (subpestaña **Explorar**)
1. En **¿Qué quieres explorar?** elige **País del dataset** o **Perfil nuevo**.
2. *País del dataset:* elige el **País o territorio** y mira su grupo, su nombre, el ingreso y la región, y los países más parecidos.
3. *Perfil nuevo:* completa **Generación (kg/hab/día)** y los porcentajes de **Orgánico, Papel y cartón, Plástico, Vidrio, Metal y Otros**. La suma de la composición no puede pasar de 100 %. La app asigna el grupo cuyo centro esté más cerca.
4. La subpestaña **Mapa y grupos** muestra los países en 2D y el perfil de cada grupo.

**Cómo interpretarlo**
- La estructura de grupos es **débil y poco estable** (cambia con el preprocesamiento y con las variables usadas): son una **tipología orientativa**, no categorías naturales.
- Si el perfil está casi a igual distancia de dos grupos, la app avisa que la asignación es poco firme.
- Las políticas sugeridas para cada grupo son sugerencias, no conclusiones de los datos.

![Clustering: explorar](capturas/06_clustering_explorar.png)
![Clustering: mapa y grupos](capturas/07_clustering_mapa.png)

## 5. 📝 Resumen

**Propósito:** resumir un texto largo.

**Pasos** (subpestaña **Resumir un texto**)
1. Pega el texto en **Texto a resumir**, o sube un `.txt` de hasta 1 MB, o pulsa **Usar un texto de ejemplo**. Mínimo 20 palabras.
2. Elige el **Método**: *Extractivo (TextRank)*, que copia las oraciones más importantes, o *Abstractivo (mT5 XL-Sum)*, que reescribe con un modelo (solo aparece si instalaste `requirements-abstractivo.txt`).
3. Con el extractivo, ajusta **Oraciones del resumen** (1 a 8).
4. Pulsa **Resumir** y lee el **Resumen** y los avisos.

**Cómo interpretarlo**
- El abstractivo **puede inventar o alterar datos** (nombres, cifras, quién hizo qué). Contrástalo siempre con el original; la app marca cifras y nombres del resumen que no están en el texto, como pista, no como garantía.
- La primera vez, el abstractivo descarga unos 2.3 GB; sin GPU se midieron unos 15 s por bloque de ≈ 260 palabras en el PC del equipo (el tuyo puede ser distinto).
- Para textos largos se resume por bloques; ese procedimiento **no se evaluó** con ROUGE.
- La subpestaña **Evaluación y límites** muestra cómo se comparó cada método en noticias; la ventaja del abstractivo se concentra en el conjunto de noticias con el que fue entrenado.

![Resumen: extractivo](capturas/08_resumen_extractivo.png)
![Resumen: abstractivo](capturas/09_resumen_abstractivo.png)

## Capturas pendientes (guardar en `docs/capturas/`)

| Archivo | Qué mostrar |
|---|---|
| `01_inicio.png` | Pestaña Inicio con la barra lateral |
| `02_prediccion_simulador.png` | Simulador con una estimación |
| `03_prediccion_paises.png` | Países del dataset |
| `04_series_pronostico.png` | Pronóstico de una serie |
| `05_imagenes_clasificar.png` | Foto clasificada con su contenedor |
| `06_clustering_explorar.png` | Explorar con un país |
| `07_clustering_mapa.png` | Mapa y grupos |
| `08_resumen_extractivo.png` | Resumen extractivo |
| `09_resumen_abstractivo.png` | Resumen abstractivo (si lo instalaste) |
