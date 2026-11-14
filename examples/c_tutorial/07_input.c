#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char buffer[64];
    fputs("Score (0..100): ", stdout);
    if (fflush(stdout) == EOF) {
        return EXIT_FAILURE;
    }
    if (fgets(buffer, sizeof buffer, stdin) == NULL) {
        fputs("could not read input\n", stderr);
        return EXIT_FAILURE;
    }
    /* Require Enter and at most 62 bytes before the newline. */
    if (strchr(buffer, '\n') == NULL) {
        fputs("input too long or missing newline\n", stderr);
        return EXIT_FAILURE;
    }

    char *end = NULL;
    errno = 0;
    long score = strtol(buffer, &end, 10);
    if (end == buffer || errno == ERANGE) {
        fputs("not a representable integer\n", stderr);
        return EXIT_FAILURE;
    }
    while (isspace((unsigned char)*end)) {
        ++end;
    }
    if (*end != '\0' || score < 0 || score > 100) {
        fputs("expected one integer from 0 to 100\n", stderr);
        return EXIT_FAILURE;
    }

    printf("accepted=%ld\n", score);
    return EXIT_SUCCESS;
}
