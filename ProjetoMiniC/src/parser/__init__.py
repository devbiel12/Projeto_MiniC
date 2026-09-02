"""
Pacote Parser - MiniC
=====================
Analisador sintático por descida recursiva. Consome os tokens produzidos
pelo Scanner existente (src.lexer) e produz uma AST (src.ast).

Uso básico:
    from src.lexer import Scanner
    from src.parser import Parser

    tokens = Scanner(codigo_fonte).scan_tokens()
    parser = Parser(tokens)
    programa = parser.parse()
"""

from .errors import ErroSintatico
from .parser import Parser

__all__ = ["Parser", "ErroSintatico"]

__version__ = "1.0.0"
