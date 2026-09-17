"""
scanner.py
==========
Mecanismo principal de análise léxica (Scanner). Converte o código fonte
em uma lista sequencial de tokens e identifica violações sintáticas/léxicas.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

DIRETORIO_ATUAL = Path(__file__).resolve().parent
if str(DIRETORIO_ATUAL) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_ATUAL))

try:
    from .analysis_result import ResultadoAnalise
    from .errors import (
        ErroCaractereNaoTerminado,
        ErroCadeiaNaoTerminada,
        ErroComentarioNaoTerminado,
        ErroIdentificadorInvalido,
        ErroLexico,
        ErroLiteralRealMalformado,
        ErroSimboloInvalido,
    )
    from .jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
    from .token_types import PALAVRAS_RESERVADAS, TokenType
    from .tokens import Token
except (ImportError, ValueError):
    from ProjetoMiniC.src.lexer.analysis_result import ResultadoAnalise
    from ProjetoMiniC.src.lexer.errors import (
        ErroCaractereNaoTerminado,
        ErroCadeiaNaoTerminada,
        ErroComentarioNaoTerminado,
        ErroIdentificadorInvalido,
        ErroLexico,
        ErroLiteralRealMalformado,
        ErroSimboloInvalido,
    )
    from ProjetoMiniC.src.lexer.jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
    from ProjetoMiniC.src.lexer.token_types import PALAVRAS_RESERVADAS, TokenType
    from ProjetoMiniC.src.lexer.tokens import Token


class Scanner:
    """Analisador léxico por autômato finito determinístico de leitura direta."""

    # Mapeamento direto de pontuações de caractere único
    OPERADORES_SIMPLES: Dict[str, TokenType] = {
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

    def __init__(self, codigo_fonte: str):
        self.codigo_fonte: str = codigo_fonte
        self.tamanho: int = len(codigo_fonte)
        self.posicao: int = 0
        self.linha: int = 1
        self.coluna: int = 1
        self.tokens: List[Token] = []
        self.errors: List[LexicalError] = []

    def _at_end(self) -> bool:
        return self.pos >= self.length

    @staticmethod
    def _is_identifier_start(ch: str) -> bool:
        return ch == "_" or (ch.isascii() and ch.isalpha())

    @staticmethod
    def _is_identifier_continue(ch: str) -> bool:
        return Scanner._is_identifier_start(ch) or (ch.isascii() and ch.isdigit())

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
            self.coluna += 1
        return caractere

    def _compara_e_avanca(self, esperado: str) -> bool:
        """Avança o ponteiro apenas se o próximo caractere corresponder ao caractere esperado."""
        if self._espiar() == esperado:
            self._avancar()
            return True
        return False

    def _adicionar_token(self, tipo: TokenType, lexema: str, linha: int, coluna: int,
                           atributo: Optional[Union[int, float, str]] = None) -> None:
        """Instancia e adiciona um token reconhecido na coleção principal."""
        self.tokens.append(Token(tipo, lexema, linha, coluna, atributo))

    def scan_tokens(self) -> List[Token]:
        """Varre iterativamente a fonte até o fim e anexa o token EOF final."""
        while not self._esta_no_fim():
            self._ignorar_espacos_em_branco()
            if self._esta_no_fim():
                break
            self._processar_proximo_token()
        self.tokens.append(Token(TokenType.EOF, "", self.linha, self.coluna, None))
        return self.tokens

    def analisar(self) -> ResultadoAnalise:
        """Executa a análise e compila o relatório formal no objeto ResultadoAnalise."""
        self.scan_tokens()
        return AnalysisResult(tokens=self.tokens, errors=self.errors)

    def _skip_whitespace(self) -> None:
        while not self._at_end() and self._peek() in " \t\r\n":
            self._advance()

    def _scan_token(self) -> None:
        start_line, start_col = self.line, self.column
        ch = self._advance()

        if self._is_identifier_start(ch):
            self._identifier(start_line, start_col, ch)
        elif ch.isascii() and ch.isdigit():
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

    def _identifier(self, line: int, col: int, first_char: str) -> None:
        lexeme = first_char
        while not self._at_end() and self._is_identifier_continue(self._peek()):
            lexeme += self._advance()

        ttype = RESERVED_WORDS.get(lexeme, TokenType.ID)
        attribute = lexeme if ttype is TokenType.ID else None
        self._add_token(ttype, lexeme, line, col, attribute)

    def _number(self, line: int, col: int, first_digit: str) -> None:
        digits = first_digit
        while not self._at_end() and self._peek().isascii() and self._peek().isdigit():
            digits += self._advance()

        # Caso i06: Identificador iniciado por dígito
        if not self._at_end() and self._is_identifier_start(self._peek()):
            letters = ""
            letters_col = self.column
            while not self._at_end() and self._is_identifier_continue(self._peek()):
                letters += self._advance()

            self.errors.append(InvalidIdentifierError(digits + letters, line, col))
            self._add_token(TokenType.NUM_INT, digits, line, col, int(digits))
            self._add_token(TokenType.ID, letters, line, letters_col, letters)
            return

        # Número real ou malformado (Caso i05)
        if self._peek() == ".":
            if not (self._peek(1).isascii() and self._peek(1).isdigit()):
                dot_col = self.column
                self._advance()
                self.errors.append(MalformedRealLiteralError(digits + ".", line, col))
                self._add_token(TokenType.NUM_INT, digits, line, col, int(digits))
                self._add_token(TokenType.DOT, ".", line, dot_col, None)
                return

            lexeme = digits + self._advance()
            while not self._at_end() and self._peek().isascii() and self._peek().isdigit():
                lexeme += self._advance()

            self._adicionar_token(TokenType.NUM_FLOAT, lexema, linha, coluna, float(lexema))
            return

        self._adicionar_token(TokenType.NUM_INT, digitos, linha, coluna, int(digitos))

    def _string(self, line: int, col: int) -> None:
        start_pos = self.pos - 1
        content = ""
        closed = False

        while not self._esta_no_fim():
            if self._espiar() == "\n":
                break
            if self._espiar() == '"':
                self._avancar()
                fechado = True
                break
            ch = self._advance()
            if ch == "\\" and not self._at_end() and self._peek() != "\n":
                escape = self._advance()
                if escape in "nt\\\"'":
                    content += {"n": "\n", "t": "\t"}.get(escape, escape)
                    continue
                content += "\\" + escape
                continue
            content += ch

        if closed:
            lexeme = self.source[start_pos:self.pos]
            self._add_token(TokenType.STRING, lexeme, line, col, content)
        else:
            err_lexeme = self.source[start_pos:self.pos]
            self.errors.append(UnterminatedStringError(err_lexeme, line, col))

            # Mantém delimitadores finais no fluxo para recuperação dos fixtures.
            while self.pos > start_pos + 1 and self.source[self.pos - 1] in ") ;}]":
                self.pos -= 1
                self.column -= 1

    def _char_literal(self, line: int, col: int) -> None:
        if self._at_end() or self._peek() == "\n":
            self.errors.append(UnterminatedCharError("'", line, col))
            return

        ch = self._advance()
        raw = ch
        if ch == "\\":
            if self._at_end() or self._peek() == "\n":
                self.errors.append(UnterminatedCharError("'\\", line, col))
                return
            escape = self._advance()
            if escape not in "nt\\\"'":
                self.errors.append(UnterminatedCharError("'\\" + escape, line, col))
                return
            raw = "\\" + escape
            ch = {"n": "\n", "t": "\t"}.get(escape, escape)
        if self._match("'"):
            self._add_token(TokenType.CHAR_LITERAL, f"'{raw}'", line, col, ch)
        else:
            lexema = f"'{caractere}"
            self.erros.append(ErroCaractereNaoTerminado(lexema, linha, coluna))
            if self._espiar() == ";":
                self._avancar()

    def _processar_comentario_linha(self) -> None:
        """Descarta o restante da linha atual ao identificar comentários de linha (//)."""
        self._avancar()
        while not self._esta_no_fim() and self._espiar() != "\n":
            self._avancar()

    def _processar_comentario_bloco(self, linha: int, coluna: int) -> None:
        """Processa comentários de múltiplas linhas (/* ... */)."""
        posicao_inicial = self.posicao - 1
        self._avancar()
        while True:
            if self._esta_no_fim():
                lexema = self.codigo_fonte[posicao_inicial:]
                self.erros.append(ErroComentarioNaoTerminado(linha, coluna, lexema))
                return
            if self._espiar() == "*" and self._espiar(1) == "/":
                self._avancar()
                self._avancar()
                return
            self._avancar()

    def _processar_operador_ou_erro(self, caractere: str, linha: int, coluna: int) -> None:
        """Analisa operadores de um ou dois caracteres e aciona erro para símbolos desconhecidos."""
        if caractere == "=":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.EQ, "==", linha, coluna)
            else:
                self._adicionar_token(TokenType.ASSIGN, "=", linha, coluna)
        elif caractere == "!":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.NEQ, "!=", linha, coluna)
            else:
                self._adicionar_token(TokenType.NOT, "!", linha, coluna)
        elif caractere == "<":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.LE, "<=", linha, coluna)
            else:
                self._adicionar_token(TokenType.LT, "<", linha, coluna)
        elif caractere == ">":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.GE, ">=", linha, coluna)
            else:
                self._adicionar_token(TokenType.GT, ">", linha, coluna)
        elif caractere == "&":
            if self._compara_e_avanca("&"):
                self._adicionar_token(TokenType.AND, "&&", linha, coluna)
            else:
                self._sinalizar_invalido(caractere, linha, coluna)
        elif caractere == "|":
            if self._compara_e_avanca("|"):
                self._adicionar_token(TokenType.OR, "||", linha, coluna)
            else:
                self._sinalizar_invalido(caractere, linha, coluna)
        elif caractere == "/":
            self._adicionar_token(TokenType.SLASH, "/", linha, coluna)
        elif caractere in self.OPERADORES_SIMPLES:
            self._adicionar_token(self.OPERADORES_SIMPLES[caractere], caractere, linha, coluna)
        else:
            self._sinalizar_invalido(caractere, linha, coluna)

    def _sinalizar_invalido(self, caractere: str, linha: int, coluna: int) -> None:
        """Registra a presença de caracteres não reconhecidos."""
        self.erros.append(ErroSimboloInvalido(caractere, linha, coluna))

    def possui_erros(self) -> bool:
        """Informa se foram registrados erros na execução do scanner."""
        return len(self.erros) > 0

    def imprimir_tokens(self) -> None:
        """Exibe a lista dos tokens reconhecidos em formato de tabela no terminal."""
        cabecalho = f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for token in self.tokens:
            nome, lexema, linha, coluna, atributo = token.para_linha_tabela()
            lexema_repr = repr(lexema)
            if len(lexema_repr) > 24:
                lexema_repr = lexema_repr[:21] + "...'"
            print(f"{nome:<14}{lexema_repr:<26}{linha:<7}{coluna:<8}{atributo}")

    def imprimir_erros(self) -> None:
        """Imprime os erros identificados de maneira legível."""
        if not self.erros:
            print("Nenhum erro léxico encontrado.")
            return
        print(f"{len(self.erros)} erro(s) léxico(s) encontrado(s):")
        for erro in self.erros:
            print(f"  [ERRO LÉXICO] {erro.diagnostico()}")


def main() -> int:
    """Função de entrada do CLI ao rodar diretamente o módulo scanner.py."""
    caminho_alvo: str | None = None
    modo_apenas_jsonl = True

    for arg in sys.argv[1:]:
        if arg == "--jsonl":
            modo_apenas_jsonl = True
        elif not arg.startswith("--") and caminho_alvo is None:
            caminho_alvo = arg

    if not caminho_alvo:
        print("Uso: python scanner.py <arquivo.c | arquivo.minic> [--jsonl]", file=sys.stderr)
        return 1

    arquivo = Path(caminho_alvo)
    if not arquivo.exists() or not arquivo.is_file():
        print(f"Erro: Arquivo '{caminho_alvo}' não encontrado.", file=sys.stderr)
        return 1

    try:
        conteudo = arquivo.read_text(encoding="utf-8")
    except OSError as err:
        print(f"Erro ao ler arquivo: {err}", file=sys.stderr)
        return 1

    scanner = Scanner(conteudo)
    scanner.scan_tokens()

    saida_tokens_json = serialize_tokens_jsonl(scanner.tokens)
    saida_erros_json = serialize_errors_jsonl(scanner.erros) if scanner.erros else ""

    if modo_apenas_jsonl:
        if saida_tokens_json:
            print(saida_tokens_json)
        if saida_erros_json:
            print(saida_erros_json, file=sys.stderr)
        return 2 if scanner.possui_erros() else 0

    print("=" * 80)
    print(f"Análise Léxica - Arquivo: {arquivo.name}")
    print("=" * 80)
    print("Tokens reconhecidos:")
    scanner.imprimir_tokens()
    print("-" * 80)
    print("Diagnóstico:")
    scanner.imprimir_erros()

    print("-" * 80)
    print("Saída JSONL (Tokens):")
    print(saida_tokens_json if saida_tokens_json else "(vazio)")

    if scanner.erros:
        print("-" * 80)
        print("Saída JSONL (Erros):")
        print(saida_erros_json if saida_erros_json else "(vazio)")

    return 2 if scanner.possui_erros() else 0


if __name__ == "__main__":
    sys.exit(main())
