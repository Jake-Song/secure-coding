/* 03_flow.decompiled.c의 Ghidra 의사 코드를 바탕으로 재구현한 C17 프로그램. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int32_t add_bias(int32_t left, int32_t right) {
    /* 바이너리의 32비트 덧셈처럼 상위 비트를 버리고, 결과를 부호 있게 해석한다. */
    const uint32_t bits = (uint32_t)left + (uint32_t)right + UINT32_C(3);
    if (bits <= INT32_MAX) {
        return (int32_t)bits;
    }
    return -1 - (int32_t)(UINT32_MAX - bits);
}

int choose_signed(int32_t value) {
    return value < 10;
}

int choose_unsigned(uint32_t value) {
    return value < UINT32_C(10);
}

uint32_t sum_to(uint32_t limit) {
    uint32_t total = 0;
    for (uint32_t index = 0; index < limit; ++index) {
        total += index;
    }
    return total;
}

uint32_t mix_bits(uint32_t value) {
    const uint32_t shifted_byte = (value * UINT32_C(2)) & UINT32_C(0x1fe);
    const uint32_t mixed_byte = shifted_byte ^ UINT32_C(0xb4);
    return (value >> 4) | mixed_byte;
}

int main(void) {
    const int32_t biased_total = add_bias(4, 5);
    printf("add_bias(4,5)=%" PRId32 "\n", biased_total);

    const int unsigned_result = choose_unsigned(UINT32_MAX);
    const int signed_result = choose_signed(-1);
    printf("signed(-1)=%d unsigned(UINT_MAX)=%d\n", signed_result, unsigned_result);

    const uint32_t sum_four = sum_to(4);
    const uint32_t sum_one = sum_to(1);
    const uint32_t sum_zero = sum_to(0);
    printf("sum_to(0)=%" PRIu32 " sum_to(1)=%" PRIu32 " sum_to(4)=%" PRIu32 "\n",
           sum_zero, sum_one, sum_four);

    const uint32_t mixed_value = mix_bits(UINT32_C(0x23));
    printf("mix_bits(0x23)=%" PRIu32 "\n", mixed_value);
    return 0;
}
