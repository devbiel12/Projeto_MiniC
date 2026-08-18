#include <stdlib.h>
#include "token.h"
#include "util.h"

Token token_create(TokenType type, const char *lexeme, int line, int column) {
    Token tok;
    tok.type = type;
    tok.lexeme = xstrdup(lexeme);
    tok.line = line;
    tok.column = column;
    tok.attr_kind = ATTR_NONE;
    tok.attr.sval = NULL;
    return tok;
}

void token_set_attr_int(Token *tok, long value) {
    tok->attr_kind = ATTR_INT;
    tok->attr.ival = value;
}

void token_set_attr_float(Token *tok, double value) {
    tok->attr_kind = ATTR_FLOAT;
    tok->attr.fval = value;
}

void token_set_attr_string(Token *tok, const char *value) {
    tok->attr_kind = ATTR_STRING;
    tok->attr.sval = xstrdup(value);
}

void token_free(Token *tok) {
    free(tok->lexeme);
    if (tok->attr_kind == ATTR_STRING && tok->attr.sval) {
        free(tok->attr.sval);
    }
}
