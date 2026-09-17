"""
nodes.py
========
Definição dos nós da Árvore Sintática Abstrata (AST) da linguagem MiniC.

Cada nó representa uma construção semântica do programa (não uma cópia
literal da sintaxe concreta): parênteses de agrupamento, ponto-e-vírgula
e outros detalhes puramente sintáticos não geram nós próprios.

Todos os nós preservam `linha` e `coluna` de origem para diagnósticos
das etapas posteriores (análise semântica, geração de código etc.).

Convenção adotada (compatível com o tutorial de conversão tokens->AST
e com a seção 8 da especificação MiniC):

    Program
    FunctionDecl / VarDecl / Param
    Block
    IfStmt / WhileStmt / ForStmt
    ReturnStmt / BreakStmt / ContinueStmt
    PrintStmt / ReadStmt / ExprStmt
    Assignment / BinaryOp / UnaryOp
    Literal / Identifier / CallExpr / ArrayAccess
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class NoAST:
    """Classe base de todo nó da AST. Guarda a posição de origem no código-fonte."""
    linha: int
    coluna: int


# ----------------------------------------------------------------------
# Estrutura de programa
# ----------------------------------------------------------------------

@dataclass
class Program(NoAST):
    """Nó raiz: sequência ordenada de declarações globais e de funções."""
    declarations: List[NoAST] = field(default_factory=list)


@dataclass
class Param(NoAST):
    """Parâmetro de uma função (tipo, nome e se é vetor)."""
    tipo: str
    nome: str
    eh_vetor: bool = False


@dataclass
class FunctionDecl(NoAST):
    """Declaração de função: tipo de retorno, nome, parâmetros e corpo."""
    tipo_retorno: str
    nome: str
    parametros: List[Param]
    corpo: "Block"


@dataclass
class VarDecl(NoAST):
    """Declaração de variável (global ou local), com inicializador opcional
    ou tamanho de vetor opcional (mutuamente exclusivos, conforme a gramática)."""
    tipo: str
    nome: str
    inicializador: Optional[NoAST] = None
    tamanho_vetor: Optional[NoAST] = None
    eh_vetor: bool = False


# ----------------------------------------------------------------------
# Comandos (statements)
# ----------------------------------------------------------------------

@dataclass
class Block(NoAST):
    """Bloco delimitado por chaves; preserva a ordem dos comandos/declarações."""
    comandos: List[NoAST] = field(default_factory=list)


@dataclass
class IfStmt(NoAST):
    condicao: NoAST
    entao: NoAST
    senao: Optional[NoAST] = None


@dataclass
class WhileStmt(NoAST):
    condicao: NoAST
    corpo: NoAST


@dataclass
class ForStmt(NoAST):
    """Os três componentes do cabeçalho são opcionais, conforme a gramática MiniC."""
    inicializacao: Optional[NoAST]
    condicao: Optional[NoAST]
    incremento: Optional[NoAST]
    corpo: NoAST


@dataclass
class ReturnStmt(NoAST):
    valor: Optional[NoAST] = None


@dataclass
class BreakStmt(NoAST):
    pass


@dataclass
class ContinueStmt(NoAST):
    pass


@dataclass
class PrintStmt(NoAST):
    valor: NoAST


@dataclass
class ReadStmt(NoAST):
    alvo: NoAST  # Identifier ou ArrayAccess


@dataclass
class ExprStmt(NoAST):
    """Comando de expressão (ex.: chamada de função usada como comando) ou ';' vazio."""
    expressao: Optional[NoAST] = None


# ----------------------------------------------------------------------
# Expressões
# ----------------------------------------------------------------------

@dataclass
class Assignment(NoAST):
    alvo: NoAST   # Identifier ou ArrayAccess
    valor: NoAST


@dataclass
class BinaryOp(NoAST):
    operador: str
    esquerda: NoAST
    direita: NoAST


@dataclass
class UnaryOp(NoAST):
    operador: str
    operando: NoAST


@dataclass
class Literal(NoAST):
    valor: Union[int, float, bool, str, None]
    tipo_literal: str  # 'int' | 'float' | 'bool' | 'char' | 'string'


@dataclass
class Identifier(NoAST):
    nome: str


@dataclass
class CallExpr(NoAST):
    nome_funcao: str
    argumentos: List[NoAST] = field(default_factory=list)


@dataclass
class ArrayAccess(NoAST):
    vetor: NoAST
    indice: NoAST
