"""
Pacote Lexer - MiniC
====================

Estrutura do pacote:
    token_types.py     -> TokenType (Enum) e RESERVED_WORDS (palavras reservadas)
    tokens.py          -> Token (dataclass): tipo, lexema, linha, coluna, atributo
    errors.py          -> hierarquia de LexicalError (diagnóstico de erros léxicos)
    scanner.py         -> classe Scanner (motor da análise léxica)
    analysis_result.py -> agrupador de tokens e erros
    jsonl_serializer.py-> serialização para conformidade com fixtures

Uso básico:
    from src.lexer import Scanner

    scanner = Scanner(codigo_fonte)
    tokens = scanner.scan_tokens()
"""

from .analysis_result import AnalysisResult
from .errors import (
    InvalidIdentifierError,
    InvalidSymbolError,
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
    "AnalysisResult",
    "LexicalError",
    "InvalidSymbolError",
    "InvalidIdentifierError",
    "MalformedRealLiteralError",
    "UnterminatedStringError",
    "UnterminatedCommentError",
    "UnterminatedCharError",
]

__version__ = "1.0.0"
