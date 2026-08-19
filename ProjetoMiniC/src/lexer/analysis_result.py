"""
analysis_result.py
==================

Estruturas de dados que agrupam o resultado de uma análise léxica.
Compatível com Python 3.8+.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .errors import LexicalError
from .tokens import Token


@dataclass
class AnalysisResult:
    tokens: List[Token] = field(default_factory=list)
    errors: List[LexicalError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class AnalysisView:
    title: str
    source: str
    result: AnalysisResult
    formatted_output: str
    tokens_jsonl: str = ""
    errors_jsonl: str = ""
    source_path: Optional[Path] = None
