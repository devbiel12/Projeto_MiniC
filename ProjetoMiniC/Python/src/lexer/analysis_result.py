"""Estruturas de resultado da análise léxica.

Separar o resultado do scanner do formato de apresentação facilita a
integração futura com o parser e com serializadores externos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import LexicalError
from .tokens import Token


@dataclass(slots=True)
class AnalysisResult:
    """Agrupa os tokens e erros produzidos por uma análise léxica."""

    tokens: list[Token]
    errors: list[LexicalError]

@dataclass(slots=True)
class AnalysisView:
    """Representa uma análise pronta para exibição e exportação."""

    title: str
    source: str
    result: AnalysisResult
    formatted_output: str
    tokens_jsonl: str
    errors_jsonl: str
    source_path: Path | None = None