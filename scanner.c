#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "scanner.h"
#include "token_types.h"
#include "util.h"

#define INITIAL_CAP 64

/* Equivalente ao dicionario SIMPLE_OPS do Python */
static int simple_op_type(char ch, TokenType *out) {
    switch (ch) {
        case '+': *out = PLUS;     return 1;
        case '-': *out = MINUS;    return 1;
        case '*': *out = STAR;     return 1;
        case '%': *out = PERCENT;  return 1;
        case '.': *out = DOT;      return 1;
        case '(': *out = LPAREN;   return 1;
        case ')': *out = RPAREN;   return 1;
        case '{': *out = LBRACE;   return 1;
        case '}': *out = RBRACE;   return 1;
        case '[': *out = LBRACKET; return 1;
        case ']': *out = RBRACKET; return 1;
        case ';': *out = SEMI;     return 1;
        case ',': *out = COMMA;    return 1;
        default: return 0;
    }
}

void scanner_init(Scanner *sc, const char *source) {
    sc->source = source;
    sc->length = strlen(source);
    sc->pos = 0;
    sc->line = 1;
    sc->column = 1;

    sc->tokens_cap = INITIAL_CAP;
    sc->tokens_len = 0;
    sc->tokens = xmalloc(sc->tokens_cap * sizeof(Token));

    sc->errors_cap = INITIAL_CAP;
    sc->errors_len = 0;
    sc->errors = xmalloc(sc->errors_cap * sizeof(LexicalError));
}

void scanner_free(Scanner *sc) {
    for (size_t i = 0; i < sc->tokens_len; i++) {
        token_free(&sc->tokens[i]);
    }
    free(sc->tokens);

    for (size_t i = 0; i < sc->errors_len; i++) {
        error_free(&sc->errors[i]);
    }
    free(sc->errors);
}

/* ---------------------------- navegacao ------------------------------ */

static int at_end(Scanner *sc) {
    return sc->pos >= sc->length;
}

static char peek_at(Scanner *sc, int offset) {
    size_t idx = sc->pos + (size_t)offset;
    return idx < sc->length ? sc->source[idx] : '\0';
}

static char peek(Scanner *sc) {
    return peek_at(sc, 0);
}

static char advance(Scanner *sc) {
    char ch = sc->source[sc->pos];
    sc->pos++;
    if (ch == '\n') {
        sc->line++;
        sc->column = 1;
    } else {
        sc->column++;
    }
    return ch;
}

static int match(Scanner *sc, char expected) {
    if (peek(sc) == expected) {
        advance(sc);
        return 1;
    }
    return 0;
}

static void add_token_raw(Scanner *sc, Token tok) {
    if (sc->tokens_len == sc->tokens_cap) {
        sc->tokens_cap *= 2;
        sc->tokens = xrealloc(sc->tokens, sc->tokens_cap * sizeof(Token));
    }
    sc->tokens[sc->tokens_len++] = tok;
}

static void add_token(Scanner *sc, TokenType type, const char *lexeme, int line, int col) {
    add_token_raw(sc, token_create(type, lexeme, line, col));
}

static void add_error(Scanner *sc, LexicalError err) {
    if (sc->errors_len == sc->errors_cap) {
        sc->errors_cap *= 2;
        sc->errors = xrealloc(sc->errors, sc->errors_cap * sizeof(LexicalError));
    }
    sc->errors[sc->errors_len++] = err;
}

/* ------------------------------ laco principal ------------------------ */

static void skip_whitespace(Scanner *sc) {
    while (!at_end(sc)) {
        char c = peek(sc);
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            advance(sc);
        } else {
            break;
        }
    }
}

static void scan_identifier(Scanner *sc, int line, int col, char first_char);
static void scan_number(Scanner *sc, int line, int col, char first_digit);
static void scan_string(Scanner *sc, int line, int col);
static void scan_char_literal(Scanner *sc, int line, int col);
static void scan_line_comment(Scanner *sc);
static void scan_block_comment(Scanner *sc, int line, int col);
static void scan_operator_or_error(Scanner *sc, char ch, int line, int col);
static void scan_invalid(Scanner *sc, char ch, int line, int col);

static void scan_token(Scanner *sc) {
    int start_line = sc->line;
    int start_col = sc->column;
    char ch = advance(sc);

    if (isalpha((unsigned char)ch) || ch == '_') {
        scan_identifier(sc, start_line, start_col, ch);
    } else if (isdigit((unsigned char)ch)) {
        scan_number(sc, start_line, start_col, ch);
    } else if (ch == '"') {
        scan_string(sc, start_line, start_col);
    } else if (ch == '\'') {
        scan_char_literal(sc, start_line, start_col);
    } else if (ch == '/' && peek(sc) == '/') {
        scan_line_comment(sc);
    } else if (ch == '/' && peek(sc) == '*') {
        scan_block_comment(sc, start_line, start_col);
    } else {
        scan_operator_or_error(sc, ch, start_line, start_col);
    }
}

void scanner_scan_tokens(Scanner *sc) {
    while (!at_end(sc)) {
        skip_whitespace(sc);
        if (at_end(sc)) break;
        scan_token(sc);
    }
    add_token(sc, TOK_EOF, "", sc->line, sc->column);
}

/* ------------------------------ lexemas -------------------------------- */

static void scan_identifier(Scanner *sc, int line, int col, char first_char) {
    DynStr buf;
    dynstr_init(&buf);
    dynstr_push_char(&buf, first_char);

    while (!at_end(sc) && (isalnum((unsigned char)peek(sc)) || peek(sc) == '_')) {
        dynstr_push_char(&buf, advance(sc));
    }

    TokenType type = lookup_reserved_word(buf.data);
    Token tok = token_create(type, buf.data, line, col);
    /* atributo: para ID guardamos o proprio nome; para palavra reservada, None */
    if (type == ID) {
        token_set_attr_string(&tok, buf.data);
    }
    add_token_raw(sc, tok);
    dynstr_free(&buf);
}

static void scan_number(Scanner *sc, int line, int col, char first_digit) {
    DynStr buf;
    dynstr_init(&buf);
    dynstr_push_char(&buf, first_digit);

    while (!at_end(sc) && isdigit((unsigned char)peek(sc))) {
        dynstr_push_char(&buf, advance(sc));
    }

    if (isalpha((unsigned char)peek(sc)) || peek(sc) == '_') {
        while (!at_end(sc) && (isalnum((unsigned char)peek(sc)) || peek(sc) == '_')) {
            dynstr_push_char(&buf, advance(sc));
        }
        add_error(sc, make_invalid_identifier_error(buf.data, line, col));
        add_token(sc, TOK_ERROR, buf.data, line, col);
        dynstr_free(&buf);
        return;
    }

    if (peek(sc) == '.') {
        dynstr_push_char(&buf, advance(sc));

        if (isdigit((unsigned char)peek(sc))) {
            while (!at_end(sc) && isdigit((unsigned char)peek(sc))) {
                dynstr_push_char(&buf, advance(sc));
            }
            if (isalpha((unsigned char)peek(sc)) || peek(sc) == '_') {
                while (!at_end(sc) && (isalnum((unsigned char)peek(sc)) || peek(sc) == '_')) {
                    dynstr_push_char(&buf, advance(sc));
                }
                add_error(sc, make_invalid_identifier_error(buf.data, line, col));
                add_token(sc, TOK_ERROR, buf.data, line, col);
                dynstr_free(&buf);
                return;
            }
            Token tok = token_create(NUM_FLOAT, buf.data, line, col);
            token_set_attr_float(&tok, atof(buf.data));
            add_token_raw(sc, tok);
            dynstr_free(&buf);
            return;
        }

        add_error(sc, make_malformed_real_literal_error(buf.data, line, col));
        add_token(sc, TOK_ERROR, buf.data, line, col);
        dynstr_free(&buf);
        return;
    }

    Token tok = token_create(NUM_INT, buf.data, line, col);
    token_set_attr_int(&tok, atol(buf.data));
    add_token_raw(sc, tok);
    dynstr_free(&buf);
}

static void scan_string(Scanner *sc, int line, int col) {
    DynStr content;
    dynstr_init(&content);

    for (;;) {
        if (at_end(sc) || peek(sc) == '\n') {
            /* cadeia nao terminada: fim de linha/arquivo antes do '"' */
            DynStr lexeme;
            dynstr_init(&lexeme);
            dynstr_push_char(&lexeme, '"');
            dynstr_push_str(&lexeme, content.data);

            add_error(sc, make_unterminated_string_error(lexeme.data, line, col));
            add_token(sc, TOK_ERROR, lexeme.data, line, col);

            dynstr_free(&lexeme);
            dynstr_free(&content);
            return;
        }
        if (peek(sc) == '"') {
            advance(sc);
            break;
        }
        dynstr_push_char(&content, advance(sc));
    }

    DynStr lexeme;
    dynstr_init(&lexeme);
    dynstr_push_char(&lexeme, '"');
    dynstr_push_str(&lexeme, content.data);
    dynstr_push_char(&lexeme, '"');

    Token tok = token_create(STRING, lexeme.data, line, col);
    token_set_attr_string(&tok, content.data);
    add_token_raw(sc, tok);

    dynstr_free(&lexeme);
    dynstr_free(&content);
}

static void scan_char_literal(Scanner *sc, int line, int col) {
    if (at_end(sc) || peek(sc) == '\n') {
        add_error(sc, make_unterminated_char_error("'", line, col));
        add_token(sc, TOK_ERROR, "'", line, col);
        return;
    }

    char ch = advance(sc);
    if (peek(sc) == '\'') {
        advance(sc);
        char lexeme[4] = { '\'', ch, '\'', '\0' };
        char attr[2] = { ch, '\0' };
        Token tok = token_create(CHAR_LITERAL, lexeme, line, col);
        token_set_attr_string(&tok, attr);
        add_token_raw(sc, tok);
    } else {
        char lexeme[3] = { '\'', ch, '\0' };
        add_error(sc, make_unterminated_char_error(lexeme, line, col));
        add_token(sc, TOK_ERROR, lexeme, line, col);
    }
}

static void scan_line_comment(Scanner *sc) {
    advance(sc); /* consome o segundo '/' */
    while (!at_end(sc) && peek(sc) != '\n') {
        advance(sc);
    }
}

static void scan_block_comment(Scanner *sc, int line, int col) {
    advance(sc); /* consome '*' */
    for (;;) {
        if (at_end(sc)) {
            add_error(sc, make_unterminated_comment_error(line, col));
            return;
        }
        if (peek(sc) == '*' && peek_at(sc, 1) == '/') {
            advance(sc);
            advance(sc);
            return;
        }
        advance(sc);
    }
}

static void scan_operator_or_error(Scanner *sc, char ch, int line, int col) {
    TokenType simple;

    if (ch == '=') {
        if (match(sc, '=')) add_token(sc, EQ, "==", line, col);
        else add_token(sc, ASSIGN, "=", line, col);
    } else if (ch == '!') {
        if (match(sc, '=')) add_token(sc, NEQ, "!=", line, col);
        else add_token(sc, NOT, "!", line, col);
    } else if (ch == '<') {
        if (match(sc, '=')) add_token(sc, LE, "<=", line, col);
        else add_token(sc, LT, "<", line, col);
    } else if (ch == '>') {
        if (match(sc, '=')) add_token(sc, GE, ">=", line, col);
        else add_token(sc, GT, ">", line, col);
    } else if (ch == '&') {
        if (match(sc, '&')) add_token(sc, AND, "&&", line, col);
        else scan_invalid(sc, ch, line, col);
    } else if (ch == '|') {
        if (match(sc, '|')) add_token(sc, OR, "||", line, col);
        else scan_invalid(sc, ch, line, col);
    } else if (ch == '/') {
        add_token(sc, SLASH, "/", line, col);
    } else if (simple_op_type(ch, &simple)) {
        char lexeme[2] = { ch, '\0' };
        add_token(sc, simple, lexeme, line, col);
    } else {
        scan_invalid(sc, ch, line, col);
    }
}

static void scan_invalid(Scanner *sc, char ch, int line, int col) {
    char lexeme[2] = { ch, '\0' };
    add_error(sc, make_invalid_symbol_error(lexeme, line, col));
    add_token(sc, TOK_ERROR, lexeme, line, col);
}

/* ------------------------------- relatorios ---------------------------- */

int scanner_has_errors(const Scanner *sc) {
    return sc->errors_len > 0;
}

/* Imita repr() do Python: envolve em aspas simples, escapa aspas/barras
 * e trunca para "21 chars + ...'" quando o resultado passa de 24 chars,
 * igual ao print_tokens() original. */
static void quote_lexeme(const char *lexeme, char *out, size_t out_size) {
    char quoted[300];
    size_t qi = 0;
    quoted[qi++] = '\'';
    for (const char *p = lexeme; *p && qi < sizeof(quoted) - 2; p++) {
        if (*p == '\'' || *p == '\\') {
            quoted[qi++] = '\\';
        }
        quoted[qi++] = *p;
    }
    quoted[qi++] = '\'';
    quoted[qi] = '\0';

    if (strlen(quoted) > 24) {
        snprintf(out, out_size, "%.21s...'", quoted);
    } else {
        snprintf(out, out_size, "%s", quoted);
    }
}

void scanner_print_tokens(const Scanner *sc) {
    char header[128];
    snprintf(header, sizeof(header), "%-14s%-26s%-7s%-8s%s",
             "TIPO", "LEXEMA", "LINHA", "COLUNA", "ATRIBUTO");
    printf("%s\n", header);

    size_t hlen = strlen(header);
    for (size_t i = 0; i < hlen; i++) putchar('-');
    putchar('\n');

    for (size_t i = 0; i < sc->tokens_len; i++) {
        const Token *tok = &sc->tokens[i];

        char lexema_repr[64];
        quote_lexeme(tok->lexeme, lexema_repr, sizeof(lexema_repr));

        char attr_buf[128];
        switch (tok->attr_kind) {
            case ATTR_NONE:
                snprintf(attr_buf, sizeof(attr_buf), "None");
                break;
            case ATTR_INT:
                snprintf(attr_buf, sizeof(attr_buf), "%ld", tok->attr.ival);
                break;
            case ATTR_FLOAT:
                snprintf(attr_buf, sizeof(attr_buf), "%g", tok->attr.fval);
                break;
            case ATTR_STRING:
                snprintf(attr_buf, sizeof(attr_buf), "%s", tok->attr.sval);
                break;
        }

        printf("%-14s%-26s%-7d%-8d%s\n",
               token_type_name(tok->type), lexema_repr, tok->line, tok->column, attr_buf);
    }
}

void scanner_print_errors(const Scanner *sc) {
    if (sc->errors_len == 0) {
        printf("Nenhum erro lexico encontrado.\n");
        return;
    }
    printf("%zu erro(s) lexico(s) encontrado(s):\n", sc->errors_len);
    for (size_t i = 0; i < sc->errors_len; i++) {
        char *diag = error_diagnostic(&sc->errors[i]);
        printf("  [ERRO LEXICO] %s\n", diag);
        free(diag);
    }
}
