"""
parser.py
=========
Analisador sintático (Parser) da linguagem MiniC, implementado por
DESCIDA RECURSIVA, seguindo a gramática EBNF definida em
`especificacao-completa-minic.pdf` (seção 4) e a técnica descrita em
`tutorial-conversao-tokens-ast-glc.pdf`.

O parser NÃO reimplementa nem duplica o analisador léxico. Ele recebe a
lista de `Token` já produzida pelo `Scanner` existente (ProjetoMiniC.src.lexer)
e a converte em uma AST (ProjetoMiniC.src.ast).

    tokens = Scanner(codigo_fonte).scan_tokens()
    parser = Parser(tokens)
    programa = parser.parse()
    if parser.possui_erros():
        for erro in parser.erros:
            print(erro.diagnostico())

Hierarquia de precedência implementada (da menor para a maior precedência,
igual à seção 4.2/4.3 da especificação):

    atribuicao        (=, associativo à direita)
    expressao_or       (||)
    expressao_and       (&&)
    expressao_igualdade  (==, !=)
    expressao_relacional  (<, >, <=, >=)
    expressao_aditiva      (+, -)
    expressao_multiplicativa (*, /, %)
    expressao_unaria         (- unário, !)
    expressao_posfixa          ([...], (...))
    primario                     (literais, identificador, parênteses)

Cada nível é uma função (parse_or, parse_and, ...), exatamente como
recomendado no tutorial para eliminar recursão à esquerda e refletir a
precedência diretamente na estrutura das chamadas.
"""

from __future__ import annotations

from typing import List, Optional

try:
    from ..lexer.token_types import TokenType
    from ..lexer.tokens import Token
    from ..ast import nodes as no
except (ImportError, ValueError):
    from ProjetoMiniC.src.lexer.token_types import TokenType
    from ProjetoMiniC.src.lexer.tokens import Token
    from ProjetoMiniC.src.ast import nodes as no

from .errors import ErroSintatico

# ----------------------------------------------------------------------
# Conjuntos de tokens usados para decisões da gramática
# ----------------------------------------------------------------------

# 'tipo' (seção 4 da EBNF): usado em declarações locais/globais e parâmetros.
# Não inclui 'void' -- void só é permitido como tipo de retorno de função.
TIPOS_VARIAVEL = (TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.KW_CHAR)

# 'tipo_retorno' (seção 4 da EBNF): tipo | "void"
TIPOS_RETORNO = TIPOS_VARIAVEL + (TokenType.KW_VOID,)

# Tokens que iniciam um novo comando/declaração -- usados como pontos de
# sincronização durante a recuperação de erros (modo pânico).
INICIO_DECLARACAO_OU_COMANDO = (
    TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.KW_CHAR, TokenType.KW_VOID,
    TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR, TokenType.KW_RETURN,
    TokenType.KW_BREAK, TokenType.KW_CONTINUE, TokenType.KW_PRINT, TokenType.KW_READ,
    TokenType.LBRACE, TokenType.RBRACE,
)

_OPERADORES_IGUALDADE = (TokenType.EQ, TokenType.NEQ)
_OPERADORES_RELACIONAIS = (TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE)
_OPERADORES_ADITIVOS = (TokenType.PLUS, TokenType.MINUS)
_OPERADORES_MULTIPLICATIVOS = (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)


class Parser:
    """Analisador sintático por descida recursiva para a linguagem MiniC."""

    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.posicao: int = 0
        self.erros: List[ErroSintatico] = []

    # ------------------------------------------------------------------
    # Operações básicas de consumo de tokens (peek/advance/check/match/consume)
    # ------------------------------------------------------------------

    def _esta_no_fim(self) -> bool:
        """is_at_end(): verdadeiro quando o token atual é EOF."""
        return self._olhar().tipo is TokenType.EOF

    def _olhar(self) -> Token:
        """peek(): consulta o token atual sem consumi-lo."""
        return self.tokens[self.posicao]

    def _anterior(self) -> Token:
        """Retorna o último token consumido."""
        return self.tokens[self.posicao - 1]

    def _avancar(self) -> Token:
        """advance(): consome o token atual e avança o cursor (se não estiver no fim)."""
        if not self._esta_no_fim():
            self.posicao += 1
        return self._anterior()

    def _checar(self, tipo: TokenType) -> bool:
        """check(): verifica o tipo do token atual sem consumi-lo."""
        if self._esta_no_fim():
            return False
        return self._olhar().tipo is tipo

    def _combinar(self, *tipos: TokenType) -> bool:
        """match(): se o token atual for um dos tipos informados, consome e retorna True."""
        for tipo in tipos:
            if self._checar(tipo):
                self._avancar()
                return True
        return False

    def _consumir(self, tipo: TokenType, mensagem: str) -> Token:
        """consume(): exige um token de um tipo específico; gera erro sintático caso contrário."""
        if self._checar(tipo):
            return self._avancar()
        raise self._erro(self._olhar(), mensagem)

    # ------------------------------------------------------------------
    # Diagnóstico e recuperação de erros
    # ------------------------------------------------------------------

    def _descricao_token(self, token: Token) -> str:
        """Formata o texto do token para uso nas mensagens de erro."""
        if token.tipo is TokenType.EOF:
            return "fim do arquivo"
        return token.lexema

    def _erro(self, token: Token, mensagem: str) -> ErroSintatico:
        """error(): cria (mas não lança) um ErroSintatico e o registra na lista de erros."""
        erro = ErroSintatico(
            mensagem=mensagem,
            linha=token.linha,
            coluna=token.coluna,
            encontrado=self._descricao_token(token),
        )
        self.erros.append(erro)
        return erro

    def _sincronizar(self) -> None:
        """synchronize(): recuperação em modo pânico.

        Descarta tokens até encontrar um ponto seguro para retomar a análise
        (após um ';', ou antes de um token que claramente inicia um novo
        comando/declaração), evitando tanto laço infinito quanto a perda
        total do restante do programa após um único erro.
        """
        self._avancar()
        while not self._esta_no_fim():
            if self._anterior().tipo is TokenType.SEMI:
                return
            if self._olhar().tipo in INICIO_DECLARACAO_OU_COMANDO:
                return
            self._avancar()

    def possui_erros(self) -> bool:
        return len(self.erros) > 0

    # ------------------------------------------------------------------
    # Ponto de entrada
    # ------------------------------------------------------------------

    def parse(self) -> no.Program:
        """programa ::= declaracao_global* declaracao_funcao* funcao_main

        Na prática, declarações globais e funções podem aparecer intercaladas
        na leitura (ambas começam com `tipo identificador`); a distinção é
        feita observando se o identificador é seguido por '(' (função) ou não
        (variável). A ordem de leitura é preservada na lista `declarations`.
        """
        primeiro_token = self._olhar()
        declaracoes: List[no.NoAST] = []

        while not self._esta_no_fim():
            try:
                item = self._declaracao_topo()
                if isinstance(item, list):
                    declaracoes.extend(item)
                else:
                    declaracoes.append(item)
            except ErroSintatico:
                self._sincronizar()

        return no.Program(linha=primeiro_token.linha, coluna=primeiro_token.coluna,
                           declarations=declaracoes)

    # ------------------------------------------------------------------
    # Declarações de nível superior (globais e funções)
    # ------------------------------------------------------------------

    def _declaracao_topo(self):
        """Decide, a partir do tipo e do que vem depois do identificador, se a
        declaração é uma função (`FunctionDecl`) ou uma lista de variáveis
        globais (`List[VarDecl]`)."""
        if self._checar(TokenType.KW_VOID):
            tipo_token = self._avancar()
            nome_token = self._consumir(TokenType.ID, "esperado identificador após 'void'")
            if not self._checar(TokenType.LPAREN):
                raise self._erro(self._olhar(),
                                  "'void' só é permitido como tipo de retorno de função")
            return self._declaracao_funcao(tipo_token, nome_token)

        if not self._olhar().tipo in TIPOS_VARIAVEL:
            token = self._olhar()
            raise self._erro(token, "esperado tipo ('int', 'float', 'bool' ou 'char')")

        tipo_token = self._avancar()
        nome_token = self._consumir(TokenType.ID, "esperado identificador após o tipo")

        if self._checar(TokenType.LPAREN):
            return self._declaracao_funcao(tipo_token, nome_token)

        return self._lista_declaracao_variavel(tipo_token, nome_token)

    def _declaracao_funcao(self, tipo_token: Token, nome_token: Token) -> no.FunctionDecl:
        """declaracao_funcao ::= tipo_retorno identificador "(" parametros? ")" bloco"""
        self._consumir(TokenType.LPAREN, "esperado '(' após o nome da função")
        parametros: List[no.Param] = []
        if not self._checar(TokenType.RPAREN):
            parametros.append(self._parametro())
            while self._combinar(TokenType.COMMA):
                parametros.append(self._parametro())
        self._consumir(TokenType.RPAREN, "esperado ')' após a lista de parâmetros")

        corpo = self._bloco()
        return no.FunctionDecl(
            linha=tipo_token.linha, coluna=tipo_token.coluna,
            tipo_retorno=tipo_token.lexema, nome=nome_token.lexema,
            parametros=parametros, corpo=corpo,
        )

    def _parametro(self) -> no.Param:
        """parametro ::= tipo identificador | tipo identificador "[" "]" """
        if self._olhar().tipo not in TIPOS_VARIAVEL:
            raise self._erro(self._olhar(), "esperado tipo de parâmetro")
        tipo_token = self._avancar()
        nome_token = self._consumir(TokenType.ID, "esperado identificador do parâmetro")
        eh_vetor = False
        if self._combinar(TokenType.LBRACKET):
            self._consumir(TokenType.RBRACKET, "esperado ']' após '[' no parâmetro vetor")
            eh_vetor = True
        return no.Param(linha=nome_token.linha, coluna=nome_token.coluna,
                         tipo=tipo_token.lexema, nome=nome_token.lexema, eh_vetor=eh_vetor)

    def _lista_declaracao_variavel(self, tipo_token: Token, primeiro_nome: Token) -> List[no.VarDecl]:
        """declaracao_local/global ::= tipo declarador ("," declarador)* ";"
        declarador ::= identificador inicializacao? | identificador "[" tamanho "]"
        """
        declaracoes: List[no.VarDecl] = [self._declarador(tipo_token, primeiro_nome)]
        while self._combinar(TokenType.COMMA):
            nome_token = self._consumir(TokenType.ID, "esperado identificador após ','")
            declaracoes.append(self._declarador(tipo_token, nome_token))
        self._consumir(TokenType.SEMI, "esperado ';' ao final da declaração de variável")
        return declaracoes

    def _declarador(self, tipo_token: Token, nome_token: Token) -> no.VarDecl:
        if self._combinar(TokenType.LBRACKET):
            tamanho = self._expressao()
            self._consumir(TokenType.RBRACKET, "esperado ']' após o tamanho do vetor")
            return no.VarDecl(linha=nome_token.linha, coluna=nome_token.coluna,
                               tipo=tipo_token.lexema, nome=nome_token.lexema,
                               inicializador=None, tamanho_vetor=tamanho, eh_vetor=True)

        inicializador = None
        if self._combinar(TokenType.ASSIGN):
            inicializador = self._expressao()
        return no.VarDecl(linha=nome_token.linha, coluna=nome_token.coluna,
                           tipo=tipo_token.lexema, nome=nome_token.lexema,
                           inicializador=inicializador, tamanho_vetor=None, eh_vetor=False)

    # ------------------------------------------------------------------
    # Blocos e comandos
    # ------------------------------------------------------------------

    def _bloco(self) -> no.Block:
        """bloco ::= "{" item_bloco* "}" """
        abre = self._consumir(TokenType.LBRACE, "esperado '{' para iniciar o bloco")
        comandos: List[no.NoAST] = []
        while not self._checar(TokenType.RBRACE) and not self._esta_no_fim():
            try:
                item = self._item_bloco()
                if isinstance(item, list):
                    comandos.extend(item)
                else:
                    comandos.append(item)
            except ErroSintatico:
                self._sincronizar()
        self._consumir(TokenType.RBRACE, "esperado '}' para fechar o bloco")
        return no.Block(linha=abre.linha, coluna=abre.coluna, comandos=comandos)

    def _item_bloco(self):
        """item_bloco ::= declaracao_local | comando"""
        if self._olhar().tipo in TIPOS_VARIAVEL:
            tipo_token = self._avancar()
            nome_token = self._consumir(TokenType.ID, "esperado identificador após o tipo")
            return self._lista_declaracao_variavel(tipo_token, nome_token)
        return self._comando()

    def _comando(self) -> no.NoAST:
        """comando ::= comando_bloco | comando_if | comando_while | comando_for
        | comando_return | comando_break | comando_continue
        | comando_print | comando_read | comando_expressao
        """
        if self._checar(TokenType.LBRACE):
            return self._bloco()
        if self._checar(TokenType.KW_IF):
            return self._comando_if()
        if self._checar(TokenType.KW_WHILE):
            return self._comando_while()
        if self._checar(TokenType.KW_FOR):
            return self._comando_for()
        if self._checar(TokenType.KW_RETURN):
            return self._comando_return()
        if self._checar(TokenType.KW_BREAK):
            return self._comando_break()
        if self._checar(TokenType.KW_CONTINUE):
            return self._comando_continue()
        if self._checar(TokenType.KW_PRINT):
            return self._comando_print()
        if self._checar(TokenType.KW_READ):
            return self._comando_read()
        return self._comando_expressao()

    def _comando_if(self) -> no.IfStmt:
        """comando_if ::= "if" "(" expressao ")" comando ("else" comando)?"""
        palavra = self._avancar()
        self._consumir(TokenType.LPAREN, "esperado '(' após 'if'")
        condicao = self._expressao()
        self._consumir(TokenType.RPAREN, "esperado ')' após a condição do 'if'")
        entao = self._comando()
        senao = None
        if self._combinar(TokenType.KW_ELSE):
            senao = self._comando()
        return no.IfStmt(linha=palavra.linha, coluna=palavra.coluna,
                          condicao=condicao, entao=entao, senao=senao)

    def _comando_while(self) -> no.WhileStmt:
        """comando_while ::= "while" "(" expressao ")" comando"""
        palavra = self._avancar()
        self._consumir(TokenType.LPAREN, "esperado '(' após 'while'")
        condicao = self._expressao()
        self._consumir(TokenType.RPAREN, "esperado ')' após a condição do 'while'")
        corpo = self._comando()
        return no.WhileStmt(linha=palavra.linha, coluna=palavra.coluna,
                             condicao=condicao, corpo=corpo)

    def _comando_for(self) -> no.ForStmt:
        """comando_for ::= "for" "(" expressao? ";" expressao? ";" expressao? ")" comando"""
        palavra = self._avancar()
        self._consumir(TokenType.LPAREN, "esperado '(' após 'for'")

        inicializacao = None
        if not self._checar(TokenType.SEMI):
            inicializacao = self._expressao()
        self._consumir(TokenType.SEMI, "esperado ';' após a inicialização do 'for'")

        condicao = None
        if not self._checar(TokenType.SEMI):
            condicao = self._expressao()
        self._consumir(TokenType.SEMI, "esperado ';' após a condição do 'for'")

        incremento = None
        if not self._checar(TokenType.RPAREN):
            incremento = self._expressao()
        self._consumir(TokenType.RPAREN, "esperado ')' após o cabeçalho do 'for'")

        corpo = self._comando()
        return no.ForStmt(linha=palavra.linha, coluna=palavra.coluna,
                           inicializacao=inicializacao, condicao=condicao,
                           incremento=incremento, corpo=corpo)

    def _comando_return(self) -> no.ReturnStmt:
        """comando_return ::= "return" expressao? ";" """
        palavra = self._avancar()
        valor = None
        if not self._checar(TokenType.SEMI):
            valor = self._expressao()
        self._consumir(TokenType.SEMI, "esperado ';' após 'return'")
        return no.ReturnStmt(linha=palavra.linha, coluna=palavra.coluna, valor=valor)

    def _comando_break(self) -> no.BreakStmt:
        palavra = self._avancar()
        self._consumir(TokenType.SEMI, "esperado ';' após 'break'")
        return no.BreakStmt(linha=palavra.linha, coluna=palavra.coluna)

    def _comando_continue(self) -> no.ContinueStmt:
        palavra = self._avancar()
        self._consumir(TokenType.SEMI, "esperado ';' após 'continue'")
        return no.ContinueStmt(linha=palavra.linha, coluna=palavra.coluna)

    def _comando_print(self) -> no.PrintStmt:
        """comando_print ::= "print" "(" argumento_print ")" ";" """
        palavra = self._avancar()
        self._consumir(TokenType.LPAREN, "esperado '(' após 'print'")
        valor = self._expressao()
        self._consumir(TokenType.RPAREN, "esperado ')' após o argumento de 'print'")
        self._consumir(TokenType.SEMI, "esperado ';' após 'print(...)'")
        return no.PrintStmt(linha=palavra.linha, coluna=palavra.coluna, valor=valor)

    def _comando_read(self) -> no.ReadStmt:
        """comando_read ::= "read" "(" localizavel ")" ";" """
        palavra = self._avancar()
        self._consumir(TokenType.LPAREN, "esperado '(' após 'read'")
        alvo = self._localizavel()
        self._consumir(TokenType.RPAREN, "esperado ')' após o argumento de 'read'")
        self._consumir(TokenType.SEMI, "esperado ';' após 'read(...)'")
        return no.ReadStmt(linha=palavra.linha, coluna=palavra.coluna, alvo=alvo)

    def _comando_expressao(self) -> no.ExprStmt:
        """comando_expressao ::= expressao? ";" """
        if self._checar(TokenType.SEMI):
            ponto_virgula = self._avancar()
            return no.ExprStmt(linha=ponto_virgula.linha, coluna=ponto_virgula.coluna, expressao=None)
        inicio = self._olhar()
        expressao = self._expressao()
        self._consumir(TokenType.SEMI, "esperado ';' ao final do comando")
        return no.ExprStmt(linha=inicio.linha, coluna=inicio.coluna, expressao=expressao)

    def _localizavel(self) -> no.NoAST:
        """Um 'localizavel' é um identificador, opcionalmente seguido de um ou
        mais acessos a vetor (ex.: `x`, `valores[i]`). Usado em `read(...)` e
        como alvo de atribuição."""
        nome_token = self._consumir(TokenType.ID, "esperado identificador")
        expr: no.NoAST = no.Identifier(linha=nome_token.linha, coluna=nome_token.coluna,
                                        nome=nome_token.lexema)
        while self._combinar(TokenType.LBRACKET):
            colchete = self._anterior()
            indice = self._expressao()
            self._consumir(TokenType.RBRACKET, "esperado ']' após o índice do vetor")
            expr = no.ArrayAccess(linha=colchete.linha, coluna=colchete.coluna,
                                   vetor=expr, indice=indice)
        return expr

    # ------------------------------------------------------------------
    # Expressões (em ordem de precedência crescente)
    # ------------------------------------------------------------------

    def _expressao(self) -> no.NoAST:
        """expressao ::= atribuicao"""
        return self._atribuicao()

    def _atribuicao(self) -> no.NoAST:
        """atribuicao ::= localizavel "=" atribuicao | expressao_or

        Estratégia clássica de descida recursiva para atribuição
        associativa à direita: analisa-se primeiro o lado esquerdo como uma
        expressão comum (nível OR); se um '=' for encontrado em seguida,
        valida-se que o que foi lido é um alvo atribuível (Identifier ou
        ArrayAccess) e a atribuição é montada recursivamente.
        """
        expr = self._expressao_or()

        if self._checar(TokenType.ASSIGN):
            igual = self._avancar()
            valor = self._atribuicao()
            if isinstance(expr, (no.Identifier, no.ArrayAccess)):
                return no.Assignment(linha=igual.linha, coluna=igual.coluna,
                                      alvo=expr, valor=valor)
            raise self._erro(igual, "alvo de atribuição inválido (esperado identificador ou vetor)")

        return expr

    def _expressao_or(self) -> no.NoAST:
        """expressao_or ::= expressao_and ("||" expressao_and)*"""
        esquerda = self._expressao_and()
        while self._checar(TokenType.OR):
            op = self._avancar()
            direita = self._expressao_and()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador="||", esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_and(self) -> no.NoAST:
        """expressao_and ::= expressao_igualdade ("&&" expressao_igualdade)*"""
        esquerda = self._expressao_igualdade()
        while self._checar(TokenType.AND):
            op = self._avancar()
            direita = self._expressao_igualdade()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador="&&", esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_igualdade(self) -> no.NoAST:
        """expressao_igualdade ::= expressao_relacional (("=="|"!=") expressao_relacional)*"""
        esquerda = self._expressao_relacional()
        while self._checar(TokenType.EQ) or self._checar(TokenType.NEQ):
            op = self._avancar()
            direita = self._expressao_relacional()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador=op.lexema, esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_relacional(self) -> no.NoAST:
        """expressao_relacional ::= expressao_aditiva (op_rel expressao_aditiva)*"""
        esquerda = self._expressao_aditiva()
        while self._olhar().tipo in _OPERADORES_RELACIONAIS:
            op = self._avancar()
            direita = self._expressao_aditiva()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador=op.lexema, esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_aditiva(self) -> no.NoAST:
        """expressao_aditiva ::= expressao_multiplicativa (("+"|"-") expressao_multiplicativa)*"""
        esquerda = self._expressao_multiplicativa()
        while self._olhar().tipo in _OPERADORES_ADITIVOS:
            op = self._avancar()
            direita = self._expressao_multiplicativa()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador=op.lexema, esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_multiplicativa(self) -> no.NoAST:
        """expressao_multiplicativa ::= expressao_unaria (("*"|"/"|"%") expressao_unaria)*"""
        esquerda = self._expressao_unaria()
        while self._olhar().tipo in _OPERADORES_MULTIPLICATIVOS:
            op = self._avancar()
            direita = self._expressao_unaria()
            esquerda = no.BinaryOp(linha=op.linha, coluna=op.coluna,
                                    operador=op.lexema, esquerda=esquerda, direita=direita)
        return esquerda

    def _expressao_unaria(self) -> no.NoAST:
        """expressao_unaria ::= ("-" | "!") expressao_unaria | expressao_posfixa

        Recursiva à direita: permite encadear unários (ex.: `!!a`, `--a`
        sintaticamente, mesmo que semanticamente incomuns) e diferencia
        claramente o menos unário (`-x`) do menos binário (`a - x`), pois
        só entra nesta regra quando o '-' aparece em posição de operando.
        """
        if self._checar(TokenType.MINUS) or self._checar(TokenType.NOT):
            op = self._avancar()
            operando = self._expressao_unaria()
            return no.UnaryOp(linha=op.linha, coluna=op.coluna,
                               operador=op.lexema, operando=operando)
        return self._expressao_posfixa()

    def _expressao_posfixa(self) -> no.NoAST:
        """expressao_posfixa ::= primario ( "[" expressao "]" | "(" argumentos? ")" )*"""
        expr = self._primario()
        while True:
            if self._combinar(TokenType.LBRACKET):
                colchete = self._anterior()
                indice = self._expressao()
                self._consumir(TokenType.RBRACKET, "esperado ']' após o índice do vetor")
                expr = no.ArrayAccess(linha=colchete.linha, coluna=colchete.coluna,
                                       vetor=expr, indice=indice)
            elif self._combinar(TokenType.LPAREN):
                parenteses = self._anterior()
                if not isinstance(expr, no.Identifier):
                    raise self._erro(parenteses, "chamada inválida: apenas identificadores podem ser chamados")
                argumentos: List[no.NoAST] = []
                if not self._checar(TokenType.RPAREN):
                    argumentos.append(self._expressao())
                    while self._combinar(TokenType.COMMA):
                        argumentos.append(self._expressao())
                self._consumir(TokenType.RPAREN, "esperado ')' após os argumentos da chamada")
                expr = no.CallExpr(linha=parenteses.linha, coluna=parenteses.coluna,
                                    nome_funcao=expr.nome, argumentos=argumentos)
            else:
                break
        return expr

    def _primario(self) -> no.NoAST:
        """primario ::= identificador | literal_inteiro | literal_real
        | literal_booleano | literal_caractere | "(" expressao ")"

        Extensão pragmática: também aceita literal_cadeia (STRING), já que o
        lexer produz esse token (usado tipicamente em `print("mensagem")`)
        embora a tabela de tipos da especificação não preveja um tipo
        'string' de primeira classe -- ver PROBLEMA ENCONTRADO no relatório.
        """
        token = self._olhar()

        if self._combinar(TokenType.NUM_INT):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=token.atributo, tipo_literal="int")
        if self._combinar(TokenType.NUM_FLOAT):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=token.atributo, tipo_literal="float")
        if self._combinar(TokenType.KW_TRUE):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=True, tipo_literal="bool")
        if self._combinar(TokenType.KW_FALSE):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=False, tipo_literal="bool")
        if self._combinar(TokenType.CHAR_LITERAL):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=token.atributo, tipo_literal="char")
        if self._combinar(TokenType.STRING):
            return no.Literal(linha=token.linha, coluna=token.coluna,
                               valor=token.atributo, tipo_literal="string")
        if self._combinar(TokenType.ID):
            return no.Identifier(linha=token.linha, coluna=token.coluna, nome=token.lexema)
        if self._combinar(TokenType.LPAREN):
            expr = self._expressao()
            self._consumir(TokenType.RPAREN, "esperado ')' após a expressão entre parênteses")
            return expr

        raise self._erro(token, "era esperado identificador, literal, '(' ou expressão unária")
