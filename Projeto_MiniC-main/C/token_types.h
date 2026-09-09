#ifndef TOKEN_TYPES_H
#define TOKEN_TYPES_H

/*
 * token_types.h / token_types.c
 * ==============================
 * Equivalente ao token_types.py: define os tipos de token da
 * linguagem MiniC e a tabela de palavras reservadas.
 *
 * OBS: em C, "EOF" e "ERROR" ja existem como macros da biblioteca
 * padrao (EOF em stdio.h; ERROR pode existir em alguns headers de
 * sistema). Por isso os membros correspondentes do enum foram
 * renomeados para TOK_EOF e TOK_ERROR. O texto impresso continua
 * "EOF" e "ERROR" (veja token_type_name), entao a saida do programa
 * fica igual a versao em Python.
 */

typedef enum {
    /* Palavras reservadas */
    KW_BOOL,
    KW_INT,
    KW_FLOAT,
    KW_CHAR,
    KW_DOUBLE,
    KW_VOID,
    KW_TRUE,
    KW_FALSE,
    KW_IF,
    KW_ELSE,
    KW_WHILE,
    KW_FOR,
    KW_RETURN,
    KW_BREAK,
    KW_CONTINUE,
    KW_PRINT,
    KW_READ,

    /* Identificador */
    ID,

    /* Literais */
    NUM_INT,
    NUM_FLOAT,
    STRING,
    CHAR_LITERAL,

    /* Operadores aritmeticos */
    PLUS,
    MINUS,
    STAR,
    SLASH,
    PERCENT,

    /* Atribuicao e relacionais */
    ASSIGN,
    EQ,
    NEQ,
    LT,
    LE,
    GT,
    GE,

    /* Operadores logicos */
    AND,   /* && */
    OR,    /* || */
    NOT,   /* !  */

    /* Delimitadores */
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    LBRACKET,
    RBRACKET,
    SEMI,
    COMMA,
    DOT,

    /* Controle */
    TOK_EOF,   /* fim de arquivo (equivalente a TokenType.EOF do Python) */
    TOK_ERROR  /* token invalido, mantido para diagnostico */
} TokenType;

/* Nome textual do tipo, para impressao (ex.: KW_INT, ID, PLUS, EOF...) */
const char *token_type_name(TokenType type);

/* Se `word` for uma palavra reservada, grava o tipo em *out_type e
 * retorna 1; caso contrario retorna 0 e *out_type nao e modificado. */
int is_reserved_word(const char *word, TokenType *out_type);

/* Atalho: retorna o tipo da palavra reservada, ou ID se nao for
 * reservada (equivalente a RESERVED_WORDS.get(lexeme, TokenType.ID)). */
TokenType lookup_reserved_word(const char *word);

#endif /* TOKEN_TYPES_H */