#include <stdbool.h>
#include <stdio.h>

struct Student {
    char name[32];
    int score;
};

static bool has_passed(const struct Student *student) {
    return student->score >= 60;
}

int main(void) {
    struct Student student = {.name = "Alice", .score = 85};
    printf("%s: %d (%s)\n", student.name, student.score,
           has_passed(&student) ? "pass" : "retry");
    printf("struct bytes=%zu\n", sizeof student);
    return 0;
}
