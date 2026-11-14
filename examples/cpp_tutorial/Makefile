CXX = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -O0 -g
BUILD_DIR = build
PROGRAMS = 01_hello 02_basics 03_strings_vectors 04_classes \
           05_algorithms 06_raii 07_input 08_score_report
BINARIES = $(addprefix $(BUILD_DIR)/,$(PROGRAMS))

.PHONY: all clean
all: $(BINARIES)

$(BUILD_DIR):
	mkdir -p "$@"

$(BUILD_DIR)/%: %.cpp score.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(BINARIES)
