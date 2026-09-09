#include <string.h>
#include <stddef.h>
#include "token_types.h"

const char *token_type_name(TokenType type) {
    switch (type) {
        /* Palavras reservadas */
        case KW_BOOL:     return "KW_BOOL";
        case KW_INT:      return "KW_INT";
        case KW_FLOAT:    return "KW_FLOAT";
        case KW_CHAR:     return "KW_CHAR";
        case KW_DOUBLE:   return "KW_DOUBLE";
        case KW_VOID:     return "KW_VOID";
        case KW_TRUE:     return "KW_TRUE";
        case KW_FALSE:    return "KW_FALSE";
        case KW_IF:       return "KW_IF";
        case KW_ELSE:     return "KW_ELSE";
        case KW_WHILE:    return "KW_WHILE";
        case KW_FOR:      return "KW_FOR";
        case KW_RETURN:   return "KW_RETURN";
        case KW_BREAK:    return "KW_BREAK";
        case KW_CONTINUE: return "KW_CONTINUE";
        case KW_PRINT:    return "KW_PRINT";
        case KW_READ:     return "KW_READ";

        /* Identificador e Literais */
        case ID:          return "IDENTIFIER";
        case NUM_INT:     return "INT_LITERAL";
        case NUM_FLOAT:   return "REAL_LITERAL";
        case STRING:      return "STRING_LITERAL";
        case CHAR_LITERAL:return "CHAR_LITERAL";

        /* Operadores */
        case PLUS:        return "PLUS_OP";
        case MINUS:       return "MINUS_OP";
        case STAR:        return "STAR_OP";
        case SLASH:       return "SLASH_OP";
        case PERCENT:     return "PERCENT_OP";
        case ASSIGN:      return "ASSIGN_OP";
        case EQ:          return "EQ_OP";
        case NEQ:         return "NEQ_OP";
        case LT:          return "LT_OP";
        case LE:          return "LE_OP";
        case GT:          return "GT_OP";
        case GE:          return "GE_OP";
        case AND:         return "AND_OP";
        case OR:          return "OR_OP";
        case NOT:         return "NOT_OP";

        /* Delimitadores e Pontuação */
        case LPAREN:      return "LPAREN_PUNCT";
        case RPAREN:      return "RPAREN_PUNCT";
        case LBRACE:      return "LBRACE_PUNCT";
        case RBRACE:      return "RBRACE_PUNCT";
        case LBRACKET:    return "LBRACKET_PUNCT";
        case RBRACKET:    return "RBRACKET_PUNCT";
        case SEMI:        return "SEMI_PUNCT";
        case COMMA:       return "COMMA_PUNCT";
        case DOT:         return "DOT_PUNCT";

        case TOK_EOF:     return "EOF";
        case TOK_ERROR:   return "ERROR";
    }
    return "UNKNOWN";
}

typedef struct {
    const char *word;
    TokenType type;
} ReservedWord;

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
            if (out_type) *out_type = RESERVED_WORDS[i].type;
            return 1;
        }
    }
    return 0;
}

TokenType lookup_reserved_word(const char *word) {
    TokenType t;
    if (is_reserved_word(word, &t)) return t;
    return ID;
}