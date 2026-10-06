"""Parser descendente recursivo para os tokens produzidos pelo lexer MiniC."""

from __future__ import annotations

from typing import List, Optional, Sequence

from ProjetoMiniC.src.ast import (
    Assign, Binary, Block, Break, Call, Continue, ExprStmt, For, Function, Id,
    If, Index, Lit, Parameter, Print, Program, Read, Return, Unary, VarDecl,
    While,
)
from ProjetoMiniC.src.lexer.token_types import TokenType
from ProjetoMiniC.src.lexer.tokens import Token

TYPE_TOKENS = (TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.KW_CHAR)


class SyntaxErrorMiniC(Exception):
    """Diagnóstico sintático com a posição do token que provocou a falha."""

    def __init__(self, token: Token, expected: str):
        self.token = token
        self.expected = expected
        found = "EOF" if token.type is TokenType.EOF else repr(token.lexeme)
        super().__init__(
            "Erro sintático na linha {}, coluna {}: esperado {}; encontrado {}".format(
                token.line, token.column, expected, found
            )
        )


class Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = list(tokens)
        self.current = 0
        self.errors: List[SyntaxErrorMiniC] = []

    @staticmethod
    def _mark(node, token):
        """Preserva posição da origem sem alterar a S-expression da AST."""
        if token is not None:
            node.line = token.line
            node.column = token.column
            node.lexeme = token.lexeme
        return node

    def parse(self) -> Optional[Program]:
        declarations = []
        first = self._peek() if self.tokens else None
        while not self._at_end():
            try:
                declarations.extend(self._top_level())
            except SyntaxErrorMiniC as error:
                self.errors.append(error)
                self._synchronize()
        return self._mark(Program(declarations), first) if not self.errors else None

    def _top_level(self):
        if not self._check_any(TYPE_TOKENS + (TokenType.KW_VOID,)):
            return [self._statement()]
        type_token = self._advance()
        if type_token.type is TokenType.KW_VOID:
            return [self._function_after_type(type_token)]
        name = self._consume(TokenType.ID, "identificador após o tipo")
        if self._match(TokenType.LPAREN):
            return [self._function_after_open(type_token, name)]
        return self._global_after_name(type_token, name)

    def _function_after_type(self, type_token: Token):
        name = self._consume(TokenType.ID, "identificador após 'void'")
        self._consume(TokenType.LPAREN, "'(' após o nome da função")
        return self._function_after_open(type_token, name)

    def _function_after_open(self, type_token: Token, name: Token) -> Function:
        parameters = self._parameters()
        self._consume(TokenType.RPAREN, "')' após os parâmetros")
        body = self._block()
        return self._mark(Function(type_token.lexeme, name.lexeme, parameters, body), name)

    def _parameters(self) -> List[Parameter]:
        parameters = []
        if self._check(TokenType.RPAREN):
            return parameters
        while True:
            type_token = self._consume_any(TYPE_TOKENS, "tipo do parâmetro")
            name = self._consume(TokenType.ID, "identificador do parâmetro")
            is_array = False
            if self._match(TokenType.LBRACKET):
                self._consume(TokenType.RBRACKET, "']' após '[' no parâmetro")
                is_array = True
            parameters.append(self._mark(Parameter(type_token.lexeme, name.lexeme, is_array), name))
            if not self._match(TokenType.COMMA):
                break
            if self._check(TokenType.RPAREN):
                raise self._error(self._peek(), "parâmetro após ','")
        return parameters

    def _global_after_name(self, type_token: Token, name: Token) -> List[VarDecl]:
        declarations = [self._declarator(type_token.lexeme, name)]
        while self._match(TokenType.COMMA):
            declarations.append(self._declarator(
                type_token.lexeme,
                self._consume(TokenType.ID, "identificador após ','"),
            ))
        self._consume(TokenType.SEMI, "';' após declaração global")
        return declarations

    def _block(self) -> Block:
        lbrace = self._consume(TokenType.LBRACE, "'{' para iniciar bloco")
        items = []
        while not self._check(TokenType.RBRACE) and not self._at_end():
            try:
                items.extend(self._local_declaration() if self._check_any(TYPE_TOKENS) else [self._statement()])
            except SyntaxErrorMiniC as error:
                self.errors.append(error)
                self._synchronize()
        self._consume(TokenType.RBRACE, "'}' para encerrar bloco")
        return self._mark(Block(items), lbrace)

    def _local_declaration(self) -> List[VarDecl]:
        type_token = self._advance()
        type_name = type_token.lexeme
        declarations = [self._declarator(type_name, self._consume(TokenType.ID, "identificador na declaração local"))]
        while self._match(TokenType.COMMA):
            declarations.append(self._declarator(type_name, self._consume(TokenType.ID, "identificador após ','")))
        self._consume(TokenType.SEMI, "';' após declaração local")
        return declarations

    def _declarator(self, type_name: str, name: Token) -> VarDecl:
        size = None
        if self._match(TokenType.LBRACKET):
            size = self._expression()
            self._consume(TokenType.RBRACKET, "']' após o tamanho do vetor")
        initializer = self._expression() if self._match(TokenType.ASSIGN) else None
        return self._mark(VarDecl(type_name, name.lexeme, initializer, size), name)

    def _primary(self):
        if self._match(TokenType.ID):
            token = self._previous()
            return self._mark(Id(token.lexeme), token)
        if self._match(TokenType.NUM_INT):
            token = self._previous()
            return self._mark(Lit("int", str(token.atributo if hasattr(token, 'atributo') else token.lexeme)), token)
        if self._match(TokenType.NUM_FLOAT):
            token = self._previous()
            return self._mark(Lit("real", str(token.atributo if hasattr(token, 'atributo') else token.lexeme)), token)
        if self._match(TokenType.KW_TRUE):
            return self._mark(Lit("bool", "true"), self._previous())
        if self._match(TokenType.KW_FALSE):
            return self._mark(Lit("bool", "false"), self._previous())
        if self._match(TokenType.CHAR_LITERAL):
            token = self._previous()
            valor = token.atributo if hasattr(token, 'atributo') and token.atributo is not None else token.lexeme
            return self._mark(Lit("char", token.lexeme), token)
        if self._match(TokenType.STRING):
            token = self._previous()
            valor = token.atributo if hasattr(token, 'atributo') and token.atributo is not None else token.lexeme
            return self._mark(Lit("string", token.lexeme), token)
        if self._match(TokenType.LPAREN):
            expression = self._expression()
            self._consume(TokenType.RPAREN, "')' após expressão")
            return expression
        raise self._error(self._peek(), "expressão")

    def _statement(self):
        if self._match(TokenType.LBRACE):
            self.current -= 1
            return self._block()
        if self._match(TokenType.KW_IF):
            token = self._previous()
            return self._mark(self._if_statement(), token)
        if self._match(TokenType.KW_WHILE):
            token = self._previous()
            return self._mark(self._while_statement(), token)
        if self._match(TokenType.KW_FOR):
            token = self._previous()
            return self._mark(self._for_statement(), token)
        if self._match(TokenType.KW_RETURN):
            token = self._previous()
            return self._mark(self._return_statement(), token)
        if self._match(TokenType.KW_BREAK):
            token = self._previous()
            self._consume(TokenType.SEMI, "';' após break")
            return self._mark(Break(), token)
        if self._match(TokenType.KW_CONTINUE):
            token = self._previous()
            self._consume(TokenType.SEMI, "';' após continue")
            return self._mark(Continue(), token)
        if self._match(TokenType.KW_PRINT):
            token = self._previous()
            return self._mark(self._print_statement(), token)
        if self._match(TokenType.KW_READ):
            token = self._previous()
            return self._mark(self._read_statement(), token)
        if self._match(TokenType.KW_ELSE):
            raise self._error(self._previous(), "'if' antes de 'else'")
        expression = None if self._check(TokenType.SEMI) else self._expression()
        self._consume(TokenType.SEMI, "';' após expressão")
        return self._mark(ExprStmt(expression), getattr(expression, "lexeme", None) and self._token_for_node(expression) or self._previous())

    def _token_for_node(self, node):
        line = getattr(node, "line", None)
        col = getattr(node, "column", None)
        if line is None or col is None:
            return self._previous()
        for token in self.tokens:
            if token.line == line and token.column == col:
                return token
        return self._previous()

    def _if_statement(self):
        self._consume(TokenType.LPAREN, "'(' após if")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "')' após a condição")
        then_branch = self._statement()
        else_branch = self._statement() if self._match(TokenType.KW_ELSE) else None
        return If(condition, then_branch, else_branch)

    def _while_statement(self):
        self._consume(TokenType.LPAREN, "'(' após while")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "')' após a condição")
        if self._check(TokenType.EOF):
            raise self._error(self._peek(), "corpo após while")
        return While(condition, self._statement())

    def _for_statement(self):
        self._consume(TokenType.LPAREN, "'(' após for")
        initializer = None if self._check(TokenType.SEMI) else self._expression()
        self._consume(TokenType.SEMI, "';' após inicialização do for")
        condition = None if self._check(TokenType.SEMI) else self._expression()
        self._consume(TokenType.SEMI, "';' após condição do for")
        increment = None if self._check(TokenType.RPAREN) else self._expression()
        self._consume(TokenType.RPAREN, "')' após cláusulas do for")
        return For(initializer, condition, increment, self._statement())

    def _return_statement(self):
        value = None if self._check(TokenType.SEMI) else self._expression()
        self._consume(TokenType.SEMI, "';' após return")
        return Return(value)

    def _print_statement(self):
        self._consume(TokenType.LPAREN, "'(' após print")
        value = self._expression()
        self._consume(TokenType.RPAREN, "')' após argumento de print")
        self._consume(TokenType.SEMI, "';' após print")
        return Print(value)

    def _read_statement(self):
        self._consume(TokenType.LPAREN, "'(' após read")
        target = self._postfix()
        if not isinstance(target, (Id, Index)):
            raise self._error(self._previous(), "localizável como argumento de read")
        self._consume(TokenType.RPAREN, "')' após argumento de read")
        self._consume(TokenType.SEMI, "';' após read")
        return Read(target)

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expression = self._or()
        if self._match(TokenType.ASSIGN):
            equals = self._previous()
            value = self._assignment()
            return self._mark(Assign(expression, value), getattr(expression, "lexeme", None) and self._token_for_node(expression) or equals)
        return expression

    def _or(self): return self._left(self._and, (TokenType.OR,))
    def _and(self): return self._left(self._equality, (TokenType.AND,))
    def _equality(self): return self._left(self._relational, (TokenType.EQ, TokenType.NEQ))
    def _relational(self): return self._left(self._additive, (TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE))
    def _additive(self): return self._left(self._multiplicative, (TokenType.PLUS, TokenType.MINUS))
    def _multiplicative(self): return self._left(self._unary, (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT))

    def _left(self, next_rule, operators):
        expression = next_rule()
        while self._match(*operators):
            operator = self._previous()
            left = expression
            expression = self._mark(Binary(operator.lexeme, left, next_rule()), self._token_for_node(left) or operator)
        return expression

    def _unary(self):
        if self._match(TokenType.MINUS, TokenType.NOT):
            token = self._previous()
            return self._mark(Unary(token.lexeme, self._unary()), token)
        return self._postfix()

    def _postfix(self):
        expression = self._primary()
        while True:
            if self._match(TokenType.LBRACKET):
                token = self._previous()
                index = self._expression()
                self._consume(TokenType.RBRACKET, "']' após índice")
                expression = self._mark(Index(expression, index), token)
            elif self._match(TokenType.LPAREN):
                token = self._previous()
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._expression())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._expression())
                self._consume(TokenType.RPAREN, "')' após argumentos")
                expression = self._mark(Call(expression, arguments), self._token_for_node(expression) or token)
            else:
                break
        return expression

    def _synchronize(self):
        if not self._at_end():
            self._advance()
        while not self._at_end():
            if self._previous().type in (TokenType.SEMI, TokenType.RBRACE):
                return
            if self._peek().type in TYPE_TOKENS + (
                TokenType.KW_VOID, TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR,
                TokenType.KW_RETURN, TokenType.KW_BREAK, TokenType.KW_CONTINUE,
                TokenType.KW_PRINT, TokenType.KW_READ, TokenType.LBRACE,
            ):
                return
            self._advance()

    def _match(self, *types):
        if self._check_any(types):
            self._advance()
            return True
        return False

    def _consume(self, token_type, expected):
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), expected)

    def _consume_any(self, types, expected):
        if self._check_any(types):
            return self._advance()
        raise self._error(self._peek(), expected)

    def _check(self, token_type):
        return not self._at_end() and self._peek().type is token_type

    def _check_any(self, types):
        return any(self._check(token_type) for token_type in types)

    def _advance(self):
        if not self._at_end():
            self.current += 1
        return self._previous()

    def _at_end(self): return self._peek().type is TokenType.EOF
    def _peek(self): return self.tokens[self.current]
    def _previous(self): return self.tokens[self.current - 1]
    def _error(self, token, expected): return SyntaxErrorMiniC(token, expected)
