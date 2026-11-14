#include <stddef.h>
#include <stdio.h>

/* Caller supplies count valid elements; this lesson uses only small scores. */
static int sum_scores(const int scores[], size_t count) {
    int total = 0;
    for (size_t index = 0; index < count; ++index) {
        total += scores[index];
    }
    return total;
}

int main(void) {
    const int scores[] = {70, 80, 90};
    size_t count = sizeof scores / sizeof scores[0];
    int total = sum_scores(scores, count);
    double average = (double)total / (double)count;

    printf("count=%zu total=%d average=%.2f\n", count, total, average);
    return 0;
}
