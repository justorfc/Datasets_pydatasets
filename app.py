import streamlit as st
import pandas as pd
from pathlib import Path

# Archivo fuente esperado
DATA_FILE = Path(__file__).parent / "data" / "pydataset_list_translated.xlsx"

st.set_page_config(page_title="Pydataset — Catálogo traducido", layout="wide")

st.title("Pydataset — Catálogo traducido")

st.markdown(
    """
    Esta aplicación carga el archivo de datos `data/pydataset_list_translated.xlsx` y muestra
    una vista rápida del contenido.

    - Coloca el archivo `pydataset_list_translated.xlsx` en la carpeta `data/`.
    """
)


@st.cache_data
def load_data(path: Path):
    # Usamos engine='openpyxl' explícitamente
    return pd.read_excel(path, engine="openpyxl")


required_columns = {"dataset_id", "title", "title_es"}

if not DATA_FILE.exists():
    st.error(f"Archivo no encontrado: {DATA_FILE}. Coloca `pydataset_list_translated.xlsx` en la carpeta `data/`.")
    st.stop()

try:
    df = load_data(DATA_FILE)
except Exception as e:
    st.error(f"Error al leer el archivo Excel: {e}")
    st.stop()

# Validar columnas requeridas
missing = required_columns - set(df.columns.astype(str))
if missing:
    st.error(f"El archivo Excel no contiene las columnas requeridas: {sorted(list(missing))}")
    st.stop()

st.success(f"Cargado: {DATA_FILE.name} — {len(df)} filas, {len(df.columns)} columnas")

# Barra lateral: controles
st.sidebar.header("Controles")
search_q = st.sidebar.text_input("Buscar (dataset_id, title, title_es)")

page_size = st.sidebar.selectbox("Tamaño de página", options=[10, 25, 50, 100], index=1)

# Selector de columna para ordenación (solo columnas existentes)
sort_column = st.sidebar.selectbox("Ordenar por columna", options=[None] + list(df.columns), index=0)
sort_order = st.sidebar.radio("Orden", options=["asc", "desc"], index=0, horizontal=True)

# Aplicar filtro de búsqueda (coincidencia parcial sobre las 3 columnas)
filtered = df
if search_q:
    q = str(search_q).strip()
    try:
        mask = (
            df["dataset_id"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title_es"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = df[mask]
    except Exception as e:
        st.error(f"Error al filtrar: {e}")
        st.stop()

# Aplicar ordenación
if sort_column:
    ascending = True if sort_order == "asc" else False
    try:
        filtered = filtered.sort_values(by=sort_column, ascending=ascending)
    except Exception as e:
        st.error(f"Error al ordenar por {sort_column}: {e}")

# Paginación simple
total = len(filtered)
if total == 0:
    st.info("No hay filas que mostrar después de aplicar filtros.")
else:
    pages = (total - 1) // page_size + 1
    page = st.sidebar.number_input("Página", min_value=1, max_value=pages, value=1, step=1)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = filtered.iloc[start:end].copy()

    # Añadir columna de enumeración relativa a la página (1..k)
    page_df.insert(0, "#", range(1, len(page_df) + 1))

    # Seleccionar y limitar las columnas visibles exactamente a '#', 'dataset_id', 'title', 'title_es'
    visible_cols = ["#", "dataset_id", "title", "title_es"]
    # Filtrar sólo las columnas que existan para evitar KeyError (aunque las validamos antes)
    visible_cols = [c for c in visible_cols if c in page_df.columns]

    st.write(f"Mostrando filas {start + 1}–{min(end, total)} de {total}")
    st.dataframe(page_df[visible_cols], use_container_width=True)


# Footer
st.write("---")
st.caption("Fuente esperada: data/pydataset_list_translated.xlsx")
