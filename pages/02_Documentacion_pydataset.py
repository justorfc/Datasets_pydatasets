"""Página: Documentación de pydataset (versión definitiva, limpia).

Esta versión contiene una única implementación minimalista y probada
para evitar errores de indentación tras múltiples ediciones.
"""
from __future__ import annotations

import io
import contextlib
from typing import Optional, Tuple

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def _import_pydataset() -> Tuple[bool, Optional[object], Optional[object], Optional[str]]:
    try:
        from pydataset import data
        try:
            from pydataset import data_info
            return True, data, data_info, None
        except Exception:
            def _fallback(name: str) -> str:
                buf = io.StringIO()
                try:
                    with contextlib.redirect_stdout(buf):
                        _ = data(name, show_doc=True)
                except Exception:
                    pass
                return buf.getvalue()

            return True, data, _fallback, None
    except Exception as e:
        return False, None, None, repr(e)


st.set_page_config(page_title="Documentación de pydataset", layout="wide")


@st.cache_data
def get_catalog() -> pd.DataFrame:
    ok, data_fn, _, err = _import_pydataset()
    if not ok or data_fn is None:
        raise ImportError(f"pydataset no disponible: {err}")
    return data_fn()


@st.cache_data
def get_show_doc(name: str) -> str:
    ok, data_fn, _, err = _import_pydataset()
    if not ok or data_fn is None:
        raise ImportError(f"pydataset no disponible: {err}")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            _ = data_fn(name, show_doc=True)
    except Exception:
        return buf.getvalue()
    return buf.getvalue()


def _nav_html() -> str:
        # Eliminado el control con botones porque puede fallar en iframes.
        # Se recomienda usar la barra lateral "Pages" para navegar entre páginas.
        return ''


def main() -> None:
    st.title('Documentación de pydataset')
    components.html(_nav_html(), height=70)

    ok, _, _, err = _import_pydataset()
    if not ok:
        st.error(f'pydataset no instalado: {err}')
        return

    try:
        df = get_catalog()
    except Exception as e:
        st.error(f'Error cargando catálogo: {e}')
        return

    # Normalizar columnas comunes
    if 'Item' in df.columns and 'dataset_id' not in df.columns:
        df = df.rename(columns={'Item': 'dataset_id'})
    if 'Title' in df.columns and 'title' not in df.columns:
        df = df.rename(columns={'Title': 'title'})
    if 'package' not in df.columns:
        df['package'] = None

    st.markdown('## Catálogo')
    cols = [c for c in ('dataset_id', 'title', 'package') if c in df.columns]
    st.dataframe(df[cols].head(200), use_container_width=True)
    st.download_button('Descargar catálogo CSV', data=df.to_csv(index=False).encode('utf-8'), file_name='pydataset_catalog.csv', mime='text/csv')

    st.markdown('## Detalle')
    ids = sorted(df['dataset_id'].astype(str).unique())
    sel = st.selectbox('Seleccionar dataset_id', options=ids)
    st.subheader(sel)
    sd = get_show_doc(sel)
    if sd:
        st.code(sd, language='text')
        st.download_button('Descargar show_doc', data=sd, file_name=f'{sel}_show_doc.txt', mime='text/plain')


if __name__ == '__main__':
    main()
