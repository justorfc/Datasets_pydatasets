import streamlit as st

st.set_page_config(page_title="Pydataset — Presentación", layout="wide")

st.title("Pydataset — Presentación")

st.markdown(
    """
    Bienvenido. Esta es la página de presentación. Usa las páginas del menú lateral para navegar:

    - Catálogo traducido (página): contiene el listado y herramientas de filtrado.
    - Documentación (página): muestra la documentación de cada dataset.
    """
)

# Botones para navegar a las páginas bajo `pages/` (guardamos la URL actual en localStorage para poder volver)
nav_html = '''
<div style="display:flex;gap:8px;align-items:center;padding:6px 4px;border-radius:6px;background:#f6f8fa;max-width:640px">
    <strong style="margin-right:8px">Ir a páginas:</strong>
    <button id="open-catalog" style="padding:6px 10px;border-radius:4px">Catálogo traducido</button>
    <button id="open-doc" style="padding:6px 10px;border-radius:4px">Documentación de pydataset</button>
    <button id="app-doc-copy" style="padding:6px 8px;border-radius:4px">Copiar URL página objetivo</button>
    <span id="app-doc-msg" style="margin-left:8px;color:green"></span>
</div>
<script>
    (function(){
        const base = window.location.origin + '/';
        const catalog = base + '?page=01_Catalogo_traducido.py';
        const doc = base + '?page=02_Documentacion_pydataset.py';

        function saveReturn(){ try{ localStorage.setItem('pydataset_return_url', window.location.href); }catch(e){} }

        document.getElementById('open-catalog').onclick = function(){ saveReturn(); try{ window.location.replace(catalog); }catch(e){ window.open(catalog, '_blank'); } }
        document.getElementById('open-doc').onclick = function(){ saveReturn(); try{ window.location.replace(doc); }catch(e){ window.open(doc, '_blank'); } }

        document.getElementById('app-doc-copy').onclick = async function(){
            try{ const target = document.getElementById('open-doc') ? doc : base; await navigator.clipboard.writeText(target); document.getElementById('app-doc-msg').innerText = 'URL copiada'; }
            catch(e){ document.getElementById('app-doc-msg').innerText = 'Copia manual: ' + (doc); }
        }
    })();
</script>
'''

st.info("Usa la barra lateral 'Pages' para navegar entre 'Catálogo traducido' y 'Documentación de pydataset'.")
