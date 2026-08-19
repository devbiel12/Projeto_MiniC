"""
scanner.py

"""

import sys
from pathlib import Path

# Adiciona tanto a raiz quanto a subpasta ProjetoMiniC ao sys.path
DIRETORIO_RAIZ = Path(__file__).resolve().parent
for caminho in (DIRETORIO_RAIZ, DIRETORIO_RAIZ / "ProjetoMiniC"):
    if caminho.exists() and str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

try:
    from src.lexer.scanner import Scanner, main
except ModuleNotFoundError:
    from ProjetoMiniC.src.lexer.scanner import Scanner, main

if __name__ == "__main__":
    sys.exit(main())