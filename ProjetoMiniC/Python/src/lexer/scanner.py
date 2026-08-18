"""
scanner.py
==========

Implementa a classe `Scanner`: o analisador léxico da linguagem MiniC.

Percorre o código-fonte caractere a caractere (autômato manual, sem
expressões regulares e sem bibliotecas externas), monta a lista de
tokens e coleciona os erros léxicos encontrados, sem interromper a
análise (recuperação local: ignora o trecho inválido e continua).

Depende de `token_types.py`, `tokens.py` e `errors.py`.
"""

from typing import Dict, List, Optional, Union

from .errors import (
    InvalidSymbolError,
    InvalidIdentifierError,
    LexicalError,
    MalformedRealLiteralError,
    UnterminatedCharError,
    UnterminatedCommentError,
    UnterminatedStringError,
)
from .token_types import RESERVED_WORDS, TokenType
from .tokens import Token


class Scanner:
    """
    Analisador léxico da linguagem MiniC.

    Uso:
        scanner = Scanner(codigo_fonte)
        tokens = scanner.scan_tokens()
        scanner.print_tokens()
        scanner.print_errors()
    """

    # ------------------------------------------------------------------
    # Operadores simples que são reconhecidos por um único caractere.
    # Esses símbolos são convertidos diretamente em tokens específicos,
    # como '+' -> PLUS, '(' -> LPAREN, ';' -> SEMI.
    # ------------------------------------------------------------------
    SIMPLE_OPS: Dict[str, TokenType] = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "%": TokenType.PERCENT,
        ".": TokenType.DOT,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        ";": TokenType.SEMI,
        ",": TokenType.COMMA,
    }

    def __init__(self, source: str):
        # Inicializa o estado do scanner com o texto completo do programa,
        # a posição atual, as coordenadas de linha/coluna e as listas de
        # tokens/erros que serão montadas durante a análise.
        self.source: str = source
        self.length: int = len(source)
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.tokens: List[Token] = []
        self.errors: List[LexicalError] = []

    # ---------------------------- navegação ------------------------------ #
    def _at_end(self) -> bool:
        return self.pos >= self.length

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < self.length else "\0"

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _add_token(self, ttype: TokenType, lexeme: str, line: int, col: int,
                    attribute: Optional[Union[int, float, str]] = None) -> None:
        self.tokens.append(Token(ttype, lexeme, line, col, attribute))

    # ------------------------------ laço principal ------------------------ #
    def scan_tokens(self) -> List[Token]:
        """Executa a varredura completa e devolve a lista de tokens (com EOF)."""
        # O loop percorre todo o texto, ignorando espaços e quebrando o
        # processo em tokens. No final, adiciona o marcador de fim de arquivo.
        while not self._at_end():
            self._skip_whitespace()
            if self._at_end():
                break
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column, None))
        return self.tokens

    def _skip_whitespace(self) -> None:
        while not self._at_end() and self._peek() in " \t\r\n":
            self._advance()

    def _scan_token(self) -> None:
        # Cada caractere do código-fonte é analisado a partir de seu tipo.
        # Dependendo do símbolo, o scanner chama a rotina apropriada:
        # identificador, número, string, comentário, operador ou erro.
        start_line, start_col = self.line, self.column
        ch = self._advance()

        if ch.isalpha() or ch == "_":
            self._identifier(start_line, start_col, ch)
        elif ch.isdigit():
            self._number(start_line, start_col, ch)
        elif ch == '"':
            self._string(start_line, start_col)
        elif ch == "'":
            self._char_literal(start_line, start_col)
        elif ch == "/" and self._peek() == "/":
            self._line_comment()
        elif ch == "/" and self._peek() == "*":
            self._block_comment(start_line, start_col)
        else:
            self._operator_or_error(ch, start_line, start_col)

    # ------------------------------ lexemas -------------------------------- #
    def _identifier(self, line: int, col: int, first_char: str) -> None:
        # Reconhece nomes de variáveis, funções e palavras reservadas.
        # Ex.: int, main, total, x, print.
        lexeme = first_char
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            lexeme += self._advance()

        ttype = RESERVED_WORDS.get(lexeme, TokenType.ID)
        # atributo: para ID guardamos o próprio nome; para palavra reservada, None
        attribute = lexeme if ttype is TokenType.ID else None
        self._add_token(ttype, lexeme, line, col, attribute)

    def _number(self, line: int, col: int, first_digit: str) -> None:
        # Lê sequências numéricas inteiras ou decimais.
        # Ex.: 10, 3.14, 0.
        lexeme = first_digit

        while not self._at_end() and self._peek().isdigit():
            lexeme += self._advance()

        if self._peek().isalpha() or self._peek() == "_":
            while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
                lexeme += self._advance()
            self.errors.append(InvalidIdentifierError(lexeme, line, col))
            self._add_token(TokenType.ERROR, lexeme, line, col)
            return

        if self._peek() == ".":
            lexeme += self._advance()
            if self._peek().isdigit():
                while not self._at_end() and self._peek().isdigit():
                    lexeme += self._advance()
                if self._peek().isalpha() or self._peek() == "_":
                    while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
                        lexeme += self._advance()
                    self.errors.append(InvalidIdentifierError(lexeme, line, col))
                    self._add_token(TokenType.ERROR, lexeme, line, col)
                    return
                self._add_token(TokenType.NUM_FLOAT, lexeme, line, col, float(lexeme))
                return

            self.errors.append(MalformedRealLiteralError(lexeme, line, col))
            self._add_token(TokenType.ERROR, lexeme, line, col)
            return

        self._add_token(TokenType.NUM_INT, lexeme, line, col, int(lexeme))

    def _string(self, line: int, col: int) -> None:
        # Processa literais de string entre aspas duplas.
        # Se a string não for fechada, registra um erro léxico.
        content = ""
        while True:
            if self._at_end() or self._peek() == "\n":
                # cadeia não terminada: fim de linha/arquivo antes do '"'
                lexeme = '"' + content
                self.errors.append(UnterminatedStringError(lexeme, line, col))
                self._add_token(TokenType.ERROR, lexeme, line, col)
                return
            if self._peek() == '"':
                self._advance()
                break
            content += self._advance()

        lexeme = f'"{content}"'
        self._add_token(TokenType.STRING, lexeme, line, col, content)

    def _char_literal(self, line: int, col: int) -> None:
        if self._at_end() or self._peek() == "\n":
            self.errors.append(UnterminatedCharError("'", line, col))
            self._add_token(TokenType.ERROR, "'", line, col)
            return

        ch = self._advance()
        if self._peek() == "'":
            self._advance()
            self._add_token(TokenType.CHAR_LITERAL, f"'{ch}'", line, col, ch)
        else:
            lexeme = f"'{ch}"
            self.errors.append(UnterminatedCharError(lexeme, line, col))
            self._add_token(TokenType.ERROR, lexeme, line, col)

    def _line_comment(self) -> None:
        # Ignora comentários de linha do tipo // até o fim da linha.
        self._advance()  # consome o segundo '/'
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _block_comment(self, line: int, col: int) -> None:
        # Ignora comentários de bloco /* ... */ e gera erro se não forem fechados.
        self._advance()  # consome '*'
        while True:
            if self._at_end():
                self.errors.append(UnterminatedCommentError(line, col))
                return
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance()
                self._advance()
                return
            self._advance()

    def _operator_or_error(self, ch: str, line: int, col: int) -> None:
        # Reúne operadores compostos e valida caracteres isolados.
        # Ex.: ==, !=, <=, >=, &&, ||, !, +, -, *, /.
        if ch == "=":
            if self._match("="):
                self._add_token(TokenType.EQ, "==", line, col)
            else:
                self._add_token(TokenType.ASSIGN, "=", line, col)
        elif ch == "!":
            if self._match("="):
                self._add_token(TokenType.NEQ, "!=", line, col)
            else:
                self._add_token(TokenType.NOT, "!", line, col)
        elif ch == "<":
            if self._match("="):
                self._add_token(TokenType.LE, "<=", line, col)
            else:
                self._add_token(TokenType.LT, "<", line, col)
        elif ch == ">":
            if self._match("="):
                self._add_token(TokenType.GE, ">=", line, col)
            else:
                self._add_token(TokenType.GT, ">", line, col)
        elif ch == "&":
            if self._match("&"):
                self._add_token(TokenType.AND, "&&", line, col)
            else:
                self._invalid(ch, line, col)
        elif ch == "|":
            if self._match("|"):
                self._add_token(TokenType.OR, "||", line, col)
            else:
                self._invalid(ch, line, col)
        elif ch == "/":
            self._add_token(TokenType.SLASH, "/", line, col)
        elif ch in self.SIMPLE_OPS:
            self._add_token(self.SIMPLE_OPS[ch], ch, line, col)
        else:
            self._invalid(ch, line, col)

    def _invalid(self, ch: str, line: int, col: int) -> None:
        self.errors.append(InvalidSymbolError(ch, line, col))
        self._add_token(TokenType.ERROR, ch, line, col)

    # ------------------------------- relatórios ---------------------------- #
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_tokens(self) -> None:
        """Imprime a tabela de tokens: Nome, Lexema, Linha, Coluna, Atributo."""
        cabecalho = f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for tok in self.tokens:
            nome, lexema, linha, coluna, attr = tok.as_row()
            lexema_repr = repr(lexema)
            if len(lexema_repr) > 24:
                lexema_repr = lexema_repr[:21] + "...'"
            print(f"{nome:<14}{lexema_repr:<26}{linha:<7}{coluna:<8}{attr}")

    def print_errors(self) -> None:
        """Imprime o diagnóstico de erros léxicos encontrados."""
        if not self.errors:
            print("Nenhum erro léxico encontrado.")
            return
        print(f"{len(self.errors)} erro(s) léxico(s) encontrado(s):")
        for err in self.errors:
            print(f"  [ERRO LÉXICO] {err.diagnostic()}")
