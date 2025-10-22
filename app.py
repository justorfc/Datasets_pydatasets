import streamlit as st
import pandas as pd
import json
import io
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
from typing import List

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


@st.cache_data
def get_sheet_names_from_path(path: str | Path):
    x = pd.ExcelFile(path, engine="openpyxl")
    return x.sheet_names


@st.cache_data
def get_sheet_names_from_bytes(data: bytes):
    x = pd.ExcelFile(io.BytesIO(data), engine="openpyxl")
    return x.sheet_names


@st.cache_data
def load_data_from_path(path: str | Path, sheet_name=None):
    return pd.read_excel(path, engine="openpyxl", sheet_name=sheet_name)


@st.cache_data
def load_data_from_bytes(data: bytes, sheet_name=None):
    return pd.read_excel(io.BytesIO(data), engine="openpyxl", sheet_name=sheet_name)


def filter_sort_paginate(df: pd.DataFrame, search_q: str = "", sort_column: str | None = None,
                         sort_order: str = "asc", page_size: int = 25, page: int = 1):
    """Filtra, ordena y pagina un DataFrame según los parámetros usados en la app.

    Devuelve (page_df, total, start, end) donde page_df ya contiene la columna de enumeración '#'.
    Mantiene compatibilidad con llamadas que desempaquetan sólo (page_df, total).
    """
    filtered = df
    if search_q:
        q = str(search_q).strip()
        mask = (
            df["dataset_id"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title_es"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = df[mask]

    if sort_column:
        ascending = True if sort_order == "asc" else False
        try:
            filtered = filtered.sort_values(by=sort_column, ascending=ascending)
        except Exception:
            # En caso de error al ordenar, devolvemos sin ordenar
            pass

    total = len(filtered)
    if total == 0:
        return filtered.copy(), 0, 0, 0

    pages = (total - 1) // page_size + 1
    page = max(1, min(page, pages))
    start = (page - 1) * page_size
    end = min(start + page_size, total)
    page_df = filtered.iloc[start:end].copy()
    page_df.insert(0, "#", range(1, len(page_df) + 1))

    visible_cols = ["#", "dataset_id", "title", "title_es"]
    visible_cols = [c for c in visible_cols if c in page_df.columns]
    return page_df[visible_cols], total, start, end


def apply_filter_sort(df: pd.DataFrame, search_q: str = "", sort_column: str | None = None,
                      sort_order: str = "asc") -> pd.DataFrame:
    """Devuelve el DataFrame filtrado y ordenado (sin paginar)."""
    filtered = df
    if search_q:
        q = str(search_q).strip()
        mask = (
            df["dataset_id"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title"].astype(str).str.contains(q, case=False, na=False)
        ) | (
            df["title_es"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = df[mask]

    if sort_column:
        ascending = True if sort_order == "asc" else False
        try:
            filtered = filtered.sort_values(by=sort_column, ascending=ascending)
        except Exception:
            pass

    return filtered


required_columns = {"dataset_id", "title", "title_es"}

uploaded_bytes = None
sheet_to_use = None

if DATA_FILE.exists():
    try:
        sheets = get_sheet_names_from_path(DATA_FILE)
        if len(sheets) > 1:
            sheet_to_use = st.sidebar.selectbox("Seleccionar hoja", options=sheets, index=0)
        df = load_data_from_path(DATA_FILE, sheet_name=sheet_to_use)
        # pd.read_excel(..., sheet_name=None) devuelve un dict de DataFrames. Normalizamos a un DataFrame.
        if isinstance(df, dict):
            if sheet_to_use and sheet_to_use in df:
                df = df[sheet_to_use]
            else:
                # tomar la primera hoja disponible
                df = next(iter(df.values()))
        # Información del archivo en disco
        file_source = DATA_FILE.name
        try:
            file_mtime = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
        except Exception:
            file_mtime = datetime.now()
    except Exception as e:
        st.error(f"Error al leer el archivo Excel en {DATA_FILE}: {e}")
        st.stop()
else:
    st.warning(
        "No se encontró `data/pydataset_list_translated.xlsx`. Puedes subirlo usando el cargador abajo or colocar el archivo en la carpeta `data/`."
    )
    uploaded = st.file_uploader("Sube pydataset_list_translated.xlsx", type=["xlsx", "xls"], accept_multiple_files=False)
    if uploaded is None:
        st.stop()
    try:
        uploaded_bytes = uploaded.read()
        sheets = get_sheet_names_from_bytes(uploaded_bytes)
        if len(sheets) > 1:
            sheet_to_use = st.sidebar.selectbox("Seleccionar hoja (archivo subido)", options=sheets, index=0)
        df = load_data_from_bytes(uploaded_bytes, sheet_name=sheet_to_use)
        # Normalizar si pandas devolvió un dict (múltiples hojas y sheet_name=None)
        if isinstance(df, dict):
            if sheet_to_use and sheet_to_use in df:
                df = df[sheet_to_use]
            else:
                df = next(iter(df.values()))
        # Información del archivo subido
        file_source = getattr(uploaded, "name", "archivo_subido.xlsx")
        file_mtime = datetime.now()
    except Exception as e:
        st.error(f"Error al leer el archivo Excel subido: {e}")
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

# Sección para mostrar/copiar códigos
st.sidebar.markdown("---")
show_codes = st.sidebar.checkbox("Mostrar códigos disponibles para copiar")
code_filter = st.sidebar.text_input("Filtrar códigos (nombre)")

def list_code_files() -> List[str]: 
    p = Path(__file__).parent / "codigos"
    if not p.exists():
        return []
    files = sorted([f.name for f in p.glob('*.md')])
    return files

def read_code_file(name: str) -> str:
    p = Path(__file__).parent / "codigos" / name
    if not p.exists():
        return ""
    return p.read_text(encoding='utf-8')

def write_code_file(name: str, content: str) -> None:
    p = Path(__file__).parent / "codigos" / name
    p.write_text(content, encoding='utf-8')

page_size = st.sidebar.selectbox("Tamaño de página", options=[10, 25, 50, 100], index=1)

# Selector de columna para ordenación (solo columnas existentes)
sort_column = st.sidebar.selectbox("Ordenar por columna", options=[None] + list(df.columns), index=0)
sort_order = st.sidebar.radio("Orden", options=["asc", "desc"], index=0, horizontal=True)

# Usar la función helper para filtrar, ordenar y paginar
total_pages = max(1, (len(df) - 1) // page_size + 1)
page = st.sidebar.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

page_df, total_filtered, start_idx, end_idx = filter_sort_paginate(
    df, search_q=search_q, sort_column=sort_column, sort_order=sort_order, page_size=page_size, page=page
)

if total_filtered == 0:
    st.info("No hay filas que mostrar después de aplicar filtros.")
else:
    # Mostrar métricas: total y filtrado
    colm1, colm2, _ = st.columns([1, 1, 4])
    total_all = len(df)
    with colm1:
        st.metric(label="Total registros", value=f"{total_all:,}")
    with colm2:
        st.metric(label="Registros filtrados", value=f"{total_filtered:,}")

    # Mostrar resumen superior
    st.write(f"Mostrando {start_idx + 1}–{end_idx} de {total_filtered} registros filtrados")

    # Preparar CSVs para descarga
    filtered_full = apply_filter_sort(df, search_q=search_q, sort_column=sort_column, sort_order=sort_order)
    csv_full = filtered_full.to_csv(index=False).encode("utf-8")
    csv_page = page_df.drop(columns=[c for c in page_df.columns if c == "#"], errors="ignore").to_csv(index=False).encode("utf-8")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.download_button("Descargar CSV (filtrado completo)", data=csv_full, file_name="pydataset_filtered.csv", mime="text/csv")
    with col2:
        st.download_button("Descargar CSV (página visible)", data=csv_page, file_name="pydataset_page.csv", mime="text/csv")
    # Mostrar la tabla principal (siempre visible)
    st.dataframe(page_df, use_container_width=True)

    # Código browsing: mostrar y copiar archivos .md en `codigos/`
    if show_codes:
        st.sidebar.markdown("## Códigos disponibles")
        files = list_code_files()
        if not files:
            st.sidebar.info("No se encontraron archivos en la carpeta `codigos/`.")
        else:
            if code_filter:
                files = [f for f in files if code_filter.lower() in f.lower()]
            sel = st.sidebar.selectbox("Selecciona un archivo", options=files)
            content = read_code_file(sel)
            st.sidebar.markdown("#### Contenido (preview)")

            # Preview compacto por defecto; mostrar completo en la sidebar si el archivo es pequeño
            PREVIEW_MAX_LINES = 10
            PREVIEW_MAX_CHARS = 1200
            show_full_if_small = st.sidebar.checkbox("Mostrar completo en sidebar si es corto", value=True)

            content_str = content or ""
            content_lines = content_str.splitlines()
            n_lines = len(content_lines)
            n_chars = len(content_str)

            def sidebar_show_full(text: str):
                with st.sidebar.expander("Mostrar contenido completo", expanded=False):
                    st.code(text, language='python')

            if show_full_if_small and (n_lines <= PREVIEW_MAX_LINES and n_chars <= PREVIEW_MAX_CHARS):
                st.sidebar.code(content_str, language='python')
            else:
                preview_lines = content_lines[:PREVIEW_MAX_LINES]
                preview = "\n".join(preview_lines)
                if len(preview) > PREVIEW_MAX_CHARS:
                    preview = preview[:PREVIEW_MAX_CHARS] + "\n\n... (preview truncado por caracteres)"
                else:
                    if n_lines > PREVIEW_MAX_LINES:
                        preview += f"\n\n... (archivo truncado: mostrando {PREVIEW_MAX_LINES} de {n_lines} líneas, pulsa 'Mostrar contenido completo' para ver todo)"

                st.sidebar.code(preview, language='python')
                sidebar_show_full(content_str)

            # Editor y acciones en el área principal
            st.markdown("## Editor de código seleccionado")
            edited = st.text_area(f"Editar código (archivo: {sel})", value=content, height=400)

            col_save, col_dl = st.columns([1, 1])
            with col_save:
                if st.button("Guardar cambios"):
                    try:
                        write_code_file(sel, edited)
                        st.success(f"Guardado {sel}")
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
            with col_dl:
                st.download_button(label="Descargar archivo .md", data=edited, file_name=sel, mime="text/markdown")

            # Construir HTML/JS sin usar f-string para evitar colisiones con llaves de JS
            js_fn = (
                "<script>\n"
                "async function copyText(text){\n"
                "  try{\n"
                "    await navigator.clipboard.writeText(text);\n"
                "    const btn = document.getElementById('copy-btn');\n"
                "    if(btn) btn.innerText = 'Copiado ✅';\n"
                "  }catch(e){\n"
                "    alert('No se pudo copiar al portapapeles: ' + e);\n"
                "  }\n"
                "}\n"
                "</script>\n"
            )
            copy_js = js_fn + "<button id='copy-btn' onclick=\"copyText(" + json.dumps(edited) + ")\">Copiar código para Colab</button>"
            components.html(copy_js, height=80)


# Footer
st.write("---")
try:
    mtime_str = file_mtime.strftime("%Y-%m-%d %H:%M:%S")
except Exception:
    mtime_str = str(file_mtime)
st.caption(f"Fuente: {file_source} — Última actualización: {mtime_str}")
