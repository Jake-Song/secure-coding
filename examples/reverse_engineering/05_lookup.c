#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define FLAG_ACTIVE 0x1U
#define FLAG_ADMIN 0x4U
#define REQUIRED_LEVEL 3U

struct account {
    const char *name;
    unsigned int level;
    unsigned int flags;
};

static const struct account accounts[] = {
    {"guest", 1U, FLAG_ACTIVE},
    {"analyst", 3U, FLAG_ACTIVE},
    {"retired", 5U, 0U},
    {"root", 9U, FLAG_ACTIVE | FLAG_ADMIN},
};

unsigned int lookup_count;

static const struct account *find_account(const char *name) {
    for (size_t index = 0; index < sizeof accounts / sizeof accounts[0]; ++index) {
        ++lookup_count;
        if (strcmp(accounts[index].name, name) == 0) {
            return &accounts[index];
        }
    }
    return NULL;
}

static int is_allowed(const struct account *account, unsigned int required) {
    if ((account->flags & FLAG_ACTIVE) == 0U) {
        return 0;
    }
    return account->level >= required;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s NAME\n", argv[0]);
        return 2;
    }
    const struct account *account = find_account(argv[1]);
    if (account == NULL) {
        puts("unknown account");
        return 1;
    }
    if (!is_allowed(account, REQUIRED_LEVEL)) {
        puts("access denied");
        return 1;
    }
    printf("accepted level=%u%s\n", account->level,
           (account->flags & FLAG_ADMIN) != 0U ? " admin" : "");
    return 0;
}
