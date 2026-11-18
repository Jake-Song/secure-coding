#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define KEY_LENGTH 8U
#define PREFIX_LENGTH 4U

enum key_status {
    KEY_OK = 0,
    KEY_BAD_LENGTH = 1,
    KEY_BAD_CHARACTER = 2,
    KEY_BAD_PREFIX = 3,
    KEY_BAD_SUM = 4,
};

static const unsigned char prefix_code[PREFIX_LENGTH] = {0x36, 0x3e, 0x3e, 0x76};
static const unsigned int weighted_target = 3630U;

static int is_key_character(unsigned char value) {
    return (value >= 'a' && value <= 'z') || (value >= '0' && value <= '9');
}

static unsigned char encode(unsigned char value, size_t index) {
    return (unsigned char)((value ^ 0x5aU) + index * 3U);
}

static unsigned int weighted_sum(const unsigned char *key) {
    unsigned int total = 0U;
    for (size_t index = 0; index < KEY_LENGTH; ++index) {
        total += key[index] * (unsigned int)(index + 1U);
    }
    return total;
}

int check_key(const char *input) {
    const unsigned char *key = (const unsigned char *)input;
    if (strlen(input) != KEY_LENGTH) {
        return KEY_BAD_LENGTH;
    }
    for (size_t index = 0; index < KEY_LENGTH; ++index) {
        if (!is_key_character(key[index])) {
            return KEY_BAD_CHARACTER;
        }
    }
    for (size_t index = 0; index < PREFIX_LENGTH; ++index) {
        if (encode(key[index], index) != prefix_code[index]) {
            return KEY_BAD_PREFIX;
        }
    }
    if (weighted_sum(key) != weighted_target) {
        return KEY_BAD_SUM;
    }
    return KEY_OK;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s KEY\n", argv[0]);
        return 2;
    }
    if (check_key(argv[1]) != KEY_OK) {
        puts("rejected");
        return 1;
    }
    puts("accepted");
    return 0;
}
