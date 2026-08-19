#ifndef SCANNER_H
#define SCANNER_H

#include "token.h"
#include "errors.h"
#include <stdbool.h>

/* Estrutura principal do analisador léxico em C */
typedef struct {
    const char *source;
    int length;
    int pos;
    int line;
    int column;
    TokenList tokens;
    ErrorList errors;
} Scanner;

/* Inicialização e liberação do scanner */
void scanner_init(Scanner *scanner, const char *source);
void scanner_free(Scanner *scanner);

/* Execução da varredura léxica completa */
void scanner_scan_tokens(Scanner *scanner);

/* Verificação de presença de erros */
bool scanner_has_errors(const Scanner *scanner);

/* Impressão dos tokens formatados em tabela */
void scanner_print_tokens(const Scanner *scanner);

/* Impressão do diagnóstico dos erros léxicos */
void scanner_print_errors(const Scanner *scanner);

#endif /* SCANNER_H */