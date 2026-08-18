#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"

void *xmalloc(size_t size) {
    void *p = malloc(size);
    if (!p) {
        fprintf(stderr, "Erro fatal: memoria insuficiente.\n");
        exit(EXIT_FAILURE);
    }
    return p;
}

void *xrealloc(void *ptr, size_t size) {
    void *p = realloc(ptr, size);
    if (!p) {
        fprintf(stderr, "Erro fatal: memoria insuficiente.\n");
        exit(EXIT_FAILURE);
    }
    return p;
}

char *xstrdup(const char *s) {
    size_t len = strlen(s) + 1;
    char *copy = xmalloc(len);
    memcpy(copy, s, len);
    return copy;
}

void dynstr_init(DynStr *s) {
    s->cap = 16;
    s->len = 0;
    s->data = xmalloc(s->cap);
    s->data[0] = '\0';
}

void dynstr_push_char(DynStr *s, char c) {
    if (s->len + 1 >= s->cap) {
        s->cap *= 2;
        s->data = xrealloc(s->data, s->cap);
    }
    s->data[s->len++] = c;
    s->data[s->len] = '\0';
}

void dynstr_push_str(DynStr *s, const char *str) {
    while (*str) {
        dynstr_push_char(s, *str++);
    }
}

void dynstr_free(DynStr *s) {
    free(s->data);
    s->data = NULL;
    s->len = 0;
    s->cap = 0;
}
