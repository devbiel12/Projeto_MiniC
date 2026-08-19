"""
minic_scanner
=============


Estrutura do pacote
--------------------
    token_types.py  -> TokenType (Enum) e RESERVED_WORDS (palavras reservadas)
    tokens.py       -> Token (dataclass): tipo, lexema, linha, coluna, atributo
    errors.py       -> hierarquia de LexicalError (diagnóstico de erros)
    scanner.py      -> classe Scanner (motor da análise léxica)
    demo.py         -> testes/demonstração (bloco executável)

Cada módulo tem uma única responsabilidade, o que facilita localizar,
testar e evoluir cada parte do scanner de forma independente.

Uso básico
----------
    from minic_scanner import Scanner

    scanner = Scanner(codigo_fonte)
    tokens = scanner.scan_tokens()
    scanner.print_tokens()
    scanner.print_errors()

Executar a demonstração
------------------------
    python -m minic_scanner
"""

from .errors import (
    InvalidSymbolError,
    InvalidIdentifierError,
    LexicalError,
    MalformedRealLiteralError,
    UnterminatedCharError,
    UnterminatedCommentError,
    UnterminatedStringError,
)
from .scanner import Scanner
from .token_types import RESERVED_WORDS, TokenType
from .tokens import Token

__all__ = [
    "Scanner",
    "Token",
    "TokenType",
    "RESERVED_WORDS",
    "LexicalError",
    "InvalidSymbolError",
    "InvalidIdentifierError",
    "MalformedRealLiteralError",
    "UnterminatedStringError",
    "UnterminatedCommentError",
    "UnterminatedCharError",
]

__version__ = "1.0.0"
