"""
tokens.py
=========

Define a estrutura de dados `Token`: tipo, lexema, linha, coluna e
atributo — os cinco campos exigidos pela Etapa 1 do projeto.

Depende apenas de `token_types.py`.
"""

from dataclasses import dataclass
from typing import Optional, Union

from .token_types import RESERVED_WORDS, TokenType

Attribute = Optional[Union[int, float, str]]


# ------------------------------------------------------------------
# A estrutura Token representa a unidade mínima reconhecida pelo lexer.
# Cada token guarda o tipo, o texto original do código, a posição e,
# quando necessário, um valor semântico (como o número 42 ou a string).
# ------------------------------------------------------------------
@dataclass
class Token:
    """Representa um token: tipo, lexema, posição (linha/coluna) e atributo."""

    type: TokenType
    lexeme: str
    line: int
    column: int
    attribute: Attribute = None

    def display_type_name(self) -> str:
        """Retorna o nome externo esperado pelos fixtures do professor."""
        mapping = {
            "KW_BOOL": "BOOL",
            "KW_INT": "INT",
            "KW_FLOAT": "FLOAT",
            "KW_CHAR": "CHAR",
            "KW_DOUBLE": "DOUBLE",
            "KW_VOID": "VOID",
            "KW_TRUE": "TRUE",
            "KW_FALSE": "FALSE",
            "NUM_INT": "INT_LIT",
            "NUM_FLOAT": "FLOAT_LIT",
            "STRING": "STRING_LIT",
            "CHAR_LITERAL": "CHAR_LIT",
            "SEMI": "SEMICOLON",
        }
        return mapping.get(self.type.name, self.type.name)

    @property
    def is_keyword(self) -> bool:
        """True se o token corresponde a uma palavra reservada da linguagem."""
        # Verifica se o token pertence ao conjunto de palavras da linguagem.
        return self.type in RESERVED_WORDS.values()

    def as_row(self) -> tuple:
        """Retorna a tupla (nome, lexema, linha, coluna, atributo) para tabelas."""
        # Converte o atributo em texto para facilitar a impressão em tabelas.
        attr = "" if self.attribute is None else str(self.attribute)
        return (self.display_type_name(), self.lexeme, self.line, self.column, attr)

    def as_record(self) -> dict:
        """Retorna uma representação serializável para JSONL."""
        return {
            "type": self.display_type_name(),
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "attribute": self.attribute,
        }

    def __str__(self) -> str:
        # Gera uma representação legível do token para depuração.
        nome, lexema, linha, coluna, attr = self.as_row()
        return (f"{nome:<14} lexema={lexema!r:<16} "
                f"lin={linha:<4} col={coluna:<4} attr={attr}")
