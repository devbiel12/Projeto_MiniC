"""
token_types.py
==============

Define os tipos de token (`TokenType`) e o dicionário de palavras
reservadas (`RESERVED_WORDS`) da linguagem MiniC.

Este módulo é a base do pacote: não depende de nenhum outro módulo
interno, apenas da biblioteca padrão (`enum`, `typing`).
"""

from enum import Enum, auto
from typing import Dict


class TokenType(Enum):
    """Enumeração de todos os tipos de token reconhecidos pelo scanner."""

    # ------------------------------------------------------------------
    # A enumeração centraliza todas as categorias léxicas da linguagem.
    # Cada valor representa um tipo de token que o scanner pode produzir.
    # Isso facilita a análise sintática e a geração de diagnósticos.
    # ------------------------------------------------------------------

    # Palavras reservadas
    KW_BOOL = auto()
    KW_INT = auto()
    KW_FLOAT = auto()
    KW_CHAR = auto()
    KW_DOUBLE = auto()
    KW_VOID = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_IF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_RETURN = auto()
    KW_BREAK = auto()
    KW_CONTINUE = auto()
    KW_PRINT = auto()
    KW_READ = auto()

    # Identificador
    ID = auto()

    # Literais
    NUM_INT = auto()
    NUM_FLOAT = auto()
    STRING = auto()
    CHAR_LITERAL = auto()

    # Operadores aritméticos
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Atribuição e relacionais
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Operadores lógicos
    AND = auto()   # &&
    OR = auto()    # ||
    NOT = auto()   # !

    # Delimitadores
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMI = auto()
    COMMA = auto()
    DOT = auto()

    # Controle
    EOF = auto()
    ERROR = auto()   # token inválido, mantido na listagem para diagnóstico


# ------------------------------------------------------------------
# Dicionário que mapeia as palavras reservadas da linguagem MiniC para
# seus respectivos tipos. Quando o scanner encontra uma sequência como
# "if" ou "return", ele reconhece imediatamente o token correto.
# ------------------------------------------------------------------
RESERVED_WORDS: Dict[str, TokenType] = {
    "bool": TokenType.KW_BOOL,
    "int": TokenType.KW_INT,
    "float": TokenType.KW_FLOAT,
    "char": TokenType.KW_CHAR,
    "double": TokenType.KW_DOUBLE,
    "void": TokenType.KW_VOID,
    "true": TokenType.KW_TRUE,
    "false": TokenType.KW_FALSE,
    "if": TokenType.KW_IF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE,
    "for": TokenType.KW_FOR,
    "return": TokenType.KW_RETURN,
    "break": TokenType.KW_BREAK,
    "continue": TokenType.KW_CONTINUE,
    "print": TokenType.KW_PRINT,
    "read": TokenType.KW_READ,
}
