#ifndef ERRORS_H
#define ERRORS_H

typedef enum {
    ERR_LEXICAL,
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
    char *lexeme;
} LexicalError;

const char *error_code_name(ErrorCode code);
LexicalError error_create(ErrorCode code, const char *message, int line, int column, const char *lexeme);
void error_free(LexicalError *err);
char *error_diagnostic(const LexicalError *err);

LexicalError make_invalid_symbol_error(const char *ch, int line, int column);
LexicalError make_invalid_identifier_error(const char *lexeme, int line, int column);
LexicalError make_malformed_real_literal_error(const char *lexeme, int line, int column);
LexicalError make_unterminated_string_error(const char *partial, int line, int column);
LexicalError make_unterminated_comment_error(const char *partial, int line, int column);
LexicalError make_unterminated_char_error(const char *partial, int line, int column);

#endif /* ERRORS_H */