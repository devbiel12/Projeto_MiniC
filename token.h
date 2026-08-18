#ifndef TOKEN_H
#define TOKEN_H

#include "token_types.h"

/* Como C nao tem "Union[int, float, str, None]" pronto, guardamos o
 * atributo do token numa union marcada (tagged union): attr_kind diz
 * qual campo da union esta valido, igual ao "attribute" opcional do
 * Token do Python. */
typedef enum {
    ATTR_NONE,
    ATTR_INT,
    ATTR_FLOAT,
    ATTR_STRING
} AttributeKind;

typedef struct {
    TokenType type;
    char *lexeme;      /* alocado dinamicamente (equivalente a str do Python) */
    int line;
    int column;
    AttributeKind attr_kind;
    union {
        long ival;
        double fval;
        char *sval;     /* alocado dinamicamente */
    } attr;
} Token;

/* Cria um token com atributo ATTR_NONE. Copia `lexeme` internamente. */
Token token_create(TokenType type, const char *lexeme, int line, int column);

void token_set_attr_int(Token *tok, long value);
void token_set_attr_float(Token *tok, double value);
void token_set_attr_string(Token *tok, const char *value);

/* Libera a memoria interna do token (lexeme e, se houver, attr.sval). */
void token_free(Token *tok);

#endif /* TOKEN_H */
