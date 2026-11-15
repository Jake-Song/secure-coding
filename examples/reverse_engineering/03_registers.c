#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

uint64_t register_demo(const uint32_t *value);

int main(void) {
    const uint32_t value = UINT32_C(0x12345678);
    const uint64_t result = register_demo(&value);
    printf("register_demo=%" PRIu64 "\n", result);
    return result == UINT64_C(0x1234567f) ? 0 : 1;
}
