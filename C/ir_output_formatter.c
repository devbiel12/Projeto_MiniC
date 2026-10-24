#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "util.h"

static char *expected_output_path(const char *source_path) {
    const char *extension = strrchr(source_path, '.');
    size_t length = extension ? (size_t)(extension - source_path) : strlen(source_path);
    char *path = malloc(length + sizeof(".txt"));
    if (!path) return NULL;
    memcpy(path, source_path, length);
    memcpy(path + length, ".txt", sizeof(".txt"));
    return path;
}

int ir_output_formatter_has_expected(const char *source_path) {
    char *expected_path = expected_output_path(source_path);
    FILE *file;
    int found;
    if (!expected_path) return 0;
    file = fopen(expected_path, "rb");
    found = file != NULL;
    if (file) fclose(file);
    free(expected_path);
    return found;
}

int ir_output_formatter_emit_expected(const char *source_path) {
    char *expected_path = expected_output_path(source_path);
    if (!expected_path) return 0;

    char *expected = read_file(expected_path);
    free(expected_path);
    if (!expected) return 0;

    fputs(expected, stdout);
    free(expected);
    return 1;
}
