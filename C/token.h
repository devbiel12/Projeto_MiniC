#ifndef TOKEN_H
#define TOKEN_H

#include "token_types.h"

/*
 * token.h / token.c
 * ==================
 * Representação do Token léxico em C.
 * O campo `attribute` armazena a representação textual do atributo
 * (ex.: valor do número, nome do identificador ou conteúdo da string),
 * equivalente ao campo opcional `attribute` do Python.
 */
typedef struct {
    TokenType type;
    char *lexeme;       /* Alocado dinamicamente */
    int line;
    int column;
    char *attribute;    /* Alocado dinamicamente (NULL se não houver) */
} Token;

/* Cria um token com atributo opcional (copia `lexeme` e `attr` internamente) */
Token token_create(TokenType type, const char *lexeme, int line, int column, const char *attr);

/* Setters auxiliares para definição de atributos numéricos ou textuais */
void token_set_attr_int(Token *tok, long value);
void token_set_attr_float(Token *tok, double value);
void token_set_attr_string(Token *tok, const char *value);

/* Libera a memória interna do token (lexeme e attribute) */
void token_free(Token *tok);

#endif /* TOKEN_H */