#include <stdio.h>
#include <string.h>

/* value must point to a live int object. */
static void add_one(int *value) {
    *value += 1;
}

int main(void) {
    int score = 80;
    int *pointer = &score;
    add_one(pointer);
    printf("score=%d pointed value=%d\n", score, *pointer);
    printf("address=%p\n", (void *)pointer);

    char name[] = "Alice";
    const char *message = "hello";
    name[0] = 'M';
    printf("name=%s bytes=%zu length=%zu\n", name, sizeof name, strlen(name));
    puts(message);
    return 0;
}
