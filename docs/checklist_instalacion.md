# Checklist de instalación desde cero — EcoCiudad IA

**Estado:** `[RESULTADO REAL PENDIENTE]`. Este checklist aún no se ha ejecutado en una carpeta limpia; la columna «Resultado» la completa quien lo pruebe.

**Qué se probó hasta ahora (versiones reales, ver `estado/REGISTRO_RESULTADOS.md`, sección 0b):** Windows, Python 3.13.6. Otras versiones de Python o sistemas operativos **no se probaron** (`C2` sugería Python 3.11).

**Antes de empezar:** necesitas Git y Python. TensorFlow y el modelo abstractivo (opcional, unos 2.33 GB al descargarse la primera vez) son pesados. La app **no entrena** nada y funciona sin el abstractivo.

| # | Paso | Comando (Windows) | Resultado esperado | Resultado |
|---|---|---|---|---|
| 1 | Clonar en una carpeta nueva | `git clone <URL del repositorio> EcoCiudad_prueba` y `cd EcoCiudad_prueba` | Aparecen `app/`, `models/`, `data/processed/`, `config.py` | |
| 2 | Crear y activar el entorno | `python -m venv venv` y `venv\Scripts\activate` | El prompt muestra `(venv)` | |
| 3 | Instalar dependencias | `pip install -r requirements.txt` | Termina sin errores | |
| 4 | Revisar que `statsmodels` esté una sola vez (P29) | `findstr /c:"statsmodels" requirements.txt` | Una sola línea | |
| 5 | Comprobar archivos de los módulos | `python -c "from app.utils.diagnostico import revisar_todos; print([r for r in revisar_todos() if not r['listo']])"` | Imprime `[]` | |
| 6 | Pruebas | `python -m pytest -q` | Todas pasan (anota el total) | |
| 7 | Abrir la app | `streamlit run app/main.py` | Se abre el navegador con Inicio y 5 pestañas, sin mensajes de error | |
| 8 | Recorrer cada pestaña | (en el navegador) | Cada módulo responde; en la barra lateral, «Diagnóstico técnico» sin ❌ | |
| 9 | Seguridad (P37): `git ls-files` lista lo **confirmado en Git**, no lo que hay en el disco; borrar el archivo no basta (hace falta `git rm --cached notebooks/kaggle.json` y un commit) | `git ls-files \| findstr kaggle` | No imprime nada | |
| 10 | Medir el arranque | `python src/medir_arranque.py` | Imprime tiempos y guarda `data/processed/m8_arranque.json` | |
| 11 | (Opcional) Resumen abstractivo | `pip install -r requirements-abstractivo.txt`; en la pestaña Resumen, activar el abstractivo | Descarga el modelo y genera un resumen | |

**Si usas Git Bash en Windows (MINGW64):** activa el entorno con `source venv/Scripts/activate`, usa `grep -c statsmodels requirements.txt` en el paso 4 (el nombre de la librería no es un comando por sí solo) y `git ls-files | findstr kaggle` en el paso 9 (funciona igual).

**En Linux o macOS:** activa el entorno con `source venv/bin/activate`, usa `grep -c statsmodels requirements.txt` en el paso 4 y `git ls-files | grep kaggle` en el paso 9. No se probó en esos sistemas.

**Notas:**
- `requirements.txt` incluye `notebook` y `datasets`, que solo se usan para los notebooks y para `src/preparar_textos.py`; la app no los necesita.
- `data/processed/textos_residuos.csv` no está en el repositorio (licencia no comercial) y la app no lo necesita. Se regenera con `python src/preparar_textos.py`.
- Si el paso 3 o el 6 fallan, pega el mensaje completo con `Error:` en el chat.
