#include <stdint.h>
#include <stdio.h>

int add_bias(int left, int right) {
    return left + right + 3;
}

int choose_signed(int value) {
    if (value < 10) {
        return 1;
    }
    return 0;
}

int choose_unsigned(unsigned int value) {
    if (value < 10U) {
        return 1;
    }
    return 0;
}

unsigned int sum_to(unsigned int limit) {
    unsigned int total = 0;
    for (unsigned int index = 0; index < limit; ++index) {
        total += index;
    }
    return total;
}

uint32_t mix_bits(uint32_t value) {
    return (((value & UINT32_C(0xff)) ^ UINT32_C(0x5a)) << 1) | (value >> 4);
}

int main(void) {
    printf("add_bias(4,5)=%d\n", add_bias(4, 5));
    printf("signed(-1)=%d unsigned(UINT_MAX)=%d\n",
           choose_signed(-1), choose_unsigned((unsigned int)-1));
    printf("sum_to(0)=%u sum_to(1)=%u sum_to(4)=%u\n",
           sum_to(0), sum_to(1), sum_to(4));
    printf("mix_bits(0x23)=%u\n", (unsigned int)mix_bits(UINT32_C(0x23)));
    return 0;
}
