#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 5;
    int *values = NULL;

    if (count == 0 || count > SIZE_MAX / sizeof *values) {
        fputs("invalid allocation size\n", stderr);
        return EXIT_FAILURE;
    }
    values = malloc(count * sizeof *values);
    if (values == NULL) {
        fputs("allocation failed\n", stderr);
        return EXIT_FAILURE;
    }

    for (size_t index = 0; index < count; ++index) {
        values[index] = (int)index + 1;
        printf("%d%s", values[index], index + 1 == count ? "\n" : " ");
    }

    free(values);
    values = NULL;
    return EXIT_SUCCESS;
}
