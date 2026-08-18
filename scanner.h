#ifndef SCANNER_H
#define SCANNER_H

#include <stddef.h>
#include "token.h"
#include "errors.h"

/* Equivalente a classe Scanner do Python. Os arrays de tokens/erros
 * sao arrays dinamicos (crescem com xrealloc), fazendo o papel das
 * listas Python `self.tokens` e `self.errors`. */
typedef struct {
    const char *source;
    size_t length;
    size_t pos;
    int line;
    int column;

    Token *tokens;
    size_t tokens_len;
    size_t tokens_cap;

    LexicalError *errors;
    size_t errors_len;
    size_t errors_cap;
} Scanner;

/* Inicializa o scanner com o codigo-fonte (nao copia `source`; quem
 * chamar deve manter o ponteiro valido durante o uso do scanner). */
void scanner_init(Scanner *sc, const char *source);

/* Libera toda a memoria interna (tokens e erros). */
void scanner_free(Scanner *sc);

/* Executa a varredura completa (equivalente a scan_tokens()).
 * Ao final, sc->tokens contem todos os tokens, incluindo o TOK_EOF. */
void scanner_scan_tokens(Scanner *sc);

int scanner_has_errors(const Scanner *sc);

/* Imprime a tabela de tokens: TIPO, LEXEMA, LINHA, COLUNA, ATRIBUTO. */
void scanner_print_tokens(const Scanner *sc);

/* Imprime o diagnostico de erros lexicos encontrados. */
void scanner_print_errors(const Scanner *sc);

#endif /* SCANNER_H */
