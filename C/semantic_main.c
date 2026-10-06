#include "scanner.h"
#include "parser.h"
#include "semantic.h"
#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Uso: ./semantic <arquivo.c | arquivo.minic>\n");
        return 1;
    }
    char *source = read_file(argv[1]);
    if (!source) {
        fprintf(stderr, "Erro: Arquivo '%s' não encontrado.\n", argv[1]);
        return 1;
    }
    Scanner scanner;
    scanner_init(&scanner, source);
    scanner_scan_tokens(&scanner);
    if (scanner_has_errors(&scanner)) {
        scanner_print_errors(&scanner);
        scanner_free(&scanner); free(source);
        return 2;
    }
    Parser parser;
    parser_init(&parser, scanner.tokens, scanner.tokens_len);
    AstNode *root = parser_parse(&parser);
    if (!root) {
        scanner_free(&scanner); free(source);
        return 3;
    }
    int ok = semantic_analyze(root, stdout, stderr);
    fputc('\n', ok ? stdout : stderr);
    ast_free(root);
    scanner_free(&scanner);
    free(source);
    return ok ? 0 : 4;
}
