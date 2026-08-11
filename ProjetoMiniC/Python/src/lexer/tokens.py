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

    @property
    def is_keyword(self) -> bool:
        """True se o token corresponde a uma palavra reservada da linguagem."""
        # Verifica se o token pertence ao conjunto de palavras da linguagem.
        return self.type in RESERVED_WORDS.values()

    def as_row(self) -> tuple:
        """Retorna a tupla (nome, lexema, linha, coluna, atributo) para tabelas."""
        # Converte o atributo em texto para facilitar a impressão em tabelas.
        attr = "" if self.attribute is None else str(self.attribute)
        return (self.type.name, self.lexeme, self.line, self.column, attr)

    def __str__(self) -> str:
        # Gera uma representação legível do token para depuração.
        nome, lexema, linha, coluna, attr = self.as_row()
        return (f"{nome:<14} lexema={lexema!r:<16} "
                f"lin={linha:<4} col={coluna:<4} attr={attr}")
