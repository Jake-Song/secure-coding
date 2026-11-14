#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

enum { MAX_SCORES = 100 };

/* Accept only ASCII decimal digits and values from 0 to 100. */
static bool parse_score(const char *text, int *result) {
    if (*text == '\0') {
        return false;
    }
    for (const char *cursor = text; *cursor != '\0'; ++cursor) {
        if (*cursor < '0' || *cursor > '9') {
            return false;
        }
    }

    errno = 0;
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (errno == ERANGE || *end != '\0' || value < 0 || value > 100) {
        return false;
    }
    *result = (int)value;
    return true;
}

int main(int argc, char *argv[]) {
    if (argc < 3 || argc > MAX_SCORES + 2) {
        fputs("usage: 08_score_report NEW_FILE SCORE... (1..100 scores)\n", stderr);
        return EXIT_FAILURE;
    }

    int scores[MAX_SCORES];
    size_t count = (size_t)(argc - 2);
    int total = 0;
    for (size_t index = 0; index < count; ++index) {
        if (!parse_score(argv[index + 2], &scores[index])) {
            fprintf(stderr, "invalid score at position %zu\n", index + 1);
            return EXIT_FAILURE;
        }
        total += scores[index];
    }
    double average = (double)total / (double)count;

    /* C11 exclusive creation: an existing file must not be overwritten. */
    FILE *report = fopen(argv[1], "wx");
    if (report == NULL) {
        perror("cannot create report");
        return EXIT_FAILURE;
    }

    bool written = fprintf(report, "count,total,average\n%zu,%d,%.2f\n",
                           count, total, average) >= 0;
    int close_result = fclose(report);
    if (!written || close_result == EOF) {
        fputs("report write failed; the new file may be incomplete\n", stderr);
        return EXIT_FAILURE;
    }

    printf("count=%zu total=%d average=%.2f\n", count, total, average);
    return EXIT_SUCCESS;
}
