#ifndef UTIL_H
#define UTIL_H

#include <stddef.h>

/* ------------------------------------------------------------------
 * Wrappers de alocacao que encerram o programa com uma mensagem clara
 * em caso de falta de memoria, em vez de continuar com um ponteiro
 * invalido (equivalente ao comportamento "seguro" que o Python tem
 * embutido).
 * ------------------------------------------------------------------ */
void *xmalloc(size_t size);
void *xrealloc(void *ptr, size_t size);
char *xstrdup(const char *s);

/* ------------------------------------------------------------------
 * DynStr: string de tamanho dinamico, usada para montar lexemas que
 * podem crescer sem limite conhecido de antemao (identificadores,
 * numeros, strings, etc.), assim como o Python faz com `lexeme += ch`.
 * ------------------------------------------------------------------ */
typedef struct {
    char *data;
    size_t len;
    size_t cap;
} DynStr;

void dynstr_init(DynStr *s);
void dynstr_push_char(DynStr *s, char c);
void dynstr_push_str(DynStr *s, const char *str);
void dynstr_free(DynStr *s);

#endif /* UTIL_H */
