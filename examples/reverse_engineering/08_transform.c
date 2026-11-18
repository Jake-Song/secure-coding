#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define MAX_INPUT 64U

uint32_t transform(const uint8_t *input, size_t length, uint8_t *output) {
    uint8_t key = 0xa7U;
    uint32_t accumulator = 0x1234U;
    for (size_t index = 0; index < length; ++index) {
        const uint8_t value = input[index];
        output[index] = (uint8_t)((value ^ key) + (uint8_t)(index * 7U));
        key = (uint8_t)((key << 1) | (key >> 7));
        const int8_t signed_value = (int8_t)value;
        const int32_t quarter = signed_value / 4;
        accumulator = accumulator * 31U + (uint32_t)quarter;
    }
    return accumulator;
}

int main(void) {
    uint8_t input[MAX_INPUT + 1U];
    uint8_t output[MAX_INPUT];
    const size_t length = fread(input, 1, sizeof input, stdin);
    if (ferror(stdin)) {
        fputs("read error\n", stderr);
        return 2;
    }
    if (length > MAX_INPUT) {
        fprintf(stderr, "input too long: max %u bytes\n", MAX_INPUT);
        return 2;
    }
    const uint32_t accumulator = transform(input, length, output);
    printf("length=%zu\nout=", length);
    for (size_t index = 0; index < length; ++index) {
        printf("%02x", output[index]);
    }
    printf("\nacc=%08x\n", (unsigned int)accumulator);
    return 0;
}
