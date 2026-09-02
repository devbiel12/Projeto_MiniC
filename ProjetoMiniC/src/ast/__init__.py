"""
Pacote AST - MiniC
==================
Define os nós da Árvore Sintática Abstrata produzidos pelo parser
(src/parser) e utilitários para serializá-los em texto legível.
"""

from .nodes import (
    ArrayAccess,
    Assignment,
    BinaryOp,
    Block,
    BreakStmt,
    CallExpr,
    ContinueStmt,
    ExprStmt,
    ForStmt,
    FunctionDecl,
    Identifier,
    IfStmt,
    Literal,
    NoAST,
    Param,
    PrintStmt,
    Program,
    ReadStmt,
    ReturnStmt,
    UnaryOp,
    VarDecl,
    WhileStmt,
)
from .printer import print_tree, to_sexp

__all__ = [
    "NoAST", "Program", "FunctionDecl", "Param", "VarDecl", "Block",
    "IfStmt", "WhileStmt", "ForStmt", "ReturnStmt", "BreakStmt",
    "ContinueStmt", "PrintStmt", "ReadStmt", "ExprStmt", "Assignment",
    "BinaryOp", "UnaryOp", "Literal", "Identifier", "CallExpr", "ArrayAccess",
    "to_sexp", "print_tree",
]
