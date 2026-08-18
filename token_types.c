#include <string.h>
#include "token_types.h"

const char *token_type_name(TokenType type) {
    switch (type) {
        case KW_BOOL: return "KW_BOOL";
        case KW_INT: return "KW_INT";
        case KW_FLOAT: return "KW_FLOAT";
        case KW_CHAR: return "KW_CHAR";
        case KW_DOUBLE: return "KW_DOUBLE";
        case KW_VOID: return "KW_VOID";
        case KW_TRUE: return "KW_TRUE";
        case KW_FALSE: return "KW_FALSE";
        case KW_IF: return "KW_IF";
        case KW_ELSE: return "KW_ELSE";
        case KW_WHILE: return "KW_WHILE";
        case KW_FOR: return "KW_FOR";
        case KW_RETURN: return "KW_RETURN";
        case KW_BREAK: return "KW_BREAK";
        case KW_CONTINUE: return "KW_CONTINUE";
        case KW_PRINT: return "KW_PRINT";
        case KW_READ: return "KW_READ";
        case ID: return "ID";
        case NUM_INT: return "NUM_INT";
        case NUM_FLOAT: return "NUM_FLOAT";
        case STRING: return "STRING";
        case CHAR_LITERAL: return "CHAR_LITERAL";
        case PLUS: return "PLUS";
        case MINUS: return "MINUS";
        case STAR: return "STAR";
        case SLASH: return "SLASH";
        case PERCENT: return "PERCENT";
        case ASSIGN: return "ASSIGN";
        case EQ: return "EQ";
        case NEQ: return "NEQ";
        case LT: return "LT";
        case LE: return "LE";
        case GT: return "GT";
        case GE: return "GE";
        case AND: return "AND";
        case OR: return "OR";
        case NOT: return "NOT";
        case LPAREN: return "LPAREN";
        case RPAREN: return "RPAREN";
        case LBRACE: return "LBRACE";
        case RBRACE: return "RBRACE";
        case LBRACKET: return "LBRACKET";
        case RBRACKET: return "RBRACKET";
        case SEMI: return "SEMI";
        case COMMA: return "COMMA";
        case DOT: return "DOT";
        case TOK_EOF: return "EOF";
        case TOK_ERROR: return "ERROR";
    }
    return "UNKNOWN";
}

typedef struct {
    const char *word;
    TokenType type;
} ReservedWord;

/* Equivalente ao dicionario RESERVED_WORDS do Python */
static const ReservedWord RESERVED_WORDS[] = {
    {"bool", KW_BOOL},
    {"int", KW_INT},
    {"float", KW_FLOAT},
    {"char", KW_CHAR},
    {"double", KW_DOUBLE},
    {"void", KW_VOID},
    {"true", KW_TRUE},
    {"false", KW_FALSE},
    {"if", KW_IF},
    {"else", KW_ELSE},
    {"while", KW_WHILE},
    {"for", KW_FOR},
    {"return", KW_RETURN},
    {"break", KW_BREAK},
    {"continue", KW_CONTINUE},
    {"print", KW_PRINT},
    {"read", KW_READ},
};

#define NUM_RESERVED_WORDS (sizeof(RESERVED_WORDS) / sizeof(RESERVED_WORDS[0]))

int is_reserved_word(const char *word, TokenType *out_type) {
    for (size_t i = 0; i < NUM_RESERVED_WORDS; i++) {
        if (strcmp(RESERVED_WORDS[i].word, word) == 0) {
            *out_type = RESERVED_WORDS[i].type;
            return 1;
        }
    }
    return 0;
}

TokenType lookup_reserved_word(const char *word) {
    TokenType t;
    if (is_reserved_word(word, &t)) {
        return t;
    }
    return ID;
}
