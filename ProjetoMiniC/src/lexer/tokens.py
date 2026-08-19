"""
tokens.py
=========

Estrutura de dados Token com conversão para formato acadêmico.
Compatível com Python 3.8+.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from .token_types import RESERVED_WORDS, TokenType

Attribute = Optional[Union[int, float, str]]


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    attribute: Attribute = None

    def display_type_name(self) -> str:
        """Retorna o nome externo esperado pelos fixtures."""
        mapping = {
            "KW_BOOL": "BOOL",
            "KW_INT": "INT",
            "KW_FLOAT": "FLOAT",
            "KW_CHAR": "CHAR",
            "KW_DOUBLE": "DOUBLE",
            "KW_VOID": "VOID",
            "KW_TRUE": "TRUE",
            "KW_FALSE": "FALSE",
            "KW_IF": "IF",
            "KW_ELSE": "ELSE",
            "KW_WHILE": "WHILE",
            "KW_FOR": "FOR",
            "KW_RETURN": "RETURN",
            "KW_BREAK": "BREAK",
            "KW_CONTINUE": "CONTINUE",
            "KW_PRINT": "PRINT",
            "KW_READ": "READ",
            "ID": "IDENT",
            "NUM_INT": "INT_LIT",
            "NUM_FLOAT": "FLOAT_LIT",
            "STRING": "STRING_LIT",
            "CHAR_LITERAL": "CHAR_LIT",
            "SEMI": "SEMICOLON",
        }
        return mapping.get(self.type.name, self.type.name)

    @property
    def is_keyword(self) -> bool:
        return self.type in RESERVED_WORDS.values()

    def as_row(self) -> tuple:
        attr = "" if self.attribute is None else str(self.attribute)
        return (self.display_type_name(), self.lexeme, self.line, self.column, attr)

    def as_record(self) -> dict:
        return {
            "token": self.display_type_name(),
            "lexeme": self.lexeme,
            "attribute": self.attribute,
            "line": self.line,
            "column": self.column,
        }

    def __str__(self) -> str:
        nome, lexema, linha, coluna, attr = self.as_row()
        return f"{nome:<14} lexema={lexema!r:<16} lin={linha:<4} col={coluna:<4} attr={attr}"
