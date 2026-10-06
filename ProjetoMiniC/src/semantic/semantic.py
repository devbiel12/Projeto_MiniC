"""Analisador semântico do MiniC.

Implementa a etapa que recebe uma AST sintaticamente válida e produz:
- tabela de símbolos e escopos léxicos;
- resolução de identificadores;
- síntese/verificação de tipos;
- compatibilidade e promoção int -> float (e char -> int);
- vetores e índices;
- chamadas e parâmetros;
- retornos e análise simples de fluxo;
- contexto de break/continue;
- diagnósticos SEM001..SEM012.

A etapa não gera IR nem código.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from ProjetoMiniC.src.ast import (
    Assign, Binary, Block, Break, Call, Continue, ExprStmt, For, Function,
    Id, If, Index, Lit, Parameter, Print, Program, Read, Return, Unary,
    VarDecl, While,
)
from ProjetoMiniC.src.ast.nodes import Node


ERROR = "<error>"


@dataclass
class Diagnostic:
    code: str
    message: str
    line: int = 1
    column: int = 1
    lexeme: str = ""

    def __str__(self) -> str:
        return f"{self.code} — linha {self.line}, coluna {self.column}: {self.message}"

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "lexeme": self.lexeme,
        }


@dataclass
class Symbol:
    name: str
    category: str
    type_name: str
    line: int
    column: int
    scope_level: int
    size: Optional[int] = None
    parameters: List["Symbol"] = field(default_factory=list)
    return_type: Optional[str] = None
    initialized: bool = False

    @property
    def is_function(self) -> bool:
        return self.category == "FUNCAO"

    @property
    def is_array(self) -> bool:
        return self.category == "VETOR"

    def type_display(self) -> str:
        if self.is_array:
            suffix = "[]" if self.size is None else f"[{self.size}]"
            return f"{self.type_name}{suffix}"
        if self.is_function:
            args = ", ".join(p.type_name + ("[]" if p.is_array else "") for p in self.parameters)
            return f"({args}) -> {self.return_type}"
        return self.type_name


class Scope:
    def __init__(self, parent: Optional["Scope"] = None, level: int = 0, name: str = "global"):
        self.parent = parent
        self.level = level
        self.name = name
        self.symbols: Dict[str, Symbol] = {}

    def declare(self, symbol: Symbol) -> Optional[Symbol]:
        previous = self.symbols.get(symbol.name)
        if previous is not None:
            return previous
        self.symbols[symbol.name] = symbol
        return None

    def lookup_current(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        scope: Optional[Scope] = self
        while scope is not None:
            symbol = scope.symbols.get(name)
            if symbol is not None:
                return symbol
            scope = scope.parent
        return None


@dataclass
class SemanticResult:
    program: Optional[Program]
    diagnostics: List[Diagnostic]
    global_scope: Scope
    scopes: List[Scope]

    @property
    def success(self) -> bool:
        return not self.diagnostics


class SemanticAnalyzer:
    """Verificador semântico do núcleo MINIC definido no projeto."""

    def __init__(self, max_diagnostics: int = 100):
        self.max_diagnostics = max_diagnostics
        self.diagnostics: List[Diagnostic] = []
        self.global_scope = Scope(level=0, name="global")
        self.scopes: List[Scope] = [self.global_scope]
        self.current_scope = self.global_scope
        self.current_function: Optional[Symbol] = None
        self.loop_depth = 0

    def analyze(self, program: Program) -> SemanticResult:
        # Passagem A: coletar globais e assinaturas, permitindo recursão e
        # chamadas a funções declaradas posteriormente.
        for declaration in program.declarations:
            if isinstance(declaration, Function):
                self._declare_function(declaration)
            elif isinstance(declaration, VarDecl):
                self._declare_variable(declaration, self.global_scope)
            else:
                self._error("SEM002", "Construção fora de uma função ou declaração global inválida.", declaration)

        # Os casos semânticos usam `principal`; `main` continua aceito para
        # preservar a convenção dos testes unitários e da CLI.
        entradas = [
            s for s in self.global_scope.symbols.values()
            if s.category == "FUNCAO" and s.name in {"main", "principal"}
        ]
        if not entradas:
            self._error("SEM011", "O programa deve possuir uma função main() ou principal().", program)
        elif len(entradas) > 1:
            self._error("SEM002", "O programa deve possuir apenas uma função de entrada (main ou principal).", entradas[1])

        for declaration in program.declarations:
            if isinstance(declaration, Function):
                self._check_function(declaration)
            elif isinstance(declaration, VarDecl):
                self._check_global_initializer(declaration)

        return SemanticResult(program, self.diagnostics, self.global_scope, list(self.scopes))

    # ------------------------------------------------------------------
    # Declarações / escopos
    # ------------------------------------------------------------------
    def _declare_function(self, node: Function) -> None:
        params: List[Symbol] = []
        for parameter in node.parameters:
            params.append(Symbol(
                name=parameter.name,
                category="VETOR" if parameter.is_array else "PARAMETRO",
                type_name=self._normalize_type(parameter.type_name),
                line=self._line(parameter),
                column=self._column(parameter),
                scope_level=1,
                size=None,
            ))
        symbol = Symbol(
            name=node.name,
            category="FUNCAO",
            type_name="funcao",
            line=self._line(node),
            column=self._column(node),
            scope_level=0,
            parameters=params,
            return_type=self._normalize_type(node.return_type),
        )
        previous = self.global_scope.declare(symbol)
        if previous is not None:
            self._error(
                "SEM002",
                f"“{node.name}” já declarado neste escopo; declaração anterior na linha {previous.line}, coluna {previous.column} (tipo {previous.type_name}).",
                node,
                node.name,
            )

    def _declare_variable(self, node: VarDecl, scope: Scope) -> Optional[Symbol]:
        type_name = self._normalize_type(node.type_name)
        if type_name == "void":
            self._error("SEM004", "Uma variável não pode possuir tipo void.", node, node.name)
            type_name = ERROR
        size = self._constant_int(node.size) if node.size is not None else None
        category = "VETOR" if node.size is not None else "VARIAVEL"
        symbol = Symbol(
            name=node.name,
            category=category,
            type_name=type_name,
            line=self._line(node),
            column=self._column(node),
            scope_level=scope.level,
            size=size,
        )
        previous = scope.declare(symbol)
        if previous is not None:
            self._error(
                "SEM002",
                f"“{node.name}” já declarado neste escopo; declaração anterior na linha {previous.line}, coluna {previous.column} (tipo {previous.type_name}).",
                node,
                node.name,
            )
            return previous
        setattr(node, "symbol", symbol)
        setattr(node, "inferred_type", self._declared_type(symbol))
        return symbol

    def _check_function(self, node: Function) -> None:
        function = self.global_scope.lookup_current(node.name)
        if function is None or not function.is_function:
            return
        previous_function = self.current_function
        self.current_function = function
        self._open_scope(f"function {node.name}")

        for parameter_node, parameter_symbol in zip(node.parameters, function.parameters):
            previous = self.current_scope.declare(parameter_symbol)
            if previous is not None:
                self._error("SEM002", f"Parâmetro duplicado '{parameter_node.name}'.", parameter_node, parameter_node.name)
            setattr(parameter_node, "symbol", parameter_symbol)
            setattr(parameter_node, "inferred_type", self._declared_type(parameter_symbol))

        definitely_returns = self._check_block(node.body, create_scope=True)
        if function.return_type != "void" and not definitely_returns:
            self._error(
                "SEM011",
                f"A função “{node.name}” pode terminar sem retornar {function.return_type}; o ramo em que “{self._missing_return_condition(node.body)}” é falso alcança o fim do corpo.",
                type("Position", (), {"line": self._line(node), "column": 1})(),
                node.name,
            )
        self._close_scope()
        self.current_function = previous_function

    def _check_global_initializer(self, node: VarDecl) -> None:
        symbol = self.global_scope.lookup_current(node.name)
        if node.size is not None:
            size_type = self._type_of(node.size)
            if size_type not in ("int", ERROR):
                self._error("SEM006", "O tamanho do vetor deve ser inteiro.", node.size)
            if self._constant_int(node.size) is not None and self._constant_int(node.size) <= 0:
                self._error("SEM006", "O tamanho do vetor deve ser maior que zero.", node.size)
        if node.initializer is not None and symbol is not None:
            value_type = self._type_of(node.initializer)
            expected = self._declared_type(symbol)
            if not self._compatible(value_type, expected):
                self._error("SEM003", f"Não é possível atribuir {value_type} a {expected}.", node.initializer)
            else:
                symbol.initialized = True

    def _check_block(self, block: Block, create_scope: bool = True) -> bool:
        if create_scope:
            self._open_scope("block")
        definitely_returns = False
        for item in block.items:
            if isinstance(item, VarDecl):
                symbol = self._declare_variable(item, self.current_scope)
                if item.size is not None:
                    size_type = self._type_of(item.size)
                    if size_type not in ("int", ERROR):
                        self._error("SEM006", "O tamanho do vetor deve ser inteiro.", item.size)
                    constant = self._constant_int(item.size)
                    if constant is not None and constant <= 0:
                        self._error("SEM006", "O tamanho do vetor deve ser maior que zero.", item.size)
                if item.initializer is not None and symbol is not None:
                    value_type = self._type_of(item.initializer)
                    expected = self._declared_type(symbol)
                    if not self._compatible(value_type, expected):
                        self._error("SEM003", f"Não é possível atribuir {value_type} a {expected}.", item.initializer)
                    else:
                        symbol.initialized = True
            else:
                if definitely_returns:
                    # Código após retorno é permitido sintaticamente; não é
                    # necessário inventar um erro semântico para ele.
                    self._check_statement(item)
                else:
                    definitely_returns = self._check_statement(item)
        if create_scope:
            self._close_scope()
        return definitely_returns

    def _open_scope(self, name: str) -> Scope:
        scope = Scope(parent=self.current_scope, level=self.current_scope.level + 1, name=name)
        self.current_scope = scope
        self.scopes.append(scope)
        return scope

    def _close_scope(self) -> None:
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    # ------------------------------------------------------------------
    # Comandos / fluxo
    # ------------------------------------------------------------------
    def _check_statement(self, node: Node) -> bool:
        if isinstance(node, Block):
            return self._check_block(node, create_scope=True)
        if isinstance(node, ExprStmt):
            if node.expression is not None:
                self._type_of(node.expression, allow_void=True)
            return False
        if isinstance(node, If):
            condition = self._type_of(node.condition)
            if condition not in ("bool", ERROR):
                self._error("SEM005", f"Condição de if deve ter tipo bool; recebeu {condition} (expressão “{self._expression_text(node.condition)}”).", node.condition)
            then_returns = self._check_statement(node.then_branch)
            else_returns = self._check_statement(node.else_branch) if node.else_branch is not None else False
            return then_returns and else_returns
        if isinstance(node, While):
            condition = self._type_of(node.condition)
            if condition not in ("bool", ERROR):
                self._error("SEM005", f"Condição de while deve ter tipo bool; recebeu {condition} (expressão “{self._expression_text(node.condition)}”).", node.condition)
            self.loop_depth += 1
            self._check_statement(node.body)
            self.loop_depth -= 1
            return False
        if isinstance(node, For):
            if node.initializer is not None:
                self._type_of(node.initializer)
            if node.condition is not None:
                condition = self._type_of(node.condition)
                if condition not in ("bool", ERROR):
                    self._error("SEM005", "A condição do for deve ser bool.", node.condition)
            if node.increment is not None:
                self._type_of(node.increment)
            self.loop_depth += 1
            self._check_statement(node.body)
            self.loop_depth -= 1
            return False
        if isinstance(node, Return):
            expected = self.current_function.return_type if self.current_function else "void"
            if node.value is None:
                if expected != "void":
                    self._error("SEM009", f"Retorno sem valor em função que retorna {expected}.", node)
            else:
                actual = self._type_of(node.value)
                if expected == "void":
                    self._error("SEM009", "Função void não pode retornar um valor.", node.value)
                elif not self._compatible(actual, expected):
                    self._error("SEM009", f"Retorno {actual} incompatível com o tipo {expected} da função “{self.current_function.name}”; conversão implícita de float para int não permitida.", node.value)
            return True
        if isinstance(node, Break):
            if self.loop_depth == 0:
                self._error("SEM010", "break só pode ser usado dentro de um laço.", node)
            return False
        if isinstance(node, Continue):
            if self.loop_depth == 0:
                self._error("SEM010", "continue só pode ser usado dentro de um laço.", node)
            return False
        if isinstance(node, Print):
            self._type_of(node.value, allow_void=False)
            return False
        if isinstance(node, Read):
            target_type = self._type_of(node.target)
            if isinstance(node.target, Id):
                symbol = getattr(node.target, "symbol", None)
                if symbol is None:
                    symbol = self.current_scope.lookup(node.target.name)
                if symbol is None:
                    return False
                if symbol.category not in ("VARIAVEL", "PARAMETRO", "VETOR"):
                    self._error("SEM003", "read exige uma entidade atribuível.", node.target, node.target.name)
                else:
                    symbol.initialized = True
            elif isinstance(node.target, Index):
                self._type_of(node.target)
            if target_type == ERROR:
                return False
            return False
        return False

    # ------------------------------------------------------------------
    # Expressões
    # ------------------------------------------------------------------
    def _type_of(self, node: Optional[Node], allow_void: bool = False) -> str:
        if node is None:
            return "void"
        cached = getattr(node, "inferred_type", None)
        if cached is not None:
            return cached

        result = ERROR
        if isinstance(node, Lit):
            result = self._normalize_type(node.literal_type)
            if result == "string":
                # String está disponível lexicalmente/parser, mas não é um
                # tipo geral do núcleo MINIC. print é tratado como extensão
                # segura e não transforma string em tipo numérico.
                result = "string"
        elif isinstance(node, Id):
            symbol = self.current_scope.lookup(node.name)
            if symbol is None:
                self._error("SEM001", f"Identificador “{node.name}” não declarado neste escopo.", node, node.name)
            else:
                setattr(node, "symbol", symbol)
                if symbol.is_function:
                    self._error("SEM012", f"A função '{node.name}' não pode ser usada como valor de expressão.", node, node.name)
                else:
                    result = self._declared_type(symbol)
                    setattr(node, "category", symbol.category)
        elif isinstance(node, Unary):
            operand = self._type_of(node.operand)
            if operand == ERROR:
                result = ERROR
            elif node.operator in ("+", "-"):
                if operand in ("int", "float"):
                    result = operand
                elif operand == "char":
                    result = "int"
                else:
                    self._error("SEM004", f"Operador '{node.operator}' exige operando numérico.", node.operand)
            elif node.operator == "!":
                if operand == "bool":
                    result = "bool"
                else:
                    self._error("SEM004", "O operador '!' exige operando bool.", node.operand)
        elif isinstance(node, Binary):
            left = self._type_of(node.left)
            right = self._type_of(node.right)
            result = self._binary_type(node.operator, left, right, node)
        elif isinstance(node, Assign):
            target_type = self._type_of_lvalue(node.target)
            value_type = self._type_of(node.value, allow_void=True) if isinstance(node.value, Call) else self._type_of(node.value)
            if value_type == "void":
                callee = node.value.callee.name if isinstance(node.value, Call) and isinstance(node.value.callee, Id) else "função"
                location = node.value.callee if isinstance(node.value, Call) else node.value
                self._error("SEM012", f"Função “{callee}” não produz valor (retorno void) e não pode ser usada como expressão de atribuição.", location)
                result = ERROR
            elif target_type != ERROR and value_type != ERROR:
                if not self._compatible(value_type, target_type):
                    destination = self._expression_text(node.target)
                    expression = self._expression_text(node.value)
                    self._error("SEM003", f"Não é possível atribuir {value_type} a {target_type} sem conversão permitida (destino “{destination}”; expressão “{expression}”).", node.value)
                    result = ERROR
                else:
                    self._mark_initialized(node.target)
                    result = target_type
            else:
                result = ERROR
        elif isinstance(node, Index):
            target = self._type_of(node.target)
            index = self._type_of(node.index)
            symbol = getattr(node.target, "symbol", None)
            if index not in ("int", ERROR):
                vector_name = node.target.name if isinstance(node.target, Id) else self._expression_text(node.target)
                self._error("SEM006", f"Índice do vetor “{vector_name}” deve ser int; recebeu {index} (expressão “{self._expression_text(node.index)}”).", node.index)
            if symbol is not None and not symbol.is_array:
                self._error("SEM006", f"'{symbol.name}' não é um vetor e não pode ser indexado.", node.target, symbol.name)
            if target.startswith("array("):
                result = target[6:-1]
            elif symbol is not None and symbol.is_array:
                result = symbol.type_name
            else:
                result = ERROR
            constant = self._constant_int(node.index)
            if symbol is not None and symbol.size is not None and constant is not None:
                if constant < 0 or constant >= symbol.size:
                    self._error("SEM006", f"Índice {constant} fora dos limites do vetor '{symbol.name}'.", node.index)
        elif isinstance(node, Call):
            result = self._check_call(node)
        else:
            # Não há expressão desconhecida no AST oficial; manter ERROR
            # impede cascatas caso uma extensão seja adicionada.
            result = ERROR

        if result == "void" and not allow_void:
            if isinstance(node, Call) and isinstance(node.callee, Id):
                self._error("SEM012", f"Função “{node.callee.name}” não produz valor (retorno void) e não pode ser usada como expressão.", node.callee)
            else:
                self._error("SEM012", "Função sem valor de retorno usada em expressão.", node)
        setattr(node, "inferred_type", result)
        return result

    def _type_of_lvalue(self, node: Node) -> str:
        if isinstance(node, Id):
            symbol = self.current_scope.lookup(node.name)
            if symbol is None:
                self._error("SEM001", f"Identificador “{node.name}” não declarado neste escopo.", node, node.name)
                return ERROR
            setattr(node, "symbol", symbol)
            if symbol.category not in ("VARIAVEL", "PARAMETRO", "VETOR"):
                self._error("SEM003", f"'{node.name}' não é uma entidade atribuível.", node, node.name)
                return ERROR
            return self._declared_type(symbol)
        if isinstance(node, Index):
            return self._type_of(node)
        lexeme = getattr(node, "lexeme", "")
        if isinstance(node, Lit):
            literal = getattr(node, "value", lexeme)
            self._error(
                "SEM013",
                f"Destino de atribuição não é atribuível; o literal inteiro “{literal}” não designa uma variável ou elemento de vetor.",
                node,
                str(literal),
            )
        else:
            self._error("SEM013", "Destino da atribuição não é atribuível.", node, lexeme)
        return ERROR

    def _binary_type(self, operator: str, left: str, right: str, node: Binary) -> str:
        if left == ERROR or right == ERROR:
            return ERROR
        if operator in ("+", "-", "*", "/"):
            if self._numeric(left) and self._numeric(right):
                if operator == "/" and self._constant_number(node.right) == 0:
                    self._error("SEM004", "Divisão por zero constante.", node.right)
                    return ERROR
                return "float" if "float" in (left, right) else "int"
            self._error("SEM004", f"Operador '{operator}' exige operandos numéricos.", node)
            return ERROR
        if operator == "%":
            if self._integer_like(left) and self._integer_like(right):
                return "int"
            self._error("SEM004", "O operador '%' exige operandos inteiros.", node)
            return ERROR
        if operator in ("<", "<=", ">", ">="):
            if self._numeric(left) and self._numeric(right):
                return "bool"
            self._error("SEM004", f"Operador '{operator}' exige operandos numéricos.", node)
            return ERROR
        if operator in ("==", "!="):
            if self._comparable(left, right):
                return "bool"
            self._error("SEM004", f"Operador '{operator}' exige operandos comparáveis.", node)
            return ERROR
        if operator in ("&&", "||"):
            if left == "bool" and right == "bool":
                return "bool"
            self._error("SEM004", f"Operador '{operator}' exige operandos bool.", node)
            return ERROR
        self._error("SEM004", f"Operador '{operator}' não é suportado semanticamente.", node)
        return ERROR

    def _check_call(self, node: Call) -> str:
        if not isinstance(node.callee, Id):
            self._error("SEM007", "A chamada deve referenciar uma função.", node.callee)
            for argument in node.arguments:
                self._type_of(argument)
            return ERROR
        symbol = self.current_scope.lookup(node.callee.name)
        if symbol is None:
            self._error("SEM001", f"Identificador “{node.callee.name}” não declarado neste escopo.", node.callee, node.callee.name)
            for argument in node.arguments:
                self._type_of(argument)
            return ERROR
        setattr(node.callee, "symbol", symbol)
        if not symbol.is_function:
            self._error("SEM007", f"'{node.callee.name}' não é uma função.", node.callee, node.callee.name)
            for argument in node.arguments:
                self._type_of(argument)
            return ERROR
        if len(node.arguments) != len(symbol.parameters):
            self._error(
                "SEM007",
                f"“{symbol.name}” espera {len(symbol.parameters)} argumentos, mas recebeu {len(node.arguments)}.",
                node.callee,
                symbol.name,
            )
        for index, argument in enumerate(node.arguments):
            actual = self._type_of(argument)
            if index >= len(symbol.parameters):
                continue
            expected = self._declared_type(symbol.parameters[index])
            if symbol.parameters[index].is_array:
                expected = "array"
                if not (isinstance(argument, Id) and getattr(argument, "symbol", None) is not None and getattr(argument.symbol, "is_array", False)):
                    if actual != ERROR:
                        self._error("SEM008", f"Argumento {index + 1} deve ser um vetor.", argument)
                continue
            if not self._compatible(actual, expected):
                self._error("SEM008", f"Argumento {index + 1} de “{symbol.name}”: esperado {expected}, recebido {actual} (expressão “{self._expression_text(argument)}”).", self._expression_start(argument))
        return symbol.return_type or "void"

    # ------------------------------------------------------------------
    # Tipos e utilidades
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_type(type_name: str) -> str:
        return {"real": "float", "logico": "bool", "inteiro": "int"}.get(type_name, type_name)

    @staticmethod
    def _declared_type(symbol: Symbol) -> str:
        if symbol.is_array:
            return f"array({symbol.type_name})"
        return symbol.type_name

    @staticmethod
    def _numeric(type_name: str) -> bool:
        return type_name in ("int", "float", "char")

    @staticmethod
    def _integer_like(type_name: str) -> bool:
        return type_name in ("int", "char")

    @staticmethod
    def _comparable(left: str, right: str) -> bool:
        if left == right:
            return left not in ("void", "string", ERROR)
        return {left, right} <= {"int", "float", "char"}

    @staticmethod
    def _compatible(actual: str, expected: str) -> bool:
        if actual == ERROR or expected == ERROR:
            return True
        if actual == expected:
            return True
        if actual == "char" and expected in ("int", "float"):
            return True
        if actual == "int" and expected == "float":
            return True
        return False

    def _mark_initialized(self, node: Node) -> None:
        if isinstance(node, Id):
            symbol = getattr(node, "symbol", None) or self.current_scope.lookup(node.name)
            if symbol is not None:
                symbol.initialized = True
        elif isinstance(node, Index):
            self._mark_initialized(node.target)

    def _constant_int(self, node: Optional[Node]) -> Optional[int]:
        if isinstance(node, Lit) and node.literal_type == "int":
            try:
                return int(float(node.value))
            except (TypeError, ValueError):
                return None
        return None

    def _constant_number(self, node: Optional[Node]) -> Optional[float]:
        if isinstance(node, Lit) and node.literal_type in ("int", "real"):
            try:
                return float(node.value)
            except (TypeError, ValueError):
                return None
        return None

    @staticmethod
    def _line(node: object) -> int:
        return int(getattr(node, "line", getattr(node, "_line", 1)))

    @staticmethod
    def _column(node: object) -> int:
        return int(getattr(node, "column", getattr(node, "_column", 1)))

    @staticmethod
    def _expression_text(node: Optional[Node]) -> str:
        if node is None:
            return ""
        if isinstance(node, Id):
            return node.name
        if isinstance(node, Lit):
            return str(node.value)
        if isinstance(node, Index):
            return f"{SemanticAnalyzer._expression_text(node.target)}[{SemanticAnalyzer._expression_text(node.index)}]"
        if isinstance(node, Call):
            name = SemanticAnalyzer._expression_text(node.callee)
            return name + "(" + ", ".join(SemanticAnalyzer._expression_text(a) for a in node.arguments) + ")"
        if isinstance(node, Unary):
            return node.operator + SemanticAnalyzer._expression_text(node.operand)
        if isinstance(node, Binary):
            return f"{SemanticAnalyzer._expression_text(node.left)} {node.operator} {SemanticAnalyzer._expression_text(node.right)}"
        if isinstance(node, Assign):
            return f"{SemanticAnalyzer._expression_text(node.target)} = {SemanticAnalyzer._expression_text(node.value)}"
        return ""

    @staticmethod
    def _expression_start(node: Node) -> Node:
        while isinstance(node, Binary):
            node = node.left
        return node

    @staticmethod
    def _missing_return_condition(block: Block) -> str:
        for item in block.items:
            if isinstance(item, If) and item.else_branch is None:
                return SemanticAnalyzer._expression_text(item.condition)
        return "condição"

    def _error(self, code: str, message: str, node: object, lexeme: str = "") -> None:
        if len(self.diagnostics) >= self.max_diagnostics:
            return
        self.diagnostics.append(Diagnostic(code, message, self._line(node), self._column(node), lexeme))


def analyze(program: Program, max_diagnostics: int = 100) -> SemanticResult:
    """Atalho para executar a análise semântica."""
    return SemanticAnalyzer(max_diagnostics=max_diagnostics).analyze(program)
