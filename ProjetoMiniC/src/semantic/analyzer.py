"""
analyzer.py
===========
Analisador Semântico da linguagem MiniC (Aula 15).
Implementa checagem estática de tipos, escopo, regras de vetores,
funções, retorno e fluxo de controle conforme especificação canônica.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

try:
    from ..ast import nodes as no
except (ImportError, ValueError):
    from ProjetoMiniC.src.ast import nodes as no


@dataclass
class Diagnostic:
    codigo: str
    linha: int
    coluna: int
    mensagem: str

    def formatar(self) -> str:
        return f"{self.codigo} — linha {self.linha}, coluna {self.coluna}: {self.mensagem}"


@dataclass
class Symbol:
    nome: str
    categoria: str       # 'var', 'array', 'func'
    tipo: str            # 'int', 'float', 'bool', 'void', etc.
    linha: int
    coluna: int
    eh_vetor: bool = False
    tamanho_vetor: Optional[int] = None
    params: Optional[List[Tuple[str, str, bool]]] = None  # [(nome, tipo, eh_vetor)]


class SymbolTable:
    def __init__(self, parent: Optional[SymbolTable] = None):
        self.parent: Optional[SymbolTable] = parent
        self.symbols: Dict[str, Symbol] = {}

    def insert(self, symbol: Symbol) -> bool:
        """Insere no escopo atual. Retorna False se já existir no escopo atual."""
        if symbol.nome in self.symbols:
            return False
        self.symbols[symbol.nome] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca do escopo atual para os pais."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Busca apenas no escopo atual."""
        return self.symbols.get(name)


def expr_to_str(node: no.NoAST) -> str:
    """Converte expressão AST de volta para string canônica de diagnóstico."""
    if isinstance(node, no.Identifier):
        return node.nome
    elif isinstance(node, no.Literal):
        return str(node.valor)
    elif isinstance(node, no.BinaryOp):
        return f"{expr_to_str(node.esquerda)} {node.operador} {expr_to_str(node.direita)}"
    elif isinstance(node, no.UnaryOp):
        return f"{node.operador}{expr_to_str(node.operando)}"
    elif isinstance(node, no.CallExpr):
        args = ", ".join(expr_to_str(a) for a in node.argumentos)
        return f"{node.nome_funcao}({args})"
    elif isinstance(node, no.ArrayAccess):
        return f"{expr_to_str(node.vetor)}[{expr_to_str(node.indice)}]"
    elif isinstance(node, no.Assignment):
        return f"{expr_to_str(node.alvo)} = {expr_to_str(node.valor)}"
    return ""


class SemanticAnalyzer:
    def __init__(self):
        self.global_table = SymbolTable()
        self.diagnostics: List[Diagnostic] = []
        self.current_func: Optional[Symbol] = None
        self.loop_depth: int = 0

    def analyze(self, program: no.Program) -> List[Diagnostic]:
        self.diagnostics = []
        self.global_table = SymbolTable()

        # Passagem 1: Coletar declarações globais e assinaturas de funções
        for decl in program.declarations:
            if isinstance(decl, no.FunctionDecl):
                params_info = []
                for p in decl.parametros:
                    params_info.append((p.nome, p.tipo, p.eh_vetor))
                sym = Symbol(
                    nome=decl.nome,
                    categoria="func",
                    tipo=decl.tipo_retorno,
                    linha=decl.linha,
                    coluna=decl.coluna,
                    params=params_info,
                )
                if not self.global_table.insert(sym):
                    prev = self.global_table.lookup_current(decl.nome)
                    prev_linha = prev.linha if prev else decl.linha
                    prev_coluna = prev.coluna if prev else decl.coluna
                    prev_tipo = prev.tipo if prev else decl.tipo_retorno
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM002",
                        linha=decl.linha,
                        coluna=decl.coluna,
                        mensagem=f"“{decl.nome}” já declarado neste escopo; declaração anterior na linha {prev_linha}, coluna {prev_coluna} (tipo {prev_tipo})."
                    ))
            elif isinstance(decl, no.VarDecl):
                sym = Symbol(
                    nome=decl.nome,
                    categoria="array" if decl.eh_vetor else "var",
                    tipo=decl.tipo,
                    linha=decl.linha,
                    coluna=decl.coluna,
                    eh_vetor=decl.eh_vetor,
                )
                if not self.global_table.insert(sym):
                    prev = self.global_table.lookup_current(decl.nome)
                    prev_linha = prev.linha if prev else decl.linha
                    prev_coluna = prev.coluna if prev else decl.coluna
                    prev_tipo = prev.tipo if prev else decl.tipo
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM002",
                        linha=decl.linha,
                        coluna=decl.coluna,
                        mensagem=f"“{decl.nome}” já declarado neste escopo; declaração anterior na linha {prev_linha}, coluna {prev_coluna} (tipo {prev_tipo})."
                    ))

        # Passagem 2: Analisar corpos das funções e comandos globais
        for decl in program.declarations:
            if isinstance(decl, no.FunctionDecl):
                self._analyze_function(decl)
            elif isinstance(decl, no.VarDecl) and decl.inicializador:
                self._check_expr(decl.inicializador, self.global_table)

        return self.diagnostics

    def _analyze_function(self, func: no.FunctionDecl):
        sym = self.global_table.lookup(func.nome)
        self.current_func = sym
        self.loop_depth = 0

        func_table = SymbolTable(parent=self.global_table)

        # Inserir parâmetros no escopo da função
        for p in func.parametros:
            psym = Symbol(
                nome=p.nome,
                categoria="array" if p.eh_vetor else "var",
                tipo=p.tipo,
                linha=p.linha,
                coluna=p.coluna,
                eh_vetor=p.eh_vetor,
            )
            if not func_table.insert(psym):
                prev = func_table.lookup_current(p.nome)
                prev_linha = prev.linha if prev else p.linha
                prev_coluna = prev.coluna if prev else p.coluna
                prev_tipo = prev.tipo if prev else p.tipo
                self.diagnostics.append(Diagnostic(
                    codigo="SEM002",
                    linha=p.linha,
                    coluna=p.coluna,
                    mensagem=f"“{p.nome}” já declarado neste escopo; declaração anterior na linha {prev_linha}, coluna {prev_coluna} (tipo {prev_tipo})."
                ))

        # Analisar comandos do corpo
        for cmd in func.corpo.comandos:
            self._analyze_stmt(cmd, func_table)

        # Verificar se caminhos de retorno cobrem o fim para funções não-void
        if func.tipo_retorno != "void":
            returns_always, missing_reason = self._guarantees_return(func.corpo)
            if not returns_always:
                reason_text = missing_reason if missing_reason else "alcança o fim do corpo"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM011",
                    linha=func.linha,
                    coluna=func.coluna,
                    mensagem=f"A função “{func.nome}” pode terminar sem retornar {func.tipo_retorno}; {reason_text}."
                ))

        self.current_func = None

    def _analyze_stmt(self, stmt: no.NoAST, table: SymbolTable):
        if isinstance(stmt, no.VarDecl):
            sym = Symbol(
                nome=stmt.nome,
                categoria="array" if stmt.eh_vetor else "var",
                tipo=stmt.tipo,
                linha=stmt.linha,
                coluna=stmt.coluna,
                eh_vetor=stmt.eh_vetor,
            )
            if not table.insert(sym):
                prev = table.lookup_current(stmt.nome)
                prev_linha = prev.linha if prev else stmt.linha
                prev_coluna = prev.coluna if prev else stmt.coluna
                prev_tipo = prev.tipo if prev else stmt.tipo
                self.diagnostics.append(Diagnostic(
                    codigo="SEM002",
                    linha=stmt.linha,
                    coluna=stmt.coluna,
                    mensagem=f"“{stmt.nome}” já declarado neste escopo; declaração anterior na linha {prev_linha}, coluna {prev_coluna} (tipo {prev_tipo})."
                ))
            if stmt.inicializador:
                t_expr = self._check_expr(stmt.inicializador, table)
                if t_expr != "ERROR" and not self._is_assignable(stmt.tipo, t_expr):
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM003",
                        linha=stmt.inicializador.linha,
                        coluna=stmt.inicializador.coluna,
                        mensagem=f"Não é possível atribuir {t_expr} a {stmt.tipo} sem conversão permitida (destino “{stmt.nome}”; expressão “{expr_to_str(stmt.inicializador)}”)."
                    ))

        elif isinstance(stmt, no.Block):
            block_table = SymbolTable(parent=table)
            for s in stmt.comandos:
                self._analyze_stmt(s, block_table)

        elif isinstance(stmt, no.ExprStmt):
            if stmt.expressao is not None:
                self._check_expr(stmt.expressao, table)

        elif isinstance(stmt, no.IfStmt):
            t_cond = self._check_expr(stmt.condicao, table)
            if t_cond != "ERROR" and t_cond != "bool":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM005",
                    linha=stmt.condicao.linha,
                    coluna=stmt.condicao.coluna,
                    mensagem=f"Condição de if deve ter tipo bool; recebeu {t_cond} (expressão “{expr_to_str(stmt.condicao)}”)."
                ))
            self._analyze_stmt(stmt.entao, table)
            if stmt.senao is not None:
                self._analyze_stmt(stmt.senao, table)

        elif isinstance(stmt, no.WhileStmt):
            t_cond = self._check_expr(stmt.condicao, table)
            if t_cond != "ERROR" and t_cond != "bool":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM005",
                    linha=stmt.condicao.linha,
                    coluna=stmt.condicao.coluna,
                    mensagem=f"Condição de while deve ter tipo bool; recebeu {t_cond} (expressão “{expr_to_str(stmt.condicao)}”)."
                ))
            self.loop_depth += 1
            self._analyze_stmt(stmt.corpo, table)
            self.loop_depth -= 1

        elif isinstance(stmt, no.ForStmt):
            if stmt.inicializacao is not None:
                self._check_expr(stmt.inicializacao, table)
            if stmt.condicao is not None:
                t_cond = self._check_expr(stmt.condicao, table)
                if t_cond != "ERROR" and t_cond != "bool":
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM005",
                        linha=stmt.condicao.linha,
                        coluna=stmt.condicao.coluna,
                        mensagem=f"Condição de for deve ter tipo bool; recebeu {t_cond} (expressão “{expr_to_str(stmt.condicao)}”)."
                    ))
            if stmt.incremento is not None:
                self._check_expr(stmt.incremento, table)
            self.loop_depth += 1
            self._analyze_stmt(stmt.corpo, table)
            self.loop_depth -= 1

        elif isinstance(stmt, no.ReturnStmt):
            func_name = self.current_func.nome if self.current_func else "função"
            expected_ret = self.current_func.tipo if self.current_func else "void"
            if stmt.valor is None:
                if expected_ret != "void":
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM009",
                        linha=stmt.linha,
                        coluna=stmt.coluna,
                        mensagem=f"Função “{func_name}” com retorno {expected_ret} exige expressão de retorno."
                    ))
            else:
                t_val = self._check_expr(stmt.valor, table)
                if t_val != "ERROR":
                    if expected_ret == "void":
                        self.diagnostics.append(Diagnostic(
                            codigo="SEM009",
                            linha=stmt.valor.linha,
                            coluna=stmt.valor.coluna,
                            mensagem=f"Função “{func_name}” do tipo void não deve retornar valor."
                        ))
                    elif not self._is_assignable(expected_ret, t_val):
                        if expected_ret == "int" and t_val == "float":
                            self.diagnostics.append(Diagnostic(
                                codigo="SEM009",
                                linha=stmt.valor.linha,
                                coluna=stmt.valor.coluna,
                                mensagem=f"Retorno float incompatível com o tipo int da função “{func_name}”; conversão implícita de float para int não permitida."
                            ))
                        else:
                            self.diagnostics.append(Diagnostic(
                                codigo="SEM009",
                                linha=stmt.valor.linha,
                                coluna=stmt.valor.coluna,
                                mensagem=f"Retorno {t_val} incompatível com o tipo {expected_ret} da função “{func_name}”."
                            ))

        elif isinstance(stmt, no.BreakStmt):
            if self.loop_depth == 0:
                self.diagnostics.append(Diagnostic(
                    codigo="SEM010",
                    linha=stmt.linha,
                    coluna=stmt.coluna,
                    mensagem="break só pode ocorrer dentro de laço."
                ))

        elif isinstance(stmt, no.ContinueStmt):
            if self.loop_depth == 0:
                self.diagnostics.append(Diagnostic(
                    codigo="SEM010",
                    linha=stmt.linha,
                    coluna=stmt.coluna,
                    mensagem="continue só pode ocorrer dentro de laço."
                ))

        elif isinstance(stmt, no.PrintStmt):
            self._check_expr(stmt.valor, table)

        elif isinstance(stmt, no.ReadStmt):
            self._check_lvalue(stmt.alvo, table)

    def _check_expr(self, expr: no.NoAST, table: SymbolTable) -> str:
        if isinstance(expr, no.Literal):
            return expr.tipo_literal

        elif isinstance(expr, no.Identifier):
            sym = table.lookup(expr.nome)
            if sym is None:
                self.diagnostics.append(Diagnostic(
                    codigo="SEM001",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Identificador “{expr.nome}” não declarado neste escopo."
                ))
                return "ERROR"
            if sym.eh_vetor or sym.categoria == "array":
                return f"array_{sym.tipo}"
            return sym.tipo

        elif isinstance(expr, no.Assignment):
            # Verificar se o lado esquerdo é um L-Value
            lval_ok, target_type, target_name = self._check_lvalue(expr.alvo, table)
            t_rhs = self._check_expr(expr.valor, table)

            if not lval_ok:
                return "ERROR"

            if t_rhs == "void":
                # SEM012
                func_name = expr.valor.nome_funcao if isinstance(expr.valor, no.CallExpr) else "função"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM012",
                    linha=expr.valor.linha,
                    coluna=expr.valor.coluna,
                    mensagem=f"Função “{func_name}” não produz valor (retorno void) e não pode ser usada como expressão de atribuição."
                ))
                return "ERROR"

            if target_type != "ERROR" and t_rhs != "ERROR":
                if not self._is_assignable(target_type, t_rhs):
                    self.diagnostics.append(Diagnostic(
                        codigo="SEM003",
                        linha=expr.valor.linha,
                        coluna=expr.valor.coluna,
                        mensagem=f"Não é possível atribuir {t_rhs} a {target_type} sem conversão permitida (destino “{target_name}”; expressão “{expr_to_str(expr.valor)}”)."
                    ))
                    return "ERROR"

            return target_type

        elif isinstance(expr, no.ArrayAccess):
            # expr.vetor deve ser array
            t_vetor = self._check_expr(expr.vetor, table)
            t_indice = self._check_expr(expr.indice, table)

            vetor_name = expr.vetor.nome if isinstance(expr.vetor, no.Identifier) else expr_to_str(expr.vetor)

            if t_indice != "ERROR" and t_indice != "int":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM006",
                    linha=expr.indice.linha,
                    coluna=expr.indice.coluna,
                    mensagem=f"Índice do vetor “{vetor_name}” deve ser int; recebeu {t_indice} (expressão “{expr_to_str(expr.indice)}”)."
                ))

            if t_vetor.startswith("array_"):
                return t_vetor[len("array_"):]
            elif t_vetor != "ERROR":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM006",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Tentativa de indexar identificador “{vetor_name}” que não é vetor."
                ))
                return "ERROR"
            return "ERROR"

        elif isinstance(expr, no.CallExpr):
            sym = table.lookup(expr.nome_funcao)
            if sym is None:
                self.diagnostics.append(Diagnostic(
                    codigo="SEM001",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Identificador “{expr.nome_funcao}” não declarado neste escopo."
                ))
                for arg in expr.argumentos:
                    self._check_expr(arg, table)
                return "ERROR"

            if sym.categoria != "func":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM007",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"“{expr.nome_funcao}” não é uma função."
                ))
                for arg in expr.argumentos:
                    self._check_expr(arg, table)
                return "ERROR"

            expected_params = sym.params or []
            if len(expr.argumentos) != len(expected_params):
                self.diagnostics.append(Diagnostic(
                    codigo="SEM007",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"“{expr.nome_funcao}” espera {len(expected_params)} argumentos, mas recebeu {len(expr.argumentos)}."
                ))
                for arg in expr.argumentos:
                    self._check_expr(arg, table)
                return sym.tipo

            # Verificar tipos dos argumentos
            for i, (arg, pinfo) in enumerate(zip(expr.argumentos, expected_params), 1):
                p_name, p_type, p_is_array = pinfo
                t_arg = self._check_expr(arg, table)
                if t_arg == "ERROR":
                    continue

                if p_is_array:
                    expected_type = f"array_{p_type}"
                    if t_arg != expected_type:
                        self.diagnostics.append(Diagnostic(
                            codigo="SEM008",
                            linha=arg.linha,
                            coluna=arg.coluna,
                            mensagem=f"Argumento {i} de “{expr.nome_funcao}”: esperado vetor {p_type}, recebido {t_arg} (expressão “{expr_to_str(arg)}”)."
                        ))
                else:
                    if not self._is_assignable(p_type, t_arg):
                        self.diagnostics.append(Diagnostic(
                            codigo="SEM008",
                            linha=arg.linha,
                            coluna=arg.coluna,
                            mensagem=f"Argumento {i} de “{expr.nome_funcao}”: esperado {p_type}, recebido {t_arg} (expressão “{expr_to_str(arg)}”)."
                        ))

            return sym.tipo

        elif isinstance(expr, no.BinaryOp):
            t_esq = self._check_expr(expr.esquerda, table)
            t_dir = self._check_expr(expr.direita, table)

            if t_esq == "ERROR" or t_dir == "ERROR":
                return "ERROR"

            op = expr.operador
            if op in ("+", "-", "*", "/"):
                if t_esq in ("int", "float") and t_dir in ("int", "float"):
                    if t_esq == "int" and t_dir == "int":
                        return "int"
                    return "float"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador aritmético '{op}' exige operandos numéricos; recebido {t_esq} e {t_dir}."
                ))
                return "ERROR"

            elif op == "%":
                if t_esq == "int" and t_dir == "int":
                    return "int"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador módulo '%' exige operandos int; recebido {t_esq} e {t_dir}."
                ))
                return "ERROR"

            elif op in ("<", "<=", ">", ">="):
                if t_esq in ("int", "float") and t_dir in ("int", "float"):
                    return "bool"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador relacional '{op}' exige operandos numéricos; recebido {t_esq} e {t_dir}."
                ))
                return "ERROR"

            elif op in ("==", "!="):
                if (t_esq in ("int", "float") and t_dir in ("int", "float")) or (t_esq == t_dir and t_esq in ("bool", "char")):
                    return "bool"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador de igualdade '{op}' exige tipos comparáveis; recebido {t_esq} e {t_dir}."
                ))
                return "ERROR"

            elif op in ("&&", "||"):
                if t_esq == "bool" and t_dir == "bool":
                    return "bool"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador lógico '{op}' exige operandos bool; recebido {t_esq} e {t_dir}."
                ))
                return "ERROR"

            return "ERROR"

        elif isinstance(expr, no.UnaryOp):
            t_op = self._check_expr(expr.operando, table)
            if t_op == "ERROR":
                return "ERROR"
            if expr.operador == "-":
                if t_op in ("int", "float"):
                    return t_op
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador unário '-' exige operando numérico; recebido {t_op}."
                ))
                return "ERROR"
            elif expr.operador == "!":
                if t_op == "bool":
                    return "bool"
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=expr.linha,
                    coluna=expr.coluna,
                    mensagem=f"Operador unário '!' exige operando bool; recebido {t_op}."
                ))
                return "ERROR"
            return "ERROR"

        return "ERROR"

    def _check_lvalue(self, node: no.NoAST, table: SymbolTable) -> Tuple[bool, str, str]:
        """Retorna (is_lvalue, type, name_or_repr)."""
        if isinstance(node, no.Identifier):
            sym = table.lookup(node.nome)
            if sym is None:
                self.diagnostics.append(Diagnostic(
                    codigo="SEM001",
                    linha=node.linha,
                    coluna=node.coluna,
                    mensagem=f"Identificador “{node.nome}” não declarado neste escopo."
                ))
                return False, "ERROR", node.nome
            if sym.categoria == "func":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM013",
                    linha=node.linha,
                    coluna=node.coluna,
                    mensagem=f"Destino de atribuição não é atribuível; a função “{node.nome}” não é variável."
                ))
                return False, "ERROR", node.nome
            if sym.eh_vetor or sym.categoria == "array":
                self.diagnostics.append(Diagnostic(
                    codigo="SEM003",
                    linha=node.linha,
                    coluna=node.coluna,
                    mensagem=f"Não é possível atribuir diretamente a vetor “{node.nome}”."
                ))
                return False, "ERROR", node.nome
            return True, sym.tipo, node.nome

        elif isinstance(node, no.ArrayAccess):
            elem_type = self._check_expr(node, table)
            name = expr_to_str(node)
            return True, elem_type, name

        else:
            # SEM013: Destino não atribuível
            if isinstance(node, no.Literal) and node.tipo_literal == "int":
                tipo_descr = "o literal inteiro"
            elif isinstance(node, no.Literal):
                tipo_descr = f"o literal {node.tipo_literal}"
            elif isinstance(node, no.CallExpr):
                tipo_descr = "a chamada de função"
            else:
                tipo_descr = "a expressão"

            self.diagnostics.append(Diagnostic(
                codigo="SEM013",
                linha=node.linha,
                coluna=node.coluna,
                mensagem=f"Destino de atribuição não é atribuível; {tipo_descr} “{expr_to_str(node)}” não designa uma variável ou elemento de vetor."
            ))
            return False, "ERROR", expr_to_str(node)

    def _is_assignable(self, target_type: str, value_type: str) -> bool:
        if target_type == value_type:
            return True
        if target_type == "float" and value_type == "int":
            return True
        return False

    def _guarantees_return(self, node: no.NoAST) -> Tuple[bool, Optional[str]]:
        """Retorna (garante_retorno, motivo_de_falha)."""
        if isinstance(node, no.ReturnStmt):
            return True, None

        elif isinstance(node, no.Block):
            for i, cmd in enumerate(node.comandos):
                ret, reason = self._guarantees_return(cmd)
                if ret:
                    return True, None
            # Se nenhum comando garantiu retorno:
            # Procurar se algum comando foi um if sem retorno para dar mensagem descritiva
            for cmd in node.comandos:
                ret, reason = self._guarantees_return(cmd)
                if reason:
                    return False, reason
            return False, "alcança o fim do corpo"

        elif isinstance(node, no.IfStmt):
            if node.senao is None:
                cond_str = expr_to_str(node.condicao)
                return False, f"o ramo em que “{cond_str}” é falso alcança o fim do corpo"
            ret_then, reason_then = self._guarantees_return(node.entao)
            ret_else, reason_else = self._guarantees_return(node.senao)
            if ret_then and ret_else:
                return True, None
            if not ret_then:
                return False, reason_then or "ramo then não retorna"
            return False, reason_else or "ramo else não retorna"

        return False, None
