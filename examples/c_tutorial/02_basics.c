#include <stdbool.h>
#include <stdio.h>

int main(void) {
    int score = 85;
    double ratio = 85.0 / 100.0;
    char grade = 'B';
    bool passed = score >= 60;

    printf("score=%d ratio=%.2f grade=%c passed=%d\n",
           score, ratio, grade, passed);
    printf("integer division=%d real division=%.2f\n", 5 / 2, 5.0 / 2.0);

    if (passed) {
        puts("pass");
    } else {
        puts("retry");
    }

    int total = 0;
    for (int number = 1; number <= 5; ++number) {
        total += number;
    }
    printf("sum 1..5=%d\n", total);

    switch (grade) {
        case 'A':
            puts("excellent");
            break;
        case 'B':
            puts("good");
            break;
        default:
            puts("keep practicing");
            break;
    }
    return 0;
}
