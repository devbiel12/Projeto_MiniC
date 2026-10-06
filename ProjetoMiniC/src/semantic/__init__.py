"""Análise semântica do compilador MiniC."""

from .semantic import Diagnostic, Scope, SemanticAnalyzer, SemanticResult, Symbol, analyze

__all__ = ["Diagnostic", "Scope", "SemanticAnalyzer", "SemanticResult", "Symbol", "analyze"]
