#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "token.h"
#include "util.h"

Token token_create(TokenType type, const char *lexeme, int line, int column, const char *attr) {
    Token tok;
    tok.type = type;
    tok.lexeme = xstrdup(lexeme ? lexeme : "");
    tok.line = line;
    tok.column = column;
    tok.attribute = attr ? xstrdup(attr) : NULL;
    return tok;
}

void token_set_attr_int(Token *tok, long value) {
    char buf[64];
    snprintf(buf, sizeof(buf), "%ld", value);
    if (tok->attribute) free(tok->attribute);
    tok->attribute = xstrdup(buf);
}

void token_set_attr_float(Token *tok, double value) {
    char buf[64];
    snprintf(buf, sizeof(buf), "%g", value);
    if (tok->attribute) free(tok->attribute);
    tok->attribute = xstrdup(buf);
}

void token_set_attr_string(Token *tok, const char *value) {
    if (tok->attribute) free(tok->attribute);
    tok->attribute = value ? xstrdup(value) : NULL;
}

void token_free(Token *tok) {
    if (tok->lexeme) {
        free(tok->lexeme);
        tok->lexeme = NULL;
    }
    if (tok->attribute) {
        free(tok->attribute);
        tok->attribute = NULL;
    }
}