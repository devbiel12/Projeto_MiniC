#ifndef SEMANTIC_H
#define SEMANTIC_H

#include "ast.h"
#include <stdio.h>

/* Analisa semanticamente uma AST valida. Retorna 1 se aceita, 0 se rejeita. */
int semantic_analyze(const AstNode *program, FILE *out, FILE *err);

#endif
