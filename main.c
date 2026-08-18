#include <stdio.h>
#include <stdlib.h>
#include "scanner.h"
#include "util.h"

/* Le o conteudo inteiro de um arquivo para uma string alocada dinamicamente. */
static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "Erro: nao foi possivel abrir o arquivo '%s'\n", path);
        exit(EXIT_FAILURE);
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *buffer = xmalloc((size_t)size + 1);
    size_t read = fread(buffer, 1, (size_t)size, f);
    buffer[read] = '\0';

    fclose(f);
    return buffer;
}

/* Le todo o conteudo da entrada padrao (stdin) para uma string dinamica. */
static char *read_stdin(void) {
    DynStr buf;
    dynstr_init(&buf);

    int c;
    while ((c = fgetc(stdin)) != EOF) {
        dynstr_push_char(&buf, (char)c);
    }

    char *result = xstrdup(buf.data);
    dynstr_free(&buf);
    return result;
}

int main(int argc, char *argv[]) {
    char *source = (argc >= 2) ? read_file(argv[1]) : read_stdin();

    Scanner sc;
    scanner_init(&sc, source);
    scanner_scan_tokens(&sc);

    scanner_print_tokens(&sc);
    printf("\n");
    scanner_print_errors(&sc);

    int exit_code = scanner_has_errors(&sc) ? EXIT_FAILURE : EXIT_SUCCESS;

    scanner_free(&sc);
    free(source);

    return exit_code;
}
