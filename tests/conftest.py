import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path para que tests puedan importar app
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
