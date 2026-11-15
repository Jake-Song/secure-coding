#include <stdio.h>
#include <string.h>

static int sum_scores(const int *scores, size_t count) {
    int total = 0;
    for (size_t index = 0; index < count; ++index) {
        total += scores[index];
    }
    return total;
}

static char grade_for(int average) {
    switch (average / 10) {
        case 10:
        case 9: return 'A';
        case 8: return 'B';
        case 7: return 'C';
        default: return 'D';
    }
}

static int check(const char *input) {
    if (strlen(input) != 5) {
        return 0;
    }
    return strcmp(input, "trace") == 0;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s INPUT\n", argv[0]);
        return 2;
    }
    const int scores[] = {70, 80, 90};
    const size_t count = sizeof scores / sizeof scores[0];
    const int total = sum_scores(scores, count);
    char text[] = "trace";
    const int negative = -1;
    const unsigned int positive = 1U;

    printf("count=%zu total=%d grade=%c\n", count, total, grade_for(total / (int)count));
    printf("text=%s bytes=%zu length=%zu\n", text, sizeof text, strlen(text));
    printf("signed_less=%d unsigned_less=%d\n", negative < 1,
           (unsigned int)negative < positive);
    const int ok = check(argv[1]);
    puts(ok ? "accepted" : "rejected");
    return ok ? 0 : 1;
}
