CC = cc
CFLAGS = -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -O0 -g
BUILD_DIR = build
PROGRAMS = 01_hello 02_basics 03_functions_arrays 04_pointers_strings \
           05_structs 06_heap 07_input 08_score_report
BINARIES = $(addprefix $(BUILD_DIR)/,$(PROGRAMS))

.PHONY: all clean
all: $(BINARIES)

$(BUILD_DIR):
	mkdir -p "$@"

$(BUILD_DIR)/%: %.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(BINARIES)
