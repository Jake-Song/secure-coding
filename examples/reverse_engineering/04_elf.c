#include <stdio.h>

const char message[] = "elf-lab";
long initialized = 7;
long zeroed[4];

long sum_seven(long a, long b, long c, long d, long e, long f, long g) {
    return a + b + c + d + e + f + g;
}

long compute(long base) {
    const long subtotal = sum_seven(base, 2, 3, 4, 5, 6, 7);
    zeroed[0] = subtotal;
    return subtotal + initialized;
}

int main(void) {
    const long result = compute(1);
    printf("%s result=%ld zeroed[0]=%ld\n", message, result, zeroed[0]);
    return 0;
}
