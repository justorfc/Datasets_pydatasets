"""Página: Pydataset — Catálogo traducido

Esta página contiene la lógica del catálogo que antes vivía en `app.py`.
"""
from __future__ import annotations

import io
from pathlib import Path
from datetime import datetime
from typing import List
import json

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


DATA_FILE = Path(__file__).parent.parent / "data" / "pydataset_list_translated.xlsx"

st.set_page_config(page_title="Pydataset — Catálogo traducido", layout="wide")

st.title("Pydataset — Catálogo traducido")


def _check_pydataset_import():
    try:
        import importlib
        mod = importlib.import_module("pydataset")
        ver = getattr(mod, "__version__", None)
        return True, ver
    except Exception as e:
        return False, str(e)


available_pydataset, pydataset_info = _check_pydataset_import()
with st.sidebar:
    st.markdown("---")
    if available_pydataset:
        st.success(f"pydataset disponible — versión: {pydataset_info}")
    else:
        st.error(f"pydataset NO disponible: {pydataset_info}")


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


@st.cache_data
def load_dataset_by_name(name: str):
    """Cargar un dataset de pydataset por nombre. Devuelve un DataFrame.

    Lanza ImportError si pydataset no está disponible y RuntimeError si la carga falla.
    """
    try:
        from pydataset import data
    except Exception as e:
        raise ImportError(f"pydataset no disponible: {e}")
    try:
        df = data(name)
        return df
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar dataset {name}: {e}")


required_columns = {"dataset_id", "title", "title_es"}

uploaded_bytes = None
sheet_to_use = None

if DATA_FILE.exists():
    try:
        sheets = get_sheet_names_from_path(DATA_FILE)
        if len(sheets) > 1:
            sheet_to_use = st.sidebar.selectbox("Seleccionar hoja", options=sheets, index=0)
        df = load_data_from_path(DATA_FILE, sheet_name=sheet_to_use)
        if isinstance(df, dict):
            if sheet_to_use and sheet_to_use in df:
                df = df[sheet_to_use]
            else:
                df = next(iter(df.values()))
        file_source = DATA_FILE.name
        try:
            file_mtime = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
        except Exception:
            file_mtime = datetime.now()
    except Exception as e:
        st.error(f"Error al leer el archivo Excel en {DATA_FILE}: {e}")
        st.stop()
else:
    st.warning("No se encontró `data/pydataset_list_translated.xlsx`. Puedes subirlo usando el cargador abajo or colocar el archivo en la carpeta `data/`." )
    uploaded = st.file_uploader("Sube pydataset_list_translated.xlsx", type=["xlsx", "xls"], accept_multiple_files=False)
    if uploaded is None:
        st.stop()
    try:
        uploaded_bytes = uploaded.read()
        sheets = get_sheet_names_from_bytes(uploaded_bytes)
        if len(sheets) > 1:
            sheet_to_use = st.sidebar.selectbox("Seleccionar hoja (archivo subido)", options=sheets, index=0)
        df = load_data_from_bytes(uploaded_bytes, sheet_name=sheet_to_use)
        if isinstance(df, dict):
            if sheet_to_use and sheet_to_use in df:
                df = df[sheet_to_use]
            else:
                df = next(iter(df.values()))
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

st.success(f"Cargado: {file_source} — {len(df)} filas, {len(df.columns)} columnas")

# Barra lateral: controles
st.sidebar.header("Controles")
search_q = st.sidebar.text_input("Buscar (dataset_id, title, title_es)")

st.sidebar.markdown("---")
show_codes = st.sidebar.checkbox("Mostrar códigos disponibles para copiar")
code_filter = st.sidebar.text_input("Filtrar códigos (nombre)")

def list_code_files() -> List[str]:
    p = Path(__file__).parent / ".." / "codigos"
    p = p.resolve()
    if not p.exists():
        return []
    files = sorted([f.name for f in p.glob('*.md')])
    return files

def read_code_file(name: str) -> str:
    p = Path(__file__).parent / ".." / "codigos" / name
    p = p.resolve()
    if not p.exists():
        return ""
    return p.read_text(encoding='utf-8')

def write_code_file(name: str, content: str) -> None:
    p = Path(__file__).parent / ".." / "codigos" / name
    p = p.resolve()
    p.write_text(content, encoding='utf-8')

page_size = st.sidebar.selectbox("Tamaño de página", options=[10, 25, 50, 100], index=1)
sort_column = st.sidebar.selectbox("Ordenar por columna", options=[None] + list(df.columns), index=0)
sort_order = st.sidebar.radio("Orden", options=["asc", "desc"], index=0, horizontal=True)

total_pages = max(1, (len(df) - 1) // page_size + 1)
page = st.sidebar.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

page_df, total_filtered, start_idx, end_idx = filter_sort_paginate(
    df, search_q=search_q, sort_column=sort_column, sort_order=sort_order, page_size=page_size, page=page
)

if total_filtered == 0:
    st.info("No hay filas que mostrar después de aplicar filtros.")
else:
    colm1, colm2, _ = st.columns([1, 1, 4])
    total_all = len(df)
    with colm1:
        st.metric(label="Total registros", value=f"{total_all:,}")
    with colm2:
        st.metric(label="Registros filtrados", value=f"{total_filtered:,}")

    st.write(f"Mostrando {start_idx + 1}–{end_idx} de {total_filtered} registros filtrados")

    filtered_full = apply_filter_sort(df, search_q=search_q, sort_column=sort_column, sort_order=sort_order)
    csv_full = filtered_full.to_csv(index=False).encode("utf-8")
    csv_page = page_df.drop(columns=[c for c in page_df.columns if c == "#"], errors="ignore").to_csv(index=False).encode("utf-8")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.download_button("Descargar CSV (filtrado completo)", data=csv_full, file_name="pydataset_filtered.csv", mime="text/csv")
    with col2:
        st.download_button("Descargar CSV (página visible)", data=csv_page, file_name="pydataset_page.csv", mime="text/csv")
    st.dataframe(page_df, use_container_width=True)

    # Selector desplegable para elegir un dataset (desde los resultados filtrados)
    try:
        available_ids = list(filtered_full['dataset_id'].astype(str).unique())
    except Exception:
        available_ids = list(df['dataset_id'].astype(str).unique())

    if available_ids:
        selected_dataset = st.selectbox('Seleccionar dataset (desde resultados)', options=sorted(available_ids), key='catalog_selected')
        st.markdown(f"**Seleccionado:** `{selected_dataset}`")
    else:
        st.info('No hay datasets disponibles para seleccionar.')

    # Mostrar preview del dataset seleccionado con paginado, estadísticas y vistas categóricas
    if 'selected_dataset' in locals() and selected_dataset:
        st.markdown("---")
        st.header("Vista previa del dataset")
        try:
            with st.spinner(f"Cargando dataset `{selected_dataset}` ..."):
                df_selected = load_dataset_by_name(selected_dataset)

            if df_selected is None:
                st.warning(f"El dataset `{selected_dataset}` devolvió None.")
            else:
                # Forma y metadatos básicos
                try:
                    nrows, ncols = df_selected.shape
                except Exception:
                    nrows = len(df_selected) if hasattr(df_selected, '__len__') else 'N/A'
                    ncols = len(df_selected.columns) if hasattr(df_selected, 'columns') else 'N/A'

                st.write(f"Forma: {nrows} filas x {ncols} columnas")

                # Controles de paginado para la vista previa
                preview_col1, preview_col2 = st.columns([1, 3])
                with preview_col1:
                    preview_page_size = st.number_input("Filas por página", min_value=5, max_value=1000, value=20, step=5, key='preview_page_size')
                    total_pages_preview = max(1, (nrows - 1) // preview_page_size + 1) if isinstance(nrows, int) else 1
                    preview_page = st.number_input("Página (preview)", min_value=1, max_value=total_pages_preview, value=1, step=1, key='preview_page')
                with preview_col2:
                    st.markdown("_Navega por las primeras filas del dataset completo._")

                # Seleccionar rango y mostrar subset
                try:
                    start = (preview_page - 1) * preview_page_size
                    end = min(start + preview_page_size, nrows) if isinstance(nrows, int) else None
                    if end is None:
                        preview_df = df_selected.head(preview_page_size)
                    else:
                        preview_df = df_selected.iloc[start:end]
                    st.dataframe(preview_df, use_container_width=True)
                    st.write(f"Mostrando filas {start + 1}–{end if end is not None else '∞'}")
                except Exception as e:
                    st.error(f"No se pudo mostrar preview: {e}")

                # Tipos de columnas
                try:
                    dtypes = pd.DataFrame({'column': list(df_selected.columns), 'dtype': [str(t) for t in df_selected.dtypes]})
                    with st.expander("Tipos de columnas", expanded=False):
                        st.dataframe(dtypes, use_container_width=True)
                except Exception:
                    pass

                # Estadísticas resumidas (describe)
                try:
                    with st.expander("Estadísticas resumidas (describe)", expanded=False):
                        desc_num = df_selected.describe(include=["number"]).transpose()
                        desc_all = df_selected.describe(include='all').transpose()
                        st.markdown("**Numéricas**")
                        st.dataframe(desc_num, use_container_width=True)
                        st.markdown("**Todas (incluye categóricas)**")
                        st.dataframe(desc_all, use_container_width=True)
                except Exception as e:
                    st.warning(f"No se pudieron calcular estadísticas: {e}")

                # Vistas de columnas categóricas (value_counts)
                try:
                    with st.expander("Columnas categóricas (value_counts)", expanded=False):
                        # detectar columnas categóricas o de baja cardinalidad
                        cat_cols = [c for c in df_selected.columns if (str(df_selected[c].dtype) == 'object') or (pd.api.types.is_categorical_dtype(df_selected[c]))]
                        # incluir columnas con baja cardinalidad
                        low_card_cols = [c for c in df_selected.columns if df_selected[c].nunique(dropna=False) <= 50]
                        cols_to_show = sorted(set(cat_cols + low_card_cols))
                        if not cols_to_show:
                            st.info("No se detectaron columnas categóricas o de baja cardinalidad.")
                        else:
                            for c in cols_to_show:
                                with st.expander(f"{c} (valores)", expanded=False):
                                    try:
                                        vc = df_selected[c].value_counts(dropna=False).head(100)
                                        st.dataframe(vc.rename_axis(c).reset_index(name='count'))
                                    except Exception as e:
                                        st.write(f"No se pudo calcular value_counts para {c}: {e}")
                except Exception as e:
                    st.warning(f"Error al generar vistas categóricas: {e}")

                # Descarga CSV del dataset completo
                try:
                    csv_bytes = df_selected.to_csv(index=False).encode('utf-8')
                    st.download_button(label=f"Descargar `{selected_dataset}` como CSV", data=csv_bytes, file_name=f"{selected_dataset}.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"No se pudo preparar descarga CSV: {e}")

        except ImportError as ie:
            st.error(str(ie))
        except RuntimeError as re:
            st.error(str(re))
        except Exception as e:
            st.error(f"Error inesperado al cargar `{selected_dataset}`: {e}")

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
