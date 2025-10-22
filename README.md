# Pydatasets Streamlit (estructura mínima)

Este repositorio contiene una estructura mínima para una aplicación Streamlit que carga y muestra
un archivo Excel con la lista de datasets traducidos.

Estructura creada:

- `app.py` — aplicación Streamlit mínima.
- `data/` — carpeta donde debe colocarse el archivo fuente `pydataset_list_translated.xlsx`.
- `.streamlit/config.toml` — configuración mínima de Streamlit (puerto, CORS, tema).
- `requirements.txt` — dependencias necesarias.
- `.gitignore` — reglas para ignorar virtualenvs y cachés, además de archivos de datos locales.

Archivo fuente

La aplicación espera el archivo:

	data/pydataset_list_translated.xlsx

Coloca tu archivo con ese nombre dentro de la carpeta `data/` antes de ejecutar la aplicación.

Ejecución local

1. Crear un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar la app:

```bash
streamlit run app.py
```

Despliegue

Puedes desplegar esta aplicación en Streamlit Community Cloud o en cualquier plataforma que soporte
aplicaciones Python (Heroku, Railway, etc.). Pasos generales para Streamlit Cloud:

- Sube este repositorio a GitHub.
- En Streamlit Cloud, conecta tu repo y selecciona la rama `main`.
- Como comando de ejecución usa `streamlit run app.py`.
- Asegúrate de que `requirements.txt` esté presente para que Streamlit instale las dependencias.

Notas

- Este proyecto ignora por defecto archivos en `data/` (ver `.gitignore`). Si quieres versionar el Excel,
  quita o modifica la línea correspondiente.
- El archivo `app.py` es solo una demostración mínima. Puedes mejorarlo añadiendo paginación,
  filtros por columna o exportación de resultados.
