"""Serialização JSONL acadêmica para o MiniC.

O scanner continua responsável apenas por analisar o código-fonte. Este
módulo traduz o resultado interno para o formato acadêmico exigido pelo
professor, preservando ordem, posição e atributos.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Sequence

from .errors import LexicalError
from .token_types import TokenType
from .tokens import Token


ACADEMIC_TOKEN_NAMES: dict[TokenType, str] = {
    TokenType.KW_INT: "INT",
    TokenType.KW_FLOAT: "FLOAT",
    TokenType.KW_BOOL: "BOOL",
    TokenType.KW_CHAR: "CHAR",
    TokenType.KW_DOUBLE: "DOUBLE",
    TokenType.KW_VOID: "VOID",
    TokenType.KW_IF: "IF",
    TokenType.KW_ELSE: "ELSE",
    TokenType.KW_WHILE: "WHILE",
    TokenType.KW_FOR: "FOR",
    TokenType.KW_RETURN: "RETURN",
    TokenType.KW_BREAK: "BREAK",
    TokenType.KW_CONTINUE: "CONTINUE",
    TokenType.KW_TRUE: "TRUE",
    TokenType.KW_FALSE: "FALSE",
    TokenType.KW_PRINT: "PRINT",
    TokenType.KW_READ: "READ",
    TokenType.ID: "IDENT",
    TokenType.NUM_INT: "INT_LIT",
    TokenType.NUM_FLOAT: "FLOAT_LIT",
    TokenType.CHAR_LITERAL: "CHAR_LIT",
    TokenType.STRING: "STRING_LIT",
    TokenType.PLUS: "PLUS",
    TokenType.MINUS: "MINUS",
    TokenType.STAR: "STAR",
    TokenType.SLASH: "SLASH",
    TokenType.PERCENT: "PERCENT",
    TokenType.ASSIGN: "ASSIGN",
    TokenType.EQ: "EQ",
    TokenType.NEQ: "NEQ",
    TokenType.LT: "LT",
    TokenType.LE: "LE",
    TokenType.GT: "GT",
    TokenType.GE: "GE",
    TokenType.AND: "AND",
    TokenType.OR: "OR",
    TokenType.NOT: "NOT",
    TokenType.LPAREN: "LPAREN",
    TokenType.RPAREN: "RPAREN",
    TokenType.LBRACE: "LBRACE",
    TokenType.RBRACE: "RBRACE",
    TokenType.LBRACKET: "LBRACKET",
    TokenType.RBRACKET: "RBRACKET",
    TokenType.SEMI: "SEMICOLON",
    TokenType.COMMA: "COMMA",
    TokenType.DOT: "DOT",
    TokenType.EOF: "EOF",
}


@dataclass(frozen=True, slots=True)
class AcademicTokenRecord:
    """Representa um token no formato acadêmico JSONL."""

    token: str
    lexeme: str
    attribute: int | float | str | None
    line: int
    column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "token": self.token,
            "lexeme": self.lexeme,
            "attribute": self.attribute,
            "line": self.line,
            "column": self.column,
        }


@dataclass(frozen=True, slots=True)
class AcademicErrorRecord:
    """Representa um erro léxico no formato acadêmico JSONL."""

    error: str
    lexeme: str
    line: int
    column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "error": self.error,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
        }


def _academic_token_name(token_type: TokenType) -> str:
    try:
        return ACADEMIC_TOKEN_NAMES[token_type]
    except KeyError as exc:  # pragma: no cover - proteção para novos tipos futuros
        raise ValueError(f"Token interno sem mapeamento acadêmico: {token_type!r}") from exc


def _token_attribute(token: Token) -> int | float | str | None:
    if token.type is TokenType.ID:
        return token.lexeme
    if token.type is TokenType.NUM_INT:
        return int(token.lexeme)
    if token.type is TokenType.NUM_FLOAT:
        return float(token.lexeme)
    return token.attribute if token.attribute is not None else None


def token_to_academic_record(token: Token) -> AcademicTokenRecord:
    """Converte um token interno para o registro acadêmico."""

    return AcademicTokenRecord(
        token=_academic_token_name(token.type),
        lexeme=token.lexeme,
        attribute=_token_attribute(token),
        line=token.line,
        column=token.column,
    )


def error_to_academic_record(error: LexicalError) -> AcademicErrorRecord:
    """Converte um erro interno para o registro acadêmico."""

    return AcademicErrorRecord(
        error=error.code,
        lexeme=error.lexeme,
        line=error.line,
        column=error.column,
    )


def serialize_tokens_jsonl(tokens: Sequence[Token]) -> str:
    """Gera o JSONL acadêmico dos tokens, incluindo EOF como último registro."""

    academic_tokens = [token for token in tokens if token.type is not TokenType.ERROR]
    records = [token_to_academic_record(token).to_dict() for token in academic_tokens]
    if not records or records[-1]["token"] != "EOF":
        raise ValueError("A lista de tokens precisa terminar com EOF.")
    return "\n".join(json.dumps(record, ensure_ascii=False) for record in records)


def serialize_errors_jsonl(errors: Iterable[LexicalError]) -> str:
    """Gera o JSONL acadêmico dos erros léxicos."""

    records = [error_to_academic_record(error).to_dict() for error in errors]
    return "\n".join(json.dumps(record, ensure_ascii=False) for record in records)