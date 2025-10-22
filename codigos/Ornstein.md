```python
# Código Colab para dataset: Ornstein

import pandas as pd
import io
from IPython.display import display

# 1) Cargar el dataset
try:
    try:
        df = pd.read_csv('data/Ornstein.csv')
        print('Cargado desde data/Ornstein.csv')
    except Exception:
        df = pd.read_excel('data/Ornstein.xlsx', engine='openpyxl')
        print('Cargado desde data/Ornstein.xlsx')
except Exception:
    try:
        from google.colab import files
        uploaded = files.upload()
        if uploaded:
            # uploaded is a dict {filename: bytes}
            fname, content = next(iter(uploaded.items()))
            if fname.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            else:
                df = pd.read_csv(io.BytesIO(content))
            print('Archivo subido y cargado: {}'.format(fname))
        else:
            raise FileNotFoundError('No se proporcionó archivo')
    except Exception as e:
        raise RuntimeError('No se pudo cargar el dataset: ' + str(e))

# 2) Mostrar el dataset (primeras filas)
display(df.head())

# 3) info() del dataset
print('\nInfo del DataFrame:')
df.info()

# 4) describe() del dataset
print('\nDescribe:')
display(df.describe(include='all'))
```
