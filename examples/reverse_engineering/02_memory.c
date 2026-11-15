#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int global_count = 7;
const char banner[] = "memory-lab";

struct Record {
    char tag;
    int count;
    short flags;
};

static void inspect_memory(uint32_t *word, int *values, struct Record *record,
                           int *heap, const char *literal) {
    printf("word=%08x middle=%d record=%c/%d/%d\n", (unsigned int)*word,
           values[1], record->tag, record->count, (int)record->flags);
    printf("heap=%d,%d,%d literal=%s global=%d\n",
           heap[0], heap[1], heap[2], literal, global_count);
    printf("addresses: word=%p values=%p record=%p heap=%p literal=%p global=%p\n",
           (void *)word, (void *)values, (void *)record, (void *)heap,
           (const void *)literal, (void *)&global_count);
}

int main(void) {
    uint32_t word = UINT32_C(0x12345678);
    int values[] = {10, 20, 30};
    int *pointer = &values[1];
    struct Record record = {.tag = 'R', .count = 3, .flags = 5};
    const char *literal = "trace";
    int *heap = malloc(3 * sizeof *heap);
    if (heap == NULL) {
        fputs("allocation failed\n", stderr);
        return 1;
    }

    *pointer = 25;
    for (size_t index = 0; index < 3; ++index) {
        heap[index] = values[index] * 2;
    }
    printf("array_bytes=%zu pointer_bytes=%zu literal_length=%zu\n",
           sizeof values, sizeof pointer, strlen(literal));
    printf("record_bytes=%zu offsets=%zu,%zu,%zu\n", sizeof record,
           offsetof(struct Record, tag), offsetof(struct Record, count),
           offsetof(struct Record, flags));
    inspect_memory(&word, values, &record, heap, literal);

    free(heap);
    heap = NULL;
    puts("heap released");
    return 0;
}
