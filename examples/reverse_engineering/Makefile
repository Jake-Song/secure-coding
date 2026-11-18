CC = gcc
CFLAGS = -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -O0 -g -fno-omit-frame-pointer
BUILD_DIR = build
PROGRAMS = 01_build 02_memory 03_flow 04_elf 05_lookup 07_validate 08_transform
BINARIES = $(addprefix $(BUILD_DIR)/,$(PROGRAMS))

.PHONY: all stages clean
all: $(BINARIES) $(BUILD_DIR)/03_registers $(BUILD_DIR)/04_elf_nopie \
  $(BUILD_DIR)/05_lookup_stripped $(BUILD_DIR)/07_validate_stripped stages

$(BUILD_DIR):
	mkdir -p "$@"

$(BUILD_DIR)/%: %.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIE $< -o $@ $(LDFLAGS) -pie $(LDLIBS)

$(BUILD_DIR)/03_registers: 03_registers.c registers.S | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIE $^ -o $@ $(LDFLAGS) -pie $(LDLIBS)

$(BUILD_DIR)/04_elf_nopie: 04_elf.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fno-pie $< -o $@ $(LDFLAGS) -no-pie $(LDLIBS)

$(BUILD_DIR)/%_stripped: $(BUILD_DIR)/%
	strip -o $@ $<

stages: $(BUILD_DIR)/01_build.i $(BUILD_DIR)/01_build.s $(BUILD_DIR)/01_build.o

$(BUILD_DIR)/01_build.i: 01_build.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIE -E $< -o $@

$(BUILD_DIR)/01_build.s: $(BUILD_DIR)/01_build.i
	$(CC) $(CFLAGS) -fPIE -S -masm=intel $< -o $@

$(BUILD_DIR)/01_build.o: $(BUILD_DIR)/01_build.s
	$(CC) -c $< -o $@

clean:
	rm -f $(BINARIES) $(BUILD_DIR)/03_registers $(BUILD_DIR)/04_elf_nopie \
	  $(BUILD_DIR)/05_lookup_stripped $(BUILD_DIR)/07_validate_stripped \
	  $(BUILD_DIR)/01_build.i $(BUILD_DIR)/01_build.s $(BUILD_DIR)/01_build.o \
	  $(BUILD_DIR)/01_linked
