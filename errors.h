#ifndef ERRORS_H
#define ERRORS_H

/*
 * errors.h / errors.c
 * ====================
 * C nao tem heranca de excecoes como o Python, entao a hierarquia
 * LexicalError -> InvalidSymbolError / InvalidIdentifierError / ...
 * vira uma unica struct LexicalError com um campo `code` (ErrorCode)
 * que identifica a "subclasse". As funcoes make_*_error(...) fazem o
 * papel dos __init__ de cada subclasse do Python.
 */

typedef enum {
    ERR_LEXICAL,                      /* erro generico (base) */
    ERR_UNKNOWN_SYMBOL,
    ERR_INVALID_IDENTIFIER,
    ERR_MALFORMED_REAL_LITERAL,
    ERR_UNTERMINATED_STRING_LITERAL,
    ERR_UNTERMINATED_BLOCK_COMMENT,
    ERR_UNTERMINATED_CHAR_LITERAL
} ErrorCode;

typedef struct {
    ErrorCode code;
    char *message;
    int line;
    int column;
    char *lexeme;   /* pode ser string vazia ("") quando nao houver lexema */
} LexicalError;

/* Constrói um erro genérico (equivalente a LexicalError.__init__). */
LexicalError error_create(ErrorCode code, const char *message, int line, int column, const char *lexeme);

/* Libera a memoria interna do erro. */
void error_free(LexicalError *err);

/* Monta a mensagem de diagnostico (equivalente a LexicalError.diagnostic()).
 * Retorna uma string alocada dinamicamente; quem chamar deve dar free(). */
char *error_diagnostic(const LexicalError *err);

/* Construtores equivalentes as subclasses do Python */
LexicalError make_invalid_symbol_error(const char *ch, int line, int column);
LexicalError make_invalid_identifier_error(const char *lexeme, int line, int column);
LexicalError make_malformed_real_literal_error(const char *lexeme, int line, int column);
LexicalError make_unterminated_string_error(const char *partial, int line, int column);
LexicalError make_unterminated_comment_error(int line, int column);
LexicalError make_unterminated_char_error(const char *partial, int line, int column);

#endif /* ERRORS_H */
